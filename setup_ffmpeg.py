# setup_ffmpeg.py
import os
import urllib.request
import zipfile
import shutil

# 配置路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
FFMPEG_DIR = os.path.join(BIN_DIR, "ffmpeg")
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# 下载源：Gyan.dev 的 FFmpeg Essentials 构建（包含常用的编解码器）
# 如果下载慢，可换成 BtbN 的构建：https://github.com/BtbN/FFmpeg-Builds/releases
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

def setup_ffmpeg():
  # 1. 检查是否已安装
  if os.path.exists(FFMPEG_EXE):
    print("✅ FFmpeg 已存在于 bin/ffmpeg/ 目录，无需重新下载。")
    return

  print("⏳ 正在下载 FFmpeg（文件约 80MB，请耐心等待）...")
  os.makedirs(BIN_DIR, exist_ok=True)
  zip_path = os.path.join(BIN_DIR, "ffmpeg_download.zip")

  try:
    # 2. 下载压缩包
    req = urllib.request.Request(FFMPEG_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as response, open(zip_path, 'wb') as out_file:
      shutil.copyfileobj(response, out_file)

    print("✅ 下载完成，正在解压...")
    
    # 3. 解压并提取需要的文件
    os.makedirs(FFMPEG_DIR, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
      for file_info in z.infolist():
        # 只提取 ffmpeg.exe 和 ffprobe.exe
        if file_info.filename.endswith("ffmpeg.exe") or file_info.filename.endswith("ffprobe.exe"):
          filename = os.path.basename(file_info.filename)
          target_path = os.path.join(FFMPEG_DIR, filename)
          with z.open(file_info) as source, open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)
          print(f"📦 已提取: {filename}")

    # 4. 清理临时文件
    if os.path.exists(zip_path):
      os.remove(zip_path)
    
    print(f"🎉 FFmpeg 及 FFprobe 已成功内置到: {FFMPEG_DIR}")

  except Exception as e:
    print(f"❌ 下载或解压 FFmpeg 失败: {e}")
    if os.path.exists(zip_path):
      os.remove(zip_path)
    return

  # 5. 自动修改 main_final.py，注入环境变量
  main_path = os.path.join(BASE_DIR, "main_final.py")
  if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8") as f:
      content = f.read()
    
    # 如果还没有注入路径配置，就加上
    if "FFMPEG_DIR" not in content:
      inject_code = '''
# 🚨 自动注入 FFmpeg 环境变量（由 setup_ffmpeg.py 生成）
import os
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg")
if os.path.exists(FFMPEG_DIR) and FFMPEG_DIR not in os.environ["PATH"]:
  os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]
# ---------------------------------------------------
'''
      # 在文件最开头（import flet 之前）插入
      if "import flet" in content:
        content = content.replace("import flet", inject_code + "\nimport flet", 1)
      else:
        content = inject_code + content
      
      with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
      print("✅ 已自动在 main_final.py 中注入 FFmpeg 路径配置！")
    else:
      print("ℹ️ main_final.py 中已存在 FFmpeg 路径配置，跳过。")

if __name__ == "__main__":
  setup_ffmpeg()