# -*- coding: utf-8 -*-
"""Huijui Plus — v5.1 Pro+ 扩展包"""
import os, re, subprocess, threading, time, shutil, json
from datetime import datetime

def _safe_flag():
  return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

PLUS_GROUPS = [
  ("🚨 紧急救援", [
    ("restore_backup",   "一键从备份恢复", "扫描 D:\\RootManager\\ 并刷回所有分区（需 RESTORE 确认）", "err"),
    ("enter_fastboot",   "重启到 Fastboot", "adb reboot bootloader", "warn"),
    ("disable_all_modules","禁用所有模块",  "mv /data/adb/modules", "warn"),
    ("safe_mode_reboot",  "安全模式重启",  "开机不加载任何模块", "warn"),
  ]),
  ("🩺 健康诊断", [
    ("checkup_full",  "一键全面体检", "电池 + 内存 + 存储 + CPU", "ok"),
    ("battery_health", "电池健康",   "循环 / 设计容量 / 健康度", "info"),
    ("temp_monitor",  "温度监控",   "连续 10 秒采样", "info"),
    ("memory_detail", "内存详细",   "MemTotal / Swap / ZRAM", "info"),
    ("cpu_detail",   "CPU 详情",   "各核心当前频率", "info"),
    ("storage_tree",  "存储分布",   "/sdcard 下最占空间的目录", "info"),
  ]),
  ("🌐 网络诊断", [
    ("wifi_info", "WiFi 详情", "IP / MAC / 路由", "info"),
    ("ping_test", "Ping 测试", "8.8.8.8 + 223.5.5.5", "info"),
    ("proxy_set", "设置代理",  "读写 global http_proxy", "info"),
  ]),
  ("📦 应用管理", [
    ("bulk_install",  "批量安装 APK", "多选一次装完", "info"),
    ("bulk_uninstall", "批量卸载",   "按关键词过滤", "warn"),
    ("freeze_app",   "冻结应用",   "pm disable-user", "warn"),
    ("unfreeze_app",  "解冻应用",   "pm enable", "ok"),
    ("backup_app_data", "备份应用数据", "adb backup", "info"),
    ("debloat_preset", "去全家桶",   "小米/华为/OPPO 广告清单", "warn"),
    ("auto_start_mgr", "后台自启管理", "dump appops", "info"),
  ]),
  ("⚙ 系统工具", [
    ("backup_partitions", "批量备份分区", "boot/init_boot/vbmeta...", "info"),
    ("restore_partitions","批量恢复分区", "从目录刷回，需 RESTORE", "err"),
    ("selinux_toggle",  "SELinux 切换", "Enforcing ↔ Permissive", "warn"),
    ("build_prop_view",  "查看 build.prop", "读 /system/build.prop", "info"),
    ("sysprop_search",  "属性搜索",   "getprop | grep", "info"),
  ]),
  ("📜 日志大师", [
    ("logcat_live",  "抓 Logcat", "支持关键词过滤", "info"),
    ("crash_extract", "崩溃日志",  "抓 FATAL EXCEPTION", "err"),
    ("bugreport_pack","一键 Bugreport","打包完整诊断 zip", "info"),
  ]),
  ("🎨 美化", [
    ("theme_miku",  "初音绿主题", "#39C5BB 强调色", "ok"),
    ("theme_sakura", "樱花粉主题", "#FF89B5 强调色", "ok"),
    ("theme_cyber", "赛博紫主题", "#B47AFF 强调色", "ok"),
    ("bg_default",  "默认深色",  "原版深色（推荐）", "info"),
    ("bg_black",   "纯黑",    "OLED 省电", "info"),
    ("bg_deepblue", "深空蓝",   "深邃冷色调", "info"),
    ("bg_purple",  "暗夜紫",   "赛博氛围", "info"),
    ("bg_moss",   "墨绿",    "初音绿变体", "info"),
    ("bg_light",   "亮色",    "白底清爽", "info"),
    ("bg_custom",  "自定义 HEX", "输入 #RRGGBB", "ok"),
  ]),
]


