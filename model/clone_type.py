from enum import Enum


class CloneType(Enum):
    """
    克隆类型枚举。
    - TYPE_1: 语法和标识都相同（Type-1）
    - TYPE_2: 仅标识或字面量不同（Type-2）
    - TYPE_3: 有改动（增删或修改），但逻辑相似（Type-3）
    - TYPE_4: 抽象语义相似但实现不同（Type-4）
    - UNKNOWN: 未知/未分类
    """

    TYPE_1 = "Type-1"
    TYPE_2 = "Type-2"
    TYPE_3 = "Type-3"
    TYPE_4 = "Type-4"
    UNKNOWN = "Unknown"
