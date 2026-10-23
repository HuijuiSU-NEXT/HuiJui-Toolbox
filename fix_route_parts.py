# fix_route_parts.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 确保导入了 build_flash_parts_page
if "from pages.flash_parts import build_flash_parts_page" not in content:
    content = content.replace(
        "from pages.flash import build_flash_page",
        "from pages.flash import build_flash_page\nfrom pages.flash_parts import build_flash_parts_page"
    )
    print("✅ 已添加 flash_parts 导入语句。")

# 2. 暴力注入路由字典
# 找到 "scan": build_scan_page, 这个锚点
anchor = '"scan": build_scan_page,'
if anchor in content and '"flash_parts": build_flash_parts_page,' not in content:
    content = content.replace(
        anchor,
        anchor + '\n            "flash_parts": build_flash_parts_page,'
    )
    print("✅ 已成功将 flash_parts 强行注入 SUB_PAGES 字典！")
elif '"flash_parts": build_flash_parts_page,' in content:
    print("ℹ️ 路由字典中已存在 flash_parts。")
else:
    print("⚠️ 未找到定位锚点，尝试在字典末尾兜底注入...")
    # 兜底：直接找 "mediatek_rescue": build_mediatek_rescue_page,
    anchor2 = '"mediatek_rescue": build_mediatek_rescue_page,'
    if anchor2 in content:
        content = content.replace(
            anchor2,
            anchor2 + '\n            "flash_parts": build_flash_parts_page,'
        )
        print("✅ 已通过备用锚点注入！")

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 修复完毕！请重新启动主程序。")