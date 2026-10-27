# fix_settings_text_sharp.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

if os.path.exists(settings_path):
  with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 把所有使用 WHITE70 或 GREY 的文本，全部改为纯白加粗，拒绝发虚
  content = content.replace('color=ft.Colors.WHITE70', 'color="#FFFFFF", weight=ft.FontWeight.W_600')
  content = content.replace('color=ft.Colors.GREY_400', 'color="#FFFFFF"')
  
  # 2. 提升输入框和下拉框里的文本清晰度
  content = content.replace(
    'text_style=ft.TextStyle(font_family="MiSans"), label_style=ft.TextStyle(color=ft.Colors.WHITE70, font_family="MiSans")',
    'text_style=ft.TextStyle(font_family="MiSans", color="#FFFFFF", weight=ft.FontWeight.W_600), label_style=ft.TextStyle(color="#FFFFFF", font_family="MiSans", weight=ft.FontWeight.W_500)'
  )
  
  # 3. 确保所有的按钮文字也是 MiSans 并且纯白
  # 匹配所有的 ft.Text(..., font_family="MiSans") 并确保颜色是纯白
  content = re.sub(r'(ft\.Text\([^)]*?)color=ft\.Colors\.WHITE70', r'\1color="#FFFFFF", weight=ft.FontWeight.W_600', content)
  content = re.sub(r'(ft\.Text\([^)]*?)color=ft\.Colors\.GREY_400', r'\1color="#FFFFFF"', content)

  # 4. 针对那几个按钮的文字单独提亮
  # 应用按钮、选择图片按钮等
  btn_style_fix = 'style=ft.ButtonStyle(color=theme_color, bgcolor=ft.Colors.with_opacity(0.15, theme_color), side=ft.BorderSide(1, theme_color), shape=ft.RoundedRectangleBorder(radius=8))'
  new_btn_style = 'style=ft.ButtonStyle(color="#FFFFFF", bgcolor=ft.Colors.with_opacity(0.2, theme_color), side=ft.BorderSide(1.5, theme_color), shape=ft.RoundedRectangleBorder(radius=8), text_style=ft.TextStyle(font_family="MiSans", weight=ft.FontWeight.W_600))'
  content = content.replace(btn_style_fix, new_btn_style)

  # 红色清除按钮
  content = content.replace(
    'style=ft.ButtonStyle(color=ft.Colors.RED_300, bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.RED_400), side=ft.BorderSide(1, ft.Colors.RED_400), shape=ft.RoundedRectangleBorder(radius=8))',
    'style=ft.ButtonStyle(color="#FFFFFF", bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.RED_400), side=ft.BorderSide(1.5, ft.Colors.RED_400), shape=ft.RoundedRectangleBorder(radius=8), text_style=ft.TextStyle(font_family="MiSans", weight=ft.FontWeight.W_600))'
  )

  with open(settings_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ 个性化设置页面的字体已全面提亮加粗，拒绝锯齿感！")
else:
  print("❌ 找不到 pages/settings.py")