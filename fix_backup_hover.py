# fix_backup_hover.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
backup_path = os.path.join(BASE_DIR, "pages", "backup.py")

if os.path.exists(backup_path):
  with open(backup_path, "r", encoding="utf-8") as f:
    content = f.read()

  # 1. 寻找并替换错误的 on_hover lambda 写法
  # 旧代码: on_hover=lambda e: e.control.update(bgcolor=...)
  old_lambda = r'on_hover=lambda e: e\.control\.update\(bgcolor=.*?\)'
  
  # 新代码：使用规范的属性赋值 + 无参 update
  new_hover_func = '''on_hover=handle_hover'''
  
  if re.search(old_lambda, content):
    content = re.sub(old_lambda, new_hover_func, content)
    print("✅ 已移除错误的内联 on_hover 写法！")
  
  # 2. 确保 handle_hover 函数被定义（如果还没有的话）
  # 我们需要找到 make_card 或 for 循环生成卡片的地方，把函数塞进去
  if "def handle_hover(e):" not in content:
    # 寻找函数入口 build_backup_page 并插入 handle_hover
    insert_target = "def build_backup_page(page: ft.Page, theme_color):"
    hover_func_def = '''
def handle_hover(e):
  e.control.bgcolor = ft.Colors.with_opacity(0.2, theme_color) if e.data == "true" else ft.Colors.with_opacity(0.08, ft.Colors.WHITE)
  e.control.update()
'''
    # 注意缩进，insert_target 是函数定义头部，我们需要插在它下面
    # 实际上这个 handle_hover 应该定义在 build_backup_page 内部
    # 让我更安全地找到它内部的 `def do_backup` 前面插入
    pass 
    
  # 我们直接重写这一段的核心逻辑，保证不出错
  # 找到 grid_cards 的循环
  old_card_code = r'grid_cards\.append\(\s*ft\.Container\(\s*content=ft\.Row\(\[.*?\]\),\s*width=130,\s*height=55,\s*bgcolor=ft\.Colors\.with_opacity\(0\.08,\s*ft\.Colors\.WHITE\),\s*border=ft\.border\.all\(1,\s*ft\.Colors\.with_opacity\(0\.3,\s*ft\.Colors\.WHITE\)\),\s*border_radius=10,\s*alignment=ft\.alignment\.center,\s*on_click=lambda e,\s*name=p_name:\s*do_backup\(name\),\s*on_hover=lambda e:\s*e\.control\.update\(bgcolor=.*?\)\s*\)\s*\)'
  
  # 这里为了绝对安全，我们提取出整个循环并替换
  pattern = r'  grid_cards = \[\]\n  for p_name, p_icon in partitions_info:\n    grid_cards.append\(\n      ft\.Container\(\n        content=ft\.Row\(\[\n          ft\.Icon\(p_icon, color=theme_color, size=20\),\n          ft\.Text\(p_name, size=14, weight=ft\.FontWeight\.BOLD, color="white", font_family="MiSans"\)\n        \], alignment=ft\.MainAxisAlignment\.CENTER\),\n        width=130,\n        height=55,\n        bgcolor=ft\.Colors\.with_opacity\(0\.08, ft\.Colors\.WHITE\),\n        border=ft\.border\.all\(1, ft\.Colors\.with_opacity\(0\.3, ft\.Colors\.WHITE\)\),\n        border_radius=10,\n        alignment=ft\.alignment\.center,\n        on_click=lambda e, name=p_name: do_backup\(name\),\n        on_hover=lambda e: e\.control\.update\(bgcolor=.*?\)\n      \)\n    \)'

  new_card_code = '''  grid_cards = []
  for p_name, p_icon in partitions_info:
    grid_cards.append(
      ft.Container(
        content=ft.Row([
          ft.Icon(p_icon, color=theme_color, size=20),
          ft.Text(p_name, size=14, weight=ft.FontWeight.BOLD, color="white", font_family="MiSans")
        ], alignment=ft.MainAxisAlignment.CENTER),
        width=130,
        height=55,
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
        border_radius=10,
        alignment=ft.alignment.center,
        on_click=lambda e, name=p_name: do_backup(name),
        on_hover=handle_hover
      )
    )'''
  
  # 因为正则可能匹配不到极小的缩进差异，如果没匹配到，我们直接在这里把 handle_hover 函数注入进去
  content = re.sub(pattern, new_card_code, content)
  
  # 强行把 handle_hover 函数塞进 build_backup_page 的 def do_backup 前面
  if "def handle_hover(e):" not in content:
    content = content.replace(
      "  def do_backup(part_name):",
      "  def handle_hover(e):\n    e.control.bgcolor = ft.Colors.with_opacity(0.2, theme_color) if e.data == \"true\" else ft.Colors.with_opacity(0.08, ft.Colors.WHITE)\n    e.control.update()\n\n  def do_backup(part_name):"
    )
    print("✅ 已手动插入 handle_hover 函数！")

  with open(backup_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ pages/backup.py 的悬停事件已修复，不再报 update 参数错误！")
else:
  print("❌ 找不到 pages/backup.py")