import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

NEW_HEADER = '''import os
import sys
import shutil
import ctypes

def _setup_onefile_env():
    """终极原生单文件释放引擎"""
    if getattr(sys, 'frozen', False) or "__compiled__" in globals():
        # 获取临时解压目录
        temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # 🚨 核心修复：获取用户双击的真实 exe 所在目录
        if "__compiled__" in globals() and hasattr(__compiled__, "containing_dir"):
            target_dir = __compiled__.containing_dir
        elif "NUITKA_ONEFILE_PARENT" in os.environ and os.path.exists(os.environ["NUITKA_ONEFILE_PARENT"]):
            target_dir = os.path.dirname(os.path.abspath(os.environ["NUITKA_ONEFILE_PARENT"]))
        else:
            target_dir = os.getcwd()

        # 测试当前目录是否有写入权限
        try:
            test_file = os.path.join(target_dir, ".write_test")
            with open(test_file, 'w') as f: f.write("ok")
            os.remove(test_file)
        except:
            # 如果没有权限（比如在C盘根目录），回退到临时目录
            target_dir = temp_dir

        # 强行释放
        for folder in ['bin', 'assets']:
            src = os.path.join(temp_dir, folder)
            dst = os.path.join(target_dir, folder)
            
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True) # 覆盖旧文件
                try:
                    shutil.copytree(src, dst)
                except Exception as e:
                    # 🚨 失败弹窗，绝不静默
                    ctypes.windll.user32.MessageBoxW(0, f"释放 {folder} 失败: {str(e)}", "HuiJui 错误", 16)
                    sys.exit(1)
        return target_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _setup_onefile_env()

'''

# 替换掉旧的头部（截断到 import flet 之前）
if "import flet as ft" in content:
    parts = content.split("import flet as ft", 1)
    content = NEW_HEADER + "import flet as ft" + parts[1]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Successfully injected perfect onefile release engine!")