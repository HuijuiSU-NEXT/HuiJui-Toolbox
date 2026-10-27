import flet as ft
import threading
import time
import math
import random
from core_api import CFG

class HyperOSLiquidBackground(ft.Container):
    """澎湃OS 4 液态玻璃背景：深色动态渐变 + 流动光斑"""
    def __init__(self, theme_color):
        super().__init__(expand=True, bgcolor="#0A0E1A") # 深色基调
        self.theme_color = theme_color
        self.t = 0.0
        # 模拟动态色调映射的渐变层
        self.gradient_layer = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=["#0A0E1A", "#0F2A2E", "#0A0E1A"] # 深蓝 -> 墨绿 -> 深蓝
            ),
            animate=ft.Animation(10000, ft.AnimationCurve.EASE_IN_OUT)
        )
        # 液态光斑层
        self.glow1 = ft.Container(
            width=700, height=700,
            gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.12, theme_color), ft.Colors.TRANSPARENT]),
            border_radius=350, left=-200, top=-200, blur=80,
            animate=ft.Animation(8000, ft.AnimationCurve.EASE_IN_OUT)
        )
        self.glow2 = ft.Container(
            width=500, height=500,
            gradient=ft.RadialGradient(colors=[ft.Colors.with_opacity(0.08, "#4A9EFF"), ft.Colors.TRANSPARENT]),
            border_radius=250, right=-150, bottom=-100, blur=80,
            animate=ft.Animation(6000, ft.AnimationCurve.EASE_IN_OUT)
        )
        self.content = ft.Stack([self.gradient_layer, self.glow1, self.glow2], expand=True)

    def tick(self, dt):
        self.t += dt
        # 光斑缓慢漂移，模拟陀螺仪动态光效
        self.glow1.left = -200 + math.sin(self.t * 0.3) * 120
        self.glow1.top = -200 + math.cos(self.t * 0.4) * 100
        self.glow2.right = -150 + math.cos(self.t * 0.25) * 100
        self.glow2.bottom = -100 + math.sin(self.t * 0.35) * 100
        # 渐变层缓慢呼吸
        self.gradient_layer.opacity = 0.8 + 0.2 * math.sin(self.t * 0.2)
        self.update()


class HyperOSGlassCard(ft.Container):
    """液态玻璃卡片：半透明磨砂底纹 + 高光描边"""
    def __init__(self, content, width=720, height=480, padding=50):
        super().__init__(
            content=content, width=width, height=height, padding=padding,
            bgcolor=ft.Colors.with_opacity(0.06, "#FFFFFF"), # 极低透明度
            blur=ft.Blur(40, 40, ft.BlurTileMode.MIRROR),   # 深度模糊
            border_radius=32,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.12, "#FFFFFF")), # 玻璃高光边
            shadow=ft.BoxShadow(blur_radius=60, color=ft.Colors.with_opacity(0.3, "#000000"), offset=ft.Offset(0, 24)),
        )


