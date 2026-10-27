# fix_nav_error.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 物理切除报错的非法参数
content = content.replace('unselected_icon_color="#FFFFFF", selected_icon_color=theme_color,', '')
content = content.replace('unselected_icon_color="#FFFFFF",', '')
content = content.replace('selected_icon_color=theme_color,', '')

# 2. 重写 NavigationRail 里的 destinations，给图标强制上色
old_destinations = '''      destinations=[
        ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="控制台"),
        ft.NavigationRailDestination(icon=ft.Icons.FLASH_ON_OUTLINED, selected_icon=ft.Icons.FLASH_ON, label="一键刷机"),
        ft.NavigationRailDestination(icon=ft.Icons.SECURITY_OUTLINED, selected_icon=ft.Icons.SECURITY, label="临时Root"),
        ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="历史"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="个性化"),
      ]'''

new_destinations = '''      destinations=[
        ft.NavigationRailDestination(
          icon=ft.Icon(ft.Icons.DASHBOARD_OUTLINED, color="#FFFFFF"), 
          selected_icon=ft.Icon(ft.Icons.DASHBOARD, color=theme_color), 
          label="控制台"
        ),
        ft.NavigationRailDestination(
          icon=ft.Icon(ft.Icons.FLASH_ON_OUTLINED, color="#FFFFFF"), 
          selected_icon=ft.Icon(ft.Icons.FLASH_ON, color=theme_color), 
          label="一键刷机"
        ),
        ft.NavigationRailDestination(
          icon=ft.Icon(ft.Icons.SECURITY_OUTLINED, color="#FFFFFF"), 
          selected_icon=ft.Icon(ft.Icons.SECURITY, color=theme_color), 
          label="临时Root"
        ),
        ft.NavigationRailDestination(
          icon=ft.Icon(ft.Icons.HISTORY_OUTLINED, color="#FFFFFF"), 
          selected_icon=ft.Icon(ft.Icons.HISTORY, color=theme_color), 
          label="历史"
        ),
        ft.NavigationRailDestination(
          icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, color="#FFFFFF"), 
          selected_icon=ft.Icon(ft.Icons.SETTINGS, color=theme_color), 
          label="个性化"
        ),
      ]'''

if old_destinations in content:
  content = content.replace(old_destinations, new_destinations)
  print("✅ 侧边栏图标颜色已成功修正！未选中纯白，选中主题青！")
else:
  print("⚠️ 未找到精确匹配的 destinations，尝试正则替换...")
  import re
  # 兜底正则，匹配现有的 destinations 块
  pattern = r'      destinations=\[.*?\]'
  content = re.sub(pattern, new_destinations, content, flags=re.DOTALL)
  print("✅ 已通过正则强行替换 destinations 代码块！")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py。")