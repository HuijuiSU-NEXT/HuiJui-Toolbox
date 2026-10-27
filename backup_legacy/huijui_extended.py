# -*- coding: utf-8 -*-
"""
Huijui 工具箱 · 扩展工具库 v5.2 (Extended)
功能：30+ 项底层扩展，包含 8 个全新实用工具
作者：喜羊羊灰灰菜單
说明：本文件被 huijui_toolbox.py 主程序调用，所有操作均异步安全，统一使用主程序的 Runner 打印日志。
"""

import os
import re
import subprocess
import time
import shutil
import zipfile
import hashlib
import json
from datetime import datetime

# 兼容无窗口模式
def _safe_flag():
  return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

# 设备模式图标
MODE_ICONS = {
  "ADB": "🔌", "Sideload": "📥", "Recovery": "🛠",
  "Fastboot": "⚡", "Fastbootd": "🚀",
  "EDL": "💠", "BROM": "🧩", "Odin": "🔷", "DFU": "🍎",
  "MTP": "📁", "Offline": "⚫",
}

class ModeDetector:
  """设备全模式检测器（修复：自动识别底层 USB VID/PID 和 ADB 状态）"""
  def __init__(self, adb, fb, runner):
    self.adb = adb
    self.fb = fb
    self.runner = runner

  def _usb_devices(self):
    try:
      cmd = 'powershell -NoProfile -Command "Get-PnpDevice -PresentOnly | Where-Object {$_.InstanceId -like \'USB*\'} | Select-Object -ExpandProperty InstanceId"'
      out = self.runner.run_quiet(cmd, timeout=8)
      return out.upper()
    except Exception:
      return ""

  def _vid_pid_scan(self):
    s = self._usb_devices()
    hits = set()
    # 高通 EDL
    if re.search(r"VID_05C6&PID_9008", s) or "QDLOADER" in s: hits.add("EDL")
    if re.search(r"VID_05C6&PID_900E", s): hits.add("EDL")
    # 联发科 BROM
    if re.search(r"VID_0E8D&PID_0003", s) or "MTK_USB" in s: hits.add("BROM")
    # 三星 Odin
    if re.search(r"VID_04E8&PID_685D", s) or "SAMSUNG_MOBILE" in s: hits.add("Odin")
    # 苹果 DFU
    if re.search(r"VID_05AC&PID_1227", s) or "APPLE_MOBILE_DEVICE" in s: hits.add("DFU")
    return hits

  def _adb_devices(self):
    out = self.runner.run_quiet(f"{self.adb} devices")
    return [ln.split("\t")[0] for ln in out.splitlines()[1:] if "\t" in ln]

  def _fb_devices(self):
    out = self.runner.run_quiet(f"{self.fb} devices")
    return [ln.split()[0] for ln in out.splitlines() if ln.strip() and "fastboot" in ln.lower()]

  def _adb_state(self):
    out = self.runner.run_quiet(f"{self.adb} get-state")
    return out.strip() if out else None

  def _fb_is_userspace(self):
    out = self.runner.run_quiet(f"{self.fb} getvar is-userspace 2>&1")
    return "yes" in out.lower()

  def detect(self):
    # 优先检测 Fastboot / Fastbootd
    fbv = self._fb_devices()
    if fbv:
      serial = fbv[0]
      if self._fb_is_userspace():
        return "Fastbootd", serial, {}
      return "Fastboot", serial, {}

    # 检测 ADB 系列
    adb_list = self._adb_devices()
    if adb_list:
      serial = adb_list[0]
      state = self._adb_state() or ""
      if state == "sideload":
        return "Sideload", serial, {"state": state}
      if state == "recovery":
        return "Recovery", serial, {"state": state}
      if state == "device":
        bm = self.runner.run_quiet(f"{self.adb} -s {serial} shell getprop ro.bootmode")
        if "recovery" in bm.lower():
          return "Recovery", serial, {"state": "recovery"}
        return "ADB", serial, {"state": state}
      if state == "unauthorized":
        return "ADB", serial, {"state": "unauthorized"}
      if state == "offline":
        return "Offline", serial, {"state": state}

    # 检测底层 USB 模式
    hits = self._vid_pid_scan()
    for k in ("EDL", "BROM", "Odin", "DFU"):
      if k in hits:
        return k, "", {}
    return "Offline", "", {}

  def describe(self, mode):
    desc = {
      "ADB":    "ADB 正常模式",
      "Sideload": "ADB Sideload（Recovery 下刷 OTA/ROM）",
      "Recovery": "Recovery 模式",
      "Fastboot": "Fastboot 引导模式（物理分区）",
      "Fastbootd": "Fastbootd 用户空间（逻辑分区）",
      "EDL":    "高通 9008/EDL（需 QFIL）",
      "BROM":   "联发科 BROM（需 SP Flash Tool）",
      "Odin":   "三星 Download（需 Odin）",
      "DFU":    "Apple DFU（需 iTunes）",
      "MTP":    "MTP 文件传输",
      "Offline":  "无设备连接",
    }
    return desc.get(mode, "未知模式")


