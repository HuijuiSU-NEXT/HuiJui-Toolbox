# fix_kill_stack.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 彻底干掉背景层的 Stack，回归纯净的 main_container
old_init = '''    # 🚨 终极物理镇压：强制使用绝对宽高的容器
    bg_layer = ft.Container(
        left=0, top=0, right=0, bottom=0,
        bgcolor="#0D1017"
    )
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer.content = bg_image
    
    main_container = ft.Container(
        left=0, top=0, right=0, bottom=0
    )
    
    page.add(ft.Stack([bg_layer, main_container], expand=True))
    page.update()'''

new_init = '''    # 🚨 彻底解放 UI，废掉 Stack，直接挂载 UI 容器
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)
    page.update()'''

if old_init in content:
    content = content.replace(old_init, new_init)
else:
    # 暴力正则干掉 Stack 那一段
    content = re.sub(r'    # 🚨 终极物理镇压.*?page\.update\(\)', new_init, content, flags=re.DOTALL)
    print("✅ 已通过正则强制移除了 Stack 挂载代码！")

# 2. 重写 update_wallpaper_hot，直连 page.decoration
old_hot = '''    def update_wallpaper_hot():
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

new_hot = '''    def update_wallpaper_hot():
        """直连系统底层，更新 page.decoration，无视 UI 树重构"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 加上时间戳破缓存，保证秒切
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统级壁纸: {src}")
        else:
            page.decoration = None
            print("❌ 未找到壁纸文件，清空背景")
        page.update()'''

content = content.replace(old_hot, new_hot)

# 3. 确保 main_layout 的 Container 完美撑满
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return main_layout'''

new_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''

content = content.replace(old_return, new_return)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 系统级壁纸直连方案注入成功！请重新运行 python main_final.py")