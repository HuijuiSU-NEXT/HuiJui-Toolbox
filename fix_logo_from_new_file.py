# fix_logo_from_new_file.py
import os
import re
import base64
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
assets_dir = os.path.join(BASE_DIR, "assets")
target_logo = os.path.join(assets_dir, "logo.png")

# 你给的新图路径
source_logo = r"D:\file_00000000561081fd82a2690c35ed3eab.png"

# 1. 复制新 Logo 到 assets
if os.path.exists(source_logo):
    os.makedirs(assets_dir, exist_ok=True)
    shutil.copy2(source_logo, target_logo)
    print("✅ 新 Logo 图片已复制到 assets/logo.png！")
else:
    print(f"❌ 找不到你提供的图片: {source_logo}")
    exit()

# 2. 读取新 Logo 并转 Base64
with open(target_logo, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode("utf-8")
print(f"✅ Base64 数据读取成功，长度: {len(logo_b64)} 字符")

# 3. 替换 main_final.py 中的 LOGO_B64 变量
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 强制替换第一行的 LOGO_B64
content = re.sub(r'LOGO_B64\s*=\s*".*?"', f'LOGO_B64 = "{logo_b64}"', content, count=1, flags=re.DOTALL)
# 如果没匹配到（可能被删了），就强行在开头插入
if "LOGO_B64" not in content:
    content = f'LOGO_B64 = "{logo_b64}"\n' + content

# 4. 修复 UI 代码：确保 Logo 容器包裹，且固定 48x48 尺寸
# 寻找包含 LOGO_B64 的代码块并替换
pattern = r'ft\.Container\(\s*content=ft\.Image\(src_base64=LOGO_B64.*?\)\s*,\s*width=48,\s*height=48.*?\)'
# 上面这个正则可能太窄，用宽泛的
ui_pattern = r'ft\.Container\(\s*content=ft\.Image\(src_base64=LOGO_B64[^)]*\),[^)]*\)'

# 新的安全 UI 代码
new_ui = '''ft.Container(
                        content=ft.Image(src_base64=LOGO_B64, fit=ft.ImageFit.COVER),
                        width=48, height=48, border_radius=12
                    )'''

if re.search(ui_pattern, content, flags=re.DOTALL):
    content = re.sub(ui_pattern, new_ui, content, flags=re.DOTALL)
    print("✅ UI 代码已修复：使用 Container 包裹，固定 48x48 尺寸！")
else:
    print("⚠️ 未找到匹配的 UI 代码，请检查 main_final.py 侧边栏代码。")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请运行 python main_final.py 查看新的 Logo！")