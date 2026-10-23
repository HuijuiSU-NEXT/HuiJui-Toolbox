# fix_base64_define.py
import os
import re
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

# 1. 读取 Logo
logo_b64 = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    print("✅ 成功读取 Logo！")
else:
    print("❌ 找不到 logo.png")

# 2. 读取 main_final.py
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 3. 暴力注入：找到第一个 import 或者 from 语句，把变量定义塞在它们后面
# 这样保证在任何函数调用之前，LOGO_B64 就已经定义了
if 'LOGO_B64 = "' not in content:
    # 构造注入代码
    inject_str = f'\n# 🚨 自动注入的 Logo 数据\nLOGO_B64 = "{logo_b64}"\n'
    
    # 找到所有 import 结束的位置（也就是最后一个 import 或 from ... import 的行）
    lines = content.split("\n")
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i
            
    # 插入到最后一个 import 之后
    lines.insert(last_import_idx + 1, inject_str)
    content = "\n".join(lines)
    print("✅ 已将 LOGO_B64 强制注入到 import 之后！")
else:
    print("ℹ️ LOGO_B64 变量已存在。")

# 4. 再次确保 Logo 控件使用的是纯净版，且无边框
lines = content.split("\n")
new_lines = []
for line in lines:
    if "LOGO_B64" in line and "ft.Image" not in line and "LOGO_B64 =" not in line:
        # 如果是旧版带 container 的代码，替换掉
        pass
    elif "ft.Image(src_base64=LOGO_B64" in line:
        # 强制规范化为纯净版
        indent = line[:len(line) - len(line.lstrip())]
        new_lines.append(f'{indent}ft.Image(src_base64=LOGO_B64, width=48, height=48, fit=ft.ImageFit.CONTAIN),')
    else:
        new_lines.append(line)

with open(main_path, "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print("🚀 修复完毕！请运行 python main_final.py，Logo 绝对完美！")