# fix_ultimate_stack_again.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 替换根节点挂载逻辑
old_init = '''    # 🚨 回归最稳系统底层方案
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.TRANSPARENT
    
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)
    page.update()'''

new_init = '''    # 🚨 终极 Stack 方案：强制指定尺寸，防止缩水
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#0D1017" # 兜底深色
    
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    
    # 🚨 关键：这里强制设置 expand=True，不设死宽高，让它撑满
    main_stack = ft.Stack([bg_layer, main_container], expand=True)
    page.add(main_stack)
    page.update()'''

if old_init in content:
    content = content.replace(old_init, new_init)
else:
    # 兜底替换
    content = re.sub(r'    # 🚨 回归最稳系统底层方案.*?page\.update\(\)', new_init, content, flags=re.DOTALL)

# 2. 重写 update_wallpaper_hot，改用 Image 控件更新
old_hot = '''    def update_wallpaper_hot():
        """系统级背景终极更新法"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统级背景: {src}")
        else:
            page.decoration = None
            print("🧹 已彻底清空背景")
            
        page.update()'''

new_hot = '''    def update_wallpaper_hot():
        """Image 控件终极更新法"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            # 直接换图
            bg_image.src = src
            bg_image.visible = True
            print(f"🖼️ 已更新 Image 背景: {src}")
        else:
            bg_image.visible = False
            print("🧹 已彻底清空背景")
            
        bg_image.update()'''

content = content.replace(old_hot, new_hot)

# 3. 确保 build_main_ui 返回的 UI 也是透明的，以便透出背景
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''

new_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''

if old_return in content:
    content = content.replace(old_return, new_return)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 强制 Stack 补丁已注入！请重新运行！")