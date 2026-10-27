import os

# 1. 修改 main_final.py，强制将安全路径注入环境变量
TARGET_MAIN = r"D:\Huijui-Toolbox-Next\main_final.py"
with open(TARGET_MAIN, 'r', encoding='utf-8') as f:
    main_content = f.read()

if "HUIJUI_SAFE_DIR" not in main_content:
    inject_code = '''import os
import sys
import shutil

if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    safe_dir = os.path.join(os.environ.get('USERPROFILE', 'C:'), 'HuiJui_Toolbox_Data')
    if not os.path.exists(safe_dir):
        os.makedirs(safe_dir)
    
    # 🚨 核心：把路径写进系统环境变量，让所有底层模块都能读到
    os.environ['HUIJUI_SAFE_DIR'] = safe_dir
    
    temp_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for folder in ['bin', 'assets']:
        src = os.path.join(temp_dir, folder)
        dst = os.path.join(safe_dir, folder)
        if os.path.exists(src):
            try:
                if not os.path.exists(dst):
                    shutil.copytree(src, dst)
            except: pass

'''
    # 插在最前面
    main_content = inject_code + main_content
    with open(TARGET_MAIN, 'w', encoding='utf-8', newline='\n') as f:
        f.write(main_content)
    print("✅ main_final.py 路径注入完成！")

# 2. 修改 core/adb_core.py，让它优先读取这个环境变量
TARGET_ADB = r"D:\Huijui-Toolbox-Next\core\adb_core.py"
with open(TARGET_ADB, 'r', encoding='utf-8') as f:
    adb_content = f.read()

old_header = '''if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'''

new_header = '''if 'HUIJUI_SAFE_DIR' in os.environ:
    BASE_DIR = os.environ['HUIJUI_SAFE_DIR']
elif getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'''

if old_header in adb_content:
    adb_content = adb_content.replace(old_header, new_header)
    with open(TARGET_ADB, 'w', encoding='utf-8', newline='\n') as f:
        f.write(adb_content)
    print("✅ adb_core.py 路径读取重定向完成！")
else:
    print("⚠️ adb_core.py 头部未匹配，可能之前改过了，请检查。")