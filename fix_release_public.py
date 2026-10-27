import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

NEW_HEADER = '''import os
import sys
import shutil

# 🚨 终极释放引擎：释放到绝对安全的系统公共目录
def _setup_onefile_env():
    if getattr(sys, 'frozen', False) or "__compiled__" in globals():
        # 获取当前临时解压目录
        temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # 获取系统公共目录 (C:\\Users\\Public)，这里的权限最宽松，杀软最不敏感
        public_dir = os.environ.get('PUBLIC', 'C:\\\\Users\\\\Public')
        safe_dir = os.path.join(public_dir, 'HuiJui_Toolbox_Data')
        
        if not os.path.exists(safe_dir):
            try: os.makedirs(safe_dir)
            except: pass
            
        # 强行把 bin 和 assets 释放到安全目录
        for folder in ['bin', 'assets']:
            src = os.path.join(temp_dir, folder)
            dst = os.path.join(safe_dir, folder)
            if os.path.exists(src) and not os.path.exists(dst):
                try: 
                    shutil.copytree(src, dst)
                except: 
                    pass
                    
        # 强制让程序使用这个绝对安全的目录
        return safe_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _setup_onefile_env()

'''

# 替换旧头部
if "import flet as ft" in content:
    parts = content.split("import flet as ft", 1)
    content = NEW_HEADER + "import flet as ft" + parts[1]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Successfully injected public dir release engine!")