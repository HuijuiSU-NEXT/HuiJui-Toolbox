# fix_image_bgcolor.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 修复导致报错的 ft.Image 定义
old_bg = '''    # 🚨 统一使用 ft.Image 作为背景底图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False,
        bgcolor="#0D1017" # 直接给图片加底色，防止黑屏
    )'''

new_bg = '''    # 🚨 统一使用 Container 包裹 Image，以支持底色
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        bgcolor="#0D1017" # 底色放在 Container 上
    )'''

if old_bg in content:
    content = content.replace(old_bg, new_bg)
    print("✅ 成功修复了 Image 的 bgcolor 参数错误！")
else:
    print("⚠️ 未找到精确匹配的旧代码，尝试正则替换...")
    # 正则兜底：把任何含 bgcolor 的 ft.Image 替换掉
    import re
    content = re.sub(
        r'bg_image = ft\.Image\(\s*fit=ft\.ImageFit\.COVER,\s*expand=True,\s*visible=False,\s*bgcolor="[^"]*"\s*\)',
        '''bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")''',
        content
    )
    print("✅ 已通过正则完成兜底修复！")

# 2. 确保 bg_layer 被正确挂载到页面上
# 检查启动挂载逻辑
if "page.add(ft.Stack([bg_layer, main_container], expand=True))" not in content:
    # 如果之前的补丁把它删了，这里补回来
    content = content.replace(
        "    main_container = ft.Container(expand=True)\n    page.add(main_container)",
        "    main_container = ft.Container(expand=True)\n    page.add(ft.Stack([bg_layer, main_container], expand=True))"
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py")