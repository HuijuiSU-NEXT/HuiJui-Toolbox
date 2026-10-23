# fix_portable_path.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 注入跨平台/跨打包环境的绝对路径识别逻辑
path_logic = '''import sys
import os

# 🚨 核心：识别是否为打包后的 EXE
if getattr(sys, 'frozen', False) or '__compiled__' in globals():
    # 如果是打包后的程序，路径取 EXE 所在的目录
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    # 如果是开发环境，路径取当前 py 文件所在的目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
'''

# 替换掉原来的 BASE_DIR 定义
if "BASE_DIR = os.path.dirname(os.path.abspath(__file__))" in content:
    content = content.replace(
        "BASE_DIR = os.path.dirname(os.path.abspath(__file__))", 
        path_logic
    )
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 便携版路径补丁已注入！现在 EXE 放哪里，数据和壁纸就存哪里！")
else:
    print("⚠️ 未找到 BASE_DIR 定义，请检查代码。")