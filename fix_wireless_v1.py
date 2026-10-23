# fix_wireless_v1.py
import os

wireless_code = '''import flet as ft
import threading
import subprocess
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

def build_wireless_adb_page(page: ft.Page, theme_color):
    status_text = ft.Text("等待操作 (首次开启需插数据线)...", size=13, weight=ft.FontWeight.W_600, color=theme_color, font_family="Microsoft YaHei")
    
    ip_display = ft.Text("IP 地址: 未获取", size=18, weight=ft.FontWeight.BOLD, color="white", font_family="Consolas")
    
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

    # 状态锁定，防止并发点击
    state = {"busy": False, "connected_ip": None}

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

    # 1. 开启无线调试端口
    def enable_tcpip(e):
        if state["busy"]: return
        state["busy"] = True
        status_text.value = "正在开启端口，请确保已插线..."
        status_text.color = ft.Colors.ORANGE
        log_area.value = ""
        page.update()

        def thread():
            log("[1] 检查 USB 设备...")
            devs = run_adb("devices")
            if "device" not in devs.lower():
                log("❌ 未检测到通过 USB 连接的手机！")
                status_text.value = "开启失败: 未检测到设备"
                status_text.color = ft.Colors.RED
                state["busy"] = False
                page.update()
                return

            log("\\n[2] 正在设置 TCP/IP 端口 5555...")
            run_adb("tcpip 5555")
            
            log("\\n✅ 端口已开启，你可以拔掉数据线了。")
            status_text.value = "端口已开启，请拔线或点击获取 IP"
            status_text.color = ft.Colors.GREEN
            state["busy"] = False
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    # 2. 自动获取 IP 并连接
    def auto_connect(e):
        if state["busy"]: return
        state["busy"] = True
        status_text.value = "正在获取 IP 并尝试连接..."
        status_text.color = ft.Colors.ORANGE
        page.update()

        def thread():
            log("\\n[1] 正在获取局域网 IP...")
            out = run_adb("shell ip route", show_output=False)
            
            ip = None
            # 匹配 src 192.168.x.x 或者 wlan0
            match = re.search(r'src\\s+(\\d+\\.\\d+\\.\\d+\\.\\d+)', out)
            if match:
                ip = match.group(1)
            else:
                # 备用方案，通过 ifconfig
                out = run_adb("shell ifconfig wlan0", show_output=False)
                match = re.search(r'inet addr:(\\d+\\.\\d+\\.\\d+\\.\\d+)', out)
                if match:
                    ip = match.group(1)

            if not ip:
                log("❌ 无法获取 IP，请检查手机是否连上了 Wi-Fi。")
                status_text.value = "获取 IP 失败"
                status_text.color = ft.Colors.RED
                state["busy"] = False
                page.update()
                return

            ip_display.value = f"IP 地址: {ip}"
            log(f"✅ 获取到手机 IP: {ip}")

            log(f"\\n[2] 正在连接 {ip}:5555 ...")
            connect_out = run_adb(f"connect {ip}:5555")
            
            if "connected to" in connect_out:
                state["connected_ip"] = ip
                status_text.value = f"已成功连接至 {ip}"
                status_text.color = ft.Colors.GREEN
                log(f"\\n🎉 无线连接成功！现在可以拔掉数据线了。")
            else:
                log("\\n⚠️ 连接失败，请确保刚才开启了端口 5555 且手机与电脑在同一 Wi-Fi 下。")
                status_text.value = "连接失败"
                status_text.color = ft.Colors.RED
            
            state["busy"] = False
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    # 3. 断开连接
    def disconnect(e):
        log("\\n[!] 正在断开无线连接...")
        run_adb("disconnect")
        state["connected_ip"] = None
        ip_display.value = "IP 地址: 未获取"
        status_text.value = "已断开无线连接"
        status_text.color = theme_color
        page.update()

    # 按钮样式
    btn_enable = ft.ElevatedButton(
        "1. 开启无线端口", icon=ft.Icons.ROUTER, on_click=enable_tcpip,
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )
    btn_connect = ft.ElevatedButton(
        "2. 获取IP并连接", icon=ft.Icons.WIFI, on_click=auto_connect,
        style=ft.ButtonStyle(color="#000000", bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )
    btn_disconnect = ft.ElevatedButton(
        "断开连接", icon=ft.Icons.LINK_OFF, on_click=disconnect,
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.WIFI, color=theme_color, size=28),
                ft.Text("无线调试 (TCP/IP)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=10),
                    ip_display,
                    ft.Container(height=15),
                    ft.Row([btn_enable, btn_connect, btn_disconnect], spacing=15)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=15,
                padding=20
            ),
            
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

print("✅ 无线调试页面 [无线 ADB 控制台] 已注入完毕！")