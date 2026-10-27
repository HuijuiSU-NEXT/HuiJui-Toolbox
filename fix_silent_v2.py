import os, re

# 1. 修改 core/adb_core.py
target_core = r"D:\Huijui-Toolbox-Next\core\adb_core.py"
with open(target_core, 'r', encoding='utf-8') as f:
    core_content = f.read()

# 剔除 core 里面的 print
core_content = re.sub(r'\s*print\(.*?\)\n', '\n', core_content)

new_header = '''import os
import sys

if 'HUIJUI_SAFE_DIR' in os.environ:
    BASE_DIR = os.environ['HUIJUI_SAFE_DIR']
elif getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = os.path.join(BASE_DIR, "bin")
ADB = os.path.join(BIN_DIR, "adb.exe")
FASTBOOT = os.path.join(BIN_DIR, "fastboot.exe")
'''

# 替换旧头部
core_content = re.sub(r'(?s)^.*?FASTBOOT\s*=\s*os\.path\.join\(.*?\)\s*\n', new_header, core_content)

with open(target_core, 'w', encoding='utf-8', newline='\n') as f:
    f.write(core_content)

print("Successfully cleaned adb_core.py!")