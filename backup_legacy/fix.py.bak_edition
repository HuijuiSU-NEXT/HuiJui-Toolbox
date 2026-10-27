# -*- coding: utf-8 -*-
"""Huijui 工具箱 v5.0 Pro - 全局修复脚本"""
import os, sys, shutil

P = r'D:\Huijui\v4_python\src\huijui_toolbox.py'
if not os.path.exists(P):
    print(f"✗ 文件不存在: {P}"); sys.exit(1)

with open(P, encoding='utf-8') as f:
    s = f.read()
orig = s
log = []

def rep(old, new, tag):
    global s
    if old in s:
        s = s.replace(old, new, 1)
        log.append(f"  OK  {tag}")
    else:
        log.append(f"  FAIL {tag}  (未匹配)")

# ========== [1] get_app_dir 兼容 Nuitka onefile ==========
rep(
    "def get_resource_path(rel):",
    '''def get_app_dir():
    """返回 exe 所在目录（兼容 Nuitka onefile / PyInstaller / 源码）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    env = os.environ.get("NUITKA_ONEFILE_BINARY")
    if env:
        return os.path.dirname(os.path.abspath(env))
    if "__compiled__" in globals():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(rel):''',
    "[1] 插入 get_app_dir() 函数"
)

# ========== [2] current_dir 计算 ==========
rep(
    """self.current_dir = os.path.dirname(os.path.abspath(
            sys.argv[0] if getattr(sys,'frozen',False) else __file__))""",
    "self.current_dir = get_app_dir()",
    "[1] current_dir 改用 get_app_dir"
)

# ========== [3] _cfg_path ==========
rep(
    """def _cfg_path():
    base = os.path.dirname(os.path.abspath(
        sys.argv[0] if getattr(sys,'frozen',False) else __file__))
    return os.path.join(base, CONFIG_FILE)""",
    """def _cfg_path():
    return os.path.join(get_app_dir(), CONFIG_FILE)""",
    "[1] _cfg_path 改用 get_app_dir"
)

# ========== [4] tcpip 里的 grep ==========
rep(
    '''            ip = self.runner.run_quiet(
                f"{self.adb} -s {dev} shell ip route | grep wlan")
            m = re.search(r"src (\\d+\\.\\d+\\.\\d+\\.\\d+)", ip)''',
    '''            routes = self.runner.run_quiet(
                f"{self.adb} -s {dev} shell ip route")
            wlan_line = ""
            for ln in routes.splitlines():
                if "wlan" in ln:
                    wlan_line = ln; break
            m = re.search(r"src (\\d+\\.\\d+\\.\\d+\\.\\d+)",
                          wlan_line or routes)''',
    "[2] tcpip 提取 IP 用 Python 过滤"
)

# ========== [5] 日志环形缓冲 ==========
rep(
    """                if self._log_count > LOG_MAX_LINES:
                    try:
                        self.log_box.delete("1.0", f"{self._log_count - LOG_MAX_LINES}.0")
                        self._log_count = LOG_MAX_LINES
                    except Exception: pass""",
    """                if self._log_count > LOG_MAX_LINES:
                    try:
                        excess = self._log_count - LOG_MAX_LINES
                        self.log_box.delete("1.0", f"{excess + 1}.0")
                        self._log_count = LOG_MAX_LINES
                    except Exception: pass""",
    "[3] 日志环形缓冲行号修复"
)

# ========== [6] 主题切换不弹窗 + 刷机中不重建 ==========
rep(
    '''    def _toggle_theme(self):
        cur = cfg("theme") or "dark"
        new = "light" if cur == "dark" else "dark"
        cfg("theme", new); T.set(new)
        if messagebox.askyesno("主题切换",
            f"已切换到 {'亮色' if new=='light' else '暗黑'}。\\n"
            "是否立即重建界面？（正在进行的任务不受影响）"):
            self._rebuild_ui()
        else:
            Toast(self, "已保存，重启后生效", kind="info")

    def _on_theme_change(self, val):
        cfg("theme", val); T.set(val)
        if messagebox.askyesno("主题切换", "是否立即重建界面？"):
            self._rebuild_ui()
        else:
            Toast(self, "已保存，重启后生效", kind="info")''',
    '''    def _toggle_theme(self):
        cur = cfg("theme") or "dark"
        new = "light" if cur == "dark" else "dark"
        cfg("theme", new); T.set(new)
        self._apply_theme_change()

    def _on_theme_change(self, val):
        cfg("theme", val); T.set(val)
        self._apply_theme_change()

    def _apply_theme_change(self):
        if self.is_running:
            Toast(self, "主题已保存，刷机结束后生效",
                  kind="info", duration=3000)
            return
        self._rebuild_ui()
        Toast(self, f"主题已切换：{cfg('theme')}",
              kind="ok", duration=1500)''',
    "[4] 主题切换免弹窗 + 刷机中延后"
)

# ========== [7] Switch 亮色主题对比度 ==========
rep(
    """            ctk.CTkSwitch(row, text="", variable=var, command=on_change,
                           fg_color=T.BORDER_LIGHT, progress_color=T.ACCENT,
                           button_color=T.TEXT_MAIN,
                           button_hover_color=T.ACCENT_HOVER).pack(side="right")""",
    """            ctk.CTkSwitch(row, text="", variable=var, command=on_change,
                           fg_color=T.BORDER_LIGHT, progress_color=T.ACCENT,
                           button_color=T.BG_PANEL,
                           button_hover_color=T.ACCENT_HOVER,
                           text_color=T.TEXT_MAIN).pack(side="right")""",
    "[5] Switch 按钮亮色对比度"
)

# ========== 输出 ==========
print("=== 修复结果 ===")
for line in log:
    print(line)

if s != orig:
    backup = P + ".bak"
    if not os.path.exists(backup):
        shutil.copy(P, backup)
        print(f"\n原文件已备份: {backup}")
    with open(P, 'w', encoding='utf-8') as f:
        f.write(s)
    print("写入完成")
else:
    print("\n无改动（脚本重复跑了？）")

try:
    import py_compile
    py_compile.compile(P, doraise=True)
    print("[OK] 语法检查通过")
except Exception as e:
    print(f"[FAIL] 语法检查: {e}")