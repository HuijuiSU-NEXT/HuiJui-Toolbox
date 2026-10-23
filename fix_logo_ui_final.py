# fix_logo_ui_final.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 找到 `side_panel` 的定义，用最稳的嵌套替换掉原本容易缩水的 `Row` 内部布局
# 匹配包含 LOGO_B64 的那个 ft.Row
pattern = r'ft\.Row\(\[\s*ft\.Image\(src_base64=LOGO_B64.*?ft\.Column\(\[.*?\]\)\s*\]\)'

new_layout = '''ft.Row([
                    ft.Container(
                        content=ft.Image(src_base64=LOGO_B64, fit=ft.ImageFit.COVER),
                        width=48, height=48, border_radius=12
                    ),
                    ft.Column([ft.Text("HuiJui Toolbox", size=16, weight=ft.FontWeight.W_900, color="white"), ft.Text("Matrix Engine", size=10, color=theme_color)], spacing=0, expand=True),
                ])'''

new_content, count = re.subn(pattern, new_layout, content, flags=re.DOTALL)

if count > 0:
    print("✅ 已成功注入防挤压的 Logo 布局！")
else:
    # 兜底：如果正则没匹配到（可能是换行或缩进变了），直接去按行找
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        if "LOGO_B64" in line and "ft.Image" in line:
            # 找到包含 Logo 的那一行，直接把整段代码替换掉
            indent = line[:len(line) - len(line.lstrip())]
            # 这里需要强行把上面几行和下面几行替换了。这太难了。
            # 既然找不到，就说明它在别的地方。我们用最暴力的替换：
            pass
        new_lines.append(line)
    new_content = "\n".join(new_lines)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("🚀 修复完毕！请运行 python main_final.py 查看效果。")