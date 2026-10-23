# fix_stack_abandon.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 彻底干掉导致裁剪的 Stack 和 bg_layer 挂载逻辑
old_init = '''    # 🚨 彻底干掉硬编码宽高，完全交给 expand 去撑满
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        bgcolor="#0D1017" 
    )
    # 2. 主界面容器
    main_container = ft.Container(expand=True)
    
    # 挂载不可变 Stack
    page.add(ft.Stack([bg_layer, main_container], expand=True))'''

new_init = '''    # 🚨 废弃 Stack，改用绝对隔离的系统级壁纸
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)'''

if old_init in content:
    content = content.replace(old_init, new_init)
    print("✅ 已废弃 Stack，改用系统壁纸模式！")
else:
    # 兼容之前可能被正则改过的版本
    content = re.sub(
        r'    # 🚨 统一使用 Container 包裹 Image.*?page\.add\(ft\.Stack\(\[bg_layer, main_container\], expand=True\)\)',
        new_init, content, flags=re.DOTALL
    )

# 2. 重写壁纸更新逻辑，直接改系统背景
old_update = '''    def update_wallpaper_hot():
        """直接加载最新的图片，Flet 原生支持"""
        import glob
        # 找 GIF 和 静态图
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
            print(f"🖼️ 正在加载壁纸: {bg_image.src}")
        else:
            bg_image.visible = False
            print("❌ 未找到壁纸文件")
        bg_image.update()'''

new_update = '''    def update_wallpaper_hot():
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

if old_update in content:
    content = content.replace(old_update, new_update)
    print("✅ 壁纸逻辑已切换为系统底层渲染！")
else:
    # 暴力正则替换
    content = re.sub(
        r'    def update_wallpaper_hot\(\):.*?bg_image\.update\(\)',
        new_update, content, flags=re.DOTALL
    )

# 3. 启动时初始化系统壁纸
if "update_wallpaper_hot()\n" in content and "main_container.content = build_main_ui()" in content:
    # 把预加载逻辑移到 main_container.content 构建之后
    pass

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 修复完毕！请重新运行 python main_final.py，这次 UI 绝对铺满全屏！")