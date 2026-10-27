import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们要找的旧代码块（根据你截图里的缩进精准匹配）
OLD_CODE = '''    def scan_device(e=None):
      print("🔥 [DEBUG] scan_device 点击触发了！")
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      try: page.update()
      except Exception as ue: print(f"UI刷新失败: {ue}")

      def run():
        try:
          res = scan_device_data()
          print(f"🔥 [DEBUG] 扫描结果: {res}")
          apply_device_state(res, manual=True)
        except Exception as ex:
          print(f"❌ [DEBUG] 扫描异常: {ex}")
          device_status_text.value = f"扫描失败: {ex}"
          status_dot.bgcolor = "#E05070"
          try: page.update()
          except: pass
      threading.Thread(target=run, daemon=True).start()'''

# 纯暴力直连 ADB 的新代码
NEW_CODE = '''    def scan_device(e=None):
      print("🔥 [DEBUG] scan_device 触发！")
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      try: page.update()
      except: pass

      def run():
          import subprocess
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
      threading.Thread(target=run, daemon=True).start()'''

# 替换
if OLD_CODE in content:
    content = content.replace(OLD_CODE, NEW_CODE)
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 成功！scan_device 已替换为纯暴力直连模式！")
else:
    print("❌ 找不到匹配的旧代码。请检查是否多/少空格。")