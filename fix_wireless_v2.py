# fix_wireless_v2.py
import os

wireless_code = '''import flet as ft
import threading
import subprocess
import os
import re
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

def build_wireless_adb_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=13, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    def run_adb(cmd, show_output=True):
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        if show_output: log(f"> adb {cmd}")
        try:
            res = subprocess.run(f'"{ADB_PATH}" {cmd}', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=creationflags)
            out = res.stdout.strip() + "\\n" + res.stderr.strip()
            if show_output and out.strip():
                for line in out.strip().split('\\n'):
                    log(f"  {line}")
            return out
        except Exception as e:
            log(f"❌ 执行失败: {e}")
            return ""

    # ================= 逻辑 1：一键插线转无线 =================
    def one_click_usb_to_wifi(e):
        btn_oneclick.disabled = True
        log_area.value = ""
        log("[1] 正在检查 USB 连接...")
        page.update()
        
        def thread():
            devs = run_adb("devices")
            if "device" not in devs.lower():
                log("❌ 未检测到 USB 设备，请先插上数据线，并确保开启了 USB 调试！")
                btn_oneclick.disabled = False
                page.update()
                return

            log("\\n[2] 开启 TCP/IP 端口 5555...")
            run_adb("tcpip 5555")
            time.sleep(1.5) # 等待端口开启
            
            log("\\n[3] 正在抓取局域网 IP...")
            out = run_adb("shell ip route", show_output=False)
            ip = None
            match = re.search(r'src\\s+(\\d+\\.\\d+\\.\\d+\\.\\d+)', out)
            if match:
                ip = match.group(1)
            else:
                out = run_adb("shell ifconfig wlan0", show_output=False)
                match = re.search(r'inet addr:(\\d+\\.\\d+\\.\\d+\\.\\d+)', out)
                if match: ip = match.group(1)

            if not ip:
                log("❌ 获取 IP 失败，请确保手机连接了 Wi-Fi。")
                btn_oneclick.disabled = False
                page.update()
                return

            log(f"✅ 获取到 IP: {ip}")
            log(f"\\n[4] 正在自动连接 {ip}:5555 ...")
            connect_out = run_adb(f"connect {ip}:5555")
            
            if "connected to" in connect_out:
                log(f"\\n🎉 无线连接成功！可以拔掉数据线了！")
            else:
                log("\\n⚠️ 连接失败，请重试。")
            
            btn_oneclick.disabled = False
            page.update()
        threading.Thread(target=thread, daemon=True).start()

    # ================= 逻辑 2：安卓 11+ 免线配对 =================
    input_ip = ft.TextField(label="IP 地址", hint_text="如 192.168.1.100", width=150, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=theme_color)
    input_port = ft.TextField(label="端口", hint_text="如 37123", width=100, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=theme_color)
    input_code = ft.TextField(label="6位配对码", hint_text="如 123456", width=120, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=theme_color)

    def pair_device(e):
        ip = input_ip.value.strip()
        port = input_port.value.strip()
        code = input_code.value.strip()
        if not ip or not port or not code:
            log("❌ 请填写完整的 IP、端口和配对码！")
            return
        
        btn_pair.disabled = True
        log(f"\\n> 正在尝试配对 {ip}:{port} 配对码: {code} ...")
        page.update()

        def thread():
            # 必须用 adb pair
            res = run_adb(f"pair {ip}:{port} {code}", show_output=True)
            if "Successfully paired" in res:
                log("\\n✅ 配对成功！正在尝试连接...")
                # 配对成功后通常需要用无线调试的端口进行 connect
                # 但为了简单，这里直接提示用户用常规端口连，或者尝试解析
                log("💡 请拔掉数据线后，在手机上查看『无线调试』的 IP 和端口，点击一键连接。")
            else:
                log("\\n❌ 配对失败，请检查 IP 端口是否对应，或配对码是否过期。")
            btn_pair.disabled = False
            page.update()
        threading.Thread(target=thread, daemon=True).start()

    # 断开按钮
    def disconnect(e):
        log("\\n[!] 正在断开所有无线连接...")
        run_adb("disconnect")
        page.update()

    # 按钮定义
    btn_oneclick = ft.ElevatedButton(
        "一键开启并连接 (需插线)", icon=ft.Icons.FLASH_ON, on_click=one_click_usb_to_wifi,
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )
    
    btn_pair = ft.ElevatedButton(
        "开始配对", icon=ft.Icons.LINK, on_click=pair_device,
        style=ft.ButtonStyle(color="#000000", bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    btn_disconnect = ft.ElevatedButton(
        "断开所有连接", icon=ft.Icons.LINK_OFF, on_click=disconnect,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.WIFI, color=theme_color, size=28),
                ft.Text("无线调试 (免插线极速版)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=10),
            
            # 模式 1
            ft.Container(
                content=ft.Column([
                    ft.Text("模式 A：插线一键转无线", size=16, weight=ft.FontWeight.BOLD, color=theme_color, font_family="Microsoft YaHei"),
                    ft.Text("如果手机现在插着线，点一下这个，程序会自动开端口、抓IP、连WIFI。连上后直接拔线。", size=12, color=ft.Colors.GREY_400),
                    ft.Row([btn_oneclick])
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            ),
            
            # 模式 2
            ft.Container(
                content=ft.Column([
                    ft.Text("模式 B：安卓 11+ 免线配对 (需手机开启无线调试)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400, font_family="Microsoft YaHei"),
                    ft.Text("无需数据线，但需在同一 Wi-Fi 下。在手机『无线调试 - 使用配对码配对设备』中获取信息填入下方。", size=12, color=ft.Colors.GREY_400),
                    ft.Row([input_ip, input_port, input_code, btn_pair], spacing=10)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            ),
            
            ft.Row([btn_disconnect], alignment=ft.MainAxisAlignment.END),
            ft.Container(height=10),
            ft.Text("底层通信日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

with open("pages/wireless_adb.py", "w", encoding="utf-8") as f:
    f.write(wireless_code)

print("✅ 无线调试 [极简双模式] 已注入完毕！")