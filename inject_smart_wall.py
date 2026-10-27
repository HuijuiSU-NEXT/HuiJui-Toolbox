import os

file_path = "main_final.py"

with open(file_path, "r", encoding="utf-8") as f:
  lines = f.readlines()

# 我们准备一段极其强大的“智能壁纸生成器”代码
smart_wallpaper_code = """
def build_smart_wallpaper(file_path):
  # 智能识别后缀
  ext = os.path.splitext(file_path)[1].lower()
  if ext in ['.mp4', '.webm', '.mov']:
    # 视频引擎：硬件解码，超清60帧
    return ft.Video(
      src=file_path,
      autoplay=True,
      muted=True,
      loop=True,
      fit=ft.ImageFit.COVER,
      filter_quality=ft.FilterQuality.HIGH
    )
  else:
    # 图片/动图引擎：开启极致抗锯齿
    return ft.Image(
      src=file_path,
      fit=ft.ImageFit.COVER,
      filter_quality=ft.FilterQuality.HIGH
    )
"""

# 把这段函数注入到文件里（插在文件最前面，或者 after import 之后）
# 这里为了保险，我们插在文件开头的位置
insert_index = 0
for i, line in enumerate(lines):
  if line.startswith("import") or line.startswith("from"):
    insert_index = i + 1

lines.insert(insert_index, "\n" + smart_wallpaper_code + "\n")

with open(file_path, "w", encoding="utf-8") as f:
  f.writelines(lines)

print("✅ 全格式智能渲染组件已成功注入 main_final.py！")
