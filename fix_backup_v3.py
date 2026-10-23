# fix_backup_v3.py
import os

backup_code = '''import flet as ft
import threading
import subprocess
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")

def build_backup_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, height=180, # 固定高度，不挤占操作区
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("等待选择要备份的分区...", size=13, color=theme_color, weight=ft.FontWeight.BOLD)

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 封装一键备份逻辑
    def do_backup(part_name):
        status_text.value = f"正在处理 {part_name}..."
        status_text.color = ft.Colors.ORANGE
        page.update()
        
        def thread():
            log_area.value = ""
            log(f"> 准备备份分区: {part_name}")
            page.update()

            bk_dir = os.path.join(BASE_DIR, "backups")
            os.makedirs(bk_dir, exist_ok=True)
            timestamp = int(time.time())
            local_file = os.path.join(bk_dir, f"{part_name}_{timestamp}.img")
            remote_file = f"/sdcard/{part_name}_{timestamp}.img"

            # 1. 智能探测真实的块路径 (兼容 A/B 分区)
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
                log(f"❌ 错误: 未找到分区 {part_name} (尝试了标准及 A/B 路径)。")
                status_text.value = "备份失败: 分区不存在"
                status_text.color = ft.Colors.RED
                page.update()
                return

            log(f"✅ 找到分区路径: {block_path}")

            # 2. 执行 dd 提取
            log(f"\\n[2/4] 正在通过 Root 提取镜像...")
            log(f"> su -c dd if={block_path} of={remote_file}")
            cmd_dd = f'"{ADB_PATH}" shell "su -c \\"dd if={block_path} of={remote_file}\\""'
            proc = subprocess.Popen(cmd_dd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 3. 拉取到电脑
            log(f"\\n[3/4] 正在拉取到电脑...")
            log(f"> adb pull {remote_file} {local_file}")
            cmd_pull = f'"{ADB_PATH}" pull {remote_file} "{local_file}"'
            proc = subprocess.Popen(cmd_pull, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 4. 严格校验并清理
            log(f"\\n[4/4] 正在校验并清理临时文件...")
            subprocess.run(f'"{ADB_PATH}" shell "su -c \\"rm {remote_file}\\""', shell=True, capture_output=True)
            
            if os.path.exists(local_file) and os.path.getsize(local_file) > 1024:
                size_mb = os.path.getsize(local_file) / (1024 * 1024)
                log(f"\\n✅ 备份成功！文件大小: {size_mb:.2f} MB")
                log(f"📁 保存路径: {local_file}")
                status_text.value = "备份成功！"
                status_text.color = ft.Colors.GREEN
            else:
                log(f"\\n❌ 备份失败！拉取的文件不存在或大小为 0。")
                status_text.value = "备份失败！"
                status_text.color = ft.Colors.RED
            
            page.update()

        threading.Thread(target=thread, daemon=True).start()

    # 核心分区列表及图标
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
                    ft.Icon(p_icon, color=theme_color, size=24),
                    ft.Column([
                        ft.Text(p_name, size=15, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("一键提取", size=11, color=ft.Colors.GREY_500)
                    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                border_radius=12,
                padding=15,
                on_click=lambda e, name=p_name: do_backup(name),
                # 悬浮动画
                on_hover=lambda e: e.control.update(bgcolor=ft.Colors.with_opacity(0.1, theme_color) if e.data == "true" else ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
            )
        )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SAVE, color=theme_color, size=28), 
                ft.Text("分区备份 (真Root)", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text
            ]),
            ft.Container(height=10),
            
            # 操作区（自动换行，无滚动条）
            ft.Container(
                content=ft.Column([
                    ft.Text("点击下方卡片，自动识别 A/B 分区并备份到本地 backups 目录", size=13, color=ft.Colors.GREY_400),
                    ft.Container(height=10),
                    ft.Row(grid_cards, wrap=True, spacing=15, run_spacing=15) # 使用 wrap 实现自动换行
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

print("✅ 分区备份 v3 重构完毕！瀑布流排版，无需滑动，颜值归位！")