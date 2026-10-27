# fix_rescue_buttons.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rescue_path = os.path.join(BASE_DIR, "pages", "rescue.py")

if os.path.exists(rescue_path):
  with open(rescue_path, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 修复“选择脚本并执行”按钮 (青色)
  # 匹配原本有可能是实心的 style
  old_style_cyan = r'style=ft\.ButtonStyle\(color="#000000", bgcolor=theme_color, shape=ft\.RoundedRectangleBorder\(radius=10\), padding=15\)'
  new_style_cyan = '''style=ft.ButtonStyle(
    color=theme_color, 
    bgcolor=ft.Colors.with_opacity(0.2, theme_color), 
    side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, theme_color)), 
    shape=ft.RoundedRectangleBorder(radius=10), 
    padding=ft.padding.symmetric(horizontal=20, vertical=12), 
    elevation=0
  )'''
  content = re.sub(old_style_cyan, new_style_cyan, content)

  # 2. 修复“启动 MTKClient”按钮 (橙色)
  # 匹配实心橙色按钮
  old_style_orange = r'style=ft\.ButtonStyle\(color="white", bgcolor=ft\.Colors\.ORANGE_700, shape=ft\.RoundedRectangleBorder\(radius=10\), padding=15\)'
  new_style_orange = '''style=ft.ButtonStyle(
    color=ft.Colors.ORANGE_300, 
    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_500), 
    side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, ft.Colors.ORANGE_500)), 
    shape=ft.RoundedRectangleBorder(radius=10), 
    padding=ft.padding.symmetric(horizontal=20, vertical=12), 
    elevation=0
  )'''
  content = re.sub(old_style_orange, new_style_orange, content)

  # 3. 兼容其他可能被重写过的实心按钮格式
  content = content.replace(
    'bgcolor=theme_color, color="#000000"', 
    'bgcolor=ft.Colors.with_opacity(0.2, theme_color), color=theme_color, side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, theme_color))'
  )
  content = content.replace(
    'bgcolor=ft.Colors.ORANGE_700, color="white"', 
    'bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_500), color=ft.Colors.ORANGE_300, side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, ft.Colors.ORANGE_500))'
  )

  with open(rescue_path, "w", encoding="utf-8") as f:
    f.write(content)

  print("✅ 急救中心页面的青、橙双色按钮已彻底玻璃化！")
else:
  print("❌ 找不到 pages/rescue.py")