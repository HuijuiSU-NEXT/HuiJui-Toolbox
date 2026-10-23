# fix_base64_images.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# ==================== 1. 注入获取 Logo Base64 的辅助函数 ====================
if "def get_base64_image(filepath):" not in content:
    helper_code = '''
def get_base64_image(filepath):
    import base64
    try:
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ 读取图片转 Base64 失败: {e}")
    return ""
'''
    content = content.replace("def main(page: ft.Page):", helper_code + "\ndef main(page: ft.Page):")
    print("✅ 已注入 Base64 读取辅助函数！")

# ==================== 2. 替换 Logo 加载逻辑 ====================
old_logo = 'ft.Image(src="/logo.png", width=40, height=40, fit=ft.ImageFit.COVER)'
new_logo = 'ft.Image(src_base64=get_base64_image(os.path.join(BASE_DIR, "assets", "logo.png")), width=40, height=40, fit=ft.ImageFit.COVER)'

if old_logo in content:
    content = content.replace(old_logo, new_logo)
    print("✅ 右上角 Logo 已改为 Base64 内存加载！")
else:
    # 兜底正则
    content = re.sub(r'ft\.Image\(src="[^"]*logo\.png".*?\)', new_logo, content, flags=re.DOTALL)

# ==================== 3. 替换背景壁纸加载逻辑 ====================
# 精确匹配咱们之前的 update_wallpaper_hot 函数
pattern = r'    def update_wallpaper_hot\(\):.*?bg_image\.update\(\)'
new_hot = '''    def update_wallpaper_hot():
        import glob
        target_file = None
        
        # 找自定义壁纸或默认壁纸
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            target_file = max(all_files, key=os.path.getctime)
            print(f"🖼️ 准备加载自定义壁纸: {os.path.basename(target_file)}")
        else:
            default_gif = os.path.join(BASE_DIR, "assets", "default_wallpaper.gif")
            if os.path.exists(default_gif) and CFG.get("use_default_wallpaper", True):
                target_file = default_gif
                print("🖼️ 准备加载内置默认动态壁纸")
        
        if target_file and os.path.exists(target_file):
            # 🚨 核心：读取为 Base64 字符串
            b64_data = get_base64_image(target_file)
            if b64_data:
                bg_image.src_base64 = b64_data
                bg_image.visible = True
            else:
                bg_image.visible = False
        else:
            bg_image.visible = False
            bg_image.src_base64 = None
            print("🧹 未找到壁纸文件，清空背景")
            
        bg_image.update()'''

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_hot, content, flags=re.DOTALL)
    print("✅ 背景壁纸已改为 Base64 内存加载！")
else:
    print("⚠️ 未找到 update_wallpaper_hot 函数，请检查文件是否被破坏。")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！现在无论是开发环境还是单文件 EXE，绝对不可能再丢图！")