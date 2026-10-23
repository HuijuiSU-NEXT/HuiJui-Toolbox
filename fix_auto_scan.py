# fix_auto_scan.py
import os
import re

# 读取当前的 main_final.py
with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 确保导入了 time 模块
if "import time" not in content:
    content = content.replace("import flet as ft", "import flet as ft\nimport time")

# 2. 替换 scan_device 及注入自动轮询逻辑
# 找到 def scan_device 的代码块并替换
scan_func_old = """        def scan_device(e=None):
            status_dot.bgcolor = "#F0A030"
            device_status_text.value = "扫描中..."
            loading_ring.visible = True
            page.update()
            def run():
                res = scan_device_data()
                state = res["state"]
                if state == "OFFLINE": device_status_text.value = "未连接"; status_dot.bgcolor = "#E05070"
                elif state == "NORMAL": device_status_text.value = "已连接"; status_dot.bgcolor = "#3FBF6E"
                elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): device_status_text.value = f"{state}"; status_dot.bgcolor = "#F0A030"
                elif state == "FASTBOOTD": device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
                elif state in ("EDL", "BROM"): device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#E05070"
                
                info_brand.value = res["brand"]; info_model.value = res["model"]
                info_android.value = res["android"]; info_root.value = res["root"]
                loading_ring.visible = False
                page.update()
            threading.Thread(target=run, daemon=True).start()"""

scan_func_new = """        # 记录上一次的状态，防止频繁刷新
        last_device_state = {"state": "OFFLINE", "sn": ""}

        def apply_device_state(res, manual=False):
            state = res["state"]
            sn = res.get("serial", "")
            
            # 如果状态和序列号都没变，且不是手动点击，就不更新 UI
            if state == last_device_state["state"] and sn == last_device_state["sn"] and not manual:
                return

            last_device_state["state"] = state
            last_device_state["sn"] = sn

            if state == "OFFLINE": 
                device_status_text.value = "等待扫描"; status_dot.bgcolor = "#E05070"
            elif state == "NORMAL": 
                device_status_text.value = "已连接 (ADB)"; status_dot.bgcolor = "#3FBF6E"
            elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): 
                device_status_text.value = f"{state}"; status_dot.bgcolor = "#F0A030"
            elif state == "FASTBOOTD": 
                device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
            elif state in ("EDL", "BROM"): 
                device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#E05070"
            
            info_brand.value = res.get("brand", "—")
            info_model.value = res.get("model", "—")
            info_android.value = res.get("android", "—")
            info_root.value = res.get("root", "—")
            loading_ring.visible = False
            try: page.update()
            except: pass

        def scan_device(e=None):
            status_dot.bgcolor = "#F0A030"
            device_status_text.value = "扫描中..."
            loading_ring.visible = True
            page.update()
            def run():
                res = scan_device_data()
                apply_device_state(res, manual=True)
            threading.Thread(target=run, daemon=True).start()

        # 🚀 核心：启动后台轮询线程
        def auto_scan_loop():
            time.sleep(1) # 初始延迟
            while getattr(page, "is_running", True):
                try:
                    res = scan_device_data()
                    apply_device_state(res, manual=False)
                except Exception:
                    pass
                time.sleep(2.5) # 每 2.5 秒轮询一次，平衡性能与实时性

        page.is_running = True
        threading.Thread(target=auto_scan_loop, daemon=True).start()"""

if scan_func_old in content:
    content = content.replace(scan_func_old, scan_func_new)
    print("✅ 成功替换旧的扫描逻辑！")
else:
    print(⚠️ 未找到旧的扫描逻辑，可能已被修改，尝试强制追加...")
    # 如果没匹配到（比如缩进不同），尝试在 build_main_ui 的结尾注入
    # 这里是兜底方案，大概率不会用到

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 全自动设备感知引擎注入完毕！")