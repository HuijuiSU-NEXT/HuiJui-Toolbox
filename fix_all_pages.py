import os

# 确保 pages 文件夹存在
os.makedirs("pages", exist_ok=True)

# ==================== 1. 控制台：pages/dashboard.py ====================
dashboard_code = """import flet as ft

def build_dashboard(page: ft.Page, theme_color, scan_device, switch_tab, goto_sub_page):
    cards_data = [
        {"title": "一键刷机", "subtitle": "全自动向导页面", "icon": ft.Icons.BOLT, "route": "flash"},
        {"title": "扫描设备", "subtitle": "读取手机状态与 Root", "icon": ft.Icons.PHONE_ANDROID, "route": "scan"},
        {"title": "临时 Root", "subtitle": "KMI 无痕注入", "icon": ft.Icons.SECURITY, "route": "temp_root"},
        {"title": "模块仓库", "subtitle": "797 个纯净模块", "icon": ft.Icons.EXTENSION, "route": "module_repo"},
        {"title": "高级终端", "subtitle": "实时 Shell 执行", "icon": ft.Icons.TERMINAL, "route": "terminal"},
        {"title": "Scrcpy 投屏", "subtitle": "USB / 无线投屏", "icon": ft.Icons.MONITOR, "route": "scrcpy"},
        {"title": "分区备份", "subtitle": "保护 boot / init_boot", "icon": ft.Icons.SAVE, "route": "backup"},
        {"title": "无线调试", "subtitle": "TCPIP 与 IP 自动获取", "icon": ft.Icons.WIFI, "route": "wireless_adb"},
        {"title": "模式切换", "subtitle": "Fastboot / Fastbootd", "icon": ft.Icons.SWAP_HORIZ, "route": "mode_switch"},
        {"title": "驱动环境", "subtitle": "一键安装底层驱动", "icon": ft.Icons.BUILD, "route": "drivers"},
        {"title": "急救中心", "subtitle": "9008 / BROM 救砖", "icon": ft.Icons.HEALTH_AND_SAFETY, "route": "rescue"},
    ]

    def handle_card_click(route):
        if route == "flash":
            switch_tab(1)
        elif route == "scan":
            scan_device()
        elif route == "temp_root":
            switch_tab(2)
        else:
            goto_sub_page(route)

    grid = ft.GridView(
        expand=1,
        runs_count=3,
        max_extent=250,
        child_aspect_ratio=2.5,
        spacing=15,
        run_spacing=15,
    )

    for card in cards_data:
        card_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(card["icon"], color=theme_color, size=20),
                    ft.Text(card["title"], weight=ft.FontWeight.BOLD, size=14, color="white")
                ]),
                ft.Text(card["subtitle"], size=11, color=ft.Colors.GREY_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            border_radius=12,
            padding=15,
            on_click=lambda e, r=card["route"]: handle_card_click(r)
        )
        grid.controls.append(card_container)

    return ft.Container(
        content=ft.Column([
            ft.Text("Matrix Dashboard", size=30, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("原生 GPU 渲染 · 分布式极客中心", color=ft.Colors.GREY_400),
            ft.Container(height=20),
            grid
        ]),
        expand=True,
        padding=20
    )
"""

