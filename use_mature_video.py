import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 强制替换导入
if "import flet_video" not in content:
  content = content.replace("import flet", "import flet\nimport flet_video as ftv", 1)

# 2. 匹配整个 update_wallpaper_hot 函数
pattern = re.compile(r'def update_wallpaper_hot\(\):.*?page\.update_wallpaper_hot = update_wallpaper_hot', re.DOTALL)

new_func = '''def update_wallpaper_hot():
    import glob
    import os
    target_file = None

    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    if all_files:
      target_file = max(all_files, key=os.path.getctime)

    if target_file and os.path.exists(target_file):
      ext = os.path.splitext(target_file)[1].lower()
      
      if ext in ['.mp4', '.webm', '.mov']:
        # 🚨 核心：使用官方成熟的 flet-video 引擎，最标准写法！
        media = ftv.VideoMedia(target_file)
        new_bg = ftv.Video(
          playlist=[media],
          autoplay=True,
          muted=True
        )
        print(f"🎬 视频壁纸已加载: {os.path.basename(target_file)}")
      else:
        new_bg = ft.Image(
          src=target_file,
          fit=ft.ImageFit.COVER
        )
        print(f"🖼️ 图片壁纸已加载: {os.path.basename(target_file)}")
      
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
  print("✅ 壁纸引擎已成功挂载 flet-video 独立引擎！")
else:
  print("⚠️ 替换失败。")

