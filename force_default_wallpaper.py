# force_default_wallpaper.py
import os
import glob
from core_api import CFG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(BASE_DIR, "assets")

# 1. 强行把配置重置为“开启默认壁纸”
CFG.set("use_default_wallpaper", True)
CFG.save()
print("✅ 已强制将配置项 use_default_wallpaper 重置为 True！")

# 2. 物理清理可能残留的测试壁纸，只保留默认的
print("🧹 正在清理可能造成干扰的旧壁纸...")
all_wallpapers = glob.glob(os.path.join(assets_dir, "wallpaper_*.*"))
for f in all_wallpapers:
    try:
        os.remove(f)
        print(f"   已删除残留测试文件: {os.path.basename(f)}")
    except Exception as e:
        pass

# 3. 确保默认壁纸文件存在
default_gif = os.path.join(assets_dir, "default_wallpaper.gif")
if os.path.exists(default_gif):
    print(f"✅ 默认动态壁纸完好: {os.path.basename(default_gif)}")
else:
    print("❌ 默认壁纸丢失！请重新运行 setup_default_wallpaper.py")

print("🚀 修复完毕！请运行 python main_final.py 查看效果。")