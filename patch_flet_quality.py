import re
import os

file_path = "main_final.py"

with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 给所有的 ft.Image 加上高质量过滤
# 查找形如 ft.Image( 并且里面没有 filter_quality 的代码
def add_filter_quality(match):
  inner_code = match.group(1)
  if "filter_quality" not in inner_code:
    # 在 ft.Image( 后面的第一个参数位置加入 filter_quality
    return f"ft.Image({inner_code.strip()}, filter_quality=ft.FilterQuality.HIGH, fit=ft.ImageFit.COVER)"
  return match.group(0)

# 使用正则替换，尽量精准，防止切碎代码
content = re.sub(r'ft\.Image\((.*?)\)', add_filter_quality, content, flags=re.DOTALL)

# 2. 给所有的 ft.Video 加上完美填充属性
def add_video_fit(match):
  inner_code = match.group(1)
  if "fit=" not in inner_code:
    return f"ft.Video({inner_code.strip()}, fit=ft.ImageFit.COVER, filter_quality=ft.FilterQuality.HIGH)"
  return match.group(0)

content = re.sub(r'ft\.Video\((.*?)\)', add_video_fit, content, flags=re.DOTALL)

# 3. 在页面中添加暗色遮罩（如果原本有背景图，加遮罩能立刻消除颗粒噪点感）
# 寻找 page.add(...) 或者你原本构建 Stack 的地方，这个比较难精准替换，所以提供一段提示
with open(file_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 画质渲染参数已注入！已自动开启 FilterQuality.HIGH")
print("🚨 提示：如果还有颗粒感，请确保你的壁纸是 MP4 格式，而不是 GIF！")
