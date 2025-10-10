# DeepCloneFinder

一个代码克隆检测工具。致力于利用LLM的能力寻找出Type-4克隆。

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