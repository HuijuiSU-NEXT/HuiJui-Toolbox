# fix_ghost_n.py
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 彻底干掉因为转义失效导致的字面量 \n
# 匹配类似： "rescue": build_rescue_page,\n            "emergency_flash": build_emergency_flash_page,
# 将其替换为真正的换行
content = re.sub(r'\\n\s*', '\n            ', content)
# 再次保险替换
content = content.replace('\\n', '\n')

# 2. 为了确保字典结构完美，如果还有挤在一行的，直接手动修
bad_line = '"rescue": build_rescue_page,            "emergency_flash": build_emergency_flash_page,'
good_lines = '"rescue": build_rescue_page,\n            "emergency_flash": build_emergency_flash_page,'
content = content.replace(bad_line, good_lines)

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 幽灵字符清理完毕！如果还有报错，请截图。")