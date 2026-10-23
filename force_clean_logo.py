# force_clean_logo.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
changed = False

# 遍历每一行，找到包含 LOGO_B64 的那一行，直接把整行替换掉
for line in lines:
    if "LOGO_B64" in line and ("ft.Container" in line or "ft.Image" in line):
        # 提取缩进
        indent = line[:len(line) - len(line.lstrip())]
        # 纯净的 Logo 控件，去掉了所有的 border_radius, border, shadow 等等
        clean_logo = f'{indent}ft.Image(src_base64=LOGO_B64, width=48, height=48, fit=ft.ImageFit.CONTAIN),\n'
        new_lines.append(clean_logo)
        changed = True
        print(f"✅ 已替换掉旧代码，变成纯净 Logo！")
    else:
        new_lines.append(line)

if changed:
    with open(main_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("🚀 暴力清洗完毕！运行 python main_final.py 看看效果。")
else:
    print("❌ 连 LOGO_B64 都没找到！请检查文件是否损坏。")