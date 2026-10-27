# update_apk_logo.py - 仅处理手机端 Logo，不覆盖 PC 端
import os
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_LOGO = r"D:\file_00000000561081fd82a2690c35ed3eab.png"
DEST_PNG = os.path.join(BASE, "assets", "logo_android.png")

def process_logo():
  if not os.path.exists(SRC_LOGO):
    print(f"[X] 找不到源文件: {SRC_LOGO}")
    return

  print("[*] 正在读取手机端专属 Logo...")
  img = Image.open(SRC_LOGO).convert("RGBA")

  # 中心裁剪成正方形（防变形）
  w, h = img.size
  min_dim = min(w, h)
  left = (w - min_dim) // 2
  top = (h - min_dim) // 2
  right = left + min_dim
  bottom = top + min_dim
  img = img.crop((left, top, right, bottom))

  # 缩放成 1024x1024 并保存
  img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
  img.save(DEST_PNG, "PNG")
  
  print(f"[✅] 手机端 Logo 就绪：{DEST_PNG}")
  print("  （原电脑版 logo.png 和 logo.ico 未受任何影响）")

if __name__ == "__main__":
  process_logo()