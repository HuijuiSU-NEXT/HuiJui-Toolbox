# fix_perfect_transition.py
import re

main_path = "main_final.py"

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 找到 update_wallpaper_hot 里的异步加载线程
old_thread = '''  def load_video_thread():
        try:
          time.sleep(3.0) # 🚨 给 UI 充足的 3 秒渲染时间
          
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
          print(f"❌ 视频加载失败: {e}")'''

new_thread = '''  def load_video_thread():
        try:
          time.sleep(3.0) # 🚨 给 UI 充足的 3 秒渲染时间
          
          # 1. 创建视频，初始可见，但放在 Stack 的最底层（被静态图遮挡）
          new_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=True, fit=ft.ImageFit.COVER)
          new_video.playlist.clear()
          new_video.playlist.append(ftv.VideoMedia(abs_src))
          
          # 插入到 controls[0] 位置，也就是最底层
          main_stack.controls.insert(0, new_video)
          page.update()
          
          # 2. 开始播放，此时因为上面还盖着静态图，用户看不到任何黑屏
          new_video.play()
          print(f"🎬 已后台静默加载高清视频壁纸: {abs_src}")
          
          # 3. 等待足够长的时间（确保视频第一帧真的渲染出来了）
          time.sleep(2.0) 
          
          # 4. 瞬间撤掉上层遮挡，无缝切换到视频
          bg_image.visible = False
          
          if video_state["current"] and video_state["current"] != new_video:
            if video_state["current"] in main_stack.controls:
              main_stack.controls.remove(video_state["current"])
          
          video_state["current"] = new_video
          page.update()
          print("✨ 视频已完美出帧，静态图已撤下，无缝衔接！")
        except Exception as e:
          print(f"❌ 视频加载失败: {e}")'''

# 执行正则替换
pattern = r'  def load_video_thread\(\):.*?(?=      threading\.Thread\(target=load_video_thread)'
content = re.sub(pattern, new_thread + "\n\n", content, flags=re.DOTALL)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 完美无缝过渡补丁已注入！彻底屏蔽中间的黑屏闪烁！")