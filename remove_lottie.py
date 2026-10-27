# remove_lottie.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
  content = f.read()

# 1. 删除 Lottie 动画代码
old_lottie = '''        ft.Container(expand=True),
        ft.Row([fl.Lottie(src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json", width=140, height=140, animate=True)], alignment=ft.MainAxisAlignment.CENTER)'''

new_lottie = '''        ft.Container(expand=True)'''

if old_lottie in content:
  content = content.replace(old_lottie, new_lottie)
  print("✅ 已成功移除右下角的 Lottie 3D 动画！")
else:
  # 兜底正则替换
  pattern = r'ft\.Row\(\[fl\.Lottie\(.*?\]\)'
  if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, '', content)
    print("✅ 已通过正则完成兜底移除！")
  else:
    print("⚠️ 未找到 Lottie 代码，可能已经被改过了。")

# 顺便移除顶部不再使用的 flet_lottie 导入（可选，防报错）
content = content.replace("import flet_lottie as fl\n", "")

with open(main_path, "w", encoding="utf-8") as f:
  f.write(content)

print("🎉 移除完毕！请运行 python main_final.py 查看极简效果。")