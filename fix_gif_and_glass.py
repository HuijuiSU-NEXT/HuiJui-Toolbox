# fix_gif_and_glass.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ui_theme_path = os.path.join(BASE_DIR, "ui_theme.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
main_path = os.path.join(BASE_DIR, "main_final.py")

# ==================== 1. 调整 ui_theme.py：降低模糊，提升透光度 ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    
    if material == "frosted":
        # 毛玻璃：降低模糊度，让背景能透出一点轮廓
        return {
            "type": "frosted",
            "overlay_bg": ft.Colors.with_opacity(0.1, "#0D1017"), # 极轻的遮罩
            "overlay_blur": ft.Blur(12, 12, ft.BlurTileMode.MIRROR), # 从 30 降到 12，保留细节
            "nav_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }
    elif material == "liquid":
        # 液态玻璃：极低模糊，增加高光边框，实现晶莹剔透
        return {
            "type": "liquid",
            "overlay_bg": ft.LinearGradient(
                colors=[ft.Colors.with_opacity(0.05, theme_color), ft.Colors.with_opacity(0.2, "#0D1017")]
            ), # 渐变遮罩，让背景有明暗对比
            "overlay_blur": ft.Blur(8, 8, ft.BlurTileMode.MIRROR), # 从 40 降到 8，极具通透感
            "nav_bg": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_border": ft.border.all(2, ft.Colors.with_opacity(0.6, ft.Colors.WHITE)), # 明显的反光边框
            "log_bg": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            "log_color": theme_color
        }
    else:
        return {
            "type": "default",
            "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "overlay_blur": None,
            "nav_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "side_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }

def setup_page_style(page: ft.Page):
    theme_color = CFG.get("theme_color", "#39C5BB")
    page.bgcolor = ft.Colors.TRANSPARENT
    return theme_color
'''
with open(ui_theme_path, "w", encoding="utf-8") as f:
    f.write(ui_theme_code)
print("✅ ui_theme.py 已降低模糊度，质感大提升！")

# ==================== 2. 调整 settings.py：支持上传 GIF ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 修改文件选择器允许 GIF
settings_content = settings_content.replace(
    'file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])',
    'file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp", "gif"])'
)

# 判断如果是 GIF，跳过 PIL 裁剪，直接保存
old_pick_logic = '''                    from PIL import Image
                    
                    # 1. 读取并裁剪
                    img = Image.open(src_path)
                    w, h = img.size
                    target_ratio = 16 / 10
                    
                    if w / h > target_ratio:
                        # 太宽，切两边
                        new_w = int(h * target_ratio)
                        left = (w - new_w) // 2
                        img = img.crop((left, 0, left + new_w, h))
                    elif w / h < target_ratio:
                        # 太高，切上下
                        new_h = int(w / target_ratio)
                        top = (h - new_h) // 2
                        img = img.crop((0, top, w, top + new_h))
                        
                    # 2. 强制缩放到 1440x900 并转为 RGB 防止 png 透明报错
                    img = img.resize((1440, 900), Image.Resampling.LANCZOS).convert("RGB")
                    
                    # 3. 生成带时间戳的新文件名，打破 Flet 缓存
                    new_filename = f"wallpaper_{int(time.time())}.jpg"
                    new_filepath = os.path.join(BASE_DIR, "assets", new_filename)'''

new_pick_logic = '''                    is_gif = src_path.lower().endswith(".gif")
                    
                    if is_gif:
                        # 🚨 如果是动态图，不裁剪，直接拷贝过去
                        new_filename = f"wallpaper_{int(time.time())}.gif"
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)
                        shutil.copy2(src_path, new_filepath)
                    else:
                        from PIL import Image
                        # 静态图正常裁剪
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
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)'''

settings_content = settings_content.replace(old_pick_logic, new_pick_logic)

# 清理旧文件时，也要支持通配符 *.gif
settings_content = settings_content.replace(
    'old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))',
    'old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))'
)

# 点击清除时，也要清理 gif
settings_content = settings_content.replace(
    'files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))',
    'files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))'
)

# 初始检查是否存在
settings_content = settings_content.replace(
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))',
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))'
)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)
print("✅ settings.py 已支持 GIF 动态壁纸！")

# ==================== 3. 调整 main_final.py：支持加载 GIF ====================
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 让底层扫描支持 gif
content = content.replace(
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))',
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))'
)

content = content.replace(
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))',
    'wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))'
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 已支持动态壁纸读取！")

print("🎉 全部修改完毕！请运行 python main_final.py 体验超清材质与动态壁纸！")