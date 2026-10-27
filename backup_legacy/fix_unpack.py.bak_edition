# -*- coding: utf-8 -*-
import shutil

SRC = r"D:\Huijui\v4_python\src\huijui_toolbox.py"
shutil.copy(SRC, SRC + ".bak_unpack")
print("已备份:", SRC + ".bak_unpack")

with open(SRC, "r", encoding="utf-8") as f:
    code = f.read()

old = """        cmd = f'{self.dumper} -q -p {PAYLOAD_PARTS} payload.bin'
        ok, errs = self._run_step(cmd, "解包", timeout=1800,
                                  cwd=self.current_dir, on_line=on_line)"""

new = '''        # v5.0 Pro 修复：动态识别 payload 内实际分区，避免报错退出
        self.log("  🔍 识别 payload 内实际分区...", "info")
        list_out = self.runner.run_quiet(
            f'{self.dumper} -l payload.bin', timeout=180, cwd=self.current_dir)
        available = set()
        for ln in (list_out or "").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            m = re.search(r'(?:Partition Name|partition)[\\s:]+([a-zA-Z0-9_]+)',
                          ln, re.I)
            if m:
                available.add(m.group(1).lower())
                continue
            if re.match(r'^[a-zA-Z0-9_]+$', ln):
                available.add(ln.lower())
        requested = [p.strip() for p in PAYLOAD_PARTS.split(',') if p.strip()]
        if available:
            real_parts = [p for p in requested if p in available]
            missing = [p for p in requested if p not in available]
            if missing:
                self.log(f"  ℹ 卡刷包内无以下分区，已跳过：{', '.join(missing)}", "dim")
            if real_parts:
                part_arg = "-p " + ",".join(real_parts)
                self.log(f"  ✓ 实际解包 {len(real_parts)} 个分区", "ok")
            else:
                part_arg = ""
                self.log("  ⚠ 未匹配到任何分区，改为全量解包", "warn")
        else:
            part_arg = ""
            self.log("  ⚠ 无法识别分区列表，改为全量解包", "warn")

        cmd = f'{self.dumper} -q {part_arg} payload.bin'.strip()
        ok, errs = self._run_step(cmd, "解包", timeout=1800,
                                  cwd=self.current_dir, on_line=on_line)'''

if old not in code:
    print("ERR 未找到目标代码段")
else:
    code = code.replace(old, new, 1)
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(code)
    print("OK 修复成功")

input("按回车退出")