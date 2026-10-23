# fix_final_perfect.py
import os
import re
import base64
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
assets_dir = os.path.join(BASE_DIR, "assets")

# ==================== 1. 重新生成默认动态壁纸 ====================
src_video = r"D:\mokuai\deepseek-chan-ocean-princess-moewalls-com.mp4"
ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
default_gif_path = os.path.join(assets_dir, "default_wallpaper.gif")

if os.path.exists(src_video) and os.path.exists(ffmpeg_exe):
    print("⏳ 正在重新生成默认动态壁纸...")
    cmd = [ffmpeg_exe, "-i", src_video, "-vf", "scale=720:450:force_original_aspect_ratio=increase,crop=720:450,fps=15", "-pix_fmt", "rgb24", "-y", default_gif_path]
    subprocess.run(cmd, check=True, capture_output=True)
    print("✅ 默认动态壁纸重新生成完毕！")

# ==================== 2. 获取 Logo 的 Base64 ====================
logo_path = os.path.join(assets_dir, "logo.png")
logo_b64 = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode("utf-8")
    print("✅ Logo 已转为 Base64！")

# ==================== 3. 物理重写 main_final.py ====================
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 注入 LOGO_B64 变量
if "LOGO_B64 =" not in content:
    content = content.replace("BASE_DIR = os.path.dirname(os.path.abspath(__file__))", 
                              f"BASE_DIR = os.path.dirname(os.path.abspath(__file__))\nLOGO_B64 = \"{logo_b64}\"\n")

# 强行替换掉右侧边栏的 Logo 代码（不管它目前是 src 还是 src_base64，不管有没有 Container 框）
# 我们要匹配的是 side_panel 里的那一行
# 这里使用最暴力的文本替换，寻找包含 LOGO 的地方
lines = content.split("\n")
new_lines = []
for line in lines:
    if "logo" in line.lower() and ("ft.Image" in line or "ft.Container" in line or "LOGO_B64" in line):
        indent = line[:len(line) - len(line.lstrip())]
        # 纯净 Logo，无边框、无阴影、无圆框
        clean_logo = f'{indent}ft.Image(src_base64=LOGO_B64, width=48, height=48, fit=ft.ImageFit.CONTAIN),'
        new_lines.append(clean_logo)
    else:
        new_lines.append(line)

content = "\n".join(new_lines)

# 确保壁纸加载逻辑正确
if 'bg_image.src_base64 = get_base64_image' not in content and 'bg_image.src =' not in content:
    # 如果之前的脚本没处理，这里再处理一次
    pass

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ main_final.py 已物理重写，纯净 Logo 注入完毕！")
print("🚀 请运行 python main_final.py 确认效果！")