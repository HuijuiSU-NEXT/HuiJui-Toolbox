# fix_all_indent_final.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 重写 main_final.py ====================
main_code = '''import flet as ft
import flet_video as ftv
import threading
import time
import base64
import os
import glob
from core_api import scan_device_data, CFG
import ui_theme

from pages.dashboard import build_dashboard
from pages.flash import build_flash_page
from pages.temp_root import build_temp_root_page
from pages.history import build_history_page
from pages.settings import build_settings_page
from pages.terminal import build_terminal_page
from pages.backup import build_backup_page
from pages.scrcpy import build_scrcpy_page
from pages.mode_switch import build_mode_switch_page
from pages.rescue import build_rescue_page
from pages.module_repo import build_module_repo_page
from pages.drivers import build_drivers_page
from pages.wireless_adb import build_wireless_adb_page
from pages.scan import build_scan_page
from pages.mediatek_rescue import build_mediatek_rescue_page
from pages.flash_parts import build_flash_parts_page

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base64_image(filepath):
  try:
    if os.path.exists(filepath):
      with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
  except Exception:
    pass
  return ""

LOGO_B64 = get_base64_image(os.path.join(BASE_DIR, "assets", "logo.png"))

def main(page: ft.Page):
  CFG.set("onboarded", True)
  CFG.save()

  page.title = "HuiJui Toolbox Edition"
  page.theme_mode = ft.ThemeMode.DARK
  page.padding = 0
  page.spacing = 0
  page.bgcolor = "#0D1017"
  page.window.width = 1440
  page.window.height = 900
  page.window.min_width = 1150
  page.window.min_height = 800

  icon_path = os.path.join(BASE_DIR, "assets", "logo.ico")
  if os.path.exists(icon_path):
    page.window.icon = icon_path

  current_tab = {"idx": 0}

  bg_video = ftv.Video(expand=True, autoplay=True, playlist_mode=ftv.PlaylistMode.SINGLE, muted=True, visible=False, fit=ft.ImageFit.COVER)
  bg_image = ft.Image(fit=ft.ImageFit.COVER, expand=True, visible=False)
  ui_container = ft.Container(expand=True, bgcolor=ft.Colors.TRANSPARENT)
  
  main_stack = ft.Stack([bg_image, bg_video, ui_container], expand=True, fit=ft.StackFit.EXPAND)
  page.add(main_stack)

  def on_window_resize(e):
    if bg_video.visible:
      bg_video.update()
    if bg_image.visible:
      bg_image.update()
  page.on_resize = on_window_resize

  def update_wallpaper_hot():
    all_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    cover_path = os.path.join(BASE_DIR, "assets", "wallpaper_cover.jpg")
    
    video_files = [f for f in all_files if f.lower().endswith((".mp4", ".webm", ".mov", ".mkv", ".avi"))]
    
    if video_files:
      latest = max(video_files, key=os.path.getctime)
      src = os.path.basename(latest)
      abs_src = os.path.join(BASE_DIR, "assets", src)
      
      if os.path.exists(cover_path):
        bg_image.src = "wallpaper_cover.jpg"
        bg_image.visible = True
        print("🖼️ 已显示视频首帧封面")
      else:
        bg_image.visible = False
        
      bg_video.visible = False
      
      def load_video_thread():
        try:
          bg_video.playlist.clear()
          bg_video.playlist.append(ftv.VideoMedia(abs_src))
          bg_video.play()
          bg_video.update()
          print(f"🎬 已后台加载高清视频壁纸: {abs_src}")
          
          time.sleep(1.2)
          bg_video.visible = True
          bg_image.visible = False
          bg_video.update()
          bg_image.update()
          print("✨ 视频加载完毕，已切换至动态壁纸！")
        except Exception as e:
          print(f"❌ 视频加载失败: {e}")
          
      threading.Thread(target=load_video_thread, daemon=True).start()
      
    else:
      if all_files:
        latest = max(all_files, key=os.path.getctime)
        src = os.path.basename(latest)
        bg_video.visible = False
        bg_video.pause()
        bg_image.src = src
        bg_image.visible = True
        print(f"🖼️ 已更新图片壁纸: {src}")
      else:
        bg_video.visible = False
        bg_video.pause()
        bg_image.visible = False
        print("🧹 未找到壁纸文件")
        
    page.update()

  page.update_wallpaper_hot = update_wallpaper_hot
  update_wallpaper_hot()

  def build_main_ui():
    theme_color = ui_theme.setup_page_style(page)
    page.ui_style = ui_theme.get_ui_styles(theme_color)

    status_dot = ft.Container(width=10, height=10, bgcolor="#E05070", border_radius=5)
    device_status_text = ft.Text("等待扫描", size=13, weight=ft.FontWeight.W_600, color="#A0ABC0")
    loading_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=theme_color, visible=False)
    
    info_brand = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_model = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_android = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)
    info_root = ft.Text("—", color="white", size=13, weight=ft.FontWeight.BOLD)

    last_state = {"state": "OFFLINE", "sn": ""}

    def apply_device_state(res, manual=False):
      state = res["state"]
      sn = res.get("serial", "")
      if state == last_state["state"] and sn == last_state["sn"] and not manual: return
      last_state["state"] = state
      last_state["sn"] = sn

      if state == "OFFLINE": 
        device_status_text.value = "等待扫描"; status_dot.bgcolor = "#E05070"
      elif state == "NORMAL": 
        device_status_text.value = "已连接 (ADB)"; status_dot.bgcolor = "#3FBF6E"
      elif state in ("FASTBOOT", "RECOVERY", "SIDELOAD"): 
        device_status_text.value = f"{state}"; status_dot.bgcolor = "#F0A030"
      elif state == "FASTBOOTD": 
        device_status_text.value = "Fastbootd"; status_dot.bgcolor = "#A070E0"
      elif state in ("EDL", "BROM"): 
        device_status_text.value = f"{state} 模式"; status_dot.bgcolor = "#E05070"
      
      info_brand.value = res.get("brand", "—")
      info_model.value = res.get("model", "—")
      info_android.value = res.get("android", "—")
      info_root.value = res.get("root", "—")
      loading_ring.visible = False
      try: page.update()
      except: pass

    def scan_device(e=None):
      status_dot.bgcolor = "#F0A030"
      device_status_text.value = "扫描中..."
      loading_ring.visible = True
      page.update()
      def run():
        res = scan_device_data()
        apply_device_state(res, manual=True)
      threading.Thread(target=run, daemon=True).start()

    def auto_scan_loop():
      time.sleep(1)
      while getattr(page, "is_running", True):
        try:
          res = scan_device_data()
          apply_device_state(res, manual=False)
        except Exception: pass
        time.sleep(2.5)

    if not hasattr(page, "scan_thread_started"):
      page.is_running = True
      threading.Thread(target=auto_scan_loop, daemon=True).start()
      page.scan_thread_started = True

    side_panel = ft.Container(
      width=320, 
      bgcolor=page.ui_style["side_bg"], 
      border=ft.border.only(left=ft.border.BorderSide(1, ft.Colors.with_opacity(0.2, "white"))),
      padding=ft.padding.all(20),
      content=ft.Column([
        ft.Row([
          ft.Container(
            content=ft.Image(src_base64=LOGO_B64, fit=ft.ImageFit.CONTAIN),
            width=48, height=48, border_radius=12
          ) if LOGO_B64 else ft.Container(),
          ft.Column([ft.Text("HuiJui Toolbox Edition", size=16, weight=ft.FontWeight.W_900, color="white"), ft.Text("Matrix Engine", size=10, color=theme_color)], spacing=0, expand=True),
        ]), 
        ft.Container(height=25),
        ft.Container(
          content=ft.Column([
            ft.Row([status_dot, device_status_text, loading_ring], spacing=8),
            ft.Divider(color="#1C202D", height=15),
            ft.Row([ft.Text("品牌", color="#6E7B91", size=12), info_brand], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("型号", color="#6E7B91", size=12), info_model], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("系统", color="#6E7B91", size=12), info_android], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([ft.Text("Root", color="#6E7B91", size=12), info_root], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
          ]),
          padding=15, bgcolor=page.ui_style["card_bg"], border_radius=16, border=page.ui_style["card_border"]
        ),
        ft.Container(expand=True)
      ], expand=True)
    )

    nav_inner = ft.NavigationRail(
      selected_index=current_tab["idx"],
      label_type=ft.NavigationRailLabelType.ALL, min_width=90, bgcolor=ft.Colors.TRANSPARENT,
      indicator_color=ft.Colors.with_opacity(0.2, theme_color), indicator_shape=ft.RoundedRectangleBorder(radius=12),
      selected_label_text_style=ft.TextStyle(color=theme_color, weight=ft.FontWeight.BOLD, size=12),
      unselected_label_text_style=ft.TextStyle(color="#8892B0", size=12),
      destinations=[
        ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="控制台"),
        ft.NavigationRailDestination(icon=ft.Icons.FLASH_ON_OUTLINED, selected_icon=ft.Icons.FLASH_ON, label="一键刷机"),
        ft.NavigationRailDestination(icon=ft.Icons.SECURITY_OUTLINED, selected_icon=ft.Icons.SECURITY, label="临时Root"),
        ft.NavigationRailDestination(icon=ft.Icons.HISTORY_OUTLINED, selected_icon=ft.Icons.HISTORY, label="历史"),
        ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="个性化"),
      ]
    )
    
    nav_container = ft.Container(content=nav_inner, bgcolor=page.ui_style["nav_bg"], width=90)

    content_area = ft.Container(expand=True)
    
    SUB_PAGES = {
      "module_repo": build_module_repo_page, "terminal": build_terminal_page,
      "scrcpy": build_scrcpy_page, "backup": build_backup_page,
      "wireless_adb": build_wireless_adb_page, "mode_switch": build_mode_switch_page,
      "drivers": build_drivers_page, "rescue": build_rescue_page,
      "scan": build_scan_page, "mediatek_rescue": build_mediatek_rescue_page,
      "flash_parts": build_flash_parts_page,
    }

    def goto_sub_page(route_name):
      page.goto_sub_page = goto_sub_page
      if route_name in SUB_PAGES:
        content_area.content = SUB_PAGES[route_name](page, theme_color)
        content_area.opacity = 0
        content_area.animate_opacity = 200
        page.update()
        content_area.opacity = 1
        page.update()

    def switch_tab(idx):
      nav_inner.selected_index = idx
      on_nav_change(None)

    def on_nav_change(e):
      current_tab["idx"] = nav_inner.selected_index
      idx = nav_inner.selected_index
      if idx == 0: content_area.content = build_dashboard(page, theme_color, scan_device, switch_tab, goto_sub_page)
      elif idx == 1: content_area.content = build_flash_page(page, theme_color)
      elif idx == 2: content_area.content = build_temp_root_page(page, theme_color)
      elif idx == 3: content_area.content = build_history_page(page, theme_color)
      elif idx == 4: content_area.content = build_settings_page(page, theme_color)
      
      content_area.opacity = 0
      content_area.animate_opacity = 200
      page.update()
      content_area.opacity = 1
      page.update()

    nav_inner.on_change = on_nav_change
    
    if current_tab["idx"] == 0: content_area.content = build_dashboard(page, theme_color, scan_device, switch_tab, goto_sub_page)
    elif current_tab["idx"] == 1: content_area.content = build_flash_page(page, theme_color)
    elif current_tab["idx"] == 2: content_area.content = build_temp_root_page(page, theme_color)
    elif current_tab["idx"] == 3: content_area.content = build_history_page(page, theme_color)
    elif current_tab["idx"] == 4: content_area.content = build_settings_page(page, theme_color)

    return ft.Row([nav_container, ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE)), content_area, side_panel], expand=True, spacing=0)

  def refresh_main_ui(tab_index=0):
    current_tab["idx"] = tab_index
    ui_container.content = build_main_ui()
    ui_container.update()
    page.update()

  page.refresh_main_ui = refresh_main_ui
  ui_container.content = build_main_ui()
  page.update()

if __name__ == "__main__":
  ft.app(target=main, assets_dir="assets")
'''

