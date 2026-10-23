import flet as ft
import threading
import subprocess
import os

def build_terminal_page(page: ft.Page, theme_color):
    log_area = ft.TextField(multiline=True, read_only=True, expand=True, bgcolor=ft.Colors.BLACK, color=getattr(page, "ui_style", {}).get("log_color", "#00FFD1"), text_size=13, text_style=ft.TextStyle(font_family="Consolas"), border=ft.InputBorder.NONE)
    log_container = ft.Container(content=log_area, bgcolor=getattr(page, "ui_style", {}).get("log_bg", "#05070A"), border_radius=12, padding=15, expand=True, border=ft.border.all(1, ft.Colors.with_opacity(0.15, theme_color)))
    
    cmd_input = ft.TextField(hint_text="输入命令 (如 adb devices) 并回车...", bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color), on_submit=lambda e: run_cmd(e))
    
    def append_log(text):
        log_area.value += text + "\n"
        page.update()

    def run_cmd(e):
        cmd = cmd_input.value.strip()
        if not cmd: return
        cmd_input.value = ""
        append_log(f"\n> {cmd}")
        page.update()
        
        def thread():
            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                for line in iter(proc.stdout.readline, ''):
                    if line: append_log(line.strip())
                proc.stdout.close()
                proc.wait()
                append_log(f"[进程结束, 退出码: {proc.returncode}]")
            except Exception as ex:
                append_log(f"[执行出错]: {str(ex)}")
        threading.Thread(target=thread, daemon=True).start()

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.TERMINAL, color=theme_color, size=28), ft.Text("高级终端 · 实时 Shell", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Microsoft YaHei")]),
            ft.Container(height=10), log_container, cmd_input
        ], expand=True), expand=True, padding=20
    )
