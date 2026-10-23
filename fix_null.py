import os

flash_code = """import flet as ft

def build_flash_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Column([
            ft.Text("一键刷机 - 功能开发中", size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.ProgressRing(color=theme_color)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True
    )
"""

temp_code = """import flet as ft

def build_temp_root_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Text("临时 Root - 功能开发中", size=24, color="white"),
        expand=True
    )
"""

scan_code = """import flet as ft

def build_scan_page(page: ft.Page, theme_color):
    return ft.Container(
        content=ft.Text("扫描设备 - 功能开发中", size=24, color="white"),
        expand=True
    )
"""

# 强制以 UTF-8 写入，彻底干掉 null bytes
with open("pages/flash.py", "w", encoding="utf-8") as f:
    f.write(flash_code)

with open("pages/temp_root.py", "w", encoding="utf-8") as f:
    f.write(temp_code)

with open("pages/scan.py", "w", encoding="utf-8") as f:
    f.write(scan_code)

print("✅ 清洗完毕！Null bytes 已彻底清除！")