import os
import re

# ==========================================
# 修复 1：干掉 pages/settings.py 里的 FFmpeg 转码
# ==========================================
settings_path = "pages/settings.py"
if os.path.exists(settings_path):
  with open(settings_path, "r", encoding="utf-8") as f:
    s_content = f.read()
  
  # 精准匹配那段恶心的转码代码
  old_ffmpeg_code = re.search(r"if ext in \['\.mp4', '\.webm', '\.mov', '\.gif'\]:.*?print\(f\"\[FFmpeg\] 转码成功: \{new_filepath\}\"\)", s_content, re.DOTALL)
  
  if old_ffmpeg_code:
    new_code = """if ext in ['.mp4', '.webm', '.mov', '.gif']:
          # 🚨 已由极客强制修复：保留原画质，直接复制，绝不转码！
          shutil.copy2(src_path, new_filepath)"""
    s_content = s_content.replace(old_ffmpeg_code.group(0), new_code)
    
    # 顺手把后缀强制改成原后缀，防止因为原来写了 .gif 导致视频无法播放
    s_content = s_content.replace("new_filepath = new_filepath.replace(ext, '.gif')", "new_filepath = os.path.join(BASE_DIR, 'assets', f'wallpaper_{int(time.time())}{ext}')")
    
    with open(settings_path, "w", encoding="utf-8") as f:
      f.write(s_content)
    print("✅ pages/settings.py: FFmpeg 毒瘤已切除，画质原地起飞！")
  else:
    print("⚠️ 没找到 settings.py 里的 FFmpeg 代码，可能格式有变。")


# ==========================================
# 修复 2：干掉 ui_pages.py 里的假清除逻辑
# ==========================================
ui_path = "ui_pages.py"
if os.path.exists(ui_path):
  with open(ui_path, "r", encoding="utf-8") as f:
    u_content = f.read()
  
  old_reset = re.search(r"def reset_bg\(_\):.*?page\.update\(\)", u_content, re.DOTALL)
  
  if old_reset:
    new_reset = """def reset_bg(_):
    CFG.set("bg_image", "")
    # 1. 重置渐变背景
    page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B", "#0F172A"]))
    
    # 2. 🚨 暴力清除背景 UI 层
    # 遍历整个页面的控件，把背景的 Image 和 Video 全部移除
    for control in page.controls[:]:
      if isinstance(control, ft.Image) or isinstance(control, ft.Video):
        page.controls.remove(control)
    
    # 如果使用了 Stack 嵌套，尝试重置 Stack 的底层
    if hasattr(page, 'views') and page.views:
      for view in page.views:
        for ctrl in view.controls[:]:
          if isinstance(ctrl, ft.Stack):
            # 假设壁纸永远是 Stack 的第一个元素
            if len(ctrl.controls) > 0 and (isinstance(ctrl.controls[0], ft.Image) or isinstance(ctrl.controls[0], ft.Video)):
              ctrl.controls[0] = ft.Container() # 用空容器替换
    
    page.update()"""
    u_content = u_content.replace(old_reset.group(0), new_reset)
    
    with open(ui_path, "w", encoding="utf-8") as f:
      f.write(u_content)
    print("✅ ui_pages.py: 暴力重置逻辑已注入，一键清除壁纸彻底生效！")
  else:
    print("⚠️ 没找到 ui_pages.py 里的 reset_bg 函数。")
