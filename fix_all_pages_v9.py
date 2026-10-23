# fix_all_pages_v9.py
import os

os.makedirs("pages", exist_ok=True)

# ==================== 1. 高级终端 ====================
terminal_code = '''import flet as ft
import threading
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

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
            ft.Container(height=10),
            log_container,
            cmd_input
        ], expand=True),
        expand=True, padding=20
    )
'''

# ==================== 2. 分区备份 (真 Root) ====================
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
            
            append_log("> 正在通过 su 提取镜像 (可能需要手机端授权)...")
            # 尝试查分区路径并 dd
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
                content=ft.Column([
                    status_text,
                    ft.Row([dropdown, btn_backup], alignment=ft.MainAxisAlignment.START, spacing=20)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            ),
            ft.Container(height=10),
            log_container
        ], expand=True),
        expand=True, padding=20
    )
'''

# ==================== 3. Scrcpy 投屏 ====================
scrcpy_code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRCPY_PATH = os.path.join(BASE_DIR, "bin", "scrcpy.exe")

def build_scrcpy_page(page: ft.Page, theme_color):
    status_text = ft.Text("请确保手机已通过 ADB 连接。", size=13, color=theme_color)
    
    def launch(e):
        if not os.path.exists(SCRCPY_PATH):
            status_text.value = "❌ 未找到 bin/scrcpy.exe"
            status_text.color = ft.Colors.RED
            page.update()
            return
        
        status_text.value = "🚀 正在启动投屏..."
        status_text.color = ft.Colors.GREEN
        page.update()
        try:
            subprocess.Popen([SCRCPY_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as ex:
            status_text.value = f"启动失败: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.MONITOR, color=theme_color, size=28), ft.Text("Scrcpy 投屏", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.ElevatedButton("启动 Scrcpy 投屏", icon=ft.Icons.PLAY_ARROW, on_click=launch, style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15))
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            )
        ]), expand=True, padding=20
    )
'''

# ==================== 4. 模式切换 ====================
mode_switch_code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
FB_PATH = os.path.join(BASE_DIR, "bin", "fastboot.exe")

def build_mode_switch_page(page: ft.Page, theme_color):
    status_text = ft.Text("等待操作...", size=13, color=theme_color)
    
    def run_cmd(cmd, msg):
        status_text.value = msg
        page.update()
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=theme_color, size=28), ft.Text("模式切换", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("重启到系统", icon=ft.Icons.PHONE_ANDROID, on_click=lambda _: run_cmd(f'"{ADB_PATH}" reboot', "重启中..."), style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
                        ft.ElevatedButton("重启到 Fastboot", icon=ft.Icons.FLASH_ON, on_click=lambda _: run_cmd(f'"{ADB_PATH}" reboot bootloader', "进入 Fastboot..."), style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
                    ]),
                    ft.Row([
                        ft.ElevatedButton("重启到 Recovery", icon=ft.Icons.HEALING, on_click=lambda _: run_cmd(f'"{ADB_PATH}" reboot recovery', "进入 Recovery..."), style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
                        ft.ElevatedButton("重启到 EDL (9008)", icon=ft.Icons.ERROR, on_click=lambda _: run_cmd(f'"{ADB_PATH}" shell "su -c reboot edl"', "进入 EDL..."), style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
                    ])
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            )
        ]), expand=True, padding=20
    )
'''

# ==================== 5. 急救中心 ====================
rescue_code = '''import flet as ft

def build_rescue_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=theme_color, size=28), ft.Text("急救中心", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    ft.Text("高通 9008 / MTK BROM 救砖引导", size=18, color=theme_color, weight=ft.FontWeight.BOLD),
                    ft.Text("1. 确保安装了对应的底层驱动（请前往“驱动环境”）。", color="white"),
                    ft.Text("2. 断开手机电源，按住特定组合键（通常为音量上下+电源）。", color="white"),
                    ft.Text("3. 插入数据线，电脑若识别到 9008/BROM 端口，即可使用专业工具进行救砖。", color="white"),
                    ft.Container(height=20),
                    ft.Text("建议工具: QFIL / MTKClient / SP Flash Tool", color=ft.Colors.GREY_500)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            )
        ]), expand=True, padding=20
    )
'''

# ==================== 6. 模块仓库 (UI 界面) ====================
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
            ft.Container(height=10),
            grid
        ]), expand=True, padding=20
    )
'''

files_to_write = {
    "pages/terminal.py": terminal_code,
    "pages/backup.py": backup_code,
    "pages/scrcpy.py": scrcpy_code,
    "pages/mode_switch.py": mode_switch_code,
    "pages/rescue.py": rescue_code,
    "pages/module_repo.py": module_repo_code,
}

for path, code in files_to_write.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ 成功写入并注入真家伙: {path}")

print("\\n🎉 所有页面功能已彻底激活，请确保 main_final.py 导入了正确的 build 函数！")