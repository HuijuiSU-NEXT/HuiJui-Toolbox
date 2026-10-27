import flet as ft
import threading
import time
import math
from core_api import CFG

class LifeAestheticBackground(ft.Container):
  """HyperOS 4 ‘生命感美学’ 动态背景：多色渐变与流动光斑"""
  def __init__(self):
    super().__init__(expand=True, bgcolor="#0A0E1A") # 深色基底
    self.t = 0.0
    # 动态色调映射层：深蓝 -> 墨绿
    self.gradient_layer = ft.Container(
      expand=True,
      gradient=ft.LinearGradient(
        begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
        colors=["#0A0E1A", "#0F2A2E", "#0A0E1A"] # 深蓝 -> 墨绿 -> 深蓝
      ),
      animate=ft.Animation(10000, ft.AnimationCurve.EASE_IN_OUT)
    )
    # 液态光斑层 (绿色 & 紫色)
    self.glow_green = ft.Container(
      width=800, height=800,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.15, "#39C5BB"), ft.Colors.TRANSPARENT]),
      border_radius=400, left=-200, top=-200, blur=80,
      animate=ft.Animation(8000, ft.AnimationCurve.EASE_IN_OUT)
    )
    self.glow_purple = ft.Container(
      width=600, height=600,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.12, "#A070E0"), ft.Colors.TRANSPARENT]),
      border_radius=300, right=-150, bottom=-150, blur=80,
      animate=ft.Animation(6000, ft.AnimationCurve.EASE_IN_OUT)
    )
    self.content = ft.Stack([self.gradient_layer, self.glow_green, self.glow_purple], expand=True)

  def tick(self, dt):
    self.t += dt
    # 光斑缓慢游走
    self.glow_green.left = -200 + math.sin(self.t * 0.25) * 100
    self.glow_green.top = -200 + math.cos(self.t * 0.35) * 80
    self.glow_purple.right = -150 + math.cos(self.t * 0.2) * 80
    self.glow_purple.bottom = -150 + math.sin(self.t * 0.3) * 80
    # 渐变层呼吸
    self.gradient_layer.opacity = 0.85 + 0.15 * math.sin(self.t * 0.15)
    self.update()

class LiquidGlassCard(ft.Container):
  """液态玻璃卡片：高透明度 + 深度模糊 + 柔和光边"""
  def __init__(self, content, width=760, height=480, padding=50):
    super().__init__(
      content=content, width=width, height=height, padding=padding,
      bgcolor=ft.Colors.with_opacity(0.06, "#FFFFFF"), # 极低透明度
      blur=ft.Blur(40, 40, ft.BlurTileMode.MIRROR),  # 深度模糊
      border_radius=32,
      border=ft.border.all(1.5, ft.Colors.with_opacity(0.12, "#FFFFFF")), # 柔和高光边
      shadow=ft.BoxShadow(blur_radius=60, color=ft.Colors.with_opacity(0.2, "#000000"), offset=ft.Offset(0, 24)),
    )

