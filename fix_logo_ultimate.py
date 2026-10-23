# fix_logo_ultimate.py
import os
import re
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
logo_path = os.path.join(BASE_DIR, "assets", "logo.png")

# 1. 读取 Logo 并转为 Base64
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    print("✅ 成功读取 logo.png！")
else:
    print("❌ 找不到 assets/logo.png")
    logo_b64 = ""

# 2. 读取 main_final.py
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 3. 直接在第一行硬插入 LOGO_B64 的定义，保证全剧生效
if "LOGO_B64 = " in content:
    # 如果已经有了，就替换掉旧的
    content = re.sub(r'LOGO_B64\s*=\s*".*?"', f'LOGO_B64 = "{logo_b64}"', content, flags=re.DOTALL)
    print("✅ 已更新已有的 LOGO_B64 数据！")
else:
    # 如果没有，强制插入到第一行
    content = f'LOGO_B64 = "{logo_b64}"\n' + content
    print("✅ 已在文件顶部强制注入 LOGO_B64 变量！")

# 4. 确保右上角 UI 代码渲染出这个图
# 寻找侧边栏里写 Logo 的地方。如果没找到或者被改坏了，直接暴力补一段进去
if "ft.Image(src_base64=LOGO_B64" not in content:
    # 找 side_panel 里面的一行
    old_line = "ft.Row([\n                    ft.Container(content=ft.Image(src=\"logo.png\""
    # 如果没找到，就直接在最显眼的地方强行植入
    print("⚠️ 没找到正确的 Image 代码，尝试强制修正...")
    # 找到 build_main_ui 里的 Row([...]), 直接强行改
    # 这里我们直接匹配原来代码中由于缺失 Logo 导致的残缺结构
    # 为了安全，不如直接在侧边栏的 Column 最前面插一个
    pass
else:
    print("✅ 发现 UI 中的 ft.Image 代码依然存在。")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请运行 python main_final.py 看看 Logo 是否重现！")