import os
import sys

TARGET = r"D:\Huijui-Toolbox-Next\core\adb_core.py"

print("正在读取文件...")
with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 先把粘在一起的那句切开
if '"fastboot.exe")DUMPER' in content:
    content = content.replace('"fastboot.exe")DUMPER', '"fastboot.exe")\nDUMPER = ')
    print("✅ 成功切分了 FASTBOOT 和 DUMPER 的粘连代码")
else:
    print("⚠️ 没找到粘连的代码，可能已经是好的了")

# 2. 清理并重新注入 Nuitka 兼容的头部
# 安全起见，我们把文件从头到 ADB = 的代码全部替换成标准头部
new_header = """import os
import sys

if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = os.path.join(BASE_DIR, "bin")
ADB = os.path.join(BIN_DIR, "adb.exe")
FASTBOOT = os.path.join(BIN_DIR, "fastboot.exe")
DUMPER = os.path.join(BIN_DIR, "payload-dumper-go.exe")
"""

# 找到文件中第一个以 "import " 开头的行或者 BASE_DIR 所在的位置
# 直接把从文件开头到 "DUMPER = " 这一段全部替换掉
lines = content.split('\n')
insert_idx = 0
for i, line in enumerate(lines):
    if line.strip().startswith('DUMPER ='):
        insert_idx = i + 1
        break

# 重新组装
content = new_header + '\n'.join(lines[insert_idx:])

# 3. 写入
with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("🎉 adb_core.py 修复完毕！")