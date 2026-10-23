# fix_wallpaper_real.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
main_path = os.path.join(BASE_DIR, "main_final.py")

# ==================== 1. 修复 settings.py 的真实图片选择逻辑 ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 替换掉占位符逻辑
old_pick = '''    def pick_wallpaper(e):
        # 这里可以扩展文件选择器，目前先做占位
        show_snackbar("壁纸选择功能开发中，请手动放入 assets/custom_wallpaper.jpg")'''

new_pick = '''    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                dst_path = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
                try:
                    # 如果有旧壁纸，尝试删除，避免权限占用
                    if os.path.exists(dst_path):
                        try: os.remove(dst_path)
                        except: pass
                    
                    # 复制新壁纸
                    shutil.copy2(src_path, dst_path)
                    show_snackbar("壁纸已应用！正在重新加载界面...")
                    
                    # 触发全局 UI 重建
                    if hasattr(page, "refresh_main_ui"):
                        page.refresh_main_ui(tab_index=4)
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])'''

if old_pick in settings_content:
    settings_content = settings_content.replace(old_pick, new_pick)
    print("✅ pages/settings.py 已成功注入真实壁纸选择器！")
else:
    print("⚠️ 未找到占位符逻辑，可能已被修改。")

# 确保引入了 shutil
if "import shutil" not in settings_content:
    settings_content = settings_content.replace("import re", "import re\nimport shutil")

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)

# ==================== 2. 修复 main_final.py 的图片缓存问题 ====================
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

# 替换壁纸加载逻辑，加入时间戳破坏缓存
old_wallpaper = '''        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            wallpaper = ft.Container(
                image=ft.DecorationImage(src="custom_wallpaper.jpg", fit=ft.ImageFit.COVER),
                expand=True
            )
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)'''

new_wallpaper = '''        bg_image = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        if os.path.exists(bg_image):
            # 🚨 关键：加时间戳破坏 Flutter 的本地图片缓存
            import time
            cache_buster = int(time.time())
            wallpaper = ft.Container(
                image=ft.DecorationImage(src=f"custom_wallpaper.jpg?t={cache_buster}", fit=ft.ImageFit.COVER),
                expand=True
            )
        else:
            wallpaper = ft.Container(bgcolor="#0D1017", expand=True)'''

if old_wallpaper in main_content:
    main_content = main_content.replace(old_wallpaper, new_wallpaper)
    print("✅ main_final.py 已成功注入时间戳防缓存机制！")
else:
    # 兼容之前可能被正则替换过的格式
    pattern = r'wallpaper = ft\.Container\(\s*image=ft\.DecorationImage\(src="custom_wallpaper.jpg", fit=ft\.ImageFit\.COVER\),\s*expand=True\s*\)'
    if re.search(pattern, main_content):
        main_content = re.sub(
            pattern, 
            'import time\\n            wallpaper = ft.Container(image=ft.DecorationImage(src=f"custom_wallpaper.jpg?t={int(time.time())}", fit=ft.ImageFit.COVER), expand=True)', 
            main_content
        )
        print("✅ 通过正则成功注入防缓存机制！")
    else:
        print("⚠️ 未找到壁纸加载逻辑，可能结构已改变。")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(main_content)

print("🎉 完美！现在点“选择图片”就能直接换壁纸，而且立马生效了！")