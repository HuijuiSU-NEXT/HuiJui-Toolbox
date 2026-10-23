import flet as ft
def GlassCard(content, width=800, height=480, padding=40):
    return ft.Container(
        content=content, width=width, height=height, padding=padding,
        bgcolor=ft.Colors.with_opacity(0.03, "#FFFFFF"),
        blur=ft.Blur(30, 30, ft.BlurTileMode.MIRROR),
        border_radius=24, border=ft.border.all(1, ft.Colors.with_opacity(0.1, "#FFFFFF")),
        shadow=ft.BoxShadow(blur_radius=40, color=ft.Colors.with_opacity(0.4, "#000000"), offset=ft.Offset(0, 20))
    )
