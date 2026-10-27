import flet as ft
import subprocess
import os
import threading
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

QFIL_PATH = os.path.join(BIN_DIR, "QFIL", "QFIL.exe")
SPFLASH_PATH = os.path.join(BIN_DIR, "SPFlashTool", "flash_tool.exe")
MTKCLIENT_PATH = os.path.join(BIN_DIR, "MTKClient", "mtk_gui.bat")

def build_rescue_page(page: ft.Page, theme_color):
  log_area = ft.TextField(
    multiline=True, read_only=True, expand=True, 
    bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF"), color=getattr(page, "ui_style", {}).get("log_color", "#00FFD1"), 
    text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
    border=ft.InputBorder.NONE,
  )
  log_container = ft.Container(
    content=log_area, bgcolor=getattr(page, "ui_style", {}).get("log_bg", "#05070A"), border_radius=12,
    padding=15, expand=True,
    border=page.ui_style["card_border"]
  )
  
  status_text = ft.Text("等待选择救砖方案...", size=13, color=theme_color, weight=ft.FontWeight.BOLD)

  def log(msg):
    log_area.value += msg + "\n"
    page.update()

  # ================= 1. 高通 XML 解析 =================
  def parse_xml(xml_path):
    try:
      tree = ET.parse(xml_path)
      root = tree.getroot()
      programs = root.findall('program')
      log(f"✅ 成功解析高通 XML，包含 {len(programs)} 个刷写分区指令。")
      for p in programs[:3]:
        log(f" - 分区: {p.get('label')}, 镜像: {p.get('filename')}")
      if len(programs) > 3: log(f" ... 等共 {len(programs)} 个指令")
      return True
    except Exception as e:
      log(f"❌ 解析失败: {e}")
      return False

  # ================= 2. MTK Scatter 解析 =================
  def parse_scatter(txt_path):
    try:
      with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
      count = 0
      for line in lines:
        if line.startswith('partition_name'):
          count += 1
          if count <= 3:
            parts = line.split()
            log(f" - 分区: {parts[1]}, 镜像: {parts[3]}")
      log(f"✅ 成功解析 Scatter 文件，包含 {count} 个刷写分区。")
      return True
    except Exception as e:
      log(f"❌ 解析失败: {e}")
      return False

  # ================= 3. 文件选择与执行 =================
  file_picker = ft.FilePicker()
  page.overlay.append(file_picker)
  page.update()

  def on_file_selected(e: ft.FilePickerResultEvent):
    if not e.files:
      return
    
    path = e.files[0].path
    ext = os.path.splitext(path)[1].lower()
    log(f"\n> 已选择脚本: {os.path.basename(path)}")
    page.update()

    if ext == '.xml':
      log("> 检测到高通线刷包 XML 脚本")
      if parse_xml(path):
        log("\n💡 正在尝试调用 QFIL...")
        if os.path.exists(QFIL_PATH):
          subprocess.Popen([QFIL_PATH], cwd=os.path.dirname(QFIL_PATH), shell=True)
          log("✅ QFIL 已启动！")
        else:
          log("⚠️ 未找到 QFIL，请放入 bin/QFIL 目录。")
    elif ext == '.txt':
      log("> 检测到联发科 Scatter 文件")
      if parse_scatter(path):
        log("\n💡 正在尝试调用 SP Flash Tool...")
        if os.path.exists(SPFLASH_PATH):
          subprocess.Popen([SPFLASH_PATH], cwd=os.path.dirname(SPFLASH_PATH), shell=True)
          log("✅ SP Flash Tool 已启动！")
        else:
          log("⚠️ 未找到工具，请放入 bin/SPFlashTool 目录。")
    else:
      log("❌ 不支持的格式！")

    status_text.value = "脚本解析完成"
    status_text.color = ft.Colors.GREEN
    page.update()

  file_picker.on_result = on_file_selected

  def pick_script(e):
    file_picker.pick_files(allowed_types=[ft.FilePickerFileType.CUSTOM], allowed_extensions=["xml", "txt"])

  # 启动 MTKClient GUI
  def launch_mtkclient(e):
    if os.path.exists(MTKCLIENT_PATH):
      log("> 正在启动 MTKClient GUI...")
      subprocess.Popen([MTKCLIENT_PATH], cwd=os.path.dirname(MTKCLIENT_PATH), shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
      log("❌ 未找到 MTKClient，请先配置环境！")
    page.update()

  # ================= UI 组装 =================
  return ft.Container(
    content=ft.Column([
      ft.Row([
        ft.Icon(ft.Icons.HEALTH_AND_SAFETY, color=theme_color, size=28),
        ft.Text("急救中心 · 底层救砖", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
        ft.Container(expand=True),
        status_text
      ]),
      ft.Container(height=5),
      
      # 方案 A：高通 / MTK 脚本解析刷写
      ft.Container(
        content=ft.Row([
          ft.Column([
            ft.Text("方案 A：高通 9008 / MTK BROM 线刷", size=16, weight=ft.FontWeight.BOLD, color=theme_color),
            ft.Text("选择 rawprogram.xml 或 scatter.txt，自动解析并拉起 QFIL / SP Flash Tool。", size=12, color=ft.Colors.GREY_400)
          ], expand=True),
          ft.ElevatedButton(
            "选择脚本并执行", icon=ft.Icons.FOLDER_OPEN, 
            on_click=pick_script,
            style=ft.ButtonStyle(
    color=theme_color, 
    bgcolor=ft.Colors.with_opacity(0.2, theme_color), 
    side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, theme_color)), 
    shape=ft.RoundedRectangleBorder(radius=10), 
    padding=ft.padding.symmetric(horizontal=20, vertical=12), 
    elevation=0
  )
          )
        ]),
        bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
        border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
        border_radius=15, padding=20
      ),
      
      # 方案 B：MTKClient
      ft.Container(
        content=ft.Row([
          ft.Column([
            ft.Text("方案 B：MTK 专用救砖工具 (MTKClient)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
            ft.Text("适用于联发科机型，支持 BROM 强解、读取/写入分区等底层操作。", size=12, color=ft.Colors.GREY_400)
          ], expand=True),
          ft.ElevatedButton(
            "启动 MTKClient", icon=ft.Icons.BUILD_CIRCLE, 
            on_click=launch_mtkclient,
            style=ft.ButtonStyle(
    color=ft.Colors.ORANGE_300, 
    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_500), 
    side=ft.BorderSide(1.5, ft.Colors.with_opacity(0.6, ft.Colors.ORANGE_500)), 
    shape=ft.RoundedRectangleBorder(radius=10), 
    padding=ft.padding.symmetric(horizontal=20, vertical=12), 
    elevation=0
  )
          )
        ]),
        bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
        border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
        border_radius=15, padding=20
      ),
      
      # 操作指南
      ft.Container(
        content=ft.Column([
          ft.Text("⚠️ 操作前必读指南", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
          ft.Text("1. 请确保已安装对应芯片的底层驱动（高通 QDLoader / MTK VCOM）。", size=12, color="white"),
          ft.Text("2. 手机需完全关机，按特定组合键（或短接）进入 9008 / BROM 模式。", size=12, color="white"),
          ft.Text("3. 插入数据线，电脑识别到端口后，再点击上方按钮启动工具。", size=12, color="white"),
        ]),
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), 
        border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), 
        border_radius=15, padding=20
      ),
      
      ft.Container(height=10),
      ft.Text("解析与底层操作日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
      log_container
    ], expand=True), 
    expand=True, 
    padding=20
  )
