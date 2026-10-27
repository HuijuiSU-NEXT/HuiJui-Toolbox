# core_api.py
import os
import sys

# 🚨 修复 Nuitka 打包后的路径解析
if getattr(sys, 'frozen', False) or "__compiled__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from core.adb_core import (
  BIN_DIR, ADB, FASTBOOT, CFG, CommandRunner,
  get_active_serial, getprop, is_rooted, list_fastboot_devices, list_adb_devices,
  is_admin, reboot_to_recovery, reboot_to_edl, 
  reboot_from_fastboot_to_fastbootd, reboot_from_fastboot_to_recovery
)
from core.flasher import Flasher, BackupManager, FlashHistory
from core.device_mode import get_device_state
from core.driver_manager import install_driver

CFG.init(os.path.join(BASE_DIR, "huijui_config.json"))
runner = CommandRunner(os.path.join(BASE_DIR, "huijui_debug.log"))
flasher = Flasher(runner)
backup_mgr = BackupManager(BASE_DIR)
history_db = FlashHistory(BASE_DIR)

SCRCPY = os.path.join(BIN_DIR, "scrcpy.exe")

def scan_device_data():
  """执行全模式扫描并返回结果字典 (带强制硬核备用检测)"""
  state = get_device_state()
  res = {"state": state, "brand": "—", "model": "—", "android": "—", "root": "—"}
  
  # 🚨 双保险：如果 get_device_state() 判断为 OFFLINE，强行用底层 adb 再查一次
  if state == "OFFLINE":
      devs = list_adb_devices()
      if devs:
          state = "NORMAL"
          res["state"] = state

  if state == "NORMAL":
    dev = get_active_serial()
    if not dev:
        devs = list_adb_devices()
        dev = devs[0] if devs else None
        
    if dev:
        res["serial"] = dev
        res["brand"] = getprop(dev, "ro.product.brand").upper()
        res["model"] = getprop(dev, "ro.product.model")
        res["android"] = f"Android {getprop(dev, 'ro.build.version.release')}"
        res["root"] = "已 Root" if is_rooted(dev) else "未 Root"
    else:
        res["state"] = "OFFLINE"

  elif state == "FASTBOOT":
    res["brand"] = "Fastboot 模式"
  elif state == "FASTBOOTD":
    res["brand"] = "Fastbootd 模式"
  elif state == "RECOVERY":
    res["brand"] = "Recovery 模式"
  elif state == "SIDELOAD":
    res["brand"] = "Sideload 模式"
  elif state in ("EDL", "BROM"):
    res["brand"] = f"{state} 救砖模式"
    
  return res