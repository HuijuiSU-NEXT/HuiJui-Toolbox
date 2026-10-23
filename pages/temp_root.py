import flet as ft
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
EXTRACTOR_PATH = os.path.join(BIN_DIR, "ghostlock-extract.exe")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")
# 假设你的提权载荷放在 bin 目录下
GHOSTLOCK_BIN = os.path.join(BIN_DIR, "ghostlock-bin") 

def build_temp_root_page(page: ft.Page, theme_color):
    # ================= UI 组件 =================
    status_text = ft.Text("等待输入 OTA 链接或镜像...", size=13, weight=ft.FontWeight.W_600, color=theme_color, font_family="Microsoft YaHei")
    
    input_path = ft.TextField(
        label="OTA 链接 (http...) 或本地 boot.img / ZIP 路径",
        hint_text="例如: https://ota.example.com/update.zip",
        bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
        color="white",
        border_color=ft.Colors.with_opacity(0.2, theme_color),
        expand=True
    )
    
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color=getattr(page, "ui_style", {}).get("log_color", "#00FFD1"), 
        text_size=13, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor=getattr(page, "ui_style", {}).get("log_bg", "#05070A"), border_radius=12,
        padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    state = {"profile": None, "is_supported": False}

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    btn_analyze = ft.ElevatedButton("自动解析并检测", icon=ft.Icons.SEARCH, style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=10), padding=15))
    btn_import = ft.ElevatedButton("导入 Profile", icon=ft.Icons.UPLOAD_FILE, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), shape=ft.RoundedRectangleBorder(radius=10), padding=15))
    btn_root = ft.ElevatedButton("开始临时 Root", icon=ft.Icons.SECURITY, disabled=True, style=ft.ButtonStyle(color="#000000", bgcolor=ft.Colors.GREEN_400, shape=ft.RoundedRectangleBorder(radius=10), padding=15))

    def log(msg):
        log_area.value += msg + "\n"
        page.update()

    def run_cmd(cmd):
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=creationflags)
        out = ""
        for line in iter(proc.stdout.readline, ''):
            if line:
                log(line.strip())
                out += line
        proc.wait()
        return proc.returncode, out

    # ================= 核心检测流程 (保持原有逻辑) =================
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
                    log("❌ ZIP 内未找到 payload.bin。")
                    return None, None
                z.extract("payload.bin", BASE_DIR)
            log("✅ payload.bin 提取成功")

            log(f"> 正在提取 boot.img 与 xbl_config.img...")
            for d in os.listdir(BASE_DIR):
                if d.startswith("extracted_"):
                    try: shutil.rmtree(os.path.join(BASE_DIR, d))
                    except: pass
            
            cmd = f'"{DUMPER_PATH}" -q -p boot,xbl_config "{payload_path}"'
            run_cmd(cmd)

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

        if source.startswith("http"):
            zip_path = os.path.join(BASE_DIR, "ota_update.zip")
            if not download_file(source, zip_path):
                btn_analyze.disabled = False
                return
        else:
            if source.lower().endswith(".zip"): zip_path = source
            elif source.lower().endswith(".img"): boot_path = source

        if zip_path:
            if not os.path.exists(zip_path):
                log(f"❌ 找不到文件: {zip_path}")
                btn_analyze.disabled = False
                return
            boot_path, xbl_path = extract_boot_from_zip(zip_path)

        if not boot_path:
            log("❌ 无法提取到 boot.img。")
            btn_analyze.disabled = False
            return

        log("\n> 开始执行 GhostLock 偏移提取...")
        profile_path = os.path.join(BASE_DIR, "profile.conf")
        if os.path.exists(profile_path): os.remove(profile_path)

        if not os.path.exists(EXTRACTOR_PATH):
            log("⚠️ 未找到 ghostlock-extract.exe，无法生成 Profile！")
            log("💡 请放入工具，或手动点击“导入 Profile”。")
            btn_analyze.disabled = False
            page.update()
            return

        cmd = f'"{EXTRACTOR_PATH}" "{boot_path}"'
        if xbl_path: cmd += f' --xbl-config "{xbl_path}"'
        cmd += f' --format conf --out "{profile_path}"'

        ret, _ = run_cmd(cmd)

        if ret == 6:
            log("\n❌ 提取器报告退出码 6: 内核已修复，无法利用。")
        elif ret == 0 and os.path.exists(profile_path) and os.path.getsize(profile_path) > 0:
            log("\n✅ 偏移提取成功！Profile 已就绪。")
            state["profile"] = profile_path
            state["is_supported"] = True
            btn_root.disabled = False
            status_text.value = "解析成功，准备就绪！"
            status_text.color = ft.Colors.GREEN
        else:
            log(f"\n❌ 偏移提取失败，退出码: {ret}")

        btn_analyze.disabled = False
        page.update()

    # ================= 外部 Profile 导入 =================
    def on_import_profile(e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            if not (path.endswith(".conf") or path.endswith(".json")): return
            state["profile"] = path
            state["is_supported"] = True
            btn_root.disabled = False
            log(f"> 已导入外部 Profile: {os.path.basename(path)}")
            status_text.value = "Profile 导入成功"
            status_text.color = ft.Colors.GREEN
            page.update()

    file_picker.on_result = on_import_profile
    btn_import.on_click = lambda _: file_picker.pick_files(allowed_extensions=["conf", "json"])

    # ================= 真实的提权执行流 =================
    def start_root_flow():
        if not state["is_supported"]: return
        btn_root.disabled = True
        log("\n========================================")
        log("[ 启动真实提权注入流程 ]")
        
        # 1. 检查 ADB 连接
        log("> 1. 检查设备连接...")
        ret, out = run_cmd(f'"{ADB_PATH}" devices')
        if "device" not in out.lower():
            log("❌ 未检测到 ADB 设备，请连接手机！")
            btn_root.disabled = False
            return

        # 2. 检查载荷
        log("> 2. 校验载荷与 Profile...")
        if not os.path.exists(GHOSTLOCK_BIN):
            log(f"⚠️ 未找到底层载荷 (GhostLock ELF 文件): {os.path.basename(GHOSTLOCK_BIN)}")
            log("💡 真实利用需将编译好的 ARM 载荷放入 bin 目录。")
            btn_root.disabled = False
            return

        # 3. 推送载荷
        log("> 3. 推送漏洞载荷至 /data/local/tmp/ ...")
        run_cmd(f'"{ADB_PATH}" push "{GHOSTLOCK_BIN}" /data/local/tmp/ghostlock')
        run_cmd(f'"{ADB_PATH}" push "{state["profile"]}" /data/local/tmp/profile.conf')

        # 4. 赋权并执行
        log("> 4. 赋予执行权限并运行...")
        run_cmd(f'"{ADB_PATH}" shell chmod 755 /data/local/tmp/ghostlock')
        
        # 执行漏洞利用 (通常需要传入 profile)
        log("> 正在执行内存提权...")
        exec_cmd = f'"{ADB_PATH}" shell "/data/local/tmp/ghostlock --profile /data/local/tmp/profile.conf"'
        run_cmd(exec_cmd)

        # 5. 验证
        log("\n> 5. 验证 Root 权限...")
        ret, out = run_cmd(f'"{ADB_PATH}" shell su -c id')
        if "uid=0" in out:
            log("✅ 提权成功！获取到 uid=0 (Root 权限)！")
            log("💡 提示: 重启手机后该权限将失效。")
            status_text.value = "临时 Root 成功！"
            status_text.color = ft.Colors.GREEN
        else:
            log("❌ 提权失败，未获取到 uid=0。")
            log("可能原因：内核不兼容 / 载荷执行崩溃 / SELinux 拦截")
            status_text.value = "提权失败"
            status_text.color = ft.Colors.RED
            btn_root.disabled = False # 允许重试
        
        page.update()

    btn_analyze.on_click = lambda _: threading.Thread(target=analyze_flow, daemon=True).start()
    btn_root.on_click = lambda _: threading.Thread(target=start_root_flow, daemon=True).start()

    # ================= UI 组装 =================
    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SECURITY, color=theme_color, size=28), ft.Text("临时 Root · GhostLock 动态解析引擎", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            
            ft.Container(
                content=ft.Column([
                    status_text,
                    ft.Container(height=5),
                    ft.Row([input_path]),
                    ft.Row([btn_analyze, btn_import, btn_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
                bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
                border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
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
