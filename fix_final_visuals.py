# fix_final_visuals.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
theme_path = os.path.join(BASE_DIR, "ui_theme.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 重写 ui_theme.py：真·玻璃拟态 ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
  material = CFG.get("ui_material", "default")
  blur_val = CFG.get("blur_radius", 10)
  
  if material == "frosted":
    return {
      "type": "frosted",
      "overlay_bg": ft.Colors.with_opacity(0.15, "#0D1017"),
      "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
      "nav_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
      "side_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
      "card_bg": ft.Colors.with_opacity(0.12, ft.Colors.WHITE), # 极透纯色
      "card_border": ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
      "log_bg": ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
      "log_color": "#00FFD1"
    }
  elif material == "liquid":
    # 🚨 真·液态玻璃：极度通透的底色 + 高光亮白边框
    return {
      "type": "liquid",
      "overlay_bg": ft.Colors.with_opacity(0.05, "#0D1017"), # 背景遮罩降到极低
      "overlay_blur": ft.Blur(blur_val, blur_val, ft.BlurTileMode.MIRROR) if blur_val > 0 else None,
      "nav_bg": ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
      "side_bg": ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
      "card_bg": ft.Colors.with_opacity(0.08, ft.Colors.WHITE), # 几乎透明，只留一点底
      "card_border": ft.border.all(1.5, ft.Colors.with_opacity(0.9, ft.Colors.WHITE)), # 极高亮边框模拟反光
      "log_bg": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
      "log_color": theme_color
    }
  else:
    return {
      "type": "default",
      "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
      "overlay_blur": None,
      "nav_bg": ft.Colors.with_opacity(0.3, "#0D1017"),
      "side_bg": ft.Colors.with_opacity(0.3, "#0D1017"),
      "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
      "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
      "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
      "log_color": "#00FFD1"
    }

def setup_page_style(page: ft.Page):
  theme_color = CFG.get("theme_color", "#39C5BB")
  page.bgcolor = ft.Colors.TRANSPARENT
  return theme_color
'''
with open(theme_path, "w", encoding="utf-8") as f:
  f.write(ui_theme_code)
print("✅ ui_theme.py 已重写：液态玻璃质感大幅提升！")

# ==================== 2. 重写 main_final.py 中的导航栏配置 ====================
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

# 强制将侧边栏字体换成微软雅黑（Windows 原生渲染最清晰），并提亮颜色
old_nav = '''selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=13, font_family="MiSans"),
      unselected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE70, size=12, font_family="MiSans"),'''

new_nav = '''selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.W_900, size=14, font_family="Microsoft YaHei"),
      unselected_label_text_style=ft.TextStyle(color=ft.Colors.WHITE, size=13, font_family="Microsoft YaHei"),'''

if old_nav in m_content:
  m_content = m_content.replace(old_nav, new_nav)
  print("✅ 侧边栏字体已改为微软雅黑，未选中状态强制纯白，拒绝发虚！")
else:
  # 兜底正则
  import re
  m_content = re.sub(r'selected_label_text_style=ft\.TextStyle.*?unselected_label_text_style=ft\.TextStyle.*?\),', new_nav, m_content, flags=re.DOTALL)
  print("✅ 已通过正则修复侧边栏字体！")

# 顺便给侧边栏加一个半透明底色块，让文字在亮色壁纸上也能看清楚
old_nav_bg = 'bgcolor=page.ui_style["nav_bg"], width=90)'
new_nav_bg = 'bgcolor=page.ui_style["nav_bg"], width=90, border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))))'
if old_nav_bg in m_content:
  m_content = m_content.replace(old_nav_bg, new_nav_bg)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(m_content)

# ==================== 3. 优化 settings.py 的输入框质感 ====================
with open(settings_path, "r", encoding="utf-8") as f:
  s_content = f.read()

# 下拉框背景改成极透
s_content = s_content.replace(
  'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), border_radius=10, options=[',
  'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE), border_radius=10, options=['
)
# 输入框背景改成极透
s_content = s_content.replace(
  'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), border_radius=10)',
  'bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE), border_radius=10)'
)

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(s_content)
print("✅ 输入框与下拉框的高光感已增强！")

print("🚀 终极视觉修复完成！请重新运行 python main_final.py。")