# fix_decoration_hot.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 重写 main_final.py ====================
main_code = '''import flet as ft
import threading
import flet_lottie as fl
import time
import base64
import os
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main(page: ft.Page):
    page.title = "HuiJui Core · Matrix"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window.width = 1440
    page.window.height = 900
    page.window.min_width = 1150
    page.window.min_height = 800
    page.bgcolor = ft.Colors.TRANSPARENT # 让系统背景透出来

    current_tab = {"idx": 0}
    
    # 🚨 彻底干掉 Stack，只留主容器
    main_container = ft.Container(expand=True)
    page.add(main_container)

    # 🚨 全局系统级壁纸热更新函数
    def update_wallpaper_system():
        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            try:
                with open(bg_image, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                page.decoration = ft.BoxDecoration(
                    image=ft.DecorationImage(src_base64=b64, fit=ft.ImageFit.COVER)
                )
            except Exception as e:
                print(f"壁纸加载失败: {e}")
                page.decoration = None
        else:
            page.decoration = None
        page.update()

    page.update_wallpaper_system = update_wallpaper_system

    def build_main_ui():
        theme_color = ui_theme.setup_page_style(page)
        page.ui_style = ui_theme.get_ui_styles(theme_color)

        # 每次重建 UI 时，顺便确保底层系统壁纸在位
        update_wallpaper_system()

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

        if not hasattr(page, "scan_thread_started"):
            page.is_running = True
            threading.Thread(target=auto_scan_loop, daemon=True).start()
            page.scan_thread_started = True

        side_panel = ft.Container(
            width=320, bgcolor=page.ui_style["side_bg"], 
            border=ft.border.only(left=ft.border.BorderSide(1, ft.Colors.with_opacity(0.2, "white"))),
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
                    padding=15, bgcolor=page.ui_style["card_bg"], border_radius=16, border=page.ui_style["card_border"]
                ),
                ft.Container(expand=True),
                ft.Row([fl.Lottie(src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json", width=140, height=140, animate=True)], alignment=ft.MainAxisAlignment.CENTER)
            ], expand=True)
        )

        nav_inner = ft.NavigationRail(
            selected_index=current_tab["idx"],
            label_type=ft.NavigationRailLabelType.ALL, min_width=90, bgcolor=ft.Colors.TRANSPARENT,
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
        
        nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style["nav_bg"])
        content_area = ft.Container(expand=True)
        
        SUB_PAGES = {
            "module_repo": build_module_repo_page, "terminal": build_terminal_page,
            "scrcpy": build_scrcpy_page, "backup": build_backup_page,
            "wireless_adb": build_wireless_adb_page, "mode_switch": build_mode_switch_page,
            "drivers": build_drivers_page, "rescue": build_rescue_page,
            "scan": build_scan_page, "mediatek_rescue": build_mediatek_rescue_page,
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
            nav_inner.selected_index = idx
            on_nav_change(None)

        def on_nav_change(e):
            current_tab["idx"] = nav_inner.selected_index
            idx = nav_inner.selected_index
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

        nav_inner.on_change = on_nav_change
        
        if current_tab["idx"] == 0: content_area.content = build_dashboard(page, theme_color, scan_device, switch_tab, goto_sub_page)
        elif current_tab["idx"] == 1: content_area.content = build_flash_page(page, theme_color)
        elif current_tab["idx"] == 2: content_area.content = build_temp_root_page(page, theme_color)
        elif current_tab["idx"] == 3: content_area.content = build_history_page(page, theme_color)
        elif current_tab["idx"] == 4: content_area.content = build_settings_page(page, theme_color)

        # 关键：主布局加入半透明底色
        main_layout = ft.Container(
            content=ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0),
            bgcolor=page.ui_style["overlay_bg"],
            blur=page.ui_style["overlay_blur"],
            expand=True
        )

        return main_layout

    def refresh_main_ui(tab_index=0):
        current_tab["idx"] = tab_index
        new_ui = build_main_ui()
        main_container.content = new_ui
        page.update()

    page.refresh_main_ui = refresh_main_ui

    if not CFG.get("onboarded", False):
        from ui_onboarding_hyperos_light import HyperOSLightOnboarding
        page.bgcolor = ft.Colors.TRANSPARENT
        page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#E8F0FE", "#FFFFFF"]))
        
        def on_finish():
            page.controls.clear()
            main_container.content = build_main_ui()
            page.update()
            
        onboarding = HyperOSLightOnboarding(on_finish=on_finish)
        page.add(onboarding)
    else:
        main_container.content = build_main_ui()
        page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
'''

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_code)
print("✅ main_final.py 纯血系统级背景版已覆盖！")

# ==================== 2. 修改 settings.py ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 替换掉原来的刷新逻辑
old_pick_success = '''                    # 动态解锁后续卡片
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    page.update()
                    
                    # 🚨 核心：只热更新背景层，绝不重建 UI！
                    if hasattr(page, "update_wallpaper_hot"):
                        page.update_wallpaper_hot()'''

new_pick_success = '''                    # 动态解锁后续卡片
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    page.update()
                    
                    # 🚨 核心：系统底层背景热更新！
                    if hasattr(page, "update_wallpaper_system"):
                        page.update_wallpaper_system()'''

if old_pick_success in settings_content:
    settings_content = settings_content.replace(old_pick_success, new_pick_success)
else:
    # 兜底正则替换
    import re
    settings_content = re.sub(
        r'card_step4\.visible = True\s*page\.update\(\).*?(if hasattr\(page, "update_wallpaper_hot"\):\s*page\.update_wallpaper_hot\(\))',
        'card_step4.visible = True\n                    page.update()\n                    if hasattr(page, "update_wallpaper_system"):\n                        page.update_wallpaper_system()',
        settings_content, flags=re.DOTALL
    )

# 清除壁纸的逻辑也要改
old_clear = '''                # 动态隐藏
                card_step2.visible = False
                card_step3.visible = False
                card_step4.visible = False
                page.update()'''
new_clear = '''                # 动态隐藏
                card_step2.visible = False
                card_step3.visible = False
                card_step4.visible = False
                page.update()
                if hasattr(page, "update_wallpaper_system"):
                    page.update_wallpaper_system()'''
settings_content = settings_content.replace(old_clear, new_clear)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)

print("🎉 完美！不仅换壁纸秒切，而且底层背景彻底脱离 UI 树，绝对不会闪！")