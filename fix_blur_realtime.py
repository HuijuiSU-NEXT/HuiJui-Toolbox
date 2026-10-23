# fix_blur_realtime.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 移除原本独立在外面的 overlay_layer
old_layer = '''    # 2. 遮罩层（永不重建，只换颜色）
    overlay_layer = ft.Container(expand=True)
    # 3. 主界面层（只换这里面的 content）
    main_container = ft.Container(expand=True)
    
    # 挂载不可变 Stack，整个 APP 生命周期只执行这一次！
    page.add(ft.Stack([bg_layer, overlay_layer, main_container], expand=True))'''

new_layer = '''    # 2. 主界面容器 (遮罩层和 UI 都在这里面，随刷新重建)
    main_container = ft.Container(expand=True)
    
    # 挂载不可变 Stack：只有壁纸是钉死的，其他都在 main_container 里
    page.add(ft.Stack([bg_layer, main_container], expand=True))'''

content = content.replace(old_layer, new_layer)

# 2. 在 build_main_ui 里，把遮罩层加进去
old_build = '''        overlay_layer.bgcolor = page.ui_style["overlay_bg"]
        overlay_layer.blur = page.ui_style["overlay_blur"]
        # 更新遮罩层不需要触发整个 page.update()，只更新它自己
        overlay_layer.update()'''

new_build = '''        # 构建动态遮罩层
        overlay_layer = ft.Container(
            bgcolor=page.ui_style["overlay_bg"],
            blur=page.ui_style["overlay_blur"],
            expand=True
        )'''

content = content.replace(old_build, new_build)

# 3. 在最终返回时，把遮罩层和主布局打包成 Stack 返回
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)

        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''

new_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)

        # 🚨 把遮罩层和 UI 层一起打包返回
        return ft.Stack([overlay_layer, main_layout], expand=True)'''

content = content.replace(old_return, new_return)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 模糊度热更新补丁已注入！现在只要滑动滑块，松手立刻变清晰！")