import re

file_path = "main_final.py"

with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 仅针对 ft.Video 进行安全替换
def add_video_props(match):
  inner_code = match.group(1)
  # 如果已经有 fit，就跳过，绝不重复添加
  if "fit=" in inner_code:
    return match.group(0)
  
  # 如果没有 fit，说明是纯视频，给它加上完美铺满和高清渲染
  return f"ft.Video({inner_code.strip()}, fit=ft.ImageFit.COVER, filter_quality=ft.FilterQuality.HIGH)"

# 极其精准的正则匹配
content = re.sub(r'ft\.Video\((.*?)\)', add_video_props, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 视频组件画质修复成功！")
