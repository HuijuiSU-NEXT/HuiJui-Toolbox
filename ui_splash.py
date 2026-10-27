import flet as ft
import threading
import time
import random

class SplashScreen(ft.Container):
  def __init__(self, on_finish, theme_color="#39C5BB"):
    super().__init__()
    self.on_finish = on_finish
    self.theme_color = theme_color
    self.expand = True
    self.bgcolor = "#090A0F" 
    self.alignment = ft.alignment.center
    
    # 动态光晕背景 (模拟液态玻璃底光)
    self.bg_glow = ft.Container(
      width=400, height=400,
      gradient=ft.RadialGradient(
        colors=[ft.Colors.with_opacity(0.15, theme_color), ft.Colors.TRANSPARENT],
        radius=1.0
      ),
      animate=ft.Animation(2000, ft.AnimationCurve.EASE_IN_OUT),
      opacity=0.5
    )
    
    # Logo 和 文字
    self.logo_text = ft.Text("HuiJui Core", size=46, weight=ft.FontWeight.BOLD, color="white", opacity=0, animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT))
    self.sub_text = ft.Text("Matrix Engine · Win11 x HyperOS", size=14, color=theme_color, opacity=0, animate_opacity=ft.Animation(1200, ft.AnimationCurve.EASE_OUT))
    
    self.loading_bar = ft.ProgressBar(value=0, color=theme_color, bgcolor=ft.Colors.with_opacity(0.1, "white"), width=240, height=4, border_radius=2)
    
    self.main_col = ft.Column([
      self.logo_text,
      ft.Container(height=10),
      self.sub_text,
      ft.Container(height=50),
      self.loading_bar
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, opacity=0, animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN))

    self.content = ft.Stack([
      ft.Container(content=self.bg_glow, alignment=ft.alignment.center),
      self.main_col
    ])
    
  def did_mount(self):
    threading.Thread(target=self._pulse_glow, daemon=True).start()
    threading.Thread(target=self._animate, daemon=True).start()

  def _pulse_glow(self):
    # 模拟液态呼吸感
    while True:
      try:
        self.bg_glow.width = 600
        self.bg_glow.height = 600
        self.bg_glow.opacity = 1.0
        self.bg_glow.update()
        time.sleep(1.5)
        self.bg_glow.width = 400
        self.bg_glow.height = 400
        self.bg_glow.opacity = 0.5
        self.bg_glow.update()
        time.sleep(1.5)
      except:
        break

  def _animate(self):
    time.sleep(0.2)
    try:
      self.main_col.opacity = 1
      self.logo_text.opacity = 1
      self.sub_text.opacity = 1
      self.update()
      
      # 进度条丝滑加载
      for i in range(101):
        self.loading_bar.value = i / 100
        self.update()
        time.sleep(0.015)
        
      time.sleep(0.3)
      # 淡出
      self.opacity = 0
      self.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_OUT)
      self.update()
      time.sleep(0.6)
      self.on_finish()
    except Exception:
      self.on_finish()
