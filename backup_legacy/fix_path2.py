# -*- coding: utf-8 -*-
import os, re, shutil

SRC = r"D:\Huijui\v4_python\src\huijui_toolbox.py"
shutil.copy(SRC, SRC + ".bak_getappdir")
print("已备份:", SRC + ".bak_getappdir")

with open(SRC, "r", encoding="utf-8") as f:
  code = f.read()

# 匹配整个 get_app_dir 函数
pat = re.compile(r"def get_app_dir\(\):.*?(?=\ndef |\nclass |\Z)", re.DOTALL)

new_func = '''def get_app_dir():
  """返回 exe 所在目录（Nuitka onefile / PyInstaller / 源码都兼容）"""
  # 1. Nuitka onefile 环境变量（新版有效）
  env = os.environ.get("NUITKA_ONEFILE_BINARY")
  if env and os.path.exists(env):
    return os.path.dirname(os.path.abspath(env))
  # 2. 打包后：如果 sys.executable 落在临时目录，用 cwd
  if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    low = exe_dir.lower()
    if "onefile_" in low or "\\\\temp\\\\" in low or "/tmp/" in low:
      cwd = os.getcwd()
      if "onefile_" not in cwd.lower():
        return cwd
    return exe_dir
  # 3. 源码运行
  return os.path.dirname(os.path.abspath(__file__))

'''
new_code, n = pat.subn(new_func, code, count=1)
if n == 0:
  print("ERR 没匹配到 get_app_dir 函数")
else:
  with open(SRC, "w", encoding="utf-8") as f:
    f.write(new_code)
  print("OK 修复成功")
input("按回车退出")