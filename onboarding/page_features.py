import flet as ft
from .ui_glass_card import GlassCard
def build_features(t):
    return GlassCard(ft.Column([
        ft.Text("核心特性矩阵", size=30, weight=ft.FontWeight.BOLD, color="white"),
        ft.Divider(color=ft.Colors.with_opacity(0.1, "white")),
        ft.ListTile(leading=ft.Icon(ft.Icons.FLASH_ON, color="#FF6B6B"), title=ft.Text("全自动刷机", color="white"), subtitle=ft.Text("双阶段解包与分流", color="#94A3B8")),
        ft.ListTile(leading=ft.Icon(ft.Icons.SECURITY, color="#A070E0"), title=ft.Text("临时 Root", color="white"), subtitle=ft.Text("LKM late-load 注入", color="#94A3B8")),
    ], spacing=10))