with open(main_path, "w", encoding="utf-8") as f:
  f.write(main_code)
print("✅ main_final.py 终极完整版重写完成！缩进100%完美！")

# ==================== 2. 重写 settings.py ====================
settings_code = '''import flet as ft
import os
import re
import glob
import shutil
import time
import subprocess
from core_api import CFG
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_settings_page(page: ft.Page, theme_color):
  state = {
    "theme_color": CFG.get("theme_color", "#39C5BB"),
    "ui_material": CFG.get("ui_material", "default"),
    "card_opacity": CFG.get("card_opacity", 0.15),
    "blur_radius": CFG.get("blur_radius", 10)
  }

  wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
  has_wallpaper = len(wallpaper_files) > 0

  def show_snackbar(msg, color=ft.Colors.GREEN):
    page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=color)
    page.snack_bar.open = True
    page.update()

  def pick_wallpaper(e):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()
    
    def on_file_selected(e: ft.FilePickerResultEvent):
      if e.files:
        src_path = e.files[0].path
        print(f"\\n[选择文件] 已选中: {src_path}")
        try:
          ext = os.path.splitext(src_path)[1].lower()
          new_filename = f"wallpaper_{int(time.time())}{ext}"
          new_filepath = os.path.join(BASE_DIR, "assets", new_filename)

          cover_path = os.path.join(BASE_DIR, "assets", "wallpaper_cover.jpg")
          if os.path.exists(cover_path):
            try: os.remove(cover_path)
            except: pass

          if ext in ['.mp4', '.webm', '.mov', '.mkv', '.avi']:
            shutil.copy2(src_path, new_filepath)
            print(f"[Video] 已直接加载高清视频: {new_filepath}")
            
            ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
              print("[FFmpeg] 正在提取视频首帧封面...")
              cmd_cover = [ffmpeg_exe, "-ss", "0.1", "-i", src_path, "-vframes", "1", "-q:v", "2", "-y", cover_path]
              subprocess.run(cmd_cover, check=True, capture_output=True)
              print(f"[FFmpeg] 封面提取成功: {cover_path}")
          elif ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
            img = Image.open(src_path).convert("RGB")
            w, h = img.size
            target_ratio = 16 / 10
            if w / h > target_ratio:
              new_w = int(h * target_ratio)
              left = (w - new_w) // 2
              img = img.crop((left, 0, left + new_w, h))
            elif w / h < target_ratio:
              new_h = int(w / target_ratio)
              top = (h - new_h) // 2
              img = img.crop((0, top, w, top + new_h))
            img = img.resize((1440, 900), Image.Resampling.LANCZOS)
            img.save(new_filepath, quality=95)
            print(f"[PIL] 图片裁剪成功: {new_filepath}")
          elif ext == '.gif':
            shutil.copy2(src_path, new_filepath)
            print(f"[GIF] 已复制: {new_filepath}")
          else:
            raise Exception(f"不支持的格式: {ext}")

          old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
          for old_f in old_files:
            if old_f != new_filepath and old_f != cover_path and os.path.exists(old_f):
              try: os.remove(old_f)
              except: pass
          
          if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()
            
          show_snackbar("高清壁纸已应用！")
          
        except Exception as ex:
          show_snackbar(f"应用失败: {ex}", ft.Colors.RED)
          print(f"[异常] {ex}")

    file_picker.on_result = on_file_selected
    file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp", "gif", "bmp", "mp4", "webm", "mov", "mkv", "avi"])

  def clear_wallpaper(e):
    files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.*"))
    files.append(os.path.join(BASE_DIR, "assets", "wallpaper_cover.jpg"))
    for f in files:
      try: os.remove(f)
      except: pass
    if hasattr(page, "update_wallpaper_hot"):
      page.update_wallpaper_hot()
    show_snackbar("壁纸已清除。")

  color_input = ft.TextField(value=state["theme_color"], label="自定义 HEX 颜色", width=200, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), color="white", border_color=ft.Colors.with_opacity(0.2, theme_color))
  color_preview = ft.Container(width=40, height=40, border_radius=8, bgcolor=state["theme_color"])
  def apply_color(e):
    hex_val = color_input.value.strip()
    if re.match(r'^#[0-9a-fA-F]{6}$', hex_val):
      state["theme_color"] = hex_val
      color_preview.bgcolor = hex_val
      CFG.set("theme_color", hex_val)
      CFG.save()
      show_snackbar("颜色已应用")
      if hasattr(page, "refresh_main_ui"): page.refresh_main_ui(tab_index=4)
    else:
      color_input.error_text = "格式错误"
    page.update()

  material_dropdown = ft.Dropdown(label="UI 材质", value=state["ui_material"], width=300, bgcolor="#1A233A", color="white", options=[ft.dropdown.Option("default", "默认"), ft.dropdown.Option("frosted", "毛玻璃"), ft.dropdown.Option("liquid", "液态玻璃")], on_change=lambda e: apply_material(e.control.value))
  def apply_material(val):
    state["ui_material"] = val
    CFG.set("ui_material", val)
    CFG.save()
    if hasattr(page, "refresh_main_ui"): page.refresh_main_ui(tab_index=4)

  blur_slider = ft.Slider(min=0, max=40, divisions=40, value=state["blur_radius"], active_color=theme_color, label="{value}")
  blur_slider.on_change = lambda e: CFG.set("blur_radius", int(e.control.value))
  blur_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

  opacity_slider = ft.Slider(min=0.05, max=0.8, divisions=15, value=state["card_opacity"], active_color=theme_color, label="{value}")
  opacity_slider.on_change = lambda e: CFG.set("card_opacity", e.control.value)
  opacity_slider.on_change_end = lambda e: page.refresh_main_ui(tab_index=4)

  def make_card(title, icon, content_list):
    return ft.Container(
      content=ft.Column([
        ft.Row([ft.Icon(icon, color=theme_color, size=20), ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="white")]),
        ft.Divider(color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE), height=10),
        *content_list
      ], spacing=15),
      bgcolor=getattr(page, "ui_style", {}).get("card_bg", ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
      border=getattr(page, "ui_style", {}).get("card_border", ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE))),
      border_radius=15, padding=20
    )

  card_step1 = make_card("第一步：壁纸引擎", ft.Icons.IMAGE, [
    ft.Row([
      ft.Column([ft.Text("自定义壁纸", size=14, color="white"), ft.Text("支持高清 MP4 视频与静态图/GIF" if not has_wallpaper else "已设置壁纸，可随时更换", size=11, color=ft.Colors.GREY_500)]),
      ft.Container(expand=True),
      ft.ElevatedButton("选择图片/视频", icon=ft.Icons.UPLOAD, on_click=pick_wallpaper, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"),
      ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white")
    ])
  ])
  card_step2 = make_card("第二步：主题色", ft.Icons.COLOR_LENS, [ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")])])
  card_step3 = make_card("第三步：UI 材质", ft.Icons.LAYERS, [ft.Text("选择全局材质", size=12, color=ft.Colors.GREY_400), ft.Row([material_dropdown])])
  card_step4 = make_card("第四步：视觉特效", ft.Icons.AUTO_AWESOME, [
    ft.Row([ft.Column([ft.Text("全局模糊度", size=14, color="white")]), ft.Container(expand=True), ft.Container(content=blur_slider, width=300)]),
    ft.Divider(color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), height=15),
    ft.Row([ft.Column([ft.Text("卡片透明度", size=14, color="white")]), ft.Container(expand=True), ft.Container(content=opacity_slider, width=300)])
  ])

  return ft.Container(
    content=ft.Column([
      ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white")]),
      ft.Container(height=10),
      ft.Column([card_step1, ft.Container(height=10), card_step2, ft.Container(height=10), card_step3, ft.Container(height=10), card_step4], scroll=ft.ScrollMode.AUTO, expand=True)
    ], expand=True),
    expand=True, padding=20
  )
'''

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(settings_code)
print("✅ settings.py 终极完整版重写完成！")