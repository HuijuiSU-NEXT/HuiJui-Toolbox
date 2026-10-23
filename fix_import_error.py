# fix_import_error.py
import os

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 修复错误拼接的 import 语句
bad_import = "from pages.rescue import build_rescue_page\\nfrom pages.emergency_flash import build_emergency_flash_page"
good_import = "from pages.rescue import build_rescue_page\nfrom pages.emergency_flash import build_emergency_flash_page"

if bad_import in content:
    content = content.replace(bad_import, good_import)
    print("✅ 修复 import 语句成功！")
else:
    print("⚠️ 未找到错误的 import 语句，可能已被修改。")

# 顺便检查一下是否有其他类似被 \n 污染的语句
if '\\nfrom pages.emergency_flash' in content:
    content = content.replace('\\nfrom pages.emergency_flash', '\nfrom pages.emergency_flash')
    print("✅ 同时修复了其他的转义问题。")

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完成，请重新运行 python main_final.py")