from __future__ import annotations

import argparse
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Tuple

from utils.file.file_io import read_functions_from_disk
from utils.java_code.function_extract import FunctionInfo
from clone.clone_class_parser import parse_clone_classes_from_csv
from clone.clone_class import CloneClass
from clone.clone_pair import ClonePair

# -----------------------------
# 数据结构
# -----------------------------
class _Pair:
    def __init__(self, file1, start1, end1, file2, start2, end2):
        self.file1 = file1
        self.start1 = start1
        self.end1 = end1
        self.file2 = file2
        self.start2 = start2
        self.end2 = end2

class _Cls:
    def __init__(self, pairs: List[_Pair]):
        self.clone_pairs = pairs

# -----------------------------
# 解析克隆类（使用 parse_clone_class.py 接口）
# -----------------------------
def read_clone_classes_from_csv(filepath: str) -> List[CloneClass]:
    """使用 parse_clone_class.py 接口解析克隆类"""
    return parse_clone_classes_from_csv(filepath, "utf-8")

# -----------------------------
# 函数索引
# -----------------------------
def build_index(functions: List[FunctionInfo]) -> Dict[Tuple[str, int, int], FunctionInfo]:
    """构建函数索引，用于快速查找函数信息"""
    idx: Dict[Tuple[str, int, int], FunctionInfo] = {}
    for f in functions:
        key = (f.filename, f.start_line, f.end_line)
        idx[key] = f
    return idx

def find_function_info(
    index: Dict[Tuple[str, int, int], FunctionInfo], file_path: str, start: int, end: int
) -> Optional[FunctionInfo]:
    """根据文件路径和行号查找函数信息"""
    basename = os.path.basename(file_path)
    key = (basename, start, end)
    if key in index:
        return index[key]

    for (fn, s, e), finfo in index.items():
        if s == start and e == end and file_path.endswith(fn):
            return finfo
    return None

def pick_representative_for_clone_class(
    clone_class: CloneClass, index: Dict[Tuple[str, int, int], FunctionInfo]
) -> Optional[FunctionInfo]:
    """为克隆类选择代表函数，选择最短的函数作为代表"""
    candidates: List[FunctionInfo] = []
    for p in clone_class.clone_pairs:
        f1 = find_function_info(index, p.file1, p.start1, p.end1)
        f2 = find_function_info(index, p.file2, p.start2, p.end2)
        if f1: candidates.append(f1)
        if f2: candidates.append(f2)

    if not candidates:
        return None

    # 按代码长度+行跨度选择最短的函数作为代表
    candidates.sort(key=lambda fi: (len(fi.code_snippet or ""), fi.end_line - fi.start_line))
    return candidates[0]

# -----------------------------
# 提示词构建
# -----------------------------
def truncate_code(code: str, max_chars: int = 2000) -> str:
    """截断代码，避免提示词过长"""
    if not code:
        return ""
    if len(code) <= max_chars:
        return code
    lines = code.splitlines()
    out = []
    chars = 0
    for l in lines:
        if chars + len(l) + 1 > max_chars:
            break
        out.append(l)
        chars += len(l) + 1
    out.append("/* TRUNCATED */")
    return "\n".join(out)

PROMPT_TEMPLATE = (
    "You are a precise code clone detection assistant.\n"
    "You will be given a TARGET Java function and a list of REPRESENTATIVE functions.\n"
    "Each representative corresponds to a clone class (i.e., a group of functions considered clones of each other).\n"
    "Your job: determine whether the TARGET function is a clone of any of the provided representatives.\n"
    "Definitions and expectations:\n"
    "  - \"Clone\" may be syntactic or semantic. Be conservative if unsure.\n"
    "Output EXACTLY one JSON object:\n"
    "{{ \"is_clone\": true|false, \"matched_rep_id\": int|null, \"confidence\": float, \"reason\": string }}\n\n"
    "TARGET FUNCTION (metadata + code):\n{target_block}\n\n"
    "REPRESENTATIVE FUNCTIONS:\n{rep_block}\n"
)

def build_prompt(target: FunctionInfo, representatives: List[dict], max_code_chars: int = 2000) -> str:
    target_block = json.dumps({
        "filename": target.filename,
        "subdirectory": target.subdirectory,
        "start_line": target.start_line,
        "end_line": target.end_line,
        "code": truncate_code(target.code_snippet or "", max_chars=max_code_chars),
    }, indent=2)

    rep_list = []
    for i, r in enumerate(representatives):
        func = r["function"]
        rep_list.append({
            "id": i,
            "class_id": r["class_id"],
            "filename": func.filename,
            "subdirectory": func.subdirectory,
            "start_line": func.start_line,
            "end_line": func.end_line,
            "code": truncate_code(func.code_snippet or "", max_chars=max_code_chars),
        })

    rep_block = json.dumps(rep_list, indent=2)
    return PROMPT_TEMPLATE.format(target_block=target_block, rep_block=rep_block)

# -----------------------------
# LLM 调用
# -----------------------------
def call_openai_completion(prompt: str, model: str = "gpt-4") -> str:
    """调用 OpenAI API"""
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # 如果没有 API 密钥，返回一个模拟的响应用于测试
        print("WARNING: OPENAI_API_KEY not set, using mock response")
        return '{"is_clone": false, "matched_rep_id": null, "confidence": 0.5, "reason": "Mock response for testing"}'
    
    # 使用智谱清言的 API 服务
    base_url = "https://xiaoai.plus/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 使用 gpt-4o-mini 模型（智谱清言推荐）
    if model == "gpt-4":
        model = "gpt-4o-mini"
    
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.0,
    )
    return resp.choices[0].message.content

