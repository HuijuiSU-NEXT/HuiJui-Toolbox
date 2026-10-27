# -*- coding: utf-8 -*-
import os, sys, shutil
P = r'D:\Huijui\v4_python\src\huijui_toolbox.py'
if not os.path.exists(P): sys.exit(f"✗ 不存在: {P}")

with open(P, encoding='utf-8') as f: s = f.read()
orig = s

old = '''def get_app_dir():
  """返回 exe 所在目录（兼容 Nuitka onefile / PyInstaller / 源码）"""
  if getattr(sys, 'frozen', False):
    return os.path.dirname(os.path.abspath(sys.executable))
  env = os.environ.get("NUITKA_ONEFILE_BINARY")
  if env:
    return os.path.dirname(os.path.abspath(env))
  if "__compiled__" in globals():
    return os.path.dirname(os.path.abspath(sys.executable))
  return os.path.dirname(os.path.abspath(__file__))'''

new = '''def get_app_dir():
  """返回 exe 所在目录（兼容 Nuitka onefile / PyInstaller / 源码）"""
  # Nuitka onefile 优先级最高：环境变量指向原始 exe 路径
  env = os.environ.get("NUITKA_ONEFILE_BINARY")
  if env:
    return os.path.dirname(os.path.abspath(env))
  # PyInstaller / Nuitka standalone：sys.executable 就是 exe 路径
  if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    return os.path.dirname(os.path.abspath(sys.executable))
  # 源码运行
  return os.path.dirname(os.path.abspath(__file__))'''

if old in s:
  s = s.replace(old, new, 1)
  print("OK get_app_dir 修复")
else:
  print("FAIL 未匹配到 get_app_dir 原函数")
  sys.exit(1)

if s != orig:
  if not os.path.exists(P + ".bak"):
    shutil.copy(P, P + ".bak")
  with open(P, 'w', encoding='utf-8') as f: f.write(s)
  print("写入完成")

import py_compile
py_compile.compile(P, doraise=True)
print("[OK] 语法检查通过")