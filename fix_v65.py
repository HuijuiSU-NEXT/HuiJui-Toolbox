import os
import re
import shutil

BASE = r"D:\Huijui-Toolbox-Next"

# 遍历所有需要修改的 .py 文件
files_to_fix = []
for root, dirs, files in os.walk(BASE):
  # 跳过无关目录
  dirs[:] = [d for d in dirs if d not in ('venv', 'venv_android', 'dist', 'build', '__pycache__', '.git')]
  for f in files:
    if f.endswith('.py') and f not in ('fix_v65.py',):
      files_to_fix.append(os.path.join(root, f))

print("🔍 正在扫描并替换版本号 -> .5 ...")
changed_files = 0

for filepath in files_to_fix:
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

  # 匹配 或 或 6.0 (前后有非数字字符)
  new_content = re.sub(r'\bv6\.0\b', '.5', content, flags=re.IGNORECASE)
  
  if new_content != content:
    # 先备份
    shutil.copy2(filepath, filepath + ".bak_v6")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
      f.write(new_content)
    print(f" ✅ 已更新: {os.path.relpath(filepath, BASE)}")
    changed_files += 1

if changed_files == 0:
  print("⚠️ 没有找到 '' 的踪影，可能本来就叫别的，或者已经被改过了。")
else:
  print(f"🎉 版本号替换完成！共修改了 {changed_files} 个文件。")