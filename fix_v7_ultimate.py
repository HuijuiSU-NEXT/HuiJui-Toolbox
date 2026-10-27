import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除刚才坏掉的 shell=True 写法，恢复成列表 + env 环境变量注入
OLD_RUN = '''              env = os.environ.copy()
              env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
              proc = subprocess.run(f'"{adb_path}" devices', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

NEW_RUN = '''              env = os.environ.copy()
              env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
              proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

OLD_PROP = '''                      env2 = os.environ.copy()
                      env2["PATH"] = bin_dir + os.pathsep + env2.get("PATH", "")
                      p_res = subprocess.run(f'"{adb_path}" -s {dev} shell getprop {p}', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env2, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''

NEW_PROP = '''                      p_res = subprocess.run([adb_path, "-s", dev, "shell", "getprop", p], capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''

content = content.replace(OLD_RUN, NEW_RUN)
content = content.replace(OLD_PROP, NEW_PROP)

with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
print("✅ 修正完成！已移除 shell=True，恢复列表模式并保留环境变量。")