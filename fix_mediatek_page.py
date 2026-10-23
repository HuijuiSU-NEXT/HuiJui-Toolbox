# fix_mediatek_page.py
import os

code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN_DIR = os.path.join(BASE_DIR, "bin")

def build_mediatek_rescue_page(page: ft.Page, theme_color):
    spflash_path = os.path.join(BIN_DIR, "SPFlashTool", "flash_tool.exe")
    mtkclient_path = os.path.join(BIN_DIR, "MTKClient", "mtk_gui.bat")
    
    spflash_ready = os.path.exists(spflash_path)
    mtkclient_ready = os.path.exists(mtkclient_path)

    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=12, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    def launch_spflash(e):
        if spflash_ready:
            log("> 正在启动 SP Flash Tool...")
            page.update()
            subprocess.Popen([spflash_path], cwd=os.path.dirname(spflash_path), shell=True)
        else:
            log("❌ 未找到 SP Flash Tool，请先配置环境！")
            page.update()

    def launch_mtkclient(e):
        if mtkclient_ready:
            log("> 正在启动 MTKClient GUI...")
            page.update()
            subprocess.Popen([mtkclient_path], cwd=os.path.dirname(mtkclient_path), shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            log("❌ 未找到 MTKClient，请先配置环境！")
            page.update()

    def install_drivers(e):
        log("> 正在查找 MTK USB VCOM 驱动...")
        driver_path = os.path.join(BIN_DIR, "MTK_Drivers", "InstallDriver.exe")
        if os.path.exists(driver_path):
            log("> 正在启动驱动安装程序...")
            subprocess.Popen([driver_path], shell=True)
        else:
            log("💡 未在本地找到驱动安装包。请手动下载安装 MTK USB VCOM Drivers。")
        page.update()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PHONE_ANDROID, color=theme_color, size=28),
                ft.Text("天玑 (MediaTek) 救砖中心", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                ft.Text("环境就绪" if spflash_ready and mtkclient_ready else "环境缺失", color=ft.Colors.GREEN if spflash_ready and mtkclient_ready else ft.Colors.RED, weight=ft.FontWeight.BOLD)
            ]),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    ft.Text("⚠️ 操作指南：", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                    ft.Text("1. 请确保手机已关机。", color="white"),
                    ft.Text("2. 按住【音量上/下键 + 电源键】不松手。", color="white"),
                    ft.Text("3. 将数据线插入电脑，进入 BROM/Preloader 模式。", color="white"),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("一键安装 MTK 驱动", icon=ft.Icons.INSTALL_DESKTOP, on_click=install_drivers, style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE_700, color="white")),
                        ft.ElevatedButton("刷新状态", icon=ft.Icons.REFRESH, on_click=lambda _: page.update(), style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"))
                    ])
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15
            ),
            ft.Container(height=20),
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BUILD_CIRCLE, size=40, color=ft.Colors.GREEN_400 if spflash_ready else ft.Colors.RED_400),
                        ft.Text("SP Flash Tool", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("官方线刷工具" if spflash_ready else "未找到工具", color=ft.Colors.GREY_500),
                        ft.ElevatedButton("启动 SP Flash Tool", on_click=launch_spflash, disabled=not spflash_ready, style=ft.ButtonStyle(bgcolor=theme_color, color="black"))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15, expand=True
                ),
                ft.Container(width=20),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.TERMINAL, size=40, color=ft.Colors.GREEN_400 if mtkclient_ready else ft.Colors.RED_400),
                        ft.Text("MTKClient", size=16, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("开源底层工具箱 (GUI)" if mtkclient_ready else "未找到工具", color=ft.Colors.GREY_500),
                        ft.ElevatedButton("启动 MTKClient", on_click=launch_mtkclient, disabled=not mtkclient_ready, style=ft.ButtonStyle(bgcolor=theme_color, color="black"))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), padding=20, border_radius=15, expand=True
                )
            ], spacing=20),
            ft.Container(height=10),
            log_container
        ], expand=True),
        expand=True, padding=20
    )
'''

with open("pages/mediatek_rescue.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ pages/mediatek_rescue.py 文件已成功生成！")