import re
import os

file_path = "ui_pages.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 匹配现有的 reset_bg 函数
pattern = re.compile(r'def reset_bg\(_\):.*?page\.update\(\)', re.DOTALL)

new_func = '''def reset_bg(_):
    # 1. 彻底清空壁纸配置
    CFG.set("bg_image", "")
    
    # 2. 🚨 终极必杀：关闭默认壁纸开关！让它无图可加载！
    CFG.set("use_default_wallpaper", False)
    
    # 3. 触发主界面的壁纸刷新逻辑
    if hasattr(page, 'update_wallpaper_hot'):
      page.update_wallpaper_hot()
      
    # 4. 顺手清理页面装饰
    page.decoration = None
    page.update()
    
    page.snack_bar = ft.SnackBar(ft.Text("✅ 壁纸已彻底清除（已禁用默认壁纸）"), bgcolor=ft.Colors.GREEN_600)
    page.snack_bar.open = True
    page.update()'''

if pattern.search(content):
  content = pattern.sub(new_func, content)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ ui_pages.py 清除逻辑已被完美修正！")
else:
  print("⚠️ 未找到 reset_bg 函数，尝试直接追加...")
