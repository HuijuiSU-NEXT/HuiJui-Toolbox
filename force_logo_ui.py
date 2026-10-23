# force_logo_ui.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 寻找包含 LOGO_B64 的那个 ft.Row，直接替换成防挤压的安全布局
# 匹配包含 LOGO_B64 的整个 ft.Row
pattern = r'ft\.Row\(\[\s*ft\.Image\(src_base64=LOGO_B64.*?\]\)'

# 用 Container 包裹，设定 48x48 的固定大小，防止被右侧的 expand 挤压变 0
new_str = '''ft.Row([
                    ft.Container(
                        content=ft.Image(src_base64=LOGO_B64, fit=ft.ImageFit.COVER),
                        width=48, height=48, border_radius=12
                    ),
                    ft.Column([ft.Text("HuiJui Toolbox", size=16, weight=ft.FontWeight.W_900, color="white"), ft.Text("Matrix Engine", size=10, color=theme_color)], spacing=0, expand=True),
                ])'''

new_content, count = re.subn(pattern, new_str, content, flags=re.DOTALL)

if count > 0:
    print("✅ 已通过正则成功注入防挤压的纯净 Logo 布局！")
else:
    print("⚠️ 未找到精确匹配，尝试暴力查找包含 LOGO_B64 的行...")
    # 兜底：如果正则没匹配上，可能结构已经被改乱了，直接找包含 LOGO_B64 的行强行覆盖
    lines = content.split("\n")
    new_lines = []
    skip_flag = False
    for line in lines:
        if "ft.Image(src_base64=LOGO_B64" in line:
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(f"{indent}ft.Container(content=ft.Image(src_base64=LOGO_B64, fit=ft.ImageFit.COVER), width=48, height=48, border_radius=12),")
            print("✅ 兜底替换成功！")
        elif "ft.Column([ft.Text(\"HuiJui Toolbox\"" in line and "ft.Row" in line:
            # 防止多行重复
            pass
        else:
            new_lines.append(line)
    new_content = "\n".join(new_lines)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("🚀 修复完毕！现在可以运行主程序了。")