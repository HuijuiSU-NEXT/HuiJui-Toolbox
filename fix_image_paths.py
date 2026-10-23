# fix_image_paths.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# 1. 修复 main_final.py 里的所有相对路径
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 修复右上角 Logo
content = content.replace('ft.Image(src="logo.png"', 'ft.Image(src="/logo.png"')

# 修复动态壁纸加载
content = content.replace('bg_image.src = src', 'bg_image.src = f"/{src}"')
content = content.replace('bg_image.src = "default_wallpaper.gif"', 'bg_image.src = "/default_wallpaper.gif"')

# 如果是其他图片(如果有)
content = content.replace('src="logo.ico"', 'src="/logo.ico"')

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 的图片路径已强制补全 `/`！")

# 2. 修复 settings.py 里可能的路径问题 (比如刚选完图刷新)
with open(settings_path, "r", encoding="utf-8") as f:
    s_content = f.read()

# 确保自定义壁纸加载逻辑里也没有遗漏
if 'os.path.basename(latest)' in s_content:
    pass # 这里在 main_final.py 已经统一处理了

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(s_content)

print("🎉 修复完毕！请运行 python main_final.py")