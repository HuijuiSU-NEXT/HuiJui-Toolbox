# fix_v4b.py · 第三轮收尾：诊断精确化 + 两个真阻塞点包线程
# 铁律 3 合规：精确 str.replace，逐文件备份 + 语法预检

import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DIAG = os.path.join(BASE, "diagnose_all.py")
MS = os.path.join(BASE, "pages", "mode_switch.py")
ST = os.path.join(BASE, "pages", "settings.py")

# ---------- diagnose_all.py ----------
OLD_DIAG = (
  '    # 线程安全\n'
  '    if "subprocess.Popen" in content or "subprocess.run" in content:\n'
  '      if "threading" not in content and "async" not in content:\n'
  '        check(f"线程安全: {filename}", False, "存在 subprocess 但没有 threading 包裹")\n'
  '      else:\n'
  '        check(f"线程安全: {filename}", True)'
)
NEW_DIAG = (
  '    # 线程安全（只检测阻塞型 subprocess 调用；Popen 视为非阻塞）\n'
  '    _BLOCKING_PAT = re.compile(\n'
  '      r"subprocess\\.(?:run|call|check_output|check_call)\\s*\\(|\\.wait\\s*\\(|\\.communicate\\s*\\("\n'
  '    )\n'
  '    if _BLOCKING_PAT.search(content):\n'
  '      if "threading" not in content and "async" not in content:\n'
  '        check(f"线程安全: {filename}", False, "存在阻塞型 subprocess 调用但没有 threading/async 包裹")\n'
  '      else:\n'
  '        check(f"线程安全: {filename}", True)'
)

# ---------- mode_switch.py ----------
OLD_MS_IMP = "import subprocess\nimport os\n"
NEW_MS_IMP = "import subprocess\nimport os\nimport threading\n"

OLD_MS_RUN = (
  '  def run_cmd(cmd, msg):\n'
  '    status.value = msg\n'
  '    page.update()\n'
  "    subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)\n"
)
NEW_MS_RUN = (
  '  def run_cmd(cmd, msg):\n'
  '    status.value = msg\n'
  '    page.update()\n'
  '    def _bg():\n'
  '      try:\n'
  "        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)\n"
  '      except Exception as ex:\n'
  '        status.value = f"执行失败: {ex}"\n'
  '        try:\n'
  '          page.update()\n'
  '        except Exception:\n'
  '          pass\n'
  '    threading.Thread(target=_bg, daemon=True).start()\n'
)

# ---------- settings.py ----------
OLD_ST_IMP = "import subprocess\n"
NEW_ST_IMP = "import subprocess\nimport threading\n"

OLD_ST_RUN = (
  '              cmd_cover = [ffmpeg_exe, "-ss", "0.1", "-i", src_path, "-vframes", "1", "-q:v", "2", "-y", cover_path]\n'
  "              subprocess.run(cmd_cover, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)\n"
)
NEW_ST_RUN = (
  '              cmd_cover = [ffmpeg_exe, "-ss", "0.1", "-i", src_path, "-vframes", "1", "-q:v", "2", "-y", cover_path]\n'
  '              def _ffmpeg_cover():\n'
  '                try:\n'
  "                  subprocess.run(cmd_cover, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)\n"
  '                except Exception:\n'
  '                  pass\n'
  '              threading.Thread(target=_ffmpeg_cover, daemon=True).start()\n'
)


def apply(path, replacements, tag):
  print(f"\n=== {tag} ===")
  if not os.path.isfile(path):
    print(f"[X] 找不到 {path}")
    return False
  with open(path, "r", encoding="utf-8") as f:
    content = f.read()
  original = content
  for old, new, desc in replacements:
    if old in content:
      content = content.replace(old, new, 1)
      print(f"[OK]  {desc}")
    else:
      print(f"[FAIL] {desc} —— 源片段未匹配，跳过本文件")
      return False
  if content == original:
    print("[!] 内容无变化")
    return False
  try:
    compile(content, path, "exec")
  except SyntaxError as e:
    print(f"[X] 语法预检失败，不写回: {e}")
    return False
  backup = path + ".bak3"
  shutil.copy2(path, backup)
  print(f"[OK]  备份 → {backup}")
  with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
  print(f"[OK]  写回 → {path}")
  return True


def main():
  ok1 = apply(DIAG, [(OLD_DIAG, NEW_DIAG, "诊断脚本线程检查改为只盯阻塞型调用（Popen 放行）")], "diagnose_all.py")
  ok2 = apply(MS, [
    (OLD_MS_IMP, NEW_MS_IMP, "mode_switch.py 补 import threading"),
    (OLD_MS_RUN, NEW_MS_RUN, "mode_switch.py run_cmd 包线程"),
  ], "mode_switch.py")
  ok3 = apply(ST, [
    (OLD_ST_IMP, NEW_ST_IMP, "settings.py 补 import threading"),
    (OLD_ST_RUN, NEW_ST_RUN, "settings.py ffmpeg 提封面 包线程"),
  ], "settings.py")

  print("\n" + "=" * 60)
  if ok1 and ok2 and ok3:
    print("[✅] v4b 全绿！下一步：python diagnose_all.py 复测 → 预期 63/63")
  else:
    print("[!] 有文件修改失败，成功的已写回，失败的原文件保留")
  print("=" * 60)


if __name__ == "__main__":
  main()