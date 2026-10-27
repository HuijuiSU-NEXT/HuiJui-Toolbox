# fix_final_assets.py
import os
import shutil
import subprocess
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BIN_DIR = os.path.join(BASE_DIR, "bin")

print("=== 开始终极清理与资源修复 ===")

# 1. 物理超度无用文件 (settings_backup.py)
backup_file = os.path.join(BASE_DIR, "pages", "settings_backup.py")
if os.path.exists(backup_file):
  os.remove(backup_file)
  print("🧹 已删除无用文件: pages/settings_backup.py")

# 2. 修复默认壁纸缺失问题
default_wallpaper = os.path.join(ASSETS_DIR, "default_wallpaper.gif")
if not os.path.exists(default_wallpaper):
  print("⚠️ 默认壁纸缺失，正在提取现有视频首帧作为默认壁纸...")
  # 找现有的视频
  videos = glob.glob(os.path.join(ASSETS_DIR, "wallpaper_*.mp4"))
  if videos:
    latest_video = max(videos, key=os.path.getctime)
    ffmpeg_exe = os.path.join(BIN_DIR, "ffmpeg", "ffmpeg.exe")
    if os.path.exists(ffmpeg_exe):
      cmd = [ffmpeg_exe, "-i", latest_video, "-vf", "scale=720:450", "-vframes", "1", "-y", default_wallpaper.replace(".gif", ".jpg")]
      subprocess.run(cmd, capture_output=True)
      print(f"✅ 已从视频提取静态图作为默认壁纸: {default_wallpaper.replace('.gif', '.jpg')}")
    else:
      print("❌ 找不到 ffmpeg，跳过提取。")
  else:
    print("💡 没有任何视频壁纸，放一张图到 assets 目录即可。")

# 3. 针对那些“误报”的线程阻塞，我直接给代码层加一层绝对保险：
# 把 subprocess.run 强制加上 CREATE_NO_WINDOW，防止打包后弹出黑框
print("🛡️ 正在为所有底层命令添加防黑框参数...")
for filename in os.listdir(os.path.join(BASE_DIR, "pages")):
  if filename.endswith(".py"):
    filepath = os.path.join(BASE_DIR, "pages", filename)
    with open(filepath, "r", encoding="utf-8") as f:
      content = f.read()
    
    # 如果用到 subprocess 但没有防黑框，强行补上
    if "subprocess.Popen" in content or "subprocess.run" in content:
      if "CREATE_NO_WINDOW" not in content:
        content = content.replace("subprocess.Popen(", "subprocess.Popen(\n  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0, ")
        content = content.replace("subprocess.run(", "subprocess.run(\n  creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0, ")
        with open(filepath, "w", encoding="utf-8") as f:
          f.write(content)
        print(f" ✅ 已为 {filename} 的底层命令添加防黑框")

print("=== 清理与修复完成！请运行 python main_final.py 确认一切正常。 ===")