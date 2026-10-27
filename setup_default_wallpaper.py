# setup_default_wallpaper.py
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
src_video = r"D:\mokuai\deepseek-chan-ocean-princess-moewalls-com.mp4"
ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
default_gif_path = os.path.join(BASE_DIR, "assets", "default_wallpaper.gif")

# 1. 将 MP4 转为 GIF 存入 assets 目录
if os.path.exists(src_video) and os.path.exists(ffmpeg_exe):
  print("⏳ 正在将默认 MP4 转为内置 GIF 壁纸...")
  cmd = [ffmpeg_exe, "-i", src_video, "-vf", "scale=720:450:force_original_aspect_ratio=increase,crop=720:450,fps=15", "-pix_fmt", "rgb24", "-y", default_gif_path]
  subprocess.run(cmd, check=True, capture_output=True)
  print("✅ 默认动态壁纸生成成功！已保存至 assets/default_wallpaper.gif")
elif os.path.exists(default_gif_path):
  print("✅ 默认壁纸已存在，跳过转码。")
else:
  print("⚠️ 未找到源 MP4 文件或 FFmpeg，跳过默认壁纸生成。")

# 2. 修改 main_final.py 加载默认壁纸逻辑
main_path = os.path.join(BASE_DIR, "main_final.py")
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

old_hot = '''  def update_wallpaper_hot():
    """更新底层的原生 Image 控件"""
    import glob
    import time
    
    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if all_files:
      latest = max(all_files, key=os.path.getctime)
      src = os.path.basename(latest)
      bg_image.src = src
      bg_image.visible = True
      print(f"🖼️ 已更新背景: {src}")
    else:
      bg_image.visible = False
      bg_image.src = None
      print("🧹 未找到壁纸文件，清空背景")
    bg_image.update()'''

new_hot = '''  def update_wallpaper_hot():
    """更新底层的原生 Image 控件"""
    import glob
    import time
    
    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if all_files:
      latest = max(all_files, key=os.path.getctime)
      src = os.path.basename(latest)
      bg_image.src = src
      bg_image.visible = True
      print(f"🖼️ 已更新自定义背景: {src}")
    else:
      # 检查默认动态壁纸
      default_gif = os.path.join(BASE_DIR, "assets", "default_wallpaper.gif")
      if os.path.exists(default_gif) and CFG.get("use_default_wallpaper", True):
        bg_image.src = "default_wallpaper.gif"
        bg_image.visible = True
        print("🖼️ 已加载内置默认动态壁纸")
      else:
        bg_image.visible = False
        bg_image.src = None
        print("🧹 未找到壁纸文件，清空背景")
    bg_image.update()'''

if old_hot in m_content:
  m_content = m_content.replace(old_hot, new_hot)
  with open(main_path, "w", encoding="utf-8") as f:
    f.write(m_content)
  print("✅ main_final.py 默认壁纸加载逻辑已注入！")

# 3. 修改 settings.py 清除与恢复逻辑
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
with open(settings_path, "r", encoding="utf-8") as f:
  s_content = f.read()

# 点击清除时，关闭默认壁纸
old_clear = '''    if cleared:
      show_snackbar("壁纸已清除。")
      card_step2.visible = False
      card_step3.visible = False
      card_step4.visible = False
      if hasattr(page, "update_wallpaper_hot"):
        page.update_wallpaper_hot()
      page.update()'''

new_clear = '''    if cleared:
      show_snackbar("壁纸已清除，默认壁纸已关闭。")
      CFG.set("use_default_wallpaper", False)
      CFG.save()
      card_step2.visible = False
      card_step3.visible = False
      card_step4.visible = False
      if hasattr(page, "update_wallpaper_hot"):
        page.update_wallpaper_hot()
      page.update()'''

if old_clear in s_content:
  s_content = s_content.replace(old_clear, new_clear)

# 当用户自定义图片时，恢复默认壁纸开关（防止以后删了自定义图没背景）
old_pick = '''          if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()'''
new_pick = '''          CFG.set("use_default_wallpaper", True)
          CFG.save()
          if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()'''
s_content = s_content.replace(old_pick, new_pick)

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(s_content)
print("✅ settings.py 逻辑已联动！")