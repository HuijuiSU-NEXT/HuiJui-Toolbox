import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 要插入的暴力扫描函数
NEW_SCAN_CODE = '''        def scan_device(e=None):
            print("🔥 [DEBUG] scan_device 点击触发了！")
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

# 寻找 scan_device 并替换，直到遇到 def apply_device_state 或下一个同级函数
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "def scan_device(e=None):" in line:
        start_idx = i
    elif start_idx != -1 and line.startswith("        def ") and "scan_device" not in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # 替换
    lines = lines[:start_idx] + [NEW_SCAN_CODE] + lines[end_idx:]
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(lines)
    print("✅ 扫描函数已被成功替换为纯暴力直连模式！")
else:
    print("⚠️ 无法定位 scan_device 函数边界，请检查源码结构。")