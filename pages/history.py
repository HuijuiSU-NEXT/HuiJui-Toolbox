import flet as ft
from core_api import history_db

def build_history_page(page, theme_color):
  records = history_db.all(limit=100)
  history_list = ft.ListView(expand=True, spacing=10, padding=10)
  if not records: 
    history_list.controls.append(ft.Container(content=ft.Column([ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=60, color="#222634"), ft.Text("暂无刷机记录", size=16, color="#6E7B91")], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.alignment.center, expand=True))
  else:
    for ts, brand, model, zp, dur, ok in records:
      status_color = "#3FBF6E" if ok else "#E05070"
      status_text = "成功" if ok else "失败"
      dt_str = ts.replace("T", " ")[:19]
      history_list.controls.append(ft.Container(content=ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE if ok else ft.Icons.ERROR, color=status_color, size=28), ft.Container(width=15), ft.Column([ft.Text(f"{brand.upper()} {model}", size=16, weight=ft.FontWeight.BOLD, color="white"), ft.Text(f"包名: {zp}", size=12, color="#8892B0"), ft.Text(f"时间: {dt_str} | 耗时: {dur}秒", size=11, color="#6E7B91")], spacing=4, expand=True), ft.Container(content=ft.Text(status_text, size=12, color="white", weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.with_opacity(0.2, status_color), padding=ft.padding.symmetric(horizontal=10, vertical=4), border_radius=8)], alignment=ft.MainAxisAlignment.START), bgcolor=ft.Colors.with_opacity(0.4, "#131722"), blur=10, border=ft.border.all(1, ft.Colors.with_opacity(0.1, status_color)), border_radius=12, padding=15))
  return ft.Container(expand=True, padding=30, content=ft.Column([ft.Text("Flash History", size=36, weight=ft.FontWeight.BOLD, color="white"), ft.Text("包含机型、耗时与状态", size=14, color=theme_color, weight=ft.FontWeight.W_600), ft.Container(height=20), ft.Container(content=history_list, expand=True)]))