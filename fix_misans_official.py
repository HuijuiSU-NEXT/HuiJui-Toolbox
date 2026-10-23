# fix_misans_official.py
import os
import urllib.request
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

# 小米官方字体下载直链
MI_SANS_URL = "https://hyperos.mi.com/font-download/MiSans.zip"

def setup_misans():
    print("=== 开始配置 MiSans 字体 (官方源) ===")
    
    # 1. 下载官方压缩包
    zip_path = os.path.join(BASE_DIR, "MiSans.zip")
    if not os.path.exists(zip_path):
        print("⏳ 正在从小米官方服务器下载 MiSans 字体包 (约 20MB)...")
        try:
            req = urllib.request.Request(MI_SANS_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response, open(zip_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            print("✅ 下载完成！")
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return
    else:
        print("✅ 字体包已存在，跳过下载。")

    # 2. 解压并提取所需文件
    print("正在解压并提取 MiSans-Regular.ttf 和 MiSans-Bold.ttf...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # 查找压缩包内所需的两个文件
            for file_info in z.infolist():
                filename = os.path.basename(file_info.filename)
                if filename in ["MiSans-Regular.ttf", "MiSans-Bold.ttf"]:
                    target_path = os.path.join(FONTS_DIR, filename)
                    with z.open(file_info) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)
                    print(f"📦 已提取: {filename}")
        print("✅ 字体提取完成！")
        
        # 清理压缩包
        if os.path.exists(zip_path):
            os.remove(zip_path)
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return

    # 3. 清理旧配置并重新注入到 main_final.py
    main_path = os.path.join(BASE_DIR, "main_final.py")
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 移除之前可能注入的错误字体配置块
    import re
    content = re.sub(r'\n    # 🚨 全局字体配置：使用 MiSans\n    page\.fonts = \{.*?\n    \}\n    page\.theme = ft\.Theme\(font_family="MiSans"\)\n', '', content, flags=re.DOTALL)

    # 注入新的字体配置
    inject_code = '''
    # 🚨 全局字体配置：使用 MiSans
    page.fonts = {
        "MiSans": "fonts/MiSans-Regular.ttf",
        "MiSans Bold": "fonts/MiSans-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="MiSans")
'''
    if "page.fonts" not in content:
        content = content.replace("def main(page: ft.Page):\n", "def main(page: ft.Page):\n" + inject_code)
    
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 已清理旧配置并在 main_final.py 中注入正确的 MiSans 字体配置！")

if __name__ == "__main__":
    setup_misans()