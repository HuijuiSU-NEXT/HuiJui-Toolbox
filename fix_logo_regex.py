# fix_logo_regex.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 极客级精准正则：匹配所有加载 logo.png 的 Image 控件
pattern = r'ft\.Image\([^)]*src=["\']/?logo\.png["\'][^)]*\)'

new_logo_code = 'ft.Image(src_base64=get_base64_image(os.path.join(BASE_DIR, "assets", "logo.png")), width=40, height=40, fit=ft.ImageFit.COVER)'

# 执行替换
new_content, count = re.subn(pattern, new_logo_code, content)

if count > 0:
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 成功找到并替换了 {count} 处 Logo 图标加载代码！")
else:
    print("⚠️ 未找到 Logo 代码，尝试逐行暴力匹配...")
    # 兜底：直接按行替换
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "logo.png" in line and "ft.Image" in line:
            lines[i] = line.replace(line.strip(), new_logo_code + ",")
            count += 1
    content = "\n".join(lines)
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 兜底替换完毕，共修复 {count} 处！")

print("🚀 修复完毕！请运行 python main_final.py 确认 Logo 出现，然后打包！")