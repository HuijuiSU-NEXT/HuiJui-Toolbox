# fix_ultimate_lazy_video.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 移除一开始的 bg_video 实例化，只留 Image
old_stack_init = '''  bg_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=False, fit=ft.ImageFit.COVER)
  bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
  ui_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
  
  main_stack = ft.Stack([bg_image, bg_video, ui_container], expand=True, fit=ft.StackFit.EXPAND)
  page.add(main_stack)'''

new_stack_init = '''  # 🚨 核心：启动时不实例化 Video，只放 Image，保证主界面秒开！
  bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
  ui_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
  
  main_stack = ft.Stack([bg_image, ui_container], expand=True, fit=ft.StackFit.EXPAND)
  page.add(main_stack)
  
  # 用一个字典来跟踪当前的 video 状态
  video_state = {"current": None}'''

content = content.replace(old_stack_init, new_stack_init)

# 2. 重写 update_wallpaper_hot 函数，使用延迟实例化方案
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
      
      # 1. 立即显示首帧静态图，让用户瞬间看到画面
      if os.path.exists(cover_path):
        bg_image.src = "wallpaper_cover.jpg"
        bg_image.visible = True
        print("🖼️ 已显示视频首帧封面，界面秒开")
      else:
        bg_image.visible = False
        
      # 2. 后台延迟加载视频
      def load_video_thread():
        try:
          time.sleep(0.5) # 给 UI 充分的渲染时间
          
          # 创建新的 Video 实例
          new_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=False, fit=ft.ImageFit.COVER)
          new_video.playlist.clear()
          new_video.playlist.append(ftv.VideoMedia(abs_src))
          
          # 插入到 Stack 的最底层
          main_stack.controls.insert(0, new_video)
          page.update()
          
          new_video.play()
          print(f"🎬 已后台加载高清视频壁纸: {abs_src}")
          
          # 3. 再等 1 秒，等视频第一帧渲染完毕，无缝切换
          time.sleep(1.0)
          new_video.visible = True
          bg_image.visible = False
          
          # 清理旧的 video 实例，防止内存泄漏
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
      # 静态图处理
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

# 3. 移除之前 on_window_resize 里对 bg_video 的引用（如果有）
old_resize = '''  def on_window_resize(e):
    if bg_video.visible:
      bg_video.update()
    if bg_image.visible:
      bg_image.update()
  page.on_resize = on_window_resize'''
new_resize = '''  def on_window_resize(e):
    if video_state["current"] and video_state["current"].visible:
      video_state["current"].update()
    if bg_image.visible:
      bg_image.update()
  page.on_resize = on_window_resize'''
content = content.replace(old_resize, new_resize)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 延迟实例化视频引擎已注入！启动将绝对秒开！")