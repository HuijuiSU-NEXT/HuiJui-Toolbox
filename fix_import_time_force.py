# fix_import_time_force.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 暴力干掉函数内部任何可能的局部 import time
content = re.sub(r'\n\s+import\s+time', '', content)

# 2. 暴力在文件最顶端（第一行）强制加入 import time
if not content.startswith("import time"):
    content = "import time\n" + content

# 3. 确保全局有且只有一个 import time，清理掉可能被插到中间的空行
# 防止出现 import time\nimport time 的情况
content = re.sub(r'^(import time\s*)+', 'import time\n', content, flags=re.MULTILINE)

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 强制全局导入 time 成功！现在就算闭包想发疯也没机会了。")