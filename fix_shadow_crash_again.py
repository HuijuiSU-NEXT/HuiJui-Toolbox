# fix_shadow_crash_again.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dashboard_path = os.path.join(BASE_DIR, "pages", "dashboard.py")

dashboard_code = '''import flet as ft

def build_dashboard(page: ft.Page, theme_color, scan_device, switch_tab, goto_sub_page):
  cards_data = [
    {"title": "一键刷机", "subtitle": "全自动向导页面", "icon": ft.Icons.BOLT, "route": "flash"},
    {"title": "扫描设备", "subtitle": "读取手机状态与 Root", "icon": ft.Icons.PHONE_ANDROID, "route": "scan"},
    {"title": "临时 Root", "subtitle": "KMI 无痕注入", "icon": ft.Icons.SECURITY, "route": "temp_root"},
    {"title": "模块仓库", "subtitle": "797 个纯净模块", "icon": ft.Icons.EXTENSION, "route": "module_repo"},
    {"title": "高级终端", "subtitle": "实时 Shell 执行", "icon": ft.Icons.TERMINAL, "route": "terminal"},
    {"title": "Scrcpy 投屏", "subtitle": "USB / 无线投屏", "icon": ft.Icons.MONITOR, "route": "scrcpy"},
    {"title": "分区刷入", "subtitle": "救砖/单刷指南", "icon": ft.Icons.BUILD_CIRCLE, "route": "flash_parts"},
    {"title": "分区备份", "subtitle": "保护 boot / init_boot", "icon": ft.Icons.SAVE, "route": "backup"},
    {"title": "无线调试", "subtitle": "TCPIP 与 IP 自动获取", "icon": ft.Icons.WIFI, "route": "wireless_adb"},
    {"title": "模式切换", "subtitle": "Fastboot / Fastbootd", "icon": ft.Icons.SWAP_HORIZ, "route": "mode_switch"},
    {"title": "驱动环境", "subtitle": "一键安装底层驱动", "icon": ft.Icons.BUILD, "route": "drivers"},
    {"title": "急救中心", "subtitle": "9008 / BROM 救砖", "icon": ft.Icons.HEALTH_AND_SAFETY, "route": "rescue"},
  ]

  def handle_card_click(route):
    if route == "flash":
      switch_tab(1)
    elif route == "scan":
      scan_device()
    elif route == "temp_root":
      switch_tab(2)
    else:
      goto_sub_page(route)

  grid = ft.GridView(
    expand=1,
    runs_count=3,
    max_extent=250,
    child_aspect_ratio=2.5,
    spacing=15,
    run_spacing=15,
  )

  for card in cards_data:
    card_container = ft.Container(
      content=ft.Column([
        ft.Row([
          ft.Icon(card["icon"], color=theme_color, size=20),
          # 彻底移除 shadow，保持纯白加粗
          ft.Text(card["title"], weight=ft.FontWeight.W_700, size=14, color="#FFFFFF", font_family="MiSans")
        ]),
        # 彻底移除 shadow
        ft.Text(card["subtitle"], size=12, color=ft.Colors.WHITE70, font_family="MiSans")
      ], alignment=ft.MainAxisAlignment.CENTER),
      # 🚨 核心：给卡片垫上一层淡淡的黑色，保证文字清晰，同时没有违和感
      bgcolor=ft.Colors.with_opacity(0.2, "#000000"),
      border=ft.border.all(1, ft.Colors.with_opacity(0.25, ft.Colors.WHITE)),
      border_radius=12,
      padding=15,
      on_click=lambda e, r=card["route"]: handle_card_click(r)
    )
    grid.controls.append(card_container)

  return ft.Container(
    content=ft.Column([
      ft.Text("HuiJui Toolbox Edition", size=30, weight=ft.FontWeight.W_900, color="#FFFFFF", font_family="MiSans"),
      ft.Text("Matrix Engine · 原生 GPU 渲染", size=13, color="#FFFFFF", weight=ft.FontWeight.W_600, font_family="MiSans"),
      ft.Container(height=20),
      grid
    ]),
    expand=True,
    padding=20
  )
'''

with open(dashboard_path, "w", encoding="utf-8") as f:
  f.write(dashboard_code)

print("✅ dashboard.py 已重写：非法 shadow 参数已彻底物理清除！")
print("✅ 卡片背景已调整为 0.2 透明度的黑玻璃，既透亮又保证白字极其清晰！")