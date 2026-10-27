# -*- coding: utf-8 -*-
import shutil

SRC = r"D:\Huijui\v4_python\src\huijui_toolbox.py"
shutil.copy(SRC, SRC + ".bak_line210")
print("已备份:", SRC + ".bak_line210")

with open(SRC, "r", encoding="utf-8") as f:
  lines = f.readlines()

# 找到错误行
target = None
for i, line in enumerate(lines):
  if 'onefile_' in line and 'temp' in line.lower() and 'if' in line:
    target = i
    break

if target is None:
  print("ERR 没找到目标行，请手动截图")
else:
  print(f"原第 {target+1} 行: {lines[target].rstrip()}")
  # 用简单字符串替换，避免转义
  lines[target] = '      if "onefile_" in low or "temp" in low or "/tmp/" in low:\n'
  with open(SRC, "w", encoding="utf-8") as f:
    f.writelines(lines)
  print("OK 修复成功")

input("按回车退出")