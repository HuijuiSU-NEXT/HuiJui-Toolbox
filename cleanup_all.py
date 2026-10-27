import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 彻底删掉我之前瞎加的垃圾 import
content = content.replace("import flet_desktop.version\n", "")
content = content.replace("import flet_video as ftv\n", "")
content = content.replace("import flet_video\n", "")

# 2. 修复启动入口
content = content.replace("ft.run(main)", 'ft.app(target=main, assets_dir="assets")')

# 3. 修复被 0.28.3 废弃的 API
# 3.1 把 src_base64 换回 src
content = re.sub(r'ft\.Image\(src_base64=LOGO_B64,.*?\)', 'ft.Image(src="assets/logo.png", width=48, height=48, fit="contain")', content)
content = re.sub(r'src_base64=b64_data,', 'src=target_file,', content)

# 3.2 把被删掉的 ImageFit 枚举换成底层支持的字符串
content = content.replace("ft.ImageFit.CONTAIN", '"contain"')
content = content.replace("ft.ImageFit.COVER", '"cover"')
content = content.replace("ft.ImageFit.FILL", '"fill"')

# 3.3 把被删掉的 FilterQuality 换掉
content = content.replace("ft.FilterQuality.HIGH", '"high"')

# 4. 视频引擎：因为 0.28.3 删了 ft.Video，咱们先把它注释掉，确保程序能跑起来。
# 只要程序能跑，咱们再去单独解决视频问题。
def replace_video(match):
  return """# 🚨 视频加载已被临时注释，保证程序能跑
        # new_bg = ft.Video(...)
        new_bg = ft.Container(expand=True)"""

content = re.sub(r'new_bg = ft\.Video\((.*?)\)', replace_video, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
  f.write(content)

print("✅ 垃圾已清理，代码已纯净，图片加载已适配 0.28.3！")
