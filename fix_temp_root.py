# fix_temp_root.py · 一键修复 pages/temp_root.py 的必炸雷
# 铁律 3 合规：只做精确 str.replace，先备份，语法预检通过才写回

import os
import shutil
import sys

TARGET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "temp_root.py")

# (old, new, 说明) —— old 必须与源文件逐字符一致（含缩进）
REPLACEMENTS = [
  (
    "import re\n",
    "import re\nimport urllib.request\nimport zipfile\nimport shutil\n",
    "补齐 urllib.request / zipfile / shutil 三个缺失 import（修 NameError）",
  ),
  (
    '  def show_snackbar(msg):\n'
    '    page.snack_bar = ft.SnackBar(content=ft.Text(msg, font_family="MiSans"), bgcolor=theme_color)\n'
    '    page.snack_bar.open = True\n'
    '    page.update()',
    '  def show_snackbar(msg, color=None):\n'
    '    page.snack_bar = ft.SnackBar(content=ft.Text(msg, font_family="MiSans"), bgcolor=color or theme_color)\n'
    '    page.snack_bar.open = True\n'
    '    page.update()',
    "show_snackbar 加 color 参数（修 TypeError: takes 1 positional argument but 2 were given）",
  ),
  (
    '  btn_import.on_click = lambda _: file_picker.pick_files(allowed_extensions=["conf", "json"])',
    '  btn_import.on_click = lambda _: page.run_task(file_picker.pick_files, allowed_extensions=["conf", "json"])',
    "pick_files 改用 page.run_task（修「导入 Profile」点了不弹框）",
  ),
  (
    '    if "device" not in out.lower():',
    '    if "\\tdevice" not in out:',
    "adb devices 判断改为 \\tdevice（修无设备被误判为有设备）",
  ),
  (
    '      cmd = f\'"{DUMPER_PATH}" -q -p boot,xbl_config "{payload_path}"\'',
    '      cmd = f\'"{DUMPER_PATH}" -q -p boot,xbl_config -o "{BASE_DIR}" "{payload_path}"\'',
    "payload-dumper-go 加 -o 指定输出目录（修 boot.img 找不到）",
  ),
]


def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到目标文件: {TARGET}")
    print("  请在 D:\\Huijui-Toolbox-Next 根目录下运行本脚本")
    sys.exit(1)

  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()
  original = content

  print("=" * 60)
  print(f"目标: {TARGET}")
  print("=" * 60)

  failed = []
  for old, new, desc in REPLACEMENTS:
    if old in content:
      content = content.replace(old, new, 1)
      print(f"[OK]  {desc}")
    else:
      failed.append(desc)
      print(f"[FAIL] {desc} —— 源片段未匹配")

  if failed:
    print("\n[!] 有替换失败，为保护源文件，本次不写回。")
    print("  多半是源文件已被改过，请把上面 [FAIL] 行贴给 AI 重新定位。")
    sys.exit(2)

  if content == original:
    print("\n[!] 内容无变化，可能已经修过了。")
    return

  # 语法预检：不通过绝不写回
  try:
    compile(content, TARGET, "exec")
  except SyntaxError as e:
    print(f"\n[X] 语法预检失败，不写回: {e}")
    sys.exit(3)

  backup = TARGET + ".bak"
  shutil.copy2(TARGET, backup)
  print(f"\n[OK]  原文件已备份 → {backup}")

  with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
  print(f"[OK]  已写回 → {TARGET}")
  print("\n[✅] 修复完成！下一步：python main_final.py 启动测试")
  print("   想回滚：copy pages\\temp_root.py.bak pages\\temp_root.py")


if __name__ == "__main__":
  main()