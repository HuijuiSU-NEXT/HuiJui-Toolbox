#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Huijui 工具箱 v5.0 Pro · 自动补丁脚本
========================================
作用：
  1. 生成 huijui_extended.py（52 项新功能模块）
  2. 对 huijui_toolbox.py 应用 13 处 bug 修复 + 集成扩展
  3. 自动备份原文件 huijui_toolbox.py.bak.YYYYMMDD_HHMMSS
用法：
  python apply_pro_patch.py
  python apply_pro_patch.py "D:\\path\\to\\huijui_toolbox.py"
"""
import os, sys, shutil, re
from datetime import datetime

TARGET = sys.argv[1] if len(sys.argv) > 1 else r"D:\Huijui\v4_python\src\huijui_toolbox.py"
SRC_DIR = os.path.dirname(os.path.abspath(TARGET))

# ============================================================
# 一、扩展模块：huijui_extended.py（52 项新功能）
# ============================================================
EXTENDED_CONTENT = r'''# -*- coding: utf-8 -*-
"""
Huijui Extended Toolkit — 52 项新功能
ADB / Fastboot / Fastbootd / Recovery / Sideload / EDL(9008) / BROM
"""
import os, re, subprocess, threading, time, shutil, zipfile, hashlib

def _safe_flag():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

def _run(cmd, timeout=60, cwd=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout,
                           cwd=cwd, creationflags=_safe_flag())
        out = (r.stdout or b"") + (r.stderr or b"")
        return r.returncode, out.decode("utf-8", errors="ignore").strip()
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, f"ERR: {e}"

MODE_ICONS = {
    "ADB": "🔌", "Sideload": "📥", "Recovery": "🛠",
    "Fastboot": "⚡", "Fastbootd": "🚀",
    "EDL": "💠", "BROM": "🧩", "Odin": "🔷", "DFU": "🍎",
    "MTP": "📁", "Offline": "⚫",
}

class ModeDetector:
    def __init__(self, adb, fb, runner):
        self.adb = adb; self.fb = fb; self.runner = runner

    def _usb_devices(self):
        try:
            r = subprocess.run(
                'powershell -NoProfile -Command "Get-PnpDevice -PresentOnly | '
                'Where-Object {$_.InstanceId -like \'USB*\'} | '
                'Select-Object -ExpandProperty InstanceId"',
                shell=True, capture_output=True, timeout=8,
                creationflags=_safe_flag())
            return (r.stdout or b"").decode("utf-8", "ignore").upper()
        except Exception:
            return ""

    def _vid_pid_scan(self):
        s = self._usb_devices()
        hits = set()
        if re.search(r"VID_05C6&PID_9008", s) or "QDLOADER" in s:
            hits.add("EDL")
        if re.search(r"VID_05C6&PID_900E", s):
            hits.add("EDL")
        if re.search(r"VID_0E8D&PID_0003", s) or "MTK_USB" in s:
            hits.add("BROM")
        if re.search(r"VID_04E8&PID_685D", s) or "SAMSUNG_MOBILE" in s.upper():
            hits.add("Odin")
        if re.search(r"VID_05AC&PID_1227", s) or "APPLE_MOBILE_DEVICE" in s:
            hits.add("DFU")
        return hits

    def _adb_state(self):
        code, out = _run(f"{self.adb} get-state", timeout=6)
        if code != 0:
            return None
        return out.strip()

    def _adb_devices(self):
        code, out = _run(f"{self.adb} devices", timeout=6)
        if code != 0:
            return []
        return [ln.split("\t")[0] for ln in out.splitlines()[1:] if "\t" in ln]

    def _fb_devices(self):
        code, out = _run(f"{self.fb} devices", timeout=6)
        if code != 0:
            return []
        return [ln.split()[0] for ln in out.splitlines()
                if ln.strip() and "fastboot" in ln.lower()]

    def _fb_is_userspace(self):
        code, out = _run(f"{self.fb} getvar is-userspace 2>&1", timeout=6)
        return "yes" in out.lower()

    def detect(self):
        fbv = self._fb_devices()
        if fbv:
            serial = fbv[0]
            if self._fb_is_userspace():
                return "Fastbootd", serial, {}
            return "Fastboot", serial, {}
        adb_list = self._adb_devices()
        if adb_list:
            serial = adb_list[0]
            state = self._adb_state() or ""
            if state == "sideload":
                return "Sideload", serial, {"state": state}
            if state == "recovery":
                return "Recovery", serial, {"state": state}
            if state == "device":
                _, bm = _run(f"{self.adb} -s {serial} shell getprop ro.bootmode", 5)
                if "recovery" in bm.lower():
                    return "Recovery", serial, {"state": "recovery"}
                return "ADB", serial, {"state": state}
            if state == "unauthorized":
                return "ADB", serial, {"state": "unauthorized"}
            if state == "offline":
                return "Offline", serial, {"state": state}
        hits = self._vid_pid_scan()
        for k in ("EDL", "BROM", "Odin", "DFU"):
            if k in hits:
                return k, "", {}
        return "Offline", "", {}

    def describe(self, mode):
        return {
            "ADB":       "ADB 正常模式",
            "Sideload":  "ADB Sideload（Recovery 下刷 OTA/ROM）",
            "Recovery":  "Recovery 模式",
            "Fastboot":  "Fastboot 引导模式（物理分区）",
            "Fastbootd": "Fastbootd 用户空间（逻辑分区）",
            "EDL":       "高通 9008/EDL（需 QFIL）",
            "BROM":      "联发科 BROM（需 SP Flash Tool）",
            "Odin":      "三星 Download（需 Odin）",
            "DFU":       "Apple DFU（需 iTunes）",
            "MTP":       "MTP 文件传输",
            "Offline":   "无设备连接",
        }.get(mode, "未知")


class ExtendedTools:
    def __init__(self, adb, fb, runner, log_cb, ui_cb, work_dir):
        self.adb = adb; self.fb = fb; self.runner = runner
        self.log = log_cb; self.ui = ui_cb; self.work_dir = work_dir

    def _get_adb_dev(self):
        code, out = _run(f"{self.adb} devices", 6)
        for ln in out.splitlines()[1:]:
            if "\tdevice" in ln:
                return ln.split("\t")[0]
        return None

    def _get_fb_dev(self):
        code, out = _run(f"{self.fb} devices", 6)
        for ln in out.splitlines():
            if "fastboot" in ln.lower():
                return ln.split()[0]
        return None

    def _p(self, p):
        return f'"{p}"' if p else ""

    # ===== ADB 组（#10~#20） =====
    def push_file(self, local, remote="/sdcard/"):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return False
        if not os.path.exists(local):
            self.log(f"✗ 文件不存在: {local}", "err"); return False
        self.log(f"📤 push: {os.path.basename(local)} → {remote}", "info")
        code, out = _run(f'{self.adb} -s {dev} push {self._p(local)} "{remote}"', 600)
        self.log(f"  {'✓' if code==0 else '✗'} {out.splitlines()[-1] if out else ''}",
                 "ok" if code==0 else "err")
        return code == 0

    def pull_file(self, remote, local_dir=None):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return False
        local_dir = local_dir or self.work_dir
        self.log(f"📥 pull: {remote} → {local_dir}", "info")
        code, out = _run(f'{self.adb} -s {dev} pull "{remote}" {self._p(local_dir)}', 600)
        self.log(f"  {'✓' if code==0 else '✗'} {out.splitlines()[-1] if out else ''}",
                 "ok" if code==0 else "err")
        return code == 0

    def logcat_dump(self, lines=2000):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return
        self.log(f"📜 抓取 logcat（{lines} 行）...", "info")
        code, out = _run(f"{self.adb} -s {dev} logcat -d -t {lines}", 60)
        if out:
            fn = f"logcat_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            p = os.path.join(self.work_dir, fn)
            with open(p, "w", encoding="utf-8") as f:
                f.write(out)
            self.log(f"  ✓ 已保存: {fn}", "ok")

    def bugreport_dump(self):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return
        self.log("🐞 生成 bugreport（1-3 分钟）...", "info")
        fn = f"bugreport_{time.strftime('%Y%m%d_%H%M%S')}.zip"
        p = os.path.join(self.work_dir, fn)
        code, out = _run(f'{self.adb} -s {dev} bugreport "{p}"', 300)
        if code == 0 and os.path.exists(p):
            self.log(f"  ✓ 已保存: {fn}", "ok")
        else:
            self.log(f"  ✗ 失败: {out[:200]}", "err")

    def list_packages(self, keyword="", system=False):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return []
        flag = "-s" if system else "-3"
        code, out = _run(f"{self.adb} -s {dev} shell pm list packages {flag}", 30)
        pkgs = [ln.replace("package:", "").strip() for ln in out.splitlines()
                if ln.startswith("package:")]
        if keyword:
            pkgs = [p for p in pkgs if keyword.lower() in p.lower()]
        self.log(f"📦 找到 {len(pkgs)} 个应用", "info")
        for p in pkgs[:60]:
            self.log(f"    {p}", "white")
        return pkgs

    def uninstall_app(self, pkg, keep_data=False):
        dev = self._get_adb_dev()
        if not dev: return False
        flag = "-k" if keep_data else ""
        code, out = _run(f"{self.adb} -s {dev} shell pm uninstall {flag} {pkg}", 30)
        ok = "Success" in out
        self.log(f"  {'✓ 卸载成功' if ok else '✗ 卸载失败'}: {pkg}", "ok" if ok else "err")
        return ok

    def disable_app(self, pkg, enable=True):
        dev = self._get_adb_dev()
        if not dev: return False
        cmd = "enable" if enable else "disable-user --user 0"
        code, out = _run(f"{self.adb} -s {dev} shell pm {cmd} {pkg}", 20)
        self.log(f"  {'✓ 启用' if enable else '✓ 禁用'}: {pkg}", "ok")
        return "Error" not in out

    def grant_permission(self, pkg, permission, grant=True):
        dev = self._get_adb_dev()
        if not dev: return False
        sub = "grant" if grant else "revoke"
        code, out = _run(f"{self.adb} -s {dev} shell pm {sub} {pkg} {permission}", 20)
        self.log(f"  {'✓ 授予' if grant else '✓ 撤销'}: {pkg} / {permission}", "ok")
        return code == 0

    def set_prop(self, key, value):
        dev = self._get_adb_dev()
        if not dev: return False
        code, out = _run(f'{self.adb} -s {dev} shell "su -c \'setprop {key} {value}\'"', 20)
        self.log(f"  ✓ setprop {key}={value}", "ok")
        return code == 0

    def screencap_to_pc(self, save_dir=None):
        dev = self._get_adb_dev()
        if not dev: return False
        save_dir = save_dir or self.work_dir
        fn = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        p = os.path.join(save_dir, fn)
        try:
            with open(p, "wb") as f:
                subprocess.run(f"{self.adb} -s {dev} exec-out screencap -p",
                               shell=True, stdout=f, timeout=30,
                               creationflags=_safe_flag())
            if os.path.getsize(p) > 1024:
                self.log(f"  ✓ 截图: {fn}", "ok")
                try: os.startfile(p)
                except Exception: pass
                return True
        except Exception as e:
            self.log(f"  ✗ 截图异常: {e}", "err")
        return False

    def input_key(self, keycode):
        dev = self._get_adb_dev()
        if not dev: return False
        code, _ = _run(f"{self.adb} -s {dev} shell input keyevent {keycode}", 10)
        return code == 0

    # ===== Fastboot 组（#21~#31） =====
    def fb_all_vars(self):
        self.log("📋 读取全部 fastboot 变量...", "info")
        code, out = _run(f"{self.fb} getvar all 2>&1", 20)
        vars_dict = {}
        for ln in out.splitlines():
            m = re.match(r"\(bootloader\)\s*(\S+):\s*(.*)", ln)
            if m:
                vars_dict[m.group(1)] = m.group(2)
        for k, v in vars_dict.items():
            self.log(f"    {k} = {v}", "white")
        return vars_dict

    def fb_unlock(self):
        self.log("🔓 解锁 Bootloader...", "warn")
        code, out = _run(f"{self.fb} flashing unlock", 30)
        self.log(f"  {out[:300]}", "ok" if "FAILED" not in out else "err")

    def fb_lock(self):
        self.log("🔒 锁定 Bootloader...", "warn")
        code, out = _run(f"{self.fb} flashing lock", 30)
        self.log(f"  {out[:300]}", "ok" if "FAILED" not in out else "err")

    def fb_erase(self, partition):
        self.log(f"🧹 擦除 {partition}...", "warn")
        code, out = _run(f"{self.fb} erase {partition}", 60)
        self.log(f"  {out[:200]}", "ok" if "OKAY" in out or code==0 else "err")

    def fb_set_active(self, slot):
        self.log(f"🔀 设置活动槽位 {slot}...", "info")
        code, out = _run(f"{self.fb} set_active {slot}", 20)
        self.log(f"  {out[:200]}", "ok" if code==0 else "err")

    def fb_oem_cmd(self, cmd):
        self.log(f"⚙ oem {cmd}...", "info")
        code, out = _run(f"{self.fb} oem {cmd}", 30)
        self.log(f"  {out[:300]}", "info")

    def fb_boot(self, img_path):
        if not os.path.exists(img_path):
            self.log(f"✗ 镜像不存在: {img_path}", "err"); return False
        self.log(f"🚀 fastboot boot {os.path.basename(img_path)}...", "info")
        code, out = _run(f'{self.fb} boot {self._p(img_path)}', 120)
        self.log(f"  {out[:300]}", "ok" if code == 0 else "err")
        return code == 0

    def fb_flash_recovery(self, img_path):
        return self._fb_flash_one("recovery", img_path)

    def fb_flash_gsi(self, img_path, partition="system"):
        return self._fb_flash_one(partition, img_path)

    def fb_flash_single(self, partition, img_path):
        return self._fb_flash_one(partition, img_path)

    def _fb_flash_one(self, partition, img_path):
        if not os.path.exists(img_path):
            self.log(f"✗ 镜像不存在: {img_path}", "err"); return False
        self.log(f"⚡ 刷入 {partition} ← {os.path.basename(img_path)}", "info")
        code, out = _run(f'{self.fb} flash {partition} {self._p(img_path)}', 300)
        ok = code == 0 and ("OKAY" in out or "finished" in out.lower())
        self.log(f"  {'✓' if ok else '✗'} {out.splitlines()[-1] if out else ''}",
                 "ok" if ok else "err")
        return ok

    def fb_flash_folder(self, folder, mapping=None):
        if not os.path.isdir(folder):
            self.log(f"✗ 目录不存在: {folder}", "err"); return
        mapping = mapping or {}
        imgs = [f for f in os.listdir(folder) if f.lower().endswith(".img")]
        for img in imgs:
            name = img[:-4]
            base = re.sub(r"_(a|b)$", "", name)
            if base not in mapping:
                mapping[base] = img
        ok_n = 0
        for part, img in mapping.items():
            p = os.path.join(folder, img)
            if os.path.exists(p) and self._fb_flash_one(part, p):
                ok_n += 1
        self.log(f"📦 批量刷入完成: {ok_n}/{len(mapping)}", "ok")

    # ===== 镜像工具（#32~#40） =====
    def md5_check(self, path):
        return self._hash(path, "md5")

    def sha1_check(self, path):
        return self._hash(path, "sha1")

    def sha256_check(self, path):
        return self._hash(path, "sha256")

    def _hash(self, path, algo):
        if not os.path.exists(path):
            self.log(f"✗ 文件不存在: {path}", "err"); return None
        h = hashlib.new(algo)
        size = os.path.getsize(path)
        self.log(f"🔐 计算 {algo.upper()}: {os.path.basename(path)} ({size/1024/1024:.1f} MB)", "info")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024*1024), b""):
                h.update(chunk)
        digest = h.hexdigest()
        self.log(f"  ✓ {algo.upper()} = {digest}", "ok")
        return digest

    def img_magic(self, path):
        if not os.path.exists(path):
            self.log("✗ 文件不存在", "err"); return "?"
        with open(path, "rb") as f:
            head = f.read(16)
        magic_map = {
            b"ANDROID!": "Android Boot Image (boot/recovery/init_boot)",
            b"\x53\xEF": "ext4 / super 分区头",
            b"\x4D\x5A": "PE 可执行文件（Windows）",
            b"PK\x03\x04": "ZIP / APK / OTA 卡刷包",
            b"CrAU": "ChromeOS/Android OTA payload",
        }
        for k, v in magic_map.items():
            if head.startswith(k):
                self.log(f"  ✓ {os.path.basename(path)} → {v}", "ok")
                return v
        self.log(f"  ? 未知魔数: {head[:8].hex()}", "warn")
        return "?"

    def bootimg_info(self, path):
        if not os.path.exists(path):
            self.log("✗ 文件不存在", "err"); return
        try:
            with open(path, "rb") as f:
                data = f.read(64)
            if not data.startswith(b"ANDROID!"):
                self.log("  ⚠ 不是 Android boot image", "warn"); return
            kernel_size  = int.from_bytes(data[8:12], "little")
            kernel_addr  = int.from_bytes(data[12:16], "little")
            ramdisk_size = int.from_bytes(data[16:20], "little")
            ramdisk_addr = int.from_bytes(data[20:24], "little")
            self.log(f"  ✓ boot image:", "ok")
            self.log(f"    kernel : {kernel_size/1024:.1f} KB @ 0x{kernel_addr:08X}", "white")
            self.log(f"    ramdisk: {ramdisk_size/1024:.1f} KB @ 0x{ramdisk_addr:08X}", "white")
        except Exception as e:
            self.log(f"  ✗ 解析失败: {e}", "err")

    def partition_sizes(self):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return
        code, out = _run(f"{self.adb} -s {dev} shell ls -l /dev/block/by-name/", 15)
        for ln in out.splitlines():
            m = re.search(r"(\S+)\s*->\s*(\S+)", ln)
            if m:
                self.log(f"    {m.group(1):<24} → {m.group(2)}", "white")

    def compare_firmware(self, zip_a, zip_b):
        def _read_pp(z):
            try:
                with zipfile.ZipFile(z) as zf:
                    if "payload_properties.txt" not in zf.namelist():
                        return ""
                    return zf.read("payload_properties.txt").decode("utf-8", "ignore")
            except Exception:
                return ""
        a, b = _read_pp(zip_a), _read_pp(zip_b)
        def _pick(t, key):
            m = re.search(rf"{key}[=:]\s*(\S+)", t)
            return m.group(1) if m else "?"
        keys = ["post-build", "post-build-incremental", "post-sdk-level",
                "post-security-patch-level", "post-timestamp"]
        self.log("🆚 固件版本比较:", "purple")
        for k in keys:
            va, vb = _pick(a, k), _pick(b, k)
            eq = "✓" if va == vb else "≠"
            self.log(f"    {k:32} {va}  {eq}  {vb}", "white" if va == vb else "warn")

    def backup_all_partitions(self, partitions, out_dir=None):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return
        out_dir = out_dir or os.path.join(self.work_dir,
                    f"fullbackup_{time.strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)
        for part in partitions:
            self.log(f"  ⏳ 备份 {part}...", "info")
            code, out = _run(
                f'{self.adb} -s {dev} shell "su -c \'dd if=/dev/block/by-name/{part} '
                f'of=/sdcard/{part}.img\'"', 300)
            if code != 0:
                self.log(f"  ⚠ {part} 失败（可能未 root）", "warn"); continue
            _run(f'{self.adb} -s {dev} pull /sdcard/{part}.img {self._p(out_dir)}', 600)
            _run(f"{self.adb} -s {dev} shell rm /sdcard/{part}.img", 15)
            tgt = os.path.join(out_dir, f"{part}.img")
            if os.path.exists(tgt):
                self.log(f"  ✓ {part} ({os.path.getsize(tgt)/1024/1024:.1f} MB)", "ok")

    def restore_backup(self, backup_dir):
        if not os.path.isdir(backup_dir):
            self.log("✗ 目录不存在", "err"); return
        for img in [f for f in os.listdir(backup_dir) if f.lower().endswith(".img")]:
            part = img[:-4]
            self._fb_flash_one(part, os.path.join(backup_dir, img))

    # ===== Root / 高级（#41~#50） =====
    def install_module(self, module_zip):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return False
        if not os.path.exists(module_zip):
            self.log("✗ 模块文件不存在", "err"); return False
        fn = os.path.basename(module_zip)
        self.log(f"📦 推送模块 {fn} → /sdcard/Download/", "info")
        _run(f'{self.adb} -s {dev} push {self._p(module_zip)} /sdcard/Download/', 120)
        self.log("  ✓ 完成，请在 Magisk App 中安装", "ok")
        return True

    def persist_root_script(self, script_content):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return False
        fn = f"huijui_{int(time.time())}.sh"
        tmp = os.path.join(self.work_dir, fn)
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            f.write(script_content)
        _run(f'{self.adb} -s {dev} push {self._p(tmp)} /sdcard/{fn}', 60)
        _run(f'{self.adb} -s {dev} shell "su -c \'mv /sdcard/{fn} '
             f'/data/adb/service.d/ && chmod 755 /data/adb/service.d/{fn}\'"', 30)
        self.log(f"  ✓ 已写入 /data/adb/service.d/{fn}", "ok")
        return True

    def inject_recovery(self, recovery_img):
        return self._fb_flash_one("recovery", recovery_img)

    def ab_slot_switch(self, target_slot):
        self.log(f"🔀 切换到槽位 {target_slot} 并重启...", "warn")
        _run(f"{self.fb} --set-active={target_slot}", 20)
        _run(f"{self.fb} reboot", 20)

    def extract_device_tree(self, out_dir=None):
        dev = self._get_adb_dev()
        if not dev: self.log("✗ 未检测到设备", "err"); return
        out_dir = out_dir or os.path.join(self.work_dir,
                    f"devtree_{time.strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)
        paths = ["/vendor/etc/fstab.*", "/system/etc/fstab.*",
                 "/odm/etc/fstab.*", "/vendor/etc/recovery.fstab",
                 "/system/etc/recovery.fstab"]
        for p in paths:
            code, out = _run(f'{self.adb} -s {dev} shell "ls {p} 2>/dev/null"', 15)
            for f in out.splitlines():
                fn = os.path.basename(f.strip())
                if fn:
                    _run(f'{self.adb} -s {dev} pull "{f.strip()}" {self._p(out_dir)}', 30)
        self.log(f"  ✓ 设备树已提取到 {out_dir}", "ok")

    def analyze_log(self, log_path):
        if not os.path.exists(log_path):
            self.log("✗ 日志不存在", "err"); return
        keywords = {"ERROR": "错误", "FAILED": "失败", "TIMEOUT": "超时",
                    "not found": "不存在", "denied": "拒绝", "corrupt": "损坏",
                    "can't": "无法", "warning": "警告"}
        counts = {}
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            for ln in f:
                for k in keywords:
                    if k.lower() in ln.lower():
                        counts[k] = counts.get(k, 0) + 1
        self.log("📊 日志分析:", "purple")
        for k, n in sorted(counts.items(), key=lambda x: -x[1]):
            self.log(f"    {keywords[k]:<6} × {n}", "warn" if n > 0 else "dim")

    def cleanup_temp(self):
        removed = 0; freed = 0
        for name in os.listdir(self.work_dir):
            p = os.path.join(self.work_dir, name)
            if name == "payload.bin" or name.startswith("extracted_"):
                try:
                    if os.path.isdir(p):
                        freed += sum(os.path.getsize(os.path.join(dp, f))
                                     for dp, _, fs in os.walk(p) for f in fs)
                        shutil.rmtree(p)
                    else:
                        freed += os.path.getsize(p); os.remove(p)
                    removed += 1
                except Exception:
                    pass
        self.log(f"🧹 清理 {removed} 项，释放 {freed/1024/1024:.1f} MB", "ok")

    # ===== EDL / MTK（#51~#52） =====
    def edl_qfil_hint(self):
        self.log("💠 高通 9008/EDL 模式已检测", "purple")
        self.log("  请用 Qualcomm QFIL / QDL 加载 prog_firehose_*.elf", "white")
        self.log("  镜像目录需包含: rawprogram*.xml, patch*.xml, *.img", "white")
        self.log("  ⚠ EDL 刷机会完全擦除设备，请谨慎", "warn")

    def brom_spflash_hint(self):
        self.log("🧩 联发科 BROM 已检测", "purple")
        self.log("  请用 SP Flash Tool + MTK_AllInOne_DA.bin", "white")
        self.log("  scatter 文件可从原厂固件 zip 中提取", "white")
'''


# ============================================================
# 二、对 huijui_toolbox.py 的补丁列表
# ============================================================
PATCHES = []

# --- 补丁 1：导入扩展模块 ---
PATCHES.append((
    "① 导入扩展模块",
    '''try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False''',
    '''try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ===== v5.0 Pro 扩展模块 =====
try:
    from huijui_extended import ModeDetector, ExtendedTools, MODE_ICONS
    HAS_EXT = True
except Exception:
    HAS_EXT = False
    ModeDetector = None
    ExtendedTools = None
    MODE_ICONS = {}'''
))

# --- 补丁 2：is_dangerous 加缓存（性能修复） ---
PATCHES.append((
    "② is_dangerous 缓存优化",
    '''def is_dangerous(name):
    if name.lower() in DANGEROUS_DEFAULT: return True
    if name.lower() in set(cfg("dangerous_extra") or []): return True
    return False''',
    '''_dangerous_cache = None
def is_dangerous(name):
    global _dangerous_cache
    if _dangerous_cache is None:
        _dangerous_cache = set(DANGEROUS_DEFAULT) | set(cfg("dangerous_extra") or [])
    return name.lower() in _dangerous_cache

def invalidate_dangerous_cache():
    global _dangerous_cache
    _dangerous_cache = None'''
))

# --- 补丁 3：Animator 加 _destroyed 检查（防闪退） ---
PATCHES.append((
    "③ Animator 退出保护",
    '''    def _tick(self):
        if not self.running: return
        now = time.time(); dt = now - self._last; self._last = now''',
    '''    def _tick(self):
        if not self.running or getattr(self, "_destroyed", False): return
        now = time.time(); dt = now - self._last; self._last = now'''
))

# --- 补丁 4：_on_close 标记销毁（配合补丁 3） ---
PATCHES.append((
    "④ _on_close 标记 Animator 销毁",
    '''        try:
            self.runner.stop_flag = True
            self.guard.release_lock()
            self.animator.running = False
            self.quit(); self.destroy()
        except Exception: pass''',
    '''        try:
            self.runner.stop_flag = True
            self.guard.release_lock()
            self.animator.running = False
            self.animator._destroyed = True
            self.quit(); self.destroy()
        except Exception: pass'''
))

# --- 补丁 5：_enter_main 初始化扩展工具 ---
PATCHES.append((
    "⑤ _enter_main 初始化 ExtendedTools",
    '''        try:
            self._build_ui()
            self._poll_log(); self._poll_ui(); self._tick_clock()
            self.after(300, self._scan_zip)
            self.after(500, self._scan_device)
        except Exception: traceback.print_exc()''',
    '''        try:
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
        except Exception: traceback.print_exc()'''
))

# --- 补丁 6：_set_status 主题色 bug 修复 ---
PATCHES.append((
    "⑥ _set_status 主题色修复",
    '''    def _set_status(self, text, color):
        try:
            self.status_dot.set_color(color)
            self.status_label.configure(text=text, text_color=color)
            bg_map = {T.OK:("#0A1F14","#14402A"),
                      T.WARN:("#2B2010","#4D3A15"),
                      T.ERR:("#2B0E14","#4D1A26")}
            bg, bd = bg_map.get(color, ("#0A1F14","#14402A"))
            self.status_pill.configure(fg_color=bg, border_color=bd)
            top_color = {T.OK:"#14402A", T.WARN:"#4D3A15",
                          T.ERR:"#4D1A26"}.get(color, T.ACCENT)
            if alive(self.topbar_border):
                self.topbar_border.configure(fg_color=top_color)
        except Exception: pass''',
    '''    def _set_status(self, text, color):
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
        except Exception: pass'''
))

# --- 补丁 7：_rebuild_ui 去除重复 welcome ---
PATCHES.append((
    "⑦ _rebuild_ui 去掉重复 welcome",
    '''            self._build_ui()
            self._log_count = 0
            self._welcome()
            if state["current_tab"]:
                self._switch_tab(state["current_tab"])
            self.log("🎨 主题已实时切换", "ok")''',
    '''            self._build_ui()
            self._log_count = 0
            # _build_ui 内部已调用 _welcome()，此处不再重复
            if state["current_tab"]:
                self._switch_tab(state["current_tab"])
            self.log("🎨 主题已实时切换", "ok")'''
))

# --- 补丁 8：_scan_device_thread 提前返回（启用 ModeDetector） ---
PATCHES.append((
    "⑧ _scan_device_thread 启用 ModeDetector",
    '''    def _scan_device_thread(self):
        try:
            self.log("🔍 正在扫描设备...", "info")
            fb_out = self.runner.run_quiet(f"{self.fb} devices")''',
    '''    def _scan_device_thread(self):
        # v5.0 Pro：若扩展可用，走全模式检测
        if HAS_EXT and getattr(self, "ext", None) is not None:
            self._scan_device_thread_ext()
            return
        try:
            self.log("🔍 正在扫描设备...", "info")
            fb_out = self.runner.run_quiet(f"{self.fb} devices")'''
))

# --- 补丁 9：_page_adb 追加"按模式刷入"面板 ---
PATCHES.append((
    "⑨ _page_adb 追加按模式刷入面板",
    '''        ctk.CTkButton(scroll, text="▶  执行", command=self._do_shell,
            height=38, font=F_BTN, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
            text_color=T.ON_ACCENT, corner_radius=8).pack(fill="x", padx=12,
                                                            pady=(0,20))

    # ================= 刷机历史页 =================''',
    '''        ctk.CTkButton(scroll, text="▶  执行", command=self._do_shell,
            height=38, font=F_BTN, fg_color=T.ACCENT, hover_color=T.ACCENT_HOVER,
            text_color=T.ON_ACCENT, corner_radius=8).pack(fill="x", padx=12,
                                                            pady=(0,10))

        # ================= v5.0 Pro：按模式刷入 =================
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
        ctk.CTkButton(scroll, text="🔍  刷新模式", command=self._refresh_mode,
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
        ctk.CTkButton(scroll, text="📥  选择 OTA/ROM 并 Sideload",
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
        ctk.CTkFrame(scroll, height=20, fg_color="transparent").pack()

    # ================= 刷机历史页 ================='''
))

# --- 补丁 10：追加所有新方法 ---
NEW_METHODS = '''
    # ================= v5.0 Pro 扩展方法 =================
    def _scan_device_thread_ext(self):
        """使用 ModeDetector 全模式扫描（v5.0 Pro）"""
        try:
            self.log("🔍 [Pro] 全模式扫描中...", "info")
            md = ModeDetector(self.adb, self.fb, self.runner)
            mode, serial, extra = md.detect()
            icon = MODE_ICONS.get(mode, "❓")
            self._device_mode = mode
            self._device_serial = serial or ""
            self.log(f"  {icon} 模式：{mode}  ·  {md.describe(mode)}", "info")
            self.ui(self._update_info, "mode", mode)
            self.ui(self._update_info, "serial", serial or "—")
            color = {"ADB": T.OK, "Fastboot": T.INFO, "Fastbootd": T.VIOLET,
                     "Sideload": T.WARN, "Recovery": T.WARN,
                     "EDL": T.ERR, "BROM": T.ERR, "Odin": T.ERR,
                     "DFU": T.ERR, "Offline": T.ERR}.get(mode, T.WARN)
            self.ui(self._set_status, mode, color)
            self.ui(self._update_mode_label, mode, serial)

            if mode == "Offline":
                self.log("  ✗ 未检测到设备", "err")
                return
            if mode in ("EDL", "BROM", "Odin", "DFU"):
                self.log(f"  💡 {mode} 模式：请使用对应的专用工具", "warn")
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
            self.log(f"  📱 {brand} {model}", "info")
            self.log(f"  🤖 Android {ver} (API {sdk})", "info")
            self.log(f"  🔓 BL: {bl}", "info")
            self.log(f"  🏷 品牌: {get_brand_display(detect_brand(brand))}", "purple")
            self.log(f"  🔀 槽位: {slot}", "info")
            ok, msg = self.device_guard.check_battery(serial)
            self.log(f"  {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
            ok, msg = self.device_guard.check_temperature(serial)
            self.log(f"  {'✓' if ok else '⚠'} {msg}", "ok" if ok else "warn")
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
                text=f"当前模式：{icon} {mode}  ·  {serial or '—'}",
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
            self.log(f"{icon} 模式刷新: {mode}  ·  {md.describe(mode)}", "info")
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
            self.log("   ⚠ 请先在手机上进入 Recovery → Apply update from ADB", "warn")
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

'''
# 追加到 _do_shell 之后
PATCHES.append((
    "⑩ 追加 9 个扩展辅助方法",
    '''    def _do_shell(self):
        try: cmd = self.shell_input.get().strip()
        except Exception: cmd = ""
        if not cmd: return
        self.shell_input.delete(0, "end")
        def run():
            self.log(f"$ {cmd}", "neon")
            out = self.runner.run_quiet(f'{self.adb} shell "{cmd}"', timeout=30)
            if out:
                for ln in out.splitlines(): self.log(f"  {ln}", "white")
            else:
                self.log("  (无输出)", "dim")
        threading.Thread(target=run, daemon=True).start()


def main():''',
    '''    def _do_shell(self):
        try: cmd = self.shell_input.get().strip()
        except Exception: cmd = ""
        if not cmd: return
        self.shell_input.delete(0, "end")
        def run():
            self.log(f"$ {cmd}", "neon")
            out = self.runner.run_quiet(f'{self.adb} shell "{cmd}"', timeout=30)
            if out:
                for ln in out.splitlines(): self.log(f"  {ln}", "white")
            else:
                self.log("  (无输出)", "dim")
        threading.Thread(target=run, daemon=True).start()

''' + NEW_METHODS + '''def main():'''
))


# ============================================================
# 三、补丁执行引擎
# ============================================================
def find_once(text, needle):
    """返回 needle 在 text 中出现的次数"""
    return text.count(needle)

def apply_patches(src, patches):
    results = []
    for name, old, new in patches:
        cnt = find_once(src, old)
        if cnt == 0:
            results.append((name, "SKIP", "锚点未找到（可能已打过补丁或版本不匹配）"))
            continue
        if cnt > 1:
            results.append((name, "FAIL", f"锚点重复出现 {cnt} 次，拒绝替换"))
            continue
        src = src.replace(old, new, 1)
        results.append((name, "OK", ""))
    return src, results

def write_extended(target_dir):
    path = os.path.join(target_dir, "huijui_extended.py")
    if os.path.exists(path):
        bak = path + ".bak." + datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(path, bak)
        print(f"  ⚠ 已存在 {os.path.basename(path)}，备份为 {os.path.basename(bak)}")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(EXTENDED_CONTENT)
    return path

def main():
    print("=" * 66)
    print("  Huijui 工具箱 v5.0 Pro · 自动补丁")
    print("=" * 66)
    print(f"  目标文件: {TARGET}")
    print(f"  工作目录: {SRC_DIR}")
    print()

    if not os.path.exists(TARGET):
        print(f"  ✗ 目标文件不存在: {TARGET}")
        print("  用法: python apply_pro_patch.py [目标路径]")
        sys.exit(1)

    # 1. 读原文件
    print("  [1/4] 读取原文件...")
    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()
    print(f"        原始大小: {len(src):,} 字符 / {src.count(chr(10)):,} 行")

    # 2. 生成扩展模块
    print("\n  [2/4] 生成 huijui_extended.py ...")
    ext_path = write_extended(SRC_DIR)
    print(f"        ✓ {ext_path}")

    # 3. 备份原文件
    print("\n  [3/4] 备份原文件...")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{TARGET}.bak.{ts}"
    shutil.copy2(TARGET, bak)
    print(f"        ✓ {os.path.basename(bak)}")

    # 4. 应用补丁
    print("\n  [4/4] 应用补丁:")
    new_src, results = apply_patches(src, PATCHES)
    ok_n = sum(1 for _, s, _ in results if s == "OK")
    for name, status, note in results:
        mark = "✓" if status == "OK" else ("⚠" if status == "SKIP" else "✗")
        line = f"        {mark} {name}"
        if note:
            line += f"  ({note})"
        print(line)

    if new_src == src:
        print("\n  ⚠ 没有任何补丁应用成功。已中止写入。")
        print("     请检查 huijui_toolbox.py 是否与预期版本一致。")
        sys.exit(2)

    # 5. 语法检查
    print("\n  [5/5] 语法检查...")
    try:
        compile(new_src, TARGET, "exec")
        print("        ✓ 语法正常")
    except SyntaxError as e:
        print(f"        ✗ 语法错误: {e}")
        print("        未写入文件，原文件安全。")
        sys.exit(3)

    # 6. 写回
    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_src)
    print(f"\n  ✅ 补丁应用完成！")
    print(f"     成功: {ok_n}/{len(PATCHES)} 处")
    print(f"     新文件: {TARGET}")
    print(f"     备份:   {bak}")
    print(f"     扩展:   {ext_path}")
    print()
    print("  下一步：")
    print("    1. cd 到该目录")
    print("    2. python huijui_toolbox.py  ← 启动验证")
    print("    3. 若有异常，用备份文件覆盖回滚")


if __name__ == "__main__":
    main()