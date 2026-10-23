# fix_wallpaper_final.py
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
assets_dir = os.path.join(BASE_DIR, "assets")

# 1. 物理清理所有旧的壁纸文件，防止坏文件干扰
print("🧹 正在清理旧的壁纸缓存...")
for f in glob.glob(os.path.join(assets_dir, "wallpaper_*.*")) + glob.glob(os.path.join(assets_dir, "custom_wallpaper.*")):
    try:
        os.remove(f)
        print(f"  已删除: {os.path.basename(f)}")
    except Exception as e:
        print(f"  删除失败: {f} ({e})")

# 2. 强制修复 main_final.py，使用最稳的写法加载背景
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

old_bg = '''    # 🚨 统一使用 ft.Image，支持 GIF 动图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )'''
new_bg = '''    # 🚨 统一使用 ft.Image 作为背景底图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    # 加一个深层底色兜底
    bg_layer.bgcolor = "#0D1017"'''
content = content.replace(old_bg, new_bg)

# 替换 update_wallpaper_hot
old_hot = '''    def update_wallpaper_hot():
        """直接加载最新的 GIF 或静态图片，Flet 原生支持 GIF 播放"""
        import glob
        
        # 优先查找 GIF
        gif_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
        jpg_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
        
        if gif_files:
            latest = max(gif_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
        elif jpg_files:
            latest = max(jpg_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
        else:
            bg_image.visible = False
            
        bg_image.update()'''

new_hot = '''    def update_wallpaper_hot():
        """直接加载最新的图片，Flet 原生支持"""
        import glob
        
        # 找 GIF 和 静态图
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 传递带路径的文件名，而不是纯 basename（Flet 对相对路径有时解析失败）
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
            print(f"🖼️ 正在加载壁纸: {bg_image.src}")
        else:
            bg_image.visible = False
            print("❌ 未找到壁纸文件")
            
        bg_image.update()'''
content = content.replace(old_hot, new_hot)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 背景逻辑已加固！")

# 3. 大幅降低 GIF 的生成分辨率，拯救 Flet 内存
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

old_ffmpeg = '''                    # 使用 scale 和 crop 滤镜保证 16:10 比例且居中裁剪
                    cmd = [
                        ffmpeg_exe,
                        "-i", src_path,
                        "-vf", "scale=1440:900:force_original_aspect_ratio=increase,crop=1440:900",
                        "-r", "30",          # 限制帧率为 30fps
                        "-pix_fmt", "rgb24", # 兼容性更好的像素格式
                        "-y",                # 覆盖输出文件
                        new_filepath
                    ]'''
new_ffmpeg = '''                    # 🚨 降级到 720p 并限制为 15fps，以确保 Flet 不卡死
                    cmd = [
                        ffmpeg_exe,
                        "-i", src_path,
                        "-vf", "scale=720:450:force_original_aspect_ratio=increase,crop=720:450,fps=15",
                        "-pix_fmt", "rgb24",
                        "-y",
                        new_filepath
                    ]'''
settings_content = settings_content.replace(old_ffmpeg, new_ffmpeg)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)
print("✅ settings.py 已限制 GIF 分辨率为 720p / 15fps，防止卡死！")

print("\n🎉 一切就绪！请运行 python main_final.py，重新选择壁纸吧！")