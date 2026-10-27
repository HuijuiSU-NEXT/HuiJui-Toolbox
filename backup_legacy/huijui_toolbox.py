# -*- coding: utf-8 -*-
"""
Huijui 工具箱 v5.0 · Pro Edition (Rebuilt)
刷机 / 救砖 / ADB / 教程 / 历史 五合一全能盒子
Author: 喜羊羊灰灰菜單
"""
import customtkinter as ctk
import subprocess, os, sys, zipfile, threading, time, queue, json
import webbrowser, shutil, math, re, traceback, hashlib
import ctypes, platform, sqlite3
from collections import deque
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

try:
  from PIL import Image
  HAS_PIL = True
except ImportError:
  HAS_PIL = False

# ===== v5.1 Pro 扩展模块 =====
try:
  from huijui_extended import ModeDetector, ExtendedTools, MODE_ICONS
  HAS_EXT = True
except Exception:
  HAS_EXT = False
  ModeDetector = None
  ExtendedTools = None
  MODE_ICONS = {}

try:
  from huijui_plus import PlusTools, PLUS_GROUPS
  HAS_PLUS = True
except Exception:
  HAS_PLUS = False
  PlusTools = None
  PLUS_GROUPS = []

# ================= 应用信息 =================
APP_NAME   = "Huijui 工具箱"
APP_VERSION = "v5.1"
APP_EDITION = "Pro+"
COOLAPK   = "https://www.coolapk.com/u/43549687"
CONFIG_FILE = "huijui_config.json"
HISTORY_DB  = "huijui_history.db"
LOG_MAX_LINES = 3000
LOCK_FILE  = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), ".huijui.lock")

# ================= 双主题 =================
THEMES = {
  "dark": {
    "ACCENT":"#39C5BB","ACCENT_HOVER":"#2BA69D","ACCENT_DIM":"#1A5F5A",
    "VIOLET":"#A070E0","VIOLET_DIM":"#4A3070",
    "OK":"#3FBF6E","WARN":"#F0A030","ERR":"#E05070","INFO":"#4FA0E8",
    "BG_DEEP":"#0B0E14","BG_MAIN":"#10141C","BG_PANEL":"#161B26",
    "BG_CARD":"#1E2430","BG_HOVER":"#2A303E","BG_ACTIVE":"#39C5BB",
    "BORDER":"#262E3C","BORDER_LIGHT":"#353F52",
    "TEXT_MAIN":"#EDF1F7","TEXT_DIM":"#9AA6B8","TEXT_MUTED":"#606A78",
    "ON_ACCENT":"#0B0E14",
  },
  "light": {
    "ACCENT":"#1E8C85","ACCENT_HOVER":"#176E68","ACCENT_DIM":"#B0E5E0",
    "VIOLET":"#7A4DC8","VIOLET_DIM":"#E0D0F5",
    "OK":"#2E9E58","WARN":"#C87800","ERR":"#C63858","INFO":"#2A72C8",
    "BG_DEEP":"#F0F2F5","BG_MAIN":"#F7F9FC","BG_PANEL":"#FFFFFF",
    "BG_CARD":"#F3F5F9","BG_HOVER":"#E8ECF3","BG_ACTIVE":"#1E8C85",
    "BORDER":"#DCE1E8","BORDER_LIGHT":"#C8D0DA",
    "TEXT_MAIN":"#0F1419","TEXT_DIM":"#38414E","TEXT_MUTED":"#5A6470",
    "ON_ACCENT":"#FFFFFF",
  },
}
_font_cache = {}
def F(name, size, weight="normal"):
  key = (name, size, weight)
  if key not in _font_cache: _font_cache[key] = (name, size, weight)
  return _font_cache[key]

F_TITLE   = F("Microsoft YaHei UI", 18, "bold")
F_SUB    = F("Microsoft YaHei UI", 10)
F_SUB_11   = F("Microsoft YaHei UI", 11)
F_HERO    = F("Microsoft YaHei UI", 30, "bold")
F_SECTION  = F("Consolas", 11, "bold")
F_SECTION_CN = F("Microsoft YaHei UI", 15, "bold")
F_KEY    = F("Consolas", 10)
F_VAL    = F("Consolas", 11, "bold")
F_BTN    = F("Microsoft YaHei UI", 13, "bold")
F_BTN_S   = F("Microsoft YaHei UI", 11)
F_LOG    = F("Consolas", 11)
F_CLOCK   = F("Consolas", 10)
F_TINY    = F("Consolas", 9)
F_STATUS   = F("Consolas", 11, "bold")
F_HERO_CN  = F("Microsoft YaHei UI", 22, "bold")

# ================= 分区定义 =================
COMMON_PHYSICAL = [
  ("vbmeta","vbmeta.img",[]),
  ("vbmeta_system","vbmeta_system.img",[]),
  ("vbmeta_vendor","vbmeta_vendor.img",[]),
  ("boot","boot.img",[]),
  ("init_boot","init_boot.img",[]),
  ("vendor_boot","vendor_boot.img",[]),
  ("dtbo","dtbo.img",[]),
  ("recovery","recovery.img",[]),
]
COMMON_LOGICAL = [
  ("system","system.img"),("system_ext","system_ext.img"),
  ("product","product.img"),("vendor","vendor.img"),
  ("odm","odm.img"),("mi_ext","mi_ext.img"),
  ("vendor_dlkm","vendor_dlkm.img"),("system_dlkm","system_dlkm.img"),
]
BRAND_PARTITIONS = {
  "xiaomi": [("cust","cust.img"),("super","super.img")],
  "oneplus": [("ocdt","ocdt.img"),("super","super.img")],
  "samsung": [("super","super.img")],
  "google": [("super","super.img")],
  "realme": [("super","super.img"),("ocdt","ocdt.img")],
  "vivo":  [("super","super.img")],
  "huawei": [("super","super.img")],
  "unknown": [],
}
DANGEROUS_DEFAULT = {
  "xbl","abl","tz","hyp","keymaster","devcfg","modemst1","modemst2",
  "fsg","bluetooth","modem","dsp","bootloader","radio","sbl","aboot",
}
PAYLOAD_PARTS = ("boot,init_boot,vendor_boot,dtbo,vbmeta,vbmeta_system,"
         "vbmeta_vendor,system,system_ext,product,vendor,odm,"
         "mi_ext,vendor_dlkm,system_dlkm,super,recovery,cust,ocdt")
STEPS = ["环境检查","检测设备","读取信息","查找卡刷包","提取载荷",
     "解包镜像","进入 Fastboot","刷物理分区","切换 Fastbootd","刷逻辑分区"]
STEP_PROGRESS = [0.02,0.06,0.12,0.18,0.25,0.40,0.60,0.68,0.78,0.80]

ERROR_DIAGNOSTICS = [
  (r"Not enough space","镜像空间不足：payload 解包不完整，重下卡刷包"),
  (r"Partition not found","分区名不存在：机型不匹配或卡刷包不对应"),
  (r"Write to device failed","写入失败：换线、换后置USB口、重进 Fastboot"),
  (r"Couldn't find partition","找不到分区：确认卡刷包为本机型编译"),
  (r"FAILED \(remote: 'Not allowed","被拒绝：BL 未解锁或 OEM 锁未关闭"),
  (r"Flashing is not allowed","分区保护：Anti-Rollback 版本不匹配"),
  (r"no such partition","分区不存在：检查机型与固件版本"),
  (r"cannot load","文件加载失败：镜像损坏，重新解包"),
  (r"generate image","生成镜像失败：payload 解包出错，查磁盘空间"),
  (r"Command failed","命令失败：查看上一条日志"),
  (r"more than one device","多设备冲突：拔掉其他设备重试"),
  (r"device unauthorized","未授权：在手机上点允许 USB 调试"),
  (r"device offline","设备离线：重插数据线 / 重启 adb server"),
]

ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
GARBAGE = set("Рђд─│┌┐└┘█▓░ ")

# ================= 主题代理 =================
class Theme:
  def __init__(self):
    # 绕过 __getattr__，直接写 __dict__
    self.__dict__["_d"] = dict(THEMES["dark"])
    self.__dict__["_bg_override"] = {}
  def set(self, name):
    # 用 __dict__ 直接取，不触发 __getattr__
    current_bg = self.__dict__.get("_bg_override") or {}
    if not isinstance(current_bg, dict):
      current_bg = {}
    self.__dict__["_d"] = dict(THEMES.get(name, THEMES["dark"]))
    if current_bg:
      self._d.update(current_bg)
  def __getattr__(self, k):
    # 只对 THEMES 里的键做 fallback
    return self.__dict__.get("_d", {}).get(k, "#FF00FF")
T = Theme()

# ================= 配置单例 =================
DEFAULT_CONFIG = {
  "theme":"dark","skip_wipe":False,"disable_verity":True,
  "auto_backup":True,"auto_root_patch":True,"dangerous_extra":[],
  "log_autoscroll":True,"firmware_dir":"","window_geometry":"1380x900",
  "confirm_dangerous":True,"min_battery":30,"max_temp":45,
  "check_firmware_match":True,"check_multi_device":True,
  "confirm_snapshot":True,
}
class ConfigManager:
  _i = None
  def __new__(cls):
    if cls._i is None:
      cls._i = super().__new__(cls)
      cls._i._data = dict(DEFAULT_CONFIG)
      cls._i._path = None
    return cls._i
  def init(self, path):
    self._path = path
    try:
      if path and os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
          self._data.update(json.load(f))
    except Exception: pass
  def get(self, k, d=None): return self._data.get(k, d)
  def set(self, k, v, save=True):
    self._data[k] = v
    if save: self.save()
  def save(self):
    try:
      if self._path:
        with open(self._path,"w",encoding="utf-8") as f:
          json.dump(self._data, f, ensure_ascii=False, indent=2)
      return True
    except Exception: return False
  def reset(self):
    self._data = dict(DEFAULT_CONFIG); self.save()

CFG = ConfigManager()

def _cfg_path():
  return os.path.join(get_app_dir(), CONFIG_FILE)

def cfg(key, val=None):
  if val is None: return CFG.get(key)
  CFG.set(key, val)

# ================= 工具函数 =================
def get_app_dir():
  """返回 exe 所在目录（Nuitka onefile / PyInstaller / 源码都兼容）"""
  # 1. Nuitka onefile：优先用环境变量
  for k in ("NUITKA_ONEFILE_BINARY", "NUITKA_ONEFILE_DIRECTORY"):
    env = os.environ.get(k)
    if env:
      if os.path.isfile(env):
        return os.path.dirname(os.path.abspath(env))
      if os.path.isdir(env):
        return os.path.abspath(env)
  # 2. Nuitka onefile 新版：sys.argv[0] 是 exe 路径
  if "__compiled__" in globals() or getattr(sys, 'frozen', False):
    try:
      argv0 = os.path.abspath(sys.argv[0])
      if argv0 and os.path.isfile(argv0) and argv0.lower().endswith(".exe"):
        return os.path.dirname(argv0)
    except Exception:
      pass
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    low = exe_dir.lower()
    # 只有当 sys.executable 落在临时目录时才回退到 cwd
    if "onefile_" in low or "temp" in low or "/tmp/" in low:
      cwd = os.getcwd()
      if "onefile_" not in cwd.lower() and "windows\\system32" not in cwd.lower():
        return cwd
    return exe_dir
  # 3. 源码运行
  return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(rel):
  if hasattr(sys,'_MEIPASS'): return os.path.join(sys._MEIPASS, rel)
  if "__compiled__" in globals():
    base = os.path.dirname(os.path.abspath(__file__))
    for c in (os.path.join(base,rel), os.path.join(base,"tools",rel)):
      if os.path.exists(c): return c
    env = os.environ.get("NUITKA_ONEFILE_BINARY")
    if env:
      b2 = os.path.dirname(env)
      for c in (os.path.join(b2,rel), os.path.join(b2,"tools",rel)):
        if os.path.exists(c): return c
    return os.path.join(base, rel)
  base = os.path.dirname(os.path.abspath(__file__))
  for c in (os.path.join(base,rel), os.path.join(base,"tools",rel)):
    if os.path.exists(c): return c
  return os.path.join(os.path.abspath("."), rel)

def alive(w):
  try: return w.winfo_exists()
  except Exception: return False

def lerp_color(c1, c2, t):
  t = max(0.0, min(1.0, t))
  try:
    r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
    r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
  except Exception: return c2

def is_admin():
  try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
  except Exception: return False

def run_as_admin():
  try:
    if getattr(sys,'frozen',False): exe, script = sys.executable, ""
    else: exe, script = sys.executable, os.path.abspath(__file__)
    params = " ".join(f'"{a}"' for a in sys.argv[1:])
    args = f'"{script}" {params}' if script else params
    ctypes.windll.shell32.ShellExecuteW(None,"runas",exe,args,None,1)
    return True
  except Exception: return False

def fmt_size(b):
  if b < 1024: return f"{b} B"
  if b < 1024**2: return f"{b/1024:.1f} KB"
  if b < 1024**3: return f"{b/1024**2:.1f} MB"
  return f"{b/1024**3:.2f} GB"

def safe_flag():
  return subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0

# ================= 品牌检测 =================
def detect_brand(brand_str):
  s = (brand_str or "").lower()
  if any(k in s for k in ("xiaomi","redmi","poco")): return "xiaomi"
  if "oneplus" in s: return "oneplus"
  if "samsung" in s: return "samsung"
  if any(k in s for k in ("google","pixel")): return "google"
  if any(k in s for k in ("realme","oppo")): return "realme"
  if "vivo" in s or "iqoo" in s: return "vivo"
  if any(k in s for k in ("huawei","honor")): return "huawei"
  return "unknown"
BRAND_DISPLAY = {"xiaomi":"小米 / Redmi / POCO","oneplus":"一加","samsung":"三星",
         "google":"Google Pixel","realme":"真我 / OPPO","vivo":"vivo / iQOO",
         "huawei":"华为 / 荣耀","unknown":"未知品牌"}
def get_brand_display(k): return BRAND_DISPLAY.get(k, "未知品牌")
def get_partitions_for_brand(bk):
  p = list(COMMON_PHYSICAL); l = list(COMMON_LOGICAL)
  for n,img in BRAND_PARTITIONS.get(bk,[]):
    if not any(x[0]==n for x in p) and not any(x[0]==n for x in l):
      p.append((n,img,[]))
  return p, l
_dangerous_cache = None
def is_dangerous(name):
  global _dangerous_cache
  if _dangerous_cache is None:
    _dangerous_cache = set(DANGEROUS_DEFAULT) | set(cfg("dangerous_extra") or [])
  return name.lower() in _dangerous_cache

def invalidate_dangerous_cache():
  global _dangerous_cache
  _dangerous_cache = None

# ================= 修复：Animator 节流 =================
class Animator:
  def __init__(self, root):
    self.root = root; self.running = True
    self._listeners = set(); self._last = time.time()
    self._tick()
  def register(self, cb): self._listeners.add(cb)
  def unregister(self, cb): self._listeners.discard(cb)
  def _is_busy(self):
    try:
      if self.root.state() == "iconic": return False
      return bool(self.root.winfo_viewable())
    except Exception: return True
  def _tick(self):
    if not self.running or getattr(self, "_destroyed", False): return
    now = time.time(); dt = now - self._last; self._last = now
    busy = self._is_busy()
    interval = 33 if busy else 250
    for cb in list(self._listeners):
      try: cb(dt)
      except Exception: self._listeners.discard(cb)
    try: self.root.after(interval, self._tick)
    except Exception: pass

# ================= 安全防护 =================
class SecurityGuard:
  def __init__(self, base_dir): self.base_dir = base_dir
  def check_admin(self): return is_admin()
  def single_instance(self):
    try:
      if os.path.exists(LOCK_FILE):
        try:
          with open(LOCK_FILE,"r") as f: old = int(f.read().strip())
          r = subprocess.run(f'tasklist /FI "PID eq {old}"', shell=True,
                    capture_output=True, text=True,
                    creationflags=safe_flag())
          if str(old) in (r.stdout or ""):
            return False, f"已有 Huijui 进程运行 (PID {old})"
        except Exception: pass
      with open(LOCK_FILE,"w") as f: f.write(str(os.getpid()))
      return True, ""
    except Exception: return True, ""
  def release_lock(self):
    try:
      if os.path.exists(LOCK_FILE): os.remove(LOCK_FILE)
    except Exception: pass
  def check_disk(self, path, min_gb=20):
    try:
      free = shutil.disk_usage(path).free / 1024**3
      return free >= min_gb, free
    except Exception: return True, -1.0
  def sha256(self, path, chunk=1024*1024, progress=None):
    h = hashlib.sha256()
    try:
      total = os.path.getsize(path); done = 0
      with open(path,"rb") as f:
        while True:
          b = f.read(chunk)
          if not b: break
          h.update(b); done += len(b)
          if progress and total > 0: progress(done/total)
      return h.hexdigest()
    except Exception as e: return f"ERR:{e}"

# ================= DeviceGuard 防呆 =================
class DeviceGuard:
  def __init__(self, adb, fb, runner):
    self.adb = adb; self.fb = fb; self.runner = runner
  def list_adb_devices(self):
    out = self.runner.run_quiet(f"{self.adb} devices")
    return [ln.split()[0] for ln in out.splitlines()[1:]
        if len(ln.split())>=2 and ln.split()[1]=="device"]
  def list_fb_devices(self):
    out = self.runner.run_quiet(f"{self.fb} devices")
    return [ln.split()[0] for ln in out.splitlines()
        if ln.strip() and "fastboot" in ln.lower()]
  def check_multi_device(self):
    n = len(self.list_adb_devices()) + len(self.list_fb_devices())
    if n > 1: return False, f"检测到 {n} 台设备，请只保留一台"
    return True, ""
  def check_battery(self, dev, min_level=None):
    min_level = min_level or int(cfg("min_battery") or 30)
    try:
      out = self.runner.run_quiet(f"{self.adb} -s {dev} shell dumpsys battery")
      m = re.search(r"level:\s*(\d+)", out)
      if not m: return True, "电量未知"
      lv = int(m.group(1))
      if lv < min_level: return False, f"电量 {lv}% < {min_level}%，禁止刷机"
      return True, f"电量 {lv}%"
    except Exception: return True, "电量未知"
  def check_temperature(self, dev, max_temp=None):
    max_temp = int((cfg("max_temp") or 45) * 10)
    try:
      out = self.runner.run_quiet(f"{self.adb} -s {dev} shell dumpsys battery")
      m = re.search(r"temperature:\s*(\d+)", out)
      if not m: return True, "温度未知"
      t = int(m.group(1))
      if t > max_temp: return False, f"手机温度 {t/10:.1f}°C 过高，请冷却"
      return True, f"温度 {t/10:.1f}°C"
    except Exception: return True, "温度未知"
  def check_firmware_match(self, zip_path, dev_name):
    if not cfg("check_firmware_match"): return True, "已跳过机型校验"
    try:
      with zipfile.ZipFile(zip_path) as z:
        if "payload_properties.txt" not in z.namelist():
          return True, "无 payload_properties.txt，跳过"
        txt = z.read("payload_properties.txt").decode("utf-8","ignore")
      m = re.search(r"post-build[=:]\s*([^\s]+)", txt)
      if not m: return True, "无 post-build 字段，跳过"
      parts = m.group(1).split("/")
      fw_dev = parts[1] if len(parts)>1 else ""
      if fw_dev and dev_name:
        if fw_dev.lower() not in dev_name.lower() and \
          dev_name.lower() not in fw_dev.lower():
          return False, f"固件 [{fw_dev}] ≠ 手机 [{dev_name}]，可能变砖"
      return True, f"机型匹配 ({fw_dev})"
    except Exception as e: return True, f"校验异常（跳过）: {e}"
  def check_active_slot(self, dev):
    try:
      return self.runner.run_quiet(
        f"{self.adb} -s {dev} shell getprop ro.boot.slot_suffix").strip() or "_a"
    except Exception: return "?"
  def confirm_dangerous(self, name):
    ans = simpledialog.askstring("⚠ 危险分区确认",
      f"即将刷入危险分区 [{name}]，可能导致变砖！\n若确认请输入大写 YES：")
    return ans == "YES"

