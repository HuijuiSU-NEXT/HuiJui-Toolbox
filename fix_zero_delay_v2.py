# fix_zero_delay_v2.py
import os
import base64
import io
from PIL import Image
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
cover_path = os.path.join(BASE_DIR, "assets", "wallpaper_cover.jpg")

# 1. 强行将现有的封面生成 Base64 并存入配置
if os.path.exists(cover_path):
  print("⚡ 正在将现有封面压缩为极小 Base64...")
  thumb = Image.open(cover_path)
  thumb.thumbnail((480, 300), Image.Resampling.BILINEAR)
  buffered = io.BytesIO()
  thumb.convert("RGB").save(buffered, format="JPEG", quality=60)
  img_b64 = base64.b64encode(buffered.getvalue()).decode()
  CFG.set("small_cover_b64", img_b64)
  CFG.save()
  print("✅ 极小 Base64 已成功存入 CFG！")
else:
  print("⚠️ 未找到封面图，请先在软件里选一次视频。")

# 2. 修复 main_final.py，绝不覆盖 Base64 渲染
with open(main_path, "r", encoding="utf-8") as f:
  m_content = f.read()

old_cover_update = '''      if os.path.exists(cover_path):
        bg_image.src = "wallpaper_cover.jpg"
        bg_image.visible = True
        print("🖼️ 已显示视频首帧封面，界面秒开")
      else:
        bg_image.visible = False'''

new_cover_update = '''      # 🚨 核心：如果 CFG 里有 Base64，绝不覆盖 src，保持内存直接渲染
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
        bg_image.visible = False'''

m_content = m_content.replace(old_cover_update, new_cover_update)

with open(main_path, "w", encoding="utf-8") as f:
  f.write(m_content)
print("✅ main_final.py 已强制优先读取 Base64，绝不黑屏！")