class HyperOSLifeOnboarding(ft.Container):
  def __init__(self, on_finish, theme_color="#39C5BB"):
    super().__init__(expand=True)
    self.on_finish = on_finish
    self.t = theme_color
    self.step = 0
    self.running = True

    self.bg = LifeAestheticBackground()
    self.card_area = ft.Container(expand=True, alignment=ft.alignment.center)

    self.switcher = ft.AnimatedSwitcher(
      content=ft.Container(),
      transition=ft.AnimatedSwitcherTransition.FADE,
      duration=600,
      switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
      switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
    )
    self.card_area.content = self.switcher

    # 液态玻璃按钮
    self.btn_text = ft.Text("开始使用", size=16, weight=ft.FontWeight.W_600, color="#FFFFFF")
    self.btn = ft.Container(
      content=self.btn_text, width=200, height=54,
      bgcolor=ft.Colors.with_opacity(0.15, self.t), # 半透明绿色
      border_radius=27,
      alignment=ft.alignment.center,
      border=ft.border.all(1, ft.Colors.with_opacity(0.3, "#FFFFFF")),
      shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.3, self.t)),
      animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
      animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
      on_click=self.next_step,
    )

    self.layout = ft.Column([
      ft.Container(expand=True, content=self.card_area),
      ft.Container(content=ft.Row([self.btn], alignment=ft.MainAxisAlignment.CENTER), padding=ft.padding.only(bottom=60))
    ], expand=True)

    self.content = ft.Stack([self.bg, self.layout], expand=True)
    threading.Thread(target=self._animate_loop, daemon=True).start()

  def _animate_loop(self):
    last = time.time()
    while self.running:
      now = time.time()
      dt = min(now - last, 0.05)
      last = now
      try: self.bg.tick(dt)
      except: pass
      time.sleep(1 / 60)

  def did_mount(self):
    self._show_page(0)

  def _show_page(self, idx):
    self.step = idx
    if idx == 0:
      page = self._build_welcome(); self.btn_text.value = "开始使用"
    elif idx == 1:
      page = self._build_features(); self.btn_text.value = "下一步"
    else:
      page = self._build_disclaimer(); self.btn_text.value = "进入矩阵"
    self.switcher.content = page
    self.switcher.update()

  def _build_welcome(self):
    return LiquidGlassCard(ft.Column([
      ft.Icon(ft.Icons.ANDROID, size=68, color=self.t),
      ft.Container(height=28),
      ft.Text("欢迎使用", size=40, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
      ft.Text("Xiaomi HyperOS 4", size=18, color="#8892B0"),
      ft.Container(height=16),
      ft.Text("轻点，开始你的新日常", size=14, color="#4B5568"),
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6))

  def _build_features(self):
    def item(icon, title, desc):
      return ft.Row([
        ft.Container(ft.Icon(icon, size=22, color=self.t), width=44, height=44, bgcolor=ft.Colors.with_opacity(0.1, self.t), border_radius=12, alignment=ft.alignment.center),
        ft.Column([ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#FFFFFF"), ft.Text(desc, size=13, color="#8892B0")], spacing=2)
      ], spacing=16)
    return LiquidGlassCard(ft.Column([
      ft.Text("全新特性", size=26, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
      ft.Container(height=20),
      item(ft.Icons.BOLT_ROUNDED, "全自动刷机", "双阶段解包与分区自动分流"),
      ft.Container(height=12),
      item(ft.Icons.SECURITY_ROUNDED, "临时 Root", "LKM late-load 无痕注入"),
      ft.Container(height=12),
      item(ft.Icons.HEALTH_AND_SAFETY_ROUNDED, "底层急救", "WMI 检测与驱动自动拉起"),
    ], spacing=0))

  def _build_disclaimer(self):
    cb = ft.Checkbox(label="我已阅读并同意上述条款", label_style=ft.TextStyle(color="#FFFFFF", size=14))
    def on_cb(e):
      self.btn.opacity = 1.0 if cb.value else 0.4
      self.btn.disabled = not cb.value
      self.btn.update()
    cb.on_change = on_cb
    self.btn.disabled = True; self.btn.opacity = 0.4

    return LiquidGlassCard(ft.Column([
      ft.Icon(ft.Icons.GPP_MAYBE_ROUNDED, size=52, color="#F59E0B"),
      ft.Container(height=14),
      ft.Text("免责与安全声明", size=24, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
      ft.Container(
        content=ft.Text("本工具仅供技术交流与安全研究使用。\n刷机、Root 及底层操作具有极高风险，\n操作不当可能导致设备变砖或数据丢失。", size=14, color="#8892B0", text_align=ft.TextAlign.CENTER),
        bgcolor=ft.Colors.with_opacity(0.05, "#F59E0B"), padding=18, border_radius=14
      ),
      ft.Container(height=14), cb
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12))

  def next_step(self, e):
    self.btn.scale = 0.95; self.btn.update(); time.sleep(0.1)
    self.btn.scale = 1.0; self.btn.update()
    if self.step < 2:
      self._show_page(self.step + 1)
    elif not self.btn.disabled:
      self.running = False
      CFG.set("onboarded", True)
      self.on_finish()