class HyperOSOnboarding(ft.Container):
    def __init__(self, on_finish, theme_color="#FF6900"): # 小米橙
        super().__init__(expand=True)
        self.on_finish = on_finish
        self.theme_color = theme_color
        self.step = 0
        self.running = True
        self._current_page = None

        # 背景层
        self.bg = HyperOSLiquidBackground(theme_color)

        # 内容区
        self.content_area = ft.Container(expand=True, alignment=ft.alignment.center)
        
        # 底部橙色主按钮 (澎湃OS标志性设计)
        self.btn_text = ft.Text("开始使用", size=16, weight=ft.FontWeight.W_600, color="#FFFFFF")
        self.btn = ft.Container(
            content=self.btn_text,
            width=200, height=54,
            bgcolor="#FF6900", # 小米橙
            border_radius=27,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.4, "#FF6900")),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            on_click=self.next_step,
        )

        # 溶解过渡容器
        self.switcher = ft.AnimatedSwitcher(
            content=ft.Container(),
            transition=ft.AnimatedSwitcherTransition.FADE, # 溶解式淡入淡出
            duration=600,
            switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
            switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
        )
        self.content_area.content = self.switcher

        self.layout = ft.Column([
            ft.Container(expand=True, content=self.content_area),
            ft.Container(
                content=ft.Row([self.btn], alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.only(bottom=60)
            )
        ], expand=True)

        self.content = ft.Stack([self.bg, self.layout], expand=True)

        # 动画驱动器
        threading.Thread(target=self._animate_loop, daemon=True).start()

    def _animate_loop(self):
        last = time.time()
        while self.running:
            now = time.time()
            dt = min(now - last, 0.05)
            last = now
            try:
                self.bg.tick(dt)
            except:
                pass
            time.sleep(1 / 60)

    def did_mount(self):
        self._show_page(0)

    def _show_page(self, idx):
        self.step = idx
        if idx == 0:
            page = self._build_welcome_page()
            self.btn_text.value = "开始使用"
        elif idx == 1:
            page = self._build_features_page()
            self.btn_text.value = "下一步"
        else:
            page = self._build_disclaimer_page()
            self.btn_text.value = "进入桌面"

        # 溶解过渡：旧页面淡出，新页面淡入
        self.switcher.content = page
        self.switcher.update()

    def _build_welcome_page(self):
        return HyperOSGlassCard(
            ft.Column([
                ft.Icon(ft.Icons.ANDROID, size=72, color=self.theme_color),
                ft.Container(height=30),
                ft.Text("欢迎使用", size=42, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Text("Xiaomi HyperOS 4", size=18, color="#8892B0"),
                ft.Container(height=20),
                ft.Text("轻点，开始你的新日常", size=14, color="#4B5568"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
        )

    def _build_features_page(self):
        def feature_item(icon, title, desc):
            return ft.Row([
                ft.Container(content=ft.Icon(icon, color=self.theme_color, size=22), width=44, height=44, bgcolor=ft.Colors.with_opacity(0.1, self.theme_color), border_radius=10, alignment=ft.alignment.center),
                ft.Column([ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="#FFFFFF"), ft.Text(desc, size=13, color="#8892B0")], spacing=2)
            ], spacing=16)

        return HyperOSGlassCard(
            ft.Column([
                ft.Text("全新特性", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(height=24),
                feature_item(ft.Icons.BOLT_ROUNDED, "全自动刷机", "双阶段解包与分区自动分流"),
                ft.Container(height=14),
                feature_item(ft.Icons.SECURITY_ROUNDED, "临时 Root", "LKM late-load 无痕注入"),
                ft.Container(height=14),
                feature_item(ft.Icons.HEALTH_AND_SAFETY_ROUNDED, "底层急救", "WMI 检测与驱动自动拉起"),
            ], spacing=0)
        )

    def _build_disclaimer_page(self):
        cb = ft.Checkbox(label="我已阅读并同意上述条款", label_style=ft.TextStyle(color="#FFFFFF", size=14))
        def on_cb(e):
            self.btn.opacity = 1.0 if cb.value else 0.4
            self.btn.disabled = not cb.value
            self.btn.update()
        cb.on_change = on_cb
        self.btn.disabled = True
        self.btn.opacity = 0.4

        return HyperOSGlassCard(
            ft.Column([
                ft.Icon(ft.Icons.GPP_MAYBE_ROUNDED, size=56, color="#F0A030"),
                ft.Container(height=16),
                ft.Text("免责与安全声明", size=26, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Container(
                    content=ft.Text("本工具仅供技术交流与安全研究使用。\n刷机、Root 及底层操作具有极高风险，\n操作不当可能导致设备变砖或数据丢失。", size=14, color="#A0ABC0", text_align=ft.TextAlign.CENTER),
                    bgcolor=ft.Colors.with_opacity(0.05, "#F0A030"), padding=20, border_radius=14
                ),
                ft.Container(height=16),
                cb
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16)
        )

    def next_step(self, e):
        # 按钮按压缩放动画
        self.btn.scale = 0.95
        self.btn.update()
        time.sleep(0.1)
        self.btn.scale = 1.0
        self.btn.update()

        if self.step < 2:
            self._show_page(self.step + 1)
        else:
            if not self.btn.disabled:
                self.running = False
                CFG.set("onboarded", True)
                self.on_finish()
