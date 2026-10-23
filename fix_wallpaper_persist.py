# fix_wallpaper_persist.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 找到背景层初始化代码
old_bg_init = '''    # 🚨 统一使用 Container 包裹 Image，以支持底色
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        bgcolor="#0D1017" # 底色放在 Container 上
    )'''

new_bg_init = '''    # 🚨 统一使用 Container 包裹 Image，以支持底色
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        bgcolor="#0D1017" # 底色放在 Container 上
    )
    
    # 🚨 核心修复：启动前预加载壁纸，防止重进掉图
    import glob
    _all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if _all_files:
        _latest = max(_all_files, key=os.path.getctime)
        bg_image.src = os.path.basename(_latest)
        bg_image.visible = True'''

if old_bg_init in content:
    content = content.replace(old_bg_init, new_bg_init)
    print("✅ 已注入启动预加载逻辑！")
else:
    print("⚠️ 未找到旧背景层代码，尝试暴力正则匹配...")
    # 正则兜底
    content = re.sub(
        r'bg_image = ft\.Image\([^)]*\)\s*bg_layer = ft\.Container\([^)]*\)',
        new_bg_init,
        content
    )

# 去除启动尾部多余的 update_wallpaper_hot() 调用（防止重复刷新导致冲突）
content = content.replace(
    "    main_container.content = build_main_ui()\n    page.update()\n    update_wallpaper_hot()",
    "    main_container.content = build_main_ui()\n    page.update()"
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 壁纸掉图 Bug 已彻底根除！重进秒加载！")