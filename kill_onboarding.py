# kill_onboarding.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 寻找并干掉引导页的加载逻辑
# 之前的逻辑通常是 if not CFG.get("onboarded", False): ... else: ...
# 或者包含 HyperOSLightOnboarding 的代码块
pattern = r'    if not CFG\.get\("onboarded".*?page\.update\(\)'

new_startup = '''    # 🚨 彻底斩断引导页，直接启动主界面
    ui_container.content = build_main_ui()
    page.update()'''

# 暴力替换
content = re.sub(pattern, new_startup, content, flags=re.DOTALL)

# 如果没有正则匹配到（可能被其他脚本改过了），直接替换包含 on_finish 的代码块
if "HyperOSLightOnboarding" in content:
    pattern2 = r'    if not CFG\.get\("onboarded".*?else:\s+ui_container\.content = build_main_ui\(\)\s+page\.update\(\)'
    content = re.sub(pattern2, new_startup, content, flags=re.DOTALL)
    print("✅ 已通过兜底正则强制移除了引导页逻辑！")
else:
    print("✅ 引导页逻辑已彻底清除！")

# 2. 确保强行写入 CFG，防止其他模块读取到 False 又触发引导
# 这里直接把 onboarded 状态强行置为 True
if "CFG.set(\"onboarded\", True)" not in content:
    content = content.replace(
        'def main(page: ft.Page):\n',
        'def main(page: ft.Page):\n    CFG.set("onboarded", True)\n    CFG.save()\n'
    )
    print("✅ 已强制修改配置：onboarded=True")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 斩断完毕！现在可以重新打包了。")