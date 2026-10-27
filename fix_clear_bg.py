import re
import os

file_path = "ui_pages.py"
if not os.path.exists(file_path):
  print("❌ 找不到 ui_pages.py")
  exit()

with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 使用正则匹配原本的 reset_bg 函数（从 def reset_bg 到 page.update()）
pattern = re.compile(r'def reset_bg\(_\):.*?page\.update\(\)', re.DOTALL)

# 这是我们要注入的全新暴力清除函数
new_func = '''def reset_bg(_):
    # 1. 清空配置
    CFG.set("bg_image", "")
    
    # 2. 重置页面装饰
    page.decoration = None
    page.bgcolor = None
    
    # 🚨 3. 暴力遍历页面所有控件，只要是 Image 或 Video 直接强杀！
    for ctrl in page.controls[:]:
      if isinstance(ctrl, (ft.Image, ft.Video)):
        page.controls.remove(ctrl)
        
    # 🚨 4. 如果 UI 是写在 Stack 或 View 里的，直接拆家
    if len(page.views) > 0:
      for ctrl in page.views[0].controls[:]:
        if isinstance(ctrl, ft.Stack):
          for child in ctrl.controls[:]:
            if isinstance(child, (ft.Image, ft.Video)):
              ctrl.controls.remove(child)
              
    page.update()
    # 提示成功
    page.snack_bar = ft.SnackBar(ft.Text("✅ 壁纸已彻底清除！"), bgcolor=ft.Colors.GREEN_600)
    page.snack_bar.open = True
    page.update()'''

if pattern.search(content):
  content = pattern.sub(new_func, content)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ ui_pages.py 的清除逻辑已被彻底重写为暴力模式！")
else:
  print("⚠️ 正则没匹配到 reset_bg 函数，可能是格式又变了。")
