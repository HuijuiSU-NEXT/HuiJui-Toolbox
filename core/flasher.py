# core/flasher.py
import os
import sys
import re
import time
import sqlite3
import zipfile
import shutil
import subprocess
from datetime import datetime

try:
    from .adb_core import (
        BASE_DIR, BIN_DIR, ADB, FASTBOOT, DUMPER, NO_WINDOW,
        run_cmd, get_active_serial, list_fastboot_devices,
        reboot_to_bootloader, fastboot_flash, fastboot_reboot,
        shell, get_slot, probe_partition, is_admin, CommandRunner, CFG
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.adb_core import (
        BASE_DIR, BIN_DIR, ADB, FASTBOOT, DUMPER, NO_WINDOW,
        run_cmd, get_active_serial, list_fastboot_devices,
        reboot_to_bootloader, fastboot_flash, fastboot_reboot,
        shell, get_slot, probe_partition, is_admin, CommandRunner, CFG
    )

WORK_DIR = os.path.join(BASE_DIR, "flash_workspace")

COMMON_PHYSICAL = [
    ("vbmeta", "vbmeta.img", ["--disable-verity", "--disable-verification"]),
    ("vbmeta_system", "vbmeta_system.img", []),
    ("vbmeta_vendor", "vbmeta_vendor.img", []),
    ("boot", "boot.img", []),
    ("init_boot", "init_boot.img", []),
    ("vendor_boot", "vendor_boot.img", []),
    ("dtbo", "dtbo.img", []),
    ("recovery", "recovery.img", []),
]
COMMON_LOGICAL = [
    ("system", "system.img"), ("system_ext", "system_ext.img"),
    ("product", "product.img"), ("vendor", "vendor.img"),
    ("odm", "odm.img"), ("mi_ext", "mi_ext.img"),
    ("vendor_dlkm", "vendor_dlkm.img"), ("system_dlkm", "system_dlkm.img"),
]
DANGEROUS_DEFAULT = {
    "xbl", "abl", "tz", "hyp", "keymaster", "devcfg", "modemst1", "modemst2",
    "fsg", "bluetooth", "modem", "dsp", "bootloader", "radio", "sbl", "aboot",
}

class BackupManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def create_backup_dir(self):
        d = os.path.join(self.base_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        try:
            os.makedirs(d, exist_ok=True)
            return d
        except Exception:
            return None

    def backup_partition(self, dev, partition, dest_dir, log_cb):
        out_local = os.path.join(dest_dir, f"{partition}.img")
        remote = f"/sdcard/_backup_{partition}.img"
        try:
            blk = probe_partition(dev, partition, get_slot(dev))
            if not blk:
                log_cb(f"  ⚠ 未找到 {partition} 分区，跳过")
                return None
            log_cb(f"  ⏳ 备份 {partition}...")
            cmd = f'"{ADB}" -s {dev} shell "su -c \'dd if={blk} of={remote}\'"'
            r = subprocess.run(cmd, shell=True, capture_output=True, timeout=120, creationflags=NO_WINDOW)
            if r.returncode != 0:
                log_cb(f"  ⚠ {partition} 备份失败（可能未授权 su）")
                return None
            subprocess.run(f'"{ADB}" -s {dev} pull {remote} "{out_local}"', shell=True, capture_output=True, timeout=120, creationflags=NO_WINDOW)
            shell(dev, f"rm {remote}")
            if os.path.exists(out_local):
                size_mb = os.path.getsize(out_local) / (1024 * 1024)
                log_cb(f"  ✓ {partition}（{size_mb:.1f} MB）")
                return out_local
            return None
        except Exception as e:
            log_cb(f"  ⚠ {partition} 异常: {e}")
            return None

class FlashHistory:
    def __init__(self, base_dir):
        self.db = os.path.join(base_dir, "huijui_history.db")
        self._init()
        
    def _init(self):
        try:
            with sqlite3.connect(self.db) as c:
                c.execute("""CREATE TABLE IF NOT EXISTS history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, brand TEXT, model TEXT, zip TEXT, duration INTEGER, success INTEGER, note TEXT)""")
        except Exception: pass
        
    def add(self, brand, model, zip_name, duration, success, note=""):
        try:
            with sqlite3.connect(self.db) as c:
                c.execute("INSERT INTO history(ts,brand,model,zip,duration,success,note) VALUES(?,?,?,?,?,?,?)",
                          (datetime.now().isoformat(), brand, model, zip_name, duration, 1 if success else 0, note))
        except Exception: pass
        
    def all(self, limit=200):
        try:
            with sqlite3.connect(self.db) as c:
                return c.execute("SELECT ts, brand, model, zip, duration, success FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        except Exception: return []
        
    def clear(self):
        try:
            with sqlite3.connect(self.db) as c:
                c.execute("DELETE FROM history")
        except Exception: pass

class Flasher:
    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.history = FlashHistory(BASE_DIR)
        self.stop_flag = False

    def _log(self, msg, cb):
        if cb: cb(msg)

    def _progress(self, pct, stage, cb):
        if cb: cb(pct, stage)

    def check_firmware(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path) as z:
                if "payload_properties.txt" in z.namelist():
                    txt = z.read("payload_properties.txt").decode("utf-8", "ignore")
                    m = re.search(r"post-build[=:]\s*([^\s]+)", txt)
                    if m:
                        parts = m.group(1).split("/")
                        if len(parts) > 1:
                            return parts[1]
        except Exception: pass
        return None

    def flash(self, zip_path, on_log=None, on_progress=None, on_warn=None, on_need_wipe=None, on_emergency=None):
        self.stop_flag = False
        start_time = time.time()
        zip_name = os.path.basename(zip_path)
        success = False
        self.runner.clear_debug()
        
        try:
            self._log("▸ 步骤 1：环境检测", on_log)
            dev = get_active_serial()
            is_fastboot_mode = False
            
            if not dev:
                fdevs = list_fastboot_devices()
                if fdevs:
                    is_fastboot_mode = True
                    self._log("  ✓ 已连接 Fastboot 模式", on_log)
                else:
                    self._log("  ✗ 未检测到设备，请连接手机", on_log)
                    return False
            else:
                self._log(f"  ✓ 已连接 ADB 模式: {dev}", on_log)
                brand = self.runner.run_quiet(f'"{ADB}" shell getprop ro.product.brand')
                model = self.runner.run_quiet(f'"{ADB}" shell getprop ro.product.device')
                
                self._log("▸ 步骤 2：校验卡刷包完整性", on_log)
                pkg_device = self.check_firmware(zip_path)
                if pkg_device and model and pkg_device.lower() != model.lower():
                    warn_msg = f"⚠️ 警告：该卡刷包代号为 [{pkg_device}]，当前手机为 [{model}]。\n刷入不匹配的包极大概率导致变砖！\n\n是否仍要强行继续？"
                    if on_warn and not on_warn(warn_msg):
                        self._log("  ✗ 用户取消刷机", on_log)
                        return False
                    self._log("  ⚠️ 用户强行继续刷入", on_log)
                else:
                    self._log("  ✓ 卡刷包校验通过", on_log)

            self._progress(10, "提取载荷", on_progress)
            self._log("▸ 步骤 3：解压 payload.bin", on_log)
            if os.path.exists(WORK_DIR): shutil.rmtree(WORK_DIR, ignore_errors=True)
            os.makedirs(WORK_DIR, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path) as z:
                    if "payload.bin" not in z.namelist():
                        self._log("  ✗ 包内无 payload.bin", on_log)
                        return False
                    z.extract("payload.bin", WORK_DIR)
            except Exception as e:
                self._log(f"  ✗ 解压失败: {e}", on_log)
                return False

            self._progress(20, "解包镜像", on_progress)
            self._log("▸ 步骤 4：解包分区镜像", on_log)
            list_out = self.runner.run_quiet(f'"{DUMPER}" -l payload.bin', cwd=WORK_DIR)
            available = set()
            for ln in (list_out or "").splitlines():
                ln = ln.strip()
                if re.match(r'^[a-zA-Z0-9_]+$', ln): available.add(ln.lower())
            
            requested = [it[0] for it in COMMON_PHYSICAL] + [it[0] for it in COMMON_LOGICAL]
            real_parts = [p for p in requested if p in available] if available else requested
            part_arg = "-p " + ",".join(real_parts) if real_parts else ""

            cmd = f'"{DUMPER}" -q {part_arg} payload.bin'.strip()
            rc, errs = self.runner.run(cmd, cwd=WORK_DIR, timeout=1800)
            if rc != 0:
                self._log(f"  ✗ 解包失败: {errs}", on_log)
                return False
                
            extracted_dir = WORK_DIR
            for root, dirs, files in os.walk(WORK_DIR):
                if "boot.img" in files or "system.img" in files:
                    extracted_dir = root; break

            self._progress(40, "重启至 Fastboot", on_progress)
            self._log("▸ 步骤 5：重启至 Bootloader 刷入底层", on_log)
            if not is_fastboot_mode and dev:
                self.runner.run_quiet(f'"{ADB}" -s {dev} reboot bootloader')
                time.sleep(6)
                self.runner.run_quiet(f'"{FASTBOOT}" devices')
                
            valid_phys = [it for it in COMMON_PHYSICAL if os.path.exists(os.path.join(extracted_dir, it[1]))]
            for i, (name, fn, args) in enumerate(valid_phys):
                if self.stop_flag: return False
                self._log(f"  → 刷入 {name}...", on_log)
                arg_str = " ".join(args) + " " if args else ""
                cmd = f'"{FASTBOOT}" {arg_str}flash {name} "{os.path.join(extracted_dir, fn)}"'
                rc, errs = self.runner.run(cmd, timeout=180)
                if rc != 0:
                    self._log(f"  ✗ 刷入 {name} 失败: {errs}", on_log)
                    if on_emergency: on_emergency(f"刷入 {name} 失败，可能包损坏或线材问题。")
                    return False
                self._progress(40 + 30*(i+1)/len(valid_phys), f"刷入 {name}", on_progress)

            valid_log = [it for it in COMMON_LOGICAL if os.path.exists(os.path.join(extracted_dir, it[1]))]
            if valid_log:
                self._progress(70, "切换到 Fastbootd", on_progress)
                self._log("▸ 步骤 6：切换到 Fastbootd 刷入系统", on_log)
                self.runner.run_quiet(f'"{FASTBOOT}" reboot fastboot')
                time.sleep(8)
                
                for i, (name, fn) in enumerate(valid_log):
                    if self.stop_flag: return False
                    self._log(f"  → 刷入 {name}...", on_log)
                    rc, errs = self.runner.run(f'"{FASTBOOT}" flash {name} "{os.path.join(extracted_dir, fn)}"', timeout=600)
                    if rc != 0:
                        self._log(f"  ✗ 刷入 {name} 失败: {errs}", on_log)
                        if on_emergency: on_emergency(f"刷入 {name} 失败，系统可能无法开机。")
                        return False
                    self._progress(70 + 20*(i+1)/len(valid_log), f"刷入 {name}", on_progress)

            self._progress(95, "完成", on_progress)
            self._log("▸ 步骤 7：收尾处理", on_log)
            
            do_wipe = False
            if on_need_wipe:
                do_wipe = on_need_wipe()
                
            if do_wipe:
                self._log("  🧹 正在清空数据 (userdata)...", on_log)
                self.runner.run_quiet(f'"{FASTBOOT}" erase userdata')
                self._log("  ✓ 数据已清空", on_log)

            self._log("  🔄 正在重启设备...", on_log)
            self.runner.run_quiet(f'"{FASTBOOT}" reboot')
            
            self._log("🎉 刷机成功！首次开机需 10-15 分钟。", on_log)
            success = True
            return True

        except Exception as e:
            self._log(f"💥 严重异常: {e}", on_log)
            if on_emergency: on_emergency(str(e))
            return False
        finally:
            dur = int(time.time() - start_time)
            self.history.add("?", "?", zip_name, dur, success)