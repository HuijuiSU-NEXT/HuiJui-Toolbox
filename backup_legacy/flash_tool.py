# -*- coding: utf-8 -*-
"""
Huijui 刷机 v3.0 · Nebula Edition
全局优化：动态 / 性能 / 防护
Author: 喜羊羊灰灰菜單
"""
import customtkinter as ctk
import subprocess, os, sys, zipfile, threading, time, queue
import webbrowser, shutil, math, random, re, traceback, hashlib
import ctypes
from collections import deque
from datetime import datetime
from tkinter import messagebox

try:
  from PIL import Image
  HAS_PIL = True
except ImportError:
  HAS_PIL = False

# ================= 配置区 =================
APP_NAME = "Huijui 刷机"
APP_VERSION = "v3.0"
COOLAPK = "https://www.coolapk.com/u/43549687"

PHYSICAL = [
  ("vbmeta", "vbmeta.img", "--disable-verity --disable-verification"),
  ("vbmeta_system", "vbmeta_system.img", "--disable-verity --disable-verification"),
  ("vbmeta_vendor", "vbmeta_vendor.img", "--disable-verity --disable-verification"),
  ("boot", "boot.img", ""), ("init_boot", "init_boot.img", ""),
  ("vendor_boot", "vendor_boot.img", ""), ("dtbo", "dtbo.img", ""),
]
LOGICAL = [
  ("system", "system.img"), ("system_ext", "system_ext.img"),
  ("product", "product.img"), ("vendor", "vendor.img"),
  ("odm", "odm.img"), ("mi_ext", "mi_ext.img"),
  ("vendor_dlkm", "vendor_dlkm.img"), ("system_dlkm", "system_dlkm.img"),
]
PAYLOAD_PARTS = ("boot,init_boot,vendor_boot,dtbo,vbmeta,vbmeta_system,"
         "vbmeta_vendor,system,system_ext,product,vendor,odm,"
         "mi_ext,vendor_dlkm,system_dlkm")
STEPS = ["环境检查", "检测设备", "读取信息", "查找卡刷包", "提取载荷",
     "解包镜像", "进入 Fastboot", "刷物理分区", "切换 Fastbootd", "刷逻辑分区"]
STEP_PROGRESS = [0.02, 0.06, 0.12, 0.18, 0.25, 0.40, 0.60, 0.68, 0.78, 0.80]

ERROR_DIAGNOSTICS = [
  (r"Not enough space", "镜像空间不足，通常是 payload.bin 解包不完整，请重新下载卡刷包"),
  (r"Partition not found", "分区名不存在，可能是机型不匹配或卡刷包与手机型号不对应"),
  (r"Write to device failed", "写入失败：①换数据线 ②换电脑 USB 接口（后置优先） ③重启手机进 Fastboot 再试"),
  (r"Couldn't find partition", "找不到分区，确认卡刷包是为你手机的机型编译的"),
  (r"FAILED \(remote: 'Not allowed", "操作被拒绝，可能是 BL 未解锁或 OEM 锁未关闭"),
  (r"FAILED \(remote: 'Flashing is not allowed", "分区被保护，可能是 Anti-Rollback 版本不匹配"),
  (r"no such partition", "分区不存在，检查机型与固件版本是否匹配"),
  (r"cannot load", "文件加载失败，镜像文件可能损坏，重新解包一次"),
  (r"error: Cannot generate image", "生成镜像失败，payload 解包出错，检查磁盘空间"),
  (r"Command failed", "命令执行失败，查看上一条日志的具体错误"),
  (r"getvar:is-userspace FAILED", "无法确认 Fastbootd 状态，手动执行 fastboot reboot fastboot 后重试"),
]

# 配色
NEON = "#00ffd1"; NEON_DIM = "#00b894"; MAGENTA = "#ff2d92"; PURPLE = "#a78bfa"
BG_DEEP = "#05070a"; BG_MAIN = "#0a0e14"; BG_PANEL = "#0f141b"; BG_CARD = "#141a22"
BORDER = "#1a232e"; BORDER_GLOW = "#1f3540"
TEXT_MAIN = "#e8f0f5"; TEXT_DIM = "#7a8a9a"; TEXT_MUTED = "#3f4b58"
OK = "#00ff88"; WARN = "#ffb800"; ERR = "#ff3355"; INFO = "#00b4ff"

F_TITLE=("Microsoft YaHei UI",19,"bold"); F_SUB=("Microsoft YaHei UI",10)
F_SUB_11=("Microsoft YaHei UI",11); F_SUB_26=("Microsoft YaHei UI",26,"bold")
F_SECTION=("Consolas",11,"bold"); F_SECTION_CN=("Microsoft YaHei UI",13,"bold")
F_INFO_KEY=("Consolas",10); F_INFO_VAL=("Consolas",11,"bold")
F_BTN=("Microsoft YaHei UI",14,"bold"); F_BTN_S=("Microsoft YaHei UI",12)
F_BTN_XS=("Microsoft YaHei UI",11); F_LOG=("Consolas",11); F_CLOCK=("Consolas",10)
F_STATUS=("Consolas",12,"bold")

ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[a-zA-Z]')
CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
GARBAGE = set("Рђд─│┌┐└┘█▓░ ")

ctk.set_appearance_mode("Dark"); ctk.set_default_color_theme("blue")

# ================= 工具函数 =================
def get_resource_path(rel):
  if hasattr(sys, '_MEIPASS'):
    return os.path.join(sys._MEIPASS, rel)
  return os.path.join(os.path.abspath("."), rel)

def alive(w):
  try: return w.winfo_exists()
  except Exception: return False

def lerp_color(c1, c2, t):
  t = max(0.0, min(1.0, t))
  r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
  r2, g2, b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
  return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

def ease_out_cubic(t): return 1 - (1 - t) ** 3
def ease_in_out(t): return 3*t*t - 2*t*t*t

def is_admin():
  try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
  except Exception: return False

# ================= 统一动画引擎 =================
class Animator:
  """所有动画组件共享一个 30FPS 主帧，大幅降低 CPU 占用。"""
  def __init__(self, root):
    self.root = root
    self.running = True
    self._listeners = set()
    self._last = time.time()
    self._tick()

  def register(self, cb):
    self._listeners.add(cb)

  def unregister(self, cb):
    self._listeners.discard(cb)

  def _tick(self):
    if not self.running: return
    now = time.time()
    dt = now - self._last
    self._last = now
    for cb in list(self._listeners):
      try: cb(dt)
      except Exception: self._listeners.discard(cb)
    try: self.root.after(33, self._tick)
    except Exception: pass

# ================= 安全防护层 =================
class SecurityGuard:
  """权限、单实例、卡刷包校验、磁盘空间、命令转义。"""

  def __init__(self, base_dir):
    self.base_dir = base_dir
    self._lock_handle = None

  def check_admin(self):
    return is_admin()

  def single_instance(self):
    """通过文件锁保证单实例运行，返回 (ok, msg)。"""
    lock_path = os.path.join(self.base_dir, ".huijui.lock")
    try:
      if os.path.exists(lock_path):
        try:
          with open(lock_path, "r") as f:
            old_pid = int(f.read().strip())
          # Windows: tasklist 检查 PID 是否存活
          r = subprocess.run(f'tasklist /FI "PID eq {old_pid}"',
                    shell=True, capture_output=True, text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW)
          if str(old_pid) in (r.stdout or ""):
            return False, f"检测到已有一个 Huijui 刷机进程在运行 (PID {old_pid})"
        except Exception:
          pass
      with open(lock_path, "w") as f:
        f.write(str(os.getpid()))
      self._lock_handle = lock_path
      return True, ""
    except Exception:
      return True, ""

  def release_lock(self):
    try:
      if self._lock_handle and os.path.exists(self._lock_handle):
        os.remove(self._lock_handle)
    except Exception: pass

  def sha256(self, path, chunk=1024*1024, on_progress=None):
    h = hashlib.sha256()
    try:
      total = os.path.getsize(path)
      done = 0
      with open(path, "rb") as f:
        while True:
          b = f.read(chunk)
          if not b: break
          h.update(b)
          done += len(b)
          if on_progress and total > 0:
            on_progress(done / total)
      return h.hexdigest()
    except Exception as e:
      return f"ERR:{e}"

  def check_disk(self, path, min_gb=20):
    try:
      free = shutil.disk_usage(path).free / 1024**3
      return free >= min_gb, free
    except Exception:
      return True, -1.0

  def check_battery(self, adb, dev):
    try:
      r = subprocess.run(
        f'{adb} -s {dev} shell dumpsys battery',
        shell=True, capture_output=True, text=True, timeout=8,
        creationflags=subprocess.CREATE_NO_WINDOW)
      m = re.search(r"level:\s*(\d+)", r.stdout or "")
      if m: return int(m.group(1))
    except Exception: pass
    return -1

  @staticmethod
  def escape(s):
    """防止命令注入：对路径参数做安全引号。"""
    if s is None: return '""'
    s = str(s).replace('"', '\\"')
    return f'"{s}"'


