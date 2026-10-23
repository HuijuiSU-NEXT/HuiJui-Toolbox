# fix_recovery_panel.py
import os
import re

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 定位 apply_device_state 里的分支逻辑
pattern = r'            # 动态面板变阵逻辑.*?if state == "OFFLINE":.*?elif state in \("EDL", "BROM"\):'

new_branch = """            # 动态面板变阵逻辑
            if state == "OFFLINE":
                info_brand.value = "—"; info_model.value = "—"; info_android.value = "—"; info_root.value = "—"
                
            elif state in ("RECOVERY", "SIDELOAD"):
                info_brand.value = "当前模式"
                info_model.value = "Recovery 恢复模式" if state == "RECOVERY" else "Sideload 侧载模式"
                info_android.value = "设备状态"
                info_root.value = "ADB 已连接" if sn else "未获取"
                
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
                
            elif state in ("EDL", "BROM"):"""

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_branch, content, flags=re.DOTALL)
    with open("main_final.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Recovery 模式专属面板变阵逻辑已注入！")
else:
    print("⚠️ 正则匹配失败，请手动检查 main_final.py 中的 apply_device_state 函数。")