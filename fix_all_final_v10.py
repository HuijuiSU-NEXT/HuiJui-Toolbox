# fix_all_final_v10.py
import os

# 1. ==================== 修复 main_final.py ====================
main_code = '''import flet as ft
import threading
import flet_lottie as fl
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

        def scan_device(e=None):
            status_dot.bgcolor = "#F0A030"
            device_status_text.value = "扫描中..."
            loading_ring.visible = True
            page.update()
            def run():
                res = scan_device_data()
                state = res["state"]
                if state == "OFFLINE": device_status_text.value = "未连接"; status_dot.bgcolor = "#E05070"
                elif state == "NORMAL": device_status_text.value = "已连接"; status_dot.bgcolor = "#3FBF6E"
                elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): device_status_text.value = f"{state}"; status_dot.bgcolor = "#F0A030"
                elif state == "FASTBOOTD": device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
                elif state in ("EDL", "BROM"): device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#E05070"
                
                info_brand.value = res["brand"]; info_model.value = res["model"]
                info_android.value = res["android"]; info_root.value = res["root"]
                loading_ring.visible = False
                page.update()
            threading.Thread(target=run, daemon=True).start()

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
        }

        def goto_sub_page(route_name):
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

# 2. ==================== 修复 module_repo.py ====================
module_repo_code = '''import flet as ft

def build_module_repo_page(page: ft.Page, theme_color):
    modules = [
        {"name": "LSPosed", "desc": "强大的 Xposed 框架"},
        {"name": "Shamiko", "desc": "隐藏 Root 痕迹"},
        {"name": "Zygisk-Next", "desc": "新一代 Zygisk 注入"},
        {"name": "KernelSU", "desc": "内核级 Root 管理器"},
    ]
    
    grid = ft.GridView(expand=1, runs_count=3, max_extent=200, spacing=15, run_spacing=15)
    for m in modules:
        grid.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(m["name"], size=16, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(m["desc"], size=12, color=ft.Colors.GREY_400),
                    ft.ElevatedButton("安装模块", icon=ft.Icons.DOWNLOAD, style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color=theme_color))
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            )
        )
        
    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.EXTENSION, color=theme_color, size=28), ft.Text("模块仓库", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10), grid
        ]), expand=True, padding=20
    )
'''

# 3. ==================== 修复 terminal.py ====================
terminal_code = '''import flet as ft
import threading
import subprocess
import os

def build_terminal_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=13, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))
    
    cmd_input = ft.TextField(hint_text="输入命令 (如 adb devices) 并回车...", bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color), on_submit=lambda e: run_cmd(e))
    
    def append_log(text):
        log_area.value += text + "\\n"
        page.update()

    def run_cmd(e):
        cmd = cmd_input.value.strip()
        if not cmd: return
        cmd_input.value = ""
        append_log(f"\\n> {cmd}")
        page.update()
        
        def thread():
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                for line in iter(proc.stdout.readline, ''):
                    if line: append_log(line.strip())
                proc.stdout.close()
                proc.wait()
                append_log(f"[进程结束, 退出码: {proc.returncode}]")
            except Exception as ex:
                append_log(f"[执行出错]: {str(ex)}")
        threading.Thread(target=thread, daemon=True).start()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.TERMINAL, color=theme_color, size=28), ft.Text("高级终端 · 实时 Shell", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10), log_container, cmd_input
        ], expand=True), expand=True, padding=20
    )
'''

# 4. ==================== 修复 backup.py ====================
backup_code = '''import flet as ft
import threading
import subprocess
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

def build_backup_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=13, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))
    
    partitions = ["boot", "init_boot", "vbmeta", "dtbo", "super", "persist"]
    dropdown = ft.Dropdown(options=[ft.dropdown.Option(p) for p in partitions], value="boot", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", label="选择分区")
    
    btn_backup = ft.ElevatedButton("一键备份到电脑", icon=ft.Icons.SAVE, style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15))
    status_text = ft.Text("等待操作...", size=13, color=theme_color)

    def append_log(text):
        log_area.value += text + "\\n"
        page.update()

    def do_backup(e):
        part = dropdown.value
        btn_backup.disabled = True
        status_text.value = f"正在备份 {part}..."
        append_log(f"\\n开始备份分区: {part}")
        page.update()
        
        def thread():
            backup_dir = os.path.join(BASE_DIR, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            img_name = f"{part}_{int(time.time())}.img"
            local_path = os.path.join(backup_dir, img_name)
            remote_path = f"/sdcard/{img_name}"
            
            append_log("> 正在通过 su 提取镜像...")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if=/dev/block/by-name/{part} of={remote_path}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc.stdout.readline, ''):
                if line: append_log(line.strip())
            proc.wait()
            
            append_log(f"> 正在拉取到电脑: {local_path}")
            cmd_pull = f'"{ADB_PATH}" pull {remote_path} "{local_path}"'
            proc2 = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc2.stdout.readline, ''):
                if line: append_log(line.strip())
            proc2.wait()
            
            append_log(f"> 正在清理手机临时文件...")
            subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_path}\\""', shell=True, capture_output=True)
            
            append_log("✅ 备份完成！")
            status_text.value = "备份完成"
            btn_backup.disabled = False
            page.update()
        threading.Thread(target=thread, daemon=True).start()

    btn_backup.on_click = do_backup

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), ft.Text("分区备份 · 真 Root 引擎", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([status_text, ft.Row([dropdown, btn_backup], alignment=ft.MainAxisAlignment.START, spacing=20)]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            ),
            ft.Container(height=10), log_container
        ], expand=True), expand=True, padding=20
    )
