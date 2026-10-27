# rewrite_terminal.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
terminal_path = os.path.join(BASE_DIR, "pages", "terminal.py")

terminal_code = '''import flet as ft
import threading
import subprocess
import os

class TerminalPage(ft.Container):
  def __init__(self, page: ft.Page):
    super().__init__()
    self.page = page
    self.expand = True
    
    theme_color = self.page.ui_style.get("log_color", "#00FFD1")
    
    # 1. 输出区（保持你喜欢的透黑底）
    self.terminal_output = ft.TextField(
      multiline=True, 
      read_only=True, 
      expand=True, 
      bgcolor=ft.Colors.TRANSPARENT, 
      color=theme_color,
      border=ft.InputBorder.NONE,
      text_size=14,
      value="HuiJui Core Terminal v1.0\\n等待输入命令...\\n",
      text_style=ft.TextStyle(font_family="Consolas")
    )
    
    log_container = ft.Container(
      content=self.terminal_output, 
      bgcolor=self.page.ui_style.get("log_bg", ft.Colors.with_opacity(0.2, "#000000")), 
      border_radius=12, padding=15, expand=True, 
      border=self.page.ui_style.get("card_border", ft.border.all(1, theme_color))
    )

    # 2. 输入区（终极玻璃化！）
    self.cmd_input = ft.TextField(
      hint_text="输入命令 (如 adb devices) 并回车执行...", 
      on_submit=self.run_cmd,
      bgcolor=ft.Colors.with_opacity(0.05, "#FFFFFF"), # 高透白玻璃底
      border_color=ft.Colors.with_opacity(0.4, "#FFFFFF"), # 亮白边框
      focused_border_color=theme_color, # 聚焦时变成主题青色
      border_radius=10,
      color="white",
      text_size=14,
      content_padding=ft.padding.all(15),
      text_style=ft.TextStyle(font_family="Consolas")
    )
    
    self.content = ft.Column([
      ft.Row([
        ft.Icon(ft.Icons.TERMINAL, color=theme_color, size=28), 
        ft.Text("高级终端 · 实时 Shell", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="MiSans")
      ]),
      ft.Container(height=10),
      log_container,
      ft.Container(height=10),
      self.cmd_input
    ], expand=True, spacing=10)

  def run_cmd(self, e):
    cmd = self.cmd_input.value.strip()
    if not cmd:
      return
    
    self.cmd_input.value = ""
    self.append_log(f"\\n> {cmd}\\n")
    self.page.update()
    
    # 🚨 铁律 1：开新线程跑底层命令，绝不卡死 UI！
    threading.Thread(target=self._exec_cmd_thread, args=(cmd,), daemon=True).start()

  def _exec_cmd_thread(self, cmd):
    try:
      process = subprocess.Popen(
        cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
      )
      
      for line in iter(process.stdout.readline, ''):
        if line:
          self.append_log(line)
      
      process.stdout.close()
      process.wait()
      self.append_log(f"\\n[进程结束, 退出码: {process.returncode}]\\n")
    except Exception as ex:
      self.append_log(f"\\n[执行出错]: {str(ex)}\\n")

  def append_log(self, text):
    self.terminal_output.value += text
    self.page.update()
'''

with open(terminal_path, "w", encoding="utf-8") as f:
  f.write(terminal_code)

print("✅ pages/terminal.py 已全量重写！输入框已彻底玻璃化！")