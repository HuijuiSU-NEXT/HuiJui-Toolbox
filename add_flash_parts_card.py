# add_flash_parts_card.py
import os
import re

with open("pages/dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# 构造要插入的卡片数据
new_card = """        {"title": "分区刷入", "subtitle": "救砖/单刷指南", "icon": ft.Icons.BUILD_CIRCLE, "route": "flash_parts"},"""

# 找到插入点（插在 Scrcpy 投屏 后面）
anchor = """        {"title": "Scrcpy 投屏", "subtitle": "USB / 无线投屏", "icon": ft.Icons.MONITOR, "route": "scrcpy"},"""

if new_card.strip() not in content:
    if anchor in content:
        content = content.replace(anchor, anchor + "\n" + new_card)
        print("✅ 成功将『分区刷入』卡片插入 Dashboard 矩阵！")
    else:
        print("⚠️ 未找到定位锚点，尝试追加到列表末尾...")
        # 兜底：尝试加到 cards_data 列表的最后
        content = re.sub(r'(cards_data = \[.*?)(\])', r'\1' + new_card + r'\n    \2', content, flags=re.DOTALL)
else:
    print("ℹ️ 『分区刷入』卡片已存在，无需重复添加。")

with open("pages/dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)