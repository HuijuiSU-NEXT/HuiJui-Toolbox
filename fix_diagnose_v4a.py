# fix_diagnose_v4a.py · 根治 border 误报：括号配平精确扫描 ButtonStyle 块
# v3 根因：正则 [^;{}]*? 未限制在 () 内，ButtonStyle 闭合后跨块撞 Container(border=...)
# v4a 修法：用括号深度配平，只在 ButtonStyle(...) 的块内查 border=

import os
import shutil
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnose_all.py")

# v3 写回的原文（两行）
OLD_ELIF = (
  '    elif "ft.ButtonStyle" in content and __import__("re").search(\n'
  '        r"ButtonStyle\\s*\\([^;{}]*?\\bborder\\s*=", content):'
)

NEW_ELIF = '    elif "ft.ButtonStyle" in content and _buttonstyle_has_border(content):'

# 辅助函数（插在 def main() 之前）
HELPER = '''def _buttonstyle_has_border(content):
  """精确扫描：只在 ButtonStyle(...) 的括号配平范围内查 border=，杜绝跨块误伤"""
  import re as _re
  idx = 0
  n = len(content)
  while idx < n:
    m = _re.search(r"\\bButtonStyle\\s*\\(", content[idx:])
    if not m:
      return False
    start = idx + m.end()
    depth = 1
    i = start
    while i < n and depth > 0:
      ch = content[i]
      if ch == "(":
        depth += 1
      elif ch == ")":
        depth -= 1
      i += 1
    block = content[start:i - 1] if i - 1 >= start else ""
    if _re.search(r"\\bborder\\s*=", block):
      return True
    idx = i
  return False


def main():
'''


def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到: {TARGET}")
    sys.exit(1)

  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

  if OLD_ELIF not in content:
    print("[!] 没找到 v3 写回的 elif 段，可能已被改过。")
    print("  请把 diagnose_all.py 第 76-85 行贴给 AI 重新对齐。")
    sys.exit(2)

  if "def main():" not in content:
    print("[!] 没找到 def main(): 锚点，无法插入辅助函数。")
    sys.exit(3)

  # 先替换 elif
  content = content.replace(OLD_ELIF, NEW_ELIF, 1)
  print("[OK]  border 检查改为 _buttonstyle_has_border() 括号配平")

  # 再插入辅助函数（替换第一个 def main():）
  if "_buttonstyle_has_border" not in content.split("def main():")[0]:
    content = content.replace("def main():", HELPER, 1)
    print("[OK]  插入 _buttonstyle_has_border 辅助函数")

  try:
    compile(content, TARGET, "exec")
  except SyntaxError as e:
    print(f"[X] 语法预检失败，不写回: {e}")
    sys.exit(4)

  backup = TARGET + ".bak2"
  shutil.copy2(TARGET, backup)
  print(f"[OK]  已备份 → {backup}")

  with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
  print(f"[OK]  已写回 → {TARGET}")
  print("\n[✅] v4a 完成！下一步：python diagnose_all.py 复测")
  print("   预期：4 个 border 违规全消失，只剩 4 个线程违规")


if __name__ == "__main__":
  main()