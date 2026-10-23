# fix_ui_layout_final.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 恢复左侧导航栏（去掉 expand，让它回到 90 的固定宽度）
content = content.replace(
    'nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style["nav_bg"], expand=True)',
    'nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style["nav_bg"], width=90)'
)

# 2. 恢复右侧状态栏（去掉 expand，保持 320 宽度）
content = content.replace(
    'side_panel = ft.Container(\n            expand=True,\n            width=320,',
    'side_panel = ft.Container(\n            width=320,'
)
if "expand=True, width=320, bgcolor=page.ui_style[\"side_bg\"]," in content:
    content = content.replace(
        "expand=True, width=320, bgcolor=page.ui_style[\"side_bg\"],",
        "width=320, bgcolor=page.ui_style[\"side_bg\"],"
    )

# 3. 确保主容器和中间内容区完美撑满
content = content.replace(
    "main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)",
    "main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)"
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 灾难级布局已修复！左中右比例恢复完美！")