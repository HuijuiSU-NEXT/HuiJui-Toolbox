import os, subprocess, ctypes
from .adb_core import BIN_DIR, NO_WINDOW

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception: return False

def check_driver_installed(keyword="Android"):
    try:
        out = subprocess.check_output("pnputil /enum-drivers", shell=True, text=True, creationflags=NO_WINDOW, timeout=10)
        return keyword.lower() in out.lower()
    except Exception: return False

def install_driver(inf_filename):
    if not is_admin(): return False, "需要管理员权限"
    inf_path = os.path.join(BIN_DIR, inf_filename)
    if not os.path.exists(inf_path): return False, f"不存在: {inf_filename}"
    try:
        cmd = f'pnputil /add-driver "{inf_path}" /install'
        out = subprocess.check_output(cmd, shell=True, text=True, creationflags=NO_WINDOW, timeout=30)
        return True, out
    except subprocess.CalledProcessError as e: return False, e.output
