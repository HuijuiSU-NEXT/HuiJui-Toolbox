# fix_flash_parts_ui.py
import os

code = '''import flet as ft
import subprocess
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB_PATH = os.path.join(BASE_DIR, "bin", "fastboot.exe")

PARTITION_KB = {
    "boot": {"format": "raw / sparse", "desc": "内核 + ramdisk (Root/修补常用)", "risk": "刷错易无法开机", "level": "danger"},
    "init_boot": {"format": "raw / sparse", "desc": "初始化引导分区 (Android 13+)", "risk": "刷错易无法开机", "level": "danger"},
    "recovery": {"format": "raw / sparse", "desc": "恢复模式环境", "risk": "刷错可能无法进入 Recovery", "level": "warning"},
    "dtbo": {"format": "DTBO", "desc": "设备树叠加层 (硬件配置)", "risk": "刷错可能导致屏幕异常", "level": "warning"},
    "vbmeta": {"format": "AVB 元数据", "desc": "AVB 签名验证元数据", "risk": "极易导致无法启动，需配合禁用校验", "level": "danger"},
    "super": {"format": "sparse", "desc": "动态分区容器 (含 system/vendor)", "risk": "Android 11+ 系统级刷入", "level": "danger"},
    "modem": {"format": "raw / ELF", "desc": "基带固件", "risk": "刷错直接无信号", "level": "danger"},
    "vbmeta_system": {"format": "AVB 元数据", "desc": "system 分区校验", "risk": "刷错可能无法启动", "level": "danger"},
    "vbmeta_vendor": {"format": "AVB 元数据", "desc": "vendor 分区校验", "risk": "刷错可能无法启动", "level": "danger"},
    "vendor_boot": {"format": "raw / sparse", "desc": "厂商内核模块", "risk": "刷错可能影响硬件功能", "level": "warning"},
}

def build_flash_parts_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.TRANSPARENT, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, expand=True, # 让日志区撑满底部剩余空间
        border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("等待操作...", size=13, color=theme_color, weight=ft.FontWeight.BOLD)

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    # 智能格式检测与安全刷入
    def safe_flash(part_name):
        def thread():
            log_area.value = ""
            log(f"> 准备刷入分区: {part_name}")
            page.update()

            file_picker = ft.FilePicker()
            page.overlay.append(file_picker)
            page.update()

            def on_file_selected(e: ft.FilePickerResultEvent):
                if not e.files:
                    log("❌ 未选择文件，操作取消。")
                    return
                
                img_path = e.files[0].path
                log(f"✅ 已选择镜像: {img_path}")
                page.update()

                try:
                    with open(img_path, 'rb') as f:
                        header = f.read(4)
                    log("[1/2] 正在智能识别镜像格式...")
                    if header == b'\\x3A\\xFF\\x26\\xED':
                        log("✅ 检测到 Android Sparse 格式 (Fastboot 自动处理)")
                    else:
                        log("✅ 检测到 Raw (原始) 格式")
                except Exception as ex:
                    log(f"⚠️ 格式识别失败: {ex}，尝试继续刷入...")

                log(f"\\n[2/2] 正在执行刷入...")
                cmd = f'"{FB_PATH}" flash {part_name} "{img_path}"'
                log(f"> {cmd}")
                page.update()

                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        log(line.strip())
                proc.wait()

                if proc.returncode == 0:
                    log(f"\\n✅ {part_name} 刷入成功！")
                    status_text.value = f"{part_name} 刷入成功"
                    status_text.color = ft.Colors.GREEN
                else:
                    log(f"\\n❌ {part_name} 刷入失败！")
                    status_text.value = f"{part_name} 刷入失败"
                    status_text.color = ft.Colors.RED
                page.update()

            file_picker.on_result = on_file_selected
            file_picker.pick_files(allowed_extensions=["img", "bin"])

        threading.Thread(target=thread, daemon=True).start()

    # 构建美观的分区卡片
    partition_cards = []
    for part, info in PARTITION_KB.items():
        risk_color = ft.Colors.RED_400 if info["level"] == "danger" else ft.Colors.ORANGE_400
        
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MEMORY, color=theme_color, size=18),
                    ft.Text(part, size=15, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "刷入", icon=ft.Icons.FLASH_ON, 
                        on_click=lambda e, name=part: safe_flash(name), 
                        style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.1, theme_color), color=theme_color, padding=ft.padding.symmetric(horizontal=10, vertical=5))
                    )
                ]),
                ft.Divider(color=ft.Colors.GREY_800, height=8),
                ft.Text(f"格式: {info['format']}", size=11, color=ft.Colors.GREY_400),
                ft.Text(f"用途: {info['desc']}", size=11, color=ft.Colors.GREY_300),
                ft.Row([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=risk_color, size=12),
                    ft.Text(info['risk'], size=10, color=risk_color, weight=ft.FontWeight.BOLD)
                ], spacing=5)
            ], spacing=5),
            width=240, # 固定宽度
            height=135, # 固定高度，防止被撑破
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=12,
            padding=15
        )
        partition_cards.append(card)

    return ft.Container(
        content=ft.Column([
            # 顶栏
            ft.Row([
                ft.Icon(ft.Icons.BUILD_CIRCLE, color=theme_color, size=28),
                ft.Text("分区刷入 · 救砖指南", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text
            ]),
            
            ft.Text("💡 请务必确认分区名与机型匹配！点击右侧按钮自动检测格式并执行刷入。", size=12, color=ft.Colors.GREY_400),
            ft.Container(height=10),
            
            # 操作区：使用 Row(wrap=True) 自动换行
            ft.Container(
                content=ft.Row(partition_cards, wrap=True, spacing=15, run_spacing=15),
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE), 
                border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), 
                border_radius=15,
                padding=15
            ),
            
            ft.Container(height=10),
            ft.Text("刷入日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

with open("pages/flash_parts.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✅ 分区刷入 UI 重构完成！采用固定尺寸卡片，排版整齐！")