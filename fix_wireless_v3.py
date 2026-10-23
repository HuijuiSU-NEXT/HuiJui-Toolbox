# fix_wireless_v3.py
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

    # ================= 模式 A：插线一键转无线 =================
    def one_click_usb_to_wifi(e):
        btn_oneclick.disabled = True
        log_area.value = ""
        log("[1] 正在重置 ADB 服务并检查 USB 连接...")
        page.update()
        
        def thread():
            run_adb("kill-server", show_output=False)
            time.sleep(1)
            devs = run_adb("devices")
            
            if "device" not in devs.lower():
                log("❌ 未检测到 USB 设备，请先插上数据线！")
                btn_oneclick.disabled = False
                page.update()
                return

            log("\\n[2] 开启 TCP/IP 端口 5555...")
            run_adb("tcpip 5555")
            time.sleep(2) 
            
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
                log(f"\\n🎉 无线连接成功！现在可以拔掉数据线了！")
            else:
                log("\\n⚠️ 连接失败，请重试。")
            
            btn_oneclick.disabled = False
            page.update()
        threading.Thread(target=thread, daemon=True).start()

    # ================= 模式 B：安卓 11+ 免线配对 =================
    input_pair_ip = ft.TextField(label="配对 IP", width=130, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")
    input_pair_port = ft.TextField(label="配对端口", width=90, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")
    input_code = ft.TextField(label="6位码", width=90, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")

    def pair_device(e):
        ip = input_pair_ip.value.strip()
        port = input_pair_port.value.strip()
        code = input_code.value.strip()
        if not ip or not port or not code:
            log("❌ 请填写完整的 IP、配对端口和配对码！")
            return
        
        btn_pair.disabled = True
        log(f"\\n> 重置 ADB 服务...")
        page.update()

        def thread():
            run_adb("kill-server", show_output=False)
            time.sleep(1)
            run_adb("start-server", show_output=False)
            time.sleep(1)

            log(f"> 正在尝试配对 {ip}:{port} 配对码: {code} ...")
            res = run_adb(f"pair {ip}:{port} {code}", show_output=True)
            
            if "Successfully paired" in res:
                log("\\n✅ 配对成功！")
                log("💡 注意：请看一眼手机『无线调试』主页，上面有个『IP 地址和端口』(不是配对端口)。")
                log("👉 将那个端口填入下方的『连接端口』并点击连接。")
            else:
                log("\\n❌ 配对失败，请确保手机配对弹窗还没关，重新填最新的端口和码重试。")
            btn_pair.disabled = False
            page.update()
        threading.Thread(target=thread, daemon=True).start()

    # ================= 模式 B 后续：手动连接 =================
    input_conn_ip = ft.TextField(label="连接 IP", width=130, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")
    input_conn_port = ft.TextField(label="连接端口", width=100, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white")

    def manual_connect(e):
        ip = input_conn_ip.value.strip()
        port = input_conn_port.value.strip()
        if not ip or not port:
            log("❌ 请填写连接 IP 和端口！")
            return
        
        log(f"\\n> 正在连接 {ip}:{port} ...")
        res = run_adb(f"connect {ip}:{port}", show_output=True)
        if "connected to" in res:
            log(f"\\n🎉 连接成功！")
        else:
            log("\\n❌ 连接失败，端口可能已改变或被占用。")

    btn_manual_connect = ft.ElevatedButton(
        "连接", icon=ft.Icons.CABLE, on_click=manual_connect,
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=10)
    )

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
        "配对", icon=ft.Icons.LINK, on_click=pair_device,
        style=ft.ButtonStyle(color="#000000", bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10), padding=10)
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
            
            # 模式 A
            ft.Container(
                content=ft.Column([
                    ft.Text("模式 A：插线一键转无线", size=16, weight=ft.FontWeight.BOLD, color=theme_color, font_family="Microsoft YaHei"),
                    ft.Text("手机插线，点一下，自动开端口抓IP并连接。连完直接拔线即可。", size=12, color=ft.Colors.GREY_400),
                    ft.Row([btn_oneclick])
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)), border_radius=15, padding=20
            ),
            
            # 模式 B
            ft.Container(
                content=ft.Column([
                    ft.Text("模式 B：安卓 11+ 免线配对", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400, font_family="Microsoft YaHei"),
                    ft.Text("不要插线！在手机『无线调试-使用配对码配对』弹窗中获取信息。", size=12, color=ft.Colors.GREY_400),
                    ft.Row([input_pair_ip, input_pair_port, input_code, btn_pair], spacing=10),
                    ft.Divider(color=ft.Colors.GREY_800, height=20),
                    ft.Text("配对成功后，填入手机『无线调试』主页显示的端口进行连接：", size=12, color=ft.Colors.GREY_400),
                    ft.Row([input_conn_ip, input_conn_port, btn_manual_connect], spacing=10)
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

print("✅ v3 无线调试修复版注入完毕！加入了 ADB 重置与双端口引导！")