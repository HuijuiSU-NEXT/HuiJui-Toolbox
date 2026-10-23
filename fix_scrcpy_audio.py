# fix_scrcpy_audio.py
import os

scrcpy_code = '''import flet as ft
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

    def send_keyevent(keycode, action_name):
        def run():
            try:
                subprocess.run(f'"{ADB_PATH}" shell input keyevent {keycode}', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                log(f"> 发送指令: {action_name} (Keycode: {keycode})")
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
    dd_max_size = ft.Dropdown(label="分辨率限制", value="原生", width=120, options=[ft.dropdown.Option("原生"), ft.dropdown.Option("1080"), ft.dropdown.Option("720"), ft.dropdown.Option("480")], bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")
    dd_bitrate = ft.Dropdown(label="视频码率", value="8M", width=120, options=[ft.dropdown.Option("默认"), ft.dropdown.Option("2M"), ft.dropdown.Option("8M"), ft.dropdown.Option("16M")], bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")
    dd_fps = ft.Dropdown(label="帧率 (FPS)", value="60", width=120, options=[ft.dropdown.Option("默认"), ft.dropdown.Option("30"), ft.dropdown.Option("60"), ft.dropdown.Option("120")], bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")

    # 新增音频选项
    cb_audio_forward = ft.Checkbox(label="强制转发音频 (需 Android 11+)", value=True, label_style=ft.TextStyle(color=theme_color))
    cb_audio_dup = ft.Checkbox(label="电脑和手机同时发声", value=True, label_style=ft.TextStyle(color="white"))

    cb_turn_off = ft.Checkbox(label="投屏时关闭手机屏幕", value=False, label_style=ft.TextStyle(color="white"))
    cb_stay_awake = ft.Checkbox(label="保持手机常亮", value=False, label_style=ft.TextStyle(color="white"))
    cb_fullscreen = ft.Checkbox(label="启动即全屏", value=False, label_style=ft.TextStyle(color="white"))
    cb_show_touches = ft.Checkbox(label="显示屏幕触摸点", value=False, label_style=ft.TextStyle(color="white"))
    cb_record = ft.Checkbox(label="开启电脑端录制", value=False, label_style=ft.TextStyle(color=theme_color))

    def start_scrcpy(e):
        if not os.path.exists(SCRCPY_PATH):
            log("❌ 错误: bin 目录下找不到 scrcpy.exe！")
            return
        
        btn_start.disabled = True
        log_area.value = ""
        log("> 正在检查 ADB 设备连接...")
        page.update()

        def thread():
            try:
                res = subprocess.run(f'"{ADB_PATH}" devices', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                if "device" not in res.stdout.lower():
                    log("❌ 启动终止: 未检测到已授权的 ADB 设备！")
                    btn_start.disabled = False
                    page.update()
                    return

                cmd = [SCRCPY_PATH]
                if dd_max_size.value != "原生": cmd.extend(["--max-size", dd_max_size.value])
                if dd_bitrate.value != "默认": cmd.extend(["--video-bit-rate", dd_bitrate.value])
                if dd_fps.value != "默认": cmd.extend(["--max-fps", dd_fps.value])
                
                # 🚨 核心音频参数
                if cb_audio_forward.value:
                    cmd.extend(["--audio-codec=aac"]) # Scrcpy 默认用 opus，aac 在 Windows 上兼容性更好
                    if cb_audio_dup.value:
                        cmd.append("--audio-dup")

                if cb_turn_off.value: cmd.append("--turn-screen-off")
                if cb_stay_awake.value: cmd.append("--stay-awake")
                if cb_fullscreen.value: cmd.append("--fullscreen")
                if cb_show_touches.value: cmd.append("--show-touches")

                if cb_record.value:
                    record_file = f"record_{int(time.time())}.mp4"
                    cmd.extend(["--record", record_file])
                    log(f"🔴 录制已开启: {record_file}")

                log(f"> 正在启动 Scrcpy...")
                log(f"> 命令: {' '.join(cmd)}")
                page.update()
                
                # 启动 Scrcpy（独立控制台模式更稳）
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                log("✅ Scrcpy 已弹出独立窗口。")
            except Exception as ex:
                log(f"❌ 启动发生异常: {ex}")
            finally:
                btn_start.disabled = False
                page.update()

        threading.Thread(target=thread, daemon=True).start()

    def kill_scrcpy(e):
        log("> 正在尝试关闭所有 Scrcpy 进程...")
        subprocess.run("taskkill /F /IM scrcpy.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        log("✅ 已发送关闭指令。")

    btn_start = ft.ElevatedButton(
        "启动 Scrcpy 投屏", icon=ft.Icons.PLAY_ARROW, on_click=start_scrcpy,
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MONITOR, color=theme_color, size=28),
                ft.Text("Scrcpy 旗舰级投屏控制台", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                ft.Text("环境完美", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD)
            ]),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([dd_max_size, dd_bitrate, dd_fps], spacing=20),
                    ft.Container(height=10),
                    ft.Row([cb_audio_forward, cb_audio_dup]), # 加入音频选项
                    ft.Row([cb_turn_off, cb_stay_awake]),
                    ft.Row([cb_fullscreen, cb_show_touches]),
                    ft.Row([cb_record]),
                    ft.Container(height=15),
                    
                    ft.Text("快捷遥控导航 (ADB 无线控制)", size=14, color=theme_color, weight=ft.FontWeight.BOLD),
                    nav_bar,
                    
                    ft.Container(height=15),
                    ft.Row([
                        btn_start,
                        ft.ElevatedButton("强制关闭投屏", icon=ft.Icons.CLOSE, on_click=kill_scrcpy, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_900, shape=ft.RoundedRectangleBorder(radius=10), padding=15))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=15, padding=20
            ),
            ft.Container(height=10),
            ft.Text("实时运行日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True, padding=20
    )
'''

with open("pages/scrcpy.py", "w", encoding="utf-8") as f:
    f.write(scrcpy_code)

print("✅ 音频转发补丁注入完毕！")