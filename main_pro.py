import flet as ft
import time
import flet_lottie as fl

def main(page: ft.Page):
  page.title = "HuiJui Core · Engine"
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 0
  page.window_width = 1300
  page.window_height = 850
  page.bgcolor = "#090A0F" # 更深的深邃黑

  THEME_COLOR = "#39C5BB"
  THEME_COLOR_DIM = "#1C5F5A"

  # ================= 核心组件：高级质感卡片 =================
  def create_glass_card(title, subtitle, icon_name, is_main=False):
    # 图标底托
    icon_container = ft.Container(
      content=ft.Icon(icon_name, color=THEME_COLOR if is_main else "#8892B0", size=28),
      bgcolor=ft.Colors.with_opacity(0.1, THEME_COLOR) if is_main else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
      border_radius=12,
      width=50,
      height=50,
      alignment=ft.alignment.center,
      border=ft.border.all(1, ft.Colors.with_opacity(0.2, THEME_COLOR)) if is_main else None,
    )

    def on_hover(e):
      if e.data == "true":
        e.control.bgcolor = "#1A1E2A"
        # 添加多层光晕阴影
        e.control.shadow = [
          ft.BoxShadow(spread_radius=0, blur_radius=15, color=ft.Colors.with_opacity(0.2, THEME_COLOR), offset=ft.Offset(0, 4)),
        ]
        e.control.border = ft.border.all(1, ft.Colors.with_opacity(0.6, THEME_COLOR))
      else:
        e.control.bgcolor = "#131722"
        e.control.shadow = ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2))
        e.control.border = ft.border.all(1, "#222634")
      e.control.update()

    return ft.Container(
      content=ft.Column([
        ft.Row([
          icon_container,
          ft.Container(width=15), # 间距
          ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="white"),
            ft.Text(subtitle, size=12, color="#6E7B91"),
          ], spacing=4, expand=True)
        ]),
      ]),
      bgcolor="#131722",
      border_radius=16,
      padding=20,
      border=ft.border.all(1, "#222634"),
      shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
      on_hover=on_hover,
      animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
      expand=True, # 占满网格
    )

  # ================= 页面布局 =================
  
  # 右侧：Lottie 动画与状态
  side_panel = ft.Container(
    width=300,
    bgcolor="#0D1017",
    border=ft.border.only(left=ft.border.BorderSide(1, "#1C202D")),
    padding=30,
    content=ft.Column([
      ft.Text("SYSTEM STATUS", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
      ft.Container(height=10),
      ft.Container(
        content=ft.Row([
          ft.Container(width=8, height=8, bgcolor="#3FBF6E", border_radius=4),
          ft.Text(" 设备已连接 / ROOT 正常", size=13, color="#A0ABC0"),
        ]),
        padding=15,
        bgcolor="#151A26",
        border_radius=10,
        border=ft.border.all(1, "#1F2636"),
      ),
      ft.Container(height=30),
      ft.Text("ENGINE VISUALS", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
      fl.Lottie(
        src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json",
        width=240,
        height=240,
        animate=True
      ),
    ])
  )

  # 左侧主面板
  main_content = ft.Container(
    expand=True,
    padding=40,
    content=ft.Column([
      # 欢迎标题
      ft.Text("Matrix Dashboard", size=38, weight=ft.FontWeight.BOLD, color="white"),
      ft.Text("原生 GPU 渲染引擎 · 从此告别卡顿", size=14, color=THEME_COLOR, weight=ft.FontWeight.W_600),
      ft.Container(height=40),
      
      # 核心功能网格
      ft.Text("QUICK ACTIONS", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
      ft.Container(height=15),
      
      # 第一排
      ft.Row([
        create_glass_card("设备连接", "扫描 ADB / Fastboot", ft.Icons.PHONE_ANDROID, is_main=True),
        create_glass_card("一键刷机", "自动解包并刷入", ft.Icons.ELECTRIC_BOLT, is_main=True),
      ], spacing=20),
      ft.Container(height=20),
      
      # 第二排
      ft.Row([
        create_glass_card("模块仓库", "797 个纯净模块", ft.Icons.EXTENSION),
        create_glass_card("分区备份", "防变砖救援", ft.Icons.SAVE_ALT),
      ], spacing=20),
      ft.Container(height=20),
      
      # 第三排
      ft.Row([
        create_glass_card("高级终端", "实时 Shell 执行", ft.Icons.TERMINAL),
        create_glass_card("历史记录", "刷机与操作日志", ft.Icons.HISTORY),
      ], spacing=20),
    ], scroll=ft.ScrollMode.ADAPTIVE)
  )

  # ================= 侧边栏 =================
  nav_rail = ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=90,
    bgcolor="#0D1017",
    indicator_color=ft.Colors.with_opacity(0.15, THEME_COLOR),
    indicator_shape=ft.RoundedRectangleBorder(radius=10),
    selected_label_text_style=ft.TextStyle(color=THEME_COLOR, weight=ft.FontWeight.BOLD, size=12),
    unselected_label_text_style=ft.TextStyle(color="#4B5568", size=12),
    destinations=[
      ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="控制台"),
      ft.NavigationRailDestination(icon=ft.Icons.BUILD_OUTLINED, selected_icon=ft.Icons.BUILD, label="工具箱"),
      ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="历史"),
    ]
  )

  # 顶层布局
  page.add(
    ft.Row([
      nav_rail,
      ft.VerticalDivider(width=1, color="#1C202D"),
      main_content,
      side_panel
    ], expand=True)
  )

if __name__ == "__main__":
  ft.app(target=main)
