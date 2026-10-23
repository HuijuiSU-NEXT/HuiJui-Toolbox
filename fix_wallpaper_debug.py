# fix_wallpaper_debug.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# 1. 重写 settings.py（加入详细错误打印）
settings_code = '''import flet as ft
import os
import re
import glob
import shutil
import time
import subprocess
from core_api import CFG
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
    state = {
        "theme_color": CFG.get("theme_color", "#39C5BB"),
        "ui_material": CFG.get("ui_material", "default"),
        "card_opacity": CFG.get("card_opacity", 0.15),
        "blur_radius": CFG.get("blur_radius", 10)
    }

    wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    has_wallpaper = len(wallpaper_files) > 0

    def show_snackbar(msg, color=ft.Colors.GREEN):
        print(f"[UI提示] {msg}")
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            src_path = e.files[0].path
            print(f"\\n[选择文件] 已选中: {src_path}")
            
            try:
                ext = os.path.splitext(src_path)[1].lower()
                new_filename = f"wallpaper_{int(time.time())}{ext if ext in ['.gif', '.mp4'] else '.jpg'}"
                new_filepath = os.path.join(BASE_DIR, "assets", new_filename)

                if ext in ['.mp4', '.webm', '.mov', '.gif']:
                    # 视频/GIF 走 FFmpeg 转码
                    ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
                    if not os.path.exists(ffmpeg_exe):
                        raise Exception("找不到 FFmpeg，请先运行 setup_ffmpeg_fast.py")
                    
                    # 输出为 GIF 或直接复制
                    if ext == '.gif':
                        shutil.copy2(src_path, new_filepath)
                    else:
                        new_filepath = new_filepath.replace(ext, ".gif")
                        cmd = [ffmpeg_exe, "-i", src_path, "-vf", "scale=720:450:force_original_aspect_ratio=increase,crop=720:450,fps=15", "-pix_fmt", "rgb24", "-y", new_filepath]
                        print(f"[FFmpeg] 开始转码...")
                        subprocess.run(cmd, check=True, capture_output=True)
                        print(f"[FFmpeg] 转码成功: {new_filepath}")
                else:
                    # 静态图走 PIL 裁剪
                    img = Image.open(src_path).convert("RGB")
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
                    img = img.resize((1440, 900), Image.Resampling.LANCZOS)
                    img.save(new_filepath, quality=95)
                    print(f"[PIL] 图片裁剪成功: {new_filepath}")

                # 清理旧壁纸
                old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
                for old_f in old_files:
                    if old_f != new_filepath and os.path.exists(old_f):
                        try: os.remove(old_f)
                        except: pass
                
                # 刷新 UI
                if hasattr(page, "update_wallpaper_hot"):
                    page.update_wallpaper_hot()
                if hasattr(page, "refresh_main_ui"):
                    page.refresh_main_ui(tab_index=4)
                    
                show_snackbar("壁纸已应用！")
                
            except subprocess.CalledProcessError as e:
                show_snackbar("FFmpeg 转码失败", ft.Colors.RED)
                print(f"[FFmpeg 错误] {e.stderr}")
            except Exception as ex:
                show_snackbar(f"应用失败: {ex}", ft.Colors.RED)
                print(f"[异常] {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"])

    def clear_wallpaper(e):
        files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        for f in files:
            try: os.remove(f)
            except: pass
        if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)
        show_snackbar("壁纸已清除。")

    # 样式 UI
    color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))
    color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])
    def apply_color(e):
        hex_val = color_input.value.strip()
        if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
            state["theme_color"] = hex_val
            color_preview.bgcolor = hex_val
            CFG.set("theme_color", hex_val)
            CFG.save()
            show_snackbar("颜色已应用")
            if hasattr(page, "refresh_main_ui"): page.refresh_main_ui(tab_index=4)
        else:
            color_input.error_text = "格式错误"
        page.update()

    material_dropdown = ft.Dropdown(label="UI 材质", value=state["ui_material"], width=300, bgcolor="#1A233A", color="white", options=[ft.dropdown.Option("default", "默认"), ft.dropdown.Option("frosted", "毛玻璃"), ft.dropdown.Option("liquid", "液态玻璃")], on_change=lambda e: apply_material(e.control.value))
    def apply_material(val):
        state["ui_material"] = val
        CFG.set("ui_material", val)
        CFG.save()
        if hasattr(page, "refresh_main_ui"): page.refresh_main_ui(tab_index=4)

    blur_slider = ft.Slider(min=0, max=40, divisions=40, value=state["blur_radius"], active_color=theme_color, label="{value}")
    blur_slider.on_change = lambda e: CFG.set("blur_radius", int(e.control.value))
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value}")
    opacity_slider.on_change = lambda e: CFG.set("card_opacity", e.control.value)
    opacity_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

    def make_card(title, icon, content_list):
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, color=theme_color, size=20), ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white")]),
                ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE), height=10),
                *content_list
            ], spacing=15),
            bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
            border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
            border_radius=15, padding=20
        )

    card_step1 = make_card("第一步：壁纸引擎", ft.Icons.IMAGE, [
        ft.Row([
            ft.Column([ft.Text("自定义壁纸", size=14, color="white"), ft.Text("请先设置壁纸以解锁高级材质" if not has_wallpaper else "已设置壁纸，可随时更换", size=11, color=ft.Colors.GREY_500)]),
            ft.Container(expand=True),
            ft.ElevatedButton("选择图片", icon=ft.Icons.UPLOAD, on_click=pick_wallpaper, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"),
            ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white")
        ])
    ])
    card_step2 = make_card("第二步：主题色", ft.Icons.COLOR_LENS, [ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")])])
    card_step3 = make_card("第三步：UI 材质", ft.Icons.LAYERS, [ft.Text("选择全局材质", size=12, color=ft.Colors.GREY_400), ft.Row([material_dropdown])])
    card_step4 = make_card("第四步：视觉特效", ft.Icons.AUTO_AWESOME, [
        ft.Row([ft.Column([ft.Text("全局模糊度", size=14, color="white")]), ft.Container(expand=True), ft.Container(content=blur_slider, width=300)]),
        ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=15),
        ft.Row([ft.Column([ft.Text("卡片透明度", size=14, color="white")]), ft.Container(expand=True), ft.Container(content=opacity_slider, width=300)])
    ])

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            ft.Container(height=10),
            ft.Column([card_step1, ft.Container(height=10), card_step2, ft.Container(height=10), card_step3, ft.Container(height=10), card_step4], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True),
        expand=True, padding=20
    )
'''

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_code)
print("✅ settings.py 已重写，加入全链路日志！")

# 2. 修复 main_final.py 的背景更新逻辑（强制使用 page.decoration 且加时间戳）
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

old_hot = '''    def update_wallpaper_hot():
        """直接调用系统级背景，避开任何 UI 层的尺寸计算 bug"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统级背景: {src}")
        else:
            page.decoration = None
            print("🧹 已彻底清空背景")
            
        page.update()'''

new_hot = '''    def update_wallpaper_hot():
        """系统级背景终极更新法"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统级背景: {src}")
        else:
            page.decoration = None
            print("🧹 已彻底清空背景")
            
        page.update()'''

content = content.replace(old_hot, new_hot)

# 确保 page.decoration 和 page.update 在一起，且强制刷新
with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 壁纸逻辑已焊死！")