# fix_global_ui_cleaner.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")
theme_path = os.path.join(BASE_DIR, "ui_theme.py")

# ==================== 1. 强化 ui_theme.py：按亮度智能分配颜色 ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
  material = CFG.get("ui_material", "default")
  blur_val = CFG.get("blur_radius", 10)
  brightness = CFG.get("bg_brightness", 128)
  
  # 智能判断背景亮度，决定底色和边框
  if brightness > 150:
    # 浅色壁纸：用黑玻璃防瞎眼
    base_card_bg = ft.Colors.with_opacity(0.35, "#000000")
    base_border = ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE))
    nav_bg = ft.Colors.with_opacity(0.25, "#000000")
    log_bg = ft.Colors.with_opacity(0.65, "#000000") # 终端黑框更深，保证绿字可见
  else:
    # 深色壁纸：用白玻璃，清透高级
    base_card_bg = ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
    base_border = ft.border.all(1.5, ft.Colors.with_opacity(0.6, ft.Colors.WHITE))
    nav_bg = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
    log_bg = ft.Colors.with_opacity(0.3, "#000000")

  if material == "liquid":
    if brightness > 150:
      card_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
        colors=[ft.Colors.with_opacity(0.3, "#000000"), ft.Colors.with_opacity(0.1, "#000000")]
      )
    else:
      card_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
        colors=[ft.Colors.with_opacity(0.15, ft.Colors.WHITE), ft.Colors.with_opacity(0.02, ft.Colors.WHITE)]
      )
      
    return {
      "type": "liquid",
      "overlay_bg": ft.Colors.with_opacity(0.05, "#0D1017"),
      "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
      "nav_bg": nav_bg, "side_bg": nav_bg,
      "card_bg": card_gradient, "card_border": base_border,
      "log_bg": log_bg, "log_color": theme_color
    }
  else:
    return {
      "type": "default",
      "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
      "overlay_blur": None,
      "nav_bg": ft.Colors.with_opacity(0.4, "#0D1017"), "side_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
      "card_bg": base_card_bg, "card_border": base_border,
      "log_bg": log_bg, "log_color": "#00FFD1"
    }

def setup_page_style(page: ft.Page):
  theme_color = CFG.get("theme_color", "#39C5BB")
  page.bgcolor = ft.Colors.TRANSPARENT
  return theme_color
'''
with open(theme_path, "w", encoding="utf-8") as f:
  f.write(ui_theme_code)
print("✅ ui_theme.py 已升级：智能分配深浅玻璃色！")

# ==================== 2. 暴力净化 pages 目录下的所有页面 ====================
def clean_page(filename):
  filepath = os.path.join(pages_dir, filename)
  if not os.path.exists(filepath): return
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  # 🚨 统一替换所有的硬编码底色和边框
  # 1. 干掉纯黑框，换成动态的 log_bg
  content = content.replace('bgcolor=ft.Colors.BLACK', 'bgcolor=page.ui_style["log_bg"]')
  content = content.replace('bgcolor="#05070A"', 'bgcolor=page.ui_style["log_bg"]')
  content = content.replace('bgcolor="#1A233A"', 'bgcolor=page.ui_style["log_bg"]')
  
  # 2. 干掉死白卡片底，换成动态的 card_bg
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)', 'bgcolor=page.ui_style["card_bg"]')
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)', 'bgcolor=page.ui_style["card_bg"]')
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE)', 'bgcolor=page.ui_style["card_bg"]')
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.1, theme_color)', 'bgcolor=page.ui_style["card_bg"]')
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.15, theme_color)', 'bgcolor=page.ui_style["card_bg"]')
  
  # 3. 干掉各种乱七八糟的边框，统一发光玻璃边框
  content = content.replace('border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))', 'border=page.ui_style["card_border"]')
  content = content.replace('border=ft.border.all(1, ft.Colors.with_opacity(0.2, theme_color))', 'border=page.ui_style["card_border"]')
  content = content.replace('border=ft.border.all(1, ft.Colors.with_opacity(0.3, theme_color))', 'border=page.ui_style["card_border"]')
  content = content.replace('border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE))', 'border=page.ui_style["card_border"]')
  content = content.replace('border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))', 'border=page.ui_style["card_border"]')

  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"✅ 已净化: {filename}")

# 遍历 pages 下的所有 .py 文件
for filename in os.listdir(pages_dir):
  if filename.endswith(".py") and not filename.startswith("__"):
    clean_page(filename)

print("🚀 全局 UI 净化完毕！所有页面底色和边框已彻底统一！")