# ================= 命令执行器（流式增强） =================
class CommandRunner:
  MAX_LOG_SIZE = 10 * 1024 * 1024
  def __init__(self, debug_path):
    self.debug_path = debug_path
    self.stop_flag = False
    self._lock = threading.Lock()
    self._log_fh = None

  def clear_debug(self):
    with self._lock:
      try:
        if os.path.exists(self.debug_path): os.remove(self.debug_path)
      except Exception: pass

  def _rotate(self):
    try:
      if os.path.exists(self.debug_path) and os.path.getsize(self.debug_path) > self.MAX_LOG_SIZE:
        old = self.debug_path + ".old"
        if os.path.exists(old): os.remove(old)
        os.replace(self.debug_path, old)
    except Exception: pass

  def append_debug(self, text):
    with self._lock:
      self._rotate()
      try:
        with open(self.debug_path, "a", encoding="utf-8", errors="ignore") as f:
          f.write(text + "\n")
      except Exception: pass

  def run(self, cmd, timeout=1800, cwd=None, on_tick=None, on_line=None):
    """流式执行：实时把每一行喂给 on_line 回调。"""
    self.append_debug(f"\n{'='*60}\n[{time.strftime('%H:%M:%S')}] {cmd}\n")
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    if os.name == 'nt':
      creationflags |= subprocess.CREATE_NEW_PROCESS_GROUP

    try:
      proc = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, cwd=cwd,
        text=True, encoding='utf-8', errors='ignore',
        bufsize=1, creationflags=creationflags)
    except Exception as e:
      return -1, [f"启动失败: {e}"]

    def _reader():
      try:
        for line in iter(proc.stdout.readline, ''):
          if not line: break
          line = line.rstrip("\r\n")
          if not line: continue
          self.append_debug(line)
          if on_line:
            try: on_line(line)
            except Exception: pass
      except Exception: pass

    t = threading.Thread(target=_reader, daemon=True)
    t.start()

    start = time.time(); next_tick = 5
    try:
      while True:
        if self.stop_flag:
          self._kill_tree(proc)
          return -2, ["用户中止"]
        ret = proc.poll()
        if ret is not None: break
        if time.time() - start > timeout:
          self._kill_tree(proc)
          return -1, ["命令超时"]
        elapsed = time.time() - start
        if on_tick and elapsed > next_tick:
          on_tick(int(elapsed)); next_tick += 5
        time.sleep(0.15)
      t.join(timeout=1.0)
      errors = self._extract_errors()
      return proc.returncode, errors
    except Exception as e:
      try: self._kill_tree(proc)
      except Exception: pass
      return -1, [f"异常: {e}"]

  def _kill_tree(self, proc):
    try:
      if os.name == 'nt':
        subprocess.run(f"taskkill /F /T /PID {proc.pid}",
                shell=True, capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW)
      else:
        proc.kill()
    except Exception:
      try: proc.kill()
      except Exception: pass

  def _extract_errors(self):
    errors = deque(maxlen=10)
    try:
      if not os.path.exists(self.debug_path): return list(errors)
      size = os.path.getsize(self.debug_path)
      with open(self.debug_path, "rb") as f:
        if size > 200*1024: f.seek(-200*1024, 2)
        text = f.read().decode('utf-8', errors='ignore')
      err_re = re.compile(r'(fail|error|invalid|denied|cannot|no such|panic|'
                r'unsupported|unable|refused|missing|corrupt)', re.I)
      for line in text.splitlines():
        c = self._clean_line(line)
        if c and err_re.search(c) and c not in errors:
          errors.append(c)
    except Exception: pass
    return list(errors)

  def _clean_line(self, line):
    line = CTRL_RE.sub('', ANSI_RE.sub('', line)).strip()
    if not line or len(line) < 2: return None
    if all(c in GARBAGE for c in line): return None
    if len(line) > 20 and sum(1 for c in line if c in GARBAGE or ord(c) > 0x2500) / len(line) > 0.7:
      return None
    return line[:300] + "..." if len(line) > 300 else line

  def run_quiet(self, cmd, timeout=15):
    try:
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
      return ((r.stdout or b"") + (r.stderr or b"")).decode('utf-8', errors='ignore').strip()
    except Exception: return ""


# ================= 备份管理器 =================
class BackupManager:
  def __init__(self, base_dir): self.base_dir = base_dir

  def create_backup_dir(self):
    d = os.path.join(self.base_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    try: os.makedirs(d, exist_ok=True); return d
    except Exception: return None

  def backup_partition(self, adb, dev, partition, dest_dir, log):
    out_local = os.path.join(dest_dir, f"{partition}.img")
    remote_tmp = f"/sdcard/_backup_{partition}.img"
    try:
      blk = None
      for path in [f"/dev/block/by-name/{partition}_a", f"/dev/block/by-name/{partition}",
             f"/dev/block/bootdevice/by-name/{partition}_a",
             f"/dev/block/bootdevice/by-name/{partition}"]:
        check = self._shell(adb, dev, f"ls {path} 2>/dev/null")
        if check and "No such" not in check:
          blk = path; break
      if not blk:
        log(f" ⚠ 未找到 {partition} 分区，跳过备份", "warn"); return None
      log(f" ⏳ 备份 {partition} 中...", "info")
      cmd = f'{adb} -s {dev} shell "su -c \'dd if={blk} of={remote_tmp}\'"'
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW)
      if r.returncode != 0:
        log(f" ⚠ {partition} 备份失败（可能未授权 su）", "warn"); return None
      subprocess.run(f'{adb} -s {dev} pull {remote_tmp} "{out_local}"',
              shell=True, capture_output=True, timeout=120,
              creationflags=subprocess.CREATE_NO_WINDOW)
      self._shell(adb, dev, f"rm {remote_tmp}")
      if os.path.exists(out_local):
        log(f" ✓ {partition} 已备份（{os.path.getsize(out_local)/1024/1024:.1f} MB）", "ok")
        return out_local
      return None
    except Exception as e:
      log(f" ⚠ {partition} 备份异常: {e}", "warn"); return None

  def _shell(self, adb, dev, cmd):
    try:
      r = subprocess.run(f'{adb} -s {dev} shell "{cmd}"', shell=True,
                capture_output=True, timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW)
      return (r.stdout or b"").decode('utf-8', errors='ignore').strip()
    except Exception: return ""


# ================= Root 修补 =================
class RootPatcher:
  def __init__(self, work_dir): self.work_dir = work_dir

  def find_ksud(self):
    for n in ["ksud.exe", "ksud"]:
      p = get_resource_path(n)
      if os.path.exists(p): return p
    return None

  def find_original_init_boot(self):
    for d in sorted(os.listdir(self.work_dir), reverse=True):
      if d.startswith("extracted_"):
        p = os.path.join(self.work_dir, d, "init_boot.img")
        if os.path.exists(p): return p
    return None

  def patch(self, init_boot_path, log):
    ksud = self.find_ksud()
    if not ksud:
      log(" ⚠ 未找到 ksud.exe，跳过自动修补", "warn")
      log(" 💡 手动方法：用 ReSukiSU「选择并修补」init_boot.img", "dim")
      return None
    out = os.path.join(self.work_dir, f"kernelsu_patched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.img")
    log(" ⏳ 正在用 ksud 修补 init_boot...", "info")
    cmd = f'"{ksud}" boot-patch --boot-image "{init_boot_path}" --out "{out}"'
    try:
      r = subprocess.run(cmd, shell=True, capture_output=True, timeout=180,
                creationflags=subprocess.CREATE_NO_WINDOW)
      if r.returncode == 0 and os.path.exists(out):
        log(f" ✓ 已生成修补文件（{os.path.getsize(out)/1024/1024:.1f} MB）", "ok")
        log(f" 📁 {out}", "info")
        return out
    except Exception as e:
      log(f" ⚠ 修补异常: {e}", "warn")
    log(" ⚠ 修补失败，请手动用 ReSukiSU 修补", "warn")
    return None


