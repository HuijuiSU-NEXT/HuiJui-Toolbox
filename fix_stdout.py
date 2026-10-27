import os

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"

with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 如果已经注入了就直接跳过
if "sys.stdout = open(os.devnull, 'w')" not in content:
    # 强制插在文件最开头
    inject_code = '''import sys
import os
# 🚨 无黑框防闪退补丁：将标准输出和错误流重定向到黑洞，防止无控制台环境崩溃
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

'''
    content = inject_code + content
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 黑洞补丁注入成功！")
else:
    print("⚠️ 黑洞补丁已存在。")