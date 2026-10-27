# -*- coding: utf-8 -*-
"""
一键急救箱 v3.0 · KernelSU Edition
Author: 喜羊羊灰灰菜單
"""
import customtkinter as ctk
import subprocess
import os
import sys
import time
import queue
import threading
import traceback
import webbrowser
from tkinter import messagebox

try:
  from PIL import Image
  HAS_PIL = True
except ImportError:
  HAS_PIL = False

# ================= 配置区 =================
APP_NAME = "一键急救箱"
APP_VERSION = "v3.0"
COOLAPK = "https://www.coolapk.com/u/43549687"

# 配色方案
NEON = "#00ffd1"; NEON_DIM = "#00b894"
MAGENTA = "#ff2d92"; RED = "#ff3355"; ORANGE = "#ff8c00"
BG_DEEP = "#05070a"; BG_MAIN = "#0a0e14"; BG_PANEL = "#0f141b"
BG_CARD = "#141a22"; BORDER = "#1a232e"; BORDER_GLOW = "#1f3540"
TEXT_MAIN = "#e8f0f5"; TEXT_DIM = "#7a8a9a"; TEXT_MUTED = "#5a6a7a"
OK = "#00ff88"; WARN = "#ffb800"; ERR = "#ff3355"; INFO = "#00b4ff"

# 字体
F_TITLE = ("Microsoft YaHei UI", 19, "bold")
F_SUB = ("Microsoft YaHei UI", 10)
F_SUB_11 = ("Microsoft YaHei UI", 11)
F_SUB_26 = ("Microsoft YaHei UI", 26, "bold")
F_SECTION = ("Consolas", 11, "bold")
F_SECTION_CN = ("Microsoft YaHei UI", 13, "bold")
F_BTN = ("Microsoft YaHei UI", 13, "bold")
F_BTN_S = ("Microsoft YaHei UI", 11)
F_LOG = ("Consolas", 11)
F_CLOCK = ("Consolas", 10)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# ================= 工具函数 =================
def get_resource_path(rel):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, rel)
  return os.path.join(os.path.abspath("."), rel)


def alive(w):
  try:
    return w.winfo_exists()
  except Exception:
    return False


# ================= ADB 控制器 (重构版) =================
class Adb:
  def __init__(self):
    self.adb = f'"{get_resource_path("adb.exe")}"'
    self.fb = f'"{get_resource_path("fastboot.exe")}"'
    # 预热 adb 服务，极大提升后续命令速度
    self.run("start-server", timeout=5)

  def run(self, cmd, timeout=15):
    """阻塞式执行，返回结果，用于快速获取信息"""
    try:
      r = subprocess.run(cmd, shell=True, capture_output=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
      return r.stdout.decode('utf-8', errors='ignore').strip()
    except subprocess.TimeoutExpired:
      return "TIMEOUT"
    except Exception:
      return ""

  def stream_run(self, cmd, callback, timeout=300):
    """流式执行，实时返回日志，用于刷机/长任务"""
    try:
      process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='ignore',
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
      )
      start_time = time.time()
      for line in iter(process.stdout.readline, ''):
        if time.time() - start_time > timeout:
          process.kill()
          callback("✗ 命令超时，已终止", "err")
          break
        if line:
          callback(line.strip(), "info")
      process.wait()
      return process.returncode
    except Exception as e:
      callback(f"✗ 执行异常: {e}", "err")
      return -1

  def devices(self):
    """返回 (序列号, 状态) 的列表"""
    out = self.run(f"{self.adb} devices")
    devs = []
    for ln in out.splitlines()[1:]:
      parts = ln.split()
      if len(parts) >= 2:
        devs.append((parts[0], parts[1]))
    return devs

  def getprop(self, key):
    return self.run(f"{self.adb} shell getprop {key}")

  def root_available(self):
    out = self.run(f"{self.adb} shell su -c id", timeout=5)
    return "uid=0" in out