# ================= 视觉组件 =================
class ParticleCanvas(ctk.CTkCanvas):
  """优化版：复用 canvas item，避免每帧 delete/create。"""
  def __init__(self, master, animator=None, **kw):
    super().__init__(master, bg=BG_DEEP, highlightthickness=0, **kw)
    self.W, self.H = 1400, 900
    self.particles = []
    self.items = []
    for _ in range(22): # 从38降到22
      self.particles.append({
        "x": random.uniform(0, self.W), "y": random.uniform(0, self.H),
        "r": random.uniform(0.8, 2.6),
        "vx": random.uniform(-0.28, 0.28), "vy": random.uniform(-0.28, 0.28),
        "alpha": random.uniform(0.15, 0.7), "phase": random.uniform(0, 6.28),
      })
    self.bind("<Configure>", self._on_resize)
    if animator: animator.register(self._on_frame)
    self._tick_accum = 0.0

  def _on_resize(self, e):
    self.W = max(1, e.width); self.H = max(1, e.height)

  def _on_frame(self, dt):
    if not alive(self): return
    # 30FPS主帧 → 每2帧更新一次粒子 = 15FPS，视觉足够
    self._tick_accum += dt
    if self._tick_accum < 0.06: return
    self._tick_accum = 0.0
    try:
      if not self.items or len(self.items) != len(self.particles):
        self.delete("p"); self.items = []
        for p in self.particles:
          r = p["r"]
          self.items.append(self.create_oval(p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r,
                            fill=BG_DEEP, outline="", tags="p"))
      for i, p in enumerate(self.particles):
        p["x"] += p["vx"]; p["y"] += p["vy"]
        p["phase"] = (p["phase"] + 0.05) % 6.28
        if p["x"] < 0: p["x"] = self.W
        if p["x"] > self.W: p["x"] = 0
        if p["y"] < 0: p["y"] = self.H
        if p["y"] > self.H: p["y"] = 0
        breath = (math.sin(p["phase"]) + 1) / 2
        a = p["alpha"] * (0.4 + 0.6 * breath)
        color = lerp_color(BG_DEEP, NEON, a)
        r = p["r"]
        try:
          self.coords(self.items[i], p["x"]-r, p["y"]-r, p["x"]+r, p["y"]+r)
          self.itemconfig(self.items[i], fill=color)
        except Exception: pass
    except Exception: pass


class NeonRing(ctk.CTkCanvas):
  """缓动升级：使用 ease_out_cubic 让进度更顺滑。"""
  def __init__(self, master, size=150, thickness=11, animator=None, **kw):
    super().__init__(master, width=size, height=size, bg=BG_PANEL,
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
      # 使用缓动插值，视觉更"重"
      step = diff * min(1.0, dt * 8.0)
      if abs(diff) > 0.0005: self.current += step
      elif self.current != self.target: self.current = self.target
      if self.is_running: self.pulse = (self.pulse + dt * 6.0) % 6.28318
      self._render()
    except Exception: pass

  def _render(self):
    if not alive(self): return
    key = (round(self.current, 3), self.is_running)
    if key == self._last_key: return
    self._last_key = key
    self.delete("all")
    cx = cy = self.size / 2
    r = (self.size - self.thickness) / 2
    w = self.thickness
    self.create_oval(cx-r, cy-r, cx+r, cy+r, outline=BORDER, width=w)
    if self.current > 0.001:
      extent = -360 * self.current
      self.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=extent,
              style="arc", outline="#004d40", width=int(w*1.9))
      if self.is_running:
        pf = 1 + 0.15 * math.sin(self.pulse)
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=extent,
                style="arc", outline="#00997a", width=int(w*1.4*pf))
      self.create_arc(cx-r, cy-r, cx+r, cy+r, start=90, extent=extent,
              style="arc", outline=NEON, width=w)
      ang = math.radians(90 + extent)
      dx = cx + r * math.cos(ang); dy = cy - r * math.sin(ang)
      dr = w * 0.6
      self.create_oval(dx-dr*1.7, dy-dr*1.7, dx+dr*1.7, dy+dr*1.7, fill="#003d33", outline="")
      self.create_oval(dx-dr, dy-dr, dx+dr, dy+dr, fill=NEON, outline="")
    pct = int(round(self.current * 100))
    self.create_text(cx, cy-10, text=f"{pct}", fill=NEON, font=("Segoe UI", 28, "bold"))
    self.create_text(cx, cy+18, text="%", fill=TEXT_DIM, font=("Segoe UI", 11))

  def set(self, v): self.target = max(0.0, min(1.0, v))
  def set_running(self, r): self.is_running = r


class BreathingDot(ctk.CTkLabel):
  def __init__(self, master, color=OK, animator=None, **kw):
    super().__init__(master, text="●", text_color=color, font=("Segoe UI", 15), **kw)
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
        self.phase = (self.phase + dt * 6.0) % 6.28318
        t = (math.sin(self.phase) + 1) / 2
        self.configure(text_color=lerp_color(BG_DEEP, self.base_color, 0.4+0.6*t))
    except Exception: pass


class StepRow(ctk.CTkFrame):
  def __init__(self, master, index, name, animator=None):
    super().__init__(master, fg_color="transparent")
    self.index = index; self.name = name
    self.state = "idle"; self.pulse_phase = 0.0
    self._build()
    if animator: animator.register(self._on_frame)

  def _build(self):
    self.dot = ctk.CTkLabel(self, text="○", font=("Consolas", 12),
                 text_color=TEXT_MUTED, width=18)
    self.dot.pack(side="left")
    self.label = ctk.CTkLabel(self, text=f"{self.index+1:02d} {self.name}",
                  font=("Consolas", 10), text_color=TEXT_MUTED, anchor="w")
    self.label.pack(side="left", padx=(6, 0))

  def set_state(self, state):
    self.state = state
    if not alive(self.dot): return
    try:
      if state == "done":
        self.dot.configure(text="●", text_color=OK)
        self.label.configure(text_color=TEXT_DIM)
      elif state == "active":
        self.label.configure(text_color=NEON)
      elif state == "idle":
        self.dot.configure(text="○", text_color=TEXT_MUTED)
        self.label.configure(text_color=TEXT_MUTED)
    except Exception: pass

  def _on_frame(self, dt):
    if not alive(self): return
    try:
      if self.state == "active":
        self.pulse_phase = (self.pulse_phase + dt * 6.0) % 6.28318
        t = (math.sin(self.pulse_phase) + 1) / 2
        self.dot.configure(text="◉", text_color=lerp_color("#004d40", NEON, t))
    except Exception: pass


# ================= 欢迎界面 =================
class WelcomeScreen(ctk.CTkFrame):
  def __init__(self, master, on_accept, animator):
    super().__init__(master, fg_color=BG_DEEP, corner_radius=0)
    self.on_accept = on_accept
    self.animator = animator
    self._orig_logo = None
    self._logo_label = None
    self._build()

  def _build(self):
    try:
      self.particles = ParticleCanvas(self, animator=self.animator)
      self.particles.place(relx=0.5, rely=0.5, anchor="center")
    except Exception: pass

    wrap = ctk.CTkFrame(self, fg_color="transparent")
    wrap.place(relx=0.5, rely=0.5, anchor="center")

    logo_ok = False
    if HAS_PIL:
      for ext in ("logo.ico", "logo.png", "icon.ico", "icon.png"):
        p = get_resource_path(ext)
        if os.path.exists(p):
          try:
            self._orig_logo = Image.open(p).convert("RGBA")
            img = self._orig_logo.resize((110, 110), Image.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(110, 110))
            self._logo_label = ctk.CTkLabel(wrap, image=self._logo_img, text="")
            self._logo_label.pack(pady=(0, 18))
            logo_ok = True; break
          except Exception: continue
    if not logo_ok:
      self._logo_label = ctk.CTkLabel(wrap, text="🐑", font=("Segoe UI Emoji", 72), text_color=NEON)
      self._logo_label.pack(pady=(0, 18))

    ctk.CTkLabel(wrap, text=APP_NAME, font=F_SUB_26, text_color=NEON).pack()
    ctk.CTkLabel(wrap, text=f"NEBULA EDITION · {APP_VERSION}",
           font=("Consolas", 12, "bold"), text_color=MAGENTA).pack(pady=(6, 4))
    ctk.CTkLabel(wrap, text="by 喜羊羊灰灰菜單", font=F_SUB_11, text_color=TEXT_DIM).pack()

    ctk.CTkFrame(wrap, height=1, width=440, fg_color=BORDER_GLOW).pack(pady=24)
    ctk.CTkLabel(wrap, text="⚠ 免责声明", font=("Microsoft YaHei UI", 14, "bold"),
           text_color=WARN).pack(anchor="w", padx=44, pady=(0, 10))
    for t in ["刷机有风险，操作需谨慎",
         "请确保手机已解锁 BL 并已备份数据",
         "因使用本工具导致的任何设备损坏，作者概不负责",
         "继续使用即代表您已阅读并同意上述条款"]:
      ctk.CTkLabel(wrap, text=f" · {t}", font=("Microsoft YaHei UI", 11),
             text_color=TEXT_DIM, anchor="w", justify="left").pack(anchor="w", padx=40, pady=2)

    ctk.CTkFrame(wrap, height=1, width=440, fg_color=BORDER_GLOW).pack(pady=24)

    self.agree_var = ctk.BooleanVar(value=False)
    ctk.CTkCheckBox(wrap, text="我已阅读并同意上述条款", variable=self.agree_var,
            command=self._on_check, font=("Microsoft YaHei UI", 12),
            text_color=TEXT_MAIN, fg_color=NEON, hover_color=NEON_DIM,
            checkmark_color="#001a14", border_color=BORDER_GLOW,
            border_width=2, corner_radius=6).pack(pady=(0, 18))

    self.btn = ctk.CTkButton(wrap, text="进入主界面 →", command=self._on_enter,
                 height=50, width=280, font=F_BTN,
                 fg_color="#2a3038", hover_color="#3a4048",
                 text_color=TEXT_MUTED, corner_radius=12, state="disabled")
    self.btn.pack(pady=(0, 24))
    ctk.CTkLabel(wrap, text=f"© 2026 喜羊羊灰灰菜單 · {APP_NAME} {APP_VERSION}",
           font=("Consolas", 10), text_color=TEXT_MUTED).pack()

    self._logo_phase = 0.0
    if self.animator: self.animator.register(self._logo_breath)

  def _logo_breath(self, dt):
    if not alive(self) or self._logo_label is None: return
    try:
      self._logo_phase = (self._logo_phase + dt * 1.6) % 6.28318
      t = (math.sin(self._logo_phase) + 1) / 2
      size = int(110 + 6 * t)
      if self._orig_logo is not None:
        resized = self._orig_logo.resize((size, size), Image.LANCZOS)
        self._logo_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))
        self._logo_label.configure(image=self._logo_img)
    except Exception: pass

  def _on_check(self):
    try:
      if self.agree_var.get():
        self.btn.configure(state="normal", fg_color=NEON, hover_color=NEON_DIM, text_color="#001a14")
      else:
        self.btn.configure(state="disabled", fg_color="#2a3038", hover_color="#3a4048", text_color=TEXT_MUTED)
    except Exception: pass

  def _on_enter(self):
    if self.agree_var.get(): self.on_accept()


