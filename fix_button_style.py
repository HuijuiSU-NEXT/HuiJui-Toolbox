# fix_button_style.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")
wireless_path = os.path.join(pages_dir, "wireless_adb.py")

# 1. 修复 wireless_adb.py
if os.path.exists(wireless_path):
  with open(wireless_path, "r", encoding="utf-8") as f:
    content = f.read()
  
  # 把 ButtonStyle 里的 border 强行换成 side (Flet 的边框属性)
  content = content.replace(
    'style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.2, "#000000"), border=ft.border.all(1, theme_color), shape=ft.RoundedRectangleBorder(radius=10), padding=15)',
    'style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.2, "#000000"), side=ft.BorderSide(1, theme_color), shape=ft.RoundedRectangleBorder(radius=10), padding=15)'
  )
  # 兜底，如果有任何 ButtonStyle 里包含 border=，一律改成 side=
  content = re.sub(r'ButtonStyle\((.*?)border=ft\.border\.all\((.*?)\)(.*?)\)', r'ButtonStyle(\1side=ft.BorderSide(\2)\3)', content)
  
  with open(wireless_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ pages/wireless_adb.py 中的 ButtonStyle 语法已修复！")

# 2. 全局扫描，把其他可能被误伤的地方也修一下
for filename in os.listdir(pages_dir):
  if filename.endswith(".py") and not filename.startswith("__"):
    filepath = os.path.join(pages_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
      c = f.read()
    
    # 把错误写法统统改掉
    c = re.sub(r'ButtonStyle\((.*?)border=ft\.border\.all\((.*?)\)(.*?)\)', r'ButtonStyle(\1side=ft.BorderSide(\2)\3)', c)
    
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(c)

print("🚀 修复完毕！请重新运行 python main_final.py")