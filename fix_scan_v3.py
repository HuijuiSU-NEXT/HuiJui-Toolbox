# fix_scan_v3.py
import os
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(BASE, "main_final.py")

OLD_SCAN = '''    def scan_device(e=None):
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      page.update()
      def run():
        res = scan_device_data()
        apply_device_state(res, manual=True)
      threading.Thread(target=run, daemon=True).start()'''

NEW_SCAN = '''    def scan_device(e=None):
      print("🔥 [DEBUG] scan_device 点击触发了！")
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      try: page.update()
      except Exception as ue: print(f"UI刷新失败: {ue}")
      
      def run():
        try:
          res = scan_device_data()
          print(f"🔥 [DEBUG] 扫描结果: {res}")
          apply_device_state(res, manual=True)
        except Exception as ex:
          import traceback
          traceback.print_exc()
          print(f"❌ [DEBUG] 扫描异常: {ex}")
          status_dot.bgcolor = "#E05070"
          device_status_text.value = f"失败: {str(ex)[:20]}"
          loading_ring.visible = False
          try: page.update()
          except: pass
      threading.Thread(target=run, daemon=True).start()'''

OLD_AUTO = '''    def auto_scan_loop():
      time.sleep(1)
      while getattr(page, "is_running", True):
        try:
          res = scan_device_data()
          apply_device_state(res, manual=False)
        except Exception: pass
        time.sleep(2.5)'''

NEW_AUTO = '''    def auto_scan_loop():
      time.sleep(1)
      while getattr(page, "is_running", True):
        try:
          res = scan_device_data()
          apply_device_state(res, manual=False)
        except Exception as e:
          print(f"❌ [DEBUG] 自动扫描异常: {e}")
        time.sleep(2.5)'''

def main():
  if not os.path.isfile(TARGET):
    print(f"[X] 找不到 {TARGET}")
    sys.exit(1)
  with open(TARGET, "r", encoding="utf-8") as f:
    content = f.read()

  ok = False
  if OLD_SCAN in content:
    content = content.replace(OLD_SCAN, NEW_SCAN, 1)
    print("[OK] scan_device 已注入调试与异常捕获")
    ok = True
  else:
    print("[!] scan_device 没匹配上（可能你自己改过）")

  if OLD_AUTO in content:
    content = content.replace(OLD_AUTO, NEW_AUTO, 1)
    print("[OK] auto_scan_loop 已注入异常打印")
    ok = True
  else:
    print("[!] auto_scan_loop 没匹配上（可能你自己改过）")

  if not ok:
    print("[X] 没有任何替换发生，文件未修改。")
    sys.exit(2)

  try:
    compile(content, TARGET, "exec")
  except SyntaxError as e:
    print(f"[X] 语法预检失败: {e}")
    sys.exit(3)

  shutil.copy2(TARGET, TARGET + ".bak_scan3")
  with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)
  print("[✅] 抓虫完成！请启动程序并点击扫描。")

if __name__ == "__main__":
  main()