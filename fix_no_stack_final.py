# fix_no_stack_final.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# 1. 修复 settings.py 中误删壁纸的逻辑
with open(settings_path, "r", encoding="utf-8") as f:
    s_content = f.read()

old_clear = '''                    # 清理旧壁纸
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
                    for old_f in old_files:
                        if old_f != new_filepath and os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass'''
new_clear = '''                    # 🚨 修复误删：在保存新图之前，先删除旧图
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
                    for old_f in old_files:
                        if os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass'''
s_content = s_content.replace(old_clear, new_clear)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(s_content)
print("✅ settings.py 误删逻辑已修复！")

# 2. 彻底重写 main_final.py 的根节点
with open(main_path, "r", encoding="utf-8") as f:
    m_content = f.read()

# 干掉所有乱七八糟的初始化代码，重写最稳的 Container 方案
old_init_pattern = r'    # 🚨 终极 Stack 方案.*?page\.update\(\)'
new_init = '''    # 🚨 终极方案：绝对全屏 Container，不带任何 Stack
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#0D1017"
    
    # 强制全屏的主容器
    root_container = ft.Container(
        width=page.window.width,
        height=page.window.height,
        bgcolor="#0D1017",
        image=None,
        content=None
    )
    page.add(root_container)
    page.update()'''

m_content = re.sub(old_init_pattern, new_init, m_content, flags=re.DOTALL)

# 重写 update_wallpaper_hot，直接怼给 root_container.image
old_hot_pattern = r'    def update_wallpaper_hot\(\):.*?bg_image\.update\(\)'
new_hot = '''    def update_wallpaper_hot():
        """终极方案：更新 root_container 的背景"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 加时间戳破缓存
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            root_container.image = ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            print(f"🖼️ 已更新背景图: {src}")
        else:
            root_container.image = None
            print("🧹 未找到壁纸文件，清空背景")
        root_container.update()'''

m_content = re.sub(old_hot_pattern, new_hot, m_content, flags=re.DOTALL)

# 重写 refresh_main_ui，把 UI 塞进 root_container.content
old_refresh_pattern = r'    def refresh_main_ui\(tab_index=0\):.*?page\.update\(\)'
new_refresh = '''    def refresh_main_ui(tab_index=0):
        current_tab["idx"] = tab_index
        root_container.content = build_main_ui()
        root_container.update()
        page.update()'''

m_content = re.sub(old_refresh_pattern, new_refresh, m_content, flags=re.DOTALL)

# 确保启动时加载 UI
if "main_container.content = build_main_ui()" in m_content:
    m_content = m_content.replace(
        "main_container.content = build_main_ui()",
        "root_container.content = build_main_ui()"
    )

with open(main_path, "w", encoding="utf-8") as f:
    f.write(m_content)
print("✅ main_final.py 根节点已重写为绝对全屏 Container 模式！")