# ================= FlashHistory =================
class FlashHistory:
  def __init__(self, base_dir):
    self.db = os.path.join(base_dir, HISTORY_DB); self._init()
  def _init(self):
    try:
      with sqlite3.connect(self.db) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS history(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          ts TEXT, brand TEXT, model TEXT, zip TEXT,
          duration INTEGER, success INTEGER, note TEXT)""")
    except Exception: pass
  def add(self, brand, model, zip_name, duration, success, note=""):
    try:
      with sqlite3.connect(self.db) as c:
        c.execute("INSERT INTO history(ts,brand,model,zip,duration,success,note)"
             " VALUES(?,?,?,?,?,?,?)",
             (datetime.now().isoformat(), brand, model,
              zip_name, duration, 1 if success else 0, note))
    except Exception: pass
  def all(self, limit=200):
    try:
      with sqlite3.connect(self.db) as c:
        return c.execute("SELECT ts,brand,model,zip,duration,success"
                 " FROM history ORDER BY id DESC LIMIT ?",
                 (limit,)).fetchall()
    except Exception: return []
  def clear(self):
    try:
      with sqlite3.connect(self.db) as c:
        c.execute("DELETE FROM history")
    except Exception: pass

# ================= 命令执行器（修复 stdin 挂死）=================
class CommandRunner:
  MAX_LOG_SIZE = 10*1024*1024
  def __init__(self, debug_path):
    self.debug_path = debug_path; self.stop_flag = False
    self._lock = threading.Lock()
  def clear_debug(self):
    with self._lock:
      try:
        if os.path.exists(self.debug_path): os.remove(self.debug_path)
      except Exception: pass
  def _rotate(self):
    try:
      if os.path.exists(self.debug_path) and \
        os.path.getsize(self.debug_path) > self.MAX_LOG_SIZE:
        old = self.debug_path + ".old"
        if os.path.exists(old): os.remove(old)
        os.replace(self.debug_path, old)
    except Exception: pass
  def append_debug(self, text):
    with self._lock:
      self._rotate()
      try:
        with open(self.debug_path,"a",encoding="utf-8",errors="ignore") as f:
          f.write(text + "\n")
      except Exception: pass
  def run(self, cmd, timeout=1800, cwd=None, on_tick=None, on_line=None):
    self.append_debug(f"\n{'='*60}\n[{time.strftime('%H:%M:%S')}] {cmd}\n")
    flags = safe_flag()
    if os.name=='nt': flags |= subprocess.CREATE_NEW_PROCESS_GROUP
    try:
      proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                  stderr=subprocess.STDOUT,
                  cwd=cwd, text=True, encoding='utf-8',
                  errors='ignore', bufsize=1,
                  creationflags=flags)
    except Exception as e:
      return -1, [f"启动失败: {e}"]
    def _reader():
      try:
        for line in proc.stdout:
          if not line: break
          line = line.rstrip("\r\n")
          if not line: continue
          self.append_debug(line)
          if on_line:
            try: on_line(line)
            except Exception: pass
      except Exception: pass
    threading.Thread(target=_reader, daemon=True).start()
    start = time.time(); next_tick = 5
    try:
      while True:
        if self.stop_flag:
          self._kill_tree(proc); return -2, ["用户中止"]
        ret = proc.poll()
        if ret is not None: break
        if time.time() - start > timeout:
          self._kill_tree(proc); return -1, ["命令超时"]
        if on_tick and time.time() - start > next_tick:
          on_tick(int(time.time() - start)); next_tick += 5
        time.sleep(0.15)
      return proc.returncode, self._extract_errors()
    except Exception as e:
      try: self._kill_tree(proc)
      except Exception: pass
      return -1, [f"异常: {e}"]
  def _kill_tree(self, proc):
    try:
      if os.name=='nt':
        subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True,
                capture_output=True, creationflags=safe_flag())
      else: proc.kill()
    except Exception:
      try: proc.kill()
      except Exception: pass
  def _extract_errors(self):
    errors = deque(maxlen=10)
    try:
      if not os.path.exists(self.debug_path): return list(errors)
      size = os.path.getsize(self.debug_path)
      with open(self.debug_path,"rb") as f:
        if size > 200*1024: f.seek(-200*1024, 2)
        text = f.read().decode('utf-8', errors='ignore')
      err_re = re.compile(r'(fail|error|invalid|denied|cannot|no such|panic|'
                r'unsupported|unable|refused|missing|corrupt)', re.I)
      for line in text.splitlines():
        c = self._clean_line(line)
        if c and err_re.search(c) and c not in errors: errors.append(c)
    except Exception: pass
    return list(errors)
  def _clean_line(self, line):
    line = CTRL_RE.sub('', ANSI_RE.sub('', line)).strip()
    if not line or len(line) < 2: return None
    if all(c in GARBAGE for c in line): return None
    if len(line) > 20 and sum(1 for c in line if c in GARBAGE or ord(c)>0x2500)/len(line) > 0.7:
      return None
    return line[:300] + "..." if len(line) > 300 else line
  def run_quiet(self, cmd, timeout=15, cwd=None):
    try:
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout, cwd=cwd,
                creationflags=safe_flag())
      return ((r.stdout or b"") + (r.stderr or b"")).decode('utf-8',errors='ignore').strip()
    except Exception: return ""

# ================= 备份 / Root =================
class BackupManager:
  def __init__(self, base_dir): self.base_dir = base_dir
  def create_backup_dir(self):
    d = os.path.join(self.base_dir,
             f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    try: os.makedirs(d, exist_ok=True); return d
    except Exception: return None
  def backup_partition(self, adb, dev, partition, dest_dir, log):
    out_local = os.path.join(dest_dir, f"{partition}.img")
    remote = f"/sdcard/_backup_{partition}.img"
    try:
      blk = None
      for path in [f"/dev/block/by-name/{partition}_a",
             f"/dev/block/by-name/{partition}",
             f"/dev/block/bootdevice/by-name/{partition}_a",
             f"/dev/block/bootdevice/by-name/{partition}"]:
        check = self._shell(adb, dev, f"ls {path} 2>/dev/null")
        if check and "No such" not in check: blk = path; break
      if not blk:
        log(f" ⚠ 未找到 {partition} 分区，跳过", "warn"); return None
      log(f" ⏳ 备份 {partition}...", "info")
      cmd = f'{adb} -s {dev} shell "su -c \'dd if={blk} of={remote}\'"'
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=120,
                creationflags=safe_flag())
      if r.returncode != 0:
        log(f" ⚠ {partition} 备份失败（可能未授权 su）","warn"); return None
      subprocess.run(f'{adb} -s {dev} pull {remote} "{out_local}"', shell=True,
              capture_output=True, timeout=120, creationflags=safe_flag())
      self._shell(adb, dev, f"rm {remote}")
      if os.path.exists(out_local):
        log(f" ✓ {partition}（{fmt_size(os.path.getsize(out_local))}）","ok")
        return out_local
      return None
    except Exception as e:
      log(f" ⚠ {partition} 异常: {e}", "warn"); return None
  def _shell(self, adb, dev, cmd):
    try:
      r = subprocess.run(f'{adb} -s {dev} shell "{cmd}"', shell=True,
                capture_output=True, timeout=20,
                creationflags=safe_flag())
      return (r.stdout or b"").decode('utf-8', errors='ignore').strip()
    except Exception: return ""

class RootPatcher:
  def __init__(self, work_dir): self.work_dir = work_dir
  def find_ksud(self):
    for n in ("ksud.exe","ksud"):
      p = get_resource_path(n)
      if os.path.exists(p): return p
    return None
  def find_init_boot(self):
    p = os.path.join(self.work_dir, "init_boot.img")
    if os.path.exists(p): return p
    try:
      for d in sorted(os.listdir(self.work_dir), reverse=True):
        if d.startswith("extracted_"):
          p = os.path.join(self.work_dir, d, "init_boot.img")
          if os.path.exists(p): return p
    except Exception: pass
    return None
  def find_boot(self):
    p = os.path.join(self.work_dir, "boot.img")
    if os.path.exists(p): return p
    try:
      for d in sorted(os.listdir(self.work_dir), reverse=True):
        if d.startswith("extracted_"):
          p = os.path.join(self.work_dir, d, "boot.img")
          if os.path.exists(p): return p
    except Exception: pass
    return None
  def patch(self, img_path, log):
    ksud = self.find_ksud()
    if not ksud:
      log(" ⚠ 未找到 ksud.exe", "warn")
      log(" 💡 手动：KernelSU 管理器「选择并修补」", "dim")
      return None
    if not os.path.exists(img_path):
      log(f" ✗ 文件不存在：{img_path}", "err"); return None
    out = os.path.join(self.work_dir,
              f"kernelsu_patched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.img")
    log(f" 📁 输入：{os.path.basename(img_path)}", "dim")
    log(f" 📁 输出：{os.path.basename(out)}", "dim")
    log(" ⏳ ksud 修补中...", "info")
    cmd = f'"{ksud}" boot-patch --boot "{img_path}" --out "{out}"'
    try:
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=180,
                creationflags=safe_flag())
      so = (r.stdout or b"").decode('utf-8', errors='ignore').strip()
      se = (r.stderr or b"").decode('utf-8', errors='ignore').strip()
      if so: log(f"   stdout: {so[:300]}", "muted")
      if se: log(f"   stderr: {se[:300]}", "muted")
      if "no kernel found in boot image" in (so+se).lower():
        log(" ✗ Windows 版 ksud 无法修补 init_boot.img！", "err")
        log(" 💡 init_boot.img 无内核，请用 KernelSU 管理器 APP", "warn")
        return None
      if r.returncode == 0 and os.path.exists(out):
        log(f" ✓ 修补成功（{fmt_size(os.path.getsize(out))}）", "ok")
        return out
      log(f" ✗ 修补失败，返回码 {r.returncode}", "err")
    except subprocess.TimeoutExpired: log(" ✗ 修补超时", "err")
    except Exception as e: log(f" ✗ 修补异常：{e}", "err")
    return None

# ================= 视觉组件 =================
class NeonRing(ctk.CTkCanvas):
  def __init__(self, master, size=150, thickness=11, animator=None, **kw):
    super().__init__(master, width=size, height=size, bg=T.BG_PANEL,
             highlightthickness=0, **kw)
    self.size = size; self.thickness = thickness
    self.target = 0.0; self.current = 0.0
    self.pulse = 0.0; self.is_running = False
    self._last_key = None
    if animator: animator.register(self._on_frame)
  def _on_frame(self, dt):
    if not alive(self): return
    try:
      diff = self.target - self.current
      step = diff * min(1.0, dt*8.0)
      if abs(diff) > 0.0005: self.current += step
      elif self.current != self.target: self.current = self.target
      if self.is_running: self.pulse = (self.pulse + dt*6.0) % 6.28318
      self._render()
    except Exception: pass
  def _render(self):
    if not alive(self): return
    # 修复：主题色也计入 key
    key = (round(self.current,3), self.is_running,
        T.ACCENT, T.BORDER, T.ACCENT_DIM)
    if key == self._last_key: return
    self._last_key = key
    self.delete("all")
    cx = cy = self.size/2
    r = (self.size - self.thickness)/2
    w = self.thickness
    self.create_oval(cx-r,cy-r,cx+r,cy+r, outline=T.BORDER, width=w)
    if self.current > 0.001:
      extent = -360 * self.current
      self.create_arc(cx-r,cy-r,cx+r,cy+r, start=90, extent=extent,
              style="arc", outline=T.ACCENT_DIM, width=int(w*1.9))
      if self.is_running:
        pf = 1 + 0.15*math.sin(self.pulse)
        self.create_arc(cx-r,cy-r,cx+r,cy+r, start=90, extent=extent,
                style="arc", outline=T.ACCENT_DIM, width=int(w*1.4*pf))
      self.create_arc(cx-r,cy-r,cx+r,cy+r, start=90, extent=extent,
              style="arc", outline=T.ACCENT, width=w)
      ang = math.radians(90 + extent)
      dx = cx + r*math.cos(ang); dy = cy - r*math.sin(ang); dr = w*0.6
      self.create_oval(dx-dr*1.7,dy-dr*1.7,dx+dr*1.7,dy+dr*1.7,
               fill=T.ACCENT_DIM, outline="")
      self.create_oval(dx-dr,dy-dr,dx+dr,dy+dr, fill=T.ACCENT, outline="")
    pct = int(round(self.current * 100))
    self.create_text(cx, cy-10, text=f"{pct}", fill=T.ACCENT,
             font=("Segoe UI", 28, "bold"))
    self.create_text(cx, cy+18, text="%", fill=T.TEXT_DIM,
             font=("Segoe UI", 11))
  def set(self, v): self.target = max(0.0, min(1.0, v))
  def set_running(self, r): self.is_running = r

class BreathingDot(ctk.CTkLabel):
  def __init__(self, master, color=None, animator=None, **kw):
    color = color or T.OK
    super().__init__(master, text="●", text_color=color,
             font=("Segoe UI", 15), **kw)
    self.base_color = color; self.phase = 0.0; self.active = False
    if animator: animator.register(self._on_frame)
  def set_color(self, c):
    self.base_color = c
    if not self.active:
      try: self.configure(text_color=c)
      except Exception: pass
  def set_active(self, a):
    self.active = a
    if not a:
      try: self.configure(text_color=self.base_color)
      except Exception: pass
  def _on_frame(self, dt):
    if not alive(self): return
    try:
      if self.active:
        self.phase = (self.phase + dt*6.0) % 6.28318
        t = (math.sin(self.phase)+1)/2
        self.configure(text_color=lerp_color(T.BG_DEEP, self.base_color, 0.4+0.6*t))
    except Exception: pass

class StepRow(ctk.CTkFrame):
  def __init__(self, master, index, name, animator=None):
    super().__init__(master, fg_color="transparent")
    self.index = index; self.name = name
    self.state = "idle"; self.pulse_phase = 0.0
    self.dot = ctk.CTkLabel(self, text="○", font=("Consolas", 12),
                text_color=T.TEXT_MUTED, width=18)
    self.dot.pack(side="left")
    self.label = ctk.CTkLabel(self, text=f"{index+1:02d} {name}",
                 font=F("Consolas", 10),
                 text_color=T.TEXT_MUTED, anchor="w")
    self.label.pack(side="left", padx=(6,0))
    if animator: animator.register(self._on_frame)
  def set_state(self, state):
    self.state = state
    if not alive(self.dot): return
    try:
      if state == "done":
        self.dot.configure(text="●", text_color=T.OK)
        self.label.configure(text_color=T.TEXT_DIM)
      elif state == "active":
        self.label.configure(text_color=T.ACCENT)
      elif state == "idle":
        self.dot.configure(text="○", text_color=T.TEXT_MUTED)
        self.label.configure(text_color=T.TEXT_MUTED)
    except Exception: pass
  def _on_frame(self, dt):
    if not alive(self): return
    try:
      if self.state == "active":
        self.pulse_phase = (self.pulse_phase + dt*6.0) % 6.28318
        t = (math.sin(self.pulse_phase)+1)/2
        self.dot.configure(text="◉",
                  text_color=lerp_color(T.ACCENT_DIM, T.ACCENT, t))
    except Exception: pass

class Toast(ctk.CTkToplevel):
  _stack = []
  def __init__(self, master, text, color=None, duration=2200, kind="info"):
    super().__init__(master)
    self.overrideredirect(True)
    self.attributes("-topmost", True)
    try: self.attributes("-alpha", 0.96)
    except Exception: pass
    colors = {"info":T.INFO,"ok":T.OK,"warn":T.WARN,"err":T.ERR}
    c = color or colors.get(kind, T.INFO)
    fr = ctk.CTkFrame(self, fg_color=T.BG_CARD, corner_radius=12,
             border_width=2, border_color=c)
    fr.pack(fill="both", expand=True)
    ctk.CTkLabel(fr, text=text, font=F("Microsoft YaHei UI", 12, "bold"),
           text_color=c).pack(padx=22, pady=12)
    self.update_idletasks()
    w, h = self.winfo_reqwidth(), self.winfo_reqheight()
    sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
    Toast._stack = [t for t in Toast._stack if alive(t)]
    offset = sum(t.winfo_height()+10 for t in Toast._stack)
    self.geometry(f"{w}x{h}+{sw-w-40}+{sh-h-90-offset}")
    Toast._stack.append(self)
    self.after(duration, self._close)
  def _close(self):
    try:
      Toast._stack = [t for t in Toast._stack if t is not self]
      self.destroy()
    except Exception: pass

# ================= 教程数据 =================
TUTORIAL_TEXT = """=====================================================
     Huijui 工具箱 · Pro Edition 使用指南
=====================================================

【刷机教程 · 官方卡刷包】
1. 准备：手机电量 > 50%，已解锁 BL，下载官方卡刷包(.zip)放入程序目录
2. 开启 USB 调试：设置 → 关于手机 → 连点版本号7次 → 开发者选项 → USB 调试
3. 点「一键刷机」，程序自动走完 10 步流程
4. 跨版本刷机建议清空数据，等待自动重启（首次 10-15 分钟）

【救砖教程 · 急救工具】
1. 能进 ADB：用「备份 boot/init_boot」先把关键分区备份出来
2. 能进 Fastboot：直接重新走一键刷机
3. 卡开机动画/模块冲突：连手机 →「一键禁用所有模块」
4. 刷错 boot/init_boot：
  · Fastboot 能进 → 重新刷官方 boot/init_boot
  · Fastboot 进不去：
   - 联发科(MTK)：MTK 线刷工具
   - 高通(QCOM)：进入 9008/EDL 模式，用 QFIL 救砖

【ADB 工具（Pro 新增）】
- ADB Sideload：卡刷 OTA 包 / 第三方 ROM
- 实时 Shell：直接在电脑端执行手机 shell
- 屏幕截图：一键截取手机屏幕并保存到电脑
- 安装 APK：拖拽即可安装到手机
- 无线连接：adb tcpip + connect
- 屏幕录制：最长 180 秒

【Pro 新特性】
- 双主题（暗黑/亮色）· 实时切换
- 侧边栏折叠 / 全局搜索 (Ctrl+K)
- 多品牌适配（含 vivo / 华为 / 荣耀）
- 危险分区二次确认 / 电量温度拦截
- 固件机型交叉校验（防刷错包变砖）
- 刷机历史记录（SQLite）
- 配置持久化（huijui_config.json）
- 日志导出 / 智能过滤 / 环形缓冲

【常见问题 FAQ】
Q1：未检测到设备？
A：① 换 USB 口（优先后置）② 换数据线 ③ 重开 USB 调试 ④ 检查驱动

Q2：解包提示 Not enough space？
A：磁盘空间不足，保留 20GB+

Q3：为什么杀毒软件报毒？
A：内置 adb.exe / fastboot.exe，属正常误报，加白名单即可

=====================================================
      by 喜羊羊灰灰菜單 · v5.1 Pro
