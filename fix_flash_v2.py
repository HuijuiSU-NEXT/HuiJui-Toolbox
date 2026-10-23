# fix_flash_v2.py
import os

flash_code = '''import flet as ft
import threading
import subprocess
import zipfile
import os
import time
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")
FB_PATH = os.path.join(BIN_DIR, "fastboot.exe")
DUMPER_PATH = os.path.join(BIN_DIR, "payload-dumper-go.exe")

PHYSICAL = [
    ("vbmeta", "vbmeta.img", "--disable-verity --disable-verification"),
    ("vbmeta_system", "vbmeta_system.img", "--disable-verity --disable-verification"),
    ("vbmeta_vendor", "vbmeta_vendor.img", "--disable-verity --disable-verification"),
    ("boot", "boot.img", ""), ("init_boot", "init_boot.img", ""),
    ("vendor_boot", "vendor_boot.img", ""), ("dtbo", "dtbo.img", ""),
]
LOGICAL = [
    ("system", "system.img"), ("system_ext", "system_ext.img"),
    ("product", "product.img"), ("vendor", "vendor.img"),
    ("odm", "odm.img"), ("mi_ext", "mi_ext.img"),
    ("vendor_dlkm", "vendor_dlkm.img"), ("system_dlkm", "system_dlkm.img"),
]
PAYLOAD_PARTS = ("boot,init_boot,vendor_boot,dtbo,vbmeta,vbmeta_system,"
                 "vbmeta_vendor,system,system_ext,product,vendor,odm,"
                 "mi_ext,vendor_dlkm,system_dlkm")

def build_flash_page(page: ft.Page, theme_color):
    status_text = ft.Text("等待选择官方卡刷包 (.zip)...", color="white")
    progress_bar = ft.ProgressBar(value=0, color=theme_color, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE))
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.BLACK, color=ft.Colors.GREEN_400, 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas")
    )
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()
    
    state = {"zip_path": None, "extract_dir": None, "is_running": False}

    btn_pick = ft.ElevatedButton("选择卡刷包 (.zip)", icon=ft.Icons.FOLDER_OPEN)
    btn_start = ft.ElevatedButton("开始刷机", icon=ft.Icons.FLASH_ON, bgcolor=theme_color, color="black", disabled=True)

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    def on_pick(e: ft.FilePickerResultEvent):
        if e.files:
            state["zip_path"] = e.files[0].path
            status_text.value = f"已选择: {os.path.basename(state['zip_path'])}"
            status_text.color = theme_color
            btn_start.disabled = False
            log(f"> 目标文件: {state['zip_path']}")
            page.update()

    file_picker.on_result = on_pick
    btn_pick.on_click = lambda _: file_picker.pick_files(allowed_extensions=["zip"])

    def run_cmd(cmd, cwd=None, on_line=None):
        log(f"> {cmd}")
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace', cwd=cwd, 
                creationflags=creationflags
            )
            for line in iter(proc.stdout.readline, ''):
                if line:
                    line = line.strip()
                    if on_line: on_line(line)
                    else: log(line)
            proc.stdout.close()
            proc.wait()
            return proc.returncode
        except Exception as ex:
            log(f"❌ 执行异常: {ex}")
            return -1

    def flash_flow():
        try:
            progress_bar.value = 0.05
            log("\\n[1/7] 正在提取 payload.bin...")
            payload_path = os.path.join(BASE_DIR, "payload.bin")
            if os.path.exists(payload_path): os.remove(payload_path)

            with zipfile.ZipFile(state["zip_path"], 'r') as z:
                if "payload.bin" not in z.namelist():
                    log("❌ 卡刷包内未找到 payload.bin！")
                    finish(False); return
                z.extract("payload.bin", BASE_DIR)

            progress_bar.value = 0.15
            log("\\n[2/7] 正在解包分区镜像 (payload-dumper-go)...")
            prog_re = re.compile(r"\\[(\\d+)/(\\d+)\\]")
            def on_dump_line(line):
                m = prog_re.search(line)
                if m:
                    d, t = int(m.group(1)), int(m.group(2))
                    progress_bar.value = 0.15 + 0.35 * (d / max(t, 1))
                    page.update()
                    log(line)
                else: log(line)

            cmd = f'"{DUMPER_PATH}" -q -p {PAYLOAD_PARTS} payload.bin'
            run_cmd(cmd, cwd=BASE_DIR, on_line=on_dump_line)

            for d in sorted(os.listdir(BASE_DIR), reverse=True):
                if d.startswith("extracted_"):
                    state["extract_dir"] = os.path.join(BASE_DIR, d)
                    break
            
            if not state["extract_dir"]:
                log("❌ 解包失败，找不到镜像目录！"); finish(False); return

            progress_bar.value = 0.55
            log("\\n[3/7] 检测设备状态...")
            fb_out = run_cmd(f'"{FB_PATH}" devices')
            if not fb_out or "fastboot" not in fb_out.lower():
                log("\\n未检测到 Fastboot，尝试从 ADB 重启...")
                run_cmd(f'"{ADB_PATH}" reboot bootloader')
                time.sleep(5)
                for i in range(20):
                    fb_out = run_cmd(f'"{FB_PATH}" devices')
                    if fb_out and "fastboot" in fb_out.lower(): break
                    time.sleep(1)

            log("\\n[4/7] 开始刷入物理分区...")
            for name, filename, args in PHYSICAL:
                file_path = os.path.join(state["extract_dir"], filename)
                if os.path.exists(file_path):
                    log(f"-> 刷入 {name} ...")
                    run_cmd(f'"{FB_PATH}" {args} flash {name} "{file_path}"')
            
            progress_bar.value = 0.75
            log("\\n[5/7] 切换到 Fastbootd...")
            run_cmd(f'"{FB_PATH}" reboot fastboot')
            time.sleep(3)
            
            log("\\n[6/7] 开始刷入逻辑分区...")
            for name, filename in LOGICAL:
                file_path = os.path.join(state["extract_dir"], filename)
                if os.path.exists(file_path):
                    log(f"-> 刷入 {name} ...")
                    run_cmd(f'"{FB_PATH}" flash {name} "{file_path}"')
            
            progress_bar.value = 0.95
            log("\\n[7/7] 正在重启系统...")
            run_cmd(f'"{FB_PATH}" reboot')
            
            progress_bar.value = 1.0
            log("\\n🎉 刷机成功！首次开机可能需要 10-15 分钟。")
            finish(True)

        except Exception as ex:
            log(f"❌ 刷机异常: {ex}")
            finish(False)

    def start_flash(e):
        if not state["zip_path"] or not os.path.exists(state["zip_path"]): return
        state["is_running"] = True
        btn_pick.disabled = True
        btn_start.disabled = True
        btn_start.text = "刷机中..."
        progress_bar.value = 0
        log_area.value = ""
        page.update()
        threading.Thread(target=flash_flow, daemon=True).start()

    def finish(success):
        state["is_running"] = False
        btn_pick.disabled = False
        btn_start.disabled = False
        btn_start.text = "开始刷机"
        status_text.value = "刷机完成！" if success else "刷机失败！请查看日志。"
        status_text.color = ft.Colors.GREEN if success else ft.Colors.RED
        page.update()

    btn_start.on_click = start_flash

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.FLASH_ON, color=theme_color, size=24), ft.Text("一键刷机 · 系统级刷写引擎", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            status_text,
            ft.Row([btn_pick, btn_start]),
            progress_bar,
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Text("底层刷机实时日志:", color="white"),
            log_area
        ], expand=True, spacing=15, padding=20),
        expand=True
    )
'''

# 强制以 utf-8 写入，没 BOM，没空字节
with open("pages/flash.py", "w", encoding="utf-8") as f:
    f.write(flash_code)

print("✅ 编码强制重写完毕，真的刷机逻辑已成功注入！")