# ================= KernelSU 控制器 (v3.0 新增) =================
class KernelSU:
  def __init__(self, adb: Adb):
    self.adb = adb
    self.ksud_path = get_resource_path("ksud.exe")

  def is_available(self):
    if not os.path.exists(self.ksud_path):
      return False, "未找到 ksud.exe，请将其与 adb.exe 放在同一目录"
    out = self.adb.run(f'"{self.ksud_path}" --version', timeout=5)
    if "KernelSU" in out:
      return True, out
    return False, "ksud 执行异常，请检查版本"

  def patch_boot(self, boot_img, output_img, callback):
    """调用 ksud 修补 boot/init_boot"""
    if not os.path.exists(boot_img):
      callback("✗ 找不到 boot 镜像文件", "err")
      return False
    callback(f"▶ 开始修补: {os.path.basename(boot_img)}", "neon")
    cmd = f'"{self.ksud_path}" boot-patch -b "{boot_img}" -o "{output_img}"'
    ret = self.adb.stream_run(cmd, callback, timeout=120)
    if ret == 0:
      callback("✅ 修补完成！", "ok")
      return True
    else:
      callback("✗ 修补失败", "err")
      return False


# ================= 欢迎界面 =================
class WelcomeScreen(ctk.CTkFrame):
  def __init__(self, master, on_accept):
    super().__init__(master, fg_color=BG_DEEP, corner_radius=0)
    self.on_accept = on_accept
    self._build()

  def _build(self):
    wrap = ctk.CTkFrame(self, fg_color="transparent")
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    # Logo
    logo_ok = False
    if HAS_PIL:
      for ext in ("logo.ico", "logo.png", "icon.ico", "icon.png"):
        p = get_resource_path(ext)
        if os.path.exists(p):
          try:
            img = Image.open(p).convert("RGBA").resize((110, 110), Image.LANCZOS)
            self._logo = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))
            ctk.CTkLabel(wrap, image=self._logo, text="").pack(pady=(0, 18))
            logo_ok = True
            break
          except Exception:
            continue
    if not logo_ok:
      ctk.CTkLabel(wrap, text="🚑", font=("Segoe UI Emoji", 72), text_color=RED).pack(pady=(0, 18))

    ctk.CTkLabel(wrap, text=APP_NAME, font=F_SUB_26, text_color=RED).pack()
    ctk.CTkLabel(wrap, text=f"RESCUE EDITION · {APP_VERSION}", font=("Consolas", 12, "bold"), text_color=MAGENTA).pack(pady=(6, 4))
    ctk.CTkLabel(wrap, text="by 喜羊羊灰灰菜單", font=F_SUB_11, text_color=TEXT_DIM).pack()

    ctk.CTkFrame(wrap, height=1, width=440, fg_color=BORDER_GLOW).pack(pady=24)
    ctk.CTkLabel(wrap, text="⚠ 免责声明", font=("Microsoft YaHei UI", 14, "bold"), text_color=WARN).pack(anchor="w", padx=40, pady=(0, 10))
    
    for t in ["本工具仅用于合法持有设备的维修与恢复",
         "操作前请确保手机已解锁 BL 并已备份数据",
         "因使用本工具导致的任何设备损坏，作者概不负责",
         "继续使用即代表您已阅读并同意上述条款"]:
      ctk.CTkLabel(wrap, text=f" · {t}", font=("Microsoft YaHei UI", 11), text_color=TEXT_DIM, anchor="w", justify="left").pack(anchor="w", padx=40, pady=2)

    ctk.CTkFrame(wrap, height=1, width=440, fg_color=BORDER_GLOW).pack(pady=24)

    self.agree_var = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(wrap, text="我已阅读并同意上述条款", variable=self.agree_var, command=self._on_check,
            font=("Microsoft YaHei UI", 12), text_color=TEXT_MAIN, fg_color=RED, hover_color="#a02020",
            checkmark_color="#ffffff", border_color=BORDER_GLOW, border_width=2, corner_radius=6).pack(pady=(0, 18))

    self.btn = ctk.CTkButton(wrap, text="进入急救箱 →", command=self._on_enter, height=50, width=280,
                 font=F_BTN, fg_color="#2a3038", hover_color="#3a4048",
                 text_color=TEXT_MUTED, corner_radius=12, state="disabled")
    self.btn.pack(pady=(0, 24))

    ctk.CTkLabel(wrap, text=f"© 2026 喜羊羊灰灰菜單 · {APP_NAME} {APP_VERSION}", font=("Consolas", 10), text_color=TEXT_MUTED).pack()

  def _on_check(self):
    try:
      if self.agree_var.get():
        self.btn.configure(state="normal", fg_color=RED, hover_color="#a02020", text_color="#ffffff")
      else:
        self.btn.configure(state="disabled", fg_color="#2a3038", hover_color="#3a4048", text_color=TEXT_MUTED)
    except Exception: pass

  def _on_enter(self):
    if self.agree_var.get(): self.on_accept()


