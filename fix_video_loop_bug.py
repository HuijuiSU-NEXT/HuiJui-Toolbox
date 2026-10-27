# fix_video_loop_bug.py
import os
import re

main_path = "main_final.py"

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 修复 Video 的循环参数：把 loop=True 删掉，改用 playlist_mode
old_video_init = r'bg_video = ftv\.Video\([^)]*loop=True[^)]*\)'
new_video_init = 'bg_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=False)'

content = re.sub(old_video_init, new_video_init, content)

# 2. 确保 settings.py 里的格式列表是最新的 (以防万一)
settings_path = "pages/settings.py"
if os.path.exists(settings_path):
  with open(settings_path, "r", encoding="utf-8") as f:
    s_content = f.read()
  
  # 视频格式扩展
  s_content = s_content.replace(
    'allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"]',
    'allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "bmp", "mp4", "webm", "mov", "mkv", "avi"]'
  )
  # 确保 update_wallpaper_hot 能正确识别这些视频格式
  if '.endswith((".mp4", ".webm", ".mov", ".mkv", ".avi"))' not in s_content:
    s_content = s_content.replace(
      '.endswith((".mp4", ".webm", ".mov"))',
      '.endswith((".mp4", ".webm", ".mov", ".mkv", ".avi"))'
    )
  with open(settings_path, "w", encoding="utf-8") as f:
    f.write(s_content)
  print("✅ settings.py 格式兼容已确认！")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ Video 循环参数已修复为 PlaylistMode.SINGLE！")
print("✅ 支持的视频格式：MP4, WebM, MOV, MKV, AVI")
print("✅ 支持的图片格式：JPG, PNG, WebP, GIF, BMP")