# fix_bg_layer_error.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 替换掉报错的背景定义代码
old_bg = '''    # 🚨 统一使用 ft.Image 作为背景底图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    # 加一个深层底色兜底
    bg_layer.bgcolor = "#0D1017"'''

new_bg = '''    # 🚨 统一使用 ft.Image 作为背景底图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False,
        bgcolor="#0D1017" # 直接给图片加底色，防止黑屏
    )'''

if old_bg in content:
    content = content.replace(old_bg, new_bg)
    print("✅ 成功移除了导致报错的 bg_layer.bgcolor 赋值！")
else:
    print("⚠️ 未找到精确匹配的旧代码，尝试兜底替换...")
    # 兜底：直接把报错的那行删掉
    content = content.replace("bg_layer.bgcolor = \"#0D1017\"", "")

# 2. 顺便确保 page 可以正常更新
if "main_container.content = build_main_ui()" not in content:
    content = content.replace(
        "    else:\n        build_main_ui()",
        "    else:\n        main_container.content = build_main_ui()\n        page.update()"
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py")