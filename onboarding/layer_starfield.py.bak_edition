import flet as ft
import flet.canvas as cv
import random
class Starfield(ft.Container):
    def __init__(self):
        super().__init__(expand=True)
        self.stars = [{"x": random.uniform(0, 1200), "y": random.uniform(0, 800), "r": random.uniform(0.5, 2.5), "sp": random.uniform(20, 60), "op": random.uniform(0.2, 0.9)} for _ in range(120)]
        self.cv = cv.Canvas(expand=True)
        self.content = self.cv
    def tick(self, dt):
        self.cv.shapes.clear()
        for st in self.stars:
            st["y"] += st["sp"] * dt
            if st["y"] > 800:
                st["y"] = 0
                st["x"] = random.uniform(0, 1200)
            self.cv.shapes.append(cv.Circle(st["x"], st["y"], st["r"], ft.Paint(color=ft.Colors.with_opacity(st["op"], "#FFFFFF"))))
        self.cv.update()