# ================= 主程序 =================
class FlashApp(ctk.CTk):
  def __init__(self):
    super().__init__()
    self.title(f"{APP_NAME} · Nebula Edition {APP_VERSION}")
    self.geometry("1180x820"); self.minsize(1100, 760)
    self.configure(fg_color=BG_DEEP)

    try: self.attributes("-alpha", 0.0); self._fade_in()
    except Exception: pass

    self.current_dir = os.path.dirname(os.path.abspath(
      sys.argv[0] if getattr(sys, 'frozen', False) else __file__))
    self.extract_dir = None
    self.is_running = False
    self.success_flag = False
    self.log_q = queue.Queue()
    self.ui_q = queue.Queue()
    self._log_count = 0
    self.debug_path = os.path.join(self.current_dir, "huijui_debug.log")

    self.adb = f'"{get_resource_path("adb.exe")}"'
    self.fb = f'"{get_resource_path("fastboot.exe")}"'
    self.dumper = f'"{get_resource_path("payload-dumper-go.exe")}"'

    self.animator = Animator(self)
    self.runner = CommandRunner(self.debug_path)
    self.backup_mgr = BackupManager(self.current_dir)
    self.root_patcher = RootPatcher(self.current_dir)
    self.guard = SecurityGuard(self.current_dir)

    # 安全预检
    self._admin = self.guard.check_admin()
    ok, msg = self.guard.single_instance()
    self._single_ok = ok
    self._single_msg = msg

    self.logo_image = None
    self._load_logo()
    try: self.iconbitmap(get_resource_path("logo.ico"))
    except Exception: pass

    self.protocol("WM_DELETE_WINDOW", self._on_close)

    self.welcome = WelcomeScreen(self, on_accept=self._enter_main, animator=self.animator)
    self.welcome.pack(fill="both", expand=True)
    self._main_built = False

  def _fade_in(self):
    if not alive(self): return
    try:
      a = self.attributes("-alpha")
      if a < 1.0:
        self.attributes("-alpha", min(1.0, a + 0.08))
        self.after(16, self._fade_in)
    except Exception: pass

  def _enter_main(self):
    try:
      if self._main_built: return
      if not self._single_ok:
        messagebox.showwarning("重复运行", self._single_msg)
      if self.welcome is not None:
        try: self.welcome.destroy()
        except Exception: pass
        self.welcome = None
      self._build_ui()
      self._main_built = True
      self._poll_log(); self._poll_ui(); self._tick_clock()
      self.after(200, self._scan_zip)
      self._fade_in_cards()
    except Exception as e:
      traceback.print_exc()

  def _fade_in_cards(self):
    try:
      self._card_alpha = [0.0, 0.0, 0.0]
      self._card_targets = [self.card_left, self.card_mid, self.card_right]
      self._card_anim(0)
    except Exception: pass

  def _card_anim(self, i):
    if i >= 3 or not alive(self): return
    try:
      self._card_alpha[i] = min(1.0, self._card_alpha[i] + 0.12)
      self._card_targets[i].configure(
        border_color=lerp_color(BORDER, BORDER_GLOW, ease_out_cubic(self._card_alpha[i])))
    except Exception: pass
    if self._card_alpha[i] < 1.0:
      self.after(16, lambda: self._card_anim(i))
    else:
      self.after(60, lambda: self._card_anim(i + 1))

  def _on_close(self):
    if self.is_running: return
    try:
      self.guard.release_lock()
      self.animator.running = False
      self.quit(); self.destroy()
    except Exception: pass

  def _load_logo(self):
    if not HAS_PIL: return
    for ext in ("logo.ico", "logo.png", "icon.ico", "icon.png"):
      p = get_resource_path(ext)
      if os.path.exists(p):
        try:
          img = Image.open(p)
          self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
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
    self._build_topbar(); self._build_body(); self._build_footer()

  def _build_topbar(self):
    self.topbar_border = ctk.CTkFrame(self, height=2, fg_color=BORDER_GLOW, corner_radius=0)
    self.topbar_border.pack(fill="x")
    bar = ctk.CTkFrame(self, fg_color=BG_MAIN, height=88, corner_radius=0)
    bar.pack(fill="x"); bar.pack_propagate(False)
    ctk.CTkFrame(self, height=1, fg_color=BORDER_GLOW).pack(fill="x")

    brand = ctk.CTkFrame(bar, fg_color="transparent")
    brand.pack(side="left", padx=26, pady=16)
    if self.logo_image:
      lw = ctk.CTkFrame(brand, fg_color=BG_CARD, corner_radius=14,
               width=58, height=58, border_width=1, border_color=BORDER_GLOW)
      lw.pack(side="left", padx=(0, 16)); lw.pack_propagate(False)
      ctk.CTkLabel(lw, image=self.logo_image, text="").pack(expand=True)
    else:
      lw = ctk.CTkFrame(brand, fg_color=BG_CARD, corner_radius=14, width=58, height=58)
      lw.pack(side="left", padx=(0, 16)); lw.pack_propagate(False)
      ctk.CTkLabel(lw, text="🐑", font=("Segoe UI Emoji", 26), text_color=NEON).pack(expand=True)

    tb = ctk.CTkFrame(brand, fg_color="transparent")
    tb.pack(side="left")
    ctk.CTkLabel(tb, text=APP_NAME, font=F_TITLE, text_color=NEON, anchor="w").pack(anchor="w")
    row = ctk.CTkFrame(tb, fg_color="transparent"); row.pack(anchor="w", pady=(5, 0))
    ctk.CTkLabel(row, text="NEBULA EDITION", font=("Consolas", 10, "bold"),
           text_color=MAGENTA).pack(side="left", padx=(0, 14))
    ctk.CTkLabel(row, text="by 喜羊羊灰灰菜單", font=F_SUB, text_color=TEXT_DIM).pack(side="left", padx=(0, 14))
    link = ctk.CTkLabel(row, text="酷安主页 →", font=F_SUB, text_color=TEXT_DIM, cursor="hand2")
    link.pack(side="left")
    link.bind("<Button-1>", lambda e: webbrowser.open(COOLAPK))
    link.bind("<Enter>", lambda e: link.configure(text_color=NEON))
    link.bind("<Leave>", lambda e: link.configure(text_color=TEXT_DIM))

    sr = ctk.CTkFrame(bar, fg_color="transparent")
    sr.pack(side="right", padx=26)
    self.status_pill = ctk.CTkFrame(sr, fg_color="#0d2818", corner_radius=18,
                     height=36, border_width=1, border_color="#1a4d2e")
    self.status_pill.pack(side="right"); self.status_pill.pack_propagate(False)
    self.status_dot = BreathingDot(self.status_pill, color=OK, animator=self.animator)
    self.status_dot.pack(side="left", padx=(16, 8))
    self.status_label = ctk.CTkLabel(self.status_pill, text="READY", font=F_STATUS, text_color=OK)
    self.status_label.pack(side="left", padx=(0, 18))

  def _build_body(self):
    body = ctk.CTkFrame(self, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=18, pady=16)
    self.card_left = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=16,
                    width=230, border_width=1, border_color=BORDER)
    self.card_left.pack(side="left", fill="y", padx=(0, 14)); self.card_left.pack_propagate(False)
    self._fill_sidebar(self.card_left)
    self.card_mid = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=16,
                   width=270, border_width=1, border_color=BORDER)
    self.card_mid.pack(side="left", fill="y", padx=(0, 14)); self.card_mid.pack_propagate(False)
    self._fill_dashboard(self.card_mid)
    self.card_right = ctk.CTkFrame(body, fg_color=BG_PANEL, corner_radius=16,
                    border_width=1, border_color=BORDER)
    self.card_right.pack(side="left", fill="both", expand=True)
    self._fill_logger(self.card_right)

  def _fill_sidebar(self, left):
    ctk.CTkLabel(left, text="⚡ DEVICE", font=F_SECTION, text_color=NEON).pack(pady=(24, 4), padx=20, anchor="w")
    ctk.CTkLabel(left, text="设备信息", font=F_SECTION_CN, text_color=TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(left, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=14)

    self.info = {}
    for key, label in [("brand", "品牌"), ("model", "型号"), ("android", "系统"),
              ("sdk", "API"), ("bl", "BL"), ("mode", "模式")]:
      row = ctk.CTkFrame(left, fg_color="transparent")
      row.pack(fill="x", padx=20, pady=5)
      ctk.CTkLabel(row, text=label, font=F_INFO_KEY, text_color=TEXT_DIM,
             width=42, anchor="w").pack(side="left")
      val = ctk.CTkLabel(row, text="—", font=F_INFO_VAL, text_color=NEON, anchor="w")
      val.pack(side="left", padx=(6, 0), fill="x", expand=True)
      self.info[key] = val

    ctk.CTkFrame(left, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=18)
    ctk.CTkLabel(left, text="⚙ ACTIONS", font=F_SECTION, text_color=NEON).pack(pady=(0, 4), padx=20, anchor="w")
    ctk.CTkLabel(left, text="操作", font=F_SECTION_CN, text_color=TEXT_MAIN).pack(padx=20, anchor="w", pady=(0, 14))

    self.btn_start = ctk.CTkButton(left, text="▶ 一键刷机", command=self.start,
                    height=50, font=F_BTN, fg_color=NEON, hover_color=NEON_DIM,
                    text_color="#001a14", corner_radius=12)
    self.btn_start.pack(pady=5, padx=20, fill="x")

    self.btn_stop = ctk.CTkButton(left, text="⏹ 中止", command=self.stop,
                    height=40, font=F_BTN_S, fg_color="#2a1418", hover_color="#5a1e28",
                    text_color="#ff8899", corner_radius=10, border_width=1,
                    border_color="#4a1e28", state="disabled")
    self.btn_stop.pack(pady=5, padx=20, fill="x")

    ctk.CTkButton(left, text="🗑 清空日志", command=self.clear_log,
            height=36, font=F_BTN_XS, fg_color=BG_CARD, hover_color=BORDER,
            text_color=TEXT_DIM, corner_radius=10, border_width=1,
            border_color=BORDER).pack(pady=5, padx=20, fill="x")

    ctk.CTkButton(left, text="💾 手动备份 boot/init_boot", command=self.manual_backup,
            height=36, font=F_BTN_XS, fg_color=BG_CARD, hover_color=BORDER,
            text_color=PURPLE, corner_radius=10, border_width=1,
            border_color="#3d2f5a").pack(pady=5, padx=20, fill="x")

    ctk.CTkButton(left, text="📂 打开调试日志", command=self.open_debug,
            height=32, font=("Microsoft YaHei UI", 10), fg_color="transparent",
            hover_color=BG_CARD, text_color=TEXT_MUTED, corner_radius=8,
            border_width=1, border_color=BORDER).pack(pady=5, padx=20, fill="x")

    ctk.CTkButton(left, text="📋 复制最近日志", command=self.copy_recent_log,
            height=32, font=("Microsoft YaHei UI", 10), fg_color="transparent",
            hover_color=BG_CARD, text_color=TEXT_MUTED, corner_radius=8,
            border_width=1, border_color=BORDER).pack(pady=5, padx=20, fill="x")

    ctk.CTkLabel(left, text=f"{APP_VERSION} Nebula", font=("Consolas", 10, "bold"),
           text_color=MAGENTA).pack(side="bottom", pady=(0, 4))
    ctk.CTkLabel(left, text="© 喜羊羊灰灰菜單", font=F_SUB, text_color=TEXT_MUTED).pack(side="bottom", pady=(0, 20))

  def _fill_dashboard(self, mid):
    ctk.CTkLabel(mid, text="⏣ PROGRESS", font=F_SECTION, text_color=NEON).pack(pady=(24, 4), padx=20, anchor="w")
    ctk.CTkLabel(mid, text="刷机进度", font=F_SECTION_CN, text_color=TEXT_MAIN).pack(padx=20, anchor="w")
    ctk.CTkFrame(mid, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=14)
    wrap = ctk.CTkFrame(mid, fg_color="transparent"); wrap.pack(pady=6)
    self.ring = NeonRing(wrap, size=150, thickness=11, animator=self.animator)
    self.ring.pack()
    self.step_text = ctk.CTkLabel(mid, text="等待开始", font=F_BTN_S, text_color=TEXT_DIM)
    self.step_text.pack(pady=(8, 16))
    ctk.CTkFrame(mid, height=1, fg_color=BORDER).pack(fill="x", padx=20, pady=4)
    self.steps = []
    sw = ctk.CTkFrame(mid, fg_color="transparent"); sw.pack(fill="x", padx=20, pady=12)
    for i, s in enumerate(STEPS):
      row = StepRow(sw, i, s, animator=self.animator)
      row.pack(fill="x", pady=2); self.steps.append(row)

  def _fill_logger(self, right):
    top = ctk.CTkFrame(right, fg_color="transparent")
    top.pack(fill="x", padx=24, pady=(20, 8))
    ctk.CTkLabel(top, text="▤ CONSOLE", font=F_SECTION, text_color=NEON).pack(side="left")
    ctk.CTkLabel(top, text="实时日志", font=("Microsoft YaHei UI", 12), text_color=TEXT_MAIN).pack(side="left", padx=(10, 0))
    self.log_count = ctk.CTkLabel(top, text="0 行", font=("Consolas", 10), text_color=TEXT_MUTED)
    self.log_count.pack(side="right")
    self.log_box = ctk.CTkTextbox(right, font=F_LOG, fg_color=BG_DEEP, text_color=TEXT_MAIN,
                    corner_radius=10, wrap="word", border_width=1, border_color=BORDER,
                    scrollbar_button_color=BORDER, scrollbar_button_hover_color=NEON_DIM)
    self.log_box.pack(fill="both", expand=True, padx=24, pady=(0, 22))
    for tag, color in [("ok", OK), ("err", ERR), ("warn", WARN), ("info", INFO),
              ("neon", NEON), ("dim", TEXT_DIM), ("muted", TEXT_MUTED),
              ("magenta", MAGENTA), ("purple", PURPLE), ("white", TEXT_MAIN)]:
      self.log_box.tag_config(tag, foreground=color)
    self._welcome()

  def _build_footer(self):
    ctk.CTkFrame(self, height=1, fg_color=BORDER_GLOW).pack(fill="x")
    f = ctk.CTkFrame(self, fg_color=BG_MAIN, height=32, corner_radius=0)
    f.pack(fill="x"); f.pack_propagate(False)
    ctk.CTkLabel(f, text="● ONLINE", font=("Consolas", 10, "bold"), text_color=OK).pack(side="left", padx=(20, 24))
    ctk.CTkFrame(f, width=1, height=14, fg_color=BORDER).pack(side="left")
    admin_txt = "ADMIN" if self._admin else "USER"
    admin_color = OK if self._admin else WARN
    ctk.CTkLabel(f, text=f"● {admin_txt}", font=("Consolas", 10, "bold"),
           text_color=admin_color).pack(side="left", padx=(24, 24))
    ctk.CTkFrame(f, width=1, height=14, fg_color=BORDER).pack(side="left")
    ctk.CTkLabel(f, text=f"{APP_NAME} {APP_VERSION} Nebula Edition",
           font=F_CLOCK, text_color=TEXT_DIM).pack(side="left", padx=(24, 24))
    ctk.CTkLabel(f, text="by 喜羊羊灰灰菜單", font=F_SUB, text_color=MAGENTA).pack(side="left", padx=(24, 0))
    self.clock = ctk.CTkLabel(f, text="", font=F_CLOCK, text_color=TEXT_DIM)
    self.clock.pack(side="right", padx=20)

  def _tick_clock(self):
    if not alive(self): return
    try: self.clock.configure(text=time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception: return
    self.after(1000, self._tick_clock)

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

  def _welcome(self):
    self._log_plain("━"*46, "neon")
    self._log_plain(f"  {APP_NAME} · Nebula Edition · {APP_VERSION}", "neon")
    self._log_plain("  by 喜羊羊灰灰菜單", "dim")
    self._log_plain("━"*46, "neon")
    self._log_plain("")
    self._log_plain("👋 欢迎使用 Huijui 刷机", "white")
    self._log_plain("")
    self._log_plain("🆕 v3.0 新特性：", "magenta")
    self._log_plain("  · 统一动画引擎，帧率更稳、CPU 更低", "dim")
    self._log_plain("  · 流式日志，解包/刷机进度实时可见", "dim")
    self._log_plain("  · 单实例锁 + 管理员检测 + 磁盘防护", "dim")
    self._log_plain("  · 刷机前自动备份 boot/init_boot", "dim")
    self._log_plain("")
    self._log_plain("⚠ 刷机将清空数据，请先备份！", "warn")
    self._log_plain("")

  def _log_plain(self, msg, tag=None):
    if not alive(self.log_box): return
    try:
      self.log_box.insert("end", msg + "\n", tag or ())
      self.log_box.see("end"); self._log_count += 1
    except Exception: pass

  def log(self, msg, tag=None): self.log_q.put(("ts", msg, tag))

  def _poll_log(self):
    if not alive(self): return
    try:
      # 批量插入，减少主线程压力
      batch = []
      while True:
        try: batch.append(self.log_q.get_nowait())
        except queue.Empty: break
      if batch and alive(self.log_box):
        ts = time.strftime("%H:%M:%S")
        for kind, msg, tag in batch:
          try:
            self.log_box.insert("end", f"[{ts}] ", "muted")
            self.log_box.insert("end", msg + "\n", tag or ())
            self._log_count += 1
          except Exception: pass
        try:
          self.log_box.see("end")
          self.log_count.configure(text=f"{self._log_count} 行")
        except Exception: pass
    except Exception: pass
    self.after(60, self._poll_log)

  def clear_log(self):
    if not alive(self.log_box): return
    try:
      self.log_box.delete("1.0", "end"); self._log_count = 0
      self.log_count.configure(text="0 行")
    except Exception: pass

  def open_debug(self):
    try:
      if os.path.exists(self.debug_path): os.startfile(self.debug_path)
      else: self.log("💡 调试日志还没有内容", "warn")
    except Exception as e: self.log(f"✗ 无法打开: {e}", "err")

  def copy_recent_log(self):
    try:
      if not os.path.exists(self.debug_path):
        self.log("💡 调试日志还没有内容", "warn"); return
      size = os.path.getsize(self.debug_path)
      with open(self.debug_path, "rb") as f:
        if size > 100*1024: f.seek(-100*1024, 2)
        data = f.read()
      lines = data.decode('utf-8', errors='ignore').splitlines()[-100:]
      self.clipboard_clear(); self.clipboard_append("\n".join(lines))
      self.log("✅ 已复制最近 100 行日志到剪贴板", "ok")
    except Exception as e: self.log(f"✗ 复制失败: {e}", "err")

  def manual_backup(self):
    if self.is_running:
      self.log("⚠ 刷机进行中，无法手动备份", "warn"); return
    threading.Thread(target=self._do_manual_backup, daemon=True).start()

  def _do_manual_backup(self):
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
    for part in ["boot", "init_boot"]:
      if self.runner.stop_flag: break
      r = self.backup_mgr.backup_partition(self.adb, dev, part, bdir, lambda m, t=None: self.log(m, t))
      if r: ok_count += 1
    if ok_count > 0: self.log(f"✅ 备份完成（{ok_count} 个分区）", "ok")
    else: self.log("⚠ 备份失败，可能手机未 root 或未授权 su", "warn")

  # ============ 状态 ============
  def set_status(self, text, color=OK):
    try:
      self.status_dot.set_color(color)
      self.status_label.configure(text=text, text_color=color)
      bg_map = {OK:("#0d2818","#1a4d2e"), WARN:("#2b2010","#4d3a15"),
           ERR:("#2b0e14","#4d1a26"), PURPLE:("#1a1428","#2d1f4a")}
      bg, bd = bg_map.get(color, ("#0d2818", "#1a4d2e"))
      self.status_pill.configure(fg_color=bg, border_color=bd)
      top_color = {OK:"#1a4d2e", WARN:"#4d3a15", ERR:"#4d1a26", PURPLE:"#2d1f4a"}.get(color, BORDER_GLOW)
      if alive(self.topbar_border): self.topbar_border.configure(fg_color=top_color)
    except Exception: pass

  def set_progress(self, v):
    try: self.ring.set(v)
    except Exception: pass

  def set_step(self, i):
    for idx, s in enumerate(self.steps):
      if idx < i: s.set_state("done")
      elif idx == i:
        s.set_state("active")
        try: self.step_text.configure(text=STEPS[idx], text_color=NEON)
        except Exception: pass
      else: s.set_state("idle")

  def update_info(self, key, value):
    if key in self.info:
      try: self.info[key].configure(text=value or "—")
      except Exception: pass

  # ============ 控制 ============
  def start(self):
    if self.is_running: return
    # 管理员警告
    if not self._admin:
      if not messagebox.askyesno("警告", "未以管理员身份运行，Fastboot 刷机可能失败。\n仍要继续吗？"):
        return
    # 磁盘防护
    ok, free = self.guard.check_disk(self.current_dir, min_gb=20)
    if not ok and free > 0:
      if not messagebox.askyesno("磁盘空间不足", f"仅剩 {free:.1f} GB，刷机可能失败。\n仍要继续吗？"):
        return

    self.is_running = True; self.success_flag = False
    self.runner.stop_flag = False
    try: self.btn_start.configure(state="disabled", text="刷机中...")
    except Exception: pass
    try: self.btn_stop.configure(state="normal")
    except Exception: pass
    self.ui(self.set_status, "RUNNING", WARN)
    self.ui(self.status_dot.set_active, True)
    self.ui(self.ring.set_running, True)
    self.clear_log(); self.ui(self.set_step, -1)
    try: self.step_text.configure(text="准备中...", text_color=TEXT_DIM)
    except Exception: pass
    self.runner.clear_debug()
    threading.Thread(target=self.flow, daemon=True).start()

  def stop(self):
    if not self.is_running: return
    self.runner.stop_flag = True
    self.log("⛔ 正在中止...", "err")

  def finish(self):
    self.is_running = False
    self.ui(self.status_dot.set_active, False)
    self.ui(self.ring.set_running, False)
    self.ui(self.btn_start.configure, state="normal", text="▶ 一键刷机")
    self.ui(self.btn_stop.configure, state="disabled")
    if self.runner.stop_flag:
      self.ui(self.set_status, "STOPPED", ERR)
      self.ui(self.step_text.configure, text="已中止", text_color=ERR)
    elif self.success_flag:
      self.ui(self.set_status, "COMPLETE", OK)
      self.ui(self.step_text.configure, text="刷机完成", text_color=OK)
    else:
      self.ui(self.set_status, "INCOMPLETE", WARN)
      self.ui(self.step_text.configure, text="未完成", text_color=WARN)

  def _run_step(self, cmd, hint, timeout=600, cwd=None, on_line=None):
    def beat(sec):
      m, s = divmod(sec, 60)
      self.log(f" ⏳ 已运行 {m}m{s}s" if m > 0 else f" ⏳ 已运行 {sec}s", "dim")
    ret, errs = self.runner.run(cmd, timeout=timeout, cwd=cwd, on_tick=beat, on_line=on_line)
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
    self.log(" 💡 完整日志: 点击左侧「📂 打开调试日志」", "warn")

  # ================= 主流程 =================
  def flow(self):
    try:
      self.ui(self.set_step, 0); self.ui(self.set_progress, STEP_PROGRESS[0])
      if not self.step_env(): return
      self.ui(self.set_step, 1); self.ui(self.set_progress, STEP_PROGRESS[1])
      mode, dev = self.step_detect()
      if not mode: return
      self.ui(self.set_step, 2); self.ui(self.set_progress, STEP_PROGRESS[2])
      if mode == "ADB": self.step_info()
      if mode == "ADB" and dev: self._auto_backup(dev)
      self.ui(self.set_step, 3); self.ui(self.set_progress, STEP_PROGRESS[3])
      zf = self.step_find_zip()
      if not zf: return
      self.ui(self.set_step, 4); self.ui(self.set_progress, STEP_PROGRESS[4])
      if not self.step_extract(zf): return
      self.ui(self.set_step, 5); self.ui(self.set_progress, STEP_PROGRESS[5])
      if not self.step_unpack(): return
      self.ui(self.set_step, 6); self.ui(self.set_progress, STEP_PROGRESS[6])
      if not self.step_enter_fb(mode, dev): return
      self.ui(self.set_step, 7)
      if not self.step_flash_physical(): return
      self.ui(self.set_step, 8); self.ui(self.set_progress, 0.78)
      if not self.step_enter_fbd(): return
      self.ui(self.set_step, 9); self.ui(self.set_progress, 0.80)
      if not self.step_flash_logical(): return
      self.ui(self.set_progress, 0.95)
      self.step_wipe()
      self.ui(self.set_progress, 1.0)
      self.success_flag = True
      self.log(""); self.log("🎉 ══ 刷机成功 ══ 🎉", "ok")
      self.log("首次开机需 10-15 分钟，请勿强制关机", "warn")
      self._auto_patch_root()
      self.after(3000, self._open_current_dir)
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
    self.log(f" 📁 {os.path.basename(bdir)}", "info")
    for part in ["boot", "init_boot"]:
      if self.runner.stop_flag: return
      self.backup_mgr.backup_partition(self.adb, dev, part, bdir, lambda m, t=None: self.log(m, t))

  def _auto_patch_root(self):
    self.log(""); self.log("▸ 附加：尝试自动修补 Root", "purple")
    init_boot = self.root_patcher.find_original_init_boot()
    if not init_boot:
      self.log(" ⚠ 未找到原厂 init_boot.img，跳过修补", "warn"); return
    self.log(f" 📁 {init_boot}", "dim")
    out = self.root_patcher.patch(init_boot, lambda m, t=None: self.log(m, t))
    if out:
      self.log(" 💡 修补完成后，在 Fastboot 模式手动刷入：", "info")
      self.log(f"   fastboot flash init_boot \"{os.path.basename(out)}\"", "dim")

  def _open_current_dir(self):
    try: os.startfile(self.current_dir)
    except Exception: pass

  def step_env(self):
    self.log("▸ 步骤 1/10：检查运行环境", "neon")
    ok = True
    for name, label in [("adb.exe", "ADB 工具"), ("fastboot.exe", "Fastboot 工具"),
               ("payload-dumper-go.exe", "解包工具")]:
      if os.path.exists(get_resource_path(name)): self.log(f" ✓ {label} 已就绪", "ok")
      else:
        self.log(f" ✗ 缺少 {label}（{name}）", "err"); ok = False
    try:
      free_gb = shutil.disk_usage(self.current_dir).free / 1024**3
      if free_gb < 20: self.log(f" ⚠ 磁盘剩余 {free_gb:.1f} GB，建议 20GB+", "warn")
      else: self.log(f" ✓ 磁盘剩余 {free_gb:.1f} GB", "ok")
    except Exception: pass
    try:
      zips = [f for f in os.listdir(self.current_dir) if f.lower().endswith(".zip")]
      if zips: self.log(f" ✓ 检测到 {len(zips)} 个卡刷包", "ok")
      else: self.log(f" ⚠ 未检测到卡刷包", "warn")
    except Exception: pass
    if not ok: self.log(" 💡 程序文件不完整，请重新下载", "warn")
    return ok

  def step_detect(self):
    self.log("▸ 步骤 2/10：检测手机连接", "neon")
    out = self.runner.run_quiet(f"{self.fb} devices")
    if out:
      dev = out.split()[0]
      self.log(" ✓ 已连接（Fastboot 模式）", "ok")
      self.ui(self.update_info, "mode", "Fastboot")
      return "FASTBOOT", dev
    for _ in range(6):
      if self.runner.stop_flag: return None, None
      out = self.runner.run_quiet(f"{self.adb} devices")
      for ln in out.splitlines()[1:]:
        if "\tdevice" in ln:
          dev = ln.split()[0]
          self.log(" ✓ 已连接（ADB 模式）", "ok")
          self.ui(self.update_info, "mode", "ADB")
          lv = self.guard.check_battery(self.adb, dev)
          if lv > 0:
            if lv < 20: self.log(f" ⚠ 手机电量仅 {lv}%，建议充电后再刷", "warn")
            else: self.log(f" ✓ 手机电量 {lv}%", "ok")
          return "ADB", dev
        elif "unauthorized" in ln:
          self.log(" ⚠ 请在手机上点击「允许 USB 调试」", "warn")
      time.sleep(0.5)
    self.log(" ✗ 未检测到手机", "err")
    self.log(" 💡 请检查：", "warn")
    self.log("   ① USB 数据线已连接", "dim")
    self.log("   ② 手机已开启 USB 调试", "dim")
    self.log("   ③ 手机上弹窗已点「允许」", "dim")
    return None, None

  def step_info(self):
    self.log("▸ 步骤 3/10：读取设备信息", "neon")
    get = lambda p: self.runner.run_quiet(f"{self.adb} shell getprop {p}")
    brand = get("ro.product.brand"); model = get("ro.product.model")
    ver = get("ro.build.version.release"); sdk = get("ro.build.version.sdk")
    fb = get("ro.boot.verifiedbootstate")
    bl = "已解锁" if fb in ("orange", "yellow") else "未知"
    self.log(f" 📱 品牌: {brand or '未知'}", "info")
    self.log(f" 📱 型号: {model or '未知'}", "info")
    self.log(f" 🤖 系统: Android {ver or '未知'}", "info")
    self.log(f" 🔢 API: {sdk or '未知'}", "info")
    self.log(f" 🔓 BL: {bl}", "ok" if bl == "已解锁" else "warn")
    self.ui(self.update_info, "brand", brand); self.ui(self.update_info, "model", model)
    self.ui(self.update_info, "android", "A" + (ver or "?"))
    self.ui(self.update_info, "sdk", "API " + (sdk or "?"))
    self.ui(self.update_info, "bl", bl)
    if sdk.isdigit() and int(sdk) < 29:
      self.log(" ✗ 本工具仅支持 Android 10 及以上", "err"); return False
    return True

  def step_find_zip(self):
    self.log("▸ 步骤 4/10：查找卡刷包", "neon")
    try:
      zips = [f for f in os.listdir(self.current_dir) if f.lower().endswith(".zip")]
    except Exception as e:
      self.log(f" ✗ 读取目录失败: {e}", "err"); return None
    if not zips:
      self.log(" ✗ 没有找到 .zip 卡刷包", "err")
      self.log(f" 💡 请把卡刷包放到: {self.current_dir}", "warn"); return None
    if len(zips) > 1:
      zips.sort(); chosen = self._ask_zip_choice(zips)
      if chosen is None:
        self.log(" ✗ 用户取消选择", "err"); return None
      zp = os.path.join(self.current_dir, chosen)
      size_mb = os.path.getsize(zp) / 1024 / 1024
      self.log(f" ✓ 已选择: {chosen}（{size_mb:.0f} MB）", "ok")
    else:
      zp = os.path.join(self.current_dir, zips[0])
      size_mb = os.path.getsize(zp) / 1024 / 1024
      self.log(f" ✓ 找到: {zips[0]}（{size_mb:.0f} MB）", "ok")
    # SHA256 计算（防护）
    try:
      self.log(" 🔐 正在计算卡刷包 SHA256...", "purple")
      h = self.guard.sha256(zp)
      self.log(f" ✓ SHA256: {h[:32]}...", "dim")
      self.runner.append_debug(f"[SHA256] {zp} = {h}")
    except Exception: pass
    return zp

  def _ask_zip_choice(self, zips):
    result = [None]
    dlg = ctk.CTkToplevel(self)
    dlg.title("选择卡刷包"); dlg.geometry("600x420")
    dlg.configure(fg_color=BG_MAIN); dlg.grab_set(); dlg.attributes("-topmost", True)
    dlg.resizable(False, False)
    dlg.protocol("WM_DELETE_WINDOW", lambda: dlg.destroy())
    ctk.CTkFrame(dlg, height=3, fg_color=NEON).pack(fill="x")
    ctk.CTkLabel(dlg, text="检测到多个卡刷包", font=("Microsoft YaHei UI", 16, "bold"),
           text_color=TEXT_MAIN).pack(pady=(20, 6))
    ctk.CTkLabel(dlg, text="请选择要刷入的那个：", font=("Microsoft YaHei UI", 11),
           text_color=TEXT_DIM).pack()
    scroll = ctk.CTkScrollableFrame(dlg, width=540, height=240, fg_color=BG_PANEL, corner_radius=10)
    scroll.pack(pady=16, padx=20, fill="x")
    def pick(name): result[0] = name; dlg.destroy()
    for z in zips:
      try:
        size_mb = os.path.getsize(os.path.join(self.current_dir, z))/1024/1024
        label = f"{z}  ({size_mb:.0f} MB)"
      except Exception: label = z
      ctk.CTkButton(scroll, text=label, command=lambda n=z: pick(n), height=40, anchor="w",
              font=("Microsoft YaHei UI", 11), fg_color=BG_CARD,
              hover_color=BORDER_GLOW, text_color=TEXT_MAIN, corner_radius=8
              ).pack(fill="x", pady=3, padx=6)
    ctk.CTkButton(dlg, text="取消", command=dlg.destroy, width=120, height=36,
            fg_color="#2a1418", hover_color="#5a1e28", text_color="#ff8899",
            corner_radius=8).pack(pady=(0, 16))
    self.wait_window(dlg); return result[0]

  def step_extract(self, zf):
    self.log("▸ 步骤 5/10：从卡刷包提取 payload", "neon")
    pp = os.path.join(self.current_dir, "payload.bin")
    if os.path.exists(pp):
      try: os.remove(pp); self.log(" 🧹 已清理旧 payload.bin", "dim")
      except Exception: pass
    self.log(" ⏳ 正在解压，请稍候...", "info")
    try:
      with zipfile.ZipFile(zf, 'r') as z:
        if "payload.bin" not in z.namelist():
          self.log(" ✗ 卡刷包里没有 payload.bin", "err")
          self.log(" 💡 请确认下载的是官方卡刷包(.zip)，不是线刷包(.tgz)", "warn")
          return False
        z.extract("payload.bin", self.current_dir)
    except Exception as e:
      self.log(f" ✗ 解压失败: {e}", "err"); return False
    if os.path.exists(pp):
      self.log(f" ✓ payload.bin 提取成功（{os.path.getsize(pp)/1024/1024:.0f} MB）", "ok")
      return True
    self.log(" ✗ 提取失败", "err"); return False

  def step_unpack(self):
    self.log("▸ 步骤 6/10：解包分区镜像", "neon")
    pp = os.path.join(self.current_dir, "payload.bin")
    if not os.path.exists(pp):
      self.log(" ✗ payload.bin 不存在", "err"); return False
    try:
      free_gb = shutil.disk_usage(self.current_dir).free / 1024**3
      if free_gb < 15: self.log(f" ⚠ 磁盘剩余 {free_gb:.1f} GB，可能不够", "warn")
      else: self.log(f" 💾 磁盘剩余 {free_gb:.1f} GB", "info")
    except Exception: pass
    try:
      for d in os.listdir(self.current_dir):
        if d.startswith("extracted_"):
          try: shutil.rmtree(os.path.join(self.current_dir, d))
          except Exception: pass
    except Exception: pass

    self.log(" ⏳ 正在解包，预计 3-8 分钟", "info")
    self.log(" 💡 每 5 秒心跳提示", "dim")
    # 流式解析：dumper 输出形如 "[1/15] system ..."
    prog_re = re.compile(r"\[(\d+)/(\d+)\]")
    state = {"total": 1, "done": 0}
    def on_line(line):
      m = prog_re.search(line)
      if m:
        d, t = int(m.group(1)), int(m.group(2))
        state["total"] = max(1, t); state["done"] = d
        p = 0.25 + 0.15 * (d / state["total"])
        self.ui(self.set_progress, p)
        self.ui(self.step_text.configure, text=f"解包 {d}/{t}", text_color=NEON)
    cmd = f'{self.dumper} -q -p {PAYLOAD_PARTS} payload.bin'
    ok, errs = self._run_step(cmd, "解包", timeout=1800, cwd=self.current_dir, on_line=on_line)
    if not ok:
      self._show_errors(errs, "解包"); return False
    try:
      for d in sorted(os.listdir(self.current_dir), reverse=True):
        if d.startswith("extracted_"):
          self.extract_dir = os.path.join(self.current_dir, d)
          self.log(" ✓ 镜像已解包", "ok"); return True
    except Exception: pass
    self.log(" ✗ 未找到解包目录", "err"); return False

  def step_enter_fb(self, mode, dev):
    self.log("▸ 步骤 7/10：进入 Fastboot 模式", "neon")
    if mode == "ADB":
      self.log(" ⏳ 正在让手机重启到 Fastboot...", "info")
      self.runner.run_quiet(f"{self.adb} -s {dev} reboot bootloader"); time.sleep(5)
    for i in range(120):
      if self.runner.stop_flag: return False
      if self.runner.run_quiet(f"{self.fb} devices"):
        self.log(" ✓ 已进入 Fastboot 模式", "ok"); return True
      time.sleep(0.5)
      if (i + 1) % 20 == 0: self.log(f" ⏳ 等待中... ({i+1}/120)", "dim")
    self.log(" ✗ 等待超时", "err"); return False

  def step_flash_physical(self):
    self.log("▸ 步骤 8/10：刷入物理分区", "neon")
    if not self.extract_dir:
      self.log(" ✗ 镜像目录不存在", "err"); return False
    base = 0.68; span = 0.10
    valid = [it for it in PHYSICAL if os.path.exists(os.path.join(self.extract_dir, it[1]))]
    vtotal = len(valid)
    for i, (name, fn, args) in enumerate(valid):
      if self.runner.stop_flag: return False
      p = os.path.join(self.extract_dir, fn)
      self.ui(self.set_progress, base + span * (i / max(vtotal, 1)))
      self.ui(self.step_text.configure, text=f"刷入 {name} ({i+1}/{vtotal})", text_color=NEON)
      self.log(f" [{i+1}/{vtotal}] 刷入 {name}...", "info")
      cmd = f'{self.fb} {args} flash {name} "{p}"'
      ok, errs = self._run_step(cmd, f"刷入{name}", timeout=180)
      if not ok:
        self._show_errors(errs, f"刷入{name}"); return False
      self.log(f" ✓ {name}", "ok")
    self.ui(self.set_progress, 0.78); return True

  def step_enter_fbd(self):
    self.log("▸ 步骤 9/10：切换到 Fastbootd 模式", "neon")
    self.log(" ⏳ 正在切换...", "info")
    self.runner.run_quiet(f"{self.fb} reboot fastboot"); time.sleep(3)
    for i in range(90):
      if self.runner.stop_flag: return False
      out = self.runner.run_quiet(f"{self.fb} getvar is-userspace 2>&1")
      if "yes" in out.lower():
        self.log(" ✓ Fastbootd 已就绪", "ok"); return True
      time.sleep(0.5)
    self.log(" ⚠ 未确认进入 Fastbootd，尝试继续", "warn"); return True

  def step_flash_logical(self):
    self.log("▸ 步骤 10/10：刷入逻辑分区", "neon")
    if not self.extract_dir:
      self.log(" ✗ 镜像目录不存在", "err"); return False
    base = 0.80; span = 0.15
    valid = [it for it in LOGICAL if os.path.exists(os.path.join(self.extract_dir, it[1]))]
    vtotal = len(valid)
    for i, (name, fn) in enumerate(valid):
      if self.runner.stop_flag: return False
      p = os.path.join(self.extract_dir, fn)
      self.ui(self.set_progress, base + span * (i / max(vtotal, 1)))
      self.ui(self.step_text.configure, text=f"刷入 {name} ({i+1}/{vtotal})", text_color=NEON)
      self.log(f" [{i+1}/{vtotal}] 刷入 {name}...", "info")
      cmd = f'{self.fb} flash {name} "{p}"'
      ok, errs = self._run_step(cmd, f"刷入{name}", timeout=300)
      if not ok:
        self._show_errors(errs, f"刷入{name}"); return False
      self.log(f" ✓ {name}", "ok")
    self.ui(self.set_progress, 0.95); return True

  def step_wipe(self):
    self.log("▸ 收尾：清空数据并重启", "neon")
    if self.ask_wipe():
      self.log(" ⏳ 正在清空 userdata...", "info")
      self.runner.run_quiet(f"{self.fb} erase userdata", 60)
      self.log(" ✓ userdata 已清空", "ok")
      self.log(" ⏳ 正在清空 metadata...", "info")
      self.runner.run_quiet(f"{self.fb} erase metadata", 60)
      self.log(" ✓ metadata 已清空", "ok")
    else:
      self.log(" ⏭ 已跳过清空数据", "info")
    self.log(" ⏳ 正在重启...", "info")
    self.runner.run_quiet(f"{self.fb} reboot", 30)

  def ask_wipe(self):
    result = [False]
    dlg = ctk.CTkToplevel(self)
    dlg.title("清空数据确认"); dlg.geometry("460x260")
    dlg.configure(fg_color=BG_MAIN); dlg.grab_set(); dlg.attributes("-topmost", True)
    dlg.resizable(False, False); dlg.protocol("WM_DELETE_WINDOW", lambda: dlg.destroy())
    ctk.CTkFrame(dlg, height=3, fg_color=WARN).pack(fill="x")
    ctk.CTkLabel(dlg, text="⚠ WARNING", font=("Consolas", 12, "bold"),
           text_color=WARN).pack(pady=(24, 6))
    ctk.CTkLabel(dlg, text="是否清空用户数据？", font=("Microsoft YaHei UI", 17, "bold"),
           text_color=TEXT_MAIN).pack()
    ctk.CTkLabel(dlg, text="跨版本刷机建议清空，同版本可跳过",
           font=("Microsoft YaHei UI", 11), text_color=TEXT_DIM).pack(pady=(6, 0))
    bf = ctk.CTkFrame(dlg, fg_color="transparent"); bf.pack(pady=28)
    def yes(): result[0] = True; dlg.destroy()
    def no(): result[0] = False; dlg.destroy()
    ctk.CTkButton(bf, text="清空 (推荐)", command=yes, width=150, height=44,
            fg_color="#7f1d1d", hover_color="#a02020", corner_radius=10,
            font=F_BTN_S, border_width=1, border_color=ERR).pack(side="left", padx=10)
    ctk.CTkButton(bf, text="跳过", command=no, width=150, height=44,
            fg_color=BG_CARD, hover_color=BORDER, corner_radius=10,
            font=F_BTN_S, text_color=TEXT_DIM, border_width=1,
            border_color=BORDER).pack(side="left", padx=10)
    self.wait_window(dlg); return result[0]


def main():
  try:
    app = FlashApp()
    app.mainloop()
  except KeyboardInterrupt: pass
  except Exception as e:
    traceback.print_exc()
    try: messagebox.showerror("程序崩溃", f"{e}")
    except Exception: pass


if __name__ == "__main__":
  main()