# fix_ghostlock_tools.py
import os
import urllib.request
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

# 官方下载链接（来自 Viole403/ghostlock-a53 的 releases）
TARGET_URL = "https://github.com/Viole403/ghostlock-a53/releases/download/v1.2/ghostlock-extract-windows-x86_64.exe"

# 国内加速镜像列表
MIRRORS = [
  TARGET_URL,
  f"https://ghproxy.net/{TARGET_URL}",
  f"https://gh.llkk.cc/{TARGET_URL}",
  f"https://mirror.ghproxy.com/{TARGET_URL}"
]

def download_extractor():
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
  
  print("❌ 所有镜像均下载失败，请手动下载。")
  print(f"🔗 官方链接: {TARGET_URL}")
  print("💡 下载后请重命名为 ghostlock-extract.exe 并放入 bin 目录。")
  return False

def check_ghostlock_bin():
  bin_path = os.path.join(BIN_DIR, "ghostlock-bin")
  if os.path.exists(bin_path):
    print("✅ ghostlock-bin 载荷已存在。")
    return True
  else:
    print("\n⚠️ 未找到 ghostlock-bin 载荷。")
    print(" 这是一个 Android ARM64 的可执行文件，需要针对你的手机型号和内核版本进行编译或寻找社区适配版。")
    print(" 你可以：")
    print(" 1. 去 GhostLock 相关的 GitHub 仓库或酷安社区寻找对应你机型的预编译 ghostlock-bin 文件。")
    print(" 2. 如果你有 ARM64 编译环境，可以从 GhostLock 源码自行编译。")
    print(" 暂时缺少它不会影响其他功能，临时 Root 页面会优雅地提示用户。")
    return False

if __name__ == "__main__":
  print("=== 开始补全 GhostLock 工具链 ===")
  extractor_ok = download_extractor()
  bin_ok = check_ghostlock_bin()
  
  if extractor_ok and bin_ok:
    print("\n🎉 所有 GhostLock 工具已就绪！")
  else:
    print("\n🔧 部分工具就绪，请根据上方提示手动补全剩余文件。")
    print(" 补全后，重新运行 python check_bin.py 即可确认。")