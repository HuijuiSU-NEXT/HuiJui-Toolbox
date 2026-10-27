import flet as ft
import time
import threading
from .layer_starfield import Starfield
from .layer_liquid_glow import LiquidGlow
from .layer_light_streak import LightStreak
from .transition_manager import TransitionManager
from .page_factory import get_page
from .anim_ticker import Ticker

class OnboardingCore(ft.Container):
    def __init__(self, on_finish, theme_color="#39C5BB"):
        super().__init__(expand=True, bgcolor="#050608")
        self.on_finish = on_finish
        self.t = theme_color
        self.step = 0
        self.time_now = 0

        self.stars = Starfield()
        self.glow = LiquidGlow(theme_color)
        self.streak = LightStreak()
        self.bg = ft.Stack([self.glow, self.stars, self.streak], expand=True)

        self.box = ft.Container(expand=True, alignment=ft.alignment.center)
        self.trans = TransitionManager(self.box)

        self.btn = ft.ElevatedButton(
            "继续", on_click=self.next, bgcolor=theme_color, color="#0B0E14", 
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20))
        )

        self.layout = ft.Column([
            ft.Container(expand=True, content=self.box),
            ft.Container(content=ft.Row([self.btn], alignment=ft.MainAxisAlignment.END), padding=40)
        ], expand=True)

        self.content = ft.Stack([self.bg, self.layout], expand=True)

        self.ticker = Ticker(60)
        self.ticker.add(self._tick)

    def _tick(self, dt):
        self.time_now += dt
        self.stars.tick(dt)
        self.glow.tick(dt, self.time_now)

    def did_mount(self):
        self.show(0)

    def show(self, i):
        self.step = i
        self.trans.switch(get_page(i, self.t, self), direction=1)
        self.btn.text = "进入矩阵" if i == 2 else "继续"

    def next(self, e):
        if self.step < 2:
            self.show(self.step + 1)
        else:
            self.ticker.stop()
            self.on_finish()
