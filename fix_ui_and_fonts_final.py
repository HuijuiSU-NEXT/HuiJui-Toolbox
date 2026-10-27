# fix_ui_and_fonts_final.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 优化 main_final.py 的导航栏 ====================
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

# 修复 NavigationRail 的标签字体和颜色
old_nav = '''      selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=12),
      unselected_label_text_style=ft.TextStyle(color="#8892B0", size=12),'''

new_nav = '''      selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=12, font_family="MiSans"),
      unselected_label_text_style=ft.TextStyle(color="#A0ABC0", size=12, font_family="MiSans"),'''

if old_nav in m_content:
  m_content = m_content.replace(old_nav, new_nav)
  print("✅ 已优化导航栏字体为 MiSans，并提亮未选中状态的文字！")

# 优化导航栏指示器颜色（防止太刺眼）
m_content = m_content.replace(
  'indicator_color=ft.Colors.with_opacity(0.2, theme_color)',
  'indicator_color=ft.Colors.with_opacity(0.3, theme_color)'
)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(m_content)

# ==================== 2. 优化 settings.py 的输入框和下拉框 ====================
with open(settings_path, "r", encoding="utf-8") as f:
  s_content = f.read()

# 2.1 优化颜色输入框
old_color_input = '''  color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))'''
new_color_input = '''  color_input = ft.TextField(
    value=state["theme_color"], 
    label="自定义 HEX 颜色", 
    width=200, 
    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), 
    color="white", 
    border_color=ft.Colors.with_opacity(0.4, theme_color),
    border_radius=8,
    text_style=ft.TextStyle(font_family="MiSans"),
    label_style=ft.TextStyle(color=ft.Colors.GREY_400, font_family="MiSans")
  )'''
if old_color_input in s_content:
  s_content = s_content.replace(old_color_input, new_color_input)
  print("✅ 已优化颜色输入框为半透明玻璃风！")

# 2.2 优化材质下拉框
old_dropdown = '''  material_dropdown = ft.Dropdown(label="UI 材质", value=state["ui_material"], width=300, bgcolor="#1A233A", color="white", options=[ft.dropdown.Option("default", "默认"), ft.dropdown.Option("frosted", "毛玻璃"), ft.dropdown.Option("liquid", "液态玻璃")], on_change=lambda e: apply_material(e.control.value))'''
new_dropdown = '''  material_dropdown = ft.Dropdown(
    label="UI 材质", 
    value=state["ui_material"], 
    width=300, 
    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), 
    color="white", 
    border_color=ft.Colors.with_opacity(0.4, theme_color),
    border_radius=8,
    text_style=ft.TextStyle(font_family="MiSans"),
    label_style=ft.TextStyle(color=ft.Colors.GREY_400, font_family="MiSans"),
    options=[
      ft.dropdown.Option("default", "默认"),
      ft.dropdown.Option("frosted", "毛玻璃"),
      ft.dropdown.Option("liquid", "液态玻璃")
    ], 
    on_change=lambda e: apply_material(e.control.value)
  )'''
if old_dropdown in s_content:
  s_content = s_content.replace(old_dropdown, new_dropdown)
  print("✅ 已优化下拉框样式！")

# 2.3 强行把所有 ft.Text 加上 MiSans 字体
# 用简单粗暴的替换逻辑，给 ft.Text( 后面没写 font_family 的加进去
# 先确保不重复添加
s_content = s_content.replace(', font_family="MiSans")', ')') # 清理已有的防止重复
s_content = s_content.replace('ft.Text(', 'ft.Text(font_family="MiSans", ')

# 修复可能导致双引号冲突的地方
s_content = s_content.replace('ft.Text(font_family="MiSans", title=', 'ft.Text(title=')
s_content = s_content.replace('ft.Text(font_family="MiSans", card["', 'ft.Text(card["')

print("✅ 已强制为 settings.py 内所有文本应用 MiSans 字体！")

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(s_content)

print("🚀 终极 UI 与字体补丁注入完毕！请重新运行 python main_final.py。")