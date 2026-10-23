import flet as ft
class LightStreak(ft.Container):
    def __init__(self):
        super().__init__(expand=True)
        self.shapes = ft.Column(spacing=80, controls=[
            ft.Container(height=1, width=600, gradient=ft.LinearGradient(colors=["transparent", "white", "transparent"]), opacity=0.03),
            ft.Container(height=1, width=900, gradient=ft.LinearGradient(colors=["transparent", "white", "transparent"]), opacity=0.02),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        self.content = self.shapes
