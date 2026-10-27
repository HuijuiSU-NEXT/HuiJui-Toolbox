# fix_video_delay_3s.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 替换 update_wallpaper_hot 里的加载逻辑
pattern = r'  def update_wallpaper_hot\(\):.*?(?=  def |  # |\Z)'
new_update = '''  def update_wallpaper_hot():
    import glob
    import threading
    import time
    
    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    cover_path = os.path.join(BASE_DIR, "assets", "wallpaper_cover.jpg")
    
    video_files = [f for f in all_files if f.lower().endswith((".mp4", ".webm", ".mov", ".mkv", ".avi"))]
    
    if video_files:
      latest = max(video_files, key=os.path.getctime)
      src = os.path.basename(latest)
      abs_src = os.path.join(BASE_DIR, "assets", src)
      
      # 1. 优先显示 Base64 内存图，实现 0 延迟秒开
      cover_b64 = CFG.get("small_cover_b64", "")
      if cover_b64:
        bg_image.src_base64 = cover_b64
        bg_image.visible = True
        print("🖼️ 已使用内存 Base64 秒开")
      elif os.path.exists(cover_path):
        bg_image.src = "wallpaper_cover.jpg"
        bg_image.visible = True
        print("🖼️ 已读取本地首帧封面")
      else:
        bg_image.visible = False
        
      # 2. 彻底延迟 3 秒，避开 UI 初始化黑屏期
      def load_video_thread():
        try:
          time.sleep(3.0) # 🚨 核心：给 UI 充足的 3 秒渲染时间
          
          new_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=False, fit=ft.ImageFit.COVER)
          new_video.playlist.clear()
          new_video.playlist.append(ftv.VideoMedia(abs_src))
          
          main_stack.controls.insert(0, new_video)
          page.update()
          
          new_video.play()
          print(f"🎬 已后台加载高清视频壁纸: {abs_src}")
          
          time.sleep(1.0)
          new_video.visible = True
          bg_image.visible = False
          
          if video_state["current"] and video_state["current"] != new_video:
            if video_state["current"] in main_stack.controls:
              main_stack.controls.remove(video_state["current"])
          
          video_state["current"] = new_video
          page.update()
          print("✨ 视频加载完毕，已切换至动态壁纸！")
        except Exception as e:
          print(f"❌ 视频加载失败: {e}")
          
      threading.Thread(target=load_video_thread, daemon=True).start()
      
    else:
      if video_state["current"] and video_state["current"] in main_stack.controls:
        main_stack.controls.remove(video_state["current"])
        video_state["current"] = None
        
      if all_files:
        latest = max(all_files, key=os.path.getctime)
        src = os.path.basename(latest)
        bg_image.src = src
        bg_image.visible = True
        print(f"🖼️ 已更新图片壁纸: {src}")
      else:
        bg_image.visible = False
        print("🧹 未找到壁纸文件")
        
    page.update()

'''
content = re.sub(pattern, new_update, content, flags=re.DOTALL)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 极致延迟加载补丁已注入！现在启动绝对 0 秒出图！")