=====================================================
"""

# ================= 欢迎界面 =================
class WelcomeScreen(ctk.CTkFrame):
  def __init__(self, master, on_accept, animator):
    super().__init__(master, fg_color=T.BG_DEEP, corner_radius=0)
    self.on_accept = on_accept
    self.animator = animator
    self._orig_logo = None
    self._logo_label = None
    self._entered = False
    self._logo_phase = 0.0
    self._logo_intro_done = False
    self._logo_intro_t0 = None
    self._anim_targets = []
    self._build()

  def _build(self):
    wrap = ctk.CTkFrame(self, fg_color="transparent")
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    # ---- Logo ----
    logo_ok = False
    if HAS_PIL:
      for ext in ("logo.ico", "logo.png", "icon.ico", "icon.png"):
        p = get_resource_path(ext)
        if os.path.exists(p):
          try:
            self._orig_logo = Image.open(p).convert("RGBA")
            _init = self._orig_logo.resize((110, 110), Image.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=_init,
                           dark_image=_init,
                           size=(110, 110))
            self._logo_label = ctk.CTkLabel(wrap, image=self._logo_img, text="")
            self._logo_label.pack(pady=(0, 18))
            logo_ok = True
            break
          except Exception:
            continue
    if not logo_ok:
      self._logo_label = ctk.CTkLabel(wrap, text="🐑",
        font=("Segoe UI Emoji", 72), text_color=T.ACCENT)
      self._logo_label.pack(pady=(0, 18))

    # ---- 文字组 ----
    self._title = ctk.CTkLabel(wrap, text=APP_NAME, font=F_HERO,
                  text_color=T.BG_DEEP)
    self._title.pack()
    self._anim_targets.append((self._title, T.ACCENT))

    self._sub = ctk.CTkLabel(wrap, text=f"{APP_EDITION.upper()} · {APP_VERSION}",
                 font=F("Consolas", 12, "bold"),
                 text_color=T.BG_DEEP)
    self._sub.pack(pady=(6, 4))
    self._anim_targets.append((self._sub, T.VIOLET))

    self._author = ctk.CTkLabel(wrap, text="by 喜羊羊灰灰菜單",
                   font=F_SUB_11, text_color=T.BG_DEEP)
    self._author.pack()
    self._anim_targets.append((self._author, T.TEXT_DIM))

    self._div1 = ctk.CTkFrame(wrap, height=1, width=0,
                  fg_color=T.BORDER_LIGHT)
    self._div1.pack(pady=22)

    self._disc_title = ctk.CTkLabel(wrap, text="⚠ 免责声明",
      font=F("Microsoft YaHei UI", 14, "bold"), text_color=T.BG_DEEP)
    self._disc_title.pack(anchor="w", padx=44, pady=(0, 10))
    self._anim_targets.append((self._disc_title, T.WARN))

    self._disc_items = []
    for t in ["刷机有风险，操作需谨慎",
         "请确保手机已解锁 BL 并已备份数据",
         "因使用本工具导致的任何设备损坏，作者概不负责",
         "继续使用即代表您已阅读并同意上述条款"]:
      lbl = ctk.CTkLabel(wrap, text=f" · {t}", font=F_SUB_11,
                text_color=T.BG_DEEP, anchor="w", justify="left")
      lbl.pack(anchor="w", padx=40, pady=2)
      self._disc_items.append(lbl)
      self._anim_targets.append((lbl, T.TEXT_DIM))

    self._div2 = ctk.CTkFrame(wrap, height=1, width=0,
                  fg_color=T.BORDER_LIGHT)
    self._div2.pack(pady=22)

    self.agree_var = ctk.BooleanVar(value=False)
    self._checkbox = ctk.CTkCheckBox(wrap, text="我已阅读并同意上述条款",
      variable=self.agree_var, command=self._on_check,
      font=F("Microsoft YaHei UI", 12), text_color=T.BG_DEEP,
      fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      checkmark_color=T.ON_ACCENT, border_color=T.BORDER_LIGHT,
      border_width=2, corner_radius=6)
    self._checkbox.pack(pady=(0, 18))
    self._anim_targets.append((self._checkbox, T.TEXT_MAIN))

    self.btn = ctk.CTkButton(wrap, text="进入工具箱 →",
      command=self._on_enter, height=50, width=300, font=F_BTN,
      fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.BG_DEEP, corner_radius=12, state="disabled")
    self.btn.pack(pady=(0, 24))

    self._copyright = ctk.CTkLabel(wrap,
      text=f"© 2026 喜羊羊灰灰菜單 · {APP_NAME} {APP_VERSION}",
      font=F_TINY, text_color=T.BG_DEEP)
    self._copyright.pack()
    self._anim_targets.append((self._copyright, T.TEXT_MUTED))

    # Logo 直接显示，只跑呼吸动画（不依赖 animator）
    if self._orig_logo is not None and self._logo_label is not None:
      self._logo_phase = 0.0
      self._logo_last_t = time.time()
      self.after(33, self._logo_breathe_tick)
    self.after(150, self._anim_start)

  def _anim_start(self):
    self.after(100, lambda: self._reveal(self._title))
    self.after(350, lambda: self._reveal(self._sub))
    self.after(550, lambda: self._reveal(self._author))
    self.after(750, self._grow_divider, self._div1)
    self.after(950, lambda: self._reveal(self._disc_title))
    for i, w in enumerate(self._disc_items):
      self.after(1100 + i * 120, lambda widget=w: self._reveal(widget))
    self.after(1700, self._grow_divider, self._div2)
    self.after(1900, lambda: self._reveal(self._checkbox))
    self.after(2200, lambda: self._reveal(self.btn))
    self.after(2500, lambda: self._reveal(self._copyright))

  def _reveal(self, widget):
    target = None
    for w, t in self._anim_targets:
      if w is widget:
        target = t; break
    if target is None:
      if widget is self.btn:
        target = T.TEXT_MUTED
      else:
        return
    start = T.BG_DEEP
    steps = 18
    def _step(i):
      if not alive(widget): return
      t = i / steps
      c = lerp_color(start, target, t)
      try: widget.configure(text_color=c)
      except Exception: pass
      if i < steps:
        widget.after(16, lambda: _step(i + 1))
    _step(0)

  def _grow_divider(self, divider):
    steps = 25
    target = 460
    def _step(i):
      if not alive(divider): return
      w = int(target * i / steps)
      try: divider.configure(width=w)
      except Exception: pass
      if i < steps:
        divider.after(16, lambda: _step(i + 1))
    _step(0)

  def _logo_intro_tick(self):
    """Logo 入场动画：0.7 秒弹性放大"""
    if not alive(self) or self._logo_label is None:
      return
    try:
      el = time.time() - getattr(self, "_logo_intro_start", time.time())
      DUR = 0.7
      if el < DUR:
        p = el / DUR
        c1 = 1.70158
        c3 = c1 + 1
        p2 = 1 + c3 * (p-1)**3 + c1 * (p-1)**2
        scale = 0.2 + 0.8 * max(0.0, min(1.2, p2))
        size = int(110 * scale)
        if self._orig_logo is not None and size > 8:
          resized = self._orig_logo.resize((size, size), Image.LANCZOS)
          self._logo_img = ctk.CTkImage(light_image=resized,
                         dark_image=resized,
                         size=(size, size))
          self._logo_label.configure(image=self._logo_img)
        self.after(16, self._logo_intro_tick)
      else:
        # 入场结束，切到呼吸动画
        if self._orig_logo is not None:
          resized = self._orig_logo.resize((110, 110), Image.LANCZOS)
          self._logo_img = ctk.CTkImage(light_image=resized,
                         dark_image=resized,
                         size=(110, 110))
          self._logo_label.configure(image=self._logo_img)
        self._logo_phase = 0.0
        self._logo_last_t = time.time()
        self.after(33, self._logo_breathe_tick)
    except Exception:
      pass

  def _logo_breathe_tick(self):
    """Logo 呼吸动画：独立 after 循环"""
    if not alive(self) or self._logo_label is None:
      return
    try:
      now = time.time()
      dt = now - getattr(self, "_logo_last_t", now)
      self._logo_last_t = now
      self._logo_phase = (self._logo_phase + dt*1.6) % 6.28318
      t = (math.sin(self._logo_phase)+1)/2
      size = int(110 + 6*t)
      if self._orig_logo is not None:
        resized = self._orig_logo.resize((size, size), Image.LANCZOS)
        self._logo_img = ctk.CTkImage(light_image=resized,
                       dark_image=resized,
                       size=(size, size))
        self._logo_label.configure(image=self._logo_img)
      self.after(33, self._logo_breathe_tick)
    except Exception:
      pass

  def _on_check(self):
    try:
      if self.agree_var.get():
        self.btn.configure(state="normal", fg_color=T.ACCENT,
                  hover_color=T.ACCENT_HOVER,
                  text_color=T.ON_ACCENT)
      else:
        self.btn.configure(state="disabled", fg_color=T.BG_CARD,
                  hover_color=T.BG_HOVER,
                  text_color=T.TEXT_MUTED)
    except Exception: pass

  def _on_enter(self):
    if self._entered: return
    self._entered = True
    if not self.agree_var.get(): return
    self._fadeout_and_enter()

  def _fadeout_and_enter(self):
    steps = 15
    targets = list(self._anim_targets) + [(self.btn, T.TEXT_MUTED)]
    def _step(i):
      if not alive(self): return
      t = i / steps
      for w, target in targets:
        if not alive(w): continue
        try:
          c = lerp_color(target, T.BG_DEEP, t)
          w.configure(text_color=c)
        except Exception: pass
      try:
        self._div1.configure(fg_color=lerp_color(T.BORDER_LIGHT, T.BG_DEEP, t))
        self._div2.configure(fg_color=lerp_color(T.BORDER_LIGHT, T.BG_DEEP, t))
      except Exception: pass
      try:
        self.btn.configure(
          fg_color=lerp_color(T.ACCENT, T.BG_DEEP, t),
          hover_color=lerp_color(T.ACCENT_HOVER, T.BG_DEEP, t))
      except Exception: pass
      if i < steps:
        self.after(22, lambda: _step(i + 1))
      else:
        try: self.on_accept()
        except Exception: pass
    _step(0)



# ================= 主程序 =================
class HuijuiToolboxApp(ctk.CTk):
  def __init__(self):
    super().__init__()
    CFG.init(_cfg_path())
    T.set(cfg("theme") or "dark")

    self.title(f"{APP_NAME} · {APP_VERSION} {APP_EDITION}")
    _geo = cfg("window_geometry") or ""
    try:
      _w = int(_geo.split("x")[0].split("+")[0]) if _geo else 0
    except Exception:
      _w = 0
    self.geometry(_geo if _w >= 1300 else "1500x920")
    self.minsize(1280, 780)
    self.configure(fg_color=T.BG_DEEP)
    try:
      self.attributes("-alpha", 0.0); self._fade_in()
    except Exception: pass

    self.current_dir = get_app_dir()
    self.extract_dir = None
    self.is_running = False
    self._is_backup_running = False
    self._is_scanning = False
    self._device_brand = ""
    self._device_mode = ""
    self._device_serial = ""
    self._device_model = ""
    self.success_flag = False
    self._flash_progress = 0.0
    self._flash_step_index = -1
    self.log_q = queue.Queue()
    self.ui_q = queue.Queue()
    self._log_count = 0
    self.debug_path = os.path.join(self.current_dir, "huijui_debug.log")
    self.current_tab = None
    self._nav_btns = {}
    self._nav_labels = {}
    self._nav_collapsed = False
    self._main_built = False
    self._toast_history = deque(maxlen=20)

    self.adb  = f'"{get_resource_path("adb.exe")}"'
    self.fb   = f'"{get_resource_path("fastboot.exe")}"'
    self.dumper = f'"{get_resource_path("payload-dumper-go.exe")}"'

    self.animator  = Animator(self)
    self.runner   = CommandRunner(self.debug_path)
    self.backup_mgr = BackupManager(self.current_dir)
    self.root_patcher = RootPatcher(self.current_dir)
    self.guard   = SecurityGuard(self.current_dir)
    self.device_guard = DeviceGuard(self.adb, self.fb, self.runner)
    self.history  = FlashHistory(self.current_dir)

    self._admin = self.guard.check_admin()
    ok, msg = self.guard.single_instance()
    self._single_ok = ok
    self._single_msg = msg

    self.logo_image = None
    self._load_logo()
    try: self.iconbitmap(get_resource_path("logo.ico"))
    except Exception: pass

    self.protocol("WM_DELETE_WINDOW", self._on_close)
    self._bind_shortcuts()

    self.welcome = WelcomeScreen(self, on_accept=self._enter_main,
                   animator=self.animator)
    self.welcome.pack(fill="both", expand=True)

  def _bind_shortcuts(self):
    self.bind("<Control-l>", lambda e: self.clear_log())
    self.bind("<Control-e>", lambda e: self.export_log())
    self.bind("<F5>", lambda e: self._scan_device())
    self.bind("<Control-k>", lambda e: self._focus_search())
    self.bind("<Control-r>", lambda e: (self.start() if not self.is_running else None))
    self.bind("<F1>", lambda e: self._switch_tab("tutorial"))
    self.bind("<F11>", lambda e: self.attributes(
      "-fullscreen", not self.attributes("-fullscreen")))

  def _focus_search(self):
    if hasattr(self, "nav_search") and alive(self.nav_search):
      self.nav_search.focus_set()

  def _fade_in(self):
    if not alive(self): return
    try:
      a = self.attributes("-alpha")
      if a < 1.0:
        self.attributes("-alpha", min(1.0, a+0.08))
        self.after(16, self._fade_in)
    except Exception: pass

  def _enter_main(self):
    if self._main_built: return
    self._main_built = True
    if not self._single_ok:
      messagebox.showwarning("重复运行", self._single_msg)
    if self.welcome is not None:
      try: self.welcome.destroy()
      except Exception: pass
      self.welcome = None
    try:
      if HAS_EXT:
        self.ext = ExtendedTools(self.adb, self.fb, self.runner,
                     log_cb=self.log,
                     ui_cb=self.ui,
                     work_dir=self.current_dir)
      else:
        self.ext = None
      self._build_ui()
      self._poll_log(); self._poll_ui(); self._tick_clock()
      self.after(300, self._scan_zip)
      self.after(500, self._scan_device)
    except Exception: traceback.print_exc()

  def _on_close(self):
    if self.is_running:
      if not messagebox.askyesno("退出中", "刷机/任务正在进行，确定退出吗？"):
        return
    try:
      cfg("window_geometry", self.geometry()); CFG.save()
    except Exception: pass
    try:
      self.runner.stop_flag = True
      self.guard.release_lock()
      self.animator.running = False
      self.animator._destroyed = True
      self.quit(); self.destroy()
    except Exception: pass

  def _load_logo(self):
    if not HAS_PIL: return
    for ext in ("logo.ico","logo.png","icon.ico","icon.png"):
      p = get_resource_path(ext)
      if os.path.exists(p):
        try:
          img = Image.open(p)
          self.logo_image = ctk.CTkImage(light_image=img, dark_image=img,
                          size=(44,44))
          return
        except Exception: continue

  def ui(self, fn, *a, **kw): self.ui_q.put((fn, a, kw))

  def _poll_ui(self):
    if not alive(self): return
    try:
      while True:
        fn, a, kw = self.ui_q.get_nowait()
        try: fn(*a, **kw)
        except Exception: pass
    except queue.Empty: pass
    self.after(20, self._poll_ui)

  # ================= UI 构建 =================
  def _build_ui(self):
    # v5.1 Pro+：应用已保存的背景方案
    try:
      import huijui_plus as _hp
      _bg_name = cfg("bg_scheme") or ""
      if _bg_name and _bg_name != "default":
        _scheme = getattr(_hp.PlusTools, "BG_SCHEMES", {}).get(_bg_name)
        if _scheme:
          T.__dict__["_bg_override"] = dict(_scheme)
          T._d.update(_scheme)
    except Exception:
      pass
    self._build_topbar()
    self._build_body()
    self._build_footer()

  def _build_topbar(self):
    self.topbar_border = ctk.CTkFrame(self, height=2, fg_color=T.ACCENT,
                      corner_radius=0)
    self.topbar_border.pack(fill="x")
    bar = ctk.CTkFrame(self, fg_color=T.BG_PANEL, height=72, corner_radius=0)
    bar.pack(fill="x"); bar.pack_propagate(False)
    ctk.CTkFrame(self, height=1, fg_color=T.BORDER).pack(fill="x")

    brand = ctk.CTkFrame(bar, fg_color="transparent")
    brand.pack(side="left", padx=22, pady=12)
    lw = ctk.CTkFrame(brand, fg_color=T.BG_CARD, corner_radius=12,
             width=52, height=52, border_width=2, border_color=T.ACCENT)
    lw.pack(side="left", padx=(0,14)); lw.pack_propagate(False)
    if self.logo_image:
      ctk.CTkLabel(lw, image=self.logo_image, text="").pack(expand=True)
    else:
      ctk.CTkLabel(lw, text="🐑", font=("Segoe UI Emoji", 24),
             text_color=T.ACCENT).pack(expand=True)

    tb = ctk.CTkFrame(brand, fg_color="transparent"); tb.pack(side="left")
    tr = ctk.CTkFrame(tb, fg_color="transparent"); tr.pack(anchor="w")
    ctk.CTkLabel(tr, text=APP_NAME, font=F_TITLE,
           text_color=T.TEXT_MAIN).pack(side="left")
    badge = ctk.CTkFrame(tr, fg_color=T.ACCENT, corner_radius=5,
               height=20, width=56)
    badge.pack(side="left", padx=(10,0)); badge.pack_propagate(False)
    ctk.CTkLabel(badge, text=" PRO+ ", font=F("Consolas", 10, "bold"),
           text_color=T.ON_ACCENT).pack(padx=6)
    row = ctk.CTkFrame(tb, fg_color="transparent"); row.pack(anchor="w", pady=(2,0))
    ctk.CTkLabel(row, text=APP_VERSION, font=F("Consolas", 11, "bold"),
           text_color=T.ACCENT).pack(side="left", padx=(0,12))
    ctk.CTkLabel(row, text="by 喜羊羊灰灰菜單", font=F_SUB,
           text_color=T.TEXT_DIM).pack(side="left", padx=(0,12))
    link = ctk.CTkLabel(row, text="酷安主页 →", font=F_SUB,
              text_color=T.TEXT_DIM, cursor="hand2")
    link.pack(side="left")
    link.bind("<Button-1>", lambda e: webbrowser.open(COOLAPK))
    link.bind("<Enter>", lambda e: link.configure(text_color=T.ACCENT))
    link.bind("<Leave>", lambda e: link.configure(text_color=T.TEXT_DIM))

    sr = ctk.CTkFrame(bar, fg_color="transparent"); sr.pack(side="right", padx=22)
    self.theme_btn = ctk.CTkButton(sr, text="🌗", width=42, height=42,
      font=("Segoe UI Emoji", 18), fg_color=T.BG_CARD,
      hover_color=T.BG_HOVER, text_color=T.TEXT_MAIN, corner_radius=10,
      border_width=1, border_color=T.BORDER_LIGHT,
      command=self._toggle_theme)
    self.theme_btn.pack(side="right", padx=(10,0))
    self.status_pill = ctk.CTkFrame(sr, fg_color="#0A1F14", corner_radius=20,
                     height=38, border_width=1, border_color="#14402A")
    self.status_pill.pack(side="right"); self.status_pill.pack_propagate(False)
    self.status_dot = BreathingDot(self.status_pill, color=T.OK,
                    animator=self.animator)
    self.status_dot.pack(side="left", padx=(16,8))
    self.status_label = ctk.CTkLabel(self.status_pill, text="READY",
                     font=F_STATUS, text_color=T.OK)
    self.status_label.pack(side="left", padx=(0,20))

  def _build_body(self):
    try:
      with open("D:/debug_bg.txt", "a", encoding="utf-8") as _f:
        _f.write(f"[_build_body] BG_PANEL={T.BG_PANEL} BG_DEEP={T.BG_DEEP} bg_scheme={cfg('bg_scheme')}\n")
    except Exception:
      pass
    body = ctk.CTkFrame(self, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=18, pady=16)
    self.body_frame = body

    self.card_left = ctk.CTkFrame(body, fg_color=T.BG_PANEL, corner_radius=12,
                    width=220, border_width=1, border_color=T.BORDER)
    self.card_left.pack(side="left", fill="y", padx=(0,14))
    self.card_left.pack_propagate(False)
    self._fill_nav(self.card_left)

    self.card_mid = ctk.CTkFrame(body, fg_color=T.BG_PANEL, corner_radius=12,
                   width=440, border_width=1, border_color=T.BORDER)
    self.card_mid.pack(side="left", fill="y", padx=(0,14))
    self.card_mid.pack_propagate(False)
    self.mid_container = ctk.CTkScrollableFrame(self.card_mid, fg_color="transparent", width=410, scrollbar_button_color=T.BG_PANEL, scrollbar_button_hover_color=T.BORDER_LIGHT)
    self.mid_container.pack(fill="both", expand=True)

    self.card_right = ctk.CTkFrame(body, fg_color=T.BG_PANEL, corner_radius=12,
                    border_width=1, border_color=T.BORDER)
    self.card_right.pack(side="left", fill="both", expand=True)
    self._fill_logger(self.card_right)

    self._switch_tab("device")

  def _fill_nav(self, nav):
    header = ctk.CTkFrame(nav, fg_color="transparent")
    header.pack(fill="x", padx=16, pady=(18,4))
    self.nav_toggle = ctk.CTkButton(header, text="☰", width=32, height=32,
      font=("Segoe UI Emoji", 14), fg_color="transparent",
      hover_color=T.BG_CARD, text_color=T.TEXT_DIM,
      command=self._toggle_nav)
    self.nav_toggle.pack(side="right")
    self.nav_title = ctk.CTkLabel(header, text="功能导航", font=F_SECTION_CN,
                    text_color=T.TEXT_MAIN, anchor="w")
    self.nav_title.pack(side="left")

    self.nav_search = ctk.CTkEntry(nav, placeholder_text="🔍 搜索 (Ctrl+K)",
                    font=F_SUB_11, height=32,
                    fg_color=T.BG_DEEP, border_color=T.BORDER,
                    text_color=T.TEXT_MAIN, corner_radius=8)
    self.nav_search.pack(fill="x", padx=12, pady=(6,10))
    self.nav_search.bind("<KeyRelease>", self._on_nav_search)
    self._nav_search_ref = self.nav_search

    ctk.CTkFrame(nav, height=1, fg_color=T.BORDER).pack(fill="x", padx=16, pady=(4,8))

    nav_items = [
      ("device","📱","设备信息"),
      ("flash","⚡","一键刷机"),
      ("rescue","🚨","急救工具"),
      ("adb","🔌","ADB 工具"),
      ("systools","🛠","系统工具"),
      ("apps","📦","应用管理"),
      ("history","📜","刷机历史"),
      # PLUS_NAV_MARKER
      ("tutorial","📖","使用教程"),
      ("settings","⚙","设置"),
      ("about","ℹ","关于"),
    ]
    self._nav_labels = {k:(i,t) for k,i,t in nav_items}
    self._nav_container = ctk.CTkFrame(nav, fg_color="transparent")
    self._nav_container.pack(fill="both", expand=True)

    for key, icon, title in nav_items:
      bf = ctk.CTkFrame(self._nav_container, fg_color="transparent", height=46)
      bf.pack(fill="x", padx=10, pady=2); bf.pack_propagate(False)
      btn = ctk.CTkButton(bf, text=f" {icon}  {title}",
        command=lambda k=key: self._switch_tab(k),
        height=46, anchor="w",
        font=F("Microsoft YaHei UI", 13, "bold"),
        fg_color="transparent", hover_color=T.BG_CARD,
        text_color=T.TEXT_DIM, corner_radius=10, border_width=0)
      btn.pack(fill="both", expand=True)
      self._nav_btns[key] = btn
      btn._parent_frame = bf

    ctk.CTkFrame(nav, height=1, fg_color=T.BORDER).pack(fill="x", padx=16, pady=(14,8))

    if not self._admin:
      ctk.CTkButton(nav, text="🛡  以管理员重启",
        command=self._restart_as_admin, height=38, font=F_BTN_S,
        fg_color="#2D1A00", hover_color="#4A2C00", text_color=T.WARN,
        corner_radius=8, border_width=1,
        border_color="#4A2C00").pack(side="bottom", pady=(0,8), padx=14, fill="x")

    bottom = ctk.CTkFrame(nav, fg_color="transparent")
    bottom.pack(side="bottom", fill="x", padx=20, pady=(0,16))
    ctk.CTkLabel(bottom, text=f"{APP_VERSION} {APP_EDITION}",
           font=F("Consolas", 10, "bold"),
           text_color=T.ACCENT).pack(anchor="w")
    ctk.CTkLabel(bottom, text="© 2026 喜羊羊灰灰菜單",
           font=F("Microsoft YaHei UI", 9),
           text_color=T.TEXT_MUTED).pack(anchor="w", pady=(2,0))

  def _toggle_nav(self):
    self._nav_collapsed = not self._nav_collapsed
    width = 62 if self._nav_collapsed else 220
    self.card_left.configure(width=width)
    for key, (icon, title) in self._nav_labels.items():
      btn = self._nav_btns[key]
      btn.configure(text=f" {icon}" if self._nav_collapsed
             else f" {icon}  {title}",
             anchor="center" if self._nav_collapsed else "w")
    if self._nav_collapsed:
      self.nav_title.pack_forget()
      self.nav_search.pack_forget()
    else:
      self.nav_title.pack(side="left")
      try:
        self.nav_search.pack(fill="x", padx=12, pady=(6,10),
                   before=self._nav_container)
      except Exception: pass

  def _on_nav_search(self, event):
    q = (self.nav_search.get() or "").strip().lower()
    for key, (icon, title) in self._nav_labels.items():
      bf = self._nav_btns[key]._parent_frame
      if not q or q in title.lower() or q in key:
        bf.pack(fill="x", padx=10, pady=2)
      else:
        bf.pack_forget()

  def _fill_logger(self, right):
    top = ctk.CTkFrame(right, fg_color="transparent")
    top.pack(fill="x", padx=24, pady=(20,8))
    ctk.CTkLabel(top, text="▤ CONSOLE", font=F_SECTION,
           text_color=T.ACCENT).pack(side="left")
    ctk.CTkLabel(top, text="实时日志", font=F("Microsoft YaHei UI", 12),
           text_color=T.TEXT_MAIN).pack(side="left", padx=(10,0))
    self.log_count = ctk.CTkLabel(top, text="0 行", font=F_TINY,
                    text_color=T.TEXT_MUTED)
    self.log_count.pack(side="right")

    tools = ctk.CTkFrame(right, fg_color="transparent")
    tools.pack(fill="x", padx=24, pady=(0,8))
    for text, cmd, w in [("🗑 清空",self.clear_log,76),
               ("💾 导出",self.export_log,76),
               ("📂 目录",self.open_log_dir,86)]:
      ctk.CTkButton(tools, text=text, command=cmd, height=28, width=w,
        font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
        text_color=T.TEXT_DIM, corner_radius=6,
        border_width=1, border_color=T.BORDER).pack(side="left", padx=(0,6))

    self.log_box = ctk.CTkTextbox(right, font=F_LOG, fg_color=T.BG_DEEP,
      text_color=T.TEXT_MAIN, corner_radius=10, wrap="word",
      border_width=1, border_color=T.BORDER,
      scrollbar_button_color=T.BG_PANEL,
      scrollbar_button_hover_color=T.BORDER_LIGHT)
    self.log_box.pack(fill="both", expand=True, padx=24, pady=(0,22))
    for tag, color in [("ok",T.OK),("err",T.ERR),("warn",T.WARN),
              ("info",T.INFO),("neon",T.ACCENT),("dim",T.TEXT_DIM),
              ("muted",T.TEXT_MUTED),("magenta",T.VIOLET),
              ("purple",T.VIOLET),("white",T.TEXT_MAIN),
              ("orange",T.WARN)]:
      self.log_box.tag_config(tag, foreground=color)
    self._welcome()

  def _build_footer(self):
    import tkinter as _tk
    ctk.CTkFrame(self, height=1, fg_color=T.BORDER).pack(fill="x")
    f = _tk.Frame(self, bg=T.BG_PANEL, height=30)
    f.pack(fill="x"); f.pack_propagate(False)
    self._footer_bar = f
    _tk.Label(f, text="● ONLINE", font=("Consolas", 10, "bold"),
         bg=T.BG_PANEL, fg=T.OK).pack(side="left", padx=(20, 24))
    _tk.Frame(f, width=1, height=14, bg=T.BORDER).pack(side="left")
    admin_txt = "ADMIN" if self._admin else "USER"
    admin_color = T.OK if self._admin else T.WARN
    _tk.Label(f, text=f"● {admin_txt}", font=("Consolas", 10, "bold"),
         bg=T.BG_PANEL, fg=admin_color).pack(side="left", padx=(24, 24))
    _tk.Frame(f, width=1, height=14, bg=T.BORDER).pack(side="left")
    _tk.Label(f, text=f"{APP_NAME} {APP_VERSION} {APP_EDITION}",
         font=("Consolas", 10), bg=T.BG_PANEL,
         fg=T.TEXT_DIM).pack(side="left", padx=(24, 24))
    _tk.Label(f, text="by 喜羊羊灰灰菜單", font=("Microsoft YaHei UI", 10),
         bg=T.BG_PANEL, fg=T.VIOLET).pack(side="left", padx=(24, 0))
    self.clock = _tk.Label(f, text="", font=("Consolas", 10),
                bg=T.BG_PANEL, fg=T.TEXT_DIM)
    self.clock.pack(side="right", padx=20)

  def _restart_as_admin(self):
    if messagebox.askyesno("提权确认",
      "将以管理员身份重启工具箱。\n当前实例会关闭。是否继续？"):
      if run_as_admin(): self._on_close()
      else: messagebox.showerror("提权失败", "无法提权，请手动右键以管理员运行。")

  def _switch_tab(self, key):
    if self.current_tab == key: return
    self.current_tab = key
    for k, btn in self._nav_btns.items():
      if k == key:
        btn.configure(fg_color=T.ACCENT, text_color=T.ON_ACCENT,
               hover_color=T.ACCENT_HOVER)
      else:
        btn.configure(fg_color="transparent", text_color=T.TEXT_DIM,
               hover_color=T.BG_CARD)
    for w in self.mid_container.winfo_children(): w.destroy()
    pages = {"device":self._page_device, "flash":self._page_flash,
         "rescue":self._page_rescue, "adb":self._page_adb,
         "history":self._page_history, "systools":self._page_systools, "apps":self._page_apps, "tutorial":self._page_tutorial,
         "settings":self._page_settings, "about":self._page_about}
    fn = pages.get(key)
    if fn: fn()

  # ================= 设备信息页 =================
  def _page_device(self):
    ctk.CTkLabel(self.mid_container, text="📱 DEVICE", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="设备信息", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    self.info = {}
    for key, label in [("brand","品牌"),("model","型号"),("android","系统"),
              ("sdk","API"),("bl","BL"),("root","Root"),
              ("ksu","KernelSU"),("mode","模式"),("serial","序列号"),
              ("slot","槽位")]:
      row = ctk.CTkFrame(self.mid_container, fg_color="transparent")
      row.pack(fill="x", padx=20, pady=5)
      ctk.CTkLabel(row, text=label, font=F_KEY, text_color=T.TEXT_DIM,
             width=64, anchor="w").pack(side="left")
      val = ctk.CTkLabel(row, text="—", font=F_VAL,
                text_color=T.ACCENT, anchor="w")
      val.pack(side="left", padx=(10,0), fill="x", expand=True)
      self.info[key] = val
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=18)
    for text, cmd, fg, hfg, tc, bc in [
      ("🔍 重新扫描设备 (F5)", self._scan_device,
       T.ACCENT, T.ACCENT_HOVER, T.ON_ACCENT, None),
      ("📋 复制设备信息", self._copy_device_info,
       T.BG_CARD, T.BG_HOVER, T.TEXT_MAIN, T.BORDER_LIGHT),
      ("🔓 检测 BL 锁状态", self._check_bl_action,
       T.BG_CARD, T.BG_HOVER, T.VIOLET, T.VIOLET_DIM)]:
      kw = {"border_width":1,"border_color":bc} if bc else {}
      ctk.CTkButton(self.mid_container, text=text, command=cmd, height=44,
        font=F_BTN, fg_color=fg, hover_color=hfg, text_color=tc,
        corner_radius=8, **kw).pack(pady=5, padx=20, fill="x")

    if HAS_PLUS:
      self._render_plus_group(self.mid_container, "🩺 健康诊断")

  # ================= 一键刷机页 =================
  def _page_flash(self):
    ctk.CTkLabel(self.mid_container, text="⏣ PROGRESS", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="刷机进度", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    wrap = ctk.CTkFrame(self.mid_container, fg_color="transparent")
    wrap.pack(pady=6)
    self.ring = NeonRing(wrap, size=140, thickness=10, animator=self.animator)
    self.ring.pack()
    self.step_text = ctk.CTkLabel(self.mid_container, text="等待开始",
                    font=F_BTN_S, text_color=T.TEXT_DIM)
    self.step_text.pack(pady=(8,16))
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=4)
    self.steps = []
    sw = ctk.CTkFrame(self.mid_container, fg_color="transparent")
    sw.pack(fill="x", padx=20, pady=12)
    for i, s in enumerate(STEPS):
      row = StepRow(sw, i, s, animator=self.animator)
      row.pack(fill="x", pady=2)
      self.steps.append(row)
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=18)
    self.btn_start = ctk.CTkButton(self.mid_container, text="▶ 一键刷机",
      command=self.start, height=52, font=F_BTN, fg_color=T.ACCENT,
      hover_color=T.ACCENT_HOVER, text_color=T.ON_ACCENT,
      corner_radius=10)
    self.btn_start.pack(pady=5, padx=20, fill="x")
    self.btn_stop = ctk.CTkButton(self.mid_container, text="⏹ 中止",
      command=self.stop, height=42, font=F_BTN_S,
      fg_color="#2A1418", hover_color="#5A1E28", text_color="#FF8899",
      corner_radius=8, border_width=1, border_color="#4A1E28",
      state="disabled")
    self.btn_stop.pack(pady=5, padx=20, fill="x")

    # v5.1 Pro 修复：切换 tab 后恢复刷机中状态
    if getattr(self, "is_running", False):
      try:
        self.ring.set(self._flash_progress)
        self.ring.current = self._flash_progress
        self.ring.set_running(True)
        self.btn_start.configure(state="disabled", text="刷机中...")
        self.btn_stop.configure(state="normal")
        idx = getattr(self, "_flash_step_index", -1)
        if 0 <= idx < len(self.steps):
          self.steps[idx].set_state("active")
          try:
            self.step_text.configure(text=STEPS[idx], text_color=T.ACCENT)
          except Exception:
            pass
          for k in range(idx):
            self.steps[k].set_state("done")
      except Exception:
        pass

  # ================= 急救工具页 =================
  def _page_rescue(self):
    ctk.CTkLabel(self.mid_container, text="🚨 RESCUE", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="急救工具", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    for text, cmd, fg, hfg, tc in [
      ("💾 备份 boot / init_boot", self.manual_backup,
       T.BG_CARD, T.BG_HOVER, T.VIOLET),
      ("🔧 修补 init_boot (KernelSU)", self._patch_boot_action,
       T.VIOLET, T.VIOLET_DIM, "#FFFFFF"),
      ("⛔ 一键禁用所有模块", self._disable_modules_action,
       T.WARN, "#B07A10", "#1A1000")]:
      ctk.CTkButton(self.mid_container, text=text, command=cmd, height=48,
        font=F_BTN, fg_color=fg, hover_color=hfg, text_color=tc,
        corner_radius=8).pack(pady=5, padx=20, fill="x")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=18)
    ctk.CTkLabel(self.mid_container, text="▸ 应急信息",
           font=F_SECTION, text_color=T.ACCENT).pack(padx=20, anchor="w")
    tip = ctk.CTkTextbox(self.mid_container, font=F_SUB_11,
      fg_color=T.BG_DEEP, text_color=T.TEXT_DIM, corner_radius=8,
      wrap="word", border_width=1, border_color=T.BORDER, height=170)
    tip.pack(fill="both", expand=True, padx=20, pady=(6,20))
    tip.insert("1.0",
      "【刷错 boot/init_boot 救砖流程】\n"
      "1. 手机还能进 Fastboot：重刷官方 boot.img / init_boot.img\n"
      "2. 只能进 Recovery：用官方卡刷包 sideload\n"
      "3. 完全黑屏：MTK 用 SP Flash Tool，高通进 9008/EDL 用 QFIL\n"
      "4. 分区表损坏：只能用厂家原厂工具深度救砖\n\n"
      "⚠ 急救前请确认：电量 > 30% / 原装数据线 / 后置 USB 口")
    tip.configure(state="disabled")

    if HAS_PLUS:
      self._render_plus_group(self.mid_container, "🚨 紧急救援")

  # ================= ADB 工具页 =================
  def _page_adb(self):
    ctk.CTkLabel(self.mid_container, text="🔌 ADB TOOLKIT", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="ADB 工具", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    scroll = self.mid_container

    # 1. Sideload
    ctk.CTkLabel(scroll, text="▸ ADB Sideload", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    self.sideload_path = ctk.CTkLabel(scroll, text="未选择文件",
      font=F_TINY, text_color=T.TEXT_MUTED, anchor="w", wraplength=320)
    self.sideload_path.pack(padx=12, fill="x", anchor="w")
    row1 = ctk.CTkFrame(scroll, fg_color="transparent")
    row1.pack(fill="x", padx=12, pady=(6,0))
    ctk.CTkButton(row1, text="选择 zip", command=self._pick_sideload,
      height=36, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.TEXT_MAIN, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(side="left", expand=True, fill="x",
                        padx=(0,4))
    ctk.CTkButton(row1, text="开始 Sideload", command=self._do_sideload,
      height=36, font=F_BTN_S, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      text_color=T.ON_ACCENT, corner_radius=8).pack(side="left", expand=True,
                              fill="x", padx=(4,0))
    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    # 2. 屏幕截图 + 录屏
    ctk.CTkLabel(scroll, text="▸ 屏幕截图 / 录制", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    row2 = ctk.CTkFrame(scroll, fg_color="transparent")
    row2.pack(fill="x", padx=12, pady=(6,0))
    ctk.CTkButton(row2, text="📸 截图", command=self._do_screencap,
      height=40, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.INFO, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(side="left", expand=True, fill="x",
                        padx=(0,4))
    ctk.CTkButton(row2, text="🎬 录屏(180s)", command=self._do_screenrecord,
      height=40, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.INFO, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(side="left", expand=True, fill="x",
                        padx=(4,0))
    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    # 3. 安装 APK
    ctk.CTkLabel(scroll, text="▸ 安装 APK", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    ctk.CTkButton(scroll, text="📦 选择 APK 并安装", command=self._do_install_apk,
      height=40, font=F_BTN, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.VIOLET, corner_radius=8, border_width=1,
      border_color=T.VIOLET_DIM).pack(fill="x", padx=12, pady=(6,0))
    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    # 4. 无线连接
    ctk.CTkLabel(scroll, text="▸ 无线 ADB (需同 WiFi)", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    self.wireless_ip = ctk.CTkEntry(scroll, font=F_LOG,
      placeholder_text="手机 IP，如 192.168.1.100:5555",
      fg_color=T.BG_DEEP, border_color=T.BORDER, text_color=T.TEXT_MAIN,
      height=38, corner_radius=8)
    self.wireless_ip.pack(fill="x", padx=12, pady=(6,6))
    row3 = ctk.CTkFrame(scroll, fg_color="transparent")
    row3.pack(fill="x", padx=12)
    ctk.CTkButton(row3, text="开启 tcpip", command=self._do_tcpip,
      height=38, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.TEXT_MAIN, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(side="left", expand=True, fill="x",
                        padx=(0,4))
    ctk.CTkButton(row3, text="连接", command=self._do_connect_wireless,
      height=38, font=F_BTN_S, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      text_color=T.ON_ACCENT, corner_radius=8).pack(side="left", expand=True,
                              fill="x", padx=(4,0))
    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    # 5. Shell
    ctk.CTkLabel(scroll, text="▸ 实时 Shell", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    ctk.CTkLabel(scroll, text="输入 adb shell 命令（无需加 adb shell 前缀）",
           font=F_TINY, text_color=T.TEXT_DIM).pack(padx=12, anchor="w")
    self.shell_input = ctk.CTkEntry(scroll, font=F_LOG,
      placeholder_text="getprop ro.product.model", fg_color=T.BG_DEEP,
      border_color=T.BORDER, text_color=T.TEXT_MAIN, height=38,
      corner_radius=8)
    self.shell_input.pack(fill="x", padx=12, pady=(6,6))
    self.shell_input.bind("<Return>", lambda e: self._do_shell())
    ctk.CTkButton(scroll, text="▶ 执行", command=self._do_shell,
      height=38, font=F_BTN, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      text_color=T.ON_ACCENT, corner_radius=8).pack(fill="x", padx=12,
                              pady=(0,10))

    # ================= v5.1 Pro：按模式刷入 =================
    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)
    ctk.CTkLabel(scroll, text="▸ 按模式刷入", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,4))
    ctk.CTkLabel(scroll, text="自动识别 ADB / Sideload / Recovery / Fastboot / Fastbootd / EDL / BROM",
           font=F_TINY, text_color=T.TEXT_DIM, wraplength=340,
           justify="left").pack(padx=12, anchor="w")
    mode_row = ctk.CTkFrame(scroll, fg_color="transparent")
    mode_row.pack(fill="x", padx=12, pady=(6,0))
    self.mode_label = ctk.CTkLabel(mode_row, text="当前模式：—",
      font=F_LOG, text_color=T.TEXT_MUTED, anchor="w")
    self.mode_label.pack(side="left", fill="x", expand=True)
    ctk.CTkButton(scroll, text="🔍 刷新模式", command=self._refresh_mode,
      height=36, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.TEXT_MAIN, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(fill="x", padx=12, pady=(6,8))

    ctk.CTkLabel(scroll, text="ADB 模式操作", font=F_SECTION,
           text_color=T.VIOLET).pack(padx=12, anchor="w", pady=(6,2))
    adb_ops = ctk.CTkFrame(scroll, fg_color="transparent")
    adb_ops.pack(fill="x", padx=12)
    for txt, fn in [
      ("📜 Logcat", lambda: self._call_ext("logcat_dump")),
      ("🐞 Bugreport", lambda: self._call_ext("bugreport_dump")),
      ("📦 包列表", lambda: self._call_ext("list_packages")),
      ("🔧 分区大小", lambda: self._call_ext("partition_sizes")),
      ("🌳 提取设备树", lambda: self._call_ext("extract_device_tree")),
    ]:
      ctk.CTkButton(adb_ops, text=txt, command=fn, height=34,
        font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
        text_color=T.TEXT_MAIN, corner_radius=6, border_width=1,
        border_color=T.BORDER).pack(side="left", expand=True, fill="x",
                       padx=(0,4))

    ctk.CTkLabel(scroll, text="Sideload / Recovery", font=F_SECTION,
           text_color=T.WARN).pack(padx=12, anchor="w", pady=(10,2))
    ctk.CTkButton(scroll, text="📥 选择 OTA/ROM 并 Sideload",
      command=self._pick_and_sideload,
      height=40, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.WARN, corner_radius=8, border_width=1,
      border_color="#4A2C00").pack(fill="x", padx=12, pady=(4,0))

    ctk.CTkLabel(scroll, text="Fastboot / Fastbootd", font=F_SECTION,
           text_color=T.INFO).pack(padx=12, anchor="w", pady=(10,2))
    fb_ops = ctk.CTkFrame(scroll, fg_color="transparent")
    fb_ops.pack(fill="x", padx=12)
    for txt, fn in [
      ("📋 全部变量", lambda: self._call_ext("fb_all_vars")),
      ("🔀 切换槽位", lambda: self._switch_slot_dialog()),
      ("🧹 擦除分区", lambda: self._erase_dialog()),
      ("🔓 解锁 BL", lambda: self._call_ext("fb_unlock")),
    ]:
      ctk.CTkButton(fb_ops, text=txt, command=fn, height=34,
        font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
        text_color=T.TEXT_MAIN, corner_radius=6, border_width=1,
        border_color=T.BORDER).pack(side="left", expand=True, fill="x",
                       padx=(0,4))
    fb_row = ctk.CTkFrame(scroll, fg_color="transparent")
    fb_row.pack(fill="x", padx=12, pady=(6,0))
    self.fb_part_entry = ctk.CTkEntry(fb_row, placeholder_text="分区名，如 recovery",
      font=F_LOG, fg_color=T.BG_DEEP, border_color=T.BORDER,
      text_color=T.TEXT_MAIN, height=34, corner_radius=6)
    self.fb_part_entry.pack(side="left", fill="x", expand=True, padx=(0,4))
    ctk.CTkButton(fb_row, text="⚡ 刷单分区", command=self._flash_single_action,
      height=34, font=F_TINY, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      text_color=T.ON_ACCENT, corner_radius=6).pack(side="left")

    ctk.CTkLabel(scroll, text="EDL(9008) / BROM", font=F_SECTION,
           text_color=T.ERR).pack(padx=12, anchor="w", pady=(10,2))
    row_edl = ctk.CTkFrame(scroll, fg_color="transparent")
    row_edl.pack(fill="x", padx=12)
    ctk.CTkButton(row_edl, text="💠 EDL 使用指引",
      command=lambda: self._call_ext("edl_qfil_hint"),
      height=34, font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.ERR, corner_radius=6, border_width=1,
      border_color="#4A1E28").pack(side="left", expand=True, fill="x", padx=(0,4))
    ctk.CTkButton(row_edl, text="🧩 BROM 使用指引",
      command=lambda: self._call_ext("brom_spflash_hint"),
      height=34, font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.ERR, corner_radius=6, border_width=1,
      border_color="#4A1E28").pack(side="left", expand=True, fill="x", padx=(4,0))

    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)
    ctk.CTkLabel(scroll, text="▸ 高级工具", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(6,2))
    tools_row = ctk.CTkFrame(scroll, fg_color="transparent")
    tools_row.pack(fill="x", padx=12)
    for txt, fn in [
      ("🔐 校验文件", lambda: self._hash_dialog()),
      ("🧠 镜像信息", lambda: self._magic_dialog()),
      ("🧹 清理临时", lambda: self._call_ext("cleanup_temp")),
      ("📊 分析日志", lambda: self._call_ext("analyze_log", self.debug_path)),
    ]:
      ctk.CTkButton(tools_row, text=txt, command=fn, height=34,
        font=F_TINY, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
        text_color=T.ACCENT, corner_radius=6, border_width=1,
        border_color=T.BORDER).pack(side="left", expand=True, fill="x",
                       padx=(0,4))
    ctk.CTkFrame(self.mid_container, height=20, fg_color="transparent").pack()


  # ================= 系统工具页 =================
  def _page_systools(self):
    ctk.CTkLabel(self.mid_container, text="🛠 SYS TOOLS", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="系统工具", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="网络 / 分区 / 属性 / SELinux / 日志",
           font=F_TINY, text_color=T.TEXT_DIM).pack(padx=20, anchor="w", pady=(2,0))
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    if HAS_PLUS:
      self._render_plus_group(self.mid_container, "🌐 网络诊断")
      self._render_plus_group(self.mid_container, "⚙ 系统工具")
      self._render_plus_group(self.mid_container, "📜 日志大师")
    else:
      ctk.CTkLabel(self.mid_container, text="⚠ huijui_plus.py 未加载",
             font=F_SUB_11, text_color=T.ERR).pack(pady=40)

  # ================= 应用管理页 =================
  def _page_apps(self):
    ctk.CTkLabel(self.mid_container, text="📦 APPS", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="应用管理", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="批量安装 / 卸载 / 冻结 / 去全家桶",
           font=F_TINY, text_color=T.TEXT_DIM).pack(padx=20, anchor="w", pady=(2,0))
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    if HAS_PLUS:
      self._render_plus_group(self.mid_container, "📦 应用管理")
    else:
      ctk.CTkLabel(self.mid_container, text="⚠ huijui_plus.py 未加载",
             font=F_SUB_11, text_color=T.ERR).pack(pady=40)

  def _render_plus_group(self, parent, group_title):
    if not HAS_PLUS: return
    if not getattr(self, "_plus_tools", None):
      self._plus_tools = PlusTools(self.adb, self.fb, self.runner,
                     self.log, self.current_dir, self)
    color_map = {"ok": T.OK, "err": T.ERR, "warn": T.WARN, "info": T.INFO}
    for title, items in PLUS_GROUPS:
      if title != group_title: continue
      ctk.CTkFrame(parent, height=1, fg_color=T.BORDER).pack(
        fill="x", padx=20, pady=(14,8))
      ctk.CTkLabel(parent, text=group_title, font=F_SECTION,
             text_color=T.ACCENT).pack(padx=20, anchor="w", pady=(4,6))
      for action, name, desc, kind in items:
        row = ctk.CTkFrame(parent, fg_color=T.BG_CARD, corner_radius=8,
                  border_width=1, border_color=T.BORDER)
        row.pack(fill="x", padx=20, pady=3)
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=12, pady=8)
        ctk.CTkLabel(left, text=name, font=F_BTN_S,
               text_color=T.TEXT_MAIN, anchor="w").pack(anchor="w")
        ctk.CTkLabel(left, text=desc, font=F_TINY,
               text_color=T.TEXT_DIM, anchor="w").pack(anchor="w")
        c = color_map.get(kind, T.INFO)
        ctk.CTkButton(row, text="执行", width=70, height=32,
          font=F_BTN_S, fg_color=c, hover_color=c,
          text_color=T.ON_ACCENT, corner_radius=6,
          command=lambda a=action: self._plus_tools.dispatch(a)
        ).pack(side="right", padx=12)

  # ================= 刷机历史页 =================
  def _page_history(self):
    ctk.CTkLabel(self.mid_container, text="📜 HISTORY", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="刷机历史", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    scroll = self.mid_container
    rows = self.history.all(200)
    if not rows:
      ctk.CTkLabel(scroll, text="暂无刷机记录",
             font=F_SUB_11, text_color=T.TEXT_MUTED).pack(pady=40)
    else:
      for ts, brand, model, zp, dur, ok in rows:
        card = ctk.CTkFrame(scroll, fg_color=T.BG_CARD, corner_radius=8,
                   border_width=1, border_color=T.BORDER)
        card.pack(fill="x", padx=8, pady=3)
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        ctk.CTkLabel(left, text=f"{brand} {model}",
               font=F_VAL, text_color=T.TEXT_MAIN,
               anchor="w").pack(anchor="w")
        ctk.CTkLabel(left, text=f"{ts[:19]} · {zp}",
               font=F_TINY, text_color=T.TEXT_DIM,
               anchor="w").pack(anchor="w")
        ctk.CTkLabel(card, text="✔" if ok else "✘",
               font=("Segoe UI", 20, "bold"),
               text_color=T.OK if ok else T.ERR).pack(side="right",
                                  padx=14)
    ctk.CTkButton(self.mid_container, text="🗑 清空历史",
      command=self._clear_history, height=38, font=F_BTN_S,
      fg_color="#2A1418", hover_color="#5A1E28", text_color="#FF8899",
      corner_radius=8, border_width=1,
      border_color="#4A1E28").pack(pady=(10,20), padx=20, fill="x")

  def _clear_history(self):
    if not messagebox.askyesno("清空历史", "确定清空所有刷机记录？"): return
    self.history.clear()
    self.log("✅ 刷机历史已清空", "ok")
    self._switch_tab("device")
    self.after(50, lambda: self._switch_tab("history"))

  # ================= 教程 / 设置 / 关于 =================
  def _page_tutorial(self):
    ctk.CTkLabel(self.mid_container, text="📖 TUTORIAL", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="使用教程", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    box = ctk.CTkTextbox(self.mid_container, font=F_SUB_11,
      fg_color=T.BG_DEEP, text_color=T.TEXT_MAIN, corner_radius=8,
      wrap="word", border_width=1, border_color=T.BORDER)
    box.pack(fill="both", expand=True, padx=20, pady=(0,20))
    box.insert("1.0", TUTORIAL_TEXT); box.configure(state="disabled")

  def _page_settings(self):
    ctk.CTkLabel(self.mid_container, text="⚙ SETTINGS", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="设置", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    scroll = self.mid_container

    def switch(label, key, default=False):
      row = ctk.CTkFrame(scroll, fg_color="transparent")
      row.pack(fill="x", padx=12, pady=6)
      ctk.CTkLabel(row, text=label, font=F_SUB_11,
             text_color=T.TEXT_MAIN, anchor="w").pack(side="left")
      var = ctk.BooleanVar(value=bool(cfg(key) if cfg(key) is not None else default))
      def on_change(k=key, v=var):
        cfg(k, bool(v.get()))
      ctk.CTkSwitch(row, text="", variable=var, command=on_change,
              fg_color=T.BORDER_LIGHT, progress_color=T.ACCENT,
              button_color=T.BG_PANEL,
              button_hover_color=T.ACCENT_HOVER,
              text_color=T.TEXT_MAIN).pack(side="right")

    ctk.CTkLabel(scroll, text="▸ 刷机行为", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(8,4))
    switch("刷机后跳过清空数据", "skip_wipe", False)
    switch("自动禁用 verity", "disable_verity", True)
    switch("刷机前自动备份分区", "auto_backup", True)
    switch("完成后自动修补 Root", "auto_root_patch", True)

    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    ctk.CTkLabel(scroll, text="▸ 防呆检查", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(8,4))
    switch("危险分区二次确认", "confirm_dangerous", True)
    switch("固件机型交叉校验", "check_firmware_match", True)
    switch("多设备冲突检测", "check_multi_device", True)

    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    ctk.CTkLabel(scroll, text="▸ 界面", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(8,4))
    switch("日志自动滚动", "log_autoscroll", True)

    row = ctk.CTkFrame(scroll, fg_color="transparent")
    row.pack(fill="x", padx=12, pady=6)
    ctk.CTkLabel(row, text="当前主题", font=F_SUB_11,
           text_color=T.TEXT_MAIN).pack(side="left")
    self.theme_var = ctk.StringVar(value=cfg("theme") or "dark")
    ctk.CTkOptionMenu(row, values=["dark","light"], variable=self.theme_var,
              command=self._on_theme_change, width=110,
              fg_color=T.BG_CARD, button_color=T.ACCENT,
              button_hover_color=T.ACCENT_HOVER,
              text_color=T.TEXT_MAIN,
              dropdown_fg_color=T.BG_CARD,
              dropdown_text_color=T.TEXT_MAIN).pack(side="right")

    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    ctk.CTkLabel(scroll, text="▸ 危险分区黑名单（额外）", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(8,4))
    ctk.CTkLabel(scroll, text="逗号分隔，如：cache,persist,userdata",
           font=F_TINY, text_color=T.TEXT_DIM).pack(padx=12, anchor="w")
    self.danger_entry = ctk.CTkEntry(scroll, font=F_LOG, fg_color=T.BG_DEEP,
      border_color=T.BORDER, text_color=T.TEXT_MAIN, height=36,
      corner_radius=8)
    self.danger_entry.pack(fill="x", padx=12, pady=(6,6))
    try: self.danger_entry.insert(0, ",".join(cfg("dangerous_extra") or []))
    except Exception: pass
    def save_danger():
      txt = self.danger_entry.get().strip()
      lst = [x.strip().lower() for x in txt.split(",") if x.strip()]
      cfg("dangerous_extra", lst)
      self.log(f"✅ 危险分区黑名单已保存（{len(lst)} 项）", "ok")
      Toast(self, "已保存", kind="ok")
    ctk.CTkButton(scroll, text="保存黑名单", command=save_danger,
      height=36, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.WARN, corner_radius=8, border_width=1,
      border_color="#4A2C00").pack(fill="x", padx=12, pady=(0,14))

    ctk.CTkFrame(scroll, height=1, fg_color=T.BORDER).pack(fill="x", padx=12, pady=14)

    ctk.CTkLabel(scroll, text="▸ 其他", font=F_SECTION,
           text_color=T.ACCENT).pack(padx=12, anchor="w", pady=(8,4))
    ctk.CTkButton(scroll, text="📂 打开程序目录",
      command=lambda: os.startfile(self.current_dir),
      height=38, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.TEXT_MAIN, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(fill="x", padx=12, pady=4)
    ctk.CTkButton(scroll, text="🔄 重置所有设置", command=self._reset_settings,
      height=38, font=F_BTN_S, fg_color="#2A1418", hover_color="#5A1E28",
      text_color="#FF8899", corner_radius=8, border_width=1,
      border_color="#4A1E28").pack(fill="x", padx=12, pady=(4,20))

    if HAS_PLUS:
      self._render_plus_group(self.mid_container, "🎨 美化")

  def _page_about(self):
    ctk.CTkLabel(self.mid_container, text="ℹ ABOUT", font=F_SECTION,
           text_color=T.ACCENT).pack(pady=(24,4), padx=20, anchor="w")
    ctk.CTkLabel(self.mid_container, text="关于", font=F_SECTION_CN,
           text_color=T.TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(self.mid_container, height=1, fg_color=T.BORDER).pack(
      fill="x", padx=20, pady=14)
    box = ctk.CTkTextbox(self.mid_container, font=F_SUB_11,
      fg_color=T.BG_DEEP, text_color=T.TEXT_MAIN, corner_radius=8,
      wrap="word", border_width=1, border_color=T.BORDER)
    box.pack(fill="both", expand=True, padx=20, pady=(0,12))
    info = f"""{APP_NAME} {APP_VERSION} · {APP_EDITION}
