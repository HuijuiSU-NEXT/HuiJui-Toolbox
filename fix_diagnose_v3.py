# fix_diagnose_v3.py · 修 diagnose_all.py 的 border 误报
# 根因：文件级 "border=" in content 撞上 Container 的合法参数
# 修法：改用正则只匹配 ButtonStyle( ... ) 内的 border=

import os
import shutil
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnose_all.py")

OLD = '    elif "ft.ButtonStyle" in content and "border=" in content:'
NEW = (
  '    elif "ft.ButtonStyle" in content and __import__("re").search(\n'
  '        r"ButtonStyle\\s*\\([^;{}]*?\\bborder\\s*=", content):'
)

def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到: {TARGET}")
    sys.exit(1)

  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

  if OLD not in content:
    print("[!] 没找到待替换行，可能已修过或已被改过。")
    print("  请把 diagnose_all.py 第 80 行附近贴给 AI 重新对齐。")
    sys.exit(2)

  new_content = content.replace(OLD, NEW, 1)

  if "__import__(\"re\")" in new_content and "import re" not in new_content:
    # 确保 import re 存在（正则要用）
    if new_content.startswith("import "):
      first_nl = new_content.find("\n")
      new_content = new_content[:first_nl+1] + "import re\n" + new_content[first_nl+1:]
    else:
      new_content = "import re\n" + new_content
    print("[OK]  补充 import re")

  try:
    compile(new_content, TARGET, "exec")
  except SyntaxError as e:
    print(f"[X] 语法预检失败，不写回: {e}")
    sys.exit(3)

  backup = TARGET + ".bak"
  shutil.copy2(TARGET, backup)
  print(f"[OK]  已备份 → {backup}")

  with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_content)
  print(f"[OK]  已写回 → {TARGET}")
  print("\n[✅] v3 完成！下一步：python diagnose_all.py 复测")
  print("   12 个 border 误报应全部消失，剩下 4 个线程违规待 v4 处理")

if __name__ == "__main__":
  main()