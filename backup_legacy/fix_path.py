# -*- coding: utf-8 -*-
import os, re, shutil

SRC = r"D:\Huijui\v4_python\src\huijui_toolbox.py"
if not os.path.exists(SRC):
  print("找不到源码:", SRC); input("按回车退出"); exit(1)

shutil.copy(SRC, SRC + ".bak_path2")
print("已备份到:", SRC + ".bak_path2")

with open(SRC, "r", encoding="utf-8") as f:
  code = f.read()

new_block = '''_cwd = os.getcwd()
    if (getattr(sys, 'frozen', False) or "__compiled__" in globals()) and os.path.isdir(_cwd):
      self.current_dir = _cwd
    else:
      self.current_dir = os.path.dirname(os.path.abspath(__file__))'''

# 模式1：原始代码
p1 = re.compile(
  r"self\.current_dir\s*=\s*os\.path\.dirname\(os\.path\.abspath\(\s*"
  r"sys\.argv\[0\]\s*if\s*getattr\(sys,\s*'frozen',\s*False\)\s*else\s*__file__\s*\)\)",
  re.DOTALL
)

# 模式2：之前 -c 命令替换过的版本
p2 = re.compile(
  r"env_bin\s*=\s*os\.environ\.get\(\s*[\"']NUITKA_ONEFILE_BINARY[\"']\s*\)[\s\S]*?"
  r"self\.current_dir\s*=\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\)"
)

done = False
for i, pat in enumerate((p1, p2), 1):
  code2, n = pat.subn(new_block, code, count=1)
  if n > 0:
    with open(SRC, "w", encoding="utf-8") as f:
      f.write(code2)
    print(f"OK 修复成功（匹配模式 {i}）")
    done = True
    break

if not done:
  print("ERR 没匹配上，请手动打开源码搜索 self.current_dir 并截图发我")

input("按回车退出")