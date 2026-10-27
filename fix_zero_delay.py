# fix_zero_delay.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 修改 settings.py：生成极小 Base64 缩略图 ====================
with open(settings_path, "r", encoding="utf-8") as f:
  s_content = f.read()

if "import base64" not in s_content:
  s_content = s_content.replace("import time", "import time\nimport base64\nimport io")

old_pick = '''            ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
              print("[FFmpeg] 正在提取视频首帧封面...")
              cmd_cover = [ffmpeg_exe, "-ss", "0.1", "-i", src_path, "-vframes", "1", "-q:v", "2", "-y", cover_path]
              subprocess.run(cmd_cover, check=True, capture_output=True)
              print(f"[FFmpeg] 封面提取成功: {cover_path}")'''

new_pick = '''            ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
              print("[FFmpeg] 正在提取视频首帧封面...")
              cmd_cover = [ffmpeg_exe, "-ss", "0.1", "-i", src_path, "-vframes", "1", "-q:v", "2", "-y", cover_path]
              subprocess.run(cmd_cover, check=True, capture_output=True)
              print(f"[FFmpeg] 封面提取成功: {cover_path}")
              
              # 🚨 生成极小 Base64 内存图，实现真正的 0 延迟首帧
              try:
                thumb = Image.open(cover_path)
                thumb.thumbnail((480, 300), Image.Resampling.BILINEAR)
                buffered = io.BytesIO()
                thumb.convert("RGB").save(buffered, format="JPEG", quality=60)
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                CFG.set("small_cover_b64", img_b64)
                CFG.save()
                print("⚡ 已生成极小 Base64 首帧，启动将 0 延迟！")
              except Exception as e:
                print(f"生成 Base64 封面失败: {e}")'''

s_content = s_content.replace(old_pick, new_pick)

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(s_content)
print("✅ settings.py 已加入 Base64 缩略图生成逻辑！")

# ==================== 2. 修改 main_final.py：用内存 Base64 秒开 ====================
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

# 替换启动时的 bg_image 初始化
old_init = '''  # 初始化时，只放入静态图和UI容器，不放视频
  bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)'''
new_init = '''  # 初始化时，直接读取极小 Base64 封面
  cover_b64 = CFG.get("small_cover_b64", "")
  bg_image = ft.Image(
    src_base64=cover_b64 if cover_b64 else None, 
    fit=ft.ImageFit.COVER, 
    expand=True, 
    visible=bool(cover_b64)
  )'''
m_content = m_content.replace(old_init, new_init)

# 替换 update_wallpaper_hot 里的延迟加载逻辑，把等待时间拉长，确保 UI 已经画出来
old_thread = '''  def load_video_thread():
        try:
          time.sleep(0.5)'''
new_thread = '''  def load_video_thread():
        try:
          # 给主线程 1.5 秒的时间把界面渲染好
          time.sleep(1.5)'''
m_content = m_content.replace(old_thread, new_thread)

# 把切换视频时的 delay 稍微缩短一点，无缝衔接
m_content = m_content.replace("time.sleep(1.0)\n          new_video.visible = True", "time.sleep(0.5)\n          new_video.visible = True")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(m_content)
print("✅ main_final.py 已改为 0 延迟内存首帧加载！")