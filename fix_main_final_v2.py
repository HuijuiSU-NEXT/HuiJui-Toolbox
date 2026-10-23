# fix_main_final_v2.py
import os

main_code = '''import flet as ft
import threading
import flet_lottie as fl
import time
from core_api import scan_device_data, CFG
import ui_theme

# ================= 导入所有页面 =================
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
        is_blur = CFG.get("ui_blur_enabled", True)
        
        side_bg = ft.Colors.with_opacity(0.2 if is_blur else 0.4, "#0D1017")
        side_blur = ft.Blur(20, 20, ft.BlurTileMode.MIRROR) if is_blur else None
        nav_bg = ft.Colors.with_opacity(0.2 if is_blur else 0.4, "#0D1017")

        status_dot = ft.Container(width=10, height=10, bgcolor="#E05070", border_radius=5)
        device_status_text = ft.Text("等待扫描", size=13, weight=ft.FontWeight.W_600, color="#A0ABC0")
        loading_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=theme_color, visible=False)
        
        info_brand = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_model = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_android = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
        info_root = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)

        # ================= 自动设备感知引擎 =================
        last_state = {"state": "OFFLINE", "sn": ""}

        def apply_device_state(res, manual=False):
            state = res["state"]
            sn = res.get("serial", "")
            
            # 状态没变且不是手动请求，跳过 UI 更新，节省性能
            if state == last_state["state"] and sn == last_state["sn"] and not manual:
                return

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

        # 后台轮询线程
        def auto_scan_loop():
            time.sleep(1)
            while getattr(page, "is_running", True):
                try:
                    res = scan_device_data()
                    apply_device_state(res, manual=False)
                except Exception:
                    pass
                time.sleep(2.5)
                
        page.is_running = True
        threading.Thread(target=auto_scan_loop, daemon=True).start()

        # ================= 右侧边栏 =================
        side_panel = ft.Container(
            width=320, bgcolor=side_bg, blur=side_blur,
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
                    padding=15, bgcolor=ft.Colors.with_opacity(0.2 if is_blur else 0.3, "#151A26"), border_radius=16, border=ft.border.all(1, ft.Colors.with_opacity(0.08, "white"))
                ),
                ft.Container(expand=True),
                ft.Row([fl.Lottie(src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json", width=140, height=140, animate=True)], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True)
        )

        # ================= 左侧导航栏 =================
        nav_rail = ft.NavigationRail(
            selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=90, 
            bgcolor=nav_bg, indicator_color=ft.Colors.with_opacity(0.2, theme_color), indicator_shape=ft.RoundedRectangleBorder(radius=12),
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
        }

        def goto_sub_page(route_name):
            page.goto_sub_page = goto_sub_page # 挂载给子页面用
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

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(main_code)

print("OK: main_final.py rewritten successfully.")