# one_click_theme_fix.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 1. 重写 settings.py ====================
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

    # ================= 主题色 =================
    color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))
    color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])

    def apply_color(e):
        hex_val = color_input.value.strip()
        if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
            state["theme_color"] = hex_val
            color_preview.bgcolor = hex_val
            CFG.set("theme_color", hex_val)
            show_snackbar("颜色已应用！部分 UI 需重启生效。")
        else:
            color_input.error_text = "格式错误，请填 #RRGGBB"
        page.update()

    color_input.on_submit = apply_color

    # ================= UI 材质选择器 =================
    material_dropdown = ft.Dropdown(
        label="UI 材质风格",
        value=state["ui_material"],
        width=300,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        color="white",
        options=[
            ft.dropdown.Option("default", "默认 (纯色/清晰)"),
            ft.dropdown.Option("frosted", "毛玻璃 (高斯模糊)"),
            ft.dropdown.Option("liquid", "液态玻璃 (渐变+高光)"),
        ],
        on_change=lambda e: apply_material(e.control.value)
    )

    def apply_material(val):
        state["ui_material"] = val
        CFG.set("ui_material", val)
        show_snackbar(f"材质已切换至: {val}，正在全局刷新...")
        # 触发主界面重建
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui()

    # ================= 卡片透明度 =================
    opacity_slider = ft.Slider(min=0.05, max=0.6, divisions=11, value=state["card_opacity"], active_color=state["theme_color"], label="{value:.2f}")
    def on_opacity_change(e):
        state["card_opacity"] = opacity_slider.value
        CFG.set("card_opacity", opacity_slider.value)
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
        show_snackbar("壁纸选择功能开发中，请手动放入 assets/custom_wallpaper.jpg")

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
            ft.ListView([
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
                            ft.Text("调节背景卡片的不透明度", size=11, color=ft.Colors.GREY_500)
                        ]),
                        ft.Container(expand=True),
                        ft.Container(content=opacity_slider, width=300)
                    ])
                ]),
                ft.Container(height=10),
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

