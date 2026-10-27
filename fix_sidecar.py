import os
import re

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们要替换掉之前在 main_final.py 头部的释放逻辑
OLD_HEADER_PATTERN = r'import os\nimport sys\nimport shutil.*?(?=import flet as ft)'

NEW_HEADER = '''import os
import sys
import shutil

# 🚨 单文件模式终极伴生补丁：在 exe 同级目录释放 bin 和 assets
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    # 获取用户双击的那个真实 exe 的路径
    if "NUITKA_ONEFILE_PARENT" in os.environ:
        # Nuitka 独有的环境变量，指向用户双击的 exe
        exe_path = os.environ["NUITKA_ONEFILE_PARENT"]
    else:
        exe_path = sys.argv[0]
        
    user_exe_dir = os.path.dirname(os.path.abspath(exe_path))
    
    # 当前运行的临时解压目录（里面包含被塞进去的 bin 和 assets）
    temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # 将临时目录的 bin 和 assets 复制到 exe 旁边
    for folder in ['bin', 'assets']:
        src = os.path.join(temp_dir, folder)
        dst = os.path.join(user_exe_dir, folder)
        if os.path.exists(src) and not os.path.exists(dst):
            try: 
                shutil.copytree(src, dst)
            except Exception as e: 
                print(f"释放 {folder} 失败: {e}")
                
    # 强制将基准目录设为用户 exe 所在的目录
    BASE_DIR = user_exe_dir
    os.environ['HUIJUI_SAFE_DIR'] = BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

'''

if "HUIJUI_SAFE_DIR" in content and "NUITKA_ONEFILE_PARENT" not in content:
    content = re.sub(OLD_HEADER_PATTERN, NEW_HEADER, content, flags=re.DOTALL)
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 终极伴生释放补丁注入成功！")
elif "NUITKA_ONEFILE_PARENT" in content:
    print("⚠️ 伴生补丁已经存在，无需重复注入。")
else:
    print("❌ 未找到旧头部，请确认代码结构。")