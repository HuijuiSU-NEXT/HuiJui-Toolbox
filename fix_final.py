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

end = len(lines)
for i in range(start + 1, len(lines)):
    if not lines[i].strip():
        continue
    indent = len(lines[i]) - len(lines[i].lstrip())
    if indent <= 4:
        end = i
        break

# 这是超级无敌的无 shell 的干净版本
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
              env = os.environ.copy()
              env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
              
              print(f"🔥 [DEBUG] ADB路径: {adb_path}")
              
              # 绝对是列表模式，绝对没有 shell=True！
              proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
              out = proc.stdout.strip()
              print(f"🔥 [DEBUG] STDOUT: {out}")
              
              lines_out = out.split('\\n')[1:]
              devices = [line.split('\\t')[0] for line in lines_out if 'device' in line]
              
              if devices:
                  dev = devices[0]
                  res = {"state": "NORMAL", "serial": dev}
                  def get_prop(p):
                      p_res = subprocess.run([adb_path, "-s", dev, "shell", "getprop", p], capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)
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

new_lines = lines[:start] + [NEW_SCAN_CODE] + lines[end:]

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.writelines(new_lines)

print(f"✅ 强力覆盖成功！第 {start+1} 行到 {end} 行已被彻底重写，没有任何 shell=True。")