# fix_baseband_backup.py
import os

backup_code = '''import flet as ft
import threading
import subprocess
import os
import time
import re
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

# 默认备份路径
DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "HuiJui_Backups")

# 高通/MTK 核心基带分区列表
BASEBAND_PARTS = [
    "modem", "modemst1", "modemst2", "fsg", "fsc", 
    "persist", "nvram", "nvdata", "protect1", "protect2"
]

def build_backup_page(page: ft.Page, theme_color):
    state = {"save_dir": DEFAULT_DIR}

    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, expand=True,
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("等待选择要备份的分区...", size=13, color=theme_color, weight=ft.FontWeight.BOLD)
    path_display = ft.Text(f"当前保存路径: {state['save_dir']}", size=11, color=ft.Colors.GREY_400, font_family="Consolas")

    # 目录选择器
    dir_picker = ft.FilePicker()
    page.overlay.append(dir_picker)
    page.update()

    def on_dir_pick(e: ft.FilePickerResultEvent):
        if e.path:
            state["save_dir"] = e.path
            path_display.value = f"当前保存路径: {state['save_dir']}"
            log(f"📁 备份目录已更改为: {state['save_dir']}")
            page.update()

    dir_picker.on_result = on_dir_pick

    def pick_directory(e):
        dir_picker.get_directory_path(dialog_title="选择分区镜像保存目录")

    def open_backup_folder(e):
        os.makedirs(state["save_dir"], exist_ok=True)
        try:
            os.startfile(state["save_dir"])
        except Exception:
            log(f"📁 备份目录路径: {state['save_dir']}")

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 核心提取函数 (单个分区)
    def extract_partition(part_name, target_dir):
        try:
            temp_dir = os.path.join(BASE_DIR, "temp_pull")
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = int(time.time())
            file_name = f"{part_name}_{timestamp}.img"
            final_file = os.path.join(target_dir, file_name)
            temp_file = os.path.join(temp_dir, file_name)
            remote_file = f"/sdcard/{file_name}"

            # 1. 智能探测真实的块路径
            possible_paths = [
                f"/dev/block/by-name/{part_name}",
                f"/dev/block/by-name/{part_name}_a",
                f"/dev/block/by-name/{part_name}_b",
                f"/dev/block/bootdevice/by-name/{part_name}"
            ]
            
            block_path = None
            for p in possible_paths:
                check = subprocess.run(f'"{ADB_PATH}" shell "su -c \\"ls {p}\\""', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                if "No such" not in check.stdout and "No such" not in check.stderr and check.returncode == 0:
                    block_path = p
                    break

            if not block_path:
                log(f"⚠️ 找不到 {part_name} 分区，跳过。")
                return False

            # 2. dd 提取
            log(f"  > 正在提取 {part_name} ...")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if={block_path} of={remote_file}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            proc.wait()

            # 3. pull 到中转站
            cmd_pull = f'"{ADB_PATH}" pull {remote_file} "{temp_file}"'
            proc = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            proc.wait()

            # 4. 移动到最终目录
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1024:
                shutil.move(temp_file, final_file)
                size_mb = os.path.getsize(final_file) / (1024 * 1024)
                log(f"  ✅ {part_name} 备份成功 ({size_mb:.2f} MB)")
                subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_file}\\""', shell=True, capture_output=True)
                return True
            else:
                log(f"  ❌ {part_name} 备份失败 (文件为空)。")
                return False
                
        except Exception as e:
            log(f"  ❌ {part_name} 提取出错: {e}")
            return False

    # 单分区备份入口
    def do_single_backup(part_name):
        status_text.value = f"正在处理 {part_name}..."
        status_text.color = ft.Colors.ORANGE
        page.update()
        
        def thread():
            log_area.value = ""
            target_dir = state["save_dir"]
            os.makedirs(target_dir, exist_ok=True)
            extract_partition(part_name, target_dir)
            status_text.value = "处理完成"
            status_text.color = ft.Colors.GREEN
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    # 🚨 全量基带备份入口
    def do_baseband_backup(e):
        status_text.value = "正在全量备份基带数据 (极度重要)..."
        status_text.color = ft.Colors.RED
        page.update()
        
        def thread():
            log_area.value = ""
            # 专门建个专属文件夹防止混淆
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            target_dir = os.path.join(state["save_dir"], f"Baseband_Backup_{timestamp_str}")
            os.makedirs(target_dir, exist_ok=True)
            
            log(f"🚨 开始全量基带备份 (防格机保命)")
            log(f"📁 保存目标: {target_dir}\\n")
            
            success_count = 0
            for part in BASEBAND_PARTS:
                if extract_partition(part, target_dir):
                    success_count += 1
                time.sleep(0.5) # 稍微停顿一下，防止手机IO卡死

            log(f"\\n========================================")
            if success_count > 0:
                log(f"🎉 基带备份完成！共成功提取 {success_count} 个分区。")
                log(f"💡 请务必将该文件夹拷贝至 U 盘或云盘双重备份！")
                status_text.value = "基带备份完成！"
                status_text.color = ft.Colors.GREEN
            else:
                log(f"❌ 基带备份彻底失败，请检查 Root 权限。")
                status_text.value = "备份失败"
                status_text.color = ft.Colors.RED
                
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    def handle_hover(e):
        e.control.bgcolor = ft.Colors.with_opacity(0.15, theme_color) if e.data == "true" else ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        e.control.update()

    # 基础快捷备份
    basic_parts = [
        ("boot", ft.Icons.ADB),
        ("init_boot", ft.Icons.MEMORY),
        ("recovery", ft.Icons.SETTINGS_BACKUP_RESTORE),
        ("vbmeta", ft.Icons.SECURITY),
        ("dtbo", ft.Icons.DEVICE_HUB),
        ("persist", ft.Icons.FOLDER_SHARED),
        ("modem", ft.Icons.WIFI_TETHERING),
        ("super", ft.Icons.DNS)
    ]
    
    grid_cards = []
    for p_name, p_icon in basic_parts:
        grid_cards.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(p_icon, color=theme_color, size=20),
                    ft.Text(p_name, size=14, weight=ft.FontWeight.BOLD, color="white")
                ], alignment=ft.MainAxisAlignment.CENTER),
                width=120, height=55,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=10,
                alignment=ft.alignment.center,
                on_click=lambda e, name=p_name: do_single_backup(name),
                on_hover=handle_hover
            )
        )

    return ft.Container(
        content=ft.Column([
            # 顶栏
            ft.Row([
                ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), 
                ft.Text("分区备份 (真Root)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text,
            ]),
            
            # 路径控制区
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER, color=theme_color, size=16),
                    path_display,
                    ft.Container(expand=True),
                    ft.TextButton("更改目录", icon=ft.Icons.EDIT, on_click=pick_directory, style=ft.ButtonStyle(color=theme_color)),
                    ft.ElevatedButton("打开目录", icon=ft.Icons.OPEN_IN_NEW, on_click=open_backup_folder, style=ft.ButtonStyle(color="#000000", bgcolor=theme_color, shape=ft.RoundedRectangleBorder(radius=8))),
                ]),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border_radius=8, padding=ft.padding.symmetric(horizontal=10, vertical=5)
            ),
            ft.Container(height=10),
            
            # 🚨 基带保命区
            ft.Container(
                content=ft.Row([
                    ft.Column([
                        ft.Text("🛡️ 防格机保命：一键全量备份基带", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                        ft.Text("将串行提取 modem, modemst1, modemst2, fsg, nvram 等核心基带分区。防止恶意模块破坏导致无信号/IMEI丢失。", size=11, color=ft.Colors.GREY_400)
                    ], expand=True),
                    ft.ElevatedButton(
                        "一键备份全量基带", icon=ft.Icons.SECURITY, on_click=do_baseband_backup,
                        style=ft.ButtonStyle(color="white", bgcolor=ft.Colors.RED_700, shape=ft.RoundedRectangleBorder(radius=8), padding=15)
                    )
                ]),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED_900),
                border=ft.border.all(1, ft.Colors.RED_700),
                border_radius=12, padding=15
            ),
            ft.Container(height=10),
            
            # 基础快捷备份区
            ft.Container(
                content=ft.Row(grid_cards, wrap=True, spacing=10, run_spacing=10),
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), 
                border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), 
                border_radius=15, padding=15
            ),
            
            ft.Container(height=10),
            ft.Text("底层通信与备份日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True), 
        expand=True, 
        padding=20
    )
'''

with open("pages/backup.py", "w", encoding="utf-8") as f:
    f.write(backup_code)

print("✅ 分区备份 v11 注入完毕！加入全量基带保命备份，核心分区一网打尽！")