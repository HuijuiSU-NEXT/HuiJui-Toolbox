# fix_icons.py
import os

mode_code = '''import flet as ft
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
FB_PATH = os.path.join(BASE_DIR, "bin", "fastboot.exe")

def build_mode_switch_page(page: ft.Page, theme_color):
    status = ft.Text("等待操作...", size=14, color=theme_color)
    
    def run_cmd(cmd, msg):
        status.value = msg
        page.update()
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

    def make_btn(text, icon, cmd, msg, color=None):
        bg = ft.Colors.with_opacity(0.1, color) if color else ft.Colors.with_opacity(0.1, theme_color)
        bd = ft.Colors.with_opacity(0.3, color) if color else ft.Colors.with_opacity(0.3, theme_color)
        return ft.Container(
            content=ft.Row([ft.Icon(icon, color="white"), ft.Text(text, size=16, color="white", weight=ft.FontWeight.BOLD)]),
            bgcolor=bg,
            border=ft.border.all(1, bd),
            border_radius=10, padding=20,
            on_click=lambda _: run_cmd(cmd, msg) if cmd else None
        )

    # 获取主程序注入的跳转函数
    def go_mtk(e):
        if hasattr(page, "goto_sub_page"):
            page.goto_sub_page("mediatek_rescue")
        else:
            status.value = "❌ 无法跳转: 主程序未注入回调"
            page.update()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.SWAP_HORIZ, color=theme_color, size=28), ft.Text("模式切换", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10),
            status,
            ft.Container(height=10),
            ft.GridView(expand=1, runs_count=2, max_extent=300, spacing=15, run_spacing=15, controls=[
                make_btn("重启到系统 (System)", ft.Icons.PHONE_ANDROID, f'"{ADB_PATH}" reboot', "正在重启到系统..."),
                make_btn("重启到 Bootloader", ft.Icons.FLASH_ON, f'"{ADB_PATH}" reboot bootloader', "正在进入 Fastboot..."),
                # 换掉长得像 LSPosed 的图标，换成更硬核的恢复图标
                make_btn("重启到 Recovery", ft.Icons.SETTINGS_BACKUP_RESTORE, f'"{ADB_PATH}" reboot recovery', "正在进入 Recovery..."),
                make_btn("重启到 EDL (9008)", ft.Icons.ERROR, f'"{ADB_PATH}" shell "su -c reboot edl"', "正在进入 9008 模式..."),
                # 添加天玑 BROM 救砖入口 (橙色)
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.MEMORY, color="white"), ft.Text("天玑 BROM 救砖", size=16, color="white", weight=ft.FontWeight.BOLD)]),
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_700),
                    border=ft.border.all(1, ft.Colors.ORANGE_700),
                    border_radius=10, padding=20,
                    on_click=go_mtk
                )
            ])
        ], expand=True), expand=True, padding=20
    )
'''

with open("pages/mode_switch.py", "w", encoding="utf-8") as f:
    f.write(mode_code)

print("✅ 图标已替换！Recovery 换成了更硬核的恢复图标，天玑换成了芯片图标！")