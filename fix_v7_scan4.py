import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
for i, line in enumerate(lines):
    if "def scan_device" in line:
        start = i
        break

if start == -1:
    print("❌ 找不到 def scan_device")
    exit()

# 找到函数结束边界（找下一个缩进 <= 4 的非空行）
end = len(lines)
for i in range(start + 1, len(lines)):
    line = lines[i]
    if not line.strip():
        continue
    indent = len(line) - len(line.lstrip())
    if indent <= 4: # 意味着到了下一个同级函数
        end = i
        break

NEW_SCAN_CODE = '''    def scan_device(e=None):
      print("🔥 [DEBUG] scan_device 触发！")
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      try: page.update()
      except: pass

      def run():
          import subprocess, os
          try:
              bin_dir = os.path.join(BASE_DIR, "bin")
              adb_path = os.path.join(bin_dir, "adb.exe")
              print(f"🔥 [DEBUG] ADB路径: {adb_path}")
              
              proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
              out = proc.stdout.strip()
              print(f"🔥 [DEBUG] 原始输出: {out}")
              
              lines = out.split('\\n')[1:]
              devices = [line.split('\\t')[0] for line in lines if 'device' in line]
              
              if devices:
                  dev = devices[0]
                  res = {"state": "NORMAL", "serial": dev}
                  def get_prop(p):
                      p_res = subprocess.run([adb_path, "-s", dev, "shell", "getprop", p], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
                      return p_res.stdout.strip()
                  
                  res["brand"] = get_prop("ro.product.brand").upper()
                  res["model"] = get_prop("ro.product.model")
                  res["android"] = f"Android {get_prop('ro.build.version.release')}"
                  res["root"] = "已 Root" if "uid=0" in get_prop("su -c id") else "未 Root"
                  print(f"🔥 [DEBUG] 成功获取: {res}")
                  apply_device_state(res, manual=True)
              else:
                  print("❌ [DEBUG] 未检测到设备")
                  apply_device_state({"state": "OFFLINE"}, manual=True)
          except Exception as ex:
              print(f"❌ [DEBUG] 扫描异常: {ex}")
              apply_device_state({"state": "OFFLINE"}, manual=True)
      threading.Thread(target=run, daemon=True).start()

'''

# 用新块替换旧的行范围
new_lines = lines[:start] + [NEW_SCAN_CODE] + lines[end:]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)

print(f"✅ 成功！已将第 {start+1} 行到第 {end} 行的 scan_device 函数替换为纯暴力直连模式！")