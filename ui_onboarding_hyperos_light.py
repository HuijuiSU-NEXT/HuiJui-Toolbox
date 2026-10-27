# ui_onboarding_hyperos_light.py
import flet as ft
from core_api import CFG
import threading
import time

class HyperOSLightOnboarding(ft.Container):
  def __init__(self, on_finish):
    super().__init__(expand=True)
    self.on_finish = on_finish
    self.current_index = 0
    self.total_pages = 8
    self.agreed = False
    self.animating = False # 动画防抖锁

    # ================= 1. 高饱和背景 =================
    self.bg_base = ft.Container(expand=True, bgcolor="#FFFDF8")
    self.orb_green = ft.Container(
      width=2500, height=2500,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.8, "#1DE9B6"), ft.Colors.with_opacity(0.0, "#1DE9B6")]),
      border_radius=1250, left=-1000, top=-1200
    )
    self.orb_yellow = ft.Container(
      width=2500, height=2500,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.7, "#FFEA00"), ft.Colors.with_opacity(0.0, "#FFEA00")]),
      border_radius=1250, right=-1200, top=-500
    )
    self.orb_purple = ft.Container(
      width=2500, height=2500,
      gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.6, "#D500F9"), ft.Colors.with_opacity(0.0, "#D500F9")]),
      border_radius=1250, left=-400, bottom=-1200
    )
    self.bg_stack = ft.Stack([self.bg_base, self.orb_green, self.orb_yellow, self.orb_purple], expand=True)

    # ================= 2. 最稳的官方切换器 =================
    self.switcher = ft.AnimatedSwitcher(
      content=ft.Container(),
      transition=ft.AnimatedSwitcherTransition.SCALE,
      duration=500,
      switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
      switch_out_curve=ft.AnimationCurve.EASE_IN,
    )

    # ================= 3. 底部气泡按钮 =================
    self.btn_container = ft.Container(
      content=ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#333333", size=26),
      width=68, height=68,
      bgcolor=ft.Colors.with_opacity(0.5, "#FFFFFF"),
      blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
      border=ft.border.all(1, ft.Colors.with_opacity(0.8, "#FFFFFF")),
      border_radius=34,
      alignment=ft.alignment.center,
      shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.15, "#000000")),
    )
    self.btn_next = ft.GestureDetector(content=self.btn_container, on_tap=self.next_page)
    self.bottom_area = ft.Container(
      content=ft.Row([self.btn_next], alignment=ft.MainAxisAlignment.CENTER),
      padding=ft.padding.only(bottom=60)
    )

    self.layout = ft.Column([
      ft.Container(expand=True, content=self.switcher, alignment=ft.alignment.center),
      self.bottom_area
    ], expand=True)
    self.content = ft.Stack([self.bg_stack, self.layout], expand=True)

  def did_mount(self):
    self._render_page(0)

  def _render_page(self, index):
    self.current_index = index
    builders = [
      self._page_welcome, self._page_flash, self._page_rescue, self._page_root,
      self._page_modules, self._page_theme, self._page_ready, self._page_disclaimer
    ]
    
    # 构建新的页面容器
    new_page = ft.Container(
      content=builders[index](),
      expand=True,
      alignment=ft.alignment.center
    )
    
    # 切换内容
    self.switcher.content = new_page
    self.switcher.update()
    
    self._update_button_state()

  def _update_button_state(self):
    if self.current_index == self.total_pages - 1:
      self.btn_container.content = ft.Text("进入", size=15, weight=ft.FontWeight.W_600, color="#333333")
      self.btn_container.width = 100
      self.btn_container.bgcolor = ft.Colors.with_opacity(0.6, "#FFFFFF") if self.agreed else ft.Colors.with_opacity(0.2, "#FFFFFF")
    else:
      self.btn_container.content = ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#333333", size=26)
      self.btn_container.width = 68
      self.btn_container.bgcolor = ft.Colors.with_opacity(0.5, "#FFFFFF")
    
    # 如果还在动画中，按钮保持半透明
    if self.animating:
      self.btn_container.opacity = 0.4
    else:
      self.btn_container.opacity = 1.0
      
    self.btn_container.update()

  def _cool_down(self):
    """冷却 1 秒，防止疯狂连点导致动画飞页"""
    time.sleep(1.0)
    self.animating = False
    self._update_button_state()

  def next_page(self, e):
    # 1. 检查冷却锁
    if self.animating:
      return 
      
    # 2. 检查最后一页的同意状态
    if self.current_index == self.total_pages - 1:
      if not self.agreed:
        return
      else:
        self._finish()
        return

    # 3. 加锁并执行翻页
    self.animating = True
    self._update_button_state() # 让按钮变灰
    
    self._render_page(self.current_index + 1)
    
    # 4. 启动后台冷却线程
    threading.Thread(target=self._cool_down, daemon=True).start()

  def _on_agree_change(self, e):
    self.agreed = e.control.value
    if self.current_index == self.total_pages - 1:
      self._update_button_state()

  def _finish(self):
    CFG.set("onboarded", True)
    self.on_finish()

  # ================= 8 个页面 =================

  def _page_welcome(self):
    text_shadow = ft.Text("HuiJui OS", size=38, weight=ft.FontWeight.W_900, color=ft.Colors.with_opacity(0.3, "#FFFFFF"), offset=ft.Offset(0.02, 0.02))
    text_main = ft.Text("HuiJui OS", size=38, weight=ft.FontWeight.W_900, color="#FFFFFF")
    
    logo_box = ft.Container(
      content=ft.Image(src="D:/file_00000000561081fd82a2690c35ed3eab.png", width=140, height=140, fit=ft.ImageFit.COVER),
      width=140, height=140, border_radius=70, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
      shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.2, "#000000")),
      border=ft.border.all(3, "#FFFFFF"),
    )

    return ft.Column([
      ft.Stack([text_shadow, text_main], alignment=ft.alignment.center),
      ft.Container(height=60),
      logo_box,
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

  def _page_flash(self):
    return self._feature_layout("01", "全自动刷机", "智能 payload 解析与分区自动分流，底层逻辑全自动接管。")
  def _page_rescue(self):
    return self._feature_layout("02", "底层急救", "WMI 硬件级检测，精准识别 EDL / BROM 模式，一键拉起驱动。")
  def _page_root(self):
    return self._feature_layout("03", "临时 Root", "LKM late-load 无痕注入，无需解锁 BL，重启自动失效。")
  def _page_modules(self):
    return self._feature_layout("04", "模块矩阵", "内置 797 个纯净模块，支持实时搜索与一键下载安装。")
  def _page_theme(self):
    return self._feature_layout("05", "个性化定制", "深度自定义主题色与毛玻璃壁纸，打造属于你的极客桌面。")
  def _page_ready(self):
    return self._feature_layout("06", "准备就绪", "所有底层引擎已就绪，点击下一步完成最后的配置。")

  def _page_disclaimer(self):
    cb = ft.Checkbox(
      label="我已阅读并同意上述条款", 
      label_style=ft.TextStyle(color="#1E293B", size=15),
      active_color="#333333", 
      on_change=self._on_agree_change
    )
    
    # 把所有元素塞进一个 Column，确保复选框绝对居中
    return ft.Column([
      ft.Text("免责与安全声明", size=32, weight=ft.FontWeight.W_900, color="#1E293B"),
      ft.Container(height=20),
      ft.Text("本工具仅供技术交流与安全研究使用。\n刷机、Root 及底层操作具有极高风险，操作不当可能导致设备变砖或数据丢失。\n开发者不对任何设备损坏负责。",
          size=16, color="#334155", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_600),
      ft.Container(height=40),
      ft.Row([cb], alignment=ft.MainAxisAlignment.CENTER) # 强制复选框居中
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

  def _feature_layout(self, index_str, title, desc):
    title_shadow = ft.Text(title, size=38, weight=ft.FontWeight.W_900, color=ft.Colors.with_opacity(0.3, "#FFFFFF"), offset=ft.Offset(0.02, 0.02))
    title_main = ft.Text(title, size=38, weight=ft.FontWeight.W_900, color="#FFFFFF")
    desc_shadow = ft.Text(desc, size=18, weight=ft.FontWeight.W_600, color=ft.Colors.with_opacity(0.3, "#FFFFFF"), offset=ft.Offset(0.01, 0.01), text_align=ft.TextAlign.CENTER)
    desc_main = ft.Text(desc, size=18, weight=ft.FontWeight.W_600, color="#FFFFFF", text_align=ft.TextAlign.CENTER)

    return ft.Column([
      ft.Row([
        ft.Text(index_str, size=18, weight=ft.FontWeight.W_900, color=ft.Colors.with_opacity(0.7, "#FFFFFF")),
        ft.Container(width=15),
        ft.Container(width=40, height=2, bgcolor=ft.Colors.with_opacity(0.7, "#FFFFFF"), margin=ft.margin.only(top=8))
      ], alignment=ft.MainAxisAlignment.CENTER),
      ft.Container(height=30),
      ft.Stack([title_shadow, title_main], alignment=ft.alignment.center),
      ft.Container(height=15),
      ft.Stack([desc_shadow, desc_main], alignment=ft.alignment.center),
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
