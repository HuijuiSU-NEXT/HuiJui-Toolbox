# fix_ultimate_perfect.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 重写 settings.py ====================
settings_code = '''import flet as ft
import os
import re
import glob
import shutil
import time
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
    state = {
        "theme_color": CFG.get("theme_color", "#39C5BB"),
        "ui_material": CFG.get("ui_material", "default"),
        "card_opacity": CFG.get("card_opacity", 0.15),
        "blur_radius": CFG.get("blur_radius", 10)
    }

    wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
    has_wallpaper = len(wallpaper_files) > 0

    def show_snackbar(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=theme_color)
        page.snack_bar.open = True
        page.update()

    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                try:
                    is_gif = src_path.lower().endswith((".gif", ".mp4", ".webm", ".mov"))
                    if is_gif:
                        new_filename = f"wallpaper_{int(time.time())}.gif"
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)
                        # 使用 ffmpeg 将视频转为低分辨率 GIF
                        ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
                        cmd = [ffmpeg_exe, "-i", src_path, "-vf", "scale=720:450:force_original_aspect_ratio=increase,crop=720:450,fps=15", "-pix_fmt", "rgb24", "-y", new_filepath]
                        subprocess.run(cmd, check=True, capture_output=True)
                    else:
                        from PIL import Image
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
                        new_filename = f"wallpaper_{int(time.time())}.jpg"
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)

                    # 清理旧图
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*")) + glob.glob(os.path.join(BASE_DIR, "assets", "custom_wallpaper.*"))
                    for old_f in old_files:
                        if os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass
                    
                    if not is_gif:
                        img.save(new_filepath, quality=95)
                    
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    
                    if hasattr(page, "update_wallpaper_hot"):
                        page.update_wallpaper_hot()
                        
                    show_snackbar("壁纸已应用！")
                    page.update()
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"])

    def clear_wallpaper(e):
        files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*")) + glob.glob(os.path.join(BASE_DIR, "assets", "custom_wallpaper.*"))
        cleared = False
        for f in files:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    cleared = True
                    print(f"已物理删除: {f}")
                except Exception as ex: 
                    print(f"删除失败: {f} - {ex}")
                
        if cleared:
            show_snackbar("壁纸已清除。")
            card_step2.visible = False
            card_step3.visible = False
            card_step4.visible = False
            if hasattr(page, "update_wallpaper_hot"):
                page.update_wallpaper_hot()
            page.update()
        else:
            show_snackbar("当前没有自定义壁纸。")

    # 颜色滑块等UI
    color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))
    color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])

    def apply_color(e):
        hex_val = color_input.value.strip()
        if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
            state["theme_color"] = hex_val
            color_preview.bgcolor = hex_val
            CFG.set("theme_color", hex_val)
            CFG.save()
            show_snackbar("颜色已应用，正在刷新...")
            if hasattr(page, "refresh_main_ui"):
                page.refresh_main_ui(tab_index=4)

    material_dropdown = ft.Dropdown(
        label="UI 材质风格", value=state["ui_material"], width=300,
        bgcolor="#1A233A", color="white",
        options=[
            ft.dropdown.Option("default", "默认 (纯色/清晰)"),
            ft.dropdown.Option("frosted", "毛玻璃 (半透明)"),
            ft.dropdown.Option("liquid", "液态玻璃 (晶莹剔透)"),
        ],
        on_change=lambda e: apply_material(e.control.value)
    )

    def apply_material(val):
        state["ui_material"] = val
        CFG.set("ui_material", val)
        CFG.save()
        show_snackbar(f"材质已切换: {val}")
        if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)

    blur_slider = ft.Slider(min=0, max=40, divisions=40, value=state["blur_radius"], active_color=theme_color, label="{value}")
    def on_blur_change(e):
        state["blur_radius"] = int(blur_slider.value)
        CFG.set("blur_radius", int(blur_slider.value))
        CFG.save()
        if hasattr(page, "update_overlay_blur"):
            page.update_overlay_blur(int(blur_slider.value))
    blur_slider.on_change = on_blur_change
    blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

    opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value}")
    def on_opacity_change(e):
        state["card_opacity"] = opacity_slider.value
        CFG.set("card_opacity", opacity_slider.value)
        CFG.save()
        page.refresh_main_ui(tab_index=4)
    opacity_slider.on_change = on_opacity_change

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
            ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white", disabled=not has_wallpaper)
        ])
    ])
    
    card_step2 = make_card("第二步：主题色强化", ft.Icons.COLOR_LENS, [
        ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")])
    ])
    card_step2.visible = has_wallpaper

    card_step3 = make_card("第三步：UI 材质风格", ft.Icons.LAYERS, [
        ft.Text("选择全局界面渲染材质，切换后立即生效。", size=12, color=ft.Colors.GREY_400),
        ft.Row([material_dropdown])
    ])
    card_step3.visible = has_wallpaper

    card_step4 = make_card("第四步：视觉特效微调", ft.Icons.AUTO_AWESOME, [
        ft.Row([
            ft.Column([ft.Text("全局模糊度", size=14, color="white"), ft.Text("调节毛玻璃/液态玻璃的模糊程度", size=11, color=ft.Colors.GREY_500)]),
            ft.Container(expand=True),
            ft.Container(content=blur_slider, width=300)
        ]),
        ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=15),
        ft.Row([
            ft.Column([ft.Text("卡片透明度", size=14, color="white"), ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)]),
            ft.Container(expand=True),
            ft.Container(content=opacity_slider, width=300)
        ])
    ])
    card_step4.visible = has_wallpaper

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            ft.Column([card_step1, ft.Container(height=10), card_step2, ft.Container(height=10), card_step3, ft.Container(height=10), card_step4], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True),
        expand=True, padding=20
    )
'''

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_code)
print("✅ settings.py 终极重写完毕！")


# ==================== 2. 修复 main_final.py 缩水问题 ====================
with open(main_path, "r", encoding="utf-8") as f:
    m_content = f.read()

# 1. 强制撑满 nav_container
m_content = m_content.replace(
    "nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style[\"nav_bg\"])",
    "nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style[\"nav_bg\"], expand=True)"
)

# 2. 强制撑满 side_panel
m_content = m_content.replace(
    "side_panel = ft.Container(\n            width=320,",
    "side_panel = ft.Container(\n            expand=True,\n            width=320,"
)
if "expand=True,\n            width=320" not in m_content:
    m_content = m_content.replace("width=320, bgcolor=page.ui_style[\"side_bg\"],", "expand=True, width=320, bgcolor=page.ui_style[\"side_bg\"],")

# 3. 确保最终 UI 有 expand=True
m_content = m_content.replace(
    "return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)",
    "return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)"
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(m_content)
print("✅ main_final.py 容器撑满属性已强化！")