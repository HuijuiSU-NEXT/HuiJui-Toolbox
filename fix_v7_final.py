import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到原始的输出打印代码
OLD_CODE = '''              proc = subprocess.run(f'"{adb_path}" devices', shell=True, capture_output=True, text=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
              out = proc.stdout.strip()
              print(f"🔥 [DEBUG] 原始输出: {out}")'''

# 替换为强杀旧服务 + 强制编码 + 打印 stderr 的全能版
NEW_CODE = '''              # 1. 先强杀可能卡死的旧 adb 服务
              subprocess.run(f'"{adb_path}" kill-server', shell=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True)
              
              # 2. 强制使用 utf-8 编码捕获输出
              proc = subprocess.run(f'"{adb_path}" devices', shell=True, capture_output=True, cwd=bin_dir, env=env, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
              out = proc.stdout.decode('utf-8', errors='ignore').strip()
              err = proc.stderr.decode('utf-8', errors='ignore').strip()
              
              print(f"🔥 [DEBUG] STDOUT: {out}")
              print(f"🔥 [DEBUG] STDERR: {err}")'''

if OLD_CODE in content:
    content = content.replace(OLD_CODE, NEW_CODE)
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 成功注入终极透视 Debug 代码！")
else:
    print("❌ 没找到目标代码，请检查是否被改过。")