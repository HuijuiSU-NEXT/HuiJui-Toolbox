# onboarding/page_disclaimer.py
import flet as ft
from .ui_glass_card import GlassCard
def build_disclaimer(t, core):
    cb = ft.Checkbox(label="我已阅读并同意条款", label_style=ft.TextStyle(color="white"))
    def on_cb(e):
        core.btn.disabled = not cb.value
        core.btn.update()
    cb.on_change = on_cb
    core.btn.disabled = True
    return GlassCard(ft.Column([
        ft.Icon(ft.Icons.GPP_MAYBE_ROUNDED, size=60, color="#F0A030"),
        ft.Text("免责声明", size=30, weight=ft.FontWeight.BOLD, color="white"),
        ft.Text("本工具仅供技术交流与安全研究。操作不当可能导致设备变砖。", color="#94A3B8", text_align=ft.TextAlign.CENTER),
        cb
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20))
