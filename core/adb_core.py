import re
import json
import time
import subprocess
import threading
import ctypes
from collections import deque
import os
import sys

if 'HUIJUI_SAFE_DIR' in os.environ:
    BASE_DIR = os.environ['HUIJUI_SAFE_DIR']
elif getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = os.path.join(BASE_DIR, "bin")
ADB = os.path.join(BIN_DIR, "adb.exe")
FASTBOOT = os.path.join(BIN_DIR, "fastboot.exe")
DUMPER = os.path.join(BIN_DIR, "payload-dumper-go.exe")
NO_WINDOW = 0x08000000 if os.name == "nt" else 0

CONFIG_FILE = "huijui_config.json"
DEFAULT_CONFIG = {
    "theme": "dark", "skip_wipe": False, "disable_verity": True, "auto_backup": True,
    "auto_root_patch": True, "dangerous_extra": [], "confirm_dangerous": True,
    "min_battery": 30, "max_temp": 45, "check_firmware_match": True, "check_multi_device": True,
    "theme_color": "#39C5BB", "onboarded": False, "bg_image": "",
    "bg_opacity": 0.3
}

class ConfigManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = dict(DEFAULT_CONFIG)
            cls._instance._path = None
        return cls._instance
    def init(self, path=None):
        self._path = path or os.path.join(BASE_DIR, CONFIG_FILE)
        try:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as f: self._data.update(json.load(f))
        except Exception: pass
    def get(self, k, d=None): return self._data.get(k, d)
    def set(self, k, v, save=True):
        self._data[k] = v
        if save: self.save()
    def save(self):
        try:
            if self._path:
                with open(self._path, "w", encoding="utf-8") as f: json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception: return False

CFG = ConfigManager()

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-zA-Z]")
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

class CommandRunner:
    MAX_LOG_SIZE = 10 * 1024 * 1024
    def __init__(self, debug_path):
        self.debug_path = debug_path; self.stop_flag = False; self._lock = threading.Lock()
    def clear_debug(self):
        with self._lock:
            try:
                if os.path.exists(self.debug_path): os.remove(self.debug_path)
            except Exception: pass
    def append_debug(self, text):
        with self._lock:
            try:
                with open(self.debug_path, "a", encoding="utf-8", errors="ignore") as f: f.write(text + "\n")
            except Exception: pass
    def run(self, cmd, timeout=1800, cwd=None, on_tick=None, on_line=None):
        self.append_debug(f"\n{'='*60}\n[{time.strftime('%H:%M:%S')}] {cmd}\n")
        flags = NO_WINDOW | (subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    cwd=cwd, text=True, encoding="utf-8", errors="ignore", bufsize=1, creationflags=flags)
        except Exception as e: return -1, [f"启动失败: {e}"]
        def _reader():
            try:
                for line in proc.stdout:
                    line = line.rstrip("\r\n")
                    if line:
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
                    try: on_tick(int(time.time() - start))
                    except Exception: pass
                    next_tick += 5
                time.sleep(0.15)
            return proc.returncode, self._extract_errors()
        except Exception as e:
            self._kill_tree(proc); return -1, [f"异常: {e}"]
    def _kill_tree(self, proc):
        try:
            if os.name == "nt": subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True, creationflags=NO_WINDOW)
            else: proc.kill()
        except Exception:
            try: proc.kill()
            except Exception: pass
    def _extract_errors(self):
        errors = deque(maxlen=10)
        try:
            if not os.path.exists(self.debug_path): return list(errors)
            with open(self.debug_path, "rb") as f:
                if os.path.getsize(self.debug_path) > 200*1024: f.seek(-200*1024, 2)
                text = f.read().decode("utf-8", errors="ignore")
            err_re = re.compile(r"(fail|error|invalid|denied|cannot|no such|panic|unsupported|unable|refused|missing|corrupt)", re.I)
            for line in text.splitlines():
                c = CTRL_RE.sub("", ANSI_RE.sub("", line)).strip()
                if c and err_re.search(c) and c not in errors: errors.append(c)
        except Exception: pass
        return list(errors)
    def run_quiet(self, cmd, timeout=15, cwd=None):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout, cwd=cwd, creationflags=NO_WINDOW)
            return ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", errors="ignore").strip()
        except Exception: return ""

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception: return False

def run_cmd(args, cwd=None, timeout=30):
    try:
        p = subprocess.run(args, capture_output=True, text=True, cwd=cwd or BIN_DIR, creationflags=NO_WINDOW, timeout=timeout, errors="ignore")
        return p.stdout.strip(), p.stderr.strip()
    except Exception as e: return "", str(e)

def list_adb_devices():
    out, _ = run_cmd([ADB, "devices"])
    return [line.split("\t")[0] for line in out.splitlines()[1:] if line.strip().endswith("device")]

def get_active_serial():
    devs = list_adb_devices()
    return devs[0] if devs else None

def getprop(dev, prop):
    out, _ = run_cmd([ADB, "-s", dev, "shell", "getprop", prop])
    return out.strip()

def shell(dev, cmd, timeout=30): return run_cmd([ADB, "-s", dev, "shell", cmd], timeout=timeout)
def is_rooted(dev): return "uid=0" in shell(dev, "su -c id")[0]
def get_slot(dev):
    s = shell(dev, "getprop ro.boot.slot_suffix")[0].strip().lstrip("_")
    return s if s in ("a", "b") else ""

def probe_partition(dev, part, slot=""):
    candidates = []
    if slot: candidates += [f"/dev/block/bootdevice/by-name/{part}_{slot}", f"/dev/block/by-name/{part}_{slot}"]
    candidates += [f"/dev/block/bootdevice/by-name/{part}", f"/dev/block/by-name/{part}"]
    for p in candidates:
        out, _ = shell(dev, f"ls {p} 2>/dev/null")
        if out and "No such" not in out: return p
    return None

def reboot_to_bootloader(dev): return run_cmd([ADB, "-s", dev, "reboot", "bootloader"])
def reboot_to_fastbootd(dev): return run_cmd([ADB, "-s", dev, "reboot", "fastboot"])
def reboot_system(dev): return run_cmd([ADB, "-s", dev, "reboot"])
def reboot_to_recovery(dev): return run_cmd([ADB, "-s", dev, "reboot", "recovery"])
def reboot_to_edl(dev): return run_cmd([ADB, "-s", dev, "reboot", "edl"])
def reboot_from_fastboot_to_fastbootd(): return run_cmd([FASTBOOT, "reboot", "fastboot"])
def reboot_from_fastboot_to_recovery(): return run_cmd([FASTBOOT, "reboot", "recovery"])

def list_fastboot_devices():
    out, _ = run_cmd([FASTBOOT, "devices"])
    return [line.split("\t")[0] for line in out.splitlines() if line.strip()]

def fastboot_flash(part, img_path, timeout=180): return run_cmd([FASTBOOT, "flash", part, img_path], timeout=timeout)
def fastboot_reboot(target="system"): return run_cmd([FASTBOOT, "reboot", target])
def is_fastbootd(): return "yes" in run_cmd([FASTBOOT, "getvar", "is-userspace"])[0].lower()