# fix_module_repo_v2.py
import os

module_code = '''import flet as ft
import threading
import subprocess
import os
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
MODULES_URL = "https://raw.githubusercontent.com/HuijuiSU-NEXT/Huijui_Module_Repo/main/modules.json"

def build_module_repo_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.BLACK, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, height=180, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("正在拉取仓库列表...", size=13, color=theme_color, font_family="Microsoft YaHei")
    
    # 搜索框
    search_field = ft.TextField(
        hint_text="搜索模块名称或作者...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        color="white",
        border_color=ft.Colors.with_opacity(0.2, theme_color),
        on_change=lambda e: filter_modules(e.control.value)
    )
    
    # 模块列表容器
    grid_view = ft.GridView(
        expand=1, runs_count=3, max_extent=280, spacing=15, run_spacing=15, padding=10
    )
    
    all_modules = []  # 原始数据

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    def filter_modules(keyword):
        keyword = keyword.lower().strip()
        grid_view.controls.clear()
        for m in all_modules:
            name = m.get("name", "").lower()
            author = m.get("author", "").lower()
            desc = m.get("description", "").lower()
            if keyword in name or keyword in author or keyword in desc:
                grid_view.controls.append(build_module_card(m))
        grid_view.update()

    def build_module_card(m):
        name = m.get("name", "未知模块")
        author = m.get("author", "佚名")
        version = m.get("version", "-")
        desc = m.get("description", "暂无描述").strip()
        if len(desc) > 50: desc = desc[:50] + "..."
        download_count = m.get("downloadCount", 0)
        
        # 获取最新的 zipUrl
        releases = m.get("releases", [])
        zip_url = ""
        if releases:
            zip_url = releases[0].get("zipUrl", "")

        def do_download_and_install(e):
            if not zip_url:
                log(f"[错误] 模块 {name} 没有可用的下载链接！")
                return
            threading.Thread(target=download_and_install, args=(name, zip_url), daemon=True).start()

        return ft.Container(
            content=ft.Column([
                ft.Text(name, size=16, weight=ft.FontWeight.BOLD, color="white", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"作者: {author}  |  版本: {version}", size=11, color=ft.Colors.GREY_400),
                ft.Text(desc, size=12, color=ft.Colors.GREY_300, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(expand=True),
                ft.Row([
                    ft.Text(f"下载量: {download_count}", size=10, color=ft.Colors.GREY_500),
                    ft.ElevatedButton(
                        "一键安装", icon=ft.Icons.DOWNLOAD, 
                        on_click=do_download_and_install,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.with_opacity(0.15, theme_color), 
                            color=theme_color,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=10, vertical=5)
                        )
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=15,
            padding=15,
        )

    def fetch_modules():
        log("> 正在从 Huijui 官方仓库获取 modules.json...")
        try:
            req = urllib.request.Request(MODULES_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                all_modules.extend(data)
                log(f"✅ 成功加载 {len(all_modules)} 个模块！")
                
                # 初始渲染
                for m in all_modules:
                    grid_view.controls.append(build_module_card(m))
                status_text.value = f"共找到 {len(all_modules)} 个模块"
                status_text.color = ft.Colors.GREEN
                page.update()
        except Exception as ex:
            log(f"❌ 获取失败: {ex}")
            status_text.value = "获取失败，请检查网络"
            status_text.color = ft.Colors.RED
            page.update()

    def download_and_install(name, url):
        log(f"\\n> 开始下载: {name}")
        log(f"> 链接: {url}")
        
        local_zip = os.path.join(BASE_DIR, f"{name}.zip")
        try:
            # 下载
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(local_zip, 'wb') as out_file:
                data = response.read(1024 * 1024)
                while data:
                    out_file.write(data)
                    data = response.read(1024 * 1024)
            log(f"✅ 下载完成: {local_zip}")

            # 推送到手机
            remote_path = f"/sdcard/Download/{name}.zip"
            log(f"> 正在推送到手机: {remote_path}")
            push_cmd = f'"{ADB_PATH}" push "{local_zip}" "{remote_path}"'
            proc = subprocess.Popen(push_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            # 通过 Root 安装 (这里假设使用 ksud 或 magisk)
            log("> 正在通过 Root 权限安装模块...")
            # 尝试使用 KernelSU 或 Magisk 的安装命令
            install_cmds = [
                f'"{ADB_PATH}" shell "su -c \\"ksud module install {remote_path}\\""',
                f'"{ADB_PATH}" shell "su -c \\"magisk --install-module {remote_path}\\""'
            ]
            
            success = False
            for cmd in install_cmds:
                log(f"> 尝试: {cmd}")
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                out = ""
                for line in iter(proc.stdout.readline, ''):
                    if line:
                        log(line.strip())
                        out += line
                proc.wait()
                if proc.returncode == 0 or "success" in out.lower() or "完成" in out:
                    success = True
                    break
            
            if success:
                log("✅ 模块安装指令执行成功！")
            else:
                log("⚠️ 安装命令可能失败，请检查手机上的 Root 管理器。")
                log("💡 文件已推送至手机 Download 目录，可手动安装。")

        except Exception as ex:
            log(f"❌ 操作失败: {ex}")

    # 启动加载
    threading.Thread(target=fetch_modules, daemon=True).start()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.EXTENSION, color=theme_color, size=28),
                ft.Text("Huijui 模块仓库", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=10),
            status_text,
            search_field,
            ft.Container(height=10),
            ft.Container(content=grid_view, expand=True),
            ft.Text("操作日志", size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD, font_family="Microsoft YaHei"),
            log_container
        ], expand=True),
        expand=True,
        padding=20
    )
'''

with open("pages/module_repo.py", "w", encoding="utf-8") as f:
    f.write(module_code)

print("✅ 模块仓库已接入 Huijui 官方源！支持搜索与一键安装！")