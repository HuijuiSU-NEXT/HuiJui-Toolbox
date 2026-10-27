import os

TARGET = r"D:\Huijui-Toolbox-Next\core\adb_core.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 需要补齐的核心库
missing_imports = ["import re", "import json", "import time", "import subprocess", "import threading", "import ctypes", "from collections import deque"]

to_add = []
for imp in missing_imports:
    # 如果文件里没有这个导入，就加进去
    if imp not in content:
        to_add.append(imp)

if to_add:
    insert_str = "\n".join(to_add) + "\n"
    content = insert_str + content
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 成功补齐丢失的底层库！")
else:
    print("⚠️ 库都在，无需补齐。")