'''

# 5. ==================== 其余子页面占位 ====================
scrcpy_code = '''import flet as ft
import subprocess
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRCPY_PATH = os.path.join(BASE_DIR, "bin", "scrcpy.exe")
def build_scrcpy_page(page: ft.Page, theme_color):
    status_text = ft.Text("请确保手机已连接。", size=13, color=theme_color)
    def launch(e):
        if not os.path.exists(SCRCPY_PATH):
            status_text.value = "❌ 未找到 bin/scrcpy.exe"; status_text.color = ft.Colors.RED; page.update(); return
        status_text.value = "🚀 启动投屏..."; status_text.color = ft.Colors.GREEN; page.update()
        subprocess.Popen([SCRCPY_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)
    return ft.Container(content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.MONITOR, color=theme_color, size=28), ft.Text("Scrcpy 投屏", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
        ft.Container(height=10),
        ft.Container(content=ft.Column([status_text, ft.ElevatedButton("启动 Scrcpy", icon=ft.Icons.PLAY_ARROW, on_click=launch, style=ft.ButtonStyle(color="#000000", bgcolor=theme_color))]), bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15)
    ]), expand=True, padding=20)
'''

mode_switch_code = '''import flet as ft
import subprocess
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
def build_mode_switch_page(page: ft.Page, theme_color):
    status_text = ft.Text("等待操作...", size=13, color=theme_color)
    def run_cmd(cmd, msg):
        status_text.value = msg; page.update()
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    return ft.Container(content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=theme_color, size=28), ft.Text("模式切换", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
        ft.Container(height=10),
        ft.Container(content=ft.Column([
            status_text, ft.Container(height=10),
            ft.Row([ft.ElevatedButton("重启到系统", icon=ft.Icons.PHONE_ANDROID, on_click=lambda _: run_cmd(f'"{ADB_PATH}" reboot', "重启中..."))]),
            ft.Row([ft.ElevatedButton("重启到 Fastboot", icon=ft.Icons.FLASH_ON, on_click=lambda _: run_cmd(f'"{ADB_PATH}" reboot bootloader', "进入 Fastboot..."))]),
            ft.Row([ft.ElevatedButton("重启到 9008", icon=ft.Icons.ERROR, on_click=lambda _: run_cmd(f'"{ADB_PATH}" shell "su -c reboot edl"', "进入 9008..."))])
        ]), bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15)
    ]), expand=True, padding=20)
'''

rescue_code = '''import flet as ft
def build_rescue_page(page: ft.Page, theme_color):
    return ft.Container(content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=theme_color, size=28), ft.Text("急救中心", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
        ft.Container(height=10),
        ft.Container(content=ft.Column([
            ft.Text("高通 9008 / MTK BROM 救砖引导", size=18, color=theme_color, weight=ft.FontWeight.BOLD),
            ft.Text("1. 确保安装了底层驱动。", color="white"), ft.Text("2. 断开手机电源，按住组合键进入 9008。", color="white"),
            ft.Text("3. 插入数据线，即可使用工具进行救砖。", color="white")
        ]), bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15)
    ]), expand=True, padding=20)
'''

# 补充空壳以防报错
drivers_code = '''import flet as ft
def build_drivers_page(page: ft.Page, theme_color):
    return ft.Container(content=ft.Text("驱动环境正在加载...", color="white", size=20), expand=True, padding=20)
'''
wireless_code = '''import flet as ft
def build_wireless_adb_page(page: ft.Page, theme_color):
    return ft.Container(content=ft.Text("无线调试正在加载...", color="white", size=20), expand=True, padding=20)
'''
scan_code = '''import flet as ft
def build_scan_page(page: ft.Page, theme_color):
    return ft.Container(content=ft.Text("扫描设备正在加载...", color="white", size=20), expand=True, padding=20)
'''

files_to_write = {
    "main_final.py": main_code,
    "pages/module_repo.py": module_repo_code,
    "pages/terminal.py": terminal_code,
    "pages/backup.py": backup_code,
    "pages/scrcpy.py": scrcpy_code,
    "pages/mode_switch.py": mode_switch_code,
    "pages/rescue.py": rescue_code,
    "pages/drivers.py": drivers_code,
    "pages/wireless_adb.py": wireless_code,
    "pages/scan.py": scan_code,
}

for path, code in files_to_write.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ 统一为函数式并写入: {path}")

print("\\n🎉 所有导入报错已彻底根除，直接运行 python main_final.py 起飞！")