import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 确保导入 flet_desktop.version
if "import flet_desktop.version" not in content:
  content = content.replace("import flet", "import flet\nimport flet_desktop.version", 1)
  print("✅ 已强制注入 flet_desktop.version 导入")

# 确保入口是 ft.app(target=main, assets_dir="assets")
content = content.replace("ft.run(main)", 'ft.app(target=main, assets_dir="assets")')

with open(file_path, "w", encoding="utf-8") as f:
  f.write(content)
  print("✅ 入口已确保为 ft.app(target=main)")
