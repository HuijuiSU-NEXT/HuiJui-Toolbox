# setup_ffmpeg_fast.py
import os
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
FFMPEG_DIR = os.path.join(BIN_DIR, "ffmpeg")
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# 使用 BtbN 的构建，并走 Github 国内加速代理
FFMPEG_URLS = [
  "https://ghproxy.net/https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip",
  "https://gh.llkk.cc/https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip",
  "https://mirror.ghproxy.com/https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
]

def setup_ffmpeg():
  if os.path.exists(FFMPEG_EXE):
    print("✅ FFmpeg 已存在于 bin/ffmpeg/ 目录，无需重新下载。")
    return

  print("⏳ 正在从国内加速节点下载 FFmpeg (约 80MB)...")
  os.makedirs(BIN_DIR, exist_ok=True)
  zip_path = os.path.join(BIN_DIR, "ffmpeg_download.zip")

  downloaded = False
  for url in FFMPEG_URLS:
    try:
      req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
      with urllib.request.urlopen(req, timeout=15) as response, open(zip_path, 'wb') as out_file:
        # 分块下载并显示进度
        length = int(response.getheader('Content-Length', 0))
        read = 0
        while True:
          chunk = response.read(1024 * 1024)
          if not chunk:
            break
          out_file.write(chunk)
          read += len(chunk)
          if length > 0:
            percent = int(read / length * 100)
            print(f"\r下载进度: {percent}% ({read//1024//1024}MB / {length//1024//1024}MB)", end="")
      print("\n✅ 下载成功！")
      downloaded = True
      break
    except Exception as e:
      print(f"⚠️ 节点失败: {url.split('/')[2]}, 尝试下一个...")
      
  if not downloaded:
    print("❌ 所有节点均下载失败，请检查网络。")
    return

  print("正在解压并提取文件...")
  try:
    os.makedirs(FFMPEG_DIR, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
      for file_info in z.infolist():
        # 提取所有 bin 目录下的文件（包含 exe 和 dll）
        if "/bin/" in file_info.filename and not file_info.is_dir():
          filename = os.path.basename(file_info.filename)
          target_path = os.path.join(FFMPEG_DIR, filename)
          with z.open(file_info) as source, open(target_path, "wb") as target:
            shutil.copyfileobj(source, target)
    print(f"🎉 FFmpeg 及其依赖已全部成功提取到: {FFMPEG_DIR}")
    
    if os.path.exists(zip_path):
      os.remove(zip_path)
      
  except Exception as e:
    print(f"❌ 解压失败: {e}")
    return

  # 注入环境变量配置
  main_path = os.path.join(BASE_DIR, "main_final.py")
  if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8") as f:
      content = f.read()
    
    if "FFMPEG_DIR" not in content:
      inject_code = '''
import os
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg")
if os.path.exists(FFMPEG_DIR) and FFMPEG_DIR not in os.environ["PATH"]:
  os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]
'''
      # 在 import flet 之前插入
      if "import flet" in content:
        content = content.replace("import flet", inject_code + "\nimport flet", 1)
      else:
        content = inject_code + content
      
      with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
      print("✅ 已自动在 main_final.py 中注入 FFmpeg 路径配置！")

if __name__ == "__main__":
  setup_ffmpeg()