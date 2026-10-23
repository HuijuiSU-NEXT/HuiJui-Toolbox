# fix_realtime_blur.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# 1. 在 main_final.py 中暴露一个局部更新遮罩层的函数
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# 插入 update_overlay_blur 函数
old_init = '''    page.update_wallpaper_hot = update_wallpaper_hot
    update_wallpaper_hot() # 初始化'''

new_init = '''    page.update_wallpaper_hot = update_wallpaper_hot
    update_wallpaper_hot() # 初始化

    # 🚨 新增：供 settings 调用的局部更新模糊度函数（不触发全局重建）
    def update_overlay_blur(val):
        theme_color = ui_theme.setup_page_style(page)
        page.ui_style = ui_theme.get_ui_styles(theme_color)
        # 找到现有的遮罩层并只更新它的属性
        for control in main_container.content.controls:
            if isinstance(control, ft.Stack):
                for stack_control in control.controls:
                    if isinstance(stack_control, ft.Container) and stack_control.blur is not None:
                        stack_control.blur = page.ui_style["overlay_blur"]
                        stack_control.update()
                        return

    page.update_overlay_blur = update_overlay_blur'''

main_content = main_content.replace(old_init, new_init)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)
print("✅ main_final.py 已注入局部模糊更新接口！")


# 2. 修改 settings.py 滑块事件，实现实时滑动
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

old_blur_change = '''    def on_blur_change(e):
        state["blur_radius"] = int(blur_slider.value)
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
    blur_slider.on_change = on_blur_change
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)'''

new_blur_change = '''    def on_blur_change(e):
        state["blur_radius"] = int(blur_slider.value)
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
        # 🚨 核心：滑动时直接调用局部更新，不重建 UI，绝对不闪！
        if hasattr(page, "update_overlay_blur"):
            page.update_overlay_blur(int(blur_slider.value))
    blur_slider.on_change = on_blur_change
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)'''

settings_content = settings_content.replace(old_blur_change, new_blur_change)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)

print("✅ settings.py 模糊度滑块已支持实时滑动更新！")