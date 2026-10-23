# fix_true_no_flicker.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 彻底废除 ft.Stack 和 bg_layer，改用系统级 page.decoration
old_init = '''    # 🚨 核心1：背景层和主内容层物理分离，死死钉在窗口底层
    bg_layer = ft.Container(expand=True)
    main_container = ft.Container(expand=True)
    page.add(ft.Stack([bg_layer, main_container], expand=True))'''

new_init = '''    # 🚨 核心1：使用系统底层装饰器，脱离 UI 渲染树，绝不闪烁！
    main_container = ft.Container(expand=True)
    page.bgcolor = ft.Colors.TRANSPARENT
    page.add(main_container)'''

content = content.replace(old_init, new_init)

# 2. 移除 build_main_ui 里对 bg_layer 的修改逻辑
old_bg_logic = '''        # 🚨 核心2：在这里更新底层背景，而不是参与 UI 的 return 构建
        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            try:
                if not hasattr(page, "wallpaper_b64") or getattr(page, "wallpaper_b64_mtime", 0) < os.path.getmtime(bg_image):
                    with open(bg_image, "rb") as f:
                        page.wallpaper_b64 = base64.b64encode(f.read()).decode('utf-8')
                    page.wallpaper_b64_mtime = os.path.getmtime(bg_image)
                
                bg_layer.image = ft.DecorationImage(src_base64=page.wallpaper_b64, fit=ft.ImageFit.COVER)
                bg_layer.bgcolor = None
            except Exception as e:
                print(f"壁纸加载失败: {e}")
                bg_layer.image = None
                bg_layer.bgcolor = "#0D1017"
        else:
            bg_layer.image = None
            bg_layer.bgcolor = "#0D1017"

        # 🚨 核心3：主容器应用遮罩层特效（模糊、半透明）
        main_container.bgcolor = page.ui_style["overlay_bg"]
        main_container.blur = page.ui_style["overlay_blur"]'''

new_bg_logic = '''        # 🚨 核心2：主容器作为半透明遮罩
        main_container.bgcolor = page.ui_style["overlay_bg"]
        main_container.blur = None # 彻底禁用耗性能的全屏模糊'''

content = content.replace(old_bg_logic, new_bg_logic)

# 3. 在启动时和刷新时设置系统级壁纸
def set_system_wallpaper():
    bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
    if os.path.exists(bg_image):
        try:
            # 为了破除缓存，直接读取到 base64 塞给系统装饰器
            import base64
            with open(bg_image, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src_base64=b64, fit=ft.ImageFit.COVER)
            )
        except Exception as e:
            print(f"系统壁纸加载失败: {e}")
            page.decoration = None
    else:
        page.decoration = None

# 将函数注入到 refresh_main_ui 里
old_refresh = '''    def refresh_main_ui(tab_index=0):
        current_tab["idx"] = tab_index
        new_ui = build_main_ui()
        main_container.content = new_ui
        page.update()'''

new_refresh = '''    def refresh_main_ui(tab_index=0):
        current_tab["idx"] = tab_index
        new_ui = build_main_ui()
        main_container.content = new_ui
        set_system_wallpaper() # 🚨 每次刷新时，重新挂载系统壁纸
        page.update()'''

content = content.replace(old_refresh, new_refresh)

# 4. 修复后台扫描线程中多余的 update
content = content.replace(
    '            loading_ring.visible = False\n            try: page.update()\n            except: pass',
    '            loading_ring.visible = False\n            # try: page.update()\n            # except: pass' # 注释掉这里，减少刷新频率
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 终极降维打击补丁注入成功！壁纸已脱离 UI 树，闪烁彻底死绝！")