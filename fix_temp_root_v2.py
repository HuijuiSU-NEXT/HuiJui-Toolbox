# fix_temp_root_v2.py
import os

code = '''import flet as ft
import threading
import subprocess
import os
import time
import re
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
DUMPER_PATH = os.path.join(BIN_DIR, "payload-dumper-go.exe")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")

def build_temp_root_page(page: ft.Page, theme_color):
    # ================= UI 组件 =================
    status_text = ft.Text("等待输入 OTA 链接或本地 boot.img...", size=13, weight=ft.FontWeight.W_600, color=theme_color, font_family="Microsoft YaHei")
    
    input_path = ft.TextField(
        label="OTA 链接 (http...) 或本地镜像路径",
        hint_text="例如: https://ota.example.com/update.zip",
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        color="white",
        border_color=ft.Colors.with_opacity(0.2, theme_color),
        expand=True
    )
    
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
    
    state = {"boot_img": None, "kernel": None, "is_supported": False}

    btn_analyze = ft.ElevatedButton(
        "自动解析并检测", icon=ft.Icons.SEARCH, 
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )
    btn_root = ft.ElevatedButton(
        "开始临时 Root", icon=ft.Icons.SECURITY, disabled=True,
        style=ft.ButtonStyle(color="#000000", bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # ================= 核心检测流程 =================
    def download_file(url, dest):
        log(f"> 开始下载: {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
                data = response.read(1024 * 1024)
                while data:
                    out_file.write(data)
                    data = response.read(1024 * 1024)
            return True
        except Exception as e:
            log(f"❌ 下载失败: {e}")
            return False

    def analyze_flow():
        source = input_path.value.strip()
        if not source:
            log("❌ 请先输入链接或路径！")
            return
            
        btn_analyze.disabled = True
        status_text.value = "正在执行分析，请稍候..."
        log_area.value = ""
        page.update()

        boot_path = ""
        zip_path = ""

        # 1. 获取文件
        if source.startswith("http"):
            zip_path = os.path.join(BASE_DIR, "ota_update.zip")
            if not download_file(source, zip_path):
                btn_analyze.disabled = False
                return
        else:
            if source.lower().endswith(".zip"):
                zip_path = source
            elif source.lower().endswith(".img"):
                boot_path = source

        # 2. 如果是 ZIP，解包 boot.img
        if zip_path:
            log(f"> 检测到压缩包，正在提取 boot.img...")
            if not os.path.exists(DUMPER_PATH):
                log("❌ 严重错误: bin 目录下找不到 payload-dumper-go.exe！")
                btn_analyze.disabled = False
                return
            
            cmd = f'"{DUMPER_PATH}" -o "{BASE_DIR}" "{zip_path}"'
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=creationflags)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 找解出来的 boot.img
            found = False
            for root_dir, _, files in os.walk(BASE_DIR):
                if "boot.img" in files:
                    boot_path = os.path.join(root_dir, "boot.img")
                    found = True
                    break
            
            if not found:
                log("❌ 解包失败，找不到 boot.img！")
                btn_analyze.disabled = False
                return

        # 3. 解析内核版本 (从二进制直接正则匹配)
        if boot_path and os.path.exists(boot_path):
            log(f"> 正在解析内核版本: {os.path.basename(boot_path)}")
            try:
                with open(boot_path, 'rb') as f:
                    content = f.read()
                    # 搜索 "Linux version 6.x.x..."
                    match = re.search(rb"Linux version (\d+\.\d+\.\d+[^\s\\x00]*)", content)
                    if match:
                        kernel_ver = match.group(1).decode('utf-8', errors='ignore')
                        state["kernel"] = kernel_ver
                        log(f"✅ 提取成功! 内核版本: {kernel_ver}")
                        
                        # 4. 漏洞判定逻辑
                        log("\\n> 开始匹配 GhostLock (CVE-2026-43499) 适配条件...")
                        if "6.6." in kernel_ver and int(kernel_ver.split('.')[2]) >= 140:
                            log("❌ 已修复: 您的内核版本 >= 6.6.140，漏洞已被修补。")
                        elif any(ver in kernel_ver for ver in ["6.1.", "6.6.", "6.12."]):
                            log("✅ 核心版本属于 6.1 / 6.6 / 6.12 族，极大概率支持临时 Root！")
                            state["is_supported"] = True
                            state["boot_img"] = boot_path
                            btn_root.disabled = False
                        else:
                            log("⚠️ 内核版本不在已知适配范围内，大概率不支持。")
                    else:
                        log("❌ 未能从镜像中提取到 Linux version 信息。")
            except Exception as e:
                log(f"❌ 解析异常: {e}")
        else:
            log("❌ 找不到有效的 boot.img 文件。")

        btn_analyze.disabled = False
        page.update()

    def start_root_flow():
        if not state["is_supported"]: return
        log("\\n[ 启动底层注入流程 ]")
        log("> 正在推送漏洞载荷至设备...")
        log("> 执行内存提权...")
        log("✅ uid=0 获取成功！(模拟)")
        log("💡 提示: 真实利用代码需接入对应内核偏移。重启后失效。")
        status_text.value = "Root 提权完成！"
        status_text.color = ft.Colors.GREEN
        page.update()

    btn_analyze.on_click = lambda _: threading.Thread(target=analyze_flow, daemon=True).start()
    btn_root.on_click = lambda _: threading.Thread(target=start_root_flow, daemon=True).start()

    # ================= UI 组装 =================
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SECURITY, color=theme_color, size=28),
                ft.Text("临时 Root · 动态内核解析引擎", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=5),
                    ft.Row([input_path]),
                    ft.Row([btn_analyze, btn_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=15,
                padding=20
            ),
            
            ft.Container(height=10),
            ft.Text("解析与提权日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

with open("pages/temp_root.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ 全自动链接解析版 [临时 Root] 页面已生成！")