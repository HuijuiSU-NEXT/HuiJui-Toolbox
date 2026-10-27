import os
import re

TARGET = r"D:\Huijui-Toolbox-Next\main_final.py"
with open(TARGET, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除之前暴力的黑洞代码
bad_code = '''import sys
import os
# 🚨 无黑框防闪退补丁：将标准输出和错误流重定向到黑洞，防止无控制台环境崩溃
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

'''
content = content.replace(bad_code, "")

# 换成一个极度安全的防报错机制（只在需要 print 时拦截，不破坏底层流）
safe_header = '''import sys
import os

# 🚨 安全拦截：在无控制台模式下，防止 print 导致崩溃
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    if sys.stdout is None:
        class DummyStream:
            def write(self, *args, **kwargs): pass
            def flush(self): pass
        sys.stdout = DummyStream()
        sys.stderr = DummyStream()

'''
# 插到文件最前面
if "safe_header" not in content:
    content = safe_header + content
    with open(TARGET, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("✅ 安全防闪退补丁已替换成功！")