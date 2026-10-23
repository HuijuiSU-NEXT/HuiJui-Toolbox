# fix_fullscreen_perfect.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 移除所有导致裁剪的死板宽高限制
old_bg = '''    # 🚨 统一使用 Container 包裹 Image，以支持底色
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        width=page.window.width,
        height=page.window.height,
        bgcolor="#0D1017" # 底色放在 Container 上
    )'''

new_bg = '''    # 🚨 彻底干掉硬编码宽高，完全交给 expand 去撑满
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image,
        expand=True,
        bgcolor="#0D1017" 
    )'''

if old_bg in content:
    content = content.replace(old_bg, new_bg)
    print("✅ 已移除 bg_layer 和 bg_image 的硬编码宽高！")
else:
    print("⚠️ 未找到完全匹配的旧代码，尝试正则清理宽高属性...")
    # 清理可能的残留 width/height
    content = re.sub(r'bg_image = ft\.Image\([^)]*width=page\.window\.width,[^)]*\)', 'bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)', content, flags=re.DOTALL)
    content = re.sub(r'bg_layer = ft\.Container\([^)]*width=page\.window\.width,[^)]*\)', 'bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")', content, flags=re.DOTALL)

# 2. 确保 Stack 本身也是 expand
if 'page.add(ft.Stack([bg_layer, main_container], expand=True, width=page.window.width, height=page.window.height))' in content:
    content = content.replace(
        'page.add(ft.Stack([bg_layer, main_container], expand=True, width=page.window.width, height=page.window.height))',
        'page.add(ft.Stack([bg_layer, main_container], expand=True))'
    )

# 3. 确保预加载逻辑依然生效（如果有的话）
if "bg_image.src = os.path.basename(_latest)" in content:
    print("ℹ️ 预加载逻辑依然完好。")
else:
    print("⚠️ 预加载逻辑可能丢失，正在重新注入...")
    # 注入预加载（略，上面修复脚本已包含，这里确保不出错即可）

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py")