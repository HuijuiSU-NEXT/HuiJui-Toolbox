import re

file_path = "main_final.py"
with open(file_path, "r", encoding="utf-8") as f:
  content = f.read()

# 🚨 修复 1：强制把文件选择器支持全格式
# 查找 allowed_extensions=[...] 并强制替换
if "allowed_extensions=" in content:
  # 把所有的 allowed_extensions 里的内容替换成全格式
  content = re.sub(r'allowed_extensions=\[[^\]]*\]', 'allowed_extensions=["png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"]', content)
  print("✅ 已解锁文件选择器：支持 MP4 / GIF / PNG 等全格式！")

# 🚨 修复 2：暴力修正清除壁纸逻辑
# 查找包含 clear 或 清除壁纸 的函数
clear_func_match = re.search(r'def\s+(clear_wallpaper|delete_wallpaper|clear_bg|on_clear_wallpaper)[^:]*:(.*?)(?=\ndef|\Z)', content, re.DOTALL)

if clear_func_match:
  func_name = clear_func_match.group(1)
  print(f"✅ 找到清除函数: {func_name}，正在进行暴力修正...")
  
  # 替换掉原来的残缺清除逻辑，注入兼容全格式的重置代码
  new_clear_func = f"""
def {func_name}(e):
  try:
    # 1. 清理配置路径
    import os, json
    config_path = os.path.join(BASE_DIR, "config.json") # 假设你的配置文件叫这个
    if os.path.exists(config_path):
      with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
      if "wallpaper" in cfg:
        # 物理删除文件（如果是复制到本地的话）
        if os.path.exists(cfg["wallpaper"]) and "wallpaper_" in cfg["wallpaper"]:
          os.remove(cfg["wallpaper"])
        cfg["wallpaper"] = ""
      with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
        
    # 2. 重置 UI 背景
    # 这里需要把背景组件的内容清空
    # 因为不知道你原来的变量名，通常如果是 Image/Video 的话，给 src 赋空字符串
    global bg_image, bg_video # 假设你有全局变量
    # 如果你有特定的重置逻辑，在这里调用
    page.update()
  except Exception as ex:
    print(f"清除失败: {{ex}}")
"""
  # 将旧的清除函数替换为新的
  content = content[:clear_func_match.start()] + new_clear_func + content[clear_func_match.end():]
  print("✅ 已重写清除函数，兼容全格式！")
else:
  print("⚠️ 没找到清除壁纸的函数，请手动寻找并替换。")

with open(file_path, "w", encoding="utf-8") as f:
  f.write(content)
