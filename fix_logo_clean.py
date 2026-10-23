# fix_logo_clean.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 匹配目前包含 LOGO_B64 的那一整行 Container 代码
# 旧代码大概是：
# ft.Container(content=ft.Image(src_base64=LOGO_B64, width=40, height=40, fit=ft.ImageFit.COVER), border_radius=20, border=ft.border.all(2, theme_color), shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.4, theme_color)))

pattern = r'ft\.Container\(\s*content=ft\.Image\([^)]*src_base64=LOGO_B64[^)]*\)[^)]*\)'

# 新代码：直接放一个 Image 控件，去掉所有边框和阴影，稍微放大一点，防变形
new_logo_code = 'ft.Image(src_base64=LOGO_B64, width=48, height=48, fit=ft.ImageFit.CONTAIN)'

new_content, count = re.subn(pattern, new_logo_code, content)

if count > 0:
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ 成功拆掉了 {count} 个空心圆边框，只保留纯 Logo！")
else:
    # 兜底：精确暴力替换
    print("⚠️ 正则未匹配，尝试精确查找并替换...")
    old_line = 'ft.Container(content=ft.Image(src_base64=LOGO_B64, width=40, height=40, fit=ft.ImageFit.COVER), border_radius=20, border=ft.border.all(2, theme_color), shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.4, theme_color)))'
    if old_line in content:
        content = content.replace(old_line, new_logo_code)
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 兜底替换成功！")
    else:
        print("❌ 依然找不到旧 Logo 代码，请检查 main_final.py。")

print("🚀 修复完毕！运行 python main_final.py 看看效果。")