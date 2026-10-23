# fix_remaining_pages.py
import os

# ==================== 1. 驱动环境 ====================
drivers_code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

def build_drivers_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=12, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 扫描驱动
    drivers = []
    if os.path.exists(BIN_DIR):
        for f in os.listdir(BIN_DIR):
            if f.endswith(".exe") and ("driver" in f.lower() or "setup" in f.lower() or "qcom" in f.lower() or "mtk" in f.lower()):
                drivers.append(f)

    def install_driver(e, exe_name):
        log(f"\\n> 正在启动底层驱动安装程序: {exe_name}")
        log("💡 请在弹出的安装窗口中点击『下一步』完成安装。")
        page.update()
        exe_path = os.path.join(BIN_DIR, exe_name)
        try:
            # 提权启动
            subprocess.Popen([exe_path], shell=True)
        except Exception as ex:
            log(f"❌ 启动失败: {ex}")

    cards = []
    if not drivers:
        log("⚠️ 未在 bin 目录找到驱动安装包。")
        cards.append(ft.Text("未找到驱动包，请将高通/MTK驱动.exe放入 bin 目录", color=ft.Colors.GREY_500))
    else:
        for d in drivers:
            cards.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SETTINGS_SUGGEST, color=theme_color),
                        ft.Text(d, size=14, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(expand=True),
                        ft.ElevatedButton("一键安装", icon=ft.Icons.INSTALL_DESKTOP, on_click=lambda e, name=d: install_driver(e, name), style=ft.ButtonStyle(bgcolor=theme_color, color="black"))
                    ]),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=15, border_radius=10
                )
            )

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.BUILD, color=theme_color, size=28), ft.Text("驱动环境", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(content=ft.Column(cards, spacing=10), bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), border_radius=15, padding=15),
            ft.Container(height=10),
            log_container
        ], expand=True), expand=True, padding=20
    )
'''

# ==================== 2. 分区备份 ====================
backup_code = '''import flet as ft
import subprocess
import os
import time
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

def build_backup_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=12, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 核心分区
    parts = ["boot", "init_boot", "recovery", "vbmeta", "dtbo", "persist", "modem", "super"]
    dropdown = ft.Dropdown(
        label="选择要备份的分区", value="boot", width=200,
        options=[ft.dropdown.Option(p) for p in parts],
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white"
    )

    btn_backup = ft.ElevatedButton("一键备份", icon=ft.Icons.SAVE, style=ft.ButtonStyle(bgcolor=theme_color, color="black", shape=ft.RoundedRectangleBorder(radius=10), padding=15))

    def do_backup(e):
        part = dropdown.value
        btn_backup.disabled = True
        log(f"\\n> 开始备份分区: {part}")
        page.update()

        def thread():
            bk_dir = os.path.join(BASE_DIR, "backups")
            os.makedirs(bk_dir, exist_ok=True)
            timestamp = int(time.time())
            local_file = os.path.join(bk_dir, f"{part}_{timestamp}.img")
            remote_file = f"/sdcard/{part}_{timestamp}.img"

            log(f"[1/3] 正在通过 Root 提取 {part} 到手机内存...")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if=/dev/block/by-name/{part} of={remote_file}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            log(f"\\n[2/3] 正在拉取到电脑: {local_file}")
            cmd_pull = f'"{ADB_PATH}" pull {remote_file} "{local_file}"'
            proc = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            log(f"\\n[3/3] 正在清理手机临时文件...")
            subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_file}\\""', shell=True, capture_output=True)

            log("✅ 备份完成！")
            btn_backup.disabled = False
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    btn_backup.on_click = do_backup

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), ft.Text("分区备份 (真Root)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(content=ft.Row([dropdown, btn_backup]), bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15),
            ft.Container(height=10),
            log_container
        ], expand=True), expand=True, padding=20
    )
'''

# ==================== 3. 模式切换 ====================
mode_code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
FB_PATH = os.path.join(BASE_DIR, "bin", "fastboot.exe")

def build_mode_switch_page(page: ft.Page, theme_color):
    status = ft.Text("等待操作...", size=14, color=theme_color)
    
    def run_cmd(cmd, msg):
        status.value = msg
        page.update()
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

    def make_btn(text, icon, cmd, msg):
        return ft.Container(
            content=ft.Row([ft.Icon(icon, color="white"), ft.Text(text, size=16, color="white", weight=ft.FontWeight.BOLD)]),
            bgcolor=ft.Colors.with_opacity(0.1, theme_color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, theme_color)),
            border_radius=10, padding=20,
            on_click=lambda _: run_cmd(cmd, msg)
        )

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=theme_color, size=28), ft.Text("模式切换", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            status,
            ft.Container(height=10),
            ft.GridView(expand=1, runs_count=2, max_extent=300, spacing=15, run_spacing=15, controls=[
                make_btn("重启到系统 (System)", ft.Icons.PHONE_ANDROID, f'"{ADB_PATH}" reboot', "正在重启到系统..."),
                make_btn("重启到 Bootloader", ft.Icons.FLASH_ON, f'"{ADB_PATH}" reboot bootloader', "正在进入 Fastboot..."),
                make_btn("重启到 Recovery", ft.Icons.HEALING, f'"{ADB_PATH}" reboot recovery', "正在进入 Recovery..."),
                make_btn("重启到 EDL (9008)", ft.Icons.ERROR, f'"{ADB_PATH}" shell "su -c reboot edl"', "正在进入 9008 模式...")
            ])
        ], expand=True), expand=True, padding=20
    )
'''

# 写入
with open("pages/drivers.py", "w", encoding="utf-8") as f: f.write(drivers_code)
with open("pages/backup.py", "w", encoding="utf-8") as f: f.write(backup_code)
with open("pages/mode_switch.py", "w", encoding="utf-8") as f: f.write(mode_code)

print("✅ 驱动环境、分区备份、模式切换 三大页面真逻辑已注入！")