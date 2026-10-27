# core/temp_root_manager.py
# HuiJui Core · 临时 Root 管理器 (免解锁 / LKM late-load / OTA 回退)

import os
import re
import sys
import zipfile
import shutil
import threading
import urllib.request
from core.adb_core import (
  BASE_DIR, BIN_DIR, ADB, DUMPER, NO_WINDOW,
  run_cmd, get_active_serial, shell, is_rooted
)

TEMP_ROOT_ROOT = os.path.join(BIN_DIR, "temp_root")

# ================= KMI 解析 =================
def get_device_kmi(dev):
  """从 uname -r 解析 KMI，例如 'android12-5.10'"""
  out, _ = shell(dev, "uname -r")
  kernel_ver = out.strip()
  if not kernel_ver:
    return None
  m = re.search(r"(\d+\.\d+).*?-android(\d+)", kernel_ver)
  if m:
    major_minor = m.group(1)
    android_ver = m.group(2)
    return f"android{android_ver}-{major_minor}"
  m2 = re.search(r"(\d+)\.(\d+)\.\d+.*android(\d+)", kernel_ver)
  if m2:
    return f"android{m2.group(3)}-{m2.group(1)}.{m2.group(2)}"
  return None

# ================= 设备支持检测 =================
def check_device_support(dev, supported_profiles=None):
  if supported_profiles is None:
    supported_profiles = []

  model = shell(dev, "getprop ro.product.device")[0].strip()
  brand = shell(dev, "getprop ro.product.brand")[0].strip()
  kernel = shell(dev, "uname -r")[0].strip()
  kmi = get_device_kmi(dev)

  info = {
    "model": model,
    "brand": brand,
    "kernel": kernel,
    "kmi": kmi or "未知",
    "supported": False,
    "reason": ""
  }

  if not kmi:
    info["reason"] = "无法解析内核 KMI，可能不是 GKI 设备"
    return False, info

  for p in supported_profiles:
    if p.get("model", "").lower() == model.lower() and p.get("kmi", "").lower() == kmi.lower():
      info["supported"] = True
      info["payload_dir"] = os.path.join(TEMP_ROOT_ROOT, model.lower(), kmi)
      return True, info

  payload_dir = os.path.join(TEMP_ROOT_ROOT, model.lower(), kmi)
  if os.path.isdir(payload_dir):
    info["supported"] = True
    info["payload_dir"] = payload_dir
    return True, info

  info["reason"] = f"型号 [{model}] + KMI [{kmi}] 不在支持列表，且未找到预置 Payload"
  return False, info

# ================= OTA 回退：解析 OTA 提取 boot =================
def parse_ota_for_kmi(ota_path_or_url, log_cb=print):
  work_dir = os.path.join(BASE_DIR, "temp_ota_work")
  if os.path.exists(work_dir):
    shutil.rmtree(work_dir, ignore_errors=True)
  os.makedirs(work_dir, exist_ok=True)

  local_zip = ota_path_or_url
  if ota_path_or_url.startswith("http://") or ota_path_or_url.startswith("https://"):
    local_zip = os.path.join(work_dir, "ota.zip")
    log_cb(f"📥 正在下载 OTA: {ota_path_or_url[:60]}...")
    try:
      urllib.request.urlretrieve(ota_path_or_url, local_zip)
      log_cb("✅ OTA 下载完成")
    except Exception as e:
      log_cb(f"❌ OTA 下载失败: {e}")
      return None, None, None

  if not os.path.isfile(local_zip):
    log_cb(f"❌ OTA 文件不存在: {local_zip}")
    return None, None, None

  log_cb("▸ 解压 payload.bin...")
  try:
    with zipfile.ZipFile(local_zip) as z:
      payload_candidates = [n for n in z.namelist() if n.endswith("payload.bin")]
      if not payload_candidates:
        log_cb("❌ OTA 内未找到 payload.bin")
        return None, None, None
      payload_name = payload_candidates[0]
      z.extract(payload_name, work_dir)
      payload_path = os.path.join(work_dir, payload_name)
      if os.path.dirname(payload_path) != work_dir:
        dst = os.path.join(work_dir, "payload.bin")
        shutil.move(payload_path, dst)
        payload_path = dst
  except Exception as e:
    log_cb(f"❌ 解压 payload 失败: {e}")
    return None, None, None

  log_cb("▸ 解包 boot / init_boot...")
  extract_dir = os.path.join(work_dir, "extracted")
  os.makedirs(extract_dir, exist_ok=True)
  cmd = f'"{DUMPER}" -q -p boot,init_boot -o "{extract_dir}" payload.bin'
  rc, errs = run_cmd(cmd, cwd=work_dir, timeout=1800)[0], ""
  if isinstance(rc, tuple):
    rc, errs = rc

  if rc != 0:
    log_cb(f"⚠️ payload-dumper-go 返回码 {rc}，尝试全量解包...")
    run_cmd(f'"{DUMPER}" -q payload.bin', cwd=work_dir, timeout=1800)

  boot_path = None
  init_boot_path = None
  kmi_guess = None
  for root, _, files in os.walk(work_dir):
    for f in files:
      if f == "boot.img":
        boot_path = os.path.join(root, f)
      elif f == "init_boot.img":
        init_boot_path = os.path.join(root, f)

  if boot_path:
    log_cb("▸ 尝试从 boot.img 识别 KMI...")
    kmi_guess = _guess_kmi_from_img(boot_path)
    if kmi_guess:
      log_cb(f" 🔍 推断 KMI: {kmi_guess}")

  return boot_path, init_boot_path, kmi_guess

