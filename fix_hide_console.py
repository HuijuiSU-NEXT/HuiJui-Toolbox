# fix_hide_console.py
import os

with open("pages/scrcpy.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. 替换启动 Scrcpy 的方式，隐藏控制台并丢弃标准输出
old_launch = "subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)"
new_launch = "subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)"

if old_launch in code:
    code = code.replace(old_launch, new_launch)
    print("✅ 成功替换底层启动命令，隐藏黑框！")
else:
    print("⚠️ 未找到旧启动命令，可能已经修改过。")

# 2. 微调一下 UI，既然没黑框了，把输出日志也改一下
code = code.replace('log("✅ Scrcpy 已启动。")', 'log("✅ Scrcpy 已启动，纯画面无控制台模式。")')

with open("pages/scrcpy.py", "w", encoding="utf-8") as f:
    f.write(code)

print("🎉 补丁注入完成！")