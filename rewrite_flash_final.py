# rewrite_flash_final.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
flash_path = os.path.join(BASE_DIR, "pages", "flash.py")

flash_code = '''import flet as ft
import threading
import subprocess
import os
import time
import re
import zipfile
import shutil

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
  status_text = ft.Text("等待导入官方卡刷包 (.zip)", size=13, weight=ft.FontWeight.W_600, color=theme_color, font_family="MiSans")
  
  progress_bar = ft.ProgressBar(value=0, color=theme_color, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=4, border_radius=2)
  
  log_area = ft.TextField(
    multiline=True, read_only=True, expand=True, 
    bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
    text_size=13, text_style=ft.TextStyle(font_family="Consolas"),
    border=ft.InputBorder.NONE,
  )
  log_container = ft.Container(
    content=log_area, 
    bgcolor=page.ui_style.get("log_bg", ft.Colors.with_opacity(0.2, "#000000")), 
    border_radius=12, padding=15, expand=True, 
    border=page.ui_style.get("card_border", ft.border.all(1, theme_color))
  )
  
  file_picker = ft.FilePicker()
  page.overlay.append(file_picker)
  page.update()
  
  state = {"zip_path": None, "extract_dir": None, "is_running": False}

  drop_icon = ft.Icon(ft.Icons.CLOUD_UPLOAD_OUTLINED, size=54, color=theme_color)
  drop_title = ft.Text("点击这里导入刷机包", size=20, weight=ft.FontWeight.W_700, color="#FFFFFF", font_family="MiSans")
  drop_subtitle = ft.Text("支持官方 .zip 卡刷包 / payload 解析", size=13, weight=ft.FontWeight.W_500, color="#A0ABC0", font_family="MiSans")
  
  drop_zone = ft.Container(
    content=ft.Column([drop_icon, drop_title, drop_subtitle], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
    bgcolor=ft.Colors.with_opacity(0.08, theme_color),
    border=ft.border.all(2, ft.Colors.with_opacity(0.5, theme_color)),
    border_radius=16, padding=30, height=180, alignment=ft.alignment.center,
    on_click=lambda _: file_picker.pick_files(allowed_extensions=["zip"]) if not state["is_running"] else None
  )

  btn_start = ft.ElevatedButton(
    "开始刷机", 
    icon=ft.Icons.FLASH_ON, 
    disabled=True,
    style=ft.ButtonStyle(
      color=theme_color, 
      bgcolor=ft.Colors.with_opacity(0.2, theme_color), 
      side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, theme_color)), 
      shape=ft.RoundedRectangleBorder(radius=10), 
      padding=ft.padding.symmetric(horizontal=40, vertical=18), 
      elevation=0
    )
  )

  def log(msg):
    log_area.value += msg + "\\n"
    page.update()

  def on_pick(e: ft.FilePickerResultEvent):
    if e.files:
      state["zip_path"] = e.files[0].path
      status_text.value = f"已加载: {os.path.basename(state['zip_path'])}"
      drop_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
      drop_title.value = "刷机包已就绪"
      drop_title.color = theme_color
      drop_subtitle.value = "点击可重新选择"
      btn_start.disabled = False
      log(f"> 已加载包: {state['zip_path']}")
      page.update()

  file_picker.on_result = on_pick

  def run_cmd(cmd, cwd=None, on_line=None, timeout=1800):
    log(f"> {cmd}")
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    try:
      proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace', cwd=cwd, creationflags=creationflags
      )
      start_time = time.time()
      for line in iter(proc.stdout.readline, ''):
        if line:
          line = line.strip()
          if on_line: on_line(line)
          else: log(line)
        if time.time() - start_time > timeout:
          proc.kill()
          log("❌ 执行超时，已强制终止。")
          break
      proc.stdout.close()
      proc.wait()
      return proc.returncode
    except Exception as ex:
      log(f"❌ 执行异常: {ex}")
      return -1

  def flash_flow():
    try:
      progress_bar.value = 0.02
      log_area.value = ""
      log("\\n[1/7] 正在提取 payload.bin...")
      payload_path = os.path.join(BASE_DIR, "payload.bin")
      if os.path.exists(payload_path): os.remove(payload_path)

      with zipfile.ZipFile(state["zip_path"], 'r') as z:
        if "payload.bin" not in z.namelist():
          log("❌ 卡刷包内未找到 payload.bin！请确认是官方包。")
          finish(False); return
        z.extract("payload.bin", BASE_DIR)

      progress_bar.value = 0.10
      page.update()
      log("\\n[2/7] 正在清理旧的解包目录...")
      for d in os.listdir(BASE_DIR):
        if d.startswith("extracted_"):
          try: shutil.rmtree(os.path.join(BASE_DIR, d))
          except Exception as e: log(f"⚠️ 清理 {d} 失败: {e}")

      log("\\n[3/7] 正在解包镜像 (payload-dumper-go)...")
      prog_re = re.compile(r"\\[(\\d+)/(\\d+)\\]")
      def on_dump_line(line):
        m = prog_re.search(line)
        if m:
          d, t = int(m.group(1)), int(m.group(2))
          progress_bar.value = 0.10 + 0.30 * (d / max(t, 1))
          page.update()
        log(line)

      cmd = f'"{DUMPER_PATH}" -q -p {PAYLOAD_PARTS} payload.bin'
      run_cmd(cmd, cwd=BASE_DIR, on_line=on_dump_line)

      for d in sorted(os.listdir(BASE_DIR), reverse=True):
        if d.startswith("extracted_"):
          state["extract_dir"] = os.path.join(BASE_DIR, d)
          break
      
      if not state["extract_dir"]:
        log("❌ 解包失败，找不到镜像目录！"); finish(False); return

      progress_bar.value = 0.40
      page.update()
      log("\\n[4/7] 检测设备与 Fastboot 状态...")
      fb_out = run_cmd(f'"{FB_PATH}" devices')
      
      if not fb_out or "fastboot" not in fb_out.lower():
        log("⚠️ 未检测到 Fastboot 设备，尝试从 ADB 重启...")
        run_cmd(f'"{ADB_PATH}" reboot bootloader')
        log("> 等待设备进入 Fastboot 模式 (最多 30 秒)...")
        time.sleep(5)
        for i in range(25):
          fb_out = run_cmd(f'"{FB_PATH}" devices')
          if fb_out and "fastboot" in fb_out.lower(): break
          time.sleep(1)
        else:
          log("❌ 等待超时，请手动将手机进入 Bootloader 模式！")
          finish(False); return
      
      progress_bar.value = 0.50
      page.update()
      log("\\n[5/7] 开始刷入物理分区...")
      for name, filename, args in PHYSICAL:
        file_path = os.path.join(state["extract_dir"], filename)
        if os.path.exists(file_path):
          run_cmd(f'"{FB_PATH}" {args} flash {name} "{file_path}"')
          progress_bar.value += 0.03
          page.update()
      
      log("\\n[6/7] 切换到 Fastbootd 并刷入逻辑分区...")
      run_cmd(f'"{FB_PATH}" reboot fastboot')
      time.sleep(3)
      for name, filename in LOGICAL:
        file_path = os.path.join(state["extract_dir"], filename)
        if os.path.exists(file_path):
          run_cmd(f'"{FB_PATH}" flash {name} "{file_path}"')
          progress_bar.value += 0.02
          page.update()
      
      progress_bar.value = 0.98
      page.update()
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
    btn_start.disabled = True
    btn_start.text = "刷机中..."
    drop_zone.on_click = None
    progress_bar.value = 0
    log_area.value = ""
    page.update()
    threading.Thread(target=flash_flow, daemon=True).start()

  def finish(success):
    state["is_running"] = False
    btn_start.disabled = False
    btn_start.text = "开始刷机"
    drop_zone.on_click = lambda _: file_picker.pick_files(allowed_extensions=["zip"])
    status_text.value = "刷机完成！" if success else "刷机失败！"
    status_text.color = ft.Colors.GREEN if success else ft.Colors.RED
    page.update()

  btn_start.on_click = start_flash

  return ft.Container(
    content=ft.Column([
      ft.Row([ft.Icon(ft.Icons.FLASH_ON, color=theme_color, size=28), ft.Text("一键刷机 · 系统级刷写引擎", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="MiSans")]),
      ft.Container(height=10),
      ft.Container(
        content=ft.Column([
          status_text,
          ft.Container(height=5),
          drop_zone,
          ft.Container(height=10),
          ft.Row([btn_start], alignment=ft.MainAxisAlignment.CENTER),
          ft.Container(height=5),
          progress_bar
        ]),
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        border_radius=15, padding=20
      ),
      ft.Container(height=10),
      ft.Text("实时底层日志 (Fastboot)", size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, font_family="MiSans"),
      log_container
    ], expand=True),
    expand=True, padding=20
  )
'''

with open(flash_path, "w", encoding="utf-8") as f:
  f.write(flash_code)

print("✅ pages/flash.py 已全量重写！真刷机逻辑保留，按钮已玻璃化！")