# fix_settings_v3.py
import os

settings_code = '''import flet as ft
import os
import re
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
    # 状态保存
    state = {
        "theme_color": CFG.get("theme_color", "#39C5BB"),
        "blur_enabled": CFG.get("ui_blur_enabled", True),
        "card_opacity": CFG.get("card_opacity", 0.15)
    }

    # ================= 颜色校验与实时预览 =================
    color_input = ft.TextField(
        value=state["theme_color"], label="自定义 HEX 颜色", width=200,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white",
        border_color=ft.Colors.with_opacity(0.2, theme_color)
    )
    color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])

    def apply_color(e):
        hex_val = color_input.value.strip()
        # 校验 HEX 格式 (#RRGGBB)
        if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
            state["theme_color"] = hex_val
            color_preview.bgcolor = hex_val
            CFG["theme_color"] = hex_val
            show_snackbar("颜色已应用！部分 UI 需重启生效。")
        else:
            color_input.error_text = "格式错误，请填 #RRGGBB"
        page.update()

    color_input.on_submit = apply_color

    # ================= 背景/毛玻璃控制 =================
    blur_switch = ft.Switch(value=state["blur_enabled"], active_color=state["theme_color"])
    def on_blur_change(e):
        state["blur_enabled"] = blur_switch.value
        CFG["ui_blur_enabled"] = blur_switch.value
        show_snackbar(f"全局毛玻璃已{'开启' if blur_switch.value else '关闭'}")
        page.update()

    blur_switch.on_change = on_blur_change

    opacity_slider = ft.Slider(
        min=0.05, max=0.6, divisions=11, value=state["card_opacity"],
        active_color=state["theme_color"], label="{value:.2f}"
    )
    def on_opacity_change(e):
        state["card_opacity"] = opacity_slider.value
        CFG["card_opacity"] = opacity_slider.value
        page.update()
    
    opacity_slider.on_change = on_opacity_change

    # ================= 壁纸引擎 =================
    def clear_wallpaper(e):
        wallpaper_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(wallpaper_path):
            try:
                os.remove(wallpaper_path)
                show_snackbar("壁纸已清除，重启后生效。")
            except Exception as ex:
                show_snackbar(f"清除失败: {ex}")
        else:
            show_snackbar("当前没有自定义壁纸。")

    def pick_wallpaper(e):
        # 这里可以扩展文件选择器，目前先做占位
        show_snackbar("壁纸选择功能开发中，请手动放入 assets/custom_wallpaper.jpg")

    # ================= 侧滑提示 =================
    def show_snackbar(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=theme_color)
        page.snack_bar.open = True
        page.update()

    # ================= UI 组装 =================
    def make_card(title, icon, content_list):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=theme_color, size=20), ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white")]),
                ft.Divider(color=ft.Colors.GREY_800, height=10),
                *content_list
            ], spacing=15),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=15, padding=20
        )

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            
            # 滚动区域
            ft.ListView([
                # 1. 主题强化
                make_card("主题色强化", ft.Icons.COLOR_LENS, [
                    ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")]),
                ]),
                ft.Container(height=10),

                # 2. 视觉特效
                make_card("全局视觉特效", ft.Icons.AUTO_AWESOME, [
                    ft.Row([
                        ft.Column([
                            ft.Text("全局 UI 毛玻璃效果", size=14, color="white"),
                            ft.Text("关闭后显著降低显卡占用", size=11, color=ft.Colors.GREY_500)
                        ]),
                        ft.Container(expand=True),
                        blur_switch
                    ]),
                    ft.Divider(color=ft.Colors.GREY_800, height=10),
                    ft.Row([
                        ft.Column([
                            ft.Text("卡片透明度", size=14, color="white"),
                            ft.Text("调节背景卡片的不透明度", size=11, color=ft.Colors.GREY_500)
                        ]),
                        ft.Container(expand=True),
                        ft.Container(content=opacity_slider, width=300)
                    ])
                ]),
                ft.Container(height=10),

                # 3. 壁纸引擎
                make_card("壁纸引擎", ft.Icons.IMAGE, [
                    ft.Row([
                        ft.Column([
                            ft.Text("自定义壁纸", size=14, color="white"),
                            ft.Text("支持 16:9 智能裁剪 (需重启生效)", size=11, color=ft.Colors.GREY_500)
                        ]),
                        ft.Container(expand=True),
                        ft.ElevatedButton("选择图片", icon=ft.Icons.UPLOAD, on_click=pick_wallpaper, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"),
                        ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white")
                    ])
                ]),
                ft.Container(height=20),
            ], expand=True, spacing=10)
        ], expand=True),
        expand=True, padding=20
    )
'''

with open("pages/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)

print("✅ 个性化设置 v3 重构完毕！模块化卡片，防呆校验，滑动防崩溃！")