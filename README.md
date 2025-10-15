# DeepCloneFinder

一个代码克隆检测工具。致力于利用LLM的能力寻找出Type-4克隆。

工具目标是在识别所需时间、金钱成本和识别准确率之间取得平衡。

评估框架采用BigCloneEval。

## 依赖安装

Python 版本：3.12

```
pip install -r requirements.txt
```

## 数据集下载

链接：https://1drv.ms/u/s!AhXbM6MKt_yLj_N15CewgjM7Y8NLKA?e=cScoRJ

下载后，解压到你喜欢的地方，不建议解压到项目目录，这会导致IDE开始编制索引。

你需要在 `config.py` 中配置数据集路径。

## 自动化测试

运行下面的指令，将进行自动化测试。

目前已经实现function_extract的自动化测试，这个功能用于提取.java文件中的函数片段及函数起始行号和终止行号。

```
pytest
```

## 项目结构

```
.
├── config.py               # 配置文件，用于设置数据集的路径
├── get_all_functions.py    # 可执行脚本，提取所有java函数
├── test/                   # 测试代码目录
│   ├── function_extract.java # 用于测试的Java示例文件
│   └── test_function_extract.py # function_extract.py的自动化测试脚本
└── utils/                  # 工具脚本目录
    ├── detect_encoding.py    # 检测文件编码格式的工具
    ├── file_io.py            # 负责把FunctionInfo保存到磁盘上/从磁盘上加载进内存中。从而避免重复计算，加速效率。
    ├── function_extract.py   # 核心功能，从java文件提取函数，定义了FunctionInfo
    ├── line_counter.py       # 可执行脚本。统计.java文件代码行数
    └── logger.py             # 配置和初始化日志记录器
```
