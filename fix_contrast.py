# fix_contrast.py
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE, "main_final.py")

# 替换 1: 状态文字从灰蓝改为纯白 + 极粗
OLD_STATUS = 'device_status_text = ft.Text("等待扫描", size=13, weight=ft.FontWeight.W_600, color="#A0ABC0")'
NEW_STATUS = 'device_status_text = ft.Text("等待扫描", size=13, weight=ft.FontWeight.W_900, color="#FFFFFF")'

# 替换 2: 右侧的四个值 info_xxx 改大改亮
OLD_INFO = '''    info_brand = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_model = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_android = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_root = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)'''
NEW_INFO = '''    info_brand = ft.Text("—", color="#FFFFFF", size=14, weight=ft.FontWeight.BOLD)
    info_model = ft.Text("—", color="#FFFFFF", size=14, weight=ft.FontWeight.BOLD)
    info_android = ft.Text("—", color="#FFFFFF", size=14, weight=ft.FontWeight.BOLD)
    info_root = ft.Text("—", color="#FFFFFF", size=14, weight=ft.FontWeight.BOLD)'''

# 替换 3: 左侧标签文字改亮色 + 加粗
OLD_LABELS = '''            ft.Row([ft.Text("品牌", color="#6E7B91", size=12), info_brand], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("型号", color="#6E7B91", size=12), info_model], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("系统", color="#6E7B91", size=12), info_android], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Root", color="#6E7B91", size=12), info_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)'''
NEW_LABELS = '''            ft.Row([ft.Text("品牌", color="#E2E8F0", size=12, weight=ft.FontWeight.W_600), info_brand], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("型号", color="#E2E8F0", size=12, weight=ft.FontWeight.W_600), info_model], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("系统", color="#E2E8F0", size=12, weight=ft.FontWeight.W_600), info_android], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Root", color="#E2E8F0", size=12, weight=ft.FontWeight.W_600), info_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)'''

# 替换 4: 卡片背景加深（防止透出高光壁纸），加个保险的 0.75 透明度纯黑
OLD_BG = 'padding=15, bgcolor=page.ui_style["card_bg"], border_radius=16, border=page.ui_style["card_border"]'
NEW_BG = 'padding=15, bgcolor=ft.Colors.with_opacity(0.75, "#090A0F"), border_radius=16, border=page.ui_style["card_border"]'

def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到 {TARGET}")
    sys.exit(1)
  
  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

  changes = 0
  if OLD_STATUS in content:
    content = content.replace(OLD_STATUS, NEW_STATUS, 1)
    print("[OK] 状态文字已调亮加粗")
    changes += 1
  if OLD_INFO in content:
    content = content.replace(OLD_INFO, NEW_INFO, 1)
    print("[OK] 设备信息值已变大变亮")
    changes += 1
  if OLD_LABELS in content:
    content = content.replace(OLD_LABELS, NEW_LABELS, 1)
    print("[OK] 设备标签已提亮防瞎")
    changes += 1
  if OLD_BG in content:
    content = content.replace(OLD_BG, NEW_BG, 1)
    print("[OK] 卡片背景已加深，隔绝高光壁纸")
    changes += 1

  if changes == 0:
    print("[!] 没找到要修改的代码块，可能被改过或缩进不对。")
    sys.exit(2)

  try:
    compile(content, TARGET, "exec")
  except SyntaxError as e:
    print(f"[X] 语法预检失败: {e}")
    sys.exit(3)

  shutil.copy2(TARGET, TARGET + ".bak_contrast")
  with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
  print(f"[✅] 对比度强化完成！共修改 {changes} 处。")

if __name__ == "__main__":
  main()