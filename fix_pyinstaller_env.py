import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

NEW_HEADER = '''import os
import sys
import shutil

# 🚨 PyInstaller 专属资源释放引擎
if getattr(sys, 'frozen', False):
    # PyInstaller 临时解压目录
    bundle_dir = sys._MEIPASS
    # 当前 exe 所在目录
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 强行把 bin 和 assets 释放到 exe 旁边
    for folder in ['bin', 'assets']:
        src = os.path.join(bundle_dir, folder)
        dst = os.path.join(exe_dir, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copytree(src, dst)
            except Exception as e:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, f"释放 {folder} 失败: {str(e)}", "环境释放错误", 16)
                sys.exit(1)
                
    BASE_DIR = exe_dir
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

'''

# 替换掉旧的头部（截断到 import flet 之前）
if "import flet as ft" in content:
    parts = content.split("import flet as ft", 1)
    content = NEW_HEADER + "import flet as ft" + parts[1]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Successfully injected PyInstaller release engine!")