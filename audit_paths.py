# audit_paths.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")

# 需要检查的底层核心工具
TARGET_TOOLS = [
  "adb.exe", "fastboot.exe", "scrcpy.exe", "payload-dumper-go.exe", 
  "ffmpeg.exe", "ghostlock-extract.exe", "ghostlock-bin", 
  "mtk_gui.bat", "QFIL.exe", "flash_tool.exe", "ksud.exe"
]

# 要扫描的代码目录和文件
SCAN_DIRS = ["pages", "core"]
SCAN_FILES = ["main_final.py"]

def audit_file(filepath):
  issues = []
  with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()
    
  for i, line in enumerate(lines, 1):
    # 跳过注释行
    if line.strip().startswith("#"):
      continue
      
    for tool in TARGET_TOOLS:
      if tool in line:
        # 检查是否使用了正确的 os.path.join(BASE_DIR, "bin", ...) 或 BIN_DIR
        if "BIN_DIR" in line or 'os.path.join(BASE_DIR, "bin"' in line or "os.path.join(BASE_DIR, 'bin'" in line:
          # 正常
          pass
        else:
          # 如果是直接硬编码了 "bin/xxx.exe" 或者 "xxx.exe"
          if f'"{tool}"' in line or f"'{tool}'" in line or f'bin/{tool}' in line or f'bin\\\\{tool}' in line:
            issues.append(f" ⚠️ 第 {i} 行: {line.strip()}")
  return issues

print("=" * 60)
print("🔍 正在审计底层工具路径 (Base Dir: {})".format(BASE_DIR))
print("=" * 60)

has_issues = False
for scan_dir in SCAN_DIRS:
  dir_path = os.path.join(BASE_DIR, scan_dir)
  if not os.path.exists(dir_path):
    continue
  for filename in os.listdir(dir_path):
    if filename.endswith(".py"):
      filepath = os.path.join(dir_path, filename)
      issues = audit_file(filepath)
      if issues:
        has_issues = True
        print(f"\n📄 {scan_dir}/{filename}:")
        for issue in issues:
          print(issue)

for filename in SCAN_FILES:
  filepath = os.path.join(BASE_DIR, filename)
  if os.path.exists(filepath):
    issues = audit_file(filepath)
    if issues:
      has_issues = True
      print(f"\n📄 {filename}:")
      for issue in issues:
        print(issue)

print("\n" + "=" * 60)
if has_issues:
  print("🚨 发现以上代码可能存在路径硬编码风险，建议修复！")
else:
  print("🎉 完美！所有底层工具调用均使用了动态相对路径，打包后绝对稳！")
print("=" * 60)