class PlusTools:
  def __init__(self, adb, fb, runner, log_cb, work_dir, app=None):
    self.adb = adb; self.fb = fb; self.runner = runner
    self.log = log_cb; self.work_dir = work_dir; self.app = app
    self._busy = False

  def dispatch(self, action):
    if self._busy:
      self.log("⚠ 上一个任务还在跑", "warn"); return
    fn = getattr(self, f"do_{action}", None)
    if not fn:
      self.log(f"⚠ 未实现: {action}", "err"); return
    threading.Thread(target=self._safe_call, args=(fn,), daemon=True).start()

  def _safe_call(self, fn):
    self._busy = True
    try: fn()
    except Exception as e:
      import traceback
      self.log(f"✗ 异常: {e}", "err")
      self.log(traceback.format_exc()[:300], "muted")
    finally: self._busy = False

  def _adb_dev(self):
    out = self.runner.run_quiet(f"{self.adb} devices", 6)
    for ln in out.splitlines()[1:]:
      if "\tdevice" in ln: return ln.split("\t")[0]
    return None

  def _run_adb(self, cmd, timeout=30):
    return self.runner.run_quiet(f"{self.adb} {cmd}", timeout)

  def _run_su(self, cmd, timeout=60):
    dev = self._adb_dev()
    if not dev: return ""
    return self.runner.run_quiet(
      f"{self.adb} -s {dev} shell \"su -c '{cmd}'\"", timeout)

  def _run_fb(self, cmd, timeout=180):
    return self.runner.run_quiet(f"{self.fb} {cmd}", timeout)

  def _fb_dev(self):
    out = self.runner.run_quiet(f"{self.fb} devices", 6)
    for ln in out.splitlines():
      if "fastboot" in ln.lower(): return ln.split()[0]
    return None


  # ===== 🚨 紧急救援 =====
  def do_restore_backup(self):
    from tkinter import simpledialog
    self.log("🚨 一键从备份恢复 — 危险操作", "err")
    dev = self._fb_dev()
    if not dev:
      self.log(" ✗ 未检测到 Fastboot 设备", "err")
      self.log(" 💡 手机先进入 Fastboot 模式", "warn"); return
    self.log(f" ✓ Fastboot: {dev}", "ok")
    backup_dir, imgs = None, []
    for d in [r"D:\RootManager", r"D:\Huijui", self.work_dir]:
      if not os.path.isdir(d): continue
      found = [f for f in os.listdir(d) if f.lower().endswith(".img")]
      if found:
        backup_dir, imgs = d, found; break
    if not imgs:
      self.log(" ✗ 未找到 .img 备份文件", "err"); return
    self.log(f" 📁 {backup_dir}（{len(imgs)} 个镜像）", "info")
    for f in imgs:
      sz = os.path.getsize(os.path.join(backup_dir, f)) / 1024 / 1024
      self.log(f"  · {f} ({sz:.1f} MB)", "dim")
    if simpledialog.askstring("🚨 危险确认",
      f"将刷入 {len(imgs)} 个分区！\n输入 RESTORE 继续：") != "RESTORE":
      self.log(" ⏹ 已取消", "warn"); return
    ok_n = 0
    for img in imgs:
      part = img[:-4]
      out = self._run_fb(f'flash {part} "{os.path.join(backup_dir, img)}"', 300)
      ok = "OKAY" in out or "finished" in out.lower()
      self.log(f" {'✓' if ok else '✗'} {part}", "ok" if ok else "err")
      if ok: ok_n += 1
    self.log(f" ✅ {ok_n}/{len(imgs)}", "ok" if ok_n == len(imgs) else "warn")
    if ok_n > 0: self._run_fb("reboot", 20)

  def do_enter_fastboot(self):
    dev = self._adb_dev()
    if not dev: self.log(" ✗ 未检测到 ADB 设备", "err"); return
    self.runner.run_quiet(f"{self.adb} -s {dev} reboot bootloader", 20)
    self.log(" ✓ 已发送重启命令", "ok")

  def do_disable_all_modules(self):
    self._run_su("mv /data/adb/modules /data/adb/modules_disabled 2>/dev/null; "
           "mkdir -p /data/adb/modules; echo DONE")
    self.log(" ✓ 已禁用（重启生效）", "ok")

  def do_safe_mode_reboot(self):
    self._run_su("touch /data/adb/ksu/safe_mode 2>/dev/null; reboot")
    self.log(" ✓ 已标记安全模式并重启", "ok")

  # ===== 🩺 健康诊断 =====
  def do_checkup_full(self):
    self.log("🩺 一键全面体检...", "neon")
    dev = self._adb_dev()
    if not dev: self.log(" ✗ 无设备", "err"); return
    bat = self._run_adb(f"-s {dev} shell dumpsys battery", 15)
    lv = re.search(r"level:\s*(\d+)", bat)
    tp = re.search(r"temperature:\s*(\d+)", bat)
    if lv: self.log(f" 🔋 电量 {lv.group(1)}%", "ok")
    if tp: self.log(f" 🌡 温度 {int(tp.group(1))/10:.1f}°C", "ok")
    mem = self._run_adb(f"-s {dev} shell cat /proc/meminfo", 15)
    mt = re.search(r"MemTotal:\s*(\d+)", mem)
    ma = re.search(r"MemAvailable:\s*(\d+)", mem)
    if mt and ma:
      t = int(mt.group(1))/1024; a = int(ma.group(1))/1024
      self.log(f" 🧠 内存 {t:.0f} MB，已用 {(1-a/t)*100:.0f}%", "info")
    df = self._run_adb(f"-s {dev} shell df /data", 15)
    for ln in df.splitlines():
      m = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%", ln)
      if m and "/data" in ln:
        used = int(m.group(2))/1024/1024; tot = int(m.group(1))/1024/1024
        self.log(f" 💾 存储 {used:.1f}/{tot:.1f} GB ({m.group(4)}%)", "info")
    cpu = self._run_adb(f"-s {dev} shell cat /proc/loadavg", 10)
    if cpu: self.log(f" ⚙ CPU 负载 {cpu.split()[0]}", "info")
    self.log(" ✅ 体检完成", "ok")

  def do_battery_health(self):
    dev = self._adb_dev()
    if not dev: return
    c = self._run_adb(f"-s {dev} shell cat /sys/class/power_supply/battery/cycle_count", 10).strip()
    if c.isdigit(): self.log(f" 🔄 循环次数 {c}", "info")
    d = self._run_adb(f"-s {dev} shell cat /sys/class/power_supply/battery/charge_full_design", 10).strip()
    f = self._run_adb(f"-s {dev} shell cat /sys/class/power_supply/battery/charge_full", 10).strip()
    try:
      h = int(f)/int(d)*100
      self.log(f" 💚 健康度 {h:.1f}%", "ok" if h > 80 else "warn")
    except Exception:
      self.log(" ⚠ 该机型不支持容量读取", "dim")

  def do_temp_monitor(self):
    dev = self._adb_dev()
    if not dev: return
    self.log("🌡 温度采样 10 秒...", "info")
    for _ in range(10):
      t = self._run_adb(f"-s {dev} shell dumpsys battery | grep temperature", 5)
      m = re.search(r"(\d+)", t)
      if m: self.log(f" 🌡 {int(m.group(1))/10:.1f}°C", "info")
      time.sleep(1)

  def do_memory_detail(self):
    dev = self._adb_dev()
    if not dev: return
    mem = self._run_adb(f"-s {dev} shell cat /proc/meminfo", 15)
    keys = ("MemTotal", "MemFree", "MemAvailable", "Cached", "Buffers", "SwapTotal", "SwapFree")
    for ln in mem.splitlines():
      if ln.startswith(keys): self.log(f" {ln}", "white")
    sw = self._run_adb(f"-s {dev} shell cat /proc/swaps", 10)
    if sw.strip():
      self.log(" --- Swap/ZRAM ---", "dim")
      for ln in sw.splitlines(): self.log(f" {ln}", "white")

  def do_cpu_detail(self):
    dev = self._adb_dev()
    if not dev: return
    cores = self._run_adb(f"-s {dev} shell ls /sys/devices/system/cpu/ 2>/dev/null | grep -E '^cpu[0-9]+$'", 10)
    n = len([l for l in cores.splitlines() if l.strip()])
    self.log(f" 🎛 核心数 {n}", "info")
    for i in range(min(n, 8)):
      fr = self._run_adb(f"-s {dev} shell cat /sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq 2>/dev/null", 5).strip()
      if fr.isdigit():
        self.log(f"  cpu{i}: {int(fr)/1000:.0f} MHz", "white")

  def do_storage_tree(self):
    dev = self._adb_dev()
    if not dev: return
    out = self._run_adb(f"-s {dev} shell du -sh /sdcard/* 2>/dev/null | sort -hr | head -20", 60)
    for ln in out.splitlines(): self.log(f" {ln}", "white")

  # ===== 🌐 网络诊断 =====
  def do_wifi_info(self):
    dev = self._adb_dev()
    if not dev: return
    out = self._run_adb(f"-s {dev} shell ip addr show wlan0 2>/dev/null", 10)
    for ln in out.splitlines(): self.log(f" {ln}", "white")
    rt = self._run_adb(f"-s {dev} shell ip route | grep wlan0", 10)
    if rt: self.log(" --- 路由 ---", "dim"); self.log(f" {rt}", "white")

  def do_ping_test(self):
    dev = self._adb_dev()
    if not dev: return
    for h in ["8.8.8.8", "223.5.5.5"]:
      self.log(f" Ping {h}...", "info")
      out = self._run_adb(f"-s {dev} shell ping -c 3 -W 2 {h} 2>&1", 20)
      for ln in out.splitlines()[-4:]: self.log(f"  {ln}", "white")

  def do_proxy_set(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    cur = self._run_adb(f"-s {dev} shell settings get global http_proxy", 10).strip()
    self.log(f" 当前代理: {cur or '(空)'}", "info")
    addr = simpledialog.askstring("设置代理", "留空清除，否则填 IP:端口：")
    if addr is None: return
    if not addr.strip():
      self._run_adb(f"-s {dev} shell settings put global http_proxy :0", 10)
      self.log(" ✓ 已清除", "ok")
    else:
      self._run_adb(f"-s {dev} shell settings put global http_proxy {addr.strip()}", 10)
      self.log(f" ✓ 已设置 {addr}", "ok")

  # ===== 📦 应用管理 =====
  def do_bulk_install(self):
    from tkinter import filedialog
    paths = filedialog.askopenfilenames(title="选择 APK",
      filetypes=[("APK", "*.apk"), ("All", "*.*")])
    if not paths: return
    dev = self._adb_dev()
    if not dev: return
    ok_n = 0
    for p in paths:
      self.log(f" 📦 {os.path.basename(p)}", "info")
      out = self._run_adb(f'-s {dev} install -r "{p}"', 180)
      ok = "Success" in out
      if ok: ok_n += 1
      self.log(f"  {'✓' if ok else '✗'}", "ok" if ok else "err")
    self.log(f" ✅ {ok_n}/{len(paths)}", "ok")

  def do_bulk_uninstall(self):
    from tkinter import simpledialog, messagebox
    dev = self._adb_dev()
    if not dev: return
    kw = simpledialog.askstring("批量卸载", "关键词：")
    if not kw: return
    out = self._run_adb(f"-s {dev} shell pm list packages -3", 20)
    pkgs = [l.replace("package:", "").strip() for l in out.splitlines() if kw.lower() in l.lower()]
    if not pkgs: self.log(f" 无匹配", "warn"); return
    for p in pkgs: self.log(f"  · {p}", "white")
    if not messagebox.askyesno("确认", f"卸载 {len(pkgs)} 个应用？"): return
    for p in pkgs:
      self._run_adb(f"-s {dev} shell pm uninstall {p}", 20)
      self.log(f" ✓ {p}", "ok")

  def do_freeze_app(self):  self._freeze(True)
  def do_unfreeze_app(self): self._freeze(False)

  def _freeze(self, fr):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    pkg = simpledialog.askstring("包名", "输入包名：")
    if not pkg: return
    sub = "disable-user --user 0" if fr else "enable"
    self._run_adb(f"-s {dev} shell pm {sub} {pkg}", 20)
    self.log(f" ✓ {'冻结' if fr else '解冻'} {pkg}", "ok")

  def do_backup_app_data(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    pkg = (simpledialog.askstring("备份应用数据", "包名（留空=全部）：") or "").strip()
    fn = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ab"
    p = os.path.join(self.work_dir, fn)
    cmd = f'{self.adb} -s {dev} backup -apk -shared ' + (f'-f "{p}" {pkg}' if pkg else f'-all -f "{p}"')
    self.log(" 💾 备份中（手机需确认）...", "info")
    try:
      subprocess.run(cmd, shell=True, timeout=1800, creationflags=_safe_flag())
      if os.path.exists(p):
        self.log(f" ✓ {fn} ({os.path.getsize(p)/1024/1024:.1f} MB)", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  def do_debloat_preset(self):
    from tkinter import messagebox
    dev = self._adb_dev()
    if not dev: return
    pkgs = [
      "com.miui.analytics", "com.miui.systemAdSolution", "com.xiaomi.gamecenter.sdk.service",
      "com.miui.player", "com.miui.video", "com.miui.notes", "com.miui.bugreport",
      "com.huawei.android.hwouc", "com.huawei.appmarket", "com.huawei.wallet", "com.huawei.hwid",
      "com.heytap.browser", "com.heytap.market", "com.heytap.themestore", "com.coloros.appmarket",
      "com.android.bips", "com.android.printspooler", "com.google.android.apps.tachyon",
    ]
    self.log(f" 共 {len(pkgs)} 个常见广告/预装", "info")
    if not messagebox.askyesno("去全家桶", f"冻结 {len(pkgs)} 个应用？\n（冻结不删数据，可解冻）"):
      return
    ok_n = 0
    for p in pkgs:
      out = self._run_adb(f"-s {dev} shell pm disable-user --user 0 {p}", 15)
      if "disabled" in out.lower() or "new state" in out.lower():
        ok_n += 1; self.log(f" ✓ {p}", "ok")
      else:
        self.log(f" - {p}", "dim")
    self.log(f" ✅ {ok_n}/{len(pkgs)}", "ok")

  def do_auto_start_mgr(self):
    dev = self._adb_dev()
    if not dev: return
    out = self._run_adb(f"-s {dev} shell dumpsys appops | grep -i run_in_background | head -30", 30)
    for ln in out.splitlines()[:30]: self.log(f" {ln}", "white")
    if not out.strip(): self.log(" ⚠ 机型不支持 dumpsys appops", "warn")

  # ===== ⚙ 系统工具 =====
  def do_backup_partitions(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    parts = simpledialog.askstring("批量备份", "逗号分隔：", initialvalue="boot,init_boot,vbmeta")
    if not parts: return
    out_dir = os.path.join(self.work_dir, f"partition_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(out_dir, exist_ok=True)
    for part in [p.strip() for p in parts.split(",") if p.strip()]:
      self.log(f" ⏳ {part}...", "info")
      blk = f"/dev/block/by-name/{part}"
      if "No such" in (self._run_su(f"ls {blk} 2>/dev/null") or ""):
        self.log(f" ⚠ 分区不存在: {part}", "warn"); continue
      remote = f"/sdcard/_hb_{part}.img"
      self._run_su(f"dd if={blk} of={remote}")
      self._run_adb(f'-s {dev} pull {remote} "{out_dir}"', 300)
      self._run_su(f"rm {remote}")
      local = os.path.join(out_dir, f"{part}.img")
      if os.path.exists(local):
        self.log(f" ✓ {part} ({os.path.getsize(local)/1024/1024:.1f} MB)", "ok")
    self.log(f" 📁 {out_dir}", "info")

  def do_restore_partitions(self):
    from tkinter import filedialog, simpledialog
    if not self._fb_dev():
      self.log(" ✗ 需在 Fastboot 模式", "err"); return
    folder = filedialog.askdirectory(title="选择备份目录")
    if not folder: return
    imgs = [f for f in os.listdir(folder) if f.lower().endswith(".img")]
    if not imgs: self.log(" ✗ 无 .img", "err"); return
    if simpledialog.askstring("危险确认", f"刷入 {len(imgs)} 个分区，输 RESTORE：") != "RESTORE":
      self.log(" ⏹ 取消", "warn"); return
    for img in imgs:
      out = self._run_fb(f'flash {img[:-4]} "{os.path.join(folder, img)}"', 300)
      self.log(f" {'✓' if 'OKAY' in out else '✗'} {img[:-4]}", "ok" if "OKAY" in out else "err")

  def do_selinux_toggle(self):
    from tkinter import messagebox
    cur = self._run_su("getenforce").strip()
    self.log(f" 当前: {cur}", "info")
    target = "permissive" if cur == "Enforcing" else "enforcing"
    if not messagebox.askyesno("切换", f"→ {target}？"): return
    self._run_su(f"setenforce {0 if target=='permissive' else 1}")
    self.log(f" ✓ {target}", "ok")

  def do_build_prop_view(self):
    out = self._run_su("cat /system/build.prop 2>/dev/null | head -50")
    for ln in out.splitlines(): self.log(f" {ln}", "white")

  def do_sysprop_search(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    kw = simpledialog.askstring("属性搜索", "关键词：")
    if not kw: return
    out = self._run_adb(f"-s {dev} shell getprop | grep -i {kw}", 20)
    for ln in out.splitlines()[:50]: self.log(f" {ln}", "white")

  # ===== 📜 日志大师 =====
  def do_logcat_live(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    kw = (simpledialog.askstring("Logcat 过滤", "关键词（留空=全部）：") or "").strip()
    cmd = f"-s {dev} logcat -d -t 1000"
    if kw: cmd += f' | grep -i "{kw}"'
    out = self._run_adb(cmd, 30)
    fn = f"logcat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(os.path.join(self.work_dir, fn), "w", encoding="utf-8") as f:
      f.write(out)
    for ln in out.splitlines()[-30:]: self.log(f" {ln}", "white")
    self.log(f" ✓ {fn}", "ok")

  def do_crash_extract(self):
    dev = self._adb_dev()
    if not dev: return
    out = self._run_adb(f"-s {dev} logcat -d -t 5000 | grep -A 30 FATAL", 30)
    if not out.strip(): self.log(" ✓ 没有崩溃", "ok"); return
    for ln in out.splitlines()[:80]: self.log(f" {ln}", "err")

  def do_bugreport_pack(self):
    dev = self._adb_dev()
    if not dev: return
    fn = f"bugreport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    p = os.path.join(self.work_dir, fn)
    self.log(" 🐞 生成中...（1-3 分钟）", "info")
    try:
      subprocess.run(f'{self.adb} -s {dev} bugreport "{p}"', shell=True,
        timeout=300, creationflags=_safe_flag())
      if os.path.exists(p): self.log(f" ✓ {fn}", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  # ===== 🎨 美化 =====
  def do_theme_miku(self):  self._apply({"ACCENT":"#39C5BB","ACCENT_HOVER":"#2BA69D","OK":"#39C5BB","VIOLET":"#FF6BB5"})
  def do_theme_sakura(self): self._apply({"ACCENT":"#FF89B5","ACCENT_HOVER":"#E075A0","OK":"#FF89B5","VIOLET":"#B47AFF"})
  def do_theme_cyber(self): self._apply({"ACCENT":"#B47AFF","ACCENT_HOVER":"#9A5FE8","OK":"#B47AFF","VIOLET":"#FF6BB5"})

  def _apply(self, patch):
    if not self.app:
      self.log(" ⚠ app 引用丢失", "warn"); return
    try:
      import huijui_toolbox as hb
      hb.T._d.update(patch)
      self.app._rebuild_ui()
      self.log(" ✓ 主题已应用", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  # ===== 📜 日志大师 =====
  def do_logcat_live(self):
    from tkinter import simpledialog
    dev = self._adb_dev()
    if not dev: return
    kw = (simpledialog.askstring("Logcat 过滤", "关键词（留空=全部）：") or "").strip()
    cmd = f"-s {dev} logcat -d -t 1000"
    if kw: cmd += f' | grep -i "{kw}"'
    out = self._run_adb(cmd, 30)
    fn = f"logcat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(os.path.join(self.work_dir, fn), "w", encoding="utf-8") as f:
      f.write(out)
    for ln in out.splitlines()[-30:]: self.log(f" {ln}", "white")
    self.log(f" ✓ {fn}", "ok")

  def do_crash_extract(self):
    dev = self._adb_dev()
    if not dev: return
    out = self._run_adb(f"-s {dev} logcat -d -t 5000 | grep -A 30 FATAL", 30)
    if not out.strip(): self.log(" ✓ 没有崩溃", "ok"); return
    for ln in out.splitlines()[:80]: self.log(f" {ln}", "err")

  def do_bugreport_pack(self):
    dev = self._adb_dev()
    if not dev: return
    fn = f"bugreport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    p = os.path.join(self.work_dir, fn)
    self.log(" 🐞 生成中...（1-3 分钟）", "info")
    try:
      subprocess.run(f'{self.adb} -s {dev} bugreport "{p}"', shell=True,
        timeout=300, creationflags=_safe_flag())
      if os.path.exists(p): self.log(f" ✓ {fn}", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  # ===== 🎨 美化 =====
  def do_theme_miku(self):  self._apply({"ACCENT":"#39C5BB","ACCENT_HOVER":"#2BA69D","OK":"#39C5BB","VIOLET":"#FF6BB5"})
  def do_theme_sakura(self): self._apply({"ACCENT":"#FF89B5","ACCENT_HOVER":"#E075A0","OK":"#FF89B5","VIOLET":"#B47AFF"})
  def do_theme_cyber(self): self._apply({"ACCENT":"#B47AFF","ACCENT_HOVER":"#9A5FE8","OK":"#B47AFF","VIOLET":"#FF6BB5"})

  def _apply(self, patch):
    if not self.app:
      self.log(" ⚠ app 引用丢失", "warn"); return
    try:
      import huijui_toolbox as hb
      hb.T._d.update(patch)
      self.app._rebuild_ui()
      self.log(" ✓ 主题已应用", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  # ===== 🎨 背景方案 =====
  BG_SCHEMES = {
    "default": {
      "BG_DEEP":"#0B0E14","BG_MAIN":"#10141C","BG_PANEL":"#161B26",
      "BG_CARD":"#1E2430","BG_HOVER":"#2A303E",
      "TEXT_MAIN":"#EDF1F7","TEXT_DIM":"#9AA6B8","TEXT_MUTED":"#606A78",
      "ON_ACCENT":"#0B0E14",
    },
    "black": {
      "BG_DEEP":"#000000","BG_MAIN":"#020202","BG_PANEL":"#0A0A0A",
      "BG_CARD":"#141414","BG_HOVER":"#1E1E1E",
      "TEXT_MAIN":"#EDF1F7","TEXT_DIM":"#9AA6B8","TEXT_MUTED":"#606A78",
      "ON_ACCENT":"#000000",
    },
    "deepblue": {
      "BG_DEEP":"#0A1850","BG_MAIN":"#0E1E68","BG_PANEL":"#142A80",
      "BG_CARD":"#1C3698","BG_HOVER":"#2848B0",
      "TEXT_MAIN":"#EEF3FF","TEXT_DIM":"#B8C4E8","TEXT_MUTED":"#8894C0",
      "ON_ACCENT":"#0A1850",
    },
    "purple": {
      "BG_DEEP":"#2A0A50","BG_MAIN":"#380E68","BG_PANEL":"#48147E",
      "BG_CARD":"#5C1C98","BG_HOVER":"#7628B8",
      "TEXT_MAIN":"#F5ECFF","TEXT_DIM":"#D0B8F0","TEXT_MUTED":"#A888C8",
      "ON_ACCENT":"#2A0A50",
    },
    "moss": {
      "BG_DEEP":"#0A2818","BG_MAIN":"#0E3620","BG_PANEL":"#12482C",
      "BG_CARD":"#186038","BG_HOVER":"#1E7A46",
      "TEXT_MAIN":"#EAF8F0","TEXT_DIM":"#B0D8C0","TEXT_MUTED":"#88A898",
      "ON_ACCENT":"#0A2818",
    },
    "light": {
      "BG_DEEP":"#EEF1F5","BG_MAIN":"#F7F9FC","BG_PANEL":"#FFFFFF",
      "BG_CARD":"#F3F5F9","BG_HOVER":"#E5EAF1",
      "TEXT_MAIN":"#0F1419","TEXT_DIM":"#38414E","TEXT_MUTED":"#5A6470",
      "ON_ACCENT":"#FFFFFF",
    },
  }

  def do_bg_default(self): self._apply_bg("default")
  def do_bg_black(self):  self._apply_bg("black")
  def do_bg_deepblue(self): self._apply_bg("deepblue")
  def do_bg_purple(self):  self._apply_bg("purple")
  def do_bg_moss(self):   self._apply_bg("moss")
  def do_bg_light(self):  self._apply_bg("light")

  def _apply_bg(self, name):
    if not self.app:
      self.log(" ⚠ app 引用丢失", "warn"); return
    try:
      import huijui_toolbox as hb
      try:
        hb.cfg("bg_scheme", name)
      except Exception:
        pass
      # 同步 CTk 全局 appearance mode（影响内部组件的默认色）
      try:
        import customtkinter as _ctk
        _ctk.set_appearance_mode("light" if name == "light" else "dark")
      except Exception:
        pass
      if name == "default":
        hb.T.__dict__["_bg_override"] = {}
        hb.T.set(hb.cfg("theme") or "dark")
      else:
        scheme = self.BG_SCHEMES.get(name)
        if not scheme:
          self.log(f" ✗ 未知方案: {name}", "err"); return
        hb.T.__dict__["_bg_override"] = dict(scheme)
        hb.T._d.update(scheme)
      self.app._rebuild_ui()
      self.log(f" ✓ 背景已切换: {name}", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")

  def do_bg_custom(self):
    from tkinter import simpledialog
    hexv = simpledialog.askstring("自定义背景色",
      "输入 HEX（如 #1A2333）：", initialvalue="#1A2333")
    if not hexv: return
    hexv = hexv.strip()
    if not re.match(r'^#[0-9A-Fa-f]{6}$', hexv):
      self.log(" ✗ 格式错误，需 #RRGGBB", "err"); return
    try:
      import huijui_toolbox as hb
      # 基于主色衍生 5 档
      r0, g0, b0 = int(hexv[1:3],16), int(hexv[3:5],16), int(hexv[5:7],16)
      def mix(c, k):
        return f"#{int(c[0]*k):02x}{int(c[1]*k):02x}{int(c[2]*k):02x}"
      base = (r0, g0, b0)
      hb.T._d.update({
        "BG_DEEP": hexv,
        "BG_MAIN": mix(base, 1.15),
        "BG_PANEL": mix(base, 1.3),
        "BG_CARD": mix(base, 1.5),
        "BG_HOVER": mix(base, 1.7),
      })
      self.app._rebuild_ui()
      self.log(f" ✓ 自定义背景 {hexv}", "ok")
    except Exception as e:
      self.log(f" ✗ {e}", "err")
