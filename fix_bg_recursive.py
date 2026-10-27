import re
import os

file_path = "ui_pages.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 匹配旧的 reset_bg 函数
pattern = re.compile(r'def reset_bg\(_\):.*?page\.update\(\)', re.DOTALL)

# 🚨 真正的递归核弹清除逻辑
new_func = '''def reset_bg(_):
    CFG.set("bg_image", "")
    page.decoration = None
    page.bgcolor = None
    
    # 🚨 终极递归清除函数
    def recursive_clear(controls):
      for ctrl in controls[:]:
        # 1. 如果是图片或视频，直接扬了
        if isinstance(ctrl, (ft.Image, ft.Video)):
          controls.remove(ctrl)
        # 2. 如果是容器，清除它的背景图，并往里挖
        elif isinstance(ctrl, ft.Container):
          if ctrl.image:
            ctrl.image = None
          if ctrl.gradient:
            ctrl.gradient = None
          if ctrl.content:
            recursive_clear([ctrl.content])
        # 3. 如果是布局组件，继续往里挖
        elif hasattr(ctrl, 'controls') and ctrl.controls:
          recursive_clear(ctrl.controls)

    # 从页面根节点开始往下挖
    recursive_clear(page.controls)
    for view in page.views:
      recursive_clear(view.controls)
      
    page.update()
    page.snack_bar = ft.SnackBar(ft.Text("✅ 壁纸已彻底清除！"), bgcolor=ft.Colors.GREEN_600)
    page.snack_bar.open = True
    page.update()'''

if pattern.search(content):
  content = pattern.sub(new_func, content)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ ui_pages.py 已注入终极递归清除逻辑！")
else:
  print("⚠️ 替换失败。")

