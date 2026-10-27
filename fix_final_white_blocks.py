# fix_final_white_blocks.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")

def deep_clean(filepath):
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 干掉所有大面积的白色/浅色底
  content = content.replace('bgcolor=ft.Colors.WHITE', 'bgcolor=ft.Colors.TRANSPARENT')
  content = content.replace('bgcolor="#FFFFFF"', 'bgcolor=ft.Colors.TRANSPARENT')
  
  # 2. 把 0.1 到 0.3 透明度的白色底，全部改成深邃的玻璃黑
  # 这能干掉无线调试里那块巨大的浅灰方块
  content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\(0\.[1-3],\s*ft\.Colors\.WHITE\)', 
           'bgcolor=ft.Colors.with_opacity(0.2, "#000000"), border=ft.border.all(1, ft.Colors.with_opacity(0.2, theme_color))', 
           content)
  
  # 3. 把纯灰色的死板底色干掉
  content = content.replace('bgcolor=ft.Colors.GREY_800', 'bgcolor=ft.Colors.TRANSPARENT')
  content = content.replace('bgcolor=ft.Colors.GREY_900', 'bgcolor=ft.Colors.TRANSPARENT')
  
  # 4. 针对无线调试和模块仓库的特定灰色方块进行精准打击
  if "wireless_adb.py" in filepath:
    # 强制把那个占位的大容器变成深色玻璃
    content = content.replace('bgcolor=page.ui_style["card_bg"]', 'bgcolor=ft.Colors.with_opacity(0.2, "#000000"), border=ft.border.all(1, theme_color)')
  
  if "module_repo.py" in filepath:
    # 干掉模块仓库里卡片下方的灰色占位块
    content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\([^,]+,\s*ft\.Colors\.WHITE\)', 
             'bgcolor=ft.Colors.TRANSPARENT', content)

  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"✅ 已深度清洗: {os.path.basename(filepath)}")

# 遍历清理
for filename in os.listdir(pages_dir):
  if filename.endswith(".py") and not filename.startswith("__"):
    deep_clean(os.path.join(pages_dir, filename))

print("🚀 终极清洗完毕！请重新运行 python main_final.py。")