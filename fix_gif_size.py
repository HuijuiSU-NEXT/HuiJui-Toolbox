# fix_gif_size.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 在 main_final.py 中，强制给 Image 控件加全屏宽高
old_bg = '''    bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
    bg_layer = ft.Container(content=bg_image, expand=True, bgcolor="#0D1017")
    
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    
    # 🚨 关键：这里强制设置 expand=True，不设死宽高，让它撑满
    main_stack = ft.Stack([bg_layer, main_container], expand=True)'''

new_bg = '''    # 🚨 终极硬塞：强制给 Image 和包裹层指定宽高
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER, 
        expand=True, 
        width=1440, 
        height=900, 
        visible=False
    )
    bg_layer = ft.Container(
        content=bg_image, 
        expand=True, 
        width=1440, 
        height=900, 
        bgcolor="#0D1017"
    )
    
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    
    main_stack = ft.Stack([bg_layer, main_container], expand=True)'''

if old_bg in content:
    content = content.replace(old_bg, new_bg)
    print("✅ 已在 main_final.py 中强制锁定背景为 1440x900！")
else:
    print("⚠️ 未找到精确匹配的背景代码，尝试正则替换...")
    content = re.sub(r'    bg_image = ft\.Image.*?main_stack = ft\.Stack\(\[bg_layer, main_container\], expand=True\)', new_bg, content, flags=re.DOTALL)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新运行 python main_final.py 并重新选一次 GIF 壁纸。")