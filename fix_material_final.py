# fix_material_final.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 1. 重写 ui_theme.py ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    
    if material == "frosted":
        # 毛玻璃：半透明白色 + 模糊遮罩
        return {
            "type": "frosted",
            "overlay_bg": ft.Colors.with_opacity(0.5, "#0D1017"), # 半透明遮罩
            "overlay_blur": ft.Blur(30, 30, ft.BlurTileMode.MIRROR),
            "nav_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }
    elif material == "liquid":
        # 液态玻璃：主题色渐变 + 强模糊 + 发光边框
        return {
            "type": "liquid",
            "overlay_bg": ft.LinearGradient(
                colors=[ft.Colors.with_opacity(0.4, theme_color), ft.Colors.with_opacity(0.1, "#0D1017")]
            ),
            "overlay_blur": ft.Blur(40, 40, ft.BlurTileMode.MIRROR), # 更强模糊
            "nav_bg": ft.Colors.with_opacity(0.1, theme_color),
            "side_bg": ft.Colors.with_opacity(0.1, theme_color),
            "card_bg": ft.LinearGradient(
                colors=[ft.Colors.with_opacity(0.2, theme_color), ft.Colors.with_opacity(0.05, ft.Colors.WHITE)]
            ),
            "card_border": ft.border.all(2, theme_color),
            "log_bg": ft.LinearGradient(
                colors=[ft.Colors.with_opacity(0.15, theme_color), ft.Colors.with_opacity(0.05, ft.Colors.BLACK)]
            ),
            "log_color": theme_color
        }
    else:
        # 默认
        return {
            "type": "default",
            "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "overlay_blur": None,
            "nav_bg": ft.Colors.with_opacity(0.2, "#0D1017"),
            "side_bg": ft.Colors.with_opacity(0.2, "#0D1017"),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }

def setup_page_style(page: ft.Page):
    theme_color = CFG.get("theme_color", "#39C5BB")
    page.bgcolor = ft.Colors.TRANSPARENT # 页面必须透明
    return theme_color
'''

# ==================== 2. 重写 main_final.py ====================
main_code = '''import flet as ft
import threading
import flet_lottie as fl
import time
from core_api import scan_device_data, CFG
import ui_theme
import os

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

    current_tab = {"idx": 0}

    def build_main_ui():
        page.controls.clear()
        theme_color = ui_theme.setup_page_style(page)
        
        # 获取当前材质配置
        page.ui_style = ui_theme.get_ui_styles(theme_color)

        # ==================== 底层构建 ====================
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

        # ==================== 右侧边栏 ====================
        side_panel = ft.Container(
            width=320, 
            bgcolor=page.ui_style["side_bg"], 
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

        # ==================== 左侧导航栏 ====================
        nav_inner = ft.NavigationRail(
            selected_index=current_tab["idx"],
            label_type=ft.NavigationRailLabelType.ALL, min_width=90, 
            bgcolor=ft.Colors.TRANSPARENT,
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
        
        nav_container = ft.Container(
            content=nav_inner,
            bgcolor=page.ui_style["nav_bg"],
        )

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

        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)

        # ==================== 核心：Stack 图层合成 ====================
        # 1. 壁纸层
        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            wallpaper = ft.Container(image_src="custom_wallpaper.jpg", image_fit=ft.ImageFit.COVER, expand=True)
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)

        # 2. 模糊遮罩层
        overlay_layer = ft.Container(
            expand=True,
            bgcolor=page.ui_style["overlay_bg"],
            blur=page.ui_style["overlay_blur"] # 这里才是真正的背景模糊！
        )

        # 3. 合成并添加到 Page
        page.add(
            ft.Stack(
                [wallpaper, overlay_layer, main_layout],
                expand=True
            )
        )

        def refresh_main_ui(tab_index=0):
            current_tab["idx"] = tab_index
            page.controls.clear()
            page.update()
            build_main_ui()
            page.update()

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

# ==================== 3. 修复 settings.py 的卡片底色 ====================
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 强制替换 settings.py 里的写死底色
settings_content = settings_content.replace(
    'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)', 
    'bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE))'
)
settings_content = settings_content.replace(
    'border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))',
    'border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)))'
)

def backup_and_write(filepath, content):
    if os.path.exists(filepath):
        shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已成功更新: {filepath}")

print("=== 🚀 开始执行 Stack 级材质重构 ===")
backup_and_write(os.path.join(BASE_DIR, "ui_theme.py"), ui_theme_code)
backup_and_write(os.path.join(BASE_DIR, "main_final.py"), main_code)
backup_and_write(settings_path, settings_content)
print("🎉 全部修改完毕！运行 python main_final.py 体验真正的毛玻璃！")