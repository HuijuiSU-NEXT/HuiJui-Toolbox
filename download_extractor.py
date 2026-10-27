# download_extractor.py
import os
import urllib.request
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

# 🚨 使用你提供的 pre-release 链接
TARGET_URL = "https://github.com/Viole403/ghostlock-a53/releases/download/pre-release/ghostlock-extract-windows-x86_64.exe"

# 国内加速镜像列表（把原始链接拼接到镜像后面）
MIRRORS = [
  TARGET_URL,
  f"https://ghproxy.net/{TARGET_URL}",
  f"https://gh.llkk.cc/{TARGET_URL}",
  f"https://mirror.ghproxy.com/{TARGET_URL}"
]

def download():
  dest_path = os.path.join(BIN_DIR, "ghostlock-extract.exe")
  if os.path.exists(dest_path):
    print("✅ ghostlock-extract.exe 已存在，跳过下载。")
    return True

  for i, url in enumerate(MIRRORS):
    print(f"⏳ 正在尝试下载 (源 {i+1}/{len(MIRRORS)})...")
    try:
      req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
      with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
      print(f"✅ 下载成功！已保存为: {dest_path}")
      return True
    except Exception as e:
      print(f"⚠️ 源 {i+1} 失败: {e}")

  print("\n❌ 所有源均下载失败，请手动操作：")
  print(f"1. 在浏览器中打开这个链接: {TARGET_URL}")
  print("2. 文件会自动下载，或者点击页面上的 Download 按钮。")
  print("3. 下载完成后，将文件重命名为 ghostlock-extract.exe")
  print(f"4. 放入这个目录: {BIN_DIR}")
  return False

if __name__ == "__main__":
  print("=== 开始下载 ghostlock-extract.exe ===")
  success = download()
  if success:
    print("\n🎉 偏移提取器已就位！")
    print("💡 接下来请手动寻找适配你机型的 ghostlock-bin 载荷。")
  else:
    print("\n🔧 请按照上方提示手动下载并放置文件。")