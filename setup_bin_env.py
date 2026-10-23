# setup_bin_env.py
import os
import urllib.request
import zipfile
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
os.makedirs(BIN_DIR, exist_ok=True)

SCRCPY_URLS = [
    "https://ghproxy.net/https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-win64-v3.1.zip",
    "https://gh.llkk.cc/https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-win64-v3.1.zip"
]

def kill_adb():
    print("正在清理可能占用的 adb 进程...")
    try:
        subprocess.run("taskkill /F /IM adb.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run("taskkill /F /IM scrcpy.exe", shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("✅ 进程清理完毕。")
    except Exception:
        pass

def download_file(url, dest):
    print(f"正在尝试下载: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as response, open(dest, 'wb') as out_file:
        data = response.read(1024 * 1024)
        while data:
            out_file.write(data)
            data = response.read(1024 * 1024)
    print("✅ 下载完成")

def setup_scrcpy():
    if os.path.exists(os.path.join(BIN_DIR, "scrcpy.exe")):
        print("✅ Scrcpy 已经存在于 bin 目录中，无需下载。")
        return

    kill_adb() # 核心：解压前先杀进程
    
    tmp_zip = os.path.join(BIN_DIR, "scrcpy_tmp.zip")
    
    # 如果已经下载过没解压成功，直接跳过下载
    if not os.path.exists(tmp_zip):
        for url in SCRCPY_URLS:
            try:
                download_file(url, tmp_zip)
                break
            except Exception as e:
                print(f"❌ 镜像失败: {e}")
        else:
            print("❌ 所有镜像均下载失败，请手动下载 scrcpy 压缩包并解压到 bin 目录。")
            return

    print("正在解压 scrcpy 文件...")
    try:
        with zipfile.ZipFile(tmp_zip, 'r') as z:
            for file_info in z.infolist():
                if file_info.is_dir(): continue
                filename = os.path.basename(file_info.filename)
                if filename:
                    target_path = os.path.join(BIN_DIR, filename)
                    try:
                        with z.open(file_info) as source, open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                    except PermissionError:
                        print(f"⚠️ 跳过被占用的文件: {filename}")
                    except Exception as e:
                        print(f"⚠️ 提取 {filename} 失败: {e}")
        
        os.remove(tmp_zip)
        print("🎉 Scrcpy 解压及内置部署完成！(若有 adb.exe 跳过，不影响使用)")
    except Exception as e:
        print(f"❌ 解压发生异常: {e}")

if __name__ == "__main__":
    print("=== HuiJui Core 底层军火库初始化 ===")
    setup_scrcpy()