# ==================== 2. 修改 main_final.py (注入材质逻辑与重建回调) ====================
main_code = '''import flet as ft
import threading
import flet_lottie as fl
import time
from core_api import scan_device_data, CFG
import ui_theme

from pages.dashboard import build_dashboard
from pages.flash import build_flash_page
from pages.temp_root import build_temp_root_page
from pages.history import build_history_page
from pages.settings import build_settings_page
from pages.terminal import build_terminal_page
from pages.backup import build_backup_page
from pages.scrcpy import build_scrcpy_page
from pages.mode_switch import build_mode_switch_page
from pages.rescue import build_rescue_page
from pages.module_repo import build_module_repo_page
from pages.drivers import build_drivers_page
from pages.wireless_adb import build_wireless_adb_page
from pages.scan import build_scan_page
from pages.mediatek_rescue import build_mediatek_rescue_page
from pages.flash_parts import build_flash_parts_page

def main(page: ft.Page):
    page.title = "HuiJui Core · Matrix"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1440
    page.window.height = 900
    page.window.min_width = 1150
    page.window.min_height = 800
    
    theme_color = ui_theme.setup_page_style(page)

    def build_main_ui():
        page.controls.clear()
        theme_color = ui_theme.setup_page_style(page)
        
        # ==================== 核心：材质配置读取 ====================
        ui_material = CFG.get("ui_material", "default")
        card_opacity = CFG.get("card_opacity", 0.15)
        
        # 根据材质风格定义样式
        if ui_material == "frosted":
            side_bg = ft.Colors.with_opacity(0.2, "#0D1017")
            side_blur = ft.Blur(20, 20, ft.BlurTileMode.MIRROR)
            nav_bg = ft.Colors.with_opacity(0.2, "#0D1017")
            card_bg = ft.Colors.with_opacity(card_opacity, ft.Colors.WHITE)
            card_border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.WHITE))
        elif ui_material == "liquid":
            side_bg = ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(0.3, "#1A233A"), ft.Colors.with_opacity(0.1, "#0D1017")]
            )
            side_blur = ft.Blur(15, 15, ft.BlurTileMode.MIRROR)
            nav_bg = ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(0.3, "#1A233A"), ft.Colors.with_opacity(0.1, "#0D1017")]
            )
            card_bg = ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(card_opacity + 0.05, ft.Colors.WHITE), ft.Colors.with_opacity(card_opacity - 0.05, ft.Colors.WHITE)]
            )
            card_border = ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.WHITE))
        else:
            # default
            side_bg = ft.Colors.with_opacity(0.4, "#0D1017")
            side_blur = None
            nav_bg = ft.Colors.with_opacity(0.4, "#0D1017")
            card_bg = ft.Colors.with_opacity(card_opacity, ft.Colors.WHITE)
            card_border = ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))
        # =========================================================

        status_dot = ft.Container(width=10, height=10, bgcolor="#E05070", border_radius=5)
        device_status_text = ft.Text("等待扫描", size=13, weight=ft.FontWeight.W_600, color="#A0ABC0")
        loading_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=theme_color, visible=False)
        
        info_brand = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_model = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_android = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_root = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)

        last_state = {"state": "OFFLINE", "sn": ""}

        def apply_device_state(res, manual=False):
            state = res["state"]
            sn = res.get("serial", "")
            if state == last_state["state"] and sn == last_state["sn"] and not manual: return
            last_state["state"] = state
            last_state["sn"] = sn

            if state == "OFFLINE": 
                device_status_text.value = "等待扫描"; status_dot.bgcolor = "#E05070"
            elif state == "NORMAL": 
                device_status_text.value = "已连接 (ADB)"; status_dot.bgcolor = "#3FBF6E"
            elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): 
                device_status_text.value = f"{state}"; status_dot.bgcolor = "#F0A030"
            elif state == "FASTBOOTD": 
                device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
            elif state in ("EDL", "BROM"): 
                device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#E05070"
            
            info_brand.value = res.get("brand", "—")
            info_model.value = res.get("model", "—")
            info_android.value = res.get("android", "—")
            info_root.value = res.get("root", "—")
            loading_ring.visible = False
            try: page.update()
            except: pass

        def scan_device(e=None):
            status_dot.bgcolor = "#F0A030"
            device_status_text.value = "扫描中..."
            loading_ring.visible = True
            page.update()
            def run():
                res = scan_device_data()
                apply_device_state(res, manual=True)
            threading.Thread(target=run, daemon=True).start()

        def auto_scan_loop():
            time.sleep(1)
            while getattr(page, "is_running", True):
                try:
                    res = scan_device_data()
                    apply_device_state(res, manual=False)
                except Exception: pass
                time.sleep(2.5)

        page.is_running = True
        threading.Thread(target=auto_scan_loop, daemon=True).start()

        # ==================== 右侧边栏 (应用材质) ====================
        side_panel = ft.Container(
            width=320, 
            bgcolor=side_bg, 
            blur=side_blur,
            border=ft.border.only(left=ft.border.BorderSide(1, ft.Colors.with_opacity(0.1, "white"))),
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Row([
                    ft.Container(content=ft.Image(src="logo.png", width=40, height=40, fit=ft.ImageFit.COVER), border_radius=20, border=ft.border.all(2, theme_color), shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.4, theme_color))),
                    ft.Column([ft.Text("HuiJui Core", size=16, weight=ft.FontWeight.W_900, color="white"), ft.Text("Matrix Engine", size=10, color=theme_color)], spacing=0, expand=True),
                ]), 
                ft.Container(height=25),
                ft.Container(
                    content=ft.Column([
                        ft.Row([status_dot, device_status_text, loading_ring], spacing=8),
                        ft.Divider(color="#1C202D", height=15),
                        ft.Row([ft.Text("品牌", color="#6E7B91", size=12), info_brand], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("型号", color="#6E7B91", size=12), info_model], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("系统", color="#6E7B91", size=12), info_android], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([ft.Text("Root", color="#6E7B91", size=12), info_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    padding=15, bgcolor=card_bg, border_radius=16, border=card_border
                ),
                ft.Container(expand=True),
                ft.Row([fl.Lottie(src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json", width=140, height=140, animate=True)], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True)
        )

        # ==================== 左侧导航栏 (应用材质) ====================
        nav_rail = ft.NavigationRail(
            selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=90, 
            bgcolor=nav_bg, 
            indicator_color=ft.Colors.with_opacity(0.2, theme_color), indicator_shape=ft.RoundedRectangleBorder(radius=12),
            selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=12),
            unselected_label_text_style=ft.TextStyle(color="#8892B0", size=12),
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="控制台"),
                ft.NavigationRailDestination(icon=ft.Icons.FLASH_ON_OUTLINED, selected_icon=ft.Icons.FLASH_ON, label="一键刷机"),
                ft.NavigationRailDestination(icon=ft.Icons.SECURITY_OUTLINED, selected_icon=ft.Icons.SECURITY, label="临时Root"),
                ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="历史"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="个性化"),
            ]
        )

        content_area = ft.Container(expand=True)
        
        SUB_PAGES = {
            "module_repo": build_module_repo_page,
            "terminal": build_terminal_page,
            "scrcpy": build_scrcpy_page,
            "backup": build_backup_page,
            "wireless_adb": build_wireless_adb_page,
            "mode_switch": build_mode_switch_page,
            "drivers": build_drivers_page,
            "rescue": build_rescue_page,
            "scan": build_scan_page,
            "mediatek_rescue": build_mediatek_rescue_page,
            "flash_parts": build_flash_parts_page,
        }

        def goto_sub_page(route_name):
            page.goto_sub_page = goto_sub_page
            if route_name in SUB_PAGES:
                content_area.content = SUB_PAGES[route_name](page, theme_color)
                content_area.opacity = 0
                content_area.animate_opacity = 200
                page.update()
                content_area.opacity = 1
                page.update()

        def switch_tab(idx):
            nav_rail.selected_index = idx
            on_nav_change(None)

        def on_nav_change(e):
            idx = nav_rail.selected_index
            if idx == 0: content_area.content = build_dashboard(page, theme_color, scan_device, switch_tab, goto_sub_page)
            elif idx == 1: content_area.content = build_flash_page(page, theme_color)
            elif idx == 2: content_area.content = build_temp_root_page(page, theme_color)
            elif idx == 3: content_area.content = build_history_page(page, theme_color)
            elif idx == 4: content_area.content = build_settings_page(page, theme_color)
            
            content_area.opacity = 0
            content_area.animate_opacity = 200
            page.update()
            content_area.opacity = 1
            page.update()

        nav_rail.on_change = on_nav_change
        content_area.content = build_dashboard(page, theme_color, scan_device, switch_tab, goto_sub_page)

        page.add(ft.Row([nav_rail, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0))

        # ==================== 注册全局重建回调 ====================
        def refresh_main_ui():
            build_main_ui()
        page.refresh_main_ui = refresh_main_ui

    if not CFG.get("onboarded", False):
        from ui_onboarding_hyperos_light import HyperOSLightOnboarding
        page.bgcolor = ft.Colors.TRANSPARENT
        page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#E8F0FE", "#FFFFFF"]))
        onboarding = HyperOSLightOnboarding(on_finish=build_main_ui)
        page.add(onboarding)
    else:
        build_main_ui()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
'''

# ==================== 3. 执行备份与覆盖 ====================
def backup_and_write(filepath, content):
    if os.path.exists(filepath):
        backup_path = filepath + ".bak"
        shutil.copy2(filepath, backup_path)
        print(f"📁 已备份原文件至: {backup_path}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已成功更新: {filepath}")

print("=== 🚀 开始执行 UI 材质动态化重构 ===")
backup_and_write(os.path.join(BASE_DIR, "pages", "settings.py"), settings_code)
backup_and_write(os.path.join(BASE_DIR, "main_final.py"), main_code)
print("🎉 所有文件已更新完毕！请运行 python main_final.py 查看效果。")