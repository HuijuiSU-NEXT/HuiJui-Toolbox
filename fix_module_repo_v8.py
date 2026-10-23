# fix_module_repo_v8.py
import os

module_code = '''import flet as ft
import threading
import subprocess
import os
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB_PATH = os.path.join(BASE_DIR, "bin", "adb.exe")
REPO_OWNER = "HuijuiSU-NEXT"
REPO_NAME = "Huijui_Module_Repo"
REPO_BRANCH = "main"

MODULES_URL_JSdelivr = f"https://cdn.jsdelivr.net/gh/{REPO_OWNER}/{REPO_NAME}@{REPO_BRANCH}/modules.json"
MODULES_URL_RAW = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}/modules.json"

# 内置核心框架（CORE）
CORE_MODULES = [
    {
        "name": "LSPosed",
        "author": "LSPosed",
        "version": "官方最新",
        "description": "强大的原生 Xposed 框架，必须安装。",
        "downloadCount": "全网",
        "releases": [{"zipUrl": "https://github.com/LSPosed/LSPosed/releases/latest/download/LSPosed.zip"}],
        "tags": ["core", "xposed"]
    },
    {
        "name": "Shamiko",
        "author": "LSPosed",
        "version": "官方最新",
        "description": "完美的隐藏 Root 痕迹工具，配合 LSPosed 使用。",
        "downloadCount": "全网",
        "releases": [{"zipUrl": "https://github.com/LSPosed/LSPosed.github.io/releases/download/shamiko-312/Shamiko-v1.2.1-312-release.zip"}],
        "tags": ["core", "hide"]
    },
    {
        "name": "Zygisk-Next",
        "author": "Dr-TSNG",
        "version": "官方最新",
        "description": "新一代 Zygisk 注入实现，替代 Magisk 自带版。",
        "downloadCount": "全网",
        "releases": [{"zipUrl": "https://github.com/Dr-TSNG/ZygiskNext/releases/latest/download/Zygisk-Next.zip"}],
        "tags": ["core", "zygisk"]
    }
]

# 内置真正的 META 模块（元挂载）
META_MODULES = [
    {
        "name": "Hybrid Mount",
        "author": "HuskyDG",
        "version": "内置推荐",
        "description": "强大的元挂载工具，实现模块文件的动态替换与挂载。",
        "downloadCount": "全网",
        "releases": [{"zipUrl": "https://github.com/HuskyDG/hybrid-mount/releases/latest/download/hybrid-mount.zip"}],
        "tags": ["meta", "mount"]
    }
]

def build_module_repo_page(page: ft.Page, theme_color):
    log_area = ft.TextField(
        multiline=True, read_only=True, expand=True, 
        bgcolor=ft.Colors.BLACK, color="#00FFD1", 
        text_size=12, text_style=ft.TextStyle(font_family="Consolas"),
        border=ft.InputBorder.NONE,
    )
    log_container = ft.Container(
        content=log_area, bgcolor="#05070A", border_radius=12,
        padding=15, height=150, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color))
    )
    
    status_text = ft.Text("正在拉取仓库列表...", size=13, color=theme_color, font_family="Microsoft YaHei")
    
    search_field = ft.TextField(
        hint_text="搜索模块名称、作者或标签 (试试搜 'meta')...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        color="white",
        border_color=ft.Colors.with_opacity(0.2, theme_color),
        on_change=lambda e: filter_modules(e.control.value)
    )
    
    grid_view = ft.GridView(
        expand=1, runs_count=3, max_extent=280, spacing=15, run_spacing=15, padding=10
    )
    
    all_modules = []

    def log(msg):
        log_area.value += msg + "\\n"
        page.update()

    def fetch_url(url, is_json=False):
        if "github.com" in url or "githubusercontent.com" in url:
            mirrors = [url, f"https://ghproxy.net/{url}", f"https://gh.llkk.cc/{url}"]
        elif "jsdelivr.net" in url:
            mirrors = [
                url,
                url.replace("cdn.jsdelivr.net", "fastly.jsdelivr.net"),
                url.replace("cdn.jsdelivr.net", "gcore.jsdelivr.net"),
                url.replace("cdn.jsdelivr.net/gh/", "raw.githubusercontent.com/"),
                url.replace("cdn.jsdelivr.net/gh/", "").replace("https://", "https://raw.gitmirror.com/")
            ]
        else:
            mirrors = [url]
            
        for i, target in enumerate(mirrors):
            try:
                req = urllib.request.Request(target, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    if is_json:
                        return response.read()
                    else:
                        content_length = response.getheader('Content-Length')
                        total_size = int(content_length) if content_length else 0
                        downloaded = 0
                        chunks = []
                        while True:
                            chunk = response.read(1024 * 64)
                            if not chunk: break
                            chunks.append(chunk)
                            downloaded += len(chunk)
                            if total_size > 0 and int((downloaded/total_size)*100) % 20 == 0:
                                log(f"⏳ 下载进度: {int((downloaded/total_size)*100)}%")
                        return b"".join(chunks)
            except Exception as e:
                if i < len(mirrors) - 1:
                    log(f"⚠️ 源 {i+1} 失败，切换备用加速源...")
                else:
                    log(f"❌ 所有源均失败: {e}")
                    raise e
        raise Exception("网络请求彻底失败")

    def filter_modules(keyword):
        keyword = keyword.lower().strip()
        grid_view.controls.clear()
        
        # 匹配 CORE 模块
        for m in CORE_MODULES:
            tags = m.get("tags", [])
            if (keyword in m["name"].lower() or keyword in m["author"].lower() or 
                keyword in m["description"].lower() or any(keyword in tag for tag in tags)):
                grid_view.controls.append(build_module_card(m, badge_type="CORE"))
                
        # 匹配 META 模块
        for m in META_MODULES:
            tags = m.get("tags", [])
            if (keyword in m["name"].lower() or keyword in m["author"].lower() or 
                keyword in m["description"].lower() or any(keyword in tag for tag in tags)):
                grid_view.controls.append(build_module_card(m, badge_type="META"))

        # 匹配社区模块，并自动识别 meta 关键字
        for m in all_modules:
            name = m.get("name", "").lower()
            author = m.get("author", "").lower()
            desc = m.get("description", "").lower()
            if keyword in name or keyword in author or keyword in desc:
                badge_type = None
                if "meta" in name or "hybrid" in name:
                    badge_type = "META"
                grid_view.controls.append(build_module_card(m, badge_type=badge_type))
                
        grid_view.update()

    def build_module_card(m, badge_type=None):
        name = m.get("name", "未知模块")
        author = m.get("author", "佚名")
        version = m.get("version", "-")
        desc = m.get("description", "暂无描述").strip()
        if len(desc) > 50: desc = desc[:50] + "..."
        download_count = m.get("downloadCount", 0)
        
        releases = m.get("releases", [])
        zip_url = releases[0].get("zipUrl", "") if releases else ""

        def do_download_and_install(e):
            if not zip_url:
                log(f"[错误] 模块 {name} 没有可用的下载链接！")
                return
            threading.Thread(target=download_and_install, args=(name, zip_url), daemon=True).start()

        # 构建标题行及徽章
        title_row = ft.Row([
            ft.Text(name, size=16, weight=ft.FontWeight.BOLD, color="white", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ])
        
        if badge_type == "CORE":
            title_row.controls.insert(0, ft.Container(content=ft.Text("CORE", size=9, weight=ft.FontWeight.W_900, color="#000000"), bgcolor="#00E5FF", padding=ft.padding.symmetric(horizontal=5, vertical=2), border_radius=4))
            title_row.controls[1].color = "#00E5FF"
        elif badge_type == "META":
            title_row.controls.insert(0, ft.Container(content=ft.Text("META", size=9, weight=ft.FontWeight.W_900, color="#000000"), bgcolor="#FFD700", padding=ft.padding.symmetric(horizontal=5, vertical=2), border_radius=4))
            title_row.controls[1].color = "#FFD700"

        return ft.Container(
            content=ft.Column([
                title_row,
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
            bgcolor=ft.Colors.with_opacity(0.1, theme_color) if badge_type else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border=ft.border.all(1, theme_color) if badge_type else ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            border_radius=15,
            padding=15,
        )

    def fetch_modules():
        log("> 正在连接 Huijui 官方仓库...")
        
        # 加载内置模块
        for m in CORE_MODULES:
            grid_view.controls.append(build_module_card(m, badge_type="CORE"))
        for m in META_MODULES:
            grid_view.controls.append(build_module_card(m, badge_type="META"))
            
        try:
            log("> 尝试使用 jsDelivr 节点加速...")
            data_bytes = fetch_url(MODULES_URL_JSdelivr, is_json=True)
        except Exception:
            try:
                log("> jsDelivr 失败，尝试代理...")
                data_bytes = fetch_url(MODULES_URL_RAW, is_json=True)
            except Exception as e:
                log(f"❌ 三方仓库拉取失败: {e}")
                status_text.value = f"仅加载内置模块 (网络限制)"
                status_text.color = ft.Colors.ORANGE
                page.update()
                return

        try:
            data = json.loads(data_bytes.decode('utf-8'))
            all_modules.extend(data)
            log(f"✅ 成功加载 {len(all_modules)} 个三方模块！")
            
            for m in all_modules:
                badge = "META" if ("meta" in m.get("name", "").lower() or "hybrid" in m.get("name", "").lower()) else None
                grid_view.controls.append(build_module_card(m, badge_type=badge))
            status_text.value = f"共找到 {len(all_modules) + len(CORE_MODULES) + len(META_MODULES)} 个模块"
            status_text.color = ft.Colors.GREEN
            page.update()
        except Exception as ex:
            log(f"❌ 解析 JSON 失败: {ex}")
            page.update()

    def download_and_install(name, url):
        log(f"\\n> 开始下载: {name}")
        local_zip = os.path.join(BASE_DIR, f"{name.replace('/', '_')}.zip")
        
        try:
            data = fetch_url(url)
            with open(local_zip, "wb") as f:
                f.write(data)
            log(f"✅ 下载完成: {local_zip} ({os.path.getsize(local_zip)//1024} KB)")

            remote_path = f"/sdcard/Download/{name.replace('/', '_')}.zip"
            log(f"> 正在推送到手机: {remote_path}")
            push_cmd = f'"{ADB_PATH}" push "{local_zip}" "{remote_path}"'
            proc = subprocess.Popen(push_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            for line in iter(proc.stdout.readline, ''):
                if line: log(line.strip())
            proc.wait()

            log("> 正在通过 Root 权限刷入模块...")
            detect_cmd = f'"{ADB_PATH}" shell "su -c \\"which ksud || which magisk || which ksu\\""'
            proc = subprocess.Popen(detect_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            out, _ = proc.communicate()
            detected_root = out.strip()

            if not detected_root:
                log("⚠️ 未检测到 Root 管理器，跳过自动安装。")
                return

            if "ksud" in detected_root:
                install_cmd = f'"{ADB_PATH}" shell "su -c \\"ksud module install {remote_path}\\""'
            elif "magisk" in detected_root:
                install_cmd = f'"{ADB_PATH}" shell "su -c \\"magisk --install-module {remote_path}\\""'
            else:
                install_cmd = f'"{ADB_PATH}" shell "su -c \\"ksu module install {remote_path}\\""'

            log(f"> 执行刷入命令: {install_cmd}")
            proc = subprocess.Popen(install_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            out = ""
            for line in iter(proc.stdout.readline, ''):
                if line:
                    log(line.strip())
                    out += line
            proc.wait()
            
            if proc.returncode == 0 or "success" in out.lower() or "完成" in out:
                log(f"✅ 模块 {name} 刷入成功！")
                status_text.value = "刷入成功，建议重启生效！"
                status_text.color = ft.Colors.GREEN
                
                def restart_device(e):
                    log("> 正在重启设备...")
                    subprocess.run(f'"{ADB_PATH}" reboot', shell=True)
                    log("✅ 重启指令已发送！")

                dlg = ft.AlertDialog(
                    title=ft.Text("刷入成功"),
                    content=ft.Text(f"模块 {name} 已成功注入手机。是否立即重启以激活模块？"),
                    actions=[
                        ft.TextButton("稍后重启", on_click=lambda e: page.close(dlg)),
                        ft.TextButton("立即重启", on_click=lambda e: [page.close(dlg), restart_device(None)])
                    ],
                )
                page.open(dlg)
            else:
                log("⚠️ 安装命令可能失败，请检查手机上的 Root 管理器。")
                
        except Exception as ex:
            log(f"❌ 操作失败: {ex}")

    threading.Thread(target=fetch_modules, daemon=True).start()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.EXTENSION, color=theme_color, size=28),
                ft.Text("Huijui 模块仓库", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")
            ]),
            ft.Container(height=5),
            status_text,
            search_field,
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

print("✅ v8 概念纠错版注入完毕！CORE 是青色，META 是金色！")