# fix_ugly_blocks.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")

# 定义清洗规则：干掉所有不透明的丑陋色块
def clean_page(filename):
  filepath = os.path.join(pages_dir, filename)
  if not os.path.exists(filepath): return
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 干掉模块仓库里巨大突兀的灰色方块（通常是某个内部 Container 或 TextField 加了底）
  if "module_repo.py" in filename:
    content = content.replace('bgcolor=ft.Colors.GREY_800', 'bgcolor=ft.Colors.TRANSPARENT')
    content = content.replace('bgcolor=ft.Colors.GREY_900', 'bgcolor=ft.Colors.TRANSPARENT')
    # 把底部操作区那个大灰块改成极透的磨砂白
    content = content.replace('bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)', 'bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE)')
    # 清理可能被误伤的卡片底色
    content = content.replace('bgcolor=ft.Colors.with_opacity(0.1, "#FFFFFF")', 'bgcolor=ft.Colors.with_opacity(0.02, "#FFFFFF")')

  # 2. 干掉无线调试和Scrcpy底部的巨大灰色块
  if "wireless_adb.py" in filename or "scrcpy.py" in filename:
    # 找到那个占据半个屏幕的灰色框，强制变成透明或极透黑玻璃
    content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\(0\.[1-9],\s*ft\.Colors\.WHITE\)', 'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))', content)
    content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\(0\.[1-9],\s*"#FFFFFF"\)', 'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)', content)
    content = content.replace('bgcolor=ft.Colors.GREY_800', 'bgcolor=ft.Colors.TRANSPARENT')

  # 3. 全局兜底：把所有 `ft.Colors.with_opacity(0.5 以上的灰白底)` 降级为极透玻璃
  content = re.sub(r'bgcolor=ft\.Colors\.with_opacity\(0\.[5-9],\s*ft\.Colors\.WHITE\)', 'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)', content)
  
  # 4. 强制所有 TextField（输入框）变成完全透明，只留边框
  # 这招能直接干掉很多输入框自带的白底/灰底
  content = content.replace('bgcolor=ft.Colors.GREY_900', 'bgcolor=ft.Colors.TRANSPARENT')

  with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"✅ 已彻底净化: {filename}")

# 遍历所有页面进行清洗
for filename in os.listdir(pages_dir):
  if filename.endswith(".py") and not filename.startswith("__"):
    clean_page(filename)

print("🚀 视觉牛皮癣清理完毕！请重新运行 python main_final.py。")