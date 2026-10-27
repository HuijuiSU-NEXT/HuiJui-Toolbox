import os
import re

# 1. 清理 main_final.py 里的 print
TARGET_MAIN = r"D:\Huijui-Toolbox-Next\main_final.py"
with open(TARGET_MAIN, 'r', encoding='utf-8') as f:
    content = f.read()

# 把所有的 print("🔥 [DEBUG]...") 删掉
content = re.sub(r'\s*print\(f?"🔥 \[DEBUG\].*?\)\n', '\n', content)
content = re.sub(r'\s*print\("🔥 \[DEBUG\].*?\)\n', '\n', content)

with open(TARGET_MAIN, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print("✅ main_final.py 里的 Debug print 已清理！")

# 2. 清理 core/adb_core.py 里的 print，并加固路径
TARGET_CORE = r"D:\Huijui-Toolbox-Next\core\adb_core.py"
with open(TARGET_CORE, 'r', encoding='utf-8') as f:
    core_content = f.read()

# 剔除所有 print
core_content = re.sub(r'\s*print\(.*?\)\n', '\n', core_content)

# 确保 BASE_DIR 逻辑极简且绝对安全
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

with open(TARGET_CORE, 'w', encoding='utf-8', newline='\n') as f:
    f.write(core_content)
print("✅ adb_core.py 已清理并加固路径！")