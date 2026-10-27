import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 修复所有 src_base64 问题 (Flet 0.28 已废弃)
# 直接改回用 src=本地路径，不仅速度更快，而且完全绕过 base64 限制
content = re.sub(r'src_base64=b64_data,', 'src=target_file,', content)
content = re.sub(r'ft\.Image\(src_base64=LOGO_B64,', 'ft.Image(src="assets/logo.png",', content) # 假设你有本地 logo，如果没有直接删掉这行也行
content = re.sub(r'bg_image\.src_base64 = b64_data', 'bg_image.src = target_file', content)
content = re.sub(r'bg_image\.src_base64 = None', 'bg_image.src = None', content)

# 2. 彻底干掉那个报错的 get_base64_image
content = content.replace("b64_data = get_base64_image(target_file)", "# 已由极客跳过 base64 转码")

# 3. 重新编写最稳定的 update_wallpaper_hot
pattern = re.compile(r'def update_wallpaper_hot\(\):.*?page\.update_wallpaper_hot = update_wallpaper_hot', re.DOTALL)

new_func = '''def update_wallpaper_hot():
    import glob
    import os
    target_file = None

    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if all_files:
      target_file = max(all_files, key=os.path.getctime)
      print(f"🖼️ 准备加载自定义壁纸: {os.path.basename(target_file)}")

    if target_file and os.path.exists(target_file):
      ext = os.path.splitext(target_file)[1].lower()
      
      if ext in ['.mp4', '.webm', '.mov']:
        # 使用 flet_video 官方包的稳定 API
        try:
          import flet_video as ftv
          new_bg = ftv.Video(
            playlist=[ftv.VideoMedia(target_file)],
            autoplay=True,
            muted=True,
            fit="cover"
          )
          print("🎬 已切换至视频壁纸引擎 (flet-video 标准 API)")
        except Exception as e:
          print(f"❌ 视频加载失败: {e}")
          new_bg = ft.Container(expand=True)
      else:
        new_bg = ft.Image(
          src=target_file,
          fit="cover",
          filter_quality="high"
        )
        print("🖼️ 已切换至图片壁纸引擎")
      
      new_bg.visible = True
      main_stack.controls[0] = new_bg
    else:
      print("🧹 未找到壁纸文件，清空背景")
      main_stack.controls[0] = ft.Container(expand=True)
      
    page.update()

  page.update_wallpaper_hot = update_wallpaper_hot'''

if pattern.search(content):
  content = pattern.sub(new_func, content)
  with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
  print("✅ 壁纸渲染引擎已重构为最新的 src= 和 flet-video 标准！")
else:
  print("⚠️ 替换失败，未匹配到函数。")

