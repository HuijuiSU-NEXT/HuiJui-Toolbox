import flet as ft
import time
import subprocess
import os
import flet_lottie as fl
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
ADB_PATH = os.path.join(BIN_DIR, "adb.exe")

def main(page: ft.Page):
    page.title = "HuiJui Core · Matrix"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 1300
    page.window_height = 850
    page.bgcolor = "#090A0F"

    THEME_COLOR = "#39C5BB"
    
    status_dot = ft.Container(width=8, height=8, bgcolor="#E05070", border_radius=4)
    device_status_text = ft.Text("等待扫描", size=13, color="#A0ABC0")
    loading_ring = ft.ProgressRing(width=18, height=18, stroke_width=2, color=THEME_COLOR, visible=False)
    
    info_brand = ft.Text("—", color="white", size=14)
    info_model = ft.Text("—", color="white", size=14)
    info_android = ft.Text("—", color="white", size=14)
    info_root = ft.Text("—", color="white", size=14)

    def scan_device(e):
        status_dot.bgcolor = "#F0A030"
        device_status_text.value = "正在扫描..."
        loading_ring.visible = True
        page.update()

        def run_scan():
            try:
                out = subprocess.check_output(
                    [ADB_PATH, "devices"], text=True, cwd=BIN_DIR, creationflags=0x08000000
                )
                lines = out.strip().split("\n")[1:]
                devices = [line.split("\t")[0] for line in lines if "device" in line]
                
                if devices:
                    dev = devices[0]
                    device_status_text.value = f"已连接: {dev}"
                    status_dot.bgcolor = "#3FBF6E"
                    
                    def get_prop(prop):
                        return subprocess.check_output(
                            [ADB_PATH, "-s", dev, "shell", "getprop", prop],
                            text=True, cwd=BIN_DIR, creationflags=0x08000000
                        ).strip()

                    info_brand.value = get_prop("ro.product.brand").upper()
                    info_model.value = get_prop("ro.product.model")
                    info_android.value = f"Android {get_prop('ro.build.version.release')}"
                    
                    root_check = subprocess.check_output(
                        [ADB_PATH, "-s", dev, "shell", "which", "su"],
                        text=True, cwd=BIN_DIR, creationflags=0x08000000
                    ).strip()
                    info_root.value = "已 Root" if root_check else "未 Root / 未授权"
                else:
                    device_status_text.value = "未检测到设备"
                    status_dot.bgcolor = "#E05070"
                    info_brand.value = "—"
                    info_model.value = "—"
                    info_android.value = "—"
                    info_root.value = "—"
            except Exception as ex:
                device_status_text.value = "扫描失败"
                status_dot.bgcolor = "#E05070"
            
            loading_ring.visible = False
            page.update()

        threading.Thread(target=run_scan, daemon=True).start()

    def install_usb_driver():
        """通过 pnputil 强制安装通用 Android 驱动"""
        inf_path = os.path.join(BIN_DIR, "android_winusb.inf")
        if not os.path.exists(inf_path):
            page.snack_bar = ft.SnackBar(ft.Text("未找到 android_winusb.inf，请检查 bin 目录"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()
            return
            
        def run_install():
            try:
                # 使用管理员权限调用 cmd 执行 pnputil
                cmd = f'pnputil /add-driver "{inf_path}" /install'
                subprocess.run(cmd, shell=True, check=True)
                page.snack_bar = ft.SnackBar(ft.Text("✅ 通用 ADB/Fastboot 驱动安装成功！"), bgcolor=ft.Colors.GREEN_400)
            except subprocess.CalledProcessError:
                page.snack_bar = ft.SnackBar(ft.Text("❌ 安装失败，请以管理员身份运行工具箱！"), bgcolor=ft.Colors.RED_400)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ 驱动安装异常: {ex}"), bgcolor=ft.Colors.RED_400)
                
            page.snack_bar.open = True
            page.update()

        threading.Thread(target=run_install, daemon=True).start()

    def open_device_manager():
        """打开设备管理器，方便用户手动更新驱动"""
        try:
            subprocess.Popen("devmgmt.msc", shell=True)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"打开设备管理器失败: {ex}"), bgcolor=ft.Colors.RED_400)
            page.snack_bar.open = True
            page.update()

    def install_driver(driver_type):
        def run_install():
            try:
                if driver_type == "qualcomm":
                    exe_path = os.path.join(BIN_DIR, "Qualcomm_9008_Driver", "Qualcomm_USB_Driver_Setup.exe")
                else:
                    exe_path = os.path.join(BIN_DIR, "MTK_VCOM_Driver", "MTK_Driver_Ext.exe")
                
                if not os.path.exists(exe_path):
                    raise Exception(f"未找到驱动，请检查 bin 目录")
                import ctypes
                ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, None, os.path.dirname(exe_path), 1)
                page.snack_bar = ft.SnackBar(ft.Text("已拉起驱动安装程序"), bgcolor=ft.Colors.GREEN_400)
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"驱动安装失败: {ex}"), bgcolor=ft.Colors.RED_400)
                page.snack_bar.open = True
                page.update()
        threading.Thread(target=run_install, daemon=True).start()

    def create_glass_card(title, subtitle, icon_name, on_click=None, is_main=False):
        icon_container = ft.Container(
            content=ft.Icon(icon_name, color=THEME_COLOR if is_main else "#8892B0", size=28),
            bgcolor=ft.Colors.with_opacity(0.1, THEME_COLOR) if is_main else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=12, width=50, height=50, alignment=ft.alignment.center,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, THEME_COLOR)) if is_main else None,
        )
        def on_hover(e):
            if e.data == "true":
                e.control.bgcolor = "#1A1E2A"
                e.control.shadow = [ft.BoxShadow(spread_radius=0, blur_radius=15, color=ft.Colors.with_opacity(0.2, THEME_COLOR), offset=ft.Offset(0, 4))]
                e.control.border = ft.border.all(1, ft.Colors.with_opacity(0.6, THEME_COLOR))
            else:
                e.control.bgcolor = "#131722"
                e.control.shadow = ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2))
                e.control.border = ft.border.all(1, "#222634")
            e.control.update()

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    icon_container, ft.Container(width=15),
                    ft.Column([
                        ft.Text(title, size=16, weight=ft.FontWeight.W_600, color="white"),
                        ft.Text(subtitle, size=12, color="#6E7B91"),
                    ], spacing=4, expand=True)
                ]),
            ]),
            bgcolor="#131722", border_radius=16, padding=20,
            border=ft.border.all(1, "#222634"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            on_hover=on_hover, on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            expand=True
        )

    side_panel = ft.Container(
        width=320, bgcolor="#0D1017", border=ft.border.only(left=ft.border.BorderSide(1, "#1C202D")), padding=30,
        content=ft.Column([
            ft.Text("SYSTEM STATUS", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Container(
                content=ft.Row([status_dot, ft.Text(" ", size=13), device_status_text, loading_ring]),
                padding=15, bgcolor="#151A26", border_radius=10, border=ft.border.all(1, "#1F2636"),
            ),
            ft.Container(height=20),
            ft.Text("DEVICE INFO", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text("品牌", color="#6E7B91", size=13), info_brand], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("型号", color="#6E7B91", size=13), info_model], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("系统", color="#6E7B91", size=13), info_android], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("Root", color="#6E7B91", size=13), info_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10),
                padding=15, bgcolor="#151A26", border_radius=10, border=ft.border.all(1, "#1F2636"),
            ),
            ft.Container(height=20),
            ft.Text("DRIVER INSTALLER", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Column([
                ft.ElevatedButton("安装 高通 9008 驱动", on_click=lambda _: install_driver("qualcomm"), width=260, bgcolor="#1C202D", color="white"),
                ft.ElevatedButton("安装 MTK VCOM 驱动", on_click=lambda _: install_driver("mtk"), width=260, bgcolor="#1C202D", color="white"),
                ft.ElevatedButton("安装 通用 ADB/Fastboot 驱动", on_click=lambda _: install_usb_driver(), width=260, bgcolor="#39C5BB", color="#0B0E14", weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("打开设备管理器 (修复识别)", on_click=lambda _: open_device_manager(), width=260, bgcolor="#1C202D", color="white"),
            ], spacing=10),
            ft.Container(height=20),
            fl.Lottie(src="https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json", width=240, height=240, animate=True),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    )

    main_content = ft.Container(
        expand=True, padding=40,
        content=ft.Column([
            ft.Text("Matrix Dashboard", size=38, weight=ft.FontWeight.BOLD, color="white"),
            ft.Text("原生 GPU 渲染引擎 · 从此告别卡顿", size=14, color=THEME_COLOR, weight=ft.FontWeight.W_600),
            ft.Container(height=40),
            ft.Text("QUICK ACTIONS", size=11, color="#4B5568", weight=ft.FontWeight.BOLD),
            ft.Container(height=15),
            ft.Row([
                create_glass_card("扫描设备", "点击读取真实手机信息", ft.Icons.PHONE_ANDROID, on_click=scan_device, is_main=True),
                create_glass_card("一键刷机", "自动解包并刷入", ft.Icons.ELECTRIC_BOLT, is_main=True),
            ], spacing=20),
            ft.Container(height=20),
            ft.Row([
                create_glass_card("模块仓库", "797 个纯净模块", ft.Icons.EXTENSION),
                create_glass_card("分区备份", "防变砖救援", ft.Icons.SAVE_ALT),
            ], spacing=20),
            ft.Container(height=20),
            ft.Row([
                create_glass_card("高级终端", "实时 Shell 执行", ft.Icons.TERMINAL),
                create_glass_card("历史记录", "刷机与操作日志", ft.Icons.HISTORY),
            ], spacing=20),
        ], scroll=ft.ScrollMode.ADAPTIVE)
    )

    nav_rail = ft.NavigationRail(
        selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=90, bgcolor="#0D1017",
        indicator_color=ft.Colors.with_opacity(0.15, THEME_COLOR),
        indicator_shape=ft.RoundedRectangleBorder(radius=10),
        selected_label_text_style=ft.TextStyle(color=THEME_COLOR, weight=ft.FontWeight.BOLD, size=12),
        unselected_label_text_style=ft.TextStyle(color="#4B5568", size=12),
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="控制台"),
            ft.NavigationRailDestination(icon=ft.Icons.BUILD_OUTLINED, selected_icon=ft.Icons.BUILD, label="工具箱"),
            ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="历史"),
        ]
    )

    page.add(ft.Row([nav_rail, ft.VerticalDivider(width=1, color="#1C202D"), main_content, side_panel], expand=True))

if __name__ == "__main__":
    ft.app(target=main)
