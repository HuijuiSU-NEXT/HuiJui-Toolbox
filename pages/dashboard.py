import flet as ft

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
          # 使用纯白 + 极高字重，抵御复杂背景
          ft.Text(card["title"], weight=ft.FontWeight.W_900, size=14, color="#FFFFFF", font_family="MiSans")
        ]),
        # 副标题略微提亮并加粗
        ft.Text(card["subtitle"], size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, font_family="MiSans")
      ], alignment=ft.MainAxisAlignment.CENTER),
      # 从 page.ui_style 动态读取背景和边框
      bgcolor=None if isinstance(page.ui_style["card_bg"], ft.LinearGradient) else page.ui_style["card_bg"],
      gradient=page.ui_style["card_bg"] if isinstance(page.ui_style["card_bg"], ft.LinearGradient) else None,
      border=page.ui_style["card_border"],
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
