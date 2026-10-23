# fix_custom_blur.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ui_theme_path = os.path.join(BASE_DIR, "ui_theme.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 修改 ui_theme.py：读取动态模糊度 ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    # 🚨 从配置中读取模糊度，默认设为 10
    blur_val = CFG.get("blur_radius", 10)
    
    if material == "frosted":
        return {
            "type": "frosted",
            "overlay_bg": ft.Colors.with_opacity(0.1, "#0D1017"),
            "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
            "nav_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }
    elif material == "liquid":
        return {
            "type": "liquid",
            "overlay_bg": ft.LinearGradient(
                colors=[ft.Colors.with_opacity(0.05, theme_color), ft.Colors.with_opacity(0.2, "#0D1017")]
            ),
            "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
            "nav_bg": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_border": ft.border.all(2, ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            "log_color": theme_color
        }
    else:
        return {
            "type": "default",
            "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "overlay_blur": None,
            "nav_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "side_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }

def setup_page_style(page: ft.Page):
    theme_color = CFG.get("theme_color", "#39C5BB")
    page.bgcolor = ft.Colors.TRANSPARENT
    return theme_color
'''

with open(ui_theme_path, "w", encoding="utf-8") as f:
    f.write(ui_theme_code)
print("✅ ui_theme.py 已支持动态模糊度读取！")


# ==================== 2. 修改 settings.py：加入模糊度滑块 ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 插入滑块定义（加在透明度滑块后面）
slider_logic = '''
    # 🚨 新增：全局模糊度滑块
    blur_slider = ft.Slider(
        min=0, max=40, divisions=40, 
        value=CFG.get("blur_radius", 10), 
        active_color=theme_color, 
        label="{value:.0f}"
    )
    def on_blur_change(e):
        # 拖动时不刷新，松开鼠标才保存并刷新，防止卡死
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value:.2f}")
    def on_opacity_change(e):
        state["card_opacity"] = opacity_slider.value
        CFG.set("card_opacity", opacity_slider.value)
        CFG.save()
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)
    opacity_slider.on_change = on_opacity_change
'''

# 找到原有的 opacity_slider 定义并替换
import re
settings_content = re.sub(
    r'    opacity_slider = ft\.Slider\(.*?opacity_slider\.on_change = on_opacity_change',
    slider_logic,
    settings_content, flags=re.DOTALL
)

# 在 UI 里渲染模糊度滑块（加在视觉特效卡片里）
old_card4 = '''    card_step4 = make_card("视觉特效微调", ft.Icons.AUTO_AWESOME, [
        ft.Row([
            ft.Column([
                ft.Text("卡片透明度", size=14, color="white"),
                ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)
            ]),
            ft.Container(expand=True),
            ft.Container(content=opacity_slider, width=300)
        ])
    ])'''

new_card4 = '''    card_step4 = make_card("视觉特效微调", ft.Icons.AUTO_AWESOME, [
        ft.Row([
            ft.Column([
                ft.Text("全局模糊度", size=14, color="white"),
                ft.Text("调节毛玻璃/液态玻璃的背景模糊程度 (0 为关闭)", size=11, color=ft.Colors.GREY_500)
            ]),
            ft.Container(expand=True),
            ft.Container(content=blur_slider, width=300)
        ]),
        ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=15),
        ft.Row([
            ft.Column([
                ft.Text("卡片透明度", size=14, color="white"),
                ft.Text("调节背景卡片的不透明度", size=11, color=ft.Colors.GREY_500)
            ]),
            ft.Container(expand=True),
            ft.Container(content=opacity_slider, width=300)
        ])
    ])'''

settings_content = settings_content.replace(old_card4, new_card4)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)
print("✅ settings.py 已加入模糊度调节滑块！")

print("🎉 完美！现在你可以自由控制毛玻璃的糊度了，0 就是完全清晰，40 是极致磨砂！")