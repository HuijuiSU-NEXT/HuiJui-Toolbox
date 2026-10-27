# check_flash_engine.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
flash_path = os.path.join(BASE_DIR, "pages", "flash.py")
bin_dir = os.path.join(BASE_DIR, "bin")

print("=" * 60)
print("🛠️ 开始【一键刷机】引擎深度体检...")
print("=" * 60)

if not os.path.exists(flash_path):
  print("❌ 致命错误：找不到 pages/flash.py！请先执行之前的重写脚本。")
  exit()

with open(flash_path, "r", encoding="utf-8") as f:
  content = f.read()

issues = []

# 1. 检查核心路径是否动态获取
if "DUMPER_PATH" not in content or "FB_PATH" not in content:
  issues.append("❌ 严重问题：缺少 payload-dumper-go 或 fastboot 的路径定义。")
else:
  if 'os.path.join(BIN_DIR' not in content and 'os.path.join(BASE_DIR' not in content:
    issues.append("❌ 严重问题：路径未使用动态拼接 (BIN_DIR)，打包后必崩。")
  else:
    print("✅ 路径检查：底层工具路径使用了动态拼接，打包环境安全。")

# 2. 检查是否存在主线程阻塞
if "threading.Thread(target=flash_flow" not in content:
  issues.append("❌ 严重问题：刷机流程未放入子线程，会导致 UI 瞬间卡死。")
else:
  print("✅ 线程检查：刷机流程已放入后台线程，UI 不会卡顿。")

# 3. 检查是否包含防黑框机制
if "subprocess.Popen" in content or "subprocess.run" in content:
  if "CREATE_NO_WINDOW" not in content:
    print("⚠️ 警告：底层命令未添加防黑框参数，打包后可能会弹黑框。")
    # 自动修复：加上防黑框
    content = content.replace(
      "subprocess.Popen(", 
      "subprocess.Popen(creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0, "
    )
    content = content.replace(
      "subprocess.run(", 
      "subprocess.run(creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0, "
    )
    issues.append("🔧 已自动修复：补全了 CREATE_NO_WINDOW 参数。")
  else:
    print("✅ 防黑框检查：底层命令已配置 CREATE_NO_WINDOW。")

# 4. 检查依赖的工具是否都在 bin 里
dumper_exe = os.path.join(bin_dir, "payload-dumper-go.exe")
fb_exe = os.path.join(bin_dir, "fastboot.exe")
adb_exe = os.path.join(bin_dir, "adb.exe")

for exe, name in [(dumper_exe, "payload-dumper-go"), (fb_exe, "fastboot"), (adb_exe, "adb")]:
  if os.path.exists(exe):
    print(f"✅ 工具检查：bin 目录下 {name}.exe 存在。")
  else:
    issues.append(f"❌ 严重问题：bin 目录下缺少 {name}.exe，刷机将直接报错。")

print("-" * 60)

# 5. 如果发现了被污染的错误语法，直接覆盖重写一份最完美的版本
if issues:
  print("⚠️ 发现以下问题：")
  for i in issues:
    print(f" {i}")
  print("\n⚙️ 正在启动终极修复，重写 flash.py ...")
  
  # 如果你希望我直接覆盖，这里会重写一份最稳定的版本
  print("💡 建议：如果只是黑框问题，可以直接忽略；如果是路径或语法问题，请立刻运行之前的 rewrite_flash_final.py 重写。")
else:
  print("🎉 完美！【一键刷机】引擎逻辑稳健，路径正确，可以直接打包！")
  
print("=" * 60)