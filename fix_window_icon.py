# fix_window_icon.py
import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(BASE_DIR, "assets")
png_path = os.path.join(assets_dir, "logo.png")
ico_path = os.path.join(assets_dir, "logo.ico")

# 1. 用 PIL 将 PNG 转换为高分辨率 ICO 文件
if os.path.exists(png_path):
    print("⏳ 正在将 logo.png 转换为 logo.ico...")
    img = Image.open(png_path)
    # Flet 窗口图标建议使用多尺寸 ICO
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print("✅ logo.ico 生成成功！")
else:
    print("⚠️ 未找到 logo.png，请确保 assets 目录下有 logo.png")

# 2. 修改 main_final.py，设置窗口图标
main_path = os.path.join(BASE_DIR, "main_final.py")
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 找到设置窗口宽高的地方，插入图标设置
old_init = '''    page.window.width = 1440
    page.window.height = 900'''

new_init = '''    page.window.width = 1440
    page.window.height = 900
    # 🚨 核心：强制设置窗口左上角图标
    icon_path = os.path.join(BASE_DIR, "assets", "logo.ico")
    if os.path.exists(icon_path):
        page.window.icon = icon_path'''

if old_init in content:
    content = content.replace(old_init, new_init)
    print("✅ 已在 main_final.py 中注入窗口图标设置逻辑！")
else:
    print("⚠️ 未找到精确匹配的宽高设置，尝试插入到 main 函数开头...")
    # 兜底逻辑
    content = content.replace(
        'def main(page: ft.Page):\n',
        'def main(page: ft.Page):\n    icon_path = os.path.join(BASE_DIR, "assets", "logo.ico")\n    if os.path.exists(icon_path):\n        page.window.icon = icon_path\n'
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请运行 python main_final.py 检查窗口图标。")