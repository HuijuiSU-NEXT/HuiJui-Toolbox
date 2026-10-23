# fix_temp_root_v4.py
import os

code = '''import flet as ft
import threading
import subprocess
import os
import time
import re
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
DUMPER_PATH = os.path.join(BIN_DIR, "payload-dumper-go.exe")
EXTRACTOR_PATH = os.path.join(BIN_DIR, "ghostlock-extract.exe") # 偏移提取工具
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")

def build_temp_root_page(page: ft.Page, theme_color):
    # ================= UI 组件 =================
    status_text = ft.Text("等待输入 OTA 链接或镜像...", size=13, weight=ft.FontWeight.W_600, color=theme_color, font_family="Microsoft YaHei")
    
    input_path = ft.TextField(
        label="OTA 链接 (http...) 或本地 boot.img / ZIP 路径",
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
    
    state = {"profile": None, "is_supported": False}

    # 文件选择器 (用于导入外部 Profile)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    btn_analyze = ft.ElevatedButton(
        "自动解析并检测", icon=ft.Icons.SEARCH, 
        style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15)
    )
    btn_import = ft.ElevatedButton(
        "导入 Profile", icon=ft.Icons.UPLOAD_FILE, 
        style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), shape=ft.RoundedRectangleBorder(radius=10), padding=15)
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
            log("✅ 下载完成")
            return True
        except Exception as e:
            log(f"❌ 下载失败: {e}")
            return False

    def extract_boot_from_zip(zip_path):
        payload_path = os.path.join(BASE_DIR, "payload.bin")
        if os.path.exists(payload_path): os.remove(payload_path)
        
        log(f"> 正在从 ZIP 提取 payload.bin...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                if "payload.bin" not in z.namelist():
                    log("❌ ZIP 内未找到 payload.bin，可能不是标准 OTA 包。")
                    return None, None
                z.extract("payload.bin", BASE_DIR)
            log("✅ payload.bin 提取成功")

            log(f"> 正在使用 payload-dumper-go 提取 boot.img 与 xbl_config.img...")
            for d in os.listdir(BASE_DIR):
                if d.startswith("extracted_"):
                    try: shutil.rmtree(os.path.join(BASE_DIR, d))
                    except: pass
            
            # 同时提取 boot 和 xbl_config (高通平台偏移提取需要)
            cmd = f'"{DUMPER_PATH}" -q -p boot,xbl_config "{payload_path}"'
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', cwd=BASE_DIR, creationflags=creationflags)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            boot_path, xbl_path = None, None
            for root_dir, _, files in os.walk(BASE_DIR):
                if "boot.img" in files: boot_path = os.path.join(root_dir, "boot.img")
                if "xbl_config.img" in files: xbl_path = os.path.join(root_dir, "xbl_config.img")
            
            return boot_path, xbl_path
        except Exception as e:
            log(f"❌ 解压失败: {e}")
            return None, None

    def analyze_flow():
        source = input_path.value.strip()
        if not source:
            log("❌ 请先输入链接或路径！")
            return
            
        btn_analyze.disabled = True
        status_text.value = "正在执行分析，请稍候..."
        log_area.value = ""
        state["is_supported"] = False
        btn_root.disabled = True
        page.update()

        boot_path, xbl_path = None, None
        zip_path = ""

        # 1. 获取文件
        if source.startswith("http"):
            zip_path = os.path.join(BASE_DIR, "ota_update.zip")
            if not download_file(source, zip_path):
                btn_analyze.disabled = False
                return
        else:
            if source.lower().endswith(".zip"): zip_path = source
            elif source.lower().endswith(".img"): boot_path = source

        # 2. 提取镜像
        if zip_path:
            if not os.path.exists(zip_path):
                log(f"❌ 找不到文件: {zip_path}")
                btn_analyze.disabled = False
                return
            boot_path, xbl_path = extract_boot_from_zip(zip_path)

        if not boot_path:
            log("❌ 无法提取到 boot.img，分析中止。")
            btn_analyze.disabled = False
            return

        # 3. 偏移提取 (GhostLock 官方规范)
        log("\\n> 开始执行 GhostLock 偏移提取...")
        profile_path = os.path.join(BASE_DIR, "profile.conf")
        if os.path.exists(profile_path): os.remove(profile_path)

        if not os.path.exists(EXTRACTOR_PATH):
            log("⚠️ 未找到 ghostlock-extract.exe")
            log("💡 将尝试读取内核版本进行粗略匹配...")
            try:
                with open(boot_path, 'rb') as f:
                    content = f.read()
                    match = re.search(rb"Linux version (\d+\.\d+\.\d+[^\s\\x00]*)", content)
                    if match:
                        kernel_ver = match.group(1).decode('utf-8', errors='ignore')
                        log(f"✅ 内核版本: {kernel_ver}")
                        if "6.6." in kernel_ver and int(kernel_ver.split('.')[2]) >= 140:
                            log("❌ 已修复: 内核版本 >= 6.6.140")
                        elif any(ver in kernel_ver for ver in ["6.1.", "6.6.", "6.12."]):
                            log("⚠️ 粗略匹配通过，但缺少偏移文件，极度危险！")
                        else:
                            log("❌ 内核不在支持族内。")
            except Exception as e:
                log(f"❌ 解析异常: {e}")
            btn_analyze.disabled = False
            page.update()
            return

        # 调用 GhostLock 提取器
        cmd = f'"{EXTRACTOR_PATH}" "{boot_path}"'
        if xbl_path:
            log(f"> 检测到 xbl_config.img，将用于高通平台物理地址提取")
            cmd += f' --xbl-config "{xbl_path}"'
        cmd += f' --format conf --out "{profile_path}"'

        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=creationflags)
        for line in iter(proc.stdout.readline, ''):
            if line: log(line.strip())
        proc.wait()

        # 4. 判断结果
        if proc.returncode == 6:
            log("\\n❌ 提取器报告退出码 6: 内核的 remove_waiter() 已修复，无法利用。")
        elif proc.returncode == 0 and os.path.exists(profile_path) and os.path.getsize(profile_path) > 0:
            log("\\n✅ 偏移提取成功！Profile 已生成。")
            state["profile"] = profile_path
            state["is_supported"] = True
            btn_root.disabled = False
            status_text.value = "解析成功，Profile 已就绪！"
            status_text.color = ft.Colors.GREEN
        else:
            log(f"\\n❌ 偏移提取失败，退出码: {proc.returncode}")

        btn_analyze.disabled = False
        page.update()

    # ================= 外部 Profile 导入 =================
    def on_import_profile(e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            if not (path.endswith(".conf") or path.endswith(".json")):
                log("❌ 仅支持 .conf 或 .json 格式的 Profile 文件")
                return
            state["profile"] = path
            state["is_supported"] = True
            btn_root.disabled = False
            log(f"> 已导入外部 Profile: {os.path.basename(path)}")
            status_text.value = "Profile 导入成功，准备就绪"
            status_text.color = ft.Colors.GREEN
            page.update()

    file_picker.on_result = on_import_profile
    btn_import.on_click = lambda _: file_picker.pick_files(allowed_extensions=["conf", "json"])

    # ================= 执行提权 =================
    def start_root_flow():
        if not state["is_supported"]: return
        log("\\n[ 启动底层注入流程 ]")
        log(f"> 加载 Profile: {os.path.basename(state['profile'])}")
        log("> 正在推送漏洞载荷至设备...")
        log("> 执行内存提权...")
        log("✅ uid=0 获取成功！(演示)")
        log("💡 提示: 真实利用代码需读取 Profile 并执行对应内核漏洞。重启后失效。")
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
                ft.Text("临时 Root · GhostLock 动态解析引擎", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=5),
                    ft.Row([input_path]),
                    ft.Row([btn_analyze, btn_import, btn_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
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

print("✅ v4 官方规范版注入完毕！支持 ghostlock-extract 以及外部 Profile 导入！")