# ================= 主程序 =================
class RescuerApp(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.title(f"{APP_NAME} · by 喜羊羊灰灰菜單 {APP_VERSION}")
    self.geometry("1180x820")
    self.minsize(1100, 760)
    self.configure(fg_color=BG_DEEP)

    try:
      self.attributes("-alpha", 0.0)
      self._fade_in()
    except Exception: pass

    self.current_dir = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, 'frozen', False) else __file__))
    self.adb = Adb()
    self.ksu = KernelSU(self.adb)
    self.log_q = queue.Queue()
    self.ui_q = queue.Queue()
    self._log_count = 0
    self.current_tab = None
    self.is_scanning = False # 防止重复扫描

    try: self.iconbitmap(get_resource_path("logo.ico"))
    except Exception: pass

    self.protocol("WM_DELETE_WINDOW", self._on_close)

    self.welcome = WelcomeScreen(self, on_accept=self._enter_main)
    self.welcome.pack(fill="both", expand=True)
    self._main_built = False

  def _fade_in(self):
    if not alive(self): return
    try:
      a = self.attributes("-alpha")
      if a < 1.0:
        self.attributes("-alpha", min(1.0, a + 0.08))
        self.after(16, self._fade_in)
    except Exception:
      self.attributes("-alpha", 1.0) # 异常时强制恢复

  def _on_close(self):
    try:
      self.quit(); self.destroy()
    except Exception: pass

  def _enter_main(self):
    try:
      if self._main_built: return
      if self.welcome is not None:
        self.welcome.destroy()
        self.welcome = None
      self._build_ui()
      self._main_built = True
      self._poll_log(); self._poll_ui(); self._tick_clock()
      self.after(300, self._scan_device)
    except Exception as e:
      traceback.print_exc()

  def ui(self, fn, *a, **kw):
    self.ui_q.put((fn, a, kw))

  def _poll_ui(self):
    if not alive(self): return
    try:
      while True:
        fn, a, kw = self.ui_q.get_nowait()
        fn(*a, **kw)
    except queue.Empty: pass
    self.after(20, self._poll_ui)

  def log(self, msg, tag=None):
    self.log_q.put((msg, tag))

  def _poll_log(self):
    if not alive(self): return
    try:
      while True:
        msg, tag = self.log_q.get_nowait()
        if not alive(self.log_box): continue
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] ", "muted")
        self.log_box.insert("end", msg + "\n", tag or ())
        self.log_box.see("end")
        self._log_count += 1
      self.log_count.configure(text=f"{self._log_count} 行")
    except queue.Empty: pass
    self.after(50, self._poll_log)

  def _tick_clock(self):
    if not alive(self): return
    try: self.clock.configure(text=time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception: return
    self.after(1000, self._tick_clock)

  # ================= UI 构建 =================
  def _build_ui(self):
    self._build_topbar()
    self._build_body()
    self._build_footer()

  def _build_topbar(self):
    bar = ctk.CTkFrame(self, fg_color=BG_MAIN, height=88, corner_radius=0)
    bar.pack(fill="x"); bar.pack_propagate(False)
    ctk.CTkFrame(self, height=1, fg_color=BORDER_GLOW).pack(fill="x")

    brand = ctk.CTkFrame(bar, fg_color="transparent")
    brand.pack(side="left", padx=26, pady=16)

    logo_ok = False
    if HAS_PIL:
      for ext in ("logo.ico", "logo.png", "icon.ico", "icon.png"):
        p = get_resource_path(ext)
        if os.path.exists(p):
          try:
            img = Image.open(p)
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
            lw = ctk.CTkFrame(brand, fg_color=BG_CARD, corner_radius=14, width=58, height=58, border_width=1, border_color=BORDER_GLOW)
            lw.pack(side="left", padx=(0, 16)); lw.pack_propagate(False)
            ctk.CTkLabel(lw, image=self.logo_image, text="").pack(expand=True)
            logo_ok = True
            break
          except Exception: continue
    if not logo_ok:
      lw = ctk.CTkFrame(brand, fg_color=BG_CARD, corner_radius=14, width=58, height=58)
      lw.pack(side="left", padx=(0, 16)); lw.pack_propagate(False)
      ctk.CTkLabel(lw, text="🚑", font=("Segoe UI Emoji", 26), text_color=RED).pack(expand=True)

    tb = ctk.CTkFrame(brand, fg_color="transparent")
    tb.pack(side="left")
    ctk.CTkLabel(tb, text=APP_NAME, font=F_TITLE, text_color=RED, anchor="w").pack(anchor="w")
    
    row = ctk.CTkFrame(tb, fg_color="transparent")
    row.pack(anchor="w", pady=(5, 0))
    ctk.CTkLabel(row, text="KSU EDITION", font=("Consolas", 10, "bold"), text_color=MAGENTA).pack(side="left", padx=(0, 14))
    link = ctk.CTkLabel(row, text="酷安主页 →", font=F_SUB, text_color=TEXT_DIM, cursor="hand2")
    link.pack(side="left")
    link.bind("<Button-1>", lambda e: webbrowser.open(COOLAPK))

    sr = ctk.CTkFrame(bar, fg_color="transparent")
    sr.pack(side="right", padx=26)
    self.status_pill = ctk.CTkFrame(sr, fg_color="#0d2818", corner_radius=18, height=36, border_width=1, border_color="#1a4d2e")
    self.status_pill.pack(side="right"); self.status_pill.pack_propagate(False)
    self.status_dot = ctk.CTkLabel(self.status_pill, text="●", font=("Segoe UI", 15), text_color=OK)
    self.status_dot.pack(side="left", padx=(16, 8))
    self.status_label = ctk.CTkLabel(self.status_pill, text="等待检测", font=("Consolas", 12, "bold"), text_color=OK)
    self.status_label.pack(side="left", padx=(0, 18))

  def _build_body(self):
    body = ctk.CTkFrame(self, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=18, pady=16)

    # 左侧导航
    self.nav = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=16, width=200, border_width=1, border_color=BORDER)
    self.nav.pack(side="left", fill="y", padx=(0, 14))
    self.nav.pack_propagate(False)

    ctk.CTkLabel(self.nav, text="🧰 急救工具", font=F_SECTION_CN, text_color=TEXT_MAIN).pack(pady=(24, 4), padx=20, anchor="w")
    ctk.CTkLabel(self.nav, text="选择一个模块", font=F_SUB, text_color=TEXT_DIM).pack(padx=20, anchor="w", pady=(0, 16))

    self.nav_buttons = {}
    nav_items = [
      ("device", "📱 设备信息", "查看当前设备状态"),
      ("boot", "🩹 KSU 修补", "修补 init_boot (v3.0)"),
      ("emergency", "🚨 应急工具", "一键禁用模块"),
    ]
    for key, label, tip in nav_items:
      btn = ctk.CTkButton(self.nav, text=label, command=lambda k=key: self._switch_tab(k),
                height=48, anchor="w", font=F_BTN_S, fg_color="transparent",
                hover_color=BG_CARD, text_color=TEXT_DIM, corner_radius=10,
                border_width=1, border_color=BORDER)
      btn.pack(fill="x", padx=14, pady=4)
      self.nav_buttons[key] = btn

    ctk.CTkLabel(self.nav, text=f"{APP_VERSION} KSU", font=("Consolas", 10, "bold"), text_color=MAGENTA).pack(side="bottom", pady=(0, 4))
    ctk.CTkLabel(self.nav, text="© 喜羊羊灰灰菜單", font=F_SUB, text_color=TEXT_MUTED).pack(side="bottom", pady=(0, 20))

    # 右侧内容区
    self.content = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=16, border_width=1, border_color=BORDER)
    self.content.pack(side="left", fill="both", expand=True)

    header = ctk.CTkFrame(self.content, fg_color="transparent")
    header.pack(fill="x", padx=24, pady=(20, 4))
    self.content_title = ctk.CTkLabel(header, text="📱 设备信息", font=F_SECTION_CN, text_color=NEON, anchor="w")
    self.content_title.pack(side="left")
    
    # 进度条组件
    self.progress_frame = ctk.CTkFrame(self.content, fg_color="transparent")
    self.progress_frame.pack(fill="x", padx=24, pady=(10, 0))
    self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, corner_radius=4, fg_color=BG_DEEP, progress_color=NEON)
    self.progress_bar.set(0)
    self.progress_bar.pack(fill="x", pady=(0, 4))
    self.progress_text = ctk.CTkLabel(self.progress_frame, text="就绪", font=("Microsoft YaHei UI", 11), text_color=TEXT_DIM, anchor="w")
    self.progress_text.pack(fill="x")

    ctk.CTkFrame(self.content, height=1, fg_color=BORDER).pack(fill="x", padx=24, pady=12)

    self.page_container = ctk.CTkFrame(self.content, fg_color="transparent")
    self.page_container.pack(fill="both", expand=True, padx=24, pady=(0, 12))

    # 底部日志区
    log_frame = ctk.CTkFrame(self.content, fg_color=BG_DEEP, corner_radius=10, border_width=1, border_color=BORDER)
    log_frame.pack(fill="x", padx=24, pady=(0, 20))

    log_top = ctk.CTkFrame(log_frame, fg_color="transparent")
    log_top.pack(fill="x", padx=14, pady=(10, 4))
    ctk.CTkLabel(log_top, text="▤ LOG", font=F_SECTION, text_color=NEON).pack(side="left")
    self.log_count = ctk.CTkLabel(log_top, text="0 行", font=("Consolas", 10), text_color=TEXT_MUTED)
    self.log_count.pack(side="right")

    self.log_box = ctk.CTkTextbox(log_frame, font=F_LOG, fg_color=BG_DEEP, text_color=TEXT_MAIN, corner_radius=6, wrap="word", border_width=0, height=140)
    self.log_box.pack(fill="x", padx=10, pady=(0, 10))

    for tag, color in [("ok", OK), ("err", ERR), ("warn", WARN), ("info", INFO), ("neon", NEON), ("dim", TEXT_DIM), ("muted", TEXT_MUTED), ("magenta", MAGENTA), ("red", RED), ("white", TEXT_MAIN), ("orange", ORANGE)]:
      self.log_box.tag_config(tag, foreground=color)

    self._switch_tab("device")

  def _build_footer(self):
    ctk.CTkFrame(self, height=1, fg_color=BORDER_GLOW).pack(fill="x")
    f = ctk.CTkFrame(self, fg_color=BG_MAIN, height=32, corner_radius=0)
    f.pack(fill="x"); f.pack_propagate(False)
    ctk.CTkLabel(f, text="● RESCUE READY", font=("Consolas", 10, "bold"), text_color=RED).pack(side="left", padx=(20, 24))
    ctk.CTkFrame(f, width=1, height=14, fg_color=BORDER).pack(side="left")
    ctk.CTkLabel(f, text=f"{APP_NAME} {APP_VERSION}", font=F_CLOCK, text_color=TEXT_DIM).pack(side="left", padx=(24, 24))
    ctk.CTkFrame(f, width=1, height=14, fg_color=BORDER).pack(side="left")
    ctk.CTkLabel(f, text="by 喜羊羊灰灰菜單", font=F_SUB, text_color=MAGENTA).pack(side="left", padx=(24, 0))
    self.clock = ctk.CTkLabel(f, text="", font=F_CLOCK, text_color=TEXT_DIM)
    self.clock.pack(side="right", padx=20)

  # ================= Tab 切换 =================
  def _switch_tab(self, key):
    if self.current_tab == key: return
    self.current_tab = key

    for k, btn in self.nav_buttons.items():
      if k == key:
        btn.configure(fg_color=BG_CARD, text_color=RED, border_color=RED)
      else:
        btn.configure(fg_color="transparent", text_color=TEXT_DIM, border_color=BORDER)

    for w in self.page_container.winfo_children(): w.destroy()

    titles = {
      "device": ("📱 设备信息", "查看当前设备状态"),
      "boot": ("🩹 KSU 修补", "修补 init_boot (v3.0)"),
      "emergency": ("🚨 应急工具", "一键禁用模块"),
    }
    t, s = titles.get(key, ("", ""))
    self.content_title.configure(text=t)

    if key == "device": self._page_device()
    elif key == "boot": self._page_boot()
    elif key == "emergency": self._page_emergency()

  def _set_progress(self, val, text):
    """更新进度条 0.0 - 1.0"""
    try:
      self.progress_bar.set(val)
      self.progress_text.configure(text=text)
    except Exception: pass

  # ================= 页面：设备信息 =================
  def _page_device(self):
    wrap = ctk.CTkFrame(self.page_container, fg_color="transparent")
    wrap.pack(fill="both", expand=True)

    card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
    card.pack(fill="x", pady=(0, 12))

    ctk.CTkLabel(card, text="📱 当前设备", font=F_SECTION_CN, text_color=TEXT_MAIN, anchor="w").pack(fill="x", padx=20, pady=(16, 8))

    self.info_labels = {}
    for key, label in [("brand", "品牌"), ("model", "型号"), ("android", "系统"), ("sdk", "API"), ("bl", "BL"), ("root", "Root"), ("ksu", "KernelSU")]:
      row = ctk.CTkFrame(card, fg_color="transparent")
      row.pack(fill="x", padx=20, pady=5)
      ctk.CTkLabel(row, text=label, font=("Consolas", 11), text_color=TEXT_DIM, width=80, anchor="w").pack(side="left")
      val = ctk.CTkLabel(row, text="—", font=("Consolas", 12, "bold"), text_color=NEON, anchor="w")
      val.pack(side="left", padx=(10, 0), fill="x", expand=True)
      self.info_labels[key] = val

    ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=16)

    btn_row = ctk.CTkFrame(card, fg_color="transparent")
    btn_row.pack(fill="x", padx=20, pady=(0, 16))
    ctk.CTkButton(btn_row, text="🔍 重新扫描设备", command=self._scan_device, height=42, font=F_BTN,
           fg_color=NEON, hover_color=NEON_DIM, text_color="#001a14", corner_radius=10).pack(side="left", fill="x", expand=True, padx=(0, 6))
    ctk.CTkButton(btn_row, text="📋 复制设备信息", command=self._copy_device_info, height=42, font=F_BTN,
           fg_color=BG_PANEL, hover_color=BORDER_GLOW, text_color=TEXT_MAIN, corner_radius=10,
           border_width=1, border_color=BORDER_GLOW).pack(side="left", fill="x", expand=True, padx=(6, 0))

  def _scan_device(self):
    if self.is_scanning: return
    self.is_scanning = True
    threading.Thread(target=self._scan_device_thread, daemon=True).start()

  def _scan_device_thread(self):
    try:
      self.log("🔍 正在扫描设备...", "info")
      self.ui(self._set_progress, 0.1, "扫描设备中...")
      devs = self.adb.devices()

      if not devs:
        self.log(" ✗ 未检测到 ADB 设备", "err")
        self.log(" 💡 请连接手机并开启 USB 调试", "warn")
        self.ui(self._set_status, "设备未连接", ERR)
        self.ui(self._set_progress, 0, "就绪")
        return

      dev, state = devs[0]
      if state == "unauthorized":
        self.log(f" ⚠ 设备未授权: {dev}", "warn")
        self.log(" 📱 请在手机屏幕上点击「允许 USB 调试」", "neon")
        self.ui(self._set_status, "等待授权", WARN)
        self.ui(self._set_progress, 0, "等待授权")
        return

      if state != "device":
        self.log(f" ✗ 设备状态异常: {state}", "err")
        self.ui(self._set_status, "设备异常", ERR)
        return

      self.log(f" ✓ 已连接: {dev}", "ok")
      self.ui(self._set_status, "设备已连接", OK)
      self.ui(self._set_progress, 0.3, "读取设备属性...")

      brand = self.adb.getprop("ro.product.brand")
      model = self.adb.getprop("ro.product.model")
      ver = self.adb.getprop("ro.build.version.release")
      sdk = self.adb.getprop("ro.build.version.sdk")
      bl = self.adb.getprop("ro.boot.verifiedbootstate")
      bl_str = "已解锁" if bl in ("orange", "yellow") else "未解锁/未知"

      self.log(f" 📱 {brand} {model}", "info")
      self.log(f" 🤖 Android {ver} (API {sdk})", "info")
      self.log(f" 🔓 BL: {bl_str}", "info")

      self.ui(self._set_progress, 0.6, "检测 Root 权限...")
      self.log(" 🔑 正在检测 Root...", "info")
      root_str = "未激活"
      if self.adb.root_available():
        self.log(" ✓ Root 权限可用", "ok")
        root_str = "已激活"
      else:
        self.log(" ⚠ Root 权限不可用", "warn")

      self.ui(self._set_progress, 0.9, "检测 KernelSU...")
      ksu_ok, ksu_msg = self.ksu.is_available()
      ksu_str = "已安装" if ksu_ok else "未安装"
      if ksu_ok:
        self.log(f" ✓ KernelSU: {ksu_msg}", "ok")
      else:
        self.log(f" ⚠ KernelSU: {ksu_msg}", "warn")

      self.ui(self._update_info, "brand", brand)
      self.ui(self._update_info, "model", model)
      self.ui(self._update_info, "android", "Android " + ver)
      self.ui(self._update_info, "sdk", "API " + sdk)
      self.ui(self._update_info, "bl", bl_str)
      self.ui(self._update_info, "root", root_str)
      self.ui(self._update_info, "ksu", ksu_str)
      
      self.ui(self._set_progress, 1.0, "扫描完成")
      self.after(2000, lambda: self._set_progress(0, "就绪") if alive(self) else None)

    except Exception as e:
      self.log(f"✗ 扫描异常: {e}", "err")
    finally:
      self.is_scanning = False

  def _update_info(self, key, value):
    if key in self.info_labels:
      color = NEON
      if key == "root" and value == "已激活": color = OK
      elif key == "root" and value == "未激活": color = WARN
      elif key == "ksu" and value == "已安装": color = MAGENTA
      elif key == "ksu" and value == "未安装": color = WARN
      self.info_labels[key].configure(text=value, text_color=color)

  def _copy_device_info(self):
    try:
      lines = [f"{k}: {w.cget('text')}" for k, w in self.info_labels.items()]
      self.clipboard_clear()
      self.clipboard_append("\n".join(lines))
      self.log("✅ 设备信息已复制到剪贴板", "ok")
    except Exception as e:
      self.log(f"✗ 复制失败: {e}", "err")

  def _set_status(self, text, color):
    try:
      self.status_dot.configure(text_color=color)
      self.status_label.configure(text=text, text_color=color)
      bg_map = {OK: ("#0d2818", "#1a4d2e"), WARN: ("#2b2010", "#4d3a15"), ERR: ("#2b0e14", "#4d1a26")}
      bg, bd = bg_map.get(color, ("#0d2818", "#1a4d2e"))
      self.status_pill.configure(fg_color=bg, border_color=bd)
    except Exception: pass

  # ================= 页面：KSU 修补 =================
  def _page_boot(self):
    wrap = ctk.CTkFrame(self.page_container, fg_color="transparent")
    wrap.pack(fill="both", expand=True)

    card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
    card.pack(fill="x", pady=(0, 12))
    
    ctk.CTkLabel(card, text="🩹 KernelSU 修补", font=("Microsoft YaHei UI", 16, "bold"), text_color=TEXT_MAIN).pack(pady=(20, 10), padx=20, anchor="w")
    ctk.CTkLabel(card, text="将原厂 init_boot.img 放入本目录，点击下方按钮自动修补。", font=F_SUB_11, text_color=TEXT_DIM).pack(padx=20, anchor="w", pady=(0, 20))

    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    ctk.CTkButton(btn_frame, text="🔧 开始修补 init_boot", command=self._patch_boot_action, height=46, font=F_BTN,
           fg_color=MAGENTA, hover_color="#a02060", text_color="#ffffff", corner_radius=10).pack(fill="x")

  def _patch_boot_action(self):
    def run():
      boot_path = os.path.join(self.current_dir, "init_boot.img")
      out_path = os.path.join(self.current_dir, "init_boot_patched.img")
      self.ui(self._set_progress, 0.3, "修补中...")
      success = self.ksu.patch_boot(boot_path, out_path, self.log)
      if success:
        self.ui(self._set_progress, 1.0, "修补完成")
        self.log("💡 请将 init_boot_patched.img 刷入 fastboot flash init_boot", "neon")
      else:
        self.ui(self._set_progress, 0, "就绪")
    threading.Thread(target=run, daemon=True).start()

  # ================= 页面：应急工具 =================
  def _page_emergency(self):
    wrap = ctk.CTkFrame(self.page_container, fg_color="transparent")
    wrap.pack(fill="both", expand=True)

    card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
    card.pack(fill="x", pady=(0, 12))

    ctk.CTkLabel(card, text="🚨 应急工具", font=("Microsoft YaHei UI", 16, "bold"), text_color=ORANGE).pack(pady=(20, 10), padx=20, anchor="w")
    ctk.CTkLabel(card, text="用于设备无法正常开机、卡开机动画时的紧急恢复。", font=F_SUB_11, text_color=TEXT_DIM).pack(padx=20, anchor="w", pady=(0, 20))

    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
    btn_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    ctk.CTkButton(btn_frame, text="⛔ 一键禁用所有 Magisk/KSU 模块", command=self._disable_modules_action, height=46, font=F_BTN,
           fg_color=ORANGE, hover_color="#b05a00", text_color="#ffffff", corner_radius=10).pack(fill="x", pady=(0, 10))

  def _disable_modules_action(self):
    def run():
      self.log("🚨 正在尝试禁用所有模块...", "orange")
      self.ui(self._set_progress, 0.5, "禁用模块中...")
      # 针对 KernelSU 的模块路径
      cmd = f'{self.adb.adb} shell "su -c \'mv /data/adb/modules /data/adb/modules_disabled\'"'
      out = self.adb.run(cmd, timeout=10)
      if "TIMEOUT" in out or "denied" in out.lower() or not out:
        self.log(" ✗ 执行失败，请确保设备已 Root 并授权本工具", "err")
        self.ui(self._set_progress, 0, "就绪")
      else:
        self.log(" ✓ 模块已禁用，重启后生效", "ok")
        self.ui(self._set_progress, 1.0, "完成")
    threading.Thread(target=run, daemon=True).start()


def main():
  try:
    app = RescuerApp()
    app.mainloop()
  except Exception as e:
    traceback.print_exc()

if __name__ == "__main__":
  main()