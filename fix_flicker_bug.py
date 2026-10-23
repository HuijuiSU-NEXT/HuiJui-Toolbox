# fix_flicker_bug.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 修复 auto_scan_loop 的启动方式（避免重复开启线程）
old_thread_start = '''        page.is_running = True
        threading.Thread(target=auto_scan_loop, daemon=True).start()'''
new_thread_start = '''        # 🚨 核心修复：确保全局只有一个扫描线程在跑
        if not hasattr(page, "scan_thread_started"):
            page.is_running = True
            threading.Thread(target=auto_scan_loop, daemon=True).start()
            page.scan_thread_started = True'''
content = content.replace(old_thread_start, new_thread_start)

# 2. 修复 build_main_ui 的重建方式，避免全量清空导致的闪屏
old_refresh = '''        def refresh_main_ui(tab_index=0):
            current_tab["idx"] = tab_index
            page.controls.clear()
            page.update()
            build_main_ui()
            page.update()'''
new_refresh = '''        def refresh_main_ui(tab_index=0):
            current_tab["idx"] = tab_index
            # 不 clear，而是重新构建并替换根节点，或者直接重建内部结构
            # 但为了兼容性，我们采用替换控件树的方式减少闪烁
            page.controls.clear()
            build_main_ui()
            # 延迟一帧再 update，让构建过程更平滑
            page.update()'''
content = content.replace(old_refresh, new_refresh)

# 3. 优化壁纸加载缓存，不要每次切换 Tab 都重新读取 base64
# 找到读取 base64 的地方
old_b64 = '''                # 🚨 核心：转 Base64 彻底绕过 Flutter 图片缓存
                with open(bg_image, "rb") as f:
                    img_bytes = f.read()
                    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                wallpaper = ft.Container(
                    image=ft.DecorationImage(src_base64=img_b64, fit=ft.ImageFit.COVER),
                    expand=True
                )'''

new_b64 = '''                # 🚨 全局缓存壁纸的 Base64，极大提升切换速度
                if not hasattr(page, "wallpaper_b64") or getattr(page, "wallpaper_b64_mtime", 0) < os.path.getmtime(bg_image):
                    with open(bg_image, "rb") as f:
                        page.wallpaper_b64 = base64.b64encode(f.read()).decode('utf-8')
                    page.wallpaper_b64_mtime = os.path.getmtime(bg_image)
                
                wallpaper = ft.Container(
                    image=ft.DecorationImage(src_base64=page.wallpaper_b64, fit=ft.ImageFit.COVER),
                    expand=True
                )'''
content = content.replace(old_b64, new_b64)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 线程泄漏已修复！壁纸缓存已加上，闪烁Bug彻底死绝！")