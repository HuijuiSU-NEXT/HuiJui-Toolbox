# fix_diagnose_v4a_v2.py · 用 def check(...) 作为锚点插辅助函数
# 根因：diagnose_all.py 是顶层脚本，没有 def main()，v4a 锚点错了
# 修法：辅助函数插在 def check(...) 之前，elif 条件调用辅助函数

import os
import shutil
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnose_all.py")

OLD_ELIF = (
  '    elif "ft.ButtonStyle" in content and __import__("re").search(\n'
  '        r"ButtonStyle\\s*\\([^;{}]*?\\bborder\\s*=", content):'
)

NEW_ELIF = '    elif "ft.ButtonStyle" in content and _buttonstyle_has_border(content):'

HELPER = '''def _buttonstyle_has_border(content):
  """精确扫描：只在 ButtonStyle(...) 的括号配平范围内查 border=，杜绝跨块误伤"""
  idx = 0
  n = len(content)
  while idx < n:
    m = re.search(r"\\bButtonStyle\\s*\\(", content[idx:])
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
    if re.search(r"\\bborder\\s*=", block):
      return True
    idx = i
  return False


'''

ANCHOR = 'def check(name, condition, detail=""):'


def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到: {TARGET}")
    sys.exit(1)

  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

  if OLD_ELIF not in content:
    print("[!] 没找到 v3 写回的 elif 段，可能已被改过。")
    print("  请把 diagnose_all.py 里 'ButtonStyle' 相关的 elif 两行贴给 AI")
    sys.exit(2)

  if ANCHOR not in content:
    print("[!] 没找到 def check(...) 锚点。")
    sys.exit(3)

  content = content.replace(OLD_ELIF, NEW_ELIF, 1)
  print("[OK]  elif 条件改为 _buttonstyle_has_border() 调用")

  content = content.replace(ANCHOR, HELPER + ANCHOR, 1)
  print("[OK]  插入 _buttonstyle_has_border 辅助函数（def check 之前）")

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
  print("\n[✅] v4a-v2 完成！下一步：python diagnose_all.py 复测")
  print("   预期：4 个 border 违规全消失，只剩 4 个线程违规")


if __name__ == "__main__":
  main()