# fix_scrcpy_v3.py
import os

scrcpy_code = '''import flet as ft
import subprocess
import os
import threading
import time
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
SCRCPY_PATH = os.path.join(BIN_DIR, "scrcpy.exe")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")

# 使用国内加速镜像下载 scrcpy (以 v3.1 为例)
SCRCPY_DOWNLOAD_URL = "https://ghproxy.net/https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-win64-v3.1.zip"

def build_scrcpy_page(page: ft.Page, theme_color):
    state = {"process": None}

    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, height=150, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 自动下载并解压 scrcpy
    def install_scrcpy(e=None):
        log("> 正在准备下载 Scrcpy (Windows 64位)...")
        log("> 使用镜像加速下载中，请稍候...")
        page.update()
        
        def thread():
            tmp_zip = os.path.join(BIN_DIR, "scrcpy_tmp.zip")
            try:
                req = urllib.request.Request(SCRCPY_DOWNLOAD_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as response, open(tmp_zip, 'wb') as out_file:
                    data = response.read(1024 * 1024)
                    while data:
                        out_file.write(data)
                        data = response.read(1024 * 1024)
                
                log("✅ 下载完成，正在解压...")
                with zipfile.ZipFile(tmp_zip, 'r') as z:
                    # 压缩包里有个多套了一层文件夹，我们要把里面的文件提出来
                    for file_info in z.infolist():
                        if file_info.is_dir(): continue
                        # 只提取文件，忽略顶层文件夹
                        filename = os.path.basename(file_info.filename)
                        if filename:
                            target_path = os.path.join(BIN_DIR, filename)
                            with z.open(file_info) as source, open(target_path, "wb") as target:
                                shutil.copyfileobj(source, target)
                
                os.remove(tmp_zip)
                log("✅ Scrcpy 及依赖库已成功部署到 bin 目录！")
                status_badge.value = "环境就绪"
                status_badge.color = ft.Colors.GREEN
                page.update()
            except Exception as ex:
                log(f"❌ 下载/解压失败: {ex}")
                log("💡 请检查网络，或手动下载 scrcpy 并解压到 bin 目录。")
                page.update()
        threading.Thread(target=thread, daemon=True).start()

    # 环境自检
    def check_env(e=None):
        log_area.value = ""
        log("> 正在执行底层环境自检...")
        missing = []
        if not os.path.exists(ADB_PATH):
            missing.append("adb.exe")
        if not os.path.exists(SCRCPY_PATH):
            missing.append("scrcpy.exe")
            
        if missing:
            log(f"⚠️ 缺失核心组件: {', '.join(missing)}")
            status_badge.value = "环境缺失"
            status_badge.color = ft.Colors.RED
            btn_install.visible = "scrcpy.exe" in missing
        else:
            log("✅ adb 和 scrcpy 均已在位，环境完美！")
            status_badge.value = "环境完美"
            status_badge.color = ft.Colors.GREEN
            btn_install.visible = False
        page.update()

    # 参数配置 UI
    dd_max_size = ft.Dropdown(
        label="分辨率限制", value="1080", width=120,
        options=[ft.dropdown.Option("原生"), ft.dropdown.Option("1080"), ft.dropdown.Option("720"), ft.dropdown.Option("480")],
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white"
    )
    dd_bitrate = ft.Dropdown(
        label="视频码率", value="8M", width=120,
        options=[ft.dropdown.Option("默认"), ft.dropdown.Option("2M"), ft.dropdown.Option("8M"), ft.dropdown.Option("16M"), ft.dropdown.Option("32M")],
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white"
    )
    dd_fps = ft.Dropdown(
        label="帧率 (FPS)", value="60", width=120,
        options=[ft.dropdown.Option("默认"), ft.dropdown.Option("30"), ft.dropdown.Option("60"), ft.dropdown.Option("120")],
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white"
    )

    cb_turn_off = ft.Checkbox(label="投屏时关闭手机屏幕", value=False, label_style=ft.TextStyle(color="white"))
    cb_stay_awake = ft.Checkbox(label="保持手机常亮", value=False, label_style=ft.TextStyle(color="white"))
    cb_fullscreen = ft.Checkbox(label="启动即全屏", value=False, label_style=ft.TextStyle(color="white"))
    cb_show_touches = ft.Checkbox(label="显示屏幕触摸点", value=False, label_style=ft.TextStyle(color="white"))
    cb_record = ft.Checkbox(label="开启电脑端录制 (保存为 mp4)", value=False, label_style=ft.TextStyle(color=theme_color))

    status_badge = ft.Text("等待自检", size=13, color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD)

    btn_install = ft.ElevatedButton(
        "一键下载补齐 Scrcpy", icon=ft.Icons.CLOUD_DOWNLOAD, on_click=install_scrcpy, 
        visible=False, bgcolor=ft.Colors.ORANGE_700, color="white"
    )

    def start_scrcpy(e):
        if not os.path.exists(SCRCPY_PATH):
            log("❌ 错误: bin 目录下找不到 scrcpy.exe！请先点击上方按钮下载。")
            return
        
        # 检查是否有设备连接
        try:
            res = subprocess.run(f'"{ADB_PATH}" devices', shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if "device" not in res.stdout.lower():
                log("❌ 未检测到设备！请确保手机已通过 USB 或无线连接。")
                return
        except Exception as ex:
            log(f"❌ 检查设备失败: {ex}")
            return

        cmd = [SCRCPY_PATH]
        
        if dd_max_size.value != "原生": cmd.extend(["--max-size", dd_max_size.value])
        if dd_bitrate.value != "默认": cmd.extend(["--video-bit-rate", dd_bitrate.value])
        if dd_fps.value != "默认": cmd.extend(["--max-fps", dd_fps.value])
        if cb_turn_off.value: cmd.append("--turn-screen-off")
        if cb_stay_awake.value: cmd.append("--stay-awake")
        if cb_fullscreen.value: cmd.append("--fullscreen")
        if cb_show_touches.value: cmd.append("--show-touches")

        if cb_record.value:
            record_file = f"record_{int(time.time())}.mp4"
            cmd.extend(["--record", record_file])
            log(f"🔴 已开启录制，文件将保存至: {record_file}")

        log(f"\\n> 正在启动 Scrcpy...")
        log(f"> 执行命令: {' '.join(cmd)}")
        page.update()

        try:
            state["process"] = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            log("✅ Scrcpy 已启动，请在独立窗口中操作。")
        except Exception as ex:
            log(f"❌ 启动失败: {ex}")

    def kill_scrcpy(e):
        log("> 正在尝试关闭所有 Scrcpy 进程...")
        try:
            subprocess.run("taskkill /F /IM scrcpy.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            log("✅ 已发送关闭指令。")
        except Exception as ex:
            log(f"❌ 关闭失败: {ex}")

    # 初始化时静默执行一次自检
    def init_check():
        time.sleep(0.5)
        check_env()
        
    threading.Thread(target=init_check, daemon=True).start()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MONITOR, color=theme_color, size=28),
                ft.Text("Scrcpy 旗舰级投屏控制台", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_badge,
                btn_install
            ]),
            ft.Container(height=10),
            
            # 参数面板
            ft.Container(
                content=ft.Column([
                    ft.Row([dd_max_size, dd_bitrate, dd_fps], spacing=20),
                    ft.Container(height=10),
                    ft.Row([cb_turn_off, cb_stay_awake]),
                    ft.Row([cb_fullscreen, cb_show_touches]),
                    ft.Row([cb_record]),
                    ft.Container(height=15),
                    ft.Row([
                        ft.ElevatedButton(
                            "启动 Scrcpy 投屏", icon=ft.Icons.PLAY_ARROW, on_click=start_scrcpy,
                            style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
                        ),
                        ft.ElevatedButton(
                            "强制关闭投屏", icon=ft.Icons.CLOSE, on_click=kill_scrcpy,
                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_900, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=15,
                padding=20
            ),
            
            ft.Container(height=10),
            ft.Text("操作日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

with open("pages/scrcpy.py", "w", encoding="utf-8") as f:
    f.write(scrcpy_code)

print("✅ 自动补齐环境版 Scrcpy 注入完毕！")