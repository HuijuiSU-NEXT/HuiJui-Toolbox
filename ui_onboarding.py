# ui_onboarding.py
# HuiJui Core · 独立引导模块 (HyperOS 4 液态玻璃 x Win11 弹性动效)
import flet as ft
import threading
import time
import math
from core_api import CFG

class GlowBackground(ft.Container):
  """动态液态光晕背景"""
  def __init__(self, theme_color):
    super().__init__(expand=True, bgcolor="#F8FAFC")
    self.theme_color = theme_color
    self.glow1 = ft.Container(
      width=600, height=600,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.16, self.theme_color), ft.Colors.TRANSPARENT]),
      border_radius=300, left=-100, top=-100, blur=45
    )
    self.glow2 = ft.Container(
      width=500, height=500,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.12, "#A070E0"), ft.Colors.TRANSPARENT]),
      border_radius=250, right=-100, bottom=-100, blur=45
    )
    self.content = ft.Stack([self.glow1, self.glow2], expand=True)
  
  def did_mount(self):
    threading.Thread(target=self._animate_glow, daemon=True).start()

  def _animate_glow(self):
    t = 0
    while True:
      try:
        t += 0.02
        self.glow1.left = -100 + math.sin(t) * 60
        self.glow1.top = -100 + math.cos(t * 0.8) * 60
        self.glow2.right = -100 + math.cos(t * 1.2) * 50
        self.glow2.bottom = -100 + math.sin(t * 0.9) * 50
        self.glow1.update()
        self.glow2.update()
        time.sleep(1 / 30)
      except Exception:
        break

