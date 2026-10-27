import os
import re

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 需要注入的硬核头部逻辑
NEW_HEADER = '''import os
import sys
import shutil
import ctypes

def _setup_onefile_env():
    """原生单文件环境释放引擎：不管在哪，强行生成 bin 和 assets"""
    if getattr(sys, 'frozen', False) or "__compiled__" in globals():
        # Nuitka 的 onefile 模式特有环境变量，指向用户双击的 exe 真实路径
        if "NUITKA_ONEFILE_PARENT" in os.environ:
            target_dir = os.path.dirname(os.path.abspath(os.environ["NUITKA_ONEFILE_PARENT"]))
        else:
            target_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
        # 当前运行的临时解压目录
        temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # 检查目标目录是否有写入权限（防止用户扔进 C:\\Program Files）
        test_file = os.path.join(target_dir, ".write_test")
        try:
            with open(test_file, 'w') as f: f.write("ok")
            os.remove(test_file)
        except:
            # 没有权限，回退到系统临时目录，防止闪退
            return temp_dir

        # 强行释放 bin 和 assets
        for folder in ['bin', 'assets']:
            src = os.path.join(temp_dir, folder)
            dst = os.path.join(target_dir, folder)
            
            if os.path.exists(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst, ignore_errors=True) # 强制覆盖旧文件，防止版本落后
                try:
                    shutil.copytree(src, dst)
                except Exception as e:
                    # 🚨 如果复制失败，直接弹窗，绝不静默吞错！
                    ctypes.windll.user32.MessageBoxW(0, f"释放 {folder} 失败: {str(e)}\\n请尝试以管理员身份运行，或关闭杀毒软件。", "HuiJui Toolbox 错误", 16)
                    sys.exit(1)
        return target_dir
    else:
        return os.path.dirname(os.path.abspath(__file__))

# 强制绑定 BASE_DIR
BASE_DIR = _setup_onefile_env()

'''

# 用正则剔除旧的头部代码（从开头一直到旧的 BASE_DIR 定义结束）
pattern = r'^.*?BASE_DIR\s*=\s*.*?\n'
# 找到 import flet as ft 前面的所有代码，全部替换
if "import flet as ft" in content:
    parts = content.split("import flet as ft", 1)
    content = NEW_HEADER + "import flet as ft" + parts[1]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("Successfully injected hardcore onefile release engine!")