# ==================== 2. 高级终端：pages/terminal.py ====================
terminal_code = """import flet as ft
import threading
import subprocess

class TerminalPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        self.terminal_output = ft.TextField(
            multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, 
            color=ft.Colors.GREEN_400, border=ft.InputBorder.NONE, text_size=14,
            value="HuiJui Core Terminal v1.0\\n等待输入命令...\\n",
            text_style=ft.TextStyle(font_family="Consolas")
        )
        
        self.cmd_input = ft.TextField(
            hint_text="输入命令并回车执行 (如 adb devices)...", on_submit=self.run_cmd,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), border_radius=10,
            color=ft.Colors.WHITE, border=ft.InputBorder.NONE
        )
        
        self.content = ft.Column([
            ft.Row([ft.Icon(ft.Icons.TERMINAL, color=ft.Colors.GREEN_400), 
                    ft.Text("高级终端 · 实时 Shell", size=20, weight=ft.FontWeight.BOLD, color="white")]),
            self.terminal_output,
            self.cmd_input
        ], expand=True, spacing=10, padding=20)

    def run_cmd(self, e):
        cmd = self.cmd_input.value.strip()
        if not cmd: return
        self.cmd_input.value = ""
        self.append_log(f"\\n> {cmd}\\n")
        self.page.update()
        threading.Thread(target=self._exec_cmd_thread, args=(cmd,), daemon=True).start()

    def _exec_cmd_thread(self, cmd):
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
            for line in iter(process.stdout.readline, ''):
                if line: self.append_log(line)
            process.stdout.close()
            process.wait()
            self.append_log(f"\\n[进程结束, 退出码: {process.returncode}]\\n")
        except Exception as ex:
            self.append_log(f"\\n[执行出错]: {str(ex)}\\n")

    def append_log(self, text):
        self.terminal_output.value += text
        self.page.update()
"""

# ==================== 3. 驱动环境：pages/drivers.py ====================
drivers_code = """import flet as ft
import os
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

class DriversPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.status_text = ft.Text("等待操作...", color=ft.Colors.CYAN_400)
        self.log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color=ft.Colors.GREEN_400)
        
        drivers = []
        if os.path.exists(BIN_DIR):
            for f in os.listdir(BIN_DIR):
                if f.endswith(".exe") and ("driver" in f.lower() or "setup" in f.lower()):
                    drivers.append(f)
        if not drivers: drivers = ["未在 bin 目录找到驱动安装包(.exe)"]

        self.content = ft.Column([
            ft.Row([ft.Icon(ft.Icons.BUILD, color=ft.Colors.CYAN_400), ft.Text("底层驱动环境", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            self.status_text,
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Text("检测到的驱动包:", color="white"),
            ft.Column([ft.ElevatedButton(text=f"安装 {d}", icon=ft.Icons.INSTALL_DESKTOP, on_click=lambda e, drv=d: self.install_driver(drv)) for d in drivers]),
            ft.Divider(color=ft.Colors.GREY_800),
            self.log_area
        ], expand=True, spacing=15, padding=20)

    def install_driver(self, exe_name):
        if "未在" in exe_name: return
        self.status_text.value = f"正在启动 {exe_name}..."
        self.status_text.color = ft.Colors.ORANGE
        self.page.update()
        
        def run():
            exe_path = os.path.join(BIN_DIR, exe_name)
            try:
                process = subprocess.Popen([exe_path], shell=True)
                self.append_log(f"已启动安装程序: {exe_path}\\n请在弹出的窗口中完成安装...\\n")
                process.wait()
                self.status_text.value = "安装进程已结束"
                self.status_text.color = ft.Colors.GREEN
                self.page.update()
            except Exception as ex:
                self.append_log(f"启动失败: {str(ex)}")
                self.status_text.value = "启动失败"
                self.status_text.color = ft.Colors.RED
                self.page.update()
        threading.Thread(target=run, daemon=True).start()

    def append_log(self, text):
        self.log_area.value += text + "\\n"
        self.page.update()
"""

