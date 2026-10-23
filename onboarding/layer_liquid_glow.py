import flet as ft
import math
class LiquidGlow(ft.Container):
    def __init__(self, t):
        super().__init__(expand=True)
        self.g1 = ft.Container(width=600, height=600, gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.15, t), "transparent"]), left=-100, top=-100, blur=50)
        self.g2 = ft.Container(width=500, height=500, gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.1, "#A070E0"), "transparent"]), right=-100, bottom=-100, blur=50)
        self.content = ft.Stack([self.g1, self.g2])
    def tick(self, dt, t):
        self.g1.left = -100 + math.sin(t) * 60
        self.g1.top = -100 + math.cos(t*0.8) * 60
        self.g2.right = -100 + math.cos(t*1.2) * 60
        self.g2.bottom = -100 + math.sin(t*0.9) * 60
        self.g1.update()
        self.g2.update()
