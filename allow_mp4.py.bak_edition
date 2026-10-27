# allow_mp4.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# 把白名单里的格式补全，加上 mp4, webm 等视频格式
old_allowed = 'allowed_extensions=["jpg", "jpeg", "png", "webp", "gif"]'
new_allowed = 'allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"]'

if old_allowed in content:
    content = content.replace(old_allowed, new_allowed)
    print("✅ 成功解除视频格式限制！现在可以选 MP4 了。")
else:
    print("⚠️ 没找到旧的白名单，尝试正则替换...")
    import re
    content = re.sub(r'allowed_extensions=\[[^\]]+\]', 'allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"]', content)
    print("✅ 已通过正则完成修复！")

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(content)