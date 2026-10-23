# fix_ultimate_reset.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# 1. 修复 settings.py：确保清除壁纸时，彻底物理删除且强制刷新
with open(settings_path, "r", encoding="utf-8") as f:
    s_content = f.read()

# 暴力重写清除逻辑
old_clear = '''    def clear_wallpaper(e):
        files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
        files.append(os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg"))
        cleared = False
        for f in files:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    cleared = True
                except: pass'''
new_clear = '''    def clear_wallpaper(e):
        import glob
        files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*")) + glob.glob(os.path.join(BASE_DIR, "assets", "custom_wallpaper.*"))
        cleared = False
        for f in files:
            if os.path.exists(f):
                try: 
                    os.remove(f)
                    cleared = True
                    print(f"已物理删除: {f}")
                except Exception as ex: 
                    print(f"删除失败: {f} - {ex}")'''
s_content = s_content.replace(old_clear, new_clear)

# 清除后强制刷主界面
if "page.update_wallpaper_hot()" in s_content and "page.update()" not in s_content.split("page.update_wallpaper_hot()")[1][:50]:
    s_content = s_content.replace(
        "page.update_wallpaper_hot()",
        "page.update_wallpaper_hot()\n            page.update()"
    )
    
with open(settings_path, "w", encoding="utf-8") as f:
    f.write(s_content)
print("✅ settings.py 清除逻辑已彻底硬化！")

# 2. 修复 main_final.py：强制还原最干净的根节点
with open(main_path, "r", encoding="utf-8") as f:
    m_content = f.read()

# 暴力洗掉所有的挂载逻辑，重新写
old_init = '''    # 🚨 终极绝杀：主容器直接充当画布
    main_container = ft.Container(
        expand=True, 
        bgcolor="#0D1017", # 兜底深色
        # 背景图将会在这里动态挂载
    )
    page.add(main_container)
    page.update()'''
    
new_init = '''    # 🚨 回归最稳系统底层方案
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.TRANSPARENT
    
    main_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
    page.add(main_container)
    page.update()'''

if old_init in m_content:
    m_content = m_content.replace(old_init, new_init)
else:
    # 兜底替换
    m_content = re.sub(r'    # 🚨 终极绝杀.*?page\.update\(\)', new_init, m_content, flags=re.DOTALL)

# 修复 update_wallpaper_hot
old_hot = '''    def update_wallpaper_hot():
        """终极方案：把背景图塞给 Container 的 image 属性，完美铺满"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            # 加时间戳破缓存
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            # 🚨 核心：直接给 main_container 赋 image
            main_container.image = ft.DecorationImage(
                src=src, 
                fit=ft.ImageFit.COVER
            )
            main_container.bgcolor = None # 移除兜底底色，露出壁纸
            print(f"🖼️ 已更新主容器壁纸: {src}")
        else:
            main_container.image = None
            main_container.bgcolor = "#0D1017"
            print("❌ 未找到壁纸文件，清空背景")
        main_container.update()'''
        
new_hot = '''    def update_wallpaper_hot():
        """直接调用系统级背景，避开任何 UI 层的尺寸计算 bug"""
        import glob
        import time
        
        all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
        if all_files:
            latest = max(all_files, key=os.path.getctime)
            src = f"{os.path.basename(latest)}?t={int(time.time())}"
            
            page.decoration = ft.BoxDecoration(
                image=ft.DecorationImage(src=src, fit=ft.ImageFit.COVER)
            )
            print(f"🖼️ 已更新系统级背景: {src}")
        else:
            page.decoration = None
            print("🧹 已彻底清空背景")
            
        page.update()'''
        
m_content = m_content.replace(old_hot, new_hot)

# 确保 UI 最终返回的是个透明的全屏 Container
old_return = '''        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        # UI 整体透明，透出底下的 main_container 壁纸
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''
        
new_return = '''        # 强制外层 Container 撑满，绝对不缩水
        main_layout = ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)
        return ft.Container(content=main_layout, expand=True, bgcolor=ft.Colors.TRANSPARENT)'''

if old_return in m_content:
    m_content = m_content.replace(old_return, new_return)
else:
    m_content = re.sub(r'        main_layout = ft\.Row\(.*?return ft\.Container.*?TRANSPARENT\)', new_return, m_content, flags=re.DOTALL)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(m_content)
print("✅ main_final.py 根节点已彻底净化！")