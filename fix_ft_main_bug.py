# fix_ft_main_bug.py
import os

with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 把该死的 ft.main 换回 ft.app
content = content.replace("ft.main(target=main, assets_dir=\"assets\")", "ft.app(target=main, assets_dir=\"assets\")")

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 拼写错误修复完毕！ft.main 已替换为 ft.app。")