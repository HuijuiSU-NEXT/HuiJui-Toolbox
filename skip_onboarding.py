# skip_onboarding.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 找到页面启动的代码块
old_startup = '''  if not CFG.get("onboarded", False):
    from ui_onboarding_hyperos_light import HyperOSLightOnboarding
    page.bgcolor = ft.Colors.TRANSPARENT
    page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#E8F0FE", "#FFFFFF"]))
    
    def on_finish():
      page.controls.clear()
      ui_container.content = build_main_ui()
      page.update()
      
    onboarding = HyperOSLightOnboarding(on_finish=on_finish)
    page.add(onboarding)
  else:
    ui_container.content = build_main_ui()
    page.update()'''

# 直接强制进入主界面，干掉 if 判断
new_startup = '''  # 🚨 极客模式：直接强制进入主界面，跳过所有弱智引导页！
  ui_container.content = build_main_ui()
  page.update()'''

if old_startup in content:
  content = content.replace(old_startup, new_startup)
  print("✅ 已成功移除了引导页，实现启动直达主界面！")
else:
  # 如果格式有差异，用正则兜底
  print("⚠️ 未找到精确的引导页代码，尝试正则暴力清除...")
  # 匹配 if not CFG.get("onboarded" 到 else 后面的 page.update()
  pattern = r'  if not CFG\.get\("onboarded".*?page\.update\(\)'
  content = re.sub(pattern, new_startup, content, flags=re.DOTALL)
  print("✅ 已通过正则强行拔除引导页！")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("🎉 修复完毕！请重新打包 EXE。")