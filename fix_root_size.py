# fix_root_size.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 彻底废弃 page.decoration，回退到用 Container 包背景
old_update = '''    def update_wallpaper_hot():
        """通过 page.decoration 直接设置系统级底层壁纸，绝不影响 UI"""
        import glob
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 提取相对路径
            src = os.path.basename(latest)
            # 强制加时间戳破缓存
            import time
            src = f"{src}?t={int(time.time())}"
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统底层壁纸: {src}")
        else:
            page.decoration = None
            print("❌ 未找到壁纸文件，清空背景")
        page.update()'''

new_update = '''    def update_wallpaper_hot():
        """通过 Image 更新背景"""
        import glob
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = os.path.basename(latest)
            bg_image.src = src
            bg_image.visible = True
            print(f"🖼️ 已更新背景图: {src}")
        else:
            bg_image.visible = False
            print("❌ 未找到壁纸文件，清空背景")
        bg_image.update()'''

content = content.replace(old_update, new_update)

# 2. 重建根节点，强制全屏
old_init = '''    # 🚨 废弃 Stack，改用绝对隔离的系统级壁纸
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)
    page.update()'''

new_init = '''    # 🚨 回归经典 Stack 模式
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True)
    
    # 强制让 Stack 占用全屏尺寸，防止 Flet 抽风缩成一块
    main_stack = ft.Stack([bg_layer, main_container], expand=True, width=1440, height=900)
    page.add(main_stack)
    page.update()'''

content = content.replace(old_init, new_init)

# 3. 确保 build_main_ui 返回正确的撑满结构
# 移除之前为了避免报错加的空 Container
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''
new_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return main_layout'''

if old_return in content:
    content = content.replace(old_return, new_return)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 根节点全屏补丁已注入！强制撑开 1440x900！")