# fix_time_bug.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 确保文件顶部有全局的 import time
if not content.startswith("import time"):
    if "import time" not in content.split("\n\n")[0]:
        content = "import time\n" + content

# 2. 删掉 build_main_ui 内部那个引发血案的局部 import time
# 匹配类似：换行 + 空格 + import time + 换行
content = re.sub(r'\n\s*import time\s*\n', '\n', content)

# 3. 确保壁纸时间戳那段代码没有多余的空行或缩进错乱
content = content.replace(
    "cache_buster = int(time.time())",
    "cache_buster = int(time.time())"
)

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 修复完毕！局部 import time 已删除，全局导入已确认。")