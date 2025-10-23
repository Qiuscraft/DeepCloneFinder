import pickle
from transformers import AutoModel, AutoTokenizer
from tqdm.auto import tqdm

if __name__ == "__main__":
    
    checkpoint = "codet5p-110m-embedding"
    device = "cuda"  # for GPU usage or "cpu" for CPU usage

    tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
    model = AutoModel.from_pretrained(checkpoint, trust_remote_code=True).to(device)

    with open("functions.pkl", 'rb') as f:
        functions = pickle.load(f)
        
    for func in tqdm(functions, desc="Embedding functions"):
        inputs = tokenizer.encode(func.code_snippet, return_tensors="pt").to(device)
        embedding = model(inputs)[0]
        func.embedding = embedding
    
    with open("functions.pkl", 'wb') as f:
        pickle.dump(functions, f)
