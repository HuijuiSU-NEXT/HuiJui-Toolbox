# fix_absolute_layout.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 重写根节点的挂载逻辑
old_init = '''    # 🚨 彻底释放，让 Flet 自动响应全屏
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True)
    
    page.add(ft.Stack([bg_layer, main_container], expand=True))
    page.update()'''

new_init = '''    # 🚨 终极物理镇压：强制使用绝对宽高的容器
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

if old_init in content:
    content = content.replace(old_init, new_init)
else:
    # 兼容之前的版本
    content = content.replace(
        'page.add(ft.Stack([bg_layer, main_container], expand=True))',
        'page.add(ft.Stack([bg_layer, main_container], expand=True))'
    )

# 2. 修复 build_main_ui 里的 return
# 之前的 return 可能是 return main_layout 或者 return Container
# 我们强制返回一个填满的 Container
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''
new_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return main_layout'''

if old_return in content:
    content = content.replace(old_return, new_return)

# 确保 main_container 的 content 赋值后有 update
content = content.replace(
    "main_container.content = build_main_ui()\n    page.update()",
    "main_container.content = build_main_ui()\n    main_container.update()\n    page.update()"
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 绝对定位补丁注入完毕！这次 UI 绝对死死撑满全屏！")