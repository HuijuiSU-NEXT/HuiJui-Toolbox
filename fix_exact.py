import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 这是你截图里第 171 行的原始代码（前面14个空格）
OLD_RUN = '''              proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

# 替换后的代码：加入 env 和 shell=True
NEW_RUN = '''              env = os.environ.copy()
              env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
              proc = subprocess.run(f'"{adb_path}" devices', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

# 这是你截图里第 182 行的原始代码（前面22个空格）
OLD_PROP = '''                      p_res = subprocess.run([adb_path, "-s", dev, "shell", "getprop", p], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''

# 替换后的代码
NEW_PROP = '''                      env2 = os.environ.copy()
                      env2["PATH"] = bin_dir + os.pathsep + env2.get("PATH", "")
                      p_res = subprocess.run(f'"{adb_path}" -s {dev} shell getprop {p}', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env2, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''

# 执行替换
changes = 0
if OLD_RUN in content:
    content = content.replace(OLD_RUN, NEW_RUN)
    changes += 1
    print("✅ [1/2] adb devices 调用已修复！")
else:
    print("❌ [1/2] 没找到 adb devices 目标行。")

if OLD_PROP in content:
    content = content.replace(OLD_PROP, NEW_PROP)
    changes += 1
    print("✅ [2/2] getprop 调用已修复！")
else:
    print("❌ [2/2] 没找到 getprop 目标行。")

if changes > 0:
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("🎉 所有代码替换完成，准备打包！")
else:
    print("⚠️ 没有任何替换发生。")