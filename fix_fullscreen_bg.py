# fix_fullscreen_bg.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 修复页面挂载逻辑，强制 Stack 撑满整个屏幕
old_add = "page.add(ft.Stack([bg_layer, main_container], expand=True))"
new_add = "page.add(ft.Stack([bg_layer, main_container], expand=True, width=page.window.width, height=page.window.height))"
if old_add in content:
    content = content.replace(old_add, new_add)
    print("✅ 已强制限制 Stack 为全屏尺寸！")

# 2. 修复背景图本身的尺寸问题
old_bg = '''    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        bgcolor="#0D1017" # 底色放在 Container 上
    )'''
new_bg = '''    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        bgcolor="#0D1017" # 底色放在 Container 上
    )'''
if old_bg in content:
    content = content.replace(old_bg, new_bg)
    print("✅ 已强制限制 bg_layer 为全屏尺寸！")

# 3. 修复 Image 本身，绝不允许其萎缩
old_img = '''    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )'''
new_img = '''    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        visible=False
    )'''
if old_img in content:
    content = content.replace(old_img, new_img)
    print("✅ 已强制限制 bg_image 为全屏尺寸！")

# 4. 确保 main_container 背景透明
if 'main_container = ft.Container(expand=True)' in content:
    content = content.replace('main_container = ft.Container(expand=True)', 'main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)')

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py")