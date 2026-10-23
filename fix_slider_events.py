# fix_slider_events.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 1. 修复模糊度滑块（补齐 on_change 和修复 label）
old_blur = '''    blur_slider = ft.Slider(min=0, max=40, divisions=40, value=state["blur_radius"], active_color=theme_color, label="{value:.0f}")
    def on_blur_change(e):
        state["blur_radius"] = int(blur_slider.value)
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)'''

new_blur = '''    blur_slider = ft.Slider(min=0, max=40, divisions=40, value=state["blur_radius"], active_color=theme_color, label="{value}")
    def on_blur_change(e):
        state["blur_radius"] = int(blur_slider.value)
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
    blur_slider.on_change = on_blur_change
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)'''

if old_blur in settings_content:
    settings_content = settings_content.replace(old_blur, new_blur)
    print("✅ 模糊度滑块 on_change 事件已修复！")
else:
    print("⚠️ 未找到精确匹配的模糊度滑块代码，尝试正则替换...")
    # 用更宽容的正则
    pattern = r'blur_slider = ft\.Slider\(.*?blur_slider\.on_change_end = .*?\n'
    if re.search(pattern, settings_content, re.DOTALL):
        settings_content = re.sub(pattern, new_blur + "\n", settings_content, flags=re.DOTALL)
        print("✅ 已通过正则修复模糊度滑块！")

# 2. 修复透明度滑块（同样处理 label）
old_opacity = '''    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value:.2f}")'''
new_opacity = '''    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value}")'''
settings_content = settings_content.replace(old_opacity, new_opacity)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)

print("🎉 修复完毕！请重新运行主程序。")