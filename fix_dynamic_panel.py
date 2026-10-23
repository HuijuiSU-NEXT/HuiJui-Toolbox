# fix_dynamic_panel.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 找到当前的状态更新函数 apply_device_state，并进行替换
# 使用正则匹配整个函数块
pattern = r"        def apply_device_state\(res, manual=False\):.*?try: page\.update\(\)\n            except: pass"

new_func = """        def apply_device_state(res, manual=False):
            state = res["state"]
            sn = res.get("serial", "")
            
            if state == last_state["state"] and sn == last_state["sn"] and not manual:
                return

            last_state["state"] = state
            last_state["sn"] = sn

            # 基础状态灯与文字
            if state == "OFFLINE": 
                device_status_text.value = "等待扫描"; status_dot.bgcolor = "#E05070"
            elif state == "NORMAL": 
                device_status_text.value = "已连接 (ADB)"; status_dot.bgcolor = "#3FBF6E"
            elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): 
                device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#F0A030"
            elif state == "FASTBOOTD": 
                device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
            elif state in ("EDL", "BROM"): 
                device_status_text.value = f"{state} 紧急模式"; status_dot.bgcolor = "#E05070"
            
            # 动态面板变阵逻辑
            if state == "OFFLINE":
                info_brand.value = "—"; info_model.value = "—"; info_android.value = "—"; info_root.value = "—"
                
            elif state == "NORMAL":
                info_brand.value = res.get("brand", "—")
                info_model.value = res.get("model", "—")
                info_android.value = res.get("android", "—")
                info_root.value = res.get("root", "—")
                
            elif state in ("FASTBOOT", "FASTBOOTD"):
                info_brand.value = "序列号 (SN)"
                info_model.value = sn if sn else "未知"
                info_android.value = "底层状态"
                info_root.value = "已进入 Bootloader" if state == "FASTBOOT" else "已进入 Fastbootd"
                
            elif state in ("EDL", "BROM"):
                info_brand.value = "芯片平台"
                info_model.value = "高通 (Qualcomm)" if state == "EDL" else "联发科 (MediaTek)"
                info_android.value = "端口状态"
                info_root.value = "等待工具接管"

            loading_ring.visible = False
            try: page.update()
            except: pass"""

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_func, content, flags=re.DOTALL)
    with open("main_final.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 动态面板变阵逻辑已注入！重启后测试模式切换。")
else:
    print("⚠️ 未找到匹配的 apply_device_state 函数，请检查 main_final.py 是否被改过。")