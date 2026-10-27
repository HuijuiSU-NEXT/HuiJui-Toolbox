# install_mtk_env.py
import os
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

# 使用国内镜像加速下载 MTKClient
MTKCLIENT_URL = "https://ghproxy.net/https://github.com/bkerler/mtkclient/archive/refs/heads/main.zip"
# SP Flash Tool 直链 (版本 v5.2316)
SPFLASH_URL = "https://spflashtools.com/wp-content/uploads/2023/09/SP_Flash_Tool_v5.2316_Win.zip"

def download_file(url, dest):
  print(f"正在下载: {url}")
  req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
  with urllib.request.urlopen(req, timeout=60) as response, open(dest, 'wb') as out_file:
    data = response.read(1024 * 1024)
    while data:
      out_file.write(data)
      data = response.read(1024 * 1024)
  print("✅ 下载完成")

def install_mtkclient():
  target_dir = os.path.join(BIN_DIR, "MTKClient")
  if os.path.exists(os.path.join(target_dir, "mtk_gui.bat")):
    print("✅ MTKClient 已存在，跳过下载。")
    return

  tmp_zip = os.path.join(BIN_DIR, "mtkclient_tmp.zip")
  try:
    download_file(MTKCLIENT_URL, tmp_zip)
    print("正在解压 MTKClient...")
    with zipfile.ZipFile(tmp_zip, 'r') as z:
      # 解压到临时文件夹
      temp_extract = os.path.join(BIN_DIR, "temp_mtk")
      z.extractall(temp_extract)
      
      # 找到解压出来的根目录 (mtkclient-main)
      for item in os.listdir(temp_extract):
        src_path = os.path.join(temp_extract, item)
        if os.path.isdir(src_path):
          # 移动到 bin/MTKClient
          if os.path.exists(target_dir): shutil.rmtree(target_dir)
          shutil.move(src_path, target_dir)
          break
      # 清理临时文件
      shutil.rmtree(temp_extract, ignore_errors=True)
      os.remove(tmp_zip)
    print("🎉 MTKClient 成功安装至 bin/MTKClient！")
  except Exception as e:
    print(f"❌ MTKClient 安装失败: {e}")
    if os.path.exists(tmp_zip): os.remove(tmp_zip)

def install_spflashtool():
  target_dir = os.path.join(BIN_DIR, "SPFlashTool")
  if os.path.exists(os.path.join(target_dir, "flash_tool.exe")):
    print("✅ SP Flash Tool 已存在，跳过下载。")
    return

  tmp_zip = os.path.join(BIN_DIR, "spflash_tmp.zip")
  try:
    download_file(SPFLASH_URL, tmp_zip)
    print("正在解压 SP Flash Tool...")
    with zipfile.ZipFile(tmp_zip, 'r') as z:
      z.extractall(target_dir)
    os.remove(tmp_zip)
    print("🎉 SP Flash Tool 成功安装至 bin/SPFlashTool！")
  except Exception as e:
    print(f"❌ SP Flash Tool 安装失败: {e}")
    if os.path.exists(tmp_zip): os.remove(tmp_zip)

if __name__ == "__main__":
  print("=== 开始配置天玑 (MediaTek) 救砖军火库 ===")
  install_mtkclient()
  install_spflashtool()
  print("=== 配置结束，请确保安装了 MTK USB 驱动 ===")