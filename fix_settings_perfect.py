# fix_settings_perfect.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
wallpaper_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")

# 🚨 1. 物理超度：强制删除之前残留的垃圾壁纸，让初始状态彻底干净
if os.path.exists(wallpaper_path):
    try:
        os.remove(wallpaper_path)
        print("🧹 已强制清理残留的旧壁纸，确保进入时处于锁定状态！")
    except Exception as e:
        print(f"⚠️ 清理旧壁纸失败: {e}")

# 🚨 2. 写入绝对严谨的 settings.py
settings_code = '''import flet as ft
import os
import re
import shutil
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
    state = {
        "theme_color": CFG.get("theme_color", "#39C5BB"),
        "ui_material": CFG.get("ui_material", "default"),
        "card_opacity": CFG.get("card_opacity", 0.15)
    }

    wallpaper_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
    # 严格判断壁纸是否存在
    has_wallpaper = os.path.exists(wallpaper_path)

    def show_snackbar(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=theme_color)
        page.snack_bar.open = True
        page.update()

    # ================= 壁纸处理 =================
    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                try:
                    if os.path.exists(wallpaper_path):
                        try: os.remove(wallpaper_path)
                        except: pass
                    shutil.copy2(src_path, wallpaper_path)
                    show_snackbar("壁纸已应用！高级材质已解锁！")
                    
                    # 动态解锁
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    page.update()
                    
                    if hasattr(page, "refresh_main_ui"):
                        page.refresh_main_ui(tab_index=4)
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])

    def clear_wallpaper(e):
        if os.path.exists(wallpaper_path):
            try:
                os.remove(wallpaper_path)
                show_snackbar("壁纸已清除，高级材质已锁定。")
                
                # 动态隐藏
                card_step2.visible = False
                card_step3.visible = False
                card_step4.visible = False
                page.update()
            except Exception as ex:
                show_snackbar(f"清除失败: {ex}")

    # ================= 颜色处理 =================
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
            color_input.error_text = "格式错误，请填 #RRGGBB"
        page.update()

    # ================= 材质处理 =================
    material_dropdown = ft.Dropdown(
        label="UI 材质风格", value=state["ui_material"], width=300,
        bgcolor="#1A233A", color="white",
        options=[
            ft.dropdown.Option("default", "默认 (纯色/清晰)"),
            ft.dropdown.Option("frosted", "毛玻璃 (半透明)"),
            ft.dropdown.Option("liquid", "液态玻璃 (晶莹剔透)"),
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

    # ================= 构建卡片并设置初始可见性 =================
    card_step1 = make_card("第一步：壁纸引擎", ft.Icons.IMAGE, [
        ft.Row([
            ft.Column([
                ft.Text("自定义壁纸", size=14, color="white"),
                ft.Text("请先设置壁纸以解锁高级材质" if not has_wallpaper else "已设置壁纸，可随时更换", size=11, color=ft.Colors.GREY_500)
            ]),
            ft.Container(expand=True),
            ft.ElevatedButton("选择图片", icon=ft.Icons.UPLOAD, on_click=pick_wallpaper, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"),
            ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white", disabled=not has_wallpaper)
        ])
    ])

    card_step2 = make_card("第二步：主题色强化", ft.Icons.COLOR_LENS, [
        ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")]),
    ])
    card_step2.visible = has_wallpaper

    card_step3 = make_card("第三步：UI 材质风格", ft.Icons.LAYERS, [
        ft.Text("选择全局界面渲染材质，切换后立即生效。", size=12, color=ft.Colors.GREY_400),
        ft.Row([material_dropdown]),
    ])
    card_step3.visible = has_wallpaper

    card_step4 = make_card("视觉特效微调", ft.Icons.AUTO_AWESOME, [
        ft.Row([
            ft.Column([
                ft.Text("卡片透明度", size=14, color="white"),
                ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)
            ]),
            ft.Container(expand=True),
            ft.Container(content=opacity_slider, width=300)
        ])
    ])
    card_step4.visible = has_wallpaper

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Column([
                card_step1,
                ft.Container(height=10),
                card_step2,
                ft.Container(height=10),
                card_step3,
                ft.Container(height=10),
                card_step4,
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True),
        expand=True, padding=20
    )
'''

with open("pages/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)

print("✅ 终极锁定逻辑已注入！现在彻底清空了残留壁纸，没选壁纸前打死也不会显示下面的选项！")