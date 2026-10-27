# main_apk.py - Android 原生重构版
import flet as ft
import platform

def main(page: ft.Page):
  page.title = "HuiJui Toolbox Edition"
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = "#090A0F"
  page.padding = 20
  
  theme_color = "#39C5BB"
  log_area = ft.TextField(
    multiline=True, read_only=True, expand=True,
    bgcolor=ft.Colors.with_opacity(0.1, "#FFFFFF"), color="#00FFD1",
    text_size=13, text_style=ft.TextStyle(font_family="Consolas"),
    border=ft.InputBorder.NONE, border_radius=12,
  )

  def test_click(e):
    log_area.value += f"> {e.control.data} 被点击！\n"
    log_area.value += "> 注意：当前为 Android 端，底层 .exe 刷机指令已重构隔离。\n"
    page.update()

  def make_card(title, icon, desc, disabled=False):
    return ft.Container(
      content=ft.Row([
        ft.Icon(icon, color=theme_color if not disabled else "#555555", size=28),
        ft.Column([
          ft.Text(title, weight=ft.FontWeight.BOLD, color="white" if not disabled else "#888888", size=16),
          ft.Text(desc, color="#A0ABC0" if not disabled else "#555555", size=12),
        ], spacing=2, expand=True)
      ]),
      padding=20, border_radius=16,
      bgcolor=ft.Colors.with_opacity(0.2, "#0D1017"),
      border=ft.border.all(1, ft.Colors.with_opacity(0.3, theme_color if not disabled else "#333333")),
      on_click=None if disabled else test_click, data=title,
    )

  page.add(
    ft.Column([
      ft.Row([
        ft.Icon(ft.Icons.PHONE_ANDROID, color=theme_color, size=36),
        ft.Column([
          ft.Text("HuiJui Toolbox Edition", size=24, weight=ft.FontWeight.W_900, color="white"),
          ft.Text("Android Edition · APK 测试版", color=theme_color, size=12),
        ], spacing=0)
      ]),
      ft.Container(height=20),
      make_card("模块仓库", ft.Icons.EXTENSION, "浏览 797 个纯净模块"),
      ft.Container(height=10),
      make_card("急救中心", ft.Icons.HEALING, "驱动与端口状态监控"),
      ft.Container(height=10),
      make_card("一键刷机", ft.Icons.ELECTRIC_BOLT, "需连接 PC 辅助执行 (已禁用)", disabled=True),
      ft.Container(height=10),
      make_card("临时 Root", ft.Icons.SECURITY, "需连接 PC 辅助执行 (已禁用)", disabled=True),
      ft.Container(height=20),
      ft.Text("运行日志", size=14, color="white", weight=ft.FontWeight.BOLD),
      ft.Container(
        content=log_area, expand=True,
        bgcolor=ft.Colors.with_opacity(0.2, "#000000"),
        border_radius=12, padding=15,
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, theme_color)),
      )
    ], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
  )

if __name__ == "__main__":
  ft.app(target=main)