=========================================

作者   : 喜羊羊灰灰菜單
酷安主页 : {COOLAPK}
发布平台 : 酷安 (CoolAPK)

运行时  : Python {platform.python_version()}
系统   : {platform.system()} {platform.release()}
管理员  : {"是" if self._admin else "否"}

--- 开发历程 ---
v1.0 纯 HTML 整活
v1.1 动态分区识别
v2.2 payload 解包
v2.8 Cyber Edition
v4.2 Nebula Edition
v5.1 Pro Edition ← 当前

--- Pro 新特性 ---
· 双主题（暗黑/亮色）· 实时切换
· 侧边栏折叠 / 全局搜索 Ctrl+K
· 多品牌适配（含 vivo/华为/荣耀）
· 危险分区二次确认 / 电量温度拦截
· 固件机型交叉校验（防刷错包变砖）
· 刷机历史记录（SQLite）
· ADB 无线连接 / 屏幕录制
· 日志环形缓冲 / 智能过滤

--- 免责声明 ---
本工具仅供技术学习交流使用。
刷机有风险，操作需谨慎。
因使用本工具导致的任何设备损坏，
作者概不负责。

=========================================
    by 喜羊羊灰灰菜單 · 2026
"""
    box.insert("1.0", info); box.configure(state="disabled")
    row = ctk.CTkFrame(self.mid_container, fg_color="transparent")
    row.pack(fill="x", padx=20, pady=(0,20))
    ctk.CTkButton(row, text="🌐 酷安主页",
      command=lambda: webbrowser.open(COOLAPK),
      height=40, font=F_BTN_S, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
      text_color=T.ON_ACCENT, corner_radius=8).pack(side="left", expand=True,
                              fill="x", padx=(0,4))
    ctk.CTkButton(row, text="📄 查看日志", command=self.open_log_dir,
      height=40, font=F_BTN_S, fg_color=T.BG_CARD, hover_color=T.BG_HOVER,
      text_color=T.TEXT_MAIN, corner_radius=8, border_width=1,
      border_color=T.BORDER_LIGHT).pack(side="left", expand=True, fill="x",
                        padx=(4,0))

  # ================= 主题切换（修复：实时重建）=================
  def _toggle_theme(self):
    cur = cfg("theme") or "dark"
    new = "light" if cur == "dark" else "dark"
    cfg("theme", new)
    # 同步清掉背景方案，避免 bg_scheme 覆盖主题
    cfg("bg_scheme", "default")
    T.__dict__["_bg_override"] = {}
    T.set(new)
    self._apply_theme_change()

  def _on_theme_change(self, val):
    cfg("theme", val)
    cfg("bg_scheme", "default")
    T.__dict__["_bg_override"] = {}
    T.set(val)
    self._apply_theme_change()

  def _apply_theme_change(self):
    if self.is_running:
      Toast(self, "主题已保存，刷机结束后生效",
         kind="info", duration=3000)
      return
    self._rebuild_ui()
    Toast(self, f"主题已切换：{cfg('theme')}",
       kind="ok", duration=1500)

  def _rebuild_ui(self):
    try:
      state = {
        "current_tab": self.current_tab,
        "device_brand": self._device_brand,
        "device_mode": self._device_mode,
        "device_serial": self._device_serial,
        "plus": getattr(self, "_plus_tools", None),
      }
      for w in list(self.winfo_children()):
        try: w.destroy()
        except Exception: pass
      # 清空 CTk 残留回调，防止 TclError 污染后续 widget 创建
      try:
        self.update_idletasks()
      except Exception: pass
      try:
        self.update()
      except Exception: pass
      self.configure(fg_color=T.BG_DEEP)
      self._nav_btns = {}; self._nav_labels = {}
      self.current_tab = None
      self._build_ui()
      self._log_count = 0
      # _build_ui 内部已调用 _welcome()，此处不再重复
      if state["current_tab"]:
        self._switch_tab(state["current_tab"])
      # 延迟二次刷新，清掉 CTk 内部重绘缓存
      self.after(80, self._force_redraw)
      self.after(250, self._force_redraw)
      self.log("🎨 主题已实时切换", "ok")
    except Exception as e:
      self.log(f"✗ 重建失败: {e}", "err")
      traceback.print_exc()

  def _force_redraw(self):
    try:
      if hasattr(self, "_footer_bar") and alive(self._footer_bar):
        try: self._footer_bar.configure(bg=T.BG_PANEL)
        except Exception: pass
        for c in self._footer_bar.winfo_children():
          try: c.configure(bg=T.BG_PANEL)
          except Exception: pass
      self.update_idletasks()
      self.update()
    except Exception:
      pass

  def _reset_settings(self):
    if not messagebox.askyesno("重置设置", "确定恢复所有设置为默认值？"): return
    CFG.reset()
    self.log("✅ 设置已重置，重启程序生效", "ok")
    Toast(self, "设置已重置", kind="ok")

  # ================= 日志（修复：环形缓冲）=================
  def _welcome(self):
    self._log_plain("━" * 46, "neon")
    self._log_plain(f"  {APP_NAME} · {APP_VERSION} {APP_EDITION}", "neon")
    self._log_plain("  by 喜羊羊灰灰菜單", "dim")
    self._log_plain("━" * 46, "neon")
    self._log_plain("")
    self._log_plain("👋 欢迎使用 Huijui 工具箱 Pro", "white")
    self._log_plain("")
    self._log_plain("🆕 v5.1 Pro 新特性：", "magenta")
    self._log_plain("  · 双主题实时切换 · 侧栏折叠 · 全局搜索", "dim")
    self._log_plain("  · 危险分区二次确认 / 电量温度拦截", "dim")
    self._log_plain("  · 固件机型交叉校验（防刷错包）", "dim")
    self._log_plain("  · 刷机历史（SQLite）· ADB 无线/录屏", "dim")
    self._log_plain("  · 多品牌适配（含 vivo/华为/荣耀）", "dim")
    self._log_plain("")

  def _log_plain(self, msg, tag=None):
    if not alive(self.log_box): return
    try:
      self.log_box.insert("end", msg + "\n", tag or ())
      self.log_box.see("end")
      self._log_count += 1
    except Exception: pass

  def log(self, msg, tag=None):
    self.log_q.put(("ts", msg, tag))
    self._toast_history.append((time.strftime("%H:%M:%S"), msg, tag))

  def _poll_log(self):
    if not alive(self): return
    try:
      batch = []
      while True:
        try: batch.append(self.log_q.get_nowait())
        except queue.Empty: break
      if batch and alive(self.log_box):
        ts = time.strftime("%H:%M:%S")
        autoscroll = bool(cfg("log_autoscroll"))
        for kind, msg, tag in batch:
          try:
            self.log_box.insert("end", f"[{ts}] ", "muted")
            self.log_box.insert("end", msg + "\n", tag or ())
            self._log_count += 1
          except Exception: pass
        if self._log_count > LOG_MAX_LINES:
          try:
            excess = self._log_count - LOG_MAX_LINES
            self.log_box.delete("1.0", f"{excess + 1}.0")
            self._log_count = LOG_MAX_LINES
          except Exception: pass
        try:
          if autoscroll: self.log_box.see("end")
          self.log_count.configure(text=f"{self._log_count} 行")
        except Exception: pass
    except Exception: pass
    self.after(60, self._poll_log)

  def _tick_clock(self):
    if not alive(self): return
    try: self.clock.configure(text=time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception: return
    self.after(1000, self._tick_clock)

  def clear_log(self):
    if not alive(self.log_box): return
    try:
      self.log_box.delete("1.0", "end"); self._log_count = 0
      self.log_count.configure(text="0 行")
    except Exception: pass

  def export_log(self):
    try:
      ts = datetime.now().strftime("%Y%m%d_%H%M%S")
      save_to = os.path.join(self.current_dir, f"huijui_log_{ts}.txt")
      content = self.log_box.get("1.0", "end")
      with open(save_to, "w", encoding="utf-8") as f:
        f.write(f"Huijui Toolbox Log · {datetime.now()}\n")
        f.write("=" * 60 + "\n"); f.write(content)
      self.log(f"✅ 日志已导出：{os.path.basename(save_to)}", "ok")
      Toast(self, f"日志已导出\n{os.path.basename(save_to)}", kind="ok")
    except Exception as e:
      self.log(f"✗ 导出失败: {e}", "err")

  def open_log_dir(self):
    try: os.startfile(self.current_dir)
    except Exception: pass

  # ================= 状态 / 进度 =================
  def _set_status(self, text, color):
    try:
      self.status_dot.set_color(color)
      self.status_label.configure(text=text, text_color=color)
      if color == T.OK:
        bg, bd = "#0A1F14", "#14402A"
      elif color == T.WARN:
        bg, bd = "#2B2010", "#4D3A15"
      elif color == T.ERR:
        bg, bd = "#2B0E14", "#4D1A26"
      else:
        bg, bd = "#0A1F14", "#14402A"
      self.status_pill.configure(fg_color=bg, border_color=bd)
      if alive(self.topbar_border):
        self.topbar_border.configure(fg_color=bd)
    except Exception: pass

  def _set_progress(self, v):
    self._flash_progress = v
    try: self.ring.set(v)
    except Exception: pass

  # ================= 设备扫描（修复：并发锁）=================
  def _scan_device(self):
    if self._is_scanning: return
    self._is_scanning = True
    threading.Thread(target=self._scan_device_thread, daemon=True).start()

  def _scan_device_thread(self):
    # v5.1 Pro：若扩展可用，走全模式检测
    if HAS_EXT and getattr(self, "ext", None) is not None:
      self._scan_device_thread_ext()
      return
    try:
      self.log("🔍 正在扫描设备...", "info")
      fb_out = self.runner.run_quiet(f"{self.fb} devices")
      if fb_out and "fastboot" in fb_out.lower():
        dev = fb_out.split()[0]
        is_fbd = "yes" in self.runner.run_quiet(
          f"{self.fb} getvar is-userspace 2>&1").lower()
        mode_str = "Fastbootd" if is_fbd else "Fastboot"
        self._device_mode = mode_str; self._device_serial = dev
        self.log(f" ✓ 已连接（{mode_str} 模式）: {dev}", "ok")
        self.ui(self._set_status, f"{mode_str} 模式", T.INFO)
        self.ui(self._update_info, "mode", mode_str)
        self.ui(self._update_info, "serial", dev)
        return
      devs = self.runner.run_quiet(f"{self.adb} devices")
      dev = None; state = ""
      for ln in devs.splitlines()[1:]:
        parts = ln.split()
        if len(parts) >= 2: dev, state = parts[0], parts[1]; break
      if not dev:
        self.log(" ✗ 未检测到 ADB 设备", "err")
        self.ui(self._set_status, "设备未连接", T.ERR); return
      if state == "unauthorized":
        self.log(" ⚠ 请在手机上点击「允许 USB 调试」", "warn")
        self.ui(self._set_status, "等待授权", T.WARN); return
      if state != "device":
        self.log(f" ✗ 设备状态异常: {state}", "err")
        self.ui(self._set_status, "设备异常", T.ERR); return
      self._device_mode = "ADB"; self._device_serial = dev
      self.log(f" ✓ 已连接（ADB 模式）: {dev}", "ok")
      self.ui(self._set_status, "设备已连接", T.OK)
      get = lambda p: self.runner.run_quiet(f"{self.adb} shell getprop {p}")
      brand = get("ro.product.brand"); model = get("ro.product.model")
      ver = get("ro.build.version.release"); sdk = get("ro.build.version.sdk")
      boot = get("ro.boot.verifiedbootstate")
      bl = "已解锁" if boot in ("orange","yellow") else "未解锁/未知"
      slot = get("ro.boot.slot_suffix") or "_a"
      self._device_brand = brand; self._device_model = model
      self.log(f" 📱 {brand} {model}", "info")
      self.log(f" 🤖 Android {ver} (API {sdk})", "info")
      self.log(f" 🔓 BL: {bl}", "info")
      self.log(f" 🏷 品牌识别: {get_brand_display(detect_brand(brand))}", "purple")
      self.log(f" 🔀 槽位: {slot}", "info")
      ok, msg = self.device_guard.check_battery(dev)
      self.log(f" {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
      ok, msg = self.device_guard.check_temperature(dev)
      self.log(f" {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
      root_ok = "uid=0" in self.runner.run_quiet(f"{self.adb} shell su -c id")
      ksu_ok = bool(self.root_patcher.find_ksud())
      self.ui(self._update_info, "brand", brand)
      self.ui(self._update_info, "model", model)
      self.ui(self._update_info, "android", "Android " + ver)
      self.ui(self._update_info, "sdk", "API " + sdk)
      self.ui(self._update_info, "bl", bl)
      self.ui(self._update_info, "root", "已激活" if root_ok else "未激活")
      self.ui(self._update_info, "ksu", "已安装" if ksu_ok else "未安装")
      self.ui(self._update_info, "mode", "ADB")
      self.ui(self._update_info, "serial", dev)
      self.ui(self._update_info, "slot", slot)
    except Exception as e:
      self.log(f"✗ 扫描异常: {e}", "err")
    finally:
      self._is_scanning = False

  def _update_info(self, key, value):
    if hasattr(self, 'info') and key in self.info:
      color = T.ACCENT
      if key == "root":
        color = T.OK if value == "已激活" else T.WARN
      elif key == "ksu":
        color = T.VIOLET if value == "已安装" else T.WARN
      elif key == "bl":
        color = T.OK if value == "已解锁" else T.WARN
      try: self.info[key].configure(text=value, text_color=color)
      except Exception: pass

  def _copy_device_info(self):
    try:
      lines = [f"{k}: {w.cget('text')}" for k, w in self.info.items()]
      self.clipboard_clear(); self.clipboard_append("\n".join(lines))
      self.log("✅ 设备信息已复制到剪贴板", "ok")
      Toast(self, "已复制到剪贴板", kind="ok")
    except Exception as e:
      self.log(f"✗ 复制失败: {e}", "err")

  def _check_bl_action(self):
    def run():
      self.log("🔓 正在检测 BL 锁...", "info")
      try:
        for key in ("is-unlocked","unlocked"):
          r = self.runner.run_quiet(f"{self.fb} getvar {key} 2>&1").lower()
          if "yes" in r:
            self.log(" ✓ BL 已解锁", "ok")
            self.ui(self._update_info, "bl", "已解锁")
            Toast(self, "BL 已解锁", kind="ok"); return
          if "no" in r:
            self.log(" ⛔ BL 未解锁", "err")
            self.ui(self._update_info, "bl", "未解锁")
            Toast(self, "BL 未解锁", kind="err"); return
        r = self.runner.run_quiet(f"{self.fb} oem device-info 2>&1")
        if "Device unlocked: true" in r:
          self.log(" ✓ BL 已解锁", "ok")
          self.ui(self._update_info, "bl", "已解锁")
          Toast(self, "BL 已解锁", kind="ok")
        elif "Device unlocked: false" in r:
          self.log(" ⛔ BL 未解锁", "err")
          self.ui(self._update_info, "bl", "未解锁")
          Toast(self, "BL 未解锁", kind="err")
        else:
          self.log(" ⚠ 无法确认 BL 状态", "warn")
          Toast(self, "无法确认 BL 状态", kind="warn")
      except Exception as e:
        self.log(f" ✗ 检测异常: {e}", "err")
    threading.Thread(target=run, daemon=True).start()

  # ================= 卡刷包扫描 =================
  def _scan_zip(self):
    try:
      zips = [f for f in os.listdir(self.current_dir) if f.lower().endswith(".zip")]
    except Exception: zips = []
    if zips:
      try:
        mb = os.path.getsize(os.path.join(self.current_dir, zips[0]))/1024/1024
        self.log(f"📦 检测到卡刷包: {zips[0]}（{mb:.0f} MB）", "info")
      except Exception:
        self.log(f"📦 检测到卡刷包: {zips[0]}", "info")
    else:
      self.log(f"📁 未检测到卡刷包，请放到: {self.current_dir}", "warn")
      self.log("  放入后点击「一键刷机」即可开始", "dim")
    if self.root_patcher.find_ksud():
      self.log("🔧 检测到 ksud.exe，将支持自动修补 Root", "purple")
    else:
      self.log("💡 未找到 ksud.exe，Root 修补需手动操作", "dim")
    if not self._admin:
      self.log("⚠ 未以管理员运行，Fastboot 可能失败", "warn")

  # ================= 刷机流程 =================
  def start(self):
    if self.is_running: return
    if not self._admin:
      if not messagebox.askyesno("警告",
        "未以管理员身份运行，Fastboot 刷机可能失败。\n"
        "建议用左侧「🛡 以管理员重启」。\n\n仍要继续吗？"):
        return
    if cfg("check_multi_device"):
      ok, msg = self.device_guard.check_multi_device()
      if not ok:
        messagebox.showerror("多设备冲突", msg); return
    ok, free = self.guard.check_disk(self.current_dir, min_gb=20)
    if not ok and free > 0:
      if not messagebox.askyesno("磁盘空间不足",
        f"仅剩 {free:.1f} GB，刷机可能失败。\n仍要继续吗？"): return
    self.is_running = True; self.success_flag = False
    self.runner.stop_flag = False
    self._flash_start_time = time.time()
    self._flash_zip_name = ""
    try: self.btn_start.configure(state="disabled", text="刷机中...")
    except Exception: pass
    try: self.btn_stop.configure(state="normal")
    except Exception: pass
    self.ui(self._set_status, "RUNNING", T.WARN)
    self.ui(self.status_dot.set_active, True)
    self.ui(self.ring.set_running, True)
    self.clear_log()
    self.ui(self.set_step, -1)
    try: self.step_text.configure(text="准备中...", text_color=T.TEXT_DIM)
    except Exception: pass
    self.runner.clear_debug()
    threading.Thread(target=self.flow, daemon=True).start()

  def stop(self):
    if not self.is_running: return
    self.runner.stop_flag = True
    self.log("⛔ 正在中止...（等待当前命令结束）", "err")
    try:
      self.btn_stop.configure(state="disabled", text="中止中...")
    except Exception: pass

  def finish(self):
    self.is_running = False
    self.ui(self.status_dot.set_active, False)
    self.ui(self.ring.set_running, False)
    self.ui(self.btn_start.configure, state="normal", text="▶ 一键刷机")
    self.ui(self.btn_stop.configure, state="disabled", text="⏹ 中止")
    # 写入历史
    try:
      dur = int(time.time() - getattr(self, "_flash_start_time", time.time()))
      self.history.add(self._device_brand or "?",
               self._device_model or "?",
               getattr(self, "_flash_zip_name", "?"),
               dur, self.success_flag and not self.runner.stop_flag)
    except Exception: pass
    if self.runner.stop_flag:
      self.ui(self._set_status, "STOPPED", T.ERR)
      self.ui(self.step_text.configure, text="已中止", text_color=T.ERR)
    elif self.success_flag:
      self.ui(self._set_status, "COMPLETE", T.OK)
      self.ui(self.step_text.configure, text="刷机完成", text_color=T.OK)
      Toast(self, "🎉 刷机成功完成", kind="ok", duration=4000)
    else:
      self.ui(self._set_status, "INCOMPLETE", T.WARN)
      self.ui(self.step_text.configure, text="未完成", text_color=T.WARN)
      Toast(self, "刷机未完成，请查看日志", kind="warn", duration=4000)

  def _run_step(self, cmd, hint, timeout=600, cwd=None, on_line=None):
    def beat(sec):
      m, s = divmod(sec, 60)
      self.log(f" ⏳ 已运行 {m}m{s}s" if m > 0 else f" ⏳ 已运行 {sec}s", "dim")
    ret, errs = self.runner.run(cmd, timeout=timeout, cwd=cwd,
                  on_tick=beat, on_line=on_line)
    return ret == 0, errs

  def _show_errors(self, errs, hint):
    if not errs: return
    self.log(f" ✗ {hint}失败，关键错误：", "err")
    for e in errs[:5]: self.log(f"   · {e}", "err")
    full = " ".join(errs); suggestions = []
    for pattern, advice in ERROR_DIAGNOSTICS:
      if re.search(pattern, full, re.I): suggestions.append(advice)
    if suggestions:
      self.log(" 💡 智能诊断建议：", "purple")
      for s in suggestions[:3]: self.log(f"   → {s}", "purple")
    self.log(f" 💡 完整日志见 CONSOLE 或 {os.path.basename(self.debug_path)}", "warn")

  def set_step(self, i):
    self._flash_step_index = i
    if not hasattr(self, 'steps'): return
    for idx, s in enumerate(self.steps):
      if idx < i: s.set_state("done")
      elif idx == i:
        s.set_state("active")
        try: self.step_text.configure(text=STEPS[idx], text_color=T.ACCENT)
        except Exception: pass
      else: s.set_state("idle")

  def flow(self):
    try:
      self.ui(self.set_step, 0); self.ui(self._set_progress, STEP_PROGRESS[0])
      if not self.step_env(): return
      self.ui(self.set_step, 1); self.ui(self._set_progress, STEP_PROGRESS[1])
      mode, dev = self.step_detect()
      if not mode: return
      self.ui(self.set_step, 2); self.ui(self._set_progress, STEP_PROGRESS[2])
      if mode == "ADB":
        if not self.step_info(): return
        # 防呆：电量/温度
        ok, msg = self.device_guard.check_battery(dev)
        self.log(f" {'✓' if ok else '⛔'} {msg}", "ok" if ok else "err")
        if not ok:
          self.log(" ⛔ 电量不足，刷机中止", "err"); return
        ok, msg = self.device_guard.check_temperature(dev)
        self.log(f" {'✓' if ok else '⛔'} {msg}", "ok" if ok else "err")
        if not ok:
          self.log(" ⛔ 温度过高，刷机中止", "err"); return
        brand_key = detect_brand(self._device_brand)
        self.log(f" 🏷 品牌识别: {get_brand_display(brand_key)}", "purple")
      if mode == "ADB" and dev and cfg("auto_backup"):
        self._auto_backup(dev)
      self.ui(self.set_step, 3); self.ui(self._set_progress, STEP_PROGRESS[3])
      zf = self.step_find_zip()
      if not zf: return
      self._flash_zip_name = os.path.basename(zf)
      self.ui(self.set_step, 4); self.ui(self._set_progress, STEP_PROGRESS[4])
      if not self.step_extract(zf): return
      self.ui(self.set_step, 5); self.ui(self._set_progress, STEP_PROGRESS[5])
      if not self.step_unpack(): return
      self.ui(self.set_step, 6); self.ui(self._set_progress, STEP_PROGRESS[6])
      if not self.step_enter_fb(mode, dev): return
      self.ui(self.set_step, 7)
      if not self.step_flash_physical(): return
      self.ui(self.set_step, 8); self.ui(self._set_progress, 0.78)
      if not self.step_enter_fbd(): return
      self.ui(self.set_step, 9); self.ui(self._set_progress, 0.80)
      if not self.step_flash_logical(): return
      self.ui(self._set_progress, 0.95)
      self.step_wipe()
      self.ui(self._set_progress, 1.0)
      self.success_flag = True
      self.log(""); self.log("🎉 ══ 刷机成功 ══ 🎉", "ok")
      self.log("首次开机需 10-15 分钟，请勿强制关机", "warn")
      if cfg("auto_root_patch"): self._auto_patch_root()
    except Exception as e:
      self.log(f"✗ 程序异常: {e}", "err")
      self.runner.append_debug(f"[EXCEPTION] {traceback.format_exc()}")
    finally:
      self.finish()

  def _auto_backup(self, dev):
    self.log("▸ 附加：刷机前自动备份关键分区", "purple")
    bdir = self.backup_mgr.create_backup_dir()
    if not bdir:
      self.log(" ⚠ 无法创建备份目录，跳过", "warn"); return
    for part in ["boot","init_boot"]:
      if self.runner.stop_flag: return
      self.backup_mgr.backup_partition(self.adb, dev, part, bdir,
        lambda m, t=None: self.log(m, t))

  def _auto_patch_root(self):
    self.log(""); self.log("▸ 附加：尝试自动修补 Root", "purple")
    init_boot = self.root_patcher.find_init_boot()
    if not init_boot:
      self.log(" ⚠ 未找到原厂 init_boot.img，跳过", "warn"); return
    out = self.root_patcher.patch(init_boot, lambda m, t=None: self.log(m, t))
    if out:
      self.log(" 💡 修补完成，在 Fastboot 模式手动刷入：", "info")
      self.log(f'   fastboot flash init_boot "{os.path.basename(out)}"', "dim")

  def step_env(self):
    self.log("▸ 步骤 1/10：检查运行环境", "neon")
    ok = True
    for name, label in [("adb.exe","ADB 工具"),
               ("fastboot.exe","Fastboot 工具"),
               ("payload-dumper-go.exe","解包工具")]:
      p1 = get_resource_path(name); p2 = get_resource_path(f"tools/{name}")
      if os.path.exists(p1) or os.path.exists(p2):
        self.log(f" ✓ {label} 已就绪", "ok")
      else:
        self.log(f" ✗ 缺少 {label}（{name}）", "err"); ok = False
    try:
      free_gb = shutil.disk_usage(self.current_dir).free / 1024**3
      if free_gb < 20:
        self.log(f" ⚠ 磁盘剩余 {free_gb:.1f} GB，建议 20GB+", "warn")
      else:
        self.log(f" ✓ 磁盘剩余 {free_gb:.1f} GB", "ok")
    except Exception: pass
    try:
      zips = [f for f in os.listdir(self.current_dir) if f.lower().endswith(".zip")]
      if zips: self.log(f" ✓ 检测到 {len(zips)} 个卡刷包", "ok")
      else: self.log(" ⚠ 未检测到卡刷包", "warn")
    except Exception: pass
    return ok

  def step_detect(self):
    self.log("▸ 步骤 2/10：检测手机连接", "neon")
    out = self.runner.run_quiet(f"{self.fb} devices")
    if out and "fastboot" in out.lower():
      dev = out.split()[0]
      is_fbd = "yes" in self.runner.run_quiet(
        f"{self.fb} getvar is-userspace 2>&1").lower()
      mode_str = "Fastbootd" if is_fbd else "Fastboot"
      self.log(f" ✓ 已连接（{mode_str} 模式）", "ok")
      self.ui(self._update_info, "mode", mode_str)
      return "FASTBOOT", dev
    for _ in range(6):
      if self.runner.stop_flag: return None, None
      out = self.runner.run_quiet(f"{self.adb} devices")
      for ln in out.splitlines()[1:]:
        if "\tdevice" in ln:
          dev = ln.split()[0]
          self.log(" ✓ 已连接（ADB 模式）", "ok")
          self.ui(self._update_info, "mode", "ADB")
          return "ADB", dev
        elif "unauthorized" in ln:
          self.log(" ⚠ 请在手机上点击「允许 USB 调试」", "warn")
      time.sleep(0.5)
    self.log(" ✗ 未检测到手机", "err")
    return None, None

  def step_info(self):
    if self.runner.stop_flag: return False
    self.log("▸ 步骤 3/10：读取设备信息", "neon")
    get = lambda p: self.runner.run_quiet(f"{self.adb} shell getprop {p}")
    brand = get("ro.product.brand"); model = get("ro.product.model")
    ver = get("ro.build.version.release"); sdk = get("ro.build.version.sdk")
    boot = get("ro.boot.verifiedbootstate")
    bl = "已解锁" if boot in ("orange","yellow") else "未知"
    self._device_brand = brand; self._device_model = model
    self.log(f" 📱 {brand} {model} | Android {ver} (API {sdk})", "info")
    self.log(f" 🔓 BL: {bl}", "ok" if bl == "已解锁" else "warn")
    self.ui(self._update_info, "brand", brand)
    self.ui(self._update_info, "model", model)
    self.ui(self._update_info, "android", "A" + ver)
    self.ui(self._update_info, "sdk", "API " + sdk)
    self.ui(self._update_info, "bl", bl)
    if sdk.isdigit() and int(sdk) < 29:
      self.log(" ✗ 本工具仅支持 Android 10 及以上", "err")
      return False
    return True

  def step_find_zip(self):
    self.log("▸ 步骤 4/10：查找卡刷包", "neon")
    try:
      zips = [f for f in os.listdir(self.current_dir) if f.lower().endswith(".zip")]
    except Exception as e:
      self.log(f" ✗ 读取目录失败: {e}", "err"); return None
    if not zips:
      self.log(" ✗ 没有找到 .zip 卡刷包", "err"); return None
    if len(zips) > 1:
      try:
        zips.sort(key=lambda x: os.path.getmtime(
          os.path.join(self.current_dir, x)), reverse=True)
      except Exception: zips.sort()
      chosen = self._ask_zip_choice(zips)
      if chosen is None:
        self.log(" ✗ 用户取消选择", "err"); return None
      zp = os.path.join(self.current_dir, chosen)
      self.log(f" ✓ 已选择: {chosen}（{fmt_size(os.path.getsize(zp))}）", "ok")
    else:
      zp = os.path.join(self.current_dir, zips[0])
      self.log(f" ✓ 找到: {zips[0]}（{fmt_size(os.path.getsize(zp))}）", "ok")
    # 防呆：机型匹配
    if cfg("check_firmware_match") and self._device_model:
      ok, msg = self.device_guard.check_firmware_match(zp, self._device_model)
      self.log(f" {'✓' if ok else '⛔'} {msg}", "ok" if ok else "err")
      if not ok:
        if not messagebox.askyesno("机型不匹配",
          f"{msg}\n\n继续刷入极可能变砖，是否继续？"):
          return None
    # 空文件检测
    try:
      if os.path.getsize(zp) < 1024:
        self.log(" ✗ 卡刷包文件异常（< 1KB）", "err"); return None
    except Exception: pass
    try:
      self.log(" 🔐 正在计算卡刷包 SHA256...", "purple")
      h = self.guard.sha256(zp)
      self.log(f" ✓ SHA256: {h[:32]}...", "dim")
    except Exception: pass
    return zp

  def _ask_zip_choice(self, zips):
    result = [None]
    dlg = ctk.CTkToplevel(self)
    dlg.title("选择卡刷包"); dlg.geometry("600x420")
    dlg.configure(fg_color=T.BG_MAIN); dlg.grab_set()
    dlg.attributes("-topmost", True); dlg.resizable(False, False)
    ctk.CTkFrame(dlg, height=3, fg_color=T.ACCENT).pack(fill="x")
    ctk.CTkLabel(dlg, text="检测到多个卡刷包",
           font=F("Microsoft YaHei UI", 16, "bold"),
           text_color=T.TEXT_MAIN).pack(pady=(20,6))
    ctk.CTkLabel(dlg, text="请选择要刷入的（按修改时间排序）：",
           font=F_SUB_11, text_color=T.TEXT_DIM).pack()
    scroll = ctk.CTkScrollableFrame(dlg, width=540, height=240,
                     fg_color=T.BG_PANEL, corner_radius=8)
    scroll.pack(pady=16, padx=20, fill="x")
    def pick(name): result[0] = name; dlg.destroy()
    for z in zips:
      try:
        size_mb = os.path.getsize(os.path.join(self.current_dir, z))/1024/1024
        label = f"{z}  ({size_mb:.0f} MB)"
      except Exception: label = z
      ctk.CTkButton(scroll, text=label, command=lambda n=z: pick(n),
        height=40, anchor="w", font=F_SUB_11, fg_color=T.BG_CARD,
        hover_color=T.BG_HOVER, text_color=T.TEXT_MAIN,
        corner_radius=8).pack(fill="x", pady=3, padx=6)
    ctk.CTkButton(dlg, text="取消", command=dlg.destroy, width=120, height=36,
      fg_color="#2A1418", hover_color="#5A1E28", text_color="#FF8899",
      corner_radius=8).pack(pady=(0,16))
    self.wait_window(dlg)
    return result[0]

  def step_extract(self, zf):
    if self.runner.stop_flag: return False
    self.log("▸ 步骤 5/10：从卡刷包提取 payload", "neon")
    pp = os.path.join(self.current_dir, "payload.bin")
    if os.path.exists(pp):
      try: os.remove(pp); self.log(" 🧹 已清理旧 payload.bin", "dim")
      except Exception: pass
    self.log(" ⏳ 解压中...", "info")
    try:
      with zipfile.ZipFile(zf, 'r') as z:
        if "payload.bin" not in z.namelist():
          self.log(" ✗ 卡刷包里没有 payload.bin", "err"); return False
        z.extract("payload.bin", self.current_dir)
    except Exception as e:
      self.log(f" ✗ 解压失败: {e}", "err"); return False
    # 修复：检测空文件
    if os.path.exists(pp) and os.path.getsize(pp) > 1024:
      self.log(f" ✓ payload.bin 提取成功（{fmt_size(os.path.getsize(pp))}）", "ok")
      return True
    self.log(" ✗ 提取失败或文件异常", "err")
    return False

  def step_unpack(self):
    self.log("▸ 步骤 6/10：解包分区镜像", "neon")
    pp = os.path.join(self.current_dir, "payload.bin")
    if not os.path.exists(pp):
      self.log(" ✗ payload.bin 不存在", "err"); return False
    try:
      free_gb = shutil.disk_usage(self.current_dir).free / 1024**3
      if free_gb < 15:
        self.log(f" ⚠ 磁盘剩余 {free_gb:.1f} GB，可能不够", "warn")
    except Exception: pass
    try:
      for d in os.listdir(self.current_dir):
        if d.startswith("extracted_"):
          try: shutil.rmtree(os.path.join(self.current_dir, d))
          except Exception: pass
    except Exception: pass
    self.log(" ⏳ 解包中，预计 3-8 分钟", "info")
    prog_re = re.compile(r"\[(\d+)/(\d+)\]")
    state = {"total": 1, "done": 0}
    def on_line(line):
      m = prog_re.search(line)
      if m:
        d, t = int(m.group(1)), int(m.group(2))
        state["total"] = max(1, t); state["done"] = d
        p = 0.25 + 0.15 * (d / state["total"])
        self.ui(self._set_progress, p)
        self.ui(self.step_text.configure,
            text=f"解包 {d}/{t}", text_color=T.ACCENT)
    # v5.1 Pro 修复：动态识别 payload 内实际分区，避免报错退出
    self.log(" 🔍 识别 payload 内实际分区...", "info")
    list_out = self.runner.run_quiet(
      f'{self.dumper} -l payload.bin', timeout=180, cwd=self.current_dir)
    available = set()
    for ln in (list_out or "").splitlines():
      ln = ln.strip()
      if not ln:
        continue
      m = re.search(r'(?:Partition Name|partition)[\s:]+([a-zA-Z0-9_]+)',
             ln, re.I)
      if m:
        available.add(m.group(1).lower())
        continue
      if re.match(r'^[a-zA-Z0-9_]+$', ln):
        available.add(ln.lower())
    requested = [p.strip() for p in PAYLOAD_PARTS.split(',') if p.strip()]
    if available:
      real_parts = [p for p in requested if p in available]
      missing = [p for p in requested if p not in available]
      if missing:
        self.log(f" ℹ 卡刷包内无以下分区，已跳过：{', '.join(missing)}", "dim")
      if real_parts:
        part_arg = "-p " + ",".join(real_parts)
        self.log(f" ✓ 实际解包 {len(real_parts)} 个分区", "ok")
      else:
        part_arg = ""
        self.log(" ⚠ 未匹配到任何分区，改为全量解包", "warn")
    else:
      part_arg = ""
      self.log(" ⚠ 无法识别分区列表，改为全量解包", "warn")

    cmd = f'{self.dumper} -q {part_arg} payload.bin'.strip()
    ok, errs = self._run_step(cmd, "解包", timeout=1800,
                 cwd=self.current_dir, on_line=on_line)
    if not ok:
      self._show_errors(errs, "解包"); return False
    try:
      for d in sorted(os.listdir(self.current_dir), reverse=True):
        if d.startswith("extracted_"):
          self.extract_dir = os.path.join(self.current_dir, d)
          self.log(" ✓ 镜像已解包", "ok"); return True
    except Exception: pass
    self.log(" ✗ 未找到解包目录", "err")
    return False

  def step_enter_fb(self, mode, dev):
    self.log("▸ 步骤 7/10：进入 Fastboot 模式", "neon")
    if mode == "ADB":
      self.log(" ⏳ 让手机重启到 Fastboot...", "info")
      self.runner.run_quiet(f"{self.adb} -s {dev} reboot bootloader")
      time.sleep(5)
    for i in range(120):
      if self.runner.stop_flag: return False
      if self.runner.run_quiet(f"{self.fb} devices"):
        self.log(" ✓ 已进入 Fastboot 模式", "ok"); return True
      time.sleep(0.5)
      if (i + 1) % 20 == 0:
        self.log(f" ⏳ 等待中... ({i+1}/120)", "dim")
    self.log(" ✗ 等待超时", "err")
    return False

  def step_flash_physical(self):
    self.log("▸ 步骤 8/10：刷入物理分区", "neon")
    if not self.extract_dir:
      self.log(" ✗ 镜像目录不存在", "err"); return False
    brand_key = detect_brand(getattr(self, '_device_brand', ''))
    physical, _ = get_partitions_for_brand(brand_key)
    self.log(f" 🏷 适配品牌: {get_brand_display(brand_key)}", "purple")
    base = 0.68; span = 0.10
    valid = [it for it in physical
         if os.path.exists(os.path.join(self.extract_dir, it[1]))]
    vtotal = len(valid)
    for i, (name, fn, args) in enumerate(valid):
      if self.runner.stop_flag: return False
      if is_dangerous(name):
        self.log(f" ⛔ 跳过危险分区: {name}", "warn")
        if cfg("confirm_dangerous"):
          if not self.device_guard.confirm_dangerous(name):
            self.log(f" ⏭ 用户取消 {name}", "dim")
            continue
        else:
          continue
      p = os.path.join(self.extract_dir, fn)
      self.ui(self._set_progress, base + span * (i / max(vtotal, 1)))
      self.ui(self.step_text.configure,
          text=f"刷入 {name} ({i+1}/{vtotal})", text_color=T.ACCENT)
      self.log(f" [{i+1}/{vtotal}] 刷入 {name}...", "info")
      arg_str = " ".join(args) + " " if args else ""
      cmd = f'{self.fb} {arg_str}flash {name} "{p}"'
      ok, errs = self._run_step(cmd, f"刷入{name}", timeout=180)
      if not ok:
        self._show_errors(errs, f"刷入{name}"); return False
      self.log(f" ✓ {name}", "ok")
    self.ui(self._set_progress, 0.78)
    return True

  def step_enter_fbd(self):
    self.log("▸ 步骤 9/10：切换到 Fastbootd 模式", "neon")
    self.log(" ⏳ 切换中...", "info")
    self.runner.run_quiet(f"{self.fb} reboot fastboot")
    time.sleep(3)
    for i in range(90):
      if self.runner.stop_flag: return False
      out = self.runner.run_quiet(f"{self.fb} getvar is-userspace 2>&1")
      if "yes" in out.lower():
        self.log(" ✓ Fastbootd 已就绪", "ok"); return True
      time.sleep(0.5)
    self.log(" ⚠ 未确认进入 Fastbootd，尝试继续", "warn")
    return True

  def step_flash_logical(self):
    self.log("▸ 步骤 10/10：刷入逻辑分区", "neon")
    if not self.extract_dir:
      self.log(" ✗ 镜像目录不存在", "err"); return False
    brand_key = detect_brand(getattr(self, '_device_brand', ''))
    _, logical = get_partitions_for_brand(brand_key)
    base = 0.80; span = 0.15
    valid = [it for it in logical
         if os.path.exists(os.path.join(self.extract_dir, it[1]))]
    vtotal = len(valid)
    for i, (name, fn) in enumerate(valid):
      if self.runner.stop_flag: return False
      p = os.path.join(self.extract_dir, fn)
      self.ui(self._set_progress, base + span * (i / max(vtotal, 1)))
      self.ui(self.step_text.configure,
          text=f"刷入 {name} ({i+1}/{vtotal})", text_color=T.ACCENT)
      self.log(f" [{i+1}/{vtotal}] 刷入 {name}...", "info")
      cmd = f'{self.fb} flash {name} "{p}"'
      ok, errs = self._run_step(cmd, f"刷入{name}", timeout=300)
      if not ok:
        self._show_errors(errs, f"刷入{name}"); return False
      self.log(f" ✓ {name}", "ok")
    self.ui(self._set_progress, 0.95)
    return True

  def step_wipe(self):
    self.log("▸ 收尾：清空数据并重启", "neon")
    do_wipe = not bool(cfg("skip_wipe"))
    if do_wipe: do_wipe = self.ask_wipe()
    if do_wipe:
      self.log(" ⏳ 清空 userdata...", "info")
      self.runner.run_quiet(f"{self.fb} erase userdata", 60)
      self.log(" ✓ userdata 已清空", "ok")
      self.log(" ⏳ 清空 metadata...", "info")
      self.runner.run_quiet(f"{self.fb} erase metadata", 60)
      self.log(" ✓ metadata 已清空", "ok")
    else:
      self.log(" ⏭ 已跳过清空数据", "info")
    self.log(" ⏳ 重启中...", "info")
    self.runner.run_quiet(f"{self.fb} reboot", 30)

  def ask_wipe(self):
    result = [False]
    dlg = ctk.CTkToplevel(self)
    dlg.title("清空数据确认"); dlg.geometry("460x260")
    dlg.configure(fg_color=T.BG_MAIN); dlg.grab_set()
    dlg.attributes("-topmost", True); dlg.resizable(False, False)
    ctk.CTkFrame(dlg, height=3, fg_color=T.WARN).pack(fill="x")
    ctk.CTkLabel(dlg, text="⚠ WARNING", font=F("Consolas", 12, "bold"),
           text_color=T.WARN).pack(pady=(24,6))
    ctk.CTkLabel(dlg, text="是否清空用户数据？",
           font=F("Microsoft YaHei UI", 17, "bold"),
           text_color=T.TEXT_MAIN).pack()
    ctk.CTkLabel(dlg, text="跨版本刷机建议清空，同版本可跳过",
           font=F_SUB_11, text_color=T.TEXT_DIM).pack(pady=(6,0))
    bf = ctk.CTkFrame(dlg, fg_color="transparent"); bf.pack(pady=28)
    def yes(): result[0] = True; dlg.destroy()
    def no(): result[0] = False; dlg.destroy()
    ctk.CTkButton(bf, text="清空 (推荐)", command=yes, width=150, height=44,
      fg_color="#7F1D1D", hover_color="#A02020", corner_radius=10,
      font=F_BTN_S, border_width=1, border_color=T.ERR).pack(side="left", padx=10)
    ctk.CTkButton(bf, text="跳过", command=no, width=150, height=44,
      fg_color=T.BG_CARD, hover_color=T.BG_HOVER, corner_radius=10,
      font=F_BTN_S, text_color=T.TEXT_DIM, border_width=1,
      border_color=T.BORDER).pack(side="left", padx=10)
    self.wait_window(dlg)
    return result[0]

  # ================= 急救 / ADB 动作 =================
  def manual_backup(self):
    if self.is_running:
      self.log("⚠ 刷机进行中，无法手动备份", "warn"); return
    if self._is_backup_running:
      self.log("⚠ 备份正在进行中", "warn"); return
    self._is_backup_running = True
    threading.Thread(target=self._do_manual_backup, daemon=True).start()

  def _do_manual_backup(self):
    try:
      self.log("▸ 手动备份启动", "purple")
      out = self.runner.run_quiet(f"{self.adb} devices")
      dev = None
      for ln in out.splitlines()[1:]:
        if "\tdevice" in ln: dev = ln.split()[0]; break
      if not dev:
        self.log(" ✗ 未检测到 ADB 设备", "err"); return
      bdir = self.backup_mgr.create_backup_dir()
      if not bdir:
        self.log(" ✗ 无法创建备份目录", "err"); return
      self.log(f" 📁 备份目录: {bdir}", "info")
      ok_count = 0
      for part in ["boot","init_boot"]:
        if self.runner.stop_flag: break
        r = self.backup_mgr.backup_partition(self.adb, dev, part, bdir,
          lambda m, t=None: self.log(m, t))
        if r: ok_count += 1
      if ok_count > 0:
        self.log(f"✅ 备份完成（{ok_count} 个分区）", "ok")
        Toast(self, f"备份完成 {ok_count} 个分区", kind="ok")
      else:
        self.log("⚠ 备份失败，可能手机未 root", "warn")
        Toast(self, "备份失败", kind="err")
    finally:
      self._is_backup_running = False

  def _patch_boot_action(self):
    def run():
      init_boot = self.root_patcher.find_init_boot()
      if not init_boot:
        self.log(" ✗ 未找到 init_boot.img", "err")
        self.log(f" 💡 请把原厂 init_boot.img 放到：{self.current_dir}", "warn")
        return
      self.log(f" 📁 找到: {init_boot}", "info")
      success = self.root_patcher.patch(init_boot,
        lambda m, t=None: self.log(m, t))
      if success:
        self.log(" 💡 修补完成，请将生成的镜像刷入：", "neon")
        self.log(f'   fastboot flash init_boot "{os.path.basename(success)}"', "dim")
    threading.Thread(target=run, daemon=True).start()

  def _disable_modules_action(self):
    def run():
      self.log("🚨 尝试禁用所有模块...", "orange")
      out = self.runner.run_quiet(f"{self.adb} devices")
      dev = None
      for ln in out.splitlines()[1:]:
        if "\tdevice" in ln: dev = ln.split()[0]; break
      if not dev:
        self.log(" ✗ 未检测到设备", "err"); return
      cmd = (f'{self.adb} -s {dev} shell '
          f'"su -c \'mv /data/adb/modules /data/adb/modules_disabled\'"')
      out = self.runner.run_quiet(cmd)
      if "denied" in out.lower() or "not found" in out.lower():
        self.log(" ✗ 执行失败，请确保设备已 Root 并授权", "err")
      else:
        self.log(" ✓ 模块已禁用，重启后生效", "ok")
        Toast(self, "模块已禁用", kind="ok")
    threading.Thread(target=run, daemon=True).start()

  def _pick_sideload(self):
    p = filedialog.askopenfilename(title="选择要 Sideload 的 zip",
      filetypes=[("ZIP","*.zip"),("All","*.*")], initialdir=self.current_dir)
    if p:
      self.sideload_path.configure(text=os.path.basename(p),
                     text_color=T.TEXT_MAIN)
      self._sideload_file = p

  def _do_sideload(self):
    p = getattr(self, "_sideload_file", None)
    if not p or not os.path.exists(p):
      self.log("✗ 请先选择要 Sideload 的 zip", "err"); return
    def run():
      self.log(f"🚀 Sideload: {os.path.basename(p)}", "purple")
      self.log("  ⚠ 请先在手机上进入 Recovery 并选择 Apply update from ADB", "warn")
      time.sleep(3)
      cmd = f'{self.adb} sideload "{p}"'
      ok, errs = self._run_step(cmd, "Sideload", timeout=1800)
      if ok:
        self.log("✅ Sideload 完成", "ok")
        Toast(self, "Sideload 完成", kind="ok")
      else:
        self._show_errors(errs, "Sideload")
    threading.Thread(target=run, daemon=True).start()

  def _get_adb_dev(self):
    out = self.runner.run_quiet(f"{self.adb} devices")
    for ln in out.splitlines()[1:]:
      if "\tdevice" in ln: return ln.split()[0]
    return None

  def _do_screencap(self):
    def run():
      dev = self._get_adb_dev()
      if not dev:
        self.log("✗ 未检测到 ADB 设备", "err"); return
      ts = datetime.now().strftime("%Y%m%d_%H%M%S")
      save = os.path.join(self.current_dir, f"screenshot_{ts}.png")
      self.log(f"📸 截取屏幕 → {os.path.basename(save)}", "info")
      try:
        with open(save, "wb") as f:
          r = subprocess.run(f"{self.adb} -s {dev} exec-out screencap -p",
            shell=True, stdout=f, stderr=subprocess.PIPE, timeout=30,
            creationflags=safe_flag())
        if os.path.exists(save) and os.path.getsize(save) > 1024:
          self.log(f" ✓ 已保存（{fmt_size(os.path.getsize(save))}）", "ok")
          Toast(self, "截图已保存", kind="ok")
          try: os.startfile(save)
          except Exception: pass
        else:
          self.log(" ✗ 截图失败", "err")
      except Exception as e:
        self.log(f" ✗ 截图异常: {e}", "err")
    threading.Thread(target=run, daemon=True).start()

  def _do_screenrecord(self):
    def run():
      dev = self._get_adb_dev()
      if not dev:
        self.log("✗ 未检测到 ADB 设备", "err"); return
      ts = datetime.now().strftime("%Y%m%d_%H%M%S")
      save = os.path.join(self.current_dir, f"record_{ts}.mp4")
      self.log(f"🎬 录制 180 秒 → {os.path.basename(save)}", "info")
      self.log("  ⚠ 请勿断开数据线", "warn")
      try:
        with open(save, "wb") as f:
          subprocess.run(
            f"{self.adb} -s {dev} exec-out screenrecord --time-limit 180 -",
            shell=True, stdout=f, stderr=subprocess.PIPE, timeout=200,
            creationflags=safe_flag())
        if os.path.exists(save) and os.path.getsize(save) > 1024:
          self.log(f" ✓ 录制完成（{fmt_size(os.path.getsize(save))}）", "ok")
          Toast(self, "录屏已保存", kind="ok")
        else:
          self.log(" ✗ 录制失败", "err")
      except Exception as e:
        self.log(f" ✗ 录制异常: {e}", "err")
    threading.Thread(target=run, daemon=True).start()

  def _do_install_apk(self):
    p = filedialog.askopenfilename(title="选择 APK",
      filetypes=[("APK","*.apk"),("All","*.*")])
    if not p: return
    def run():
      self.log(f"📦 安装 APK: {os.path.basename(p)}", "purple")
      ok, errs = self._run_step(f'{self.adb} install -r "{p}"',
                    "安装 APK", timeout=180)
      if ok:
        self.log("✅ 安装成功", "ok")
        Toast(self, "APK 安装成功", kind="ok")
      else:
        self._show_errors(errs, "安装 APK")
    threading.Thread(target=run, daemon=True).start()

  def _do_tcpip(self):
    def run():
      dev = self._get_adb_dev()
      if not dev:
        self.log("✗ 未检测到 ADB 设备（需先 USB 连接）", "err"); return
      out = self.runner.run_quiet(f"{self.adb} -s {dev} tcpip 5555")
      self.log(f"📡 tcpip 结果: {out}", "info")
      routes = self.runner.run_quiet(
        f"{self.adb} -s {dev} shell ip route")
      wlan_line = ""
      for ln in routes.splitlines():
        if "wlan" in ln:
          wlan_line = ln; break
      m = re.search(r"src (\d+\.\d+\.\d+\.\d+)",
             wlan_line or routes)
      if m:
        self.wireless_ip.delete(0, "end")
        self.wireless_ip.insert(0, f"{m.group(1)}:5555")
        self.log(f" ✓ 手机 IP: {m.group(1)}:5555", "ok")
      Toast(self, "tcpip 已开启，可拔线后连接", kind="ok")
    threading.Thread(target=run, daemon=True).start()

  def _do_connect_wireless(self):
    addr = (self.wireless_ip.get() or "").strip()
    if not addr:
      self.log("✗ 请先输入 IP:端口", "err"); return
    def run():
      out = self.runner.run_quiet(f"{self.adb} connect {addr}")
      self.log(f"📡 connect: {out}", "info")
      if "connected" in out.lower():
        Toast(self, f"已连接 {addr}", kind="ok")
      else:
        Toast(self, "连接失败", kind="err")
    threading.Thread(target=run, daemon=True).start()

  def _do_shell(self):
    try: cmd = self.shell_input.get().strip()
    except Exception: cmd = ""
    if not cmd: return
    self.shell_input.delete(0, "end")
    def run():
      self.log(f"$ {cmd}", "neon")
      out = self.runner.run_quiet(f'{self.adb} shell "{cmd}"', timeout=30)
      if out:
        for ln in out.splitlines(): self.log(f" {ln}", "white")
      else:
        self.log(" (无输出)", "dim")
    threading.Thread(target=run, daemon=True).start()


  # ================= v5.1 Pro 扩展方法 =================
  def _scan_device_thread_ext(self):
    """使用 ModeDetector 全模式扫描（v5.1 Pro）"""
    try:
      self.log("🔍 [Pro] 全模式扫描中...", "info")
      md = ModeDetector(self.adb, self.fb, self.runner)
      mode, serial, extra = md.detect()
      icon = MODE_ICONS.get(mode, "❓")
      self._device_mode = mode
      if serial and (".exe" in serial.lower() or "\\" in serial or "/" in serial or ":" in serial):
        serial = ""
      self._device_serial = serial or ""
      self.log(f" {icon} 模式：{mode} · {md.describe(mode)}", "info")
      self.ui(self._update_info, "mode", mode)
      self.ui(self._update_info, "serial", serial or "—")
      color = {"ADB": T.OK, "Fastboot": T.INFO, "Fastbootd": T.VIOLET,
           "Sideload": T.WARN, "Recovery": T.WARN,
           "EDL": T.ERR, "BROM": T.ERR, "Odin": T.ERR,
           "DFU": T.ERR, "Offline": T.ERR}.get(mode, T.WARN)
      self.ui(self._set_status, mode, color)
      self.ui(self._update_mode_label, mode, serial)

      if mode == "Offline":
        self.log(" ✗ 未检测到设备", "err")
        return
      if mode in ("EDL", "BROM", "Odin", "DFU"):
        self.log(f" 💡 {mode} 模式：请使用对应的专用工具", "warn")
        return
      if mode != "ADB":
        return

      # ADB 模式详细读取
      get = lambda p: self.runner.run_quiet(f"{self.adb} shell getprop {p}")
      brand = get("ro.product.brand"); model = get("ro.product.model")
      ver = get("ro.build.version.release"); sdk = get("ro.build.version.sdk")
      boot = get("ro.boot.verifiedbootstate")
      bl = "已解锁" if boot in ("orange", "yellow") else "未解锁/未知"
      slot = get("ro.boot.slot_suffix") or "_a"
      self._device_brand = brand
      self._device_model = model
      self.log(f" 📱 {brand} {model}", "info")
      self.log(f" 🤖 Android {ver} (API {sdk})", "info")
      self.log(f" 🔓 BL: {bl}", "info")
      self.log(f" 🏷 品牌: {get_brand_display(detect_brand(brand))}", "purple")
      self.log(f" 🔀 槽位: {slot}", "info")
      ok, msg = self.device_guard.check_battery(serial)
      self.log(f" {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
      ok, msg = self.device_guard.check_temperature(serial)
      self.log(f" {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
      root_ok = "uid=0" in self.runner.run_quiet(f"{self.adb} shell su -c id")
      ksu_ok = bool(self.root_patcher.find_ksud())
      for k, v in [("brand", brand), ("model", model),
             ("android", "Android " + ver), ("sdk", "API " + sdk),
             ("bl", bl), ("root", "已激活" if root_ok else "未激活"),
             ("ksu", "已安装" if ksu_ok else "未安装"),
             ("mode", "ADB"), ("serial", serial), ("slot", slot)]:
        self.ui(self._update_info, k, v)
    except Exception as e:
      self.log(f"✗ 扫描异常: {e}", "err")
    finally:
      self._is_scanning = False

  def _update_mode_label(self, mode, serial):
    if not hasattr(self, "mode_label") or not alive(self.mode_label):
      return
    icon = MODE_ICONS.get(mode, "❓")
    try:
      self.mode_label.configure(
        text=f"当前模式：{icon} {mode} · {serial or '—'}",
        text_color={"ADB": T.OK, "Fastboot": T.INFO,
              "Fastbootd": T.VIOLET, "Sideload": T.WARN,
              "Recovery": T.WARN, "EDL": T.ERR,
              "BROM": T.ERR, "Odin": T.ERR,
              "DFU": T.ERR}.get(mode, T.TEXT_MUTED))
    except Exception:
      pass

  def _refresh_mode(self):
    def run():
      if not HAS_EXT:
        self.log("⚠ 未加载扩展模块", "warn"); return
      md = ModeDetector(self.adb, self.fb, self.runner)
      mode, serial, extra = md.detect()
      self._device_mode = mode
      icon = MODE_ICONS.get(mode, "❓")
      self.ui(self._update_mode_label, mode, serial)
      self.log(f"{icon} 模式刷新: {mode} · {md.describe(mode)}", "info")
    threading.Thread(target=run, daemon=True).start()

  def _call_ext(self, fn_name, *args, **kw):
    if not getattr(self, "ext", None):
      self.log("⚠ 扩展模块未加载（huijui_extended.py 缺失）", "warn")
      return
    fn = getattr(self.ext, fn_name, None)
    if not fn:
      self.log(f"⚠ 未知扩展功能: {fn_name}", "err"); return
    def run():
      try: fn(*args, **kw)
      except Exception as e:
        self.log(f"✗ 扩展功能 [{fn_name}] 异常: {e}", "err")
    threading.Thread(target=run, daemon=True).start()

  def _pick_and_sideload(self):
    p = filedialog.askopenfilename(title="选择 OTA/ROM zip",
      filetypes=[("ZIP", "*.zip"), ("All", "*.*")],
      initialdir=self.current_dir)
    if not p:
      return
    def run():
      self.log(f"🚀 Sideload: {os.path.basename(p)}", "purple")
      self.log("  ⚠ 请先在手机上进入 Recovery → Apply update from ADB", "warn")
      time.sleep(3)
      ok, errs = self._run_step(f'{self.adb} sideload "{p}"',
                    "Sideload", timeout=1800)
      if ok:
        self.log("✅ Sideload 完成", "ok")
        Toast(self, "Sideload 完成", kind="ok")
      else:
        self._show_errors(errs, "Sideload")
    threading.Thread(target=run, daemon=True).start()

  def _switch_slot_dialog(self):
    slot = simpledialog.askstring("切换槽位", "输入目标槽位 (a 或 b)：")
    if slot in ("a", "b"):
      self._call_ext("ab_slot_switch", slot)

  def _erase_dialog(self):
    p = simpledialog.askstring("擦除分区", "输入要擦除的分区名：")
    if p and messagebox.askyesno("确认", f"确定擦除 {p}？此操作不可逆！"):
      self._call_ext("fb_erase", p.strip())

  def _flash_single_action(self):
    try:
      part = self.fb_part_entry.get().strip()
    except Exception:
      part = ""
    if not part:
      self.log("✗ 请输入分区名", "err"); return
    p = filedialog.askopenfilename(title=f"选择 {part} 镜像",
      filetypes=[("IMG", "*.img"), ("All", "*.*")],
      initialdir=self.current_dir)
    if p:
      self._call_ext("fb_flash_single", part, p)

  def _hash_dialog(self):
    p = filedialog.askopenfilename(title="选择文件",
      filetypes=[("All", "*.*")], initialdir=self.current_dir)
    if not p:
      return
    algo = simpledialog.askstring("校验", "算法 (md5/sha1/sha256)：") or "sha256"
    algo = algo.strip().lower()
    if algo in ("md5", "sha1", "sha256"):
      self._call_ext(f"{algo}_check", p)
    else:
      self.log(f"✗ 不支持的算法: {algo}", "err")

  def _magic_dialog(self):
    p = filedialog.askopenfilename(title="选择镜像",
      filetypes=[("IMG", "*.img"), ("All", "*.*")],
      initialdir=self.current_dir)
    if p:
      self._call_ext("img_magic", p)
      self._call_ext("bootimg_info", p)

def main():
  # v5.1 Pro+：把主模块挂到 sys.modules，让 huijui_plus 拿到同一个 CFG 实例
  import sys as _sys
  if "__main__" in _sys.modules and "huijui_toolbox" not in _sys.modules:
    _sys.modules["huijui_toolbox"] = _sys.modules["__main__"]
  try:
    app = HuijuiToolboxApp()
    app.mainloop()
  except KeyboardInterrupt: pass
  except Exception as e:
    traceback.print_exc()
    try: messagebox.showerror("程序崩溃", f"{e}")
    except Exception: pass


if __name__ == "__main__":
  main()