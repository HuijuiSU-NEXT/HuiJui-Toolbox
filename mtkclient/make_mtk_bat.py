# make_mtk_bat.py
import os

# 当前在 mtkclient 目录下，获取它的绝对路径
MTK_DIR = os.getcwd()
# 项目根目录 (即上一级)
PROJECT_ROOT = os.path.dirname(MTK_DIR)
# 目标 bin 目录
BIN_MTK_DIR = os.path.join(PROJECT_ROOT, "bin", "MTKClient")
os.makedirs(BIN_MTK_DIR, exist_ok=True)

# 生成 bat 脚本内容
bat_content = f"""@echo off
cd /d "{MTK_DIR}"
call "{os.path.join(PROJECT_ROOT, "venv", "Scripts", "activate.bat")}"
python mtk_gui.py
pause
"""

# 写入文件
bat_path = os.path.join(BIN_MTK_DIR, "mtk_gui.bat")
with open(bat_path, "w", encoding="utf-8") as f:
    f.write(bat_content)

print(f"✅ 一键启动脚本已成功生成！路径: {bat_path}")