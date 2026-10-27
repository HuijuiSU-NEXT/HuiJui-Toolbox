# fix_time_scope_final.py
import re

main_path = "main_final.py"

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 暴力删除所有带有缩进的局部 import time
# 匹配：行首有空格，然后是 import time
content = re.sub(r'^[ \t]+import\s+time.*\n', '', content, flags=re.MULTILINE)

# 2. 确保文件最顶部有且仅有一个全局的 import time
if not content.startswith("import time"):
  if "import time" not in content.split("\n")[0:5]:
    content = "import time\n" + content
    print("✅ 已在顶部补全全局 import time！")

# 3. 保险起见，把之前隐藏窗口的 time.sleep 检查一下
# 如果代码里有 import time 被删了，确保没有别的依赖受影响
print("✅ 所有局部的 'import time' 已彻底清除！")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)