def validate_and_extract_json(text: str) -> dict:
    """Try to extract a single JSON object from model output and return as dict.

    This is tolerant to markdown fences and trailing text. When parsing fails,
    raise a ValueError with a helpful snippet for debugging.
    """
    s = (text or "").strip()
    
    # remove surrounding ``` fences (with optional language)
    if s.startswith("```"):
        # defensive: although uncommon, handle safely
        s = re.sub(r"^```(?:\w+)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
        s = s.strip()

    # try to parse entire string first
    try:
        parsed = json.loads(s)
    except Exception:
        # fallback: search for the last {...} block in the text
        m = re.search(r"\{[\s\S]*\}\s*$", s)
        if not m:
            raise ValueError(f"No JSON found in model output: {s[:300]!r}")
        candidate = m.group(0)
        try:
            parsed = json.loads(candidate)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON candidate: {e}; candidate snippet: {candidate[:300]!r}")

    if not isinstance(parsed, dict):
        raise ValueError(f"Parsed JSON is not an object/dict (got {type(parsed)}); snippet: {str(parsed)[:300]!r}")
    return parsed

def process_target(idx: int, target: FunctionInfo, representatives: List[dict], model: str) -> dict:
    prompt = build_prompt(target, representatives)
    raw_text = None
    try:
        raw_text = call_openai_completion(prompt, model=model)
        parsed = validate_and_extract_json(raw_text)
        matched_cls_id = None
        if parsed.get("is_clone") and parsed.get("matched_rep_id") is not None:
            mi = int(parsed["matched_rep_id"])
            if 0 <= mi < len(representatives):
                matched_cls_id = representatives[mi]["class_id"]
        return {
            "id": idx,
            "filename": target.filename,
            "start_line": target.start_line,
            "end_line": target.end_line,
            "matched_clone_class_id": matched_cls_id,
        }
    except Exception as e:
        # Return an error-bearing record so the pipeline can continue and user can debug.
        err_str = str(e)
        raw_snip = None
        if raw_text:
            raw_snip = raw_text[:1000]
        return {
            "id": idx,
            "filename": target.filename,
            "start_line": target.start_line,
            "end_line": target.end_line,
            "matched_clone_class_id": None,
            "error": err_str,
            "raw_output": raw_snip,
        }

# -----------------------------
# 主生成函数
# -----------------------------
def generate_prompts(
    functions_pkl: str,
    clone_csv: str,
    out_jsonl: str,
    limit: Optional[int] = None,
    max_reps: Optional[int] = None,
    model: str = "gpt-4",
    concurrency: int = 1,
    save_prompts: bool = False,
    prompts_out: Optional[str] = None,
):
    print(f"Loading functions from {functions_pkl}...")
    functions = read_functions_from_disk(functions_pkl)
    print(f"Loaded {len(functions)} functions.")

    print(f"Loading clone classes from {clone_csv}...")
    clone_classes = read_clone_classes_from_csv(clone_csv)
    print(f"Loaded {len(clone_classes)} clone classes.")

    index = build_index(functions)

    # 挑选代表函数
    representatives = []
    for i, cc in enumerate(clone_classes):
        rep = pick_representative_for_clone_class(cc, index)
        if rep:
            representatives.append({"class_id": i + 1, "function": rep})
    if max_reps:
        representatives = representatives[:max_reps]
    print(f"Using {len(representatives)} representatives.")

    # 准备输出
    os.makedirs(os.path.dirname(out_jsonl) or ".", exist_ok=True)
    pf = None
    if save_prompts:
        if not prompts_out:
            raise ValueError("prompts_out must be provided")
        os.makedirs(os.path.dirname(prompts_out) or ".", exist_ok=True)
        pf = open(prompts_out, "w", encoding="utf-8")

    lock = threading.Lock()
    written = 0
    with open(out_jsonl, "w", encoding="utf-8") as outf, ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = []
        for idx, target in enumerate(functions):
            if limit and idx >= limit:
                break
            futures.append(ex.submit(process_target, idx, target, representatives, model))

        for fut in as_completed(futures):
            try:
                res = fut.result()
            except Exception as e:
                print(f"Error processing target: {e}")
                # Create a dummy result for failed targets
                res = {
                    "id": -1,
                    "filename": "unknown",
                    "start_line": -1,
                    "end_line": -1,
                    "matched_clone_class_id": None,
                    "error": str(e)
                }
            with lock:
                outf.write(json.dumps(res, ensure_ascii=False) + "\n")
                written += 1
                if pf:
                    tid = res["id"]
                    prompt_text = build_prompt(functions[tid], representatives)
                    pf.write(json.dumps({"id": tid, "prompt": prompt_text}, ensure_ascii=False) + "\n")

    if pf:
        pf.close()
    print(f"Finished writing {written} results to {out_jsonl}.")

# -----------------------------
# CLI
# -----------------------------
def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Generate prompts for clone detection using test.csv")
    parser.add_argument("--functions", required=True, help="functions.pkl path")
    parser.add_argument("--clone_csv", required=True, help="test.csv path")
    parser.add_argument("--out", required=True, help="output JSONL path")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model", type=str, default="gpt-4")
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--max_reps", type=int, default=None)
    parser.add_argument("--save-prompts", action="store_true")
    parser.add_argument("--prompts-out", type=str, default=None)
    args = parser.parse_args(argv)
    generate_prompts(
        args.functions, args.clone_csv, args.out,
        limit=args.limit,
        max_reps=args.max_reps,
        model=args.model,
        concurrency=args.concurrency,
        save_prompts=args.save_prompts,
        prompts_out=args.prompts_out
    )

if __name__ == "__main__":
    main()
