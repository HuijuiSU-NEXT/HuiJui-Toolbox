# fix_image_src_bug.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 找到壁纸层的定义代码
old_wallpaper = '''        if os.path.exists(bg_image):
            wallpaper = ft.Container(image_src="custom_wallpaper.jpg", image_fit=ft.ImageFit.COVER, expand=True)
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)'''

# 使用 DecorationImage 的正确写法
new_wallpaper = '''        if os.path.exists(bg_image):
            wallpaper = ft.Container(
                image=ft.DecorationImage(src="custom_wallpaper.jpg", fit=ft.ImageFit.COVER),
                expand=True
            )
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)'''

if old_wallpaper in content:
    content = content.replace(old_wallpaper, new_wallpaper)
    print("✅ 成功将 image_src 替换为 DecorationImage！")
else:
    # 如果没匹配到完全一样的字符串，尝试用正则或更宽松的方式查找并替换
    # 查找 wallpaper = ft.Container(...image_src...)
    pattern = r'wallpaper = ft\.Container\([^)]*image_src="[^"]*"[^)]*\)'
    match = re.search(pattern, content)
    if match:
        # 构造新的正确写法
        new_line = 'wallpaper = ft.Container(image=ft.DecorationImage(src="custom_wallpaper.jpg", fit=ft.ImageFit.COVER), expand=True)'
        content = content[:match.start()] + new_line + content[match.end():]
        print("✅ 通过正则匹配并修复了 image_src！")
    else:
        print("⚠️ 未找到壁纸定义代码，可能已被修改。")

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完成！请重新运行 python main_final.py")