import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们要在程序最开头注入一段“自动释放”的逻辑
INJECT_HEADER = '''import os
import sys
import shutil

# 🚨 单文件模式终极兼容补丁：强制释放 bin 和 assets 到固定目录
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    # 单文件运行时，数据会被解压到一个临时目录，我们把它拷到安全的地方
    temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 设定一个固定的安全路径，放在 C 盘用户目录下，避开杀软对 Temp 的严打
    safe_dir = os.path.join(os.environ.get('USERPROFILE', 'C:'), 'HuiJui_Toolbox_Data')
    
    if not os.path.exists(safe_dir):
        os.makedirs(safe_dir)
        
    for folder in ['bin', 'assets']:
        src = os.path.join(temp_dir, folder)
        dst = os.path.join(safe_dir, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copytree(src, dst)
            except Exception as e:
                print(f"释放文件夹失败: {folder}, {e}")
                
    # 强制将 BASE_DIR 指向这个安全路径
    BASE_DIR = safe_dir
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

'''

# 把这段代码插在 import flet 之前
if "HuiJui_Toolbox_Data" not in content:
    # 找到 import flet as ft
    if "import flet as ft" in content:
        content = content.replace("import flet as ft", INJECT_HEADER + "import flet as ft")
        with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("✅ 终极单文件释放补丁注入成功！")
    else:
        print("❌ 没找到 import flet as ft，可能是代码被改过了。")
else:
    print("⚠️ 补丁已经存在，无需重复注入。")