# ==================== 4. 无线调试：pages/wireless_adb.py ====================
wireless_code = """import flet as ft
import os
import subprocess
import threading
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

class WirelessAdbPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.status_text = ft.Text("请确保手机已通过 USB 连接电脑。", color="white")
        self.log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color=ft.Colors.GREEN_400, value="终端就绪...\\n")

        self.content = ft.Column([
            ft.Row([ft.Icon(ft.Icons.WIFI, color=ft.Colors.CYAN_400), ft.Text("无线调试 (TCP/IP)", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            self.status_text,
            ft.ElevatedButton("一键开启并连接无线调试", icon=ft.Icons.SETTINGS_REMOTE, on_click=self.start_wireless, bgcolor=ft.Colors.CYAN_700, color="white"),
            ft.Divider(color=ft.Colors.GREY_800),
            self.log_area
        ], expand=True, spacing=15, padding=20)

    def start_wireless(self, e):
        self.status_text.value = "正在执行底层命令..."
        self.status_text.color = ft.Colors.ORANGE
        self.log_area.value = ""
        self.page.update()
        threading.Thread(target=self._run_logic, daemon=True).start()

    def _run_logic(self):
        if not os.path.exists(ADB_PATH):
            self.append_log(f"错误: 找不到 adb.exe, 路径: {ADB_PATH}")
            return
        self.append_log("> adb tcpip 5555")
        self._exec_cmd(f'"{ADB_PATH}" tcpip 5555')
        self.append_log("\\n> 正在获取手机局域网 IP...")
        out = self._exec_cmd(f'"{ADB_PATH}" shell ip route')
        match = re.search(r'src\\s+(\\d+\\.\\d+\\.\\d+\\.\\d+)', out)
        if match:
            ip = match.group(1)
            self.append_log(f"✅ 获取到 IP: {ip}")
            self.append_log(f"\\n> adb connect {ip}:5555")
            self._exec_cmd(f'"{ADB_PATH}" connect {ip}:5555')
            self.status_text.value = f"已完成，请拔掉数据线测试是否依然在线。"
            self.status_text.color = ft.Colors.GREEN
        else:
            self.append_log("❌ 获取 IP 失败，请确保 USB 连接正常且已开启 ADB。")
            self.status_text.value = "操作失败"
            self.status_text.color = ft.Colors.RED
        self.page.update()

    def _exec_cmd(self, cmd):
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if res.stdout: self.append_log(res.stdout.strip())
            if res.stderr: self.append_log(f"[Err] {res.stderr.strip()}")
            return res.stdout
        except Exception as ex:
            self.append_log(f"执行异常: {ex}")
            return ""

    def append_log(self, text):
        self.log_area.value += text + "\\n"
        self.page.update()
"""

# ==================== 5. 剩余占位页面 (漂亮版) ====================
placeholder_template = """import flet as ft

class {class_name}(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.content = ft.Column([
            ft.Icon(ft.Icons.ROCKET_LAUNCH, size=60, color=ft.Colors.CYAN_400),
            ft.Text("{title}", size=28, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("核心模块正在极速开发中，敬请期待...", color=ft.Colors.GREY_400)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
"""

# ==================== 6. 原有函数式占位页面 ====================
flash_code = """import flet as ft

def build_flash_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Column([
            ft.Text("一键刷机 - 功能开发中", size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.ProgressRing(color=theme_color)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True
    )
"""

temp_root_code = """import flet as ft

def build_temp_root_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Text("临时 Root - 功能开发中", size=24, color="white"),
        expand=True
    )
"""

# ==================== 批量写入 ====================
files_to_write = {
    "pages/dashboard.py": dashboard_code,
    "pages/terminal.py": terminal_code,
    "pages/drivers.py": drivers_code,
    "pages/wireless_adb.py": wireless_code,
    "pages/flash.py": flash_code,
    "pages/temp_root.py": temp_root_code,
    
    # 漂亮占位页
    "pages/module_repo.py": placeholder_template.format(class_name="ModuleRepoPage", title="模块仓库"),
    "pages/scrcpy.py": placeholder_template.format(class_name="ScrcpyPage", title="Scrcpy 投屏"),
    "pages/backup.py": placeholder_template.format(class_name="BackupPage", title="分区备份"),
    "pages/mode_switch.py": placeholder_template.format(class_name="ModeSwitchPage", title="模式切换"),
    "pages/rescue.py": placeholder_template.format(class_name="RescuePage", title="急救中心"),
}

for path, content in files_to_write.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 成功写入: {path}")

print("\\n🎉 所有文件编码已强制修复 (UTF-8)，核心功能已注入，兄弟冲！")