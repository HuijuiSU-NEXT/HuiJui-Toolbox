# fix_material_safe.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 1. 重写 ui_theme.py (放弃危险渐变，改用纯色高光) ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    opacity = CFG.get("card_opacity", 0.15)
    
    if material == "frosted":
        return {
            "nav_bg": ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            "nav_blur": ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
            "side_bg": ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            "side_blur": ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
            "card_bg": ft.Colors.with_opacity(opacity + 0.1, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "log_color": "#000000" # 毛玻璃模式下日志用黑字
        }
    elif material == "liquid":
        return {
            "nav_bg": ft.Colors.with_opacity(0.15, theme_color),
            "nav_blur": None,
            "side_bg": ft.Colors.with_opacity(0.15, theme_color),
            "side_blur": None,
            "card_bg": ft.Colors.with_opacity(0.08, theme_color),
            # 改用 1px 细边框，不用 2px 免得像跑马灯
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.8, theme_color)), 
            "log_bg": ft.Colors.with_opacity(0.1, theme_color),
            "log_color": theme_color
        }
    else:
        return {
            "nav_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "nav_blur": None,
            "side_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "side_blur": None,
            "card_bg": ft.Colors.with_opacity(opacity, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }

def setup_page_style(page: ft.Page):
    theme_color = CFG.get("theme_color", "#39C5BB")
    # 确保页面背景透明，让壁纸透出来
    page.bgcolor = ft.Colors.TRANSPARENT
    return theme_color
'''

with open("ui_theme.py", "w", encoding="utf-8") as f:
    f.write(ui_theme_code)
print("✅ ui_theme.py 已重写为安全材质！")

# ==================== 2. 修复 settings.py (解决灰色色块问题) ====================
settings_code = '''import flet as ft
import os
import re
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
    state = {
        "theme_color": CFG.get("theme_color", "#39C5BB"),
        "ui_material": CFG.get("ui_material", "default"),
        "card_opacity": CFG.get("card_opacity", 0.15)
    }

    def show_snackbar(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=theme_color)
        page.snack_bar.open = True
        page.update()

    color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))
    color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])

    def apply_color(e):
        hex_val = color_input.value.strip()
        if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
            state["theme_color"] = hex_val
            color_preview.bgcolor = hex_val
            CFG.set("theme_color", hex_val)
            CFG.save()
            show_snackbar("颜色已应用，正在刷新...")
            if hasattr(page, "refresh_main_ui"):
                page.refresh_main_ui(tab_index=4)
        else:
            color_input.error_text = "格式错误"
        page.update()

    color_input.on_submit = apply_color

    material_dropdown = ft.Dropdown(
        label="UI 材质风格",
        value=state["ui_material"],
        width=300,
        bgcolor="#1A233A", # 固定深色底防止渲染透明
        color="white",
        options=[
            ft.dropdown.Option("default", "默认 (纯色/清晰)"),
            ft.dropdown.Option("frosted", "毛玻璃 (半透明白)"),
            ft.dropdown.Option("liquid", "液态玻璃 (主题色微光)"),
        ],
        on_change=lambda e: apply_material(e.control.value)
    )

    def apply_material(val):
        state["ui_material"] = val
        CFG.set("ui_material", val)
        CFG.save()
        show_snackbar(f"材质已切换: {val}")
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)

    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value:.2f}")
    def on_opacity_change(e):
        state["card_opacity"] = opacity_slider.value
        CFG.set("card_opacity", opacity_slider.value)
        CFG.save()
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)
    opacity_slider.on_change = on_opacity_change

    def make_card(title, icon, content_list):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=theme_color, size=20), ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white")]),
                ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE), height=10),
                *content_list
            ], spacing=15),
            bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
            border_radius=15, padding=20
        )

    # 彻底放弃 ListView，用可滚动 Column 替代，防止高度崩塌
    scrollable_content = ft.Column([
        make_card("主题色强化", ft.Icons.COLOR_LENS, [
            ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")]),
        ]),
        ft.Container(height=10),
        make_card("UI 材质风格", ft.Icons.LAYERS, [
            ft.Text("选择全局界面渲染材质，切换后立即生效。", size=12, color=ft.Colors.GREY_400),
            ft.Row([material_dropdown]),
        ]),
        ft.Container(height=10),
        make_card("视觉特效", ft.Icons.AUTO_AWESOME, [
            ft.Row([
                ft.Column([
                    ft.Text("卡片透明度", size=14, color="white"),
                    ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)
                ]),
                ft.Container(expand=True),
                ft.Container(content=opacity_slider, width=300)
            ])
        ]),
        ft.Container(height=20),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            scrollable_content
        ], expand=True),
        expand=True, padding=20
    )
'''
with open("pages/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)
print("✅ settings.py 已修复崩溃色块！")

# ==================== 3. 调整 main_final.py ====================
with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 修复导航栏包裹的宽度问题，避免挤压
content = content.replace(
    "nav_container = ft.Container(\n            content=nav_inner,\n            bgcolor=page.ui_style[\"nav_bg\"],\n            blur=page.ui_style[\"nav_blur\"],\n            width=90 # 强制宽度\n        )",
    "nav_container = ft.Container(\n            content=nav_inner,\n            bgcolor=page.ui_style[\"nav_bg\"],\n            blur=page.ui_style[\"nav_blur\"]\n        )"
)

# 确保 page 背景是透明的，壁纸能显示出来
if 'page.bgcolor = ft.Colors.TRANSPARENT' not in content:
    content = content.replace(
        'theme_color = ui_theme.setup_page_style(page)',
        'theme_color = ui_theme.setup_page_style(page)\n        page.bgcolor = ft.Colors.TRANSPARENT'
    )

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 已确保背景透出！")

print("🎉 修复完毕！请运行 python main_final.py。")