import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    # 🚨 读取配置中的模糊度，如果没有则默认 10
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
