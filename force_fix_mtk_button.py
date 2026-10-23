# force_fix_mtk_button.py
import os

# ==================== 1. 暴力重写 mode_switch.py ====================
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
                make_btn("重启到 Recovery", ft.Icons.HEALING, f'"{ADB_PATH}" reboot recovery', "正在进入 Recovery..."),
                make_btn("重启到 EDL (9008)", ft.Icons.ERROR, f'"{ADB_PATH}" shell "su -c reboot edl"', "正在进入 9008 模式..."),
                # 添加天玑 BROM 救砖入口 (橙色)
                ft.Container(
                    content=ft.Row([ft.Icon(ft.Icons.BUILD_CIRCLE, color="white"), ft.Text("天玑 BROM 救砖", size=16, color="white", weight=ft.FontWeight.BOLD)]),
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
print("✅ pages/mode_switch.py 已重写，包含天玑按钮！")

# ==================== 2. 修复 main_final.py 注入回调 ====================
with open("main_final.py", "r", encoding="utf-8") as f:
    main_content = f.read()

# 确保导入 mediatek_rescue
if "from pages.mediatek_rescue import build_mediatek_rescue_page" not in main_content:
    main_content = main_content.replace(
        "from pages.drivers import build_drivers_page",
        "from pages.drivers import build_drivers_page\nfrom pages.mediatek_rescue import build_mediatek_rescue_page"
    )

# 确保注册路由
if '"mediatek_rescue": build_mediatek_rescue_page' not in main_content:
    main_content = main_content.replace(
        '"mode_switch": build_mode_switch_page,',
        '"mode_switch": build_mode_switch_page,\n            "mediatek_rescue": build_mediatek_rescue_page,'
    )

# 确保 page 对象挂载了 goto_sub_page 回调，供 mode_switch.py 调用
if 'page.goto_sub_page = goto_sub_page' not in main_content:
    main_content = main_content.replace(
        'def goto_sub_page(route_name):',
        'def goto_sub_page(route_name):\n            page.goto_sub_page = goto_sub_page'
    )

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(main_content)
print("✅ main_final.py 路由与回调已强制修补！")

print("\n🚀 大功告成！请执行 python main_final.py 起飞！")