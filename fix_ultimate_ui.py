# fix_ultimate_ui.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")

# ==================== 核心清洗逻辑 ====================
def clean_file(filepath):
  if not os.path.exists(filepath): return
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 干掉所有死黑/灰背景，统一改成透明或极透的玻璃色
  # 处理 TextField 和 Textbox
  content = content.replace('bgcolor=ft.Colors.BLACK', 'bgcolor=ft.Colors.with_opacity(0.1, "#000000")')
  content = content.replace('bgcolor="#05070A"', 'bgcolor=ft.Colors.with_opacity(0.1, "#000000")')
  content = content.replace('bgcolor=ft.Colors.TRANSPARENT', 'bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF")')
  
  # 处理模块仓库里突兀的灰底方块
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.1, "#FFFFFF")', 'bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF")')
  content = content.replace('bgcolor=ft.Colors.with_opacity(0.2, "#FFFFFF")', 'bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF")')

  # 2. 给所有大色块加上统一的液态玻璃边框
  content = re.sub(r'bgcolor=ft\.Colors\.BLACK\)', 'bgcolor=ft.Colors.with_opacity(0.1, "#000000"), border=ft.border.all(1, ft.Colors.with_opacity(0.3, theme_color)))', content)

  # 3. 强制清理 Scrcpy 页面可能存在的巨大黑色 Container
  if "scrcpy.py" in filepath:
    content = content.replace('bgcolor=ft.Colors.BLACK', 'bgcolor=ft.Colors.TRANSPARENT')
    content = content.replace('bgcolor="#05070A"', 'bgcolor=ft.Colors.TRANSPARENT')
    # 确保不要有大面积的死板底色
    content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\(.*?\)', 'bgcolor=ft.Colors.TRANSPARENT', content)

  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# ==================== 遍历所有页面文件 ====================
for filename in os.listdir(pages_dir):
  if filename.endswith(".py") and filename != "__init__.py":
    clean_file(os.path.join(pages_dir, filename))
    print(f"✅ 已深度清洗: {filename}")

# ==================== 修复 main_final.py 的导航栏 ====================
main_path = os.path.join(BASE_DIR, "main_final.py")
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

# 强制修复导航栏图标和文字颜色
old_nav = '''selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=13, font_family="MiSans"),
      unselected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE70, size=12, font_family="MiSans"),'''
new_nav = '''selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.W_900, size=13, font_family="MiSans"),
      unselected_label_text_style=ft.TextStyle(color="#FFFFFF", weight=ft.FontWeight.W_700, size=12, font_family="MiSans"),'''

if old_nav in m_content:
  m_content = m_content.replace(old_nav, new_nav)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(m_content)

print("🚀 全局 UI 净化完毕！黑框灰底已被彻底消灭！请重新运行 python main_final.py。")