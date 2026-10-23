# fix_cfg_bug.py
import os
import re

print("=== 🔍 正在探测 CFG 对象的正确赋值方法 ===")

# 尝试导入 CFG
try:
    from core_api import CFG
    print(f"CFG 对象类型: {type(CFG)}")
    print(f"CFG 包含的方法: {[m for m in dir(CFG) if not m.startswith('__')]}")
    
    # 尝试推理赋值方式
    if hasattr(CFG, "set"):
        assign_method = "set"
        print("💡 找到推荐赋值方法: CFG.set(key, value)")
    elif hasattr(CFG, "update"):
        assign_method = "update"
        print("💡 找到推荐赋值方法: CFG.update(key, value)")
    else:
        assign_method = "attr"
        print("💡 没找到专用的 set/update 方法，尝试使用属性赋值 (CFG.key = value)")
except Exception as e:
    print(f"❌ 导入 CFG 失败: {e}")
    assign_method = "attr"

# 修复 settings.py
settings_path = "pages/settings.py"
if os.path.exists(settings_path):
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换掉所有的 CFG["xxx"] = yyy
    # 匹配形如 CFG["theme_color"] = hex_val
    matches = re.findall(r'CFG\[[\'"](\w+)[\'"]\]\s*=\s*([^\n]+)', content)
    print(f"🔍 发现 {len(matches)} 处错误赋值，正在修复...")

    for key, val in matches:
        if assign_method == "set":
            old = f'CFG["{key}"] = {val}'
            old2 = f"CFG['{key}'] = {val}"
            new = f'CFG.set("{key}", {val})'
            content = content.replace(old, new).replace(old2, new)
        elif assign_method == "update":
            old = f'CFG["{key}"] = {val}'
            old2 = f"CFG['{key}'] = {val}"
            new = f'CFG.update("{key}", {val})'
            content = content.replace(old, new).replace(old2, new)
        else:
            old = f'CFG["{key}"] = {val}'
            old2 = f"CFG['{key}'] = {val}"
            new = f'setattr(CFG, "{key}", {val})'
            content = content.replace(old, new).replace(old2, new)

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ pages/settings.py 修复完成！")
else:
    print("❌ 找不到 pages/settings.py")