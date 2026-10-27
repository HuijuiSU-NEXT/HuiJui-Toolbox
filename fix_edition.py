import os
import re
import shutil

BASE = r"D:\Huijui-Toolbox-Next"

files_to_fix = []
for root, dirs, files in os.walk(BASE):
    # 跳过无关目录
    dirs[:] = [d for d in dirs if d not in ('venv', 'venv_android', 'dist', 'build', '__pycache__', '.git')]
    for f in files:
        if f.endswith('.py') and f not in ('fix_edition.py',):
            files_to_fix.append(os.path.join(root, f))

print("🔍 正在全局替换版本标识为 'HuiJui Toolbox Edition' ...")
changed_files = 0

for filepath in files_to_fix:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 干掉 v6.0 / V6.0 / v6 等老版本号
    new_content = re.sub(r'\b[vV]6(\.0)?\b', '', content)
    
    # 2. 把主标题从 "HuiJui Toolbox" 升级为 "HuiJui Toolbox Edition"
    # 避免重复替换变成 "HuiJui Toolbox Edition Edition"
    if "HuiJui Toolbox Edition" not in new_content:
        new_content = new_content.replace("HuiJui Toolbox", "HuiJui Toolbox Edition")

    # 清理多余空格（因为把版本号删了可能会留下双空格）
    new_content = new_content.replace("  ", " ")

    if new_content != content:
        shutil.copy2(filepath, filepath + ".bak_edition")
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_content)
        print(f"  ✅ 已更新: {os.path.relpath(filepath, BASE)}")
        changed_files += 1

if changed_files == 0:
    print("⚠️ 没有找到需要修改的地方。")
else:
    print(f"🎉 换标完成！共修改了 {changed_files} 个文件。Edition 时代开启！")