import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 匹配整个 update_wallpaper_hot 函数（从 def 到 page.update_wallpaper_hot = update_wallpaper_hot）
pattern = re.compile(r'def update_wallpaper_hot\(\):.*?page\.update_wallpaper_hot = update_wallpaper_hot', re.DOTALL)

new_func = '''def update_wallpaper_hot():
    import glob
    import os
    target_file = None

    # 找最新的自定义壁纸
    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if all_files:
      target_file = max(all_files, key=os.path.getctime)
      print(f"🖼️ 准备加载自定义壁纸: {os.path.basename(target_file)}")

    if target_file and os.path.exists(target_file):
      ext = os.path.splitext(target_file)[1].lower()
      
      # 🚨 核心：智能识别格式
      if ext in ['.mp4', '.webm', '.mov']:
        # 视频引擎
        new_bg = ft.Video(
          src=target_file,
          autoplay=True,
          muted=True,
          loop=True,
          fit=ft.ImageFit.COVER,
          filter_quality=ft.FilterQuality.HIGH
        )
        print("🎬 已切换至视频壁纸引擎")
      else:
        # 图片/动图引擎
        b64_data = get_base64_image(target_file)
        new_bg = ft.Image(
          src_base64=b64_data,
          fit=ft.ImageFit.COVER,
          filter_quality=ft.FilterQuality.HIGH
        )
        print("🖼️ 已切换至图片壁纸引擎")
      
      new_bg.visible = True
      # 替换 Stack 最底层的组件
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
  print("✅ 智能壁纸渲染引擎注入成功！")
else:
  print("⚠️ 替换失败，未匹配到函数。")

