# ui_dialogs.py
import os
import threading
import subprocess
import ctypes
import flet as ft
import urllib.request, json
from core_api import runner, flasher, backup_mgr, ADB, BIN_DIR, is_admin, install_driver, SCRCPY, get_active_serial
from core.adb_core import reboot_to_bootloader, reboot_to_recovery, reboot_to_edl, reboot_from_fastboot_to_fastbootd, reboot_from_fastboot_to_recovery
import ui_theme

def show_backup(page, theme_color):
  log_box = ft.ListView(expand=True, spacing=4, padding=10)
  boot_switch = ft.Switch(label="boot 分区", value=True, active_color=theme_color)
  initboot_switch = ft.Switch(label="init_boot 分区", value=True, active_color=theme_color)
  start_btn = ft.ElevatedButton("开始备份", style=ui_theme.get_button_style(theme_color), width=180)
  def add_log(msg, color="white"):
    log_box.controls.append(ft.Text(msg, size=12, color=color, font_family="Consolas")); page.update()
  def do_backup(_):
    start_btn.disabled = True
    def worker():
      dev = get_active_serial()
      if not dev: add_log("❌ 未检测到设备", "#E05070"); return
      bdir = backup_mgr.create_backup_dir()
      targets = []
      if boot_switch.value: targets.append("boot")
      if initboot_switch.value: targets.append("init_boot")
      for part in targets:
        backup_mgr.backup_partition(dev, part, bdir, lambda m: add_log(m, "white"))
      start_btn.disabled = False; page.update()
    threading.Thread(target=worker, daemon=True).start()
  start_btn.on_click = do_backup
  dlg = ft.AlertDialog(title=ft.Text("分区备份"), content=ft.Container(content=ft.Column([
    ft.Row([boot_switch, initboot_switch]), ft.Container(height=6), ft.Row([start_btn]), ft.Container(height=6),
    ft.Container(content=log_box, bgcolor="#090A0F", border_radius=8, border=ft.border.all(1, "#222634"), expand=True)
  ], expand=True), width=600, height=400), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()

def show_wireless(page, theme_color):
  ip_field = ft.TextField(label="设备 IP:端口", hint_text="192.168.1.100:5555", width=280, text_size=13, color="white")
  info_lbl = ft.Text("第一步：USB 连接后点击『开启 TCPIP』", size=12, color="#8892B0")
  def do_tcpip(_):
    def worker():
      info_lbl.value = "⏳ 正在开启 TCPIP..."; page.update()
      dev = get_active_serial()
      if not dev: info_lbl.value = "❌ 未检测到 USB 设备"; info_lbl.color = "#E05070"; page.update(); return
      runner.run_quiet(f'"{ADB}" -s {dev} tcpip 5555')
      routes = runner.run_quiet(f'"{ADB}" -s {dev} shell ip route')
      import re
      m = re.search(r"src (\d+\.\d+\.\d+\.\d+)", routes)
      if m:
        ip_field.value = f"{m.group(1)}:5555"
        info_lbl.value = "✅ TCPIP 已开启！拔线后点击连接"; info_lbl.color = "#3FBF6E"
      else: info_lbl.value = "✅ 已开启，但未获取到 IP"; info_lbl.color = "#F0A030"
      page.update()
    threading.Thread(target=worker, daemon=True).start()
  def do_connect(_):
    target = (ip_field.value or "").strip()
    if ":" not in target: return
    def worker():
      out = runner.run_quiet(f'"{ADB}" connect {target}')
      info_lbl.value = f"{'✅' if 'connected' in out.lower() else '❌'} {out.strip()[:80]}"
      info_lbl.color = "#3FBF6E" if "connected" in out.lower() else "#E05070"
      page.update()
    threading.Thread(target=worker, daemon=True).start()
  dlg = ft.AlertDialog(title=ft.Text("📶 无线调试"), content=ft.Container(content=ft.Column([
    info_lbl, ft.Container(height=10),
    ft.Row([ft.ElevatedButton("① 开启 TCPIP", on_click=do_tcpip, style=ui_theme.get_button_style_dark(), height=36)]),
    ft.Container(height=10),
    ft.Row([ip_field, ft.ElevatedButton("② 连接", on_click=do_connect, style=ui_theme.get_button_style(theme_color), height=40)], spacing=8),
  ], tight=True), width=460), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()

def show_terminal(page, theme_color):
  log_box = ft.ListView(expand=True, spacing=2, padding=10, auto_scroll=True)
  input_field = ft.TextField(hint_text="输入命令，如 getprop", height=40, text_size=13, border_color="#222634", bgcolor="#0D1017", color="white", expand=True)
  def add_log(text, color="#3FBF6E"):
    log_box.controls.append(ft.Text(text, size=12, color=color, font_family="Consolas")); page.update()
  def run_cmd(_):
    cmd = (input_field.value or "").strip()
    if not cmd: return
    input_field.value = ""; add_log(f"$ {cmd}", "#8892B0"); page.update()
    def worker():
      dev = get_active_serial()
      if not dev: add_log("❌ 无设备", "#E05070"); return
      out = runner.run_quiet(f'"{ADB}" -s {dev} shell "{cmd}"')
      if out: [add_log(line) for line in out.splitlines()]
      else: add_log("(无输出)", "#4B5568")
    threading.Thread(target=worker, daemon=True).start()
  input_field.on_submit = run_cmd
  dlg = ft.AlertDialog(title=ft.Text("💻 高级终端"), content=ft.Container(content=ft.Column([
    ft.Container(content=log_box, bgcolor="#090A0F", border=ft.border.all(1, "#222634"), border_radius=8, expand=True),
    ft.Container(height=8),
    ft.Row([input_field, ft.ElevatedButton("发送", on_click=run_cmd, style=ui_theme.get_button_style(theme_color), height=40)])
  ], expand=True), width=700, height=450), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update(); add_log("欢迎使用 HuiJui Core 高级终端。", theme_color)

def show_reboot(page, theme_color):
  def do_action(mode_name, cmd_func):
    def worker():
      dev = get_active_serial()
      if not dev and mode_name != "Fastbootd":
        page.snack_bar = ft.SnackBar(ft.Text("❌ 需 ADB 连接设备"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True; page.update(); return
      try:
        if mode_name in ["Fastbootd", "Recovery (FB)"]: cmd_func()
        else: cmd_func(dev)
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ 已发送重启指令: {mode_name}"), bgcolor=ft.Colors.GREEN_400)
        page.snack_bar.open = True; page.update()
      except Exception as ex:
        page.snack_bar = ft.SnackBar(ft.Text(f"❌ 执行失败: {ex}"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True; page.update()
    threading.Thread(target=worker, daemon=True).start()
  dlg = ft.AlertDialog(title=ft.Text("🔄 模式切换 / 高级重启"), content=ft.Container(content=ft.Column([
    ft.Text("请根据当前设备所处的状态选择操作：", size=12, color="#6E7B91"), ft.Divider(color="#222634", height=20),
    ft.Text("▸ 正常开机状态 (ADB)", size=13, weight=ft.FontWeight.BOLD, color="white"),
    ft.Row([
      ft.ElevatedButton("Fastboot", on_click=lambda _: do_action("Fastboot", reboot_to_bootloader), style=ui_theme.get_button_style_dark()),
      ft.ElevatedButton("Recovery", on_click=lambda _: do_action("Recovery", reboot_to_recovery), style=ui_theme.get_button_style_dark()),
      ft.ElevatedButton("EDL 9008", on_click=lambda _: do_action("EDL", reboot_to_edl), bgcolor="#E05070", color="white"),
    ], spacing=10),
    ft.Divider(color="#222634", height=20),
    ft.Text("▸ Fastboot 状态", size=13, weight=ft.FontWeight.BOLD, color="white"),
    ft.Row([
      ft.ElevatedButton("Fastbootd", on_click=lambda _: do_action("Fastbootd", reboot_from_fastboot_to_fastbootd), bgcolor="#A070E0", color="white"),
      ft.ElevatedButton("Recovery", on_click=lambda _: do_action("Recovery (FB)", reboot_from_fastboot_to_recovery), style=ui_theme.get_button_style_dark()),
    ], spacing=10)
  ], tight=True), width=550), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()

def show_drivers(page, theme_color):
  log_box = ft.ListView(expand=True, spacing=4, padding=10)
  def add_log(msg, color="white"):
    log_box.controls.append(ft.Text(msg, size=12, color=color, font_family="Consolas")); page.update()
  def run_exe_as_admin(exe_name, folder):
    exe_path = os.path.join(BIN_DIR, folder, exe_name)
    if not os.path.exists(exe_path): add_log(f"❌ 找不到文件: {exe_name}", "#E05070"); return
    try:
      ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, os.path.dirname(exe_path), 1)
      add_log(f"✅ 已拉起安装程序: {exe_name}", "#3FBF6E")
    except Exception as ex: add_log(f"❌ 启动失败: {ex}", "#E05070")
  def install_qualcomm(_):
    add_log("▸ 正在拉起高通 9008 驱动安装...", theme_color)
    run_exe_as_admin("Qualcomm_USB_Driver_Setup.exe", "Qualcomm_9008_Driver")
  def install_mtk(_):
    add_log("▸ 正在拉起 MTK VCOM 驱动安装...", theme_color)
    run_exe_as_admin("MTK_Driver_Ext.exe", "MTK_VCOM_Driver")
  def install_usb(_):
    add_log("▸ 正在安装通用 ADB 驱动...", theme_color)
    def worker():
      if not is_admin(): add_log("❌ 请以管理员身份运行", "#E05070"); return
      ok, msg = install_driver("android_winusb.inf")
      if ok: add_log("✅ 通用 ADB/Fastboot 驱动安装成功！", "#3FBF6E")
      else: add_log(f"❌ 安装失败: {msg}", "#E05070")
    threading.Thread(target=worker, daemon=True).start()
  dlg = ft.AlertDialog(title=ft.Text("🔧 驱动生态管理"), content=ft.Container(content=ft.Column([
    ft.Text("解决设备未识别、9008/EDL 无反应等问题", size=12, color="#6E7B91"), ft.Container(height=10),
    ft.Row([
      ft.ElevatedButton("高通 9008", on_click=install_qualcomm, bgcolor="#E05070", color="white"),
      ft.ElevatedButton("MTK VCOM", on_click=install_mtk, bgcolor="#F0A030", color="white"),
      ft.ElevatedButton("通用 ADB", on_click=install_usb, style=ui_theme.get_button_style(theme_color)),
    ], spacing=10), ft.Container(height=10),
    ft.Container(content=log_box, bgcolor="#090A0F", border_radius=8, border=ft.border.all(1, "#222634"), expand=True)
  ], expand=True), width=650, height=400), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()

def show_scrcpy(page, theme_color):
  def start_scrcpy(wireless=False):
    if not os.path.exists(SCRCPY):
      page.snack_bar = ft.SnackBar(ft.Text("❌ 请将 scrcpy.exe 放入 bin 目录"), bgcolor=ft.Colors.RED_400)
      page.snack_bar.open = True; page.update(); return
    def worker():
      dev = get_active_serial()
      if not dev:
        page.snack_bar = ft.SnackBar(ft.Text("❌ 需 ADB 连接设备"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True; page.update(); return
      cmd = f'"{SCRCPY}" -s {dev}'
      if wireless: cmd += " --tcpip"
      try:
        subprocess.Popen(cmd, shell=True)
        page.snack_bar = ft.SnackBar(ft.Text("✅ 正在启动 Scrcpy 投屏..."), bgcolor=ft.Colors.GREEN_400)
        page.snack_bar.open = True; page.update()
      except Exception as ex:
        page.snack_bar = ft.SnackBar(ft.Text(f"❌ 启动失败: {ex}"), bgcolor=ft.Colors.RED_400)
        page.snack_bar.open = True; page.update()
    threading.Thread(target=worker, daemon=True).start()
  dlg = ft.AlertDialog(title=ft.Text("📺 Scrcpy 投屏"), content=ft.Container(content=ft.Column([
    ft.Text("请确保 bin 目录下存在 scrcpy.exe", size=12, color="#6E7B91"), ft.Container(height=10),
    ft.Row([
      ft.ElevatedButton("USB 投屏", on_click=lambda _: start_scrcpy(False), style=ui_theme.get_button_style(theme_color)),
      ft.ElevatedButton("无线投屏 (TCPIP)", on_click=lambda _: start_scrcpy(True), style=ui_theme.get_button_style_dark()),
    ], spacing=10)
  ], tight=True), width=400), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()

def show_module_repo(page, theme_color):
  status_lbl = ft.Text("准备拉取...", size=12, color="#8892B0")
  list_view = ft.ListView(expand=True, spacing=2, padding=8)
  search_field = ft.TextField(hint_text="搜索模块...", height=38, text_size=13, border_color="#222634", bgcolor="#0D1017", color="white")
  all_modules_cache = {"data": []}
  def render_list(mods):
    list_view.controls.clear()
    for m in mods:
      list_view.controls.append(ft.ListTile(
        dense=True, leading=ft.Icon(ft.Icons.EXTENSION, color=theme_color, size=20),
        title=ft.Text(m.get("name", "未命名"), size=13, color="white"),
        subtitle=ft.Text(m.get("description", "")[:50], size=11, color="#6E7B91") if m.get("description") else None
      ))
    page.update()
  def on_search(e):
    kw = (search_field.value or "").lower().strip()
    if not kw: render_list(all_modules_cache["data"])
    else: render_list([m for m in all_modules_cache["data"] if kw in (m.get("name","")+m.get("description","")).lower()])
  search_field.on_change = on_search
  def do_fetch():
    try:
      url = "https://hhcdxii-ship-it.github.io/Huijui_Module_Repo/modules.json"
      req = urllib.request.Request(url, headers={"User-Agent": "HuiJui"})
      with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
      modules = data if isinstance(data, list) else data.get("modules", [])
      all_modules_cache["data"] = modules
      render_list(modules)
      status_lbl.value = f"✅ 加载成功 · 共 {len(modules)} 个"
      status_lbl.color = "#3FBF6E"; page.update()
    except Exception as ex:
      status_lbl.value = f"💥 失败: {ex}"; status_lbl.color = "#E05070"; page.update()
  dlg = ft.AlertDialog(title=ft.Text("📦 模块仓库"), content=ft.Container(content=ft.Column([
    search_field, ft.Container(height=6), status_lbl, ft.Container(height=4),
    ft.Container(content=list_view, bgcolor="#090A0F", border_radius=8, border=ft.border.all(1, "#222634"), expand=True),
  ], expand=True), width=600, height=450), actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())])
  page.dialog = dlg; dlg.open = True; page.update()
  threading.Thread(target=do_fetch, daemon=True).start()

def show_rescue_center(page, theme_color):
  from core.device_mode import get_device_state
  state = get_device_state()
  is_edl = state == "EDL"
  is_brom = state == "BROM"
  
  log_box = ft.ListView(expand=True, spacing=4, padding=10)
  
  def add_log(msg, color="white"):
    log_box.controls.append(ft.Text(msg, size=12, color=color, font_family="Consolas")); page.update()

  def launch_driver(folder, exe_name, name):
    exe_path = os.path.join(BIN_DIR, folder, exe_name)
    if not os.path.exists(exe_path):
      add_log(f"❌ 找不到 {name} 驱动文件", "#E05070"); return
    try:
      ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, os.path.dirname(exe_path), 1)
      add_log(f"✅ 已拉起 {name} 驱动安装程序，请在弹出的窗口完成安装", "#3FBF6E")
    except Exception as ex:
      add_log(f"❌ 启动失败: {ex}", "#E05070")

  btn_qcom = ft.ElevatedButton(
    "安装 高通 9008 驱动", 
    on_click=lambda _: launch_driver("Qualcomm_9008_Driver", "Qualcomm_USB_Driver_Setup.exe", "高通 9008"), 
    bgcolor="#E05070" if is_edl else "#1C202D", color="white", width=200
  )
  btn_mtk = ft.ElevatedButton(
    "安装 MTK VCOM 驱动", 
    on_click=lambda _: launch_driver("MTK_VCOM_Driver", "MTK_Driver_Ext.exe", "MTK VCOM"), 
    bgcolor="#F0A030" if is_brom else "#1C202D", color="white", width=200
  )

  guide_text = ft.Text(
    "等待检测设备状态... (请插入变砖的手机)" if not (is_edl or is_brom) else (
      "🚨 检测到高通 9008 (EDL) 模式！\n请点击上方安装驱动，随后使用 QFIL 救砖工具。" if is_edl else
      "🚨 检测到联发科 BROM 模式！\n请点击上方安装驱动，随后使用 SP Flash Tool 救砖。"
    ),
    size=13, color="#E05070" if (is_edl or is_brom) else "#8892B0",
    weight=ft.FontWeight.BOLD
  )

  dlg = ft.AlertDialog(
    title=ft.Row([
      ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color="#E05070", size=28),
      ft.Text("🚨 全自动急救中心", color="#E05070", weight=ft.FontWeight.BOLD)
    ]),
    content=ft.Container(content=ft.Column([
      guide_text, ft.Container(height=10),
      ft.Row([btn_qcom, btn_mtk], spacing=10),
      ft.Divider(color="#222634", height=20),
      ft.Text("底层日志输出：", size=12, color="#4B5568"),
      ft.Container(content=log_box, bgcolor="#090A0F", border=ft.border.all(1, "#222634"), border_radius=8, height=150, expand=True),
      ft.Container(height=10),
      ft.Text("💡 变砖黑屏不要慌：请长按电源键 10 秒以上强制重启，或尝试进入 Fastboot/Recovery。", size=11, color="#6E7B91")
    ], tight=True), width=500),
    actions=[ft.TextButton("关闭", on_click=lambda _: setattr(dlg, 'open', False) or page.update())],
  )
  page.dialog = dlg; dlg.open = True; page.update()