# fix_backup_v10.py
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

    def do_backup(part_name):
        status_text.value = f"正在处理 {part_name}..."
        status_text.color = ft.Colors.ORANGE
        page.update()
        
        def thread():
            log_area.value = ""
            log(f"> 准备备份分区: {part_name}")
            page.update()

            final_dir = state["save_dir"]
            
            # 1. 创建纯英文中转目录
            temp_dir = os.path.join(BASE_DIR, "temp_pull")
            os.makedirs(temp_dir, exist_ok=True)
            
            timestamp = int(time.time())
            file_name = f"{part_name}_{timestamp}.img"
            
            # 最终的中文路径
            final_file = os.path.join(final_dir, file_name)
            # 临时的纯英文路径
            temp_file = os.path.join(temp_dir, file_name)
            # 手机端路径
            remote_file = f"/sdcard/{file_name}"

            # 2. 探测分区路径
            log("[1/4] 正在探测分区真实路径...")
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
                log(f"❌ 错误: 未找到分区 {part_name}。")
                status_text.value = "备份失败: 分区不存在"
                status_text.color = ft.Colors.RED
                page.update()
                return

            log(f"✅ 找到分区路径: {block_path}")

            # 3. dd 提取到手机
            log(f"\\n[2/4] 正在通过 Root 提取镜像...")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if={block_path} of={remote_file}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 4. 拉取到临时英文目录（彻底避开中文路径坑）
            log(f"\\n[3/4] 正在拉取镜像到本地中转目录...")
            cmd_pull = f'"{ADB_PATH}" pull {remote_file} "{temp_file}"'
            proc = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 5. 用 Python 瞬间转移到中文目录
            log(f"\\n[4/4] 正在将文件移动至目标目录...")
            try:
                os.makedirs(final_dir, exist_ok=True)
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 1024:
                    # Python 的 shutil.move 完美支持中文路径
                    shutil.move(temp_file, final_file)
                    size_mb = os.path.getsize(final_file) / (1024 * 1024)
                    log(f"\\n✅ 备份成功！文件大小: {size_mb:.2f} MB")
                    log(f"📁 文件已保存至: {final_file}")
                    status_text.value = "备份成功！"
                    status_text.color = ft.Colors.GREEN
                else:
                    log(f"\\n❌ 备份失败！中转文件不存在或大小为 0。")
                    status_text.value = "备份失败！"
                    status_text.color = ft.Colors.RED
            except Exception as move_err:
                log(f"\\n❌ 移动文件时出错: {move_err}")
                log(f"💡 文件暂留在: {temp_file}")
                status_text.value = "移动文件失败"
                status_text.color = ft.Colors.RED

            # 清理手机临时文件
            subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_file}\\""', shell=True, capture_output=True)
            # 清理空的中转目录
            try: os.rmdir(temp_dir)
            except: pass
            
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    def handle_hover(e):
        e.control.bgcolor = ft.Colors.with_opacity(0.15, theme_color) if e.data == "true" else ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        e.control.update()

    partitions_info = [
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
    for p_name, p_icon in partitions_info:
        grid_cards.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(p_icon, color=theme_color, size=20),
                    ft.Text(p_name, size=14, weight=ft.FontWeight.BOLD, color="white")
                ], alignment=ft.MainAxisAlignment.CENTER),
                width=130,
                height=60,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=10,
                alignment=ft.alignment.center,
                on_click=lambda e, name=p_name: do_backup(name),
                on_hover=handle_hover
            )
        )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), 
                ft.Text("分区备份 (真Root)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text,
            ]),
            
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
            
            ft.Container(
                content=ft.Row(grid_cards, wrap=True, spacing=10, run_spacing=10),
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), 
                border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), 
                border_radius=15, 
                padding=15
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

print("✅ 分区备份 v10 搞定！纯英文中转+Python搬运，彻底消灭任何中文路径报错！")