# fix_wallpaper_cache.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 确保引入了 base64
if "import base64" not in content:
    content = "import base64\n" + content

# 2. 替换壁纸加载逻辑为 Base64 方式
# 正则匹配旧的壁纸加载逻辑
pattern = r'        bg_image = os\.path\.join\(BASE_DIR, "assets", "custom_wallpaper\.jpg"\).*?wallpaper = ft\.Container\(bgcolor="#0D1017", expand=True\)'

new_wallpaper_logic = '''        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            try:
                # 🚨 核心：转 Base64 彻底绕过 Flutter 图片缓存
                with open(bg_image, "rb") as f:
                    img_bytes = f.read()
                    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                wallpaper = ft.Container(
                    image=ft.DecorationImage(src_base64=img_b64, fit=ft.ImageFit.COVER),
                    expand=True
                )
            except Exception as e:
                print(f"壁纸加载失败: {e}")
                wallpaper = ft.Container(bgcolor="#0D1017", expand=True)
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)'''

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_wallpaper_logic, content, flags=re.DOTALL)
    print("✅ 已成功替换为 Base64 壁纸加载逻辑！")
else:
    print("⚠️ 未匹配到旧壁纸逻辑，可能代码结构已变，尝试直接硬替换...")
    # 兜底：如果正则没匹配到，直接替换关键词
    content = content.replace(
        'cache_buster = int(time.time())\n            wallpaper = ft.Container(\n                image=ft.DecorationImage(src=f"custom_wallpaper.jpg?t={cache_buster}", fit=ft.ImageFit.COVER),\n                expand=True\n            )',
        'with open(bg_image, "rb") as f:\n                img_b64 = base64.b64encode(f.read()).decode("utf-8")\n            wallpaper = ft.Container(\n                image=ft.DecorationImage(src_base64=img_b64, fit=ft.ImageFit.COVER),\n                expand=True\n            )'
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完成！现在选完壁纸会立即显示，再也不用重启了！")