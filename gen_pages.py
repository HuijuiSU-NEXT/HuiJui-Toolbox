# gen_pages.py
import os

# 确保 pages 文件夹存在
os.makedirs("pages", exist_ok=True)

# 确保 __init__.py 存在
open("pages/__init__.py", "a").close()

# 待生成的页面列表
pages_to_create = {
    "module_repo": "模块仓库",
    "terminal": "高级终端",
    "scrcpy": "Scrcpy 投屏",
    "backup": "分区备份",
    "wireless_adb": "无线调试",
    "mode_switch": "模式切换",
    "drivers": "驱动环境",
    "rescue": "急救中心"
}

template = """import flet as ft
import threading

class {class_name}(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        # 基础占位 UI，防止空白
        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CONSTRUCTION, color=ft.Colors.AMBER), 
                ft.Text("{title} - 开发中", size=24, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("等待接入核心逻辑...", color=ft.Colors.GREY_500)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # 初始化底层逻辑
        self.init_logic()

    def init_logic(self):
        # 🚨 铁律 1：在这里初始化非阻塞线程或组件
        pass
"""

for filename, title in pages_to_create.items():
    class_name = "".join([word.capitalize() for word in filename.split("_")]) + "Page"
    filepath = f"pages/{filename}.py"
    
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(template.format(class_name=class_name, title=title))
        print(f"✅ 成功生成: {filepath}")
    else:
        print(f"⚠️ 已存在，跳过: {filepath}")

print("🎉 所有页面骨架生成完毕，兄弟冲！")