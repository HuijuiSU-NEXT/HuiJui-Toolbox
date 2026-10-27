import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们要精准替换的旧代码片段
OLD_CODE = '''                  proc = subprocess.run([adb_path, "devices"], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

# 注入 PATH 环境变量和 shell=True 的新代码片段
NEW_CODE = '''                  env = os.environ.copy()
                  env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
                  proc = subprocess.run(f'"{adb_path}" devices', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)'''

if OLD_CODE in content:
    content = content.replace(OLD_CODE, NEW_CODE)
    # 为了保险，把 get_prop 里面的调用也改一下
    OLD_PROP = '''                      p_res = subprocess.run([adb_path, "-s", dev, "shell", "getprop", p], capture_output=True, text=True, cwd=bin_dir, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''
    NEW_PROP = '''                      env2 = os.environ.copy()
                      env2["PATH"] = bin_dir + os.pathsep + env2.get("PATH", "")
                      p_res = subprocess.run(f'"{adb_path}" -s {dev} shell getprop {p}', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env2, creationflags=subprocess.CREATE_NO_WINDOW, timeout=5)'''
    content = content.replace(OLD_PROP, NEW_PROP)

    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 补丁成功注入！已将 PATH 环境变量和 shell=True 加入扫描函数！")
else:
    print("❌ 没找到目标代码，可能已经被改过了。")