# fix_ui_title.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
dashboard_path = os.path.join(BASE_DIR, "pages", "dashboard.py")

# 🚨 这里修改你想要的软件名字
NEW_TITLE = "HuiJui Toolbox"
NEW_SUBTITLE = "Matrix Engine"

# 1. 修改 main_final.py 窗口标题和侧边栏文字
if os.path.exists(main_path):
    with open(main_path, "r", encoding="utf-8") as f:
        m_content = f.read()
    
    # 改窗口标题
    m_content = m_content.replace('page.title = "HuiJui Core · Matrix"', f'page.title = "{NEW_TITLE}"')
    
    # 改右侧边栏的文字 (HuiJui Core 改为 NEW_TITLE，Matrix Engine 保持不变)
    m_content = m_content.replace('ft.Text("HuiJui Core", size=16, weight=ft.FontWeight.W_900, color="white")', f'ft.Text("{NEW_TITLE}", size=16, weight=ft.FontWeight.W_900, color="white")')
    
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(m_content)
    print(f"✅ 窗口标题已改为: {NEW_TITLE}")

# 2. 修改 pages/dashboard.py 主页上的大标题
if os.path.exists(dashboard_path):
    with open(dashboard_path, "r", encoding="utf-8") as f:
        d_content = f.read()
    
    # 改大标题
    d_content = d_content.replace('ft.Text("Matrix Dashboard", size=30, weight=ft.FontWeight.BOLD, color="white")', f'ft.Text("{NEW_TITLE}", size=30, weight=ft.FontWeight.BOLD, color="white")')
    
    # 改副标题
    d_content = d_content.replace('ft.Text("原生 GPU 渲染 · 分布式极客中心", color=ft.Colors.GREY_400)', f'ft.Text("{NEW_SUBTITLE} · 原生 GPU 渲染", color=ft.Colors.GREY_400)')
    
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(d_content)
    print(f"✅ 主页大标题已改为: {NEW_TITLE}")

print("🚀 修复完毕！请运行 python main_final.py 查看效果。")