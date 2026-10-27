import os
import re

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们要替换掉旧的所有头部逻辑
OLD_HEADER_PATTERN = r'import os\nimport sys\nimport shutil.*?(?=import flet as ft)'

NEW_HEADER = '''import os
import sys
import shutil

# 🚨 Nuitka 单文件：同级目录极速释放 + 权限兜底补丁
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    # Nuitka 特有的环境变量，指向用户双击的那个真实 exe
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        user_exe_dir = os.path.dirname(os.path.abspath(os.environ["NUITKA_ONEFILE_PARENT"]))
    else:
        user_exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
    # 当前运行的临时解压目录
    temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 将 bin 和 assets 极速复制到 exe 旁边（只有几十兆，秒拷）
    write_success = True
    for folder in ['bin', 'assets']:
        src = os.path.join(temp_dir, folder)
        dst = os.path.join(user_exe_dir, folder)
        # 如果同级没有这个文件夹，且临时目录有，就复制
        if not os.path.exists(dst) and os.path.exists(src):
            try: 
                shutil.copytree(src, dst)
            except Exception: 
                write_success = False # 权限不足，或者被杀毒锁死
                
    # 如果成功释放到了同级目录，就把 BASE_DIR 指向那里
    if write_success and os.path.exists(os.path.join(user_exe_dir, "bin")):
        BASE_DIR = user_exe_dir
    else:
        # 如果没权限写入（比如放进了C盘根目录），就默默使用临时目录
        BASE_DIR = temp_dir
        
    os.environ['HUIJUI_SAFE_DIR'] = BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

'''

if "NUITKA_ONEFILE_PARENT" not in content:
    content = re.sub(OLD_HEADER_PATTERN, NEW_HEADER, content, flags=re.DOTALL)
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 终极伴生释放补丁（含权限兜底）注入成功！")
else:
    print("⚠️ 伴生补丁已经存在，无需重复注入。")