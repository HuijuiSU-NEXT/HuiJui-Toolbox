# fix_flash_parts.py
import os

flash_parts_code = '''import flet as ft
import subprocess
import os
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB_PATH = os.path.join(BASE_DIR, "bin", "fastboot.exe")

# 分区知识库
PARTITION_KB = {
    "boot": {"format": "raw / sparse", "desc": "内核 + ramdisk (Root/修补常用)", "risk": "刷错易无法开机"},
    "init_boot": {"format": "raw / sparse", "desc": "初始化引导分区 (Android 13+)", "risk": "刷错易无法开机"},
    "recovery": {"format": "raw / sparse", "desc": "恢复模式环境", "risk": "刷错可能无法进入 Recovery"},
    "dtbo": {"format": "DTBO", "desc": "设备树叠加层，包含硬件配置", "risk": "刷错可能导致屏幕异常或无法启动"},
    "vbmeta": {"format": "AVB 元数据", "desc": "AVB 签名验证元数据", "risk": "刷错极易导致无法启动。刷第三方固件时需配合 --disable-verity --disable-verification"},
    "super": {"format": "sparse", "desc": "动态分区容器 (含 system/vendor 等)", "risk": "Android 11+ 不能单独刷 system，需通过 super.img 操作"},
    "modem": {"format": "raw / ELF", "desc": "基带固件", "risk": "刷错会导致无信号"},
    "vbmeta_system": {"format": "AVB 元数据", "desc": "system 分区的 vbmeta 校验", "risk": "刷错可能导致无法启动"},
    "vbmeta_vendor": {"format": "AVB 元数据", "desc": "vendor 分区的 vbmeta 校验", "risk": "刷错可能导致无法启动"},
    "vendor_boot": {"format": "raw / sparse", "desc": "厂商内核模块 (部分设备使用)", "risk": "刷错可能影响硬件功能"},
}

def build_flash_parts_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color="#00FFD1", text_size=12, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor="#05070A", border_radius=12, padding=15, height=180, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))
    
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

            # 步骤1：让用户选择镜像文件
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

                # 步骤2：检测镜像格式
                try:
                    with open(img_path, 'rb') as f:
                        header = f.read(4)
                    
                    log("[1/2] 正在智能识别镜像格式...")
                    if header == b'\\x3A\\xFF\\x26\\xED':
                        log("✅ 检测到 Android Sparse 格式")
                        log("   (Fastboot 将自动处理稀疏格式)")
                    else:
                        log("✅ 检测到 Raw (原始) 格式")
                except Exception as ex:
                    log(f"⚠️ 格式识别失败: {ex}，尝试继续刷入...")

                # 步骤3：执行刷入
                log(f"\\n[2/2] 正在刷入 {part_name} ...")
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
                    log(f"\\n❌ {part_name} 刷入失败，请检查上方日志。")
                    status_text.value = f"{part_name} 刷入失败"
                    status_text.color = ft.Colors.RED
                page.update()

            file_picker.on_result = on_file_selected
            file_picker.pick_files(allowed_extensions=["img", "bin"])

        threading.Thread(target=thread, daemon=True).start()

    # 构建分区卡片
    partition_cards = []
    for part, info in PARTITION_KB.items():
        risk_color = ft.Colors.RED_400 if "无法启动" in info["risk"] or "无信号" in info["risk"] else ft.Colors.ORANGE_400
        
        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.MEMORY, color=theme_color, size=20),
                    ft.Text(part, size=16, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Container(expand=True),
                    ft.ElevatedButton("安全刷入", icon=ft.Icons.FLASH_ON, on_click=lambda e, name=part: safe_flash(name), style=ft.ButtonStyle(bgcolor=theme_color, color="black", padding=ft.padding.symmetric(horizontal=10, vertical=5)))
                ]),
                ft.Divider(color=ft.Colors.GREY_800, height=10),
                ft.Text(f"格式: {info['format']}", size=12, color=ft.Colors.GREY_400),
                ft.Text(f"用途: {info['desc']}", size=12, color=ft.Colors.GREY_300),
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=risk_color, size=14),
                    ft.Text(info['risk'], size=11, color=risk_color, weight=ft.FontWeight.BOLD)
                ], spacing=5)
            ]),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=12,
            padding=15
        )
        partition_cards.append(card)

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BUILD_CIRCLE, color=theme_color, size=28),
                ft.Text("分区刷入 · 救砖指南", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei"),
                ft.Container(expand=True),
                status_text
            ]),
            ft.Container(height=5),
            ft.Text("💡 点击卡片上的“安全刷入”，自动检测格式并执行 fastboot 刷入。请务必确认分区名与机型匹配！", size=12, color=ft.Colors.GREY_400),
            ft.Container(height=10),
            
            # 卡片网格
            ft.GridView(
                controls=partition_cards,
                runs_count=2,
                max_extent=400,
                spacing=15,
                run_spacing=15,
                height=400
            ),
            
            ft.Container(height=10),
            ft.Text("刷入日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

# 1. 写入页面文件
with open("pages/flash_parts.py", "w", encoding="utf-8") as f:
    f.write(flash_parts_code)
print("✅ pages/flash_parts.py 已生成！")

# 2. 注入主程序路由
with open("main_final.py", "r", encoding="utf-8") as f:
    content = f.read()

if "from pages.flash_parts import build_flash_parts_page" not in content:
    content = content.replace(
        "from pages.flash import build_flash_page",
        "from pages.flash import build_flash_page\nfrom pages.flash_parts import build_flash_parts_page"
    )

if '"flash_parts": build_flash_parts_page' not in content:
    content = content.replace(
        '"flash": build_flash_page,',
        '"flash": build_flash_page,\n            "flash_parts": build_flash_parts_page,'
    )

with open("main_final.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 路由已注入！")