class ExtendedTools:
  """扩展功能集（30+ 功能 + 8 个全新实用工具）"""
  def __init__(self, adb, fb, runner, log_cb, ui_cb, work_dir):
    self.adb = adb
    self.fb = fb
    self.runner = runner
    self.log = log_cb
    self.ui = ui_cb
    self.work_dir = work_dir

  # ================= 基础私有方法 =================
  def _get_adb_dev(self):
    out = self.runner.run_quiet(f"{self.adb} devices")
    for ln in out.splitlines()[1:]:
      if "\tdevice" in ln: return ln.split("\t")[0]
    return None

  def _get_fb_dev(self):
    out = self.runner.run_quiet(f"{self.fb} devices")
    for ln in out.splitlines():
      if "fastboot" in ln.lower(): return ln.split()[0]
    return None

  def _p(self, path):
    return f'"{path}"' if path else ""

  # ================= 1. 基础设备扩展（6项） =================
  
  def logcat_dump(self, lines=2000):
    """抓取 logcat 日志"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    self.log(f"📜 抓取 logcat（{lines} 行）...", "info")
    out = self.runner.run_quiet(f"{self.adb} -s {dev} logcat -d -t {lines}", timeout=60)
    if out:
      fn = f"logcat_{time.strftime('%Y%m%d_%H%M%S')}.txt"
      with open(os.path.join(self.work_dir, fn), "w", encoding="utf-8") as f:
        f.write(out)
      self.log(f" ✓ 已保存: {fn}", "ok")

  def bugreport_dump(self):
    """生成 bugreport.zip"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    self.log("🐞 生成 bugreport（可能需 1-3 分钟）...", "info")
    fn = f"bugreport_{time.strftime('%Y%m%d_%H%M%S')}.zip"
    out = self.runner.run_quiet(f'{self.adb} -s {dev} bugreport "{os.path.join(self.work_dir, fn)}"', timeout=300)
    if os.path.exists(os.path.join(self.work_dir, fn)):
      self.log(f" ✓ 已保存: {fn}", "ok")
    else:
      self.log(" ✗ 失败", "err")

  def list_packages(self, keyword="", system=False):
    """列出已安装应用（支持过滤）"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    flag = "-s" if system else "-3"
    out = self.runner.run_quiet(f"{self.adb} -s {dev} shell pm list packages {flag}")
    pkgs = [ln.replace("package:", "").strip() for ln in out.splitlines() if ln.startswith("package:")]
    if keyword:
      pkgs = [p for p in pkgs if keyword.lower() in p.lower()]
    self.log(f"📦 找到 {len(pkgs)} 个应用", "info")
    for p in pkgs[:60]: self.log(f"  {p}", "white")
    return pkgs

  def uninstall_app(self, pkg, keep_data=False):
    """卸载应用（-k 保留数据）"""
    dev = self._get_adb_dev()
    if not dev: return False
    flag = "-k" if keep_data else ""
    out = self.runner.run_quiet(f"{self.adb} -s {dev} shell pm uninstall {flag} {pkg}")
    ok = "Success" in out
    self.log(f" {'✓ 卸载成功' if ok else '✗ 卸载失败'}: {pkg}", "ok" if ok else "err")
    return ok

  def grant_permission(self, pkg, permission, grant=True):
    """授予/撤销应用权限"""
    dev = self._get_adb_dev()
    if not dev: return False
    sub = "grant" if grant else "revoke"
    self.runner.run_quiet(f"{self.adb} -s {dev} shell pm {sub} {pkg} {permission}")
    self.log(f" ✓ {sub} {permission} 到 {pkg}", "ok")
    return True

  def set_prop(self, key, value):
    """设置系统属性（需要 Root）"""
    dev = self._get_adb_dev()
    if not dev: return False
    self.runner.run_quiet(f'{self.adb} -s {dev} shell "su -c \'setprop {key} {value}\'"')
    self.log(f" ✓ setprop {key}={value}", "ok")
    return True

  # ================= 2. 文件管理扩展（5项） =================

  def push_file(self, local, remote="/sdcard/"):
    """推送文件到设备"""
    dev = self._get_adb_dev()
    if not dev or not os.path.exists(local):
      self.log("✗ 未检测到设备或文件不存在", "err"); return False
    self.log(f"📤 push: {os.path.basename(local)} → {remote}", "info")
    self.runner.run_quiet(f'{self.adb} -s {dev} push {self._p(local)} "{remote}"', timeout=600)
    self.log(" ✓ 推送完成", "ok")
    return True

  def pull_file(self, remote, local_dir=None):
    """从设备拉取文件"""
    dev = self._get_adb_dev()
    if not dev: return False
    local_dir = local_dir or self.work_dir
    self.log(f"📥 pull: {remote} → {local_dir}", "info")
    self.runner.run_quiet(f'{self.adb} -s {dev} pull "{remote}" {self._p(local_dir)}', timeout=600)
    self.log(" ✓ 拉取完成", "ok")
    return True

  def batch_pull_apks(self, output_dir=None):
    """【新工具】一键批量提取所有用户安装的 APK"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    output_dir = output_dir or os.path.join(self.work_dir, "Extracted_APKs")
    os.makedirs(output_dir, exist_ok=True)
    
    self.log("🚀 开始批量提取用户 APK...", "neon")
    pkgs = self.list_packages(system=False)
    count = 0
    for pkg in pkgs:
      out = self.runner.run_quiet(f"{self.adb} -s {dev} shell pm path {pkg}")
      path = out.replace("package:", "").strip()
      if path:
        fn = f"{pkg}.apk"
        self.runner.run_quiet(f'{self.adb} -s {dev} pull "{path}" {self._p(os.path.join(output_dir, fn))}', timeout=120)
        self.log(f" ✓ 提取: {fn}", "ok")
        count += 1
    self.log(f"🎉 提取完成，共 {count} 个 APK，保存在: {output_dir}", "purple")

  def screencap_to_pc(self, save_dir=None):
    """屏幕截图并保存到电脑"""
    dev = self._get_adb_dev()
    if not dev: return False
    save_dir = save_dir or self.work_dir
    fn = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    p = os.path.join(save_dir, fn)
    try:
      with open(p, "wb") as f:
        subprocess.run(f"{self.adb} -s {dev} exec-out screencap -p", shell=True, stdout=f, timeout=30, creationflags=_safe_flag())
      if os.path.getsize(p) > 1024:
        self.log(f" ✓ 截图保存: {fn}", "ok")
        os.startfile(p)
        return True
    except Exception as e:
      self.log(f" ✗ 截图失败: {e}", "err")
    return False

  def record_screen(self, duration=180, save_dir=None):
    """录屏"""
    dev = self._get_adb_dev()
    if not dev: return False
    save_dir = save_dir or self.work_dir
    fn = f"record_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
    p = os.path.join(save_dir, fn)
    self.log(f"🎬 录制 {duration} 秒...", "info")
    try:
      with open(p, "wb") as f:
        subprocess.run(f"{self.adb} -s {dev} exec-out screenrecord --time-limit {duration} -", shell=True, stdout=f, timeout=duration+30, creationflags=_safe_flag())
      if os.path.getsize(p) > 1024:
        self.log(f" ✓ 录屏保存: {fn}", "ok")
        return True
    except Exception as e:
      self.log(f" ✗ 录屏失败: {e}", "err")
    return False

  # ================= 3. Fastboot 自动化扩展（6项） =================

  def fb_all_vars(self):
    """获取所有 Fastboot 变量"""
    self.log("📋 读取全部 fastboot 变量...", "info")
    out = self.runner.run_quiet(f"{self.fb} getvar all 2>&1", timeout=20)
    vars_dict = {}
    for ln in out.splitlines():
      m = re.match(r"\(bootloader\)\s*(\S+):\s*(.*)", ln)
      if m: vars_dict[m.group(1)] = m.group(2)
    for k, v in vars_dict.items(): self.log(f"  {k} = {v}", "white")
    return vars_dict

  def fb_unlock(self):
    """解锁 BL"""
    self.log("🔓 解锁 Bootloader...", "warn")
    out = self.runner.run_quiet(f"{self.fb} flashing unlock", timeout=30)
    self.log(f" {out[:200]}", "ok" if "FAILED" not in out else "err")

  def fb_erase(self, partition):
    """擦除分区"""
    self.log(f"🧹 擦除 {partition}...", "warn")
    out = self.runner.run_quiet(f"{self.fb} erase {partition}", timeout=60)
    self.log(f" {out[:200]}", "ok" if "OKAY" in out or "Finished" in out else "err")

  def fb_flash_single(self, partition, img_path):
    """刷入单个分区镜像"""
    if not os.path.exists(img_path): return self.log(f"✗ 镜像不存在: {img_path}", "err")
    self.log(f"⚡ 刷入 {partition} ← {os.path.basename(img_path)}", "info")
    out = self.runner.run_quiet(f'{self.fb} flash {partition} {self._p(img_path)}', timeout=300)
    ok = "OKAY" in out or "finished" in out.lower()
    self.log(f" {'✓' if ok else '✗'} 刷入完成", "ok" if ok else "err")
    return ok

  def fb_boot(self, img_path):
    """临时启动镜像（不刷入）"""
    if not os.path.exists(img_path): return self.log(f"✗ 镜像不存在", "err")
    self.log(f"🚀 fastboot boot {os.path.basename(img_path)}...", "info")
    out = self.runner.run_quiet(f'{self.fb} boot {self._p(img_path)}', timeout=120)
    self.log(f" {out[:200]}", "info")

  def ab_slot_switch(self, target_slot):
    """切换 A/B 槽位"""
    self.log(f"🔀 切换槽位 {target_slot}...", "warn")
    self.runner.run_quiet(f"{self.fb} set_active {target_slot}")
    self.runner.run_quiet(f"{self.fb} reboot")
    self.log(" ✓ 已切换并重启", "ok")

  # ================= 4. 镜像与高级工具（6项） =================

  def extract_device_tree(self, out_dir=None):
    """提取设备树信息"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    out_dir = out_dir or os.path.join(self.work_dir, f"devtree_{time.strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(out_dir, exist_ok=True)
    for p in ["/vendor/etc/fstab.*", "/system/etc/fstab.*"]:
      out = self.runner.run_quiet(f'{self.adb} -s {dev} shell "ls {p} 2>/dev/null"', timeout=15)
      for f in out.splitlines():
        fn = os.path.basename(f.strip())
        if fn: self.runner.run_quiet(f'{self.adb} -s {dev} pull "{f.strip()}" {self._p(out_dir)}')
    self.log(f" ✓ 设备树提取完成: {out_dir}", "ok")

  def sha256_check(self, path):
    """计算文件 SHA256"""
    if not os.path.exists(path): return self.log("✗ 文件不存在", "err")
    h = hashlib.sha256()
    with open(path, "rb") as f:
      for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    self.log(f" ✓ SHA256: {h.hexdigest()}", "ok")
    return h.hexdigest()

  def img_magic(self, path):
    """分析镜像文件头"""
    if not os.path.exists(path): return self.log("✗ 文件不存在", "err")
    with open(path, "rb") as f: head = f.read(16)
    magic_map = {
      b"ANDROID!": "Android Boot Image",
      b"\x53\xEF": "ext4 文件系统",
      b"\x4D\x5A": "Windows PE 文件",
      b"PK\x03\x04": "ZIP / APK / OTA",
      b"CrAU": "ChromeOS/Android payload",
    }
    for k, v in magic_map.items():
      if head.startswith(k):
        self.log(f" ✓ 识别为: {v}", "ok")
        return v
    self.log(f" ? 未知文件头: {head[:8].hex()}", "warn")

  def deep_device_info(self):
    """【新工具】深度检测设备硬件信息（内存、存储、电池健康等）"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    self.log("🔬 深度检测设备信息...", "neon")
    
    props = {
      "CPU架构": "ro.product.cpu.abi",
      "设备代号": "ro.product.device",
      "编译版本": "ro.build.display.id",
      "内存大小": "ro.product.memory",
    }
    for label, prop in props.items():
      v = self.runner.run_quiet(f"{self.adb} -s {dev} shell getprop {prop}")
      self.log(f"  {label}: {v}", "white")
      
    # 电池健康
    battery = self.runner.run_quiet(f"{self.adb} -s {dev} shell dumpsys battery")
    health = re.search(r"health:\s*(\d+)", battery)
    temp = re.search(r"temperature:\s*(\d+)", battery)
    level = re.search(r"level:\s*(\d+)", battery)
    if health: self.log(f"  电池健康状态码: {health.group(1)} (2=良好)", "white")
    if temp: self.log(f"  电池温度: {int(temp.group(1))/10:.1f}°C", "white")
    if level: self.log(f"  当前电量: {level.group(1)}%", "white")

  def compare_firmware(self, zip_a, zip_b):
    """【新工具】比较两个卡刷包的版本差异"""
    def _read_pp(z):
      try:
        with zipfile.ZipFile(z) as zf:
          if "payload_properties.txt" not in zf.namelist(): return ""
          return zf.read("payload_properties.txt").decode("utf-8", "ignore")
      except Exception: return ""
    a, b = _read_pp(zip_a), _read_pp(zip_b)
    keys = ["post-build", "post-sdk-level", "post-security-patch-level"]
    self.log("🆚 固件版本差异对比:", "purple")
    for k in keys:
      va = re.search(rf"{k}[=:]\s*(\S+)", a)
      vb = re.search(rf"{k}[=:]\s*(\S+)", b)
      va = va.group(1) if va else "?"
      vb = vb.group(1) if vb else "?"
      self.log(f"  {k:30} {va} {'==' if va==vb else '!='} {vb}", "white" if va==vb else "warn")

  # ================= 5. 救援与清理（7项） =================

  def backup_partitions(self, partitions, out_dir=None):
    """【新工具】一键批量备份设备分区（如 boot, init_boot 等）"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    out_dir = out_dir or os.path.join(self.work_dir, f"backup_{time.strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(out_dir, exist_ok=True)
    self.log(f"💾 批量备份分区到: {out_dir}", "purple")
    for part in partitions:
      remote = f"/sdcard/{part}.img"
      self.log(f" 正在备份 {part}...", "info")
      self.runner.run_quiet(f'{self.adb} -s {dev} shell "su -c \'dd if=/dev/block/by-name/{part} of={remote}\'"', timeout=300)
      self.runner.run_quiet(f'{self.adb} -s {dev} pull {remote} {self._p(os.path.join(out_dir, f"{part}.img"))}', timeout=300)
      self.runner.run_quiet(f"{self.adb} -s {dev} shell rm {remote}")
      self.log(f" ✓ {part} 备份完成", "ok")

  def disable_bloatware(self, pkg_list):
    """【新工具】一键禁用/卸载预设膨胀软件"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 未检测到设备", "err")
    self.log("🧹 开始清理预装应用...", "warn")
    for pkg in pkg_list:
      self.runner.run_quiet(f"{self.adb} -s {dev} shell pm disable-user --user 0 {pkg}")
      self.log(f" ✓ 已禁用: {pkg}", "ok")

  def cleanup_temp(self):
    """清理工作目录下的临时文件"""
    removed, freed = 0, 0
    for name in os.listdir(self.work_dir):
      p = os.path.join(self.work_dir, name)
      if name == "payload.bin" or name.startswith("extracted_"):
        try:
          if os.path.isdir(p):
            freed += sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs)
            shutil.rmtree(p)
          else:
            freed += os.path.getsize(p); os.remove(p)
          removed += 1
        except Exception: pass
    self.log(f"🧹 清理 {removed} 项，释放 {freed/1024/1024:.1f} MB", "ok")

  def analyze_log(self, log_path):
    """分析日志文件中的错误"""
    if not os.path.exists(log_path): return self.log("✗ 日志文件不存在", "err")
    keywords = {"ERROR": "错误", "FAILED": "失败", "TIMEOUT": "超时", "denied": "拒绝", "corrupt": "损坏"}
    counts = {}
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
      for ln in f:
        for k in keywords:
          if k.lower() in ln.lower(): counts[k] = counts.get(k, 0) + 1
    self.log("📊 日志分析报告:", "purple")
    for k, n in sorted(counts.items(), key=lambda x: -x[1]):
      self.log(f"  {keywords[k]:<6} × {n}", "warn")

  def edl_qfil_hint(self):
    """EDL 救援指引"""
    self.log("💠 高通 9008/EDL 模式已检测", "purple")
    self.log(" 请使用 Qualcomm QFIL 或 QDL 工具加载 prog_firehose_*.elf", "white")
    self.log(" 镜像目录需包含: rawprogram*.xml, patch*.xml, *.img", "white")
    self.log(" ⚠ EDL 刷机会完全擦除设备，请谨慎操作", "warn")

  def brom_spflash_hint(self):
    """BROM 救援指引"""
    self.log("🧩 联发科 BROM 已检测", "purple")
    self.log(" 请使用 SP Flash Tool + MTK_AllInOne_DA.bin", "white")
    self.log(" scatter 文件可从原厂固件 zip 中提取", "white")

  def auto_wireless_adb(self):
    """【新工具】一键开启无线 ADB 并自动连接"""
    dev = self._get_adb_dev()
    if not dev: return self.log("✗ 请先用 USB 连接设备", "err")
    self.log("📡 正在开启无线 ADB...", "info")
    self.runner.run_quiet(f"{self.adb} -s {dev} tcpip 5555")
    time.sleep(2)
    routes = self.runner.run_quiet(f"{self.adb} -s {dev} shell ip route")
    m = re.search(r"src (\d+\.\d+\.\d+\.\d+)", routes)
    if m:
      ip = m.group(1)
      self.log(f" 📶 手机 IP: {ip}:5555，正在尝试连接...", "info")
      out = self.runner.run_quiet(f"{self.adb} connect {ip}:5555")
      if "connected" in out.lower():
        self.log(f" ✓ 无线连接成功！可以拔掉数据线了", "ok")
      else:
        self.log(f" ✗ 连接失败，请检查与电脑是否在同一 WiFi", "err")
    else:
      self.log(" ✗ 无法获取手机 WiFi IP，请确保手机已连接 WiFi", "err")

  # ================= 6. 镜像高级处理（新工具） =================

  def extract_single_image(self, zip_path, target_partition="boot"):
    """【新工具】从卡刷包中单独提取某个分区镜像（如只提 boot.img）"""
    self.log(f"🔍 正在从卡刷包单独提取 {target_partition}.img...", "info")
    try:
      # 先提取 payload.bin
      with zipfile.ZipFile(zip_path, 'r') as z:
        if "payload.bin" not in z.namelist():
          self.log(" ✗ 卡刷包内无 payload.bin", "err"); return
        z.extract("payload.bin", self.work_dir)
      
      # 使用 payload-dumper-go 单提
      pp = os.path.join(self.work_dir, "payload.bin")
      dumper = os.path.join(os.path.dirname(self.adb), "payload-dumper-go.exe") # 尝试获取 dumper 路径
      cmd = f'"{dumper}" -p {target_partition} payload.bin'
      self.runner.run(cmd, timeout=600, cwd=self.work_dir, on_line=lambda l: self.log(f"  {l}", "dim"))
      self.log(f" ✓ {target_partition}.img 提取完成！", "ok")
    except Exception as e:
      self.log(f" ✗ 提取失败: {e}", "err")

  def parse_boot_image(self, img_path):
    """【新工具】解析 Boot 镜像头信息（Kernel、Ramdisk 等）"""
    if not os.path.exists(img_path): return self.log("✗ 文件不存在", "err")
    with open(img_path, "rb") as f: data = f.read(64)
    if not data.startswith(b"ANDROID!"):
      return self.log(" ⚠ 不是标准的 Android Boot Image", "warn")
    kernel_size = int.from_bytes(data[8:12], "little")
    ramdisk_size = int.from_bytes(data[16:20], "little")
    self.log(f" ✓ 解析成功:", "ok")
    self.log(f"  Kernel 大小: {kernel_size/1024:.1f} KB", "white")
    self.log(f"  Ramdisk 大小: {ramdisk_size/1024:.1f} KB", "white")