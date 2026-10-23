# fix_final_image.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 修复 update_wallpaper_hot 的加载逻辑，去掉容易失败的 ?t=xxx 参数
old_hot = '''    def update_wallpaper_hot():
        """更新底层的原生 Image 控件"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 加上时间戳破除 Flet 的图片缓存
            src = f"/{os.path.basename(latest)}?t={int(time.time())}"
            bg_image.src = src
            bg_image.visible = True
            print(f"🖼️ 已更新动态背景: {src}")
        else:
            bg_image.visible = False
            print("🧹 未找到壁纸文件，清空背景")
        bg_image.update()'''

new_hot = '''    def update_wallpaper_hot():
        """更新底层的原生 Image 控件"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 直接用文件名，不加参数
            src = os.path.basename(latest)
            bg_image.src = src
            bg_image.visible = True
            print(f"🖼️ 已更新背景: {src}")
        else:
            bg_image.visible = False
            bg_image.src = None
            print("🧹 未找到壁纸文件，清空背景")
        bg_image.update()'''

content = content.replace(old_hot, new_hot)

# 2. 为 Image 增加 src_base64 避坑（如果是静态图，base64加载更稳）
# 保持简单，直接使用 src 是最符合 Flet 设计的方式

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 终极图片加载逻辑已注入！")