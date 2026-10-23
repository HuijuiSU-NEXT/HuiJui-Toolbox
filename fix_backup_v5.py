# fix_backup_v5.py
import os

backup_code = '''import flet as ft
import threading
import subprocess
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

def build_backup_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, height=200, # 固定日志高度
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("等待选择要备份的分区...", size=13, color=theme_color, weight=ft.FontWeight.BOLD)

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 打开本地备份文件夹
    def open_backup_folder(e):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        try:
            os.startfile(BACKUP_DIR)
        except Exception:
            log(f"📁 备份目录路径: {BACKUP_DIR}")

    # 封装一键备份逻辑
    def do_backup(part_name):
        status_text.value = f"正在处理 {part_name}..."
        status_text.color = ft.Colors.ORANGE
        page.update()
        
        def thread():
            log_area.value = ""
            log(f"> 准备备份分区: {part_name}")
            page.update()

            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = int(time.time())
            local_file = os.path.join(BACKUP_DIR, f"{part_name}_{timestamp}.img")
            remote_file = f"/sdcard/{part_name}_{timestamp}.img"

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

            log(f"\\n[2/4] 正在通过 Root 提取镜像...")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if={block_path} of={remote_file}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            log(f"\\n[3/4] 正在拉取到电脑...")
            cmd_pull = f'"{ADB_PATH}" pull {remote_file} "{local_file}"'
            proc = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            log(f"\\n[4/4] 正在校验并清理临时文件...")
            subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_file}\\""', shell=True, capture_output=True)
            
            if os.path.exists(local_file) and os.path.getsize(local_file) > 1024:
                size_mb = os.path.getsize(local_file) / (1024 * 1024)
                log(f"\\n✅ 备份成功！文件大小: {size_mb:.2f} MB")
                log(f"📁 文件已保存至: {local_file}")
                status_text.value = "备份成功！"
                status_text.color = ft.Colors.GREEN
            else:
                log(f"\\n❌ 备份失败！拉取的文件不存在或大小为 0。")
                status_text.value = "备份失败！"
                status_text.color = ft.Colors.RED
            
            page.update()

        threading.Thread(target=thread, daemon=True).start()

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
                content=ft.Column([
                    ft.Icon(p_icon, color=theme_color, size=24),
                    ft.Text(p_name, size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text("一键提取", size=10, color=ft.Colors.GREY_500)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=12,
                alignment=ft.alignment.center,
                on_click=lambda e, name=p_name: do_backup(name),
                on_hover=lambda e: e.control.update(bgcolor=ft.Colors.with_opacity(0.1, theme_color) if e.data == "true" else ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
            )
        )

    # 使用 GridView 强制网格排版
    grid_view = ft.GridView(
        controls=grid_cards,
        runs_count=4,
        max_extent=160,
        spacing=15,
        run_spacing=15,
        height=230, # 限制高度，腾出空间给日志
    )

    return ft.Container(
        content=ft.Column([
            # 顶栏：标题 + 状态 + 打开文件夹按钮
            ft.Row([
                ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), 
                ft.Text("分区备份 (真Root)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text,
                ft.ElevatedButton(
                    "打开备份目录", icon=ft.Icons.FOLDER_OPEN, on_click=open_backup_folder,
                    style=ft.ButtonStyle(color=theme_color, bgcolor=ft.Colors.with_opacity(0.1, theme_color), shape=ft.RoundedRectangleBorder(radius=8))
                )
            ]),
            ft.Container(height=10),
            
            # 操作区（限制高度的网格）
            ft.Container(
                content=ft.Column([
                    ft.Text("点击下方方块，自动识别 A/B 分区并保存到本地 backups 目录", size=13, color=ft.Colors.GREY_400),
                    ft.Container(height=10),
                    grid_view
                ]),
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), 
                border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), 
                border_radius=15, 
                padding=20
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

print("✅ 分区备份 v5 终极重构！网格排版 + 打开备份目录按钮！")