class OnboardingScreen(ft.Container):
  def __init__(self, on_finish, theme_color="#39C5BB"):
    super().__init__()
    self.on_finish = on_finish
    self.theme_color = theme_color
    self.expand = True
    self.current_step = 0
    self.agree_check = False
    
    self.bg_layer = GlowBackground(theme_color)
    
    # 核心卡片
    self.card_content = ft.Column(alignment=ft.MainAxisAlignment.CENTER, spacing=0)
    self.card = ft.Container(
      width=820, height=500,
      bgcolor=ft.Colors.with_opacity(0.65, "#FFFFFF"),
      blur=ft.Blur(30, 30, ft.BlurTileMode.MIRROR),
      border_radius=28,
      border=ft.border.all(1.5, ft.Colors.with_opacity(0.8, "#FFFFFF")),
      shadow=ft.BoxShadow(blur_radius=40, color=ft.Colors.with_opacity(0.08, "#000000"), offset=ft.Offset(0, 16)),
      padding=50,
      content=self.card_content,
      offset=ft.Offset(0, 0),
      opacity=1,
      animate_offset=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
      animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
    )

    # 底部
    self.btn_prev = ft.TextButton("上一步", on_click=self.prev_step, visible=False, style=ft.ButtonStyle(color="#5A6470"))
    self.btn_next = ft.FilledButton(
      "开始探索", on_click=self.next_step, bgcolor=theme_color, color="white",
      width=140, height=48, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=24), overlay_color=ft.Colors.with_opacity(0.2, "white"))
    )
    self.dots = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    self.layout = ft.Column([
      ft.Container(expand=True, content=ft.Row([self.card], alignment=ft.MainAxisAlignment.CENTER)),
      ft.Container(
        content=ft.Row([
          ft.Container(width=140, content=self.btn_prev),
          self.dots,
          ft.Container(width=140, content=ft.Row([self.btn_next], alignment=ft.MainAxisAlignment.END))
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=120, vertical=40)
      )
    ], expand=True)

    self.content = ft.Stack([self.bg_layer, self.layout], expand=True)

  def did_mount(self):
    self.render_step(initial=True)

  def update_dots(self):
    self.dots.controls.clear()
    for i in range(3):
      self.dots.controls.append(
        ft.Container(
          width=24 if i == self.current_step else 10,
          height=10, border_radius=5,
          bgcolor=self.theme_color if i == self.current_step else "#CBD5E1",
          animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_CUBIC)
        )
      )

  def switch_page(self, target_step, direction=1):
    self.card.offset = ft.Offset(-0.15 * direction, 0)
    self.card.opacity = 0
    self.update()
    
    def update_content():
      time.sleep(0.3)
      self.current_step = target_step
      self.update_dots()
      self._build_content(target_step)
      
      self.card.offset = ft.Offset(0.15 * direction, 0)
      self.update()
      time.sleep(0.05)
      
      self.card.offset = ft.Offset(0, 0)
      self.card.opacity = 1
      self.update()
    threading.Thread(target=update_content, daemon=True).start()

  def next_step(self, e):
    if self.current_step < 2:
      self.switch_page(self.current_step + 1, direction=1)
    else:
      if self.agree_check:
        CFG.set("onboarded", True)
        self.on_finish()

  def prev_step(self, e):
    if self.current_step > 0:
      self.switch_page(self.current_step - 1, direction=-1)

  def toggle_agree(self, e):
    self.agree_check = e.control.value
    self.btn_next.disabled = not self.agree_check
    self.btn_next.bgcolor = self.theme_color if self.agree_check else "#CBD5E1"
    self.update()

  def render_step(self, initial=False):
    self.update_dots()
    self._build_content(self.current_step)
    if initial:
      self.card.scale = 0.9
      self.card.opacity = 0
      self.update()
      time.sleep(0.1)
      self.card.scale = 1.0
      self.card.opacity = 1
      self.update()

  def _build_content(self, step):
    self.card_content.controls.clear()
    
    if step == 0:
      self.btn_prev.visible = False
      self.btn_next.text = "开始探索"
      self.btn_next.disabled = False
      self.btn_next.bgcolor = self.theme_color
      
      logo = ft.Container(
        content=ft.Icon(ft.Icons.ROCKET_LAUNCH_ROUNDED, size=64, color="white"),
        width=120, height=120,
        gradient=ft.LinearGradient(colors=[self.theme_color, "#A070E0"], begin=ft.alignment.top_left, end=ft.alignment.bottom_right),
        border_radius=30, shadow=ft.BoxShadow(blur_radius=24, color=ft.Colors.with_opacity(0.4, self.theme_color), offset=ft.Offset(0, 12)),
        alignment=ft.alignment.center, animate=ft.Animation(1800, ft.AnimationCurve.EASE_IN_OUT)
      )
      self.card_content.controls = [
        ft.Row([logo], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=40),
        ft.Text("HuiJui Core", size=38, weight=ft.FontWeight.BOLD, color="#0F172A", text_align=ft.TextAlign.CENTER),
        ft.Container(height=12),
        ft.Text("Matrix Engine · 极客安卓底层控制中心", size=16, color="#64748B", text_align=ft.TextAlign.CENTER),
      ]
    elif step == 1:
      self.btn_prev.visible = True
      self.btn_next.text = "下一步"
      self.btn_next.disabled = False
      self.btn_next.bgcolor = self.theme_color

      def f_block(icon, color, title, desc):
        return ft.Container(
          content=ft.Row([
            ft.Container(content=ft.Icon(icon, color=color, size=22), width=44, height=44, bgcolor=ft.Colors.with_opacity(0.1, color), border_radius=10, alignment=ft.alignment.center),
            ft.Column([ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#1E293B"), ft.Text(desc, size=13, color="#64748B")], spacing=2)
          ], spacing=16), padding=14, border_radius=14, bgcolor=ft.Colors.with_opacity(0.03, "#000000"), border=ft.border.all(1, ft.Colors.with_opacity(0.06, "#000000"))
        )
      self.card_content.controls = [
        ft.Text("核心模块矩阵", size=28, weight=ft.FontWeight.BOLD, color="#0F172A"),
        ft.Text("软硬结合，全场景底层接管", size=14, color="#64748B"),
        ft.Container(height=28),
        f_block(ft.Icons.ELECTRIC_BOLT_ROUNDED, "#EF4444", "全自动刷机", "双重解包与分区自动分流，进度实时同步。"),
        ft.Container(height=12),
        f_block(ft.Icons.SECURITY_ROUNDED, "#8B5CF6", "临时 Root", "LKM late-load 深度注入，重启自动擦除痕迹。"),
        ft.Container(height=12),
        f_block(ft.Icons.HEALTH_AND_SAFETY_ROUNDED, "#10B981", "底层急救", "WMI 检测底层硬件通道，一键自动拉起救砖驱动。"),
      ]
    elif step == 2:
      self.btn_prev.visible = True
      self.btn_next.text = "进入矩阵"
      self.btn_next.disabled = not self.agree_check
      self.btn_next.bgcolor = self.theme_color if self.agree_check else "#CBD5E1"
      
      self.card_content.controls = [
        ft.Row([ft.Icon(ft.Icons.GPP_MAYBE_ROUNDED, size=48, color="#F59E0B")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=20),
        ft.Text("安全与免责声明", size=26, weight=ft.FontWeight.BOLD, color="#0F172A", text_align=ft.TextAlign.CENTER),
        ft.Container(height=15),
        ft.Container(
          content=ft.Text("本工具仅供技术交流与安全研究使用。\n刷机、Root 及底层操作具有极高风险，操作不当可能导致设备变砖或数据丢失。\n用户需自行承担操作带来的全部风险。", size=14, color="#475569", text_align=ft.TextAlign.CENTER, height=100),
          bgcolor=ft.Colors.with_opacity(0.06, "#F59E0B"), padding=20, border_radius=14, width=600
        ),
        ft.Container(height=16),
        ft.Checkbox(label="我已阅读并同意上述条款", value=self.agree_check, on_change=self.toggle_agree, label_style=ft.TextStyle(color="#0F172A", size=14), active_color=self.theme_color)
      ]