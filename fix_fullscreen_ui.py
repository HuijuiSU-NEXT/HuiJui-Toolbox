# fix_fullscreen_ui.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 确保页面的 padding 和 spacing 为 0，避免边缘留白
if 'page.padding = 0' not in content:
    content = content.replace('page.window.height = 900', 'page.window.height = 900\n    page.padding = 0\n    page.spacing = 0')
else:
    # 强制替换现有的
    content = re.sub(r'page\.padding\s*=\s*\d+', 'page.padding = 0', content)
    content = re.sub(r'page\.spacing\s*=\s*\d+', 'page.spacing = 0', content)

# 2. 修复 main_container，强制其绝对撑满
old_init = '''    # 🚨 废弃 Stack，改用绝对隔离的系统级壁纸
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)'''

new_init = '''    # 🚨 废弃 Stack，改用绝对隔离的系统级壁纸
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)
    page.update()'''

content = content.replace(old_init, new_init)

# 3. 确保 build_main_ui 返回的容器能撑满
# 查找 build_main_ui 的 return 部分
# 之前逻辑中，main_layout 是一个 Row，它必须有 expand=True
if 'main_layout = ft.Row' in content:
    content = content.replace(
        'main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)',
        'main_layout = ft.Container(content=ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0), expand=True)'
    )

# 确保 build_main_ui 的返回值被正确挂载并刷新
if 'main_container.content = build_main_ui()' in content and 'page.update()' not in content.split('main_container.content = build_main_ui()')[1].split('if __name__')[0]:
    content = content.replace(
        'main_container.content = build_main_ui()',
        'main_container.content = build_main_ui()\n    page.update()'
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 全屏 UI 修复补丁已注入！")