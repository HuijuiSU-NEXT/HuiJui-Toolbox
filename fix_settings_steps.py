# fix_settings_steps.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 1. 重写 settings.py (步骤式引导) ====================
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
                    show_snackbar("壁纸已应用！正在解锁材质设置...")
                    
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
                show_snackbar("壁纸已清除，材质已锁定。")
                if hasattr(page, "refresh_main_ui"):
                    page.refresh_main_ui(tab_index=4)
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

    # ================= 组装视图 =================
    # 壁纸卡片永远显示
    card_wallpaper = make_card("第一步：壁纸引擎", ft.Icons.IMAGE, [
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

    # 只有存在壁纸时，才显示后续卡片
    advanced_cards = []
    if has_wallpaper:
        advanced_cards = [
            make_card("第二步：主题色强化", ft.Icons.COLOR_LENS, [
                ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")]),
            ]),
            ft.Container(height=10),
            make_card("第三步：UI 材质风格", ft.Icons.LAYERS, [
                ft.Text("选择全局界面渲染材质，切换后立即生效。", size=12, color=ft.Colors.GREY_400),
                ft.Row([material_dropdown]),
            ]),
            ft.Container(height=10),
            make_card("视觉特效微调", ft.Icons.AUTO_AWESOME, [
                ft.Row([
                    ft.Column([
                        ft.Text("卡片透明度", size=14, color="white"),
                        ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)
                    ]),
                    ft.Container(expand=True),
                    ft.Container(content=opacity_slider, width=300)
                ])
            ])
        ]

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Column(
                [card_wallpaper, ft.Container(height=10)] + advanced_cards,
                scroll=ft.ScrollMode.AUTO, expand=True
            )
        ], expand=True),
        expand=True, padding=20
    )
'''

with open("pages/settings.py", "w", encoding="utf-8") as f:
    f.write(settings_code)
print("✅ settings.py 已重构为步骤式解锁！")

# ==================== 2. 修复 main_final.py 后台线程报错 ====================
main_path = os.path.join(BASE_DIR, "main_final.py")
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# 修复 auto_scan_loop 里的闭包作用域问题
old_loop = '''        def auto_scan_loop():
            time.sleep(1)
            while getattr(page, "is_running", True):
                try:
                    res = scan_device_data()
                    apply_device_state(res, manual=False)
                except Exception: pass
                time.sleep(2.5)'''

new_loop = '''        def auto_scan_loop():
            time.sleep(1)
            while getattr(page, "is_running", True):
                try:
                    # 每次循环动态获取当前的 apply_device_state，防止 UI 重建后引用旧闭包
                    current_apply = locals().get("apply_device_state")
                    if current_apply:
                        res = scan_device_data()
                        current_apply(res, manual=False)
                except Exception: 
                    pass
                time.sleep(2.5)'''

if old_loop in main_content:
    main_content = main_content.replace(old_loop, new_loop)
    print("✅ main_final.py 后台轮询线程作用域已修复！")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

print("🎉 一切就绪！请运行 python main_final.py 体验全新的步骤式个性化设置！")