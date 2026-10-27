# core/device_mode.py
import subprocess
try:
  import wmi
  HAS_WMI = True
except ImportError:
  HAS_WMI = False
from .adb_core import ADB, FASTBOOT, NO_WINDOW

def get_device_state():
  # 1. 检查 ADB
  try:
    out = subprocess.check_output([ADB, "devices"], text=True, creationflags=NO_WINDOW, timeout=5)
    for line in out.splitlines()[1:]:
      parts = line.split()
      if len(parts) >= 2:
        state = parts[1]
        if state == "device": return "NORMAL"
        elif state == "recovery": return "RECOVERY"
        elif state == "sideload": return "SIDELOAD"
  except Exception: pass

  # 2. 检查 Fastboot
  try:
    out = subprocess.check_output([FASTBOOT, "devices"], text=True, creationflags=NO_WINDOW, timeout=5)
    if "fastboot" in out.lower():
      out_var = subprocess.check_output([FASTBOOT, "getvar", "is-userspace"], stderr=subprocess.STDOUT, text=True, creationflags=NO_WINDOW, timeout=5)
      return "FASTBOOTD" if "yes" in out_var.lower() else "FASTBOOT"
  except Exception: pass

  # 3. 检查硬件层 EDL/BROM (WMI)
  if HAS_WMI:
    try:
      c = wmi.WMI()
      for usb in c.Win32_PnPEntity():
        name = usb.Name or ""
        if "9008" in name or "QDLoader" in name: return "EDL"
        if "MTK" in name and ("VCOM" in name or "BROM" in name): return "BROM"
    except Exception: pass

  return "OFFLINE"