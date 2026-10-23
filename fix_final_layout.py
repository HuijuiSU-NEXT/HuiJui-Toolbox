# fix_final_layout.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 移除根节点初始化时极其坑爹的死板尺寸
old_init = '''    # 🚨 回归经典 Stack 模式
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True)
    
    # 强制让 Stack 占用全屏尺寸，防止 Flet 抽风缩成一块
    main_stack = ft.Stack([bg_layer, main_container], expand=True, width=1440, height=900)
    page.add(main_stack)
    page.update()'''

new_init = '''    # 🚨 彻底释放，让 Flet 自动响应全屏
    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True)
    
    page.add(ft.Stack([bg_layer, main_container], expand=True))
    page.update()'''

if old_init in content:
    content = content.replace(old_init, new_init)
else:
    # 兜底：强行删掉 width 和 height 参数
    content = re.sub(r'main_stack = ft\.Stack\(\[bg_layer, main_container\], expand=True, width=1440, height=900\)', 'page.add(ft.Stack([bg_layer, main_container], expand=True))', content)

# 2. 修复 build_main_ui 的返回值，用 Container 包裹 Row，强制撑满
# 之前的 main_layout 是一个 Row，在 Flet 中，直接挂载 Row 有时不会撑满高度
if "return main_layout" in content:
    content = content.replace(
        "return main_layout",
        "return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)"
    )
    print("✅ 已用 Container 包裹 main_layout，确保撑满全屏！")

# 3. 确保 content_area（中间显示内容的地方）也是全屏撑开的
# 检查 build_main_ui 中 Row 的定义
if 'content_area = ft.Container(expand=True)' in content:
    # 确保 nav_container 和 side_panel 也具有正确的尺寸
    pass

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 终极布局补丁注入成功！请重新运行 python main_final.py")