# fix_wallpaper_ultimate.py
import os
import shutil
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 重写 main_final.py 的底层图片加载 ====================
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 替换背景层的构建逻辑
old_bg = '''    # 🚨 核心：使用纯静态的 ft.Image 控件做背景，而不是 DecorationImage
    bg_image_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
    
    # 缓存破坏机制
    timestamp = int(time.time())
    if os.path.exists(bg_image_path):
        bg_src = f"/custom_wallpaper.jpg?t={timestamp}" 
    else:
        bg_src = None

    bg_image = ft.Image(
        src=bg_src,
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=bool(bg_src)
    )'''

new_bg = '''    # 🚨 核心：寻找 assets 目录下的任何 wallpaper_*.jpg
    import glob
    wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
    bg_src = None
    if wallpaper_files:
        # 取最新的一张
        latest_wp = max(wallpaper_files, key=os.path.getctime)
        # 提取相对 assets 的路径
        bg_src = os.path.basename(latest_wp)

    bg_image = ft.Image(
        src=bg_src,
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=bool(bg_src)
    )'''

content = content.replace(old_bg, new_bg)

# 替换热更新逻辑
old_hot = '''    def update_wallpaper_hot():
        bg_image_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image_path):
            new_ts = int(time.time())
            bg_image.src = f"/custom_wallpaper.jpg?t={new_ts}"
            bg_image.visible = True
        else:
            bg_image.visible = False
        bg_image.update()'''

new_hot = '''    def update_wallpaper_hot():
        import glob
        wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
        if wallpaper_files:
            latest_wp = max(wallpaper_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest_wp)
            bg_image.visible = True
        else:
            bg_image.visible = False
        bg_image.update()'''

content = content.replace(old_hot, new_hot)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 已完成动态文件名加载改造！")


# ==================== 2. 重写 settings.py 的图片裁剪与保存逻辑 ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 匹配整个 pick_wallpaper 函数
pattern = r"    def pick_wallpaper\(e\):.*?file_picker\.pick_files\(allowed_extensions=\[\"jpg\", \"jpeg\", \"png\", \"webp\"\]\)"
new_pick = '''    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                try:
                    from PIL import Image
                    import time
                    import glob
                    
                    # 1. 读取原图并裁剪
                    img = Image.open(src_path)
                    w, h = img.size
                    target_ratio = 16 / 10
                    
                    if w / h > target_ratio:
                        new_w = int(h * target_ratio)
                        left = (w - new_w) // 2
                        img = img.crop((left, 0, left + new_w, h))
                    elif w / h < target_ratio:
                        new_h = int(w / target_ratio)
                        top = (h - new_h) // 2
                        img = img.crop((0, top, w, top + new_h))
                        
                    img = img.resize((1440, 900), Image.Resampling.LANCZOS).convert("RGB")
                    
                    # 2. 生成全新的文件名 (时间戳防缓存)
                    new_filename = f"wallpaper_{int(time.time())}.jpg"
                    new_filepath = os.path.join(BASE_DIR, "assets", new_filename)
                    
                    # 3. 清理旧的壁纸
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
                    old_files.append(os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg"))
                    for old_f in old_files:
                        if os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass
                            
                    # 4. 保存新图
                    img.save(new_filepath, quality=95)
                    
                    # 5. 动态解锁 UI
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    
                    # 6. 瞬间热更新底层壁纸，绝不重启！
                    if hasattr(page, "update_wallpaper_hot"):
                        page.update_wallpaper_hot()
                        
                    show_snackbar("壁纸已智能裁剪并应用！")
                    page.update()
                    
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])'''

settings_content = re.sub(pattern, new_pick, settings_content, flags=re.DOTALL)

# 修复清除壁纸的逻辑
old_clear = '''    def clear_wallpaper(e):
        if os.path.exists(wallpaper_path):
            try:
                os.remove(wallpaper_path)
                show_snackbar("壁纸已清除，高级材质已锁定。")
                
                # 动态隐藏
                card_step2.visible = False
                card_step3.visible = False
                card_step4.visible = False
                page.update()
                if hasattr(page, "update_wallpaper_hot"):
                    page.update_wallpaper_hot()
            except Exception as ex:
                show_snackbar(f"清除失败: {ex}")'''

new_clear = '''    def clear_wallpaper(e):
        import glob
        files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
        files.append(os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg"))
        
        cleared = False
        for f in files:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    cleared = True
                except: pass
                
        if cleared:
            show_snackbar("壁纸已清除，高级材质已锁定。")
            card_step2.visible = False
            card_step3.visible = False
            card_step4.visible = False
            if hasattr(page, "update_wallpaper_hot"):
                page.update_wallpaper_hot()
            page.update()
        else:
            show_snackbar("当前没有自定义壁纸。")'''

settings_content = settings_content.replace(old_clear, new_clear)

# 在顶部确保有 import re
if "import re" not in settings_content:
    settings_content = settings_content.replace("import os", "import os\nimport re")
if "import glob" not in settings_content:
    settings_content = settings_content.replace("import os", "import os\nimport glob")

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)

print("🎉 完美！壁纸已改为时间戳动态文件名，选图后瞬间无缓存加载，再也不用重启了！")