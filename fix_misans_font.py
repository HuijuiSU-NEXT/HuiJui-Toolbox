# fix_misans_font.py
import os
import urllib.request
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

# 使用国内加速镜像下载小米 MiSans 字体
FONT_URLS = {
    "MiSans-Regular.ttf": "https://ghproxy.net/https://github.com/xiaomi-font/MiSans/raw/main/MiSans/Regular/MiSans-Regular.ttf",
    "MiSans-Bold.ttf": "https://ghproxy.net/https://github.com/xiaomi-font/MiSans/raw/main/MiSans/Bold/MiSans-Bold.ttf"
}

def setup_misans():
    print("=== 开始配置 MiSans 字体 ===")
    for filename, url in FONT_URLS.items():
        dest_path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(dest_path):
            print(f"✅ 字体已存在: {filename}")
            continue
        print(f"⏳ 正在下载字体: {filename}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as response, open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            print(f"✅ 下载成功: {filename}")
        except Exception as e:
            print(f"❌ 下载失败: {filename} ({e})")

    # 自动注入到 main_final.py
    main_path = os.path.join(BASE_DIR, "main_final.py")
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "page.fonts" not in content:
        inject_code = '''
    # 🚨 全局字体配置：使用 MiSans
    page.fonts = {
        "MiSans": "fonts/MiSans-Regular.ttf",
        "MiSans Bold": "fonts/MiSans-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="MiSans")
'''
        content = content.replace("def main(page: ft.Page):\n", "def main(page: ft.Page):\n" + inject_code)
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 已在 main_final.py 中注入 MiSans 字体配置！")
    else:
        print("ℹ️ main_final.py 中已存在字体配置，跳过。")

if __name__ == "__main__":
    setup_misans()