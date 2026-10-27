import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
  material = CFG.get("ui_material", "default")
  blur_val = CFG.get("blur_radius", 10)
  brightness = CFG.get("bg_brightness", 128)
  
  # 智能判断背景亮度，决定底色和边框
  if brightness > 150:
    # 浅色壁纸：用黑玻璃防瞎眼
    base_card_bg = ft.Colors.with_opacity(0.35, "#000000")
    base_border = ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE))
    nav_bg = ft.Colors.with_opacity(0.25, "#000000")
    log_bg = ft.Colors.with_opacity(0.65, "#000000") # 终端黑框更深，保证绿字可见
  else:
    # 深色壁纸：用白玻璃，清透高级
    base_card_bg = ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
    base_border = ft.border.all(1.5, ft.Colors.with_opacity(0.6, ft.Colors.WHITE))
    nav_bg = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
    log_bg = ft.Colors.with_opacity(0.3, "#000000")

  if material == "liquid":
    if brightness > 150:
      card_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
        colors=[ft.Colors.with_opacity(0.3, "#000000"), ft.Colors.with_opacity(0.1, "#000000")]
      )
    else:
      card_gradient = ft.LinearGradient(
        begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
        colors=[ft.Colors.with_opacity(0.15, ft.Colors.WHITE), ft.Colors.with_opacity(0.02, ft.Colors.WHITE)]
      )
      
    return {
      "type": "liquid",
      "overlay_bg": ft.Colors.with_opacity(0.05, "#0D1017"),
      "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
      "nav_bg": nav_bg, "side_bg": nav_bg,
      "card_bg": card_gradient, "card_border": base_border,
      "log_bg": log_bg, "log_color": theme_color
    }
  else:
    return {
      "type": "default",
      "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
      "overlay_blur": None,
      "nav_bg": ft.Colors.with_opacity(0.4, "#0D1017"), "side_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
      "card_bg": base_card_bg, "card_border": base_border,
      "log_bg": log_bg, "log_color": "#00FFD1"
    }

def setup_page_style(page: ft.Page):
  theme_color = CFG.get("theme_color", "#39C5BB")
  page.bgcolor = ft.Colors.TRANSPARENT
  return theme_color
