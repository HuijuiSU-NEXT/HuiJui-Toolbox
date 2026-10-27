# final_sanity_check.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pages_dir = os.path.join(BASE_DIR, "pages")

# 扫描目标
TARGET_FILES = [os.path.join(BASE_DIR, "main_final.py")]
if os.path.exists(pages_dir):
  for f in os.listdir(pages_dir):
    if f.endswith(".py") and not f.startswith("__"):
      TARGET_FILES.append(os.path.join(pages_dir, f))

print("=" * 65)
print("🚀 正在执行 HuiJui Toolbox Edition 终极功能安检...")
print("=" * 65)

issues_found = 0

# 1. UI 违规参数检查（Flet 0.28.3 铁律）
ui_rules = {
  r'ft\.Text\([^)]*shadow=': "ft.Text 不支持 shadow 参数，请使用 Stack 或移除。",
  r'ft\.Text\([^)]*line_height=': "ft.Text 不支持 line_height 参数，请移除。",
  r'ft\.Column\([^)]*padding=': "ft.Column 不支持 padding 参数，请用 Container 包裹。",
  r'ft\.Row\([^)]*padding=': "ft.Row 不支持 padding 参数，请用 Container 包裹。",
  r'ft\.ButtonStyle\([^)]*border=': "ft.ButtonStyle 不支持 border 参数，请改用 side。",
  r'update\(bgcolor=': "update() 不支持传参，请先赋值再调用 update()。",
}

for filepath in TARGET_FILES:
  if not os.path.exists(filepath): continue
  with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()
    filename = os.path.basename(filepath)
    
    for pattern, msg in ui_rules.items():
      matches = re.finditer(pattern, content)
      for m in matches:
        line_num = content[:m.start()].count('\n') + 1
        print(f"🚨 [UI API 违规] {filename} (第 {line_num} 行): {msg}")
        issues_found += 1

# 2. 线程阻塞与黑底残留扫描
for filepath in TARGET_FILES:
  if not os.path.exists(filepath): continue
  with open(filepath, "r", encoding="utf-8") as f:
    filename = os.path.basename(filepath)
    lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
      # 检查是否在主线程跑阻塞命令 (启发式判断：有 subprocess 但没看到 threading)
      if ("subprocess.Popen" in line or "subprocess.run" in line) and "threading" not in line:
        # 往上看 20 行，看是否被包在 threading.Thread 里
        context = "".join(lines[max(0, i-20):i])
        if "threading.Thread" not in context and "def run" not in context:
          print(f"⚠️ [线程阻塞风险] {filename} (第 {i} 行): 发现 subprocess 调用，请确保它在子线程中执行。")
          issues_found += 1
          
      # 检查是否还有残留的纯黑底色导致违和
      if "bgcolor=ft.Colors.BLACK" in line and "log_bg" not in line:
        print(f"🎨 [UI 视觉残留] {filename} (第 {i} 行): 发现纯黑底色，建议替换为 page.ui_style['log_bg']。")
        issues_found += 1

# 3. 检查关键依赖文件是否就绪
critical_paths = [
  os.path.join(BASE_DIR, "assets", "logo.png"),
  os.path.join(BASE_DIR, "assets", "logo.ico"),
  os.path.join(BASE_DIR, "assets", "default_wallpaper.gif"),
  os.path.join(BASE_DIR, "assets", "fonts", "MiSans-Regular.ttf"),
  os.path.join(BASE_DIR, "bin", "adb.exe")
]
for p in critical_paths:
  if not os.path.exists(p):
    print(f"❌ [资源缺失] 找不到必需文件: {p}")
    issues_found += 1

# 4. 检查导入的模块是否完整
try:
  import flet
  import flet_video
  from PIL import Image
  print("✅ [依赖检查] Flet, flet_video, PIL 均已安装。")
except ImportError as e:
  print(f"❌ [依赖缺失] {e}")
  issues_found += 1

print("=" * 65)
if issues_found == 0:
  print("🎉 太棒了！未发现明显的致命隐患，所有功能代码稳健！")
else:
  print(f"🔧 发现 {issues_found} 处潜在隐患，请根据上方提示逐一排查！")
print("=" * 65)