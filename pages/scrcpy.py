import flet as ft
import subprocess
import os
import threading
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
SCRCPY_PATH = os.path.join(BIN_DIR, "scrcpy.exe")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")

def build_scrcpy_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color=getattr(page, "ui_style", {}).get("log_color", "#00FFD1"), 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor=getattr(page, "ui_style", {}).get("log_bg", "#05070A"), border_radius=12,
        padding=15, height=120, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )

    def log(msg):
        log_area.value += msg + "\n"
        page.update()

    def send_keyevent(keycode, action_name):
        def run():
            try:
                subprocess.run(f'"{ADB_PATH}" shell input keyevent {keycode}', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                log(f"> 发送指令: {action_name}")
            except Exception as e:
                log(f"❌ 指令发送失败: {e}")
        threading.Thread(target=run, daemon=True).start()

    def make_key_btn(icon, keycode, tooltip):
        return ft.IconButton(
            icon=icon, icon_color="white", icon_size=24, tooltip=tooltip,
            style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), shape=ft.CircleBorder()),
            on_click=lambda _: send_keyevent(keycode, tooltip)
        )

    nav_bar = ft.Container(
        content=ft.Row([
            make_key_btn(ft.Icons.ARROW_BACK, 4, "返回键"),
            make_key_btn(ft.Icons.HOME, 3, "主屏幕"),
            make_key_btn(ft.Icons.RECTANGLE, 187, "多任务"),
            ft.Container(width=20),
            make_key_btn(ft.Icons.VOLUME_UP, 24, "音量+"),
            make_key_btn(ft.Icons.VOLUME_DOWN, 25, "音量-"),
            make_key_btn(ft.Icons.POWER_SETTINGS_NEW, 26, "电源/锁屏"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        bgcolor=ft.Colors.with_opacity(0.05, theme_color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, theme_color)),
        border_radius=20, padding=ft.padding.symmetric(vertical=10, horizontal=20)
    )

    # 参数配置 UI
    dd_max_size = ft.Dropdown(label="分辨率", value="原生", width=110, options=[ft.dropdown.Option("原生"), ft.dropdown.Option("1080"), ft.dropdown.Option("720")], bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)), color="white")
    dd_bitrate = ft.Dropdown(label="码率", value="8M", width=110, options=[ft.dropdown.Option("默认"), ft.dropdown.Option("2M"), ft.dropdown.Option("8M"), ft.dropdown.Option("16M")], bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)), color="white")
    dd_fps = ft.Dropdown(label="帧率", value="60", width=110, options=[ft.dropdown.Option("默认"), ft.dropdown.Option("30"), ft.dropdown.Option("60"), ft.dropdown.Option("120")], bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)), color="white")

    # 🚀 低延迟模式开关
    cb_low_latency = ft.Checkbox(label="🚀 开启电竞低延迟模式 (无线首选)", value=False, label_style=ft.TextStyle(color=ft.Colors.ORANGE_400, weight=ft.FontWeight.BOLD))
    
    cb_audio_forward = ft.Checkbox(label="转发音频 (Android 11+)", value=True, label_style=ft.TextStyle(color=theme_color))
    cb_audio_dup = ft.Checkbox(label="电脑手机同时发声", value=True, label_style=ft.TextStyle(color="white"))

    cb_turn_off = ft.Checkbox(label="投屏时息屏", value=False, label_style=ft.TextStyle(color="white"))
    cb_stay_awake = ft.Checkbox(label="保持常亮", value=False, label_style=ft.TextStyle(color="white"))
    cb_fullscreen = ft.Checkbox(label="启动全屏", value=False, label_style=ft.TextStyle(color="white"))
    cb_show_touches = ft.Checkbox(label="显示触摸点", value=False, label_style=ft.TextStyle(color="white"))

    def start_scrcpy(e):
        if not os.path.exists(SCRCPY_PATH):
            log("❌ 错误: 找不到 scrcpy.exe！")
            return
        
        btn_start.disabled = True
        log_area.value = ""
        log("> 检查设备连接...")
        page.update()

        def thread():
            try:
                res = subprocess.run(f'"{ADB_PATH}" devices', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                if "device" not in res.stdout.lower():
                    log("❌ 未检测到已授权的 ADB 设备！")
                    btn_start.disabled = False
                    page.update()
                    return

                cmd = [SCRCPY_PATH]
                
                # 🚨 核心逻辑：如果勾选了低延迟，强制覆盖参数
                if cb_low_latency.value:
                    log("> 已开启电竞低延迟模式，强制锁定 720p/2M/30帧 (H.264)...")
                    cmd.extend(["--max-size=720", "--video-bit-rate=2M", "--max-fps=30", "--video-codec=h264"])
                    # 低延迟模式下通常不需要息屏，否则可能增加唤醒延迟
                    if cb_fullscreen.value: cmd.append("--fullscreen")
                else:
                    if dd_max_size.value != "原生": cmd.extend(["--max-size", dd_max_size.value])
                    if dd_bitrate.value != "默认": cmd.extend(["--video-bit-rate", dd_bitrate.value])
                    if dd_fps.value != "默认": cmd.extend(["--max-fps", dd_fps.value])
                    if cb_turn_off.value: cmd.append("--turn-screen-off")
                    if cb_stay_awake.value: cmd.append("--stay-awake")
                    if cb_fullscreen.value: cmd.append("--fullscreen")
                    if cb_show_touches.value: cmd.append("--show-touches")

                if cb_audio_forward.value:
                    cmd.extend(["--audio-codec=aac"])
                    if cb_audio_dup.value: cmd.append("--audio-dup")

                log(f"> 正在启动 Scrcpy...")
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log("✅ Scrcpy 已启动，纯画面无控制台模式。")
            except Exception as ex:
                log(f"❌ 启动异常: {ex}")
            finally:
                btn_start.disabled = False
                page.update()

        threading.Thread(target=thread, daemon=True).start()

    def kill_scrcpy(e):
        log("> 正在关闭 Scrcpy...")
        subprocess.run("taskkill /F /IM scrcpy.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        log("✅ 已关闭。")

    btn_start = ft.ElevatedButton(
        "启动投屏", icon=ft.Icons.PLAY_ARROW, on_click=start_scrcpy,
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MONITOR, color=theme_color, size=28),
                ft.Text("Scrcpy 投屏控制台", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                ft.Text("环境完美", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD)
            ]),
            ft.Container(height=5),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([dd_max_size, dd_bitrate, dd_fps], spacing=20),
                    ft.Container(height=5),
                    # 突出显示低延迟开关
                    ft.Container(
                        content=cb_low_latency,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE_900),
                        border=ft.border.all(1, ft.Colors.ORANGE_700),
                        border_radius=8, padding=10
                    ),
                    ft.Row([cb_audio_forward, cb_audio_dup]),
                    ft.Row([cb_turn_off, cb_stay_awake, cb_fullscreen, cb_show_touches]),
                    ft.Container(height=10),
                    
                    ft.Text("快捷遥控导航", size=14, color=theme_color, weight=ft.FontWeight.BOLD),
                    nav_bar,
                    
                    ft.Container(height=10),
                    ft.Row([
                        btn_start,
                        ft.ElevatedButton("关闭投屏", icon=ft.Icons.CLOSE, on_click=kill_scrcpy, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_900, shape=ft.RoundedRectangleBorder(radius=10), padding=15))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
                border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
                border_radius=15, padding=20
            ),
            ft.Container(height=10),
            ft.Text("实时运行日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True, padding=20
    )