def _guess_kmi_from_img(img_path):
  try:
    with open(img_path, "rb") as f:
      data = f.read(2 * 1024 * 1024)
    text = data.decode("utf-8", errors="ignore")
    m = re.search(r"(\d+\.\d+\.\d+)[-_]android(\d+)", text)
    if m:
      return f"android{m.group(2)}-{m.group(1).rsplit('.', 1)[0]}"
  except Exception:
    pass
  return None

# ================= 执行临时 Root =================
def execute_temp_root(dev, payload_dir, log_cb=print):
  log_cb(f"▸ 使用 Payload 目录: {payload_dir}")
  required = ["exploit", "ksud"]
  optional = ["kernelsu.ko", "su", "libksud.so"]
  found = {}
  for f in required + optional:
    p = os.path.join(payload_dir, f)
    if os.path.exists(p):
      found[f] = p
  for f in required:
    if f not in found:
      log_cb(f"❌ 缺少必要文件: {f}")
      return False

  remote_dir = "/data/local/tmp"
  log_cb("▸ 推送文件到设备...")
  for name, local_path in found.items():
    remote_path = f"{remote_dir}/{name}"
    run_cmd([ADB, "-s", dev, "push", local_path, remote_path], timeout=60)
  shell(dev, f"chmod 755 {remote_dir}/exploit {remote_dir}/ksud")

  log_cb("▸ 执行漏洞利用 (exploit)...")
  out, err = shell(dev, f"{remote_dir}/exploit", timeout=120)
  if out.strip():
    log_cb(f" exploit 输出: {out.strip()[:200]}")

  probe, _ = shell(dev, "su -c id")
  if "uid=0" not in probe:
    log_cb("⚠️ exploit 执行后未直接获得 uid=0，继续尝试 late-load...")

  kmi = get_device_kmi(dev)
  log_cb(f"▸ 加载 KernelSU LKM (KMI: {kmi})...")
  if "libksud.so" in found:
    cmd = f'{remote_dir}/ksud late-load --kmi {kmi}'
  else:
    cmd = f'{remote_dir}/ksud late-load --kmi {kmi}'
  out, err = shell(dev, cmd, timeout=120)
  if err and "error" in err.lower():
    log_cb(f"⚠️ ksud late-load 输出: {err[:200]}")

  log_cb("▸ 初始化 KernelSU 环境...")
  for stage in ["post-fs-data", "services", "boot-completed"]:
    shell(dev, f"{remote_dir}/ksud {stage}", timeout=60)

  log_cb("▸ 验证 Root 状态...")
  final_out, _ = shell(dev, "su -c id")
  if "uid=0" in final_out:
    log_cb("✅ 临时 Root 获取成功！重启后自动失效。")
    return True
  else:
    log_cb(f"❌ Root 验证失败 (su -c id → {final_out.strip()[:100]})")
    return False