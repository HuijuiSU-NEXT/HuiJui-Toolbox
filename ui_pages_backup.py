import os
import threading
import flet as ft
from PIL import Image
from core_api import flasher, history_db, get_active_serial, CFG, BASE_DIR
import ui_theme, ui_dialogs
from core.temp_root_manager import check_device_support, parse_ota_for_kmi, execute_temp_root

def build_dashboard(page, theme_color, scan_callback, switch_tab_callback):
  grid = ft.GridView(
    expand=True, runs_count=3, max_extent=380, child_aspect_ratio=3.5,
    spacing=20, run_spacing=20, padding=ft.padding.only(top=10, bottom=30),
    controls=[
      ui_theme.create_glass_card("一键刷机", "全自动向导页面", ft.Icons.FLASH_ON, on_click=lambda e: switch_tab_callback(1), is_main=True, theme_color=theme_color, glass_style="glow"),
      ui_theme.create_glass_card("扫描设备", "读取手机状态与 Root", ft.Icons.PHONE_ANDROID, on_click=scan_callback, is_main=True, theme_color=theme_color, glass_style="glow"),
      ui_theme.create_glass_card("临时 Root", "LKM 无痕注入", ft.Icons.SECURITY, on_click=lambda e: switch_tab_callback(2), is_main=True, theme_color=theme_color, glass_style="glow"),
      ui_theme.create_glass_card("模块仓库", "797 个纯净模块", ft.Icons.EXTENSION, on_click=lambda e: ui_dialogs.show_module_repo(page, theme_color), theme_color=theme_color, glass_style="soft"),
      ui_theme.create_glass_card("高级终端", "实时 Shell 执行", ft.Icons.TERMINAL, on_click=lambda e: ui_dialogs.show_terminal(page, theme_color), theme_color=theme_color),
      ui_theme.create_glass_card("Scrcpy 投屏", "USB / 无线投屏", ft.Icons.SCREEN_SHARE, on_click=lambda e: ui_dialogs.show_scrcpy(page, theme_color), theme_color=theme_color, glass_style="soft"),
      ui_theme.create_glass_card("分区备份", "保护 boot / init_boot", ft.Icons.SAVE_ALT, on_click=lambda e: ui_dialogs.show_backup(page, theme_color), theme_color=theme_color),
      ui_theme.create_glass_card("无线调试", "TCPIP 与 IP 自动获取", ft.Icons.WIFI, on_click=lambda e: ui_dialogs.show_wireless(page, theme_color), theme_color=theme_color),
      ui_theme.create_glass_card("模式切换", "Fastboot / Fastbootd", ft.Icons.SWAP_HORIZ, on_click=lambda e: ui_dialogs.show_reboot(page, theme_color), theme_color=theme_color),
      ui_theme.create_glass_card("驱动环境", "一键安装底层驱动", ft.Icons.BUILD, on_click=lambda e: ui_dialogs.show_drivers(page, theme_color), theme_color=theme_color),
      ui_theme.create_glass_card("急救中心", "9008 / BROM 救砖", ft.Icons.HEALTH_AND_SAFETY, on_click=lambda e: ui_dialogs.show_rescue_center(page, theme_color), theme_color=theme_color, glass_style="glow"),
    ]
  )
  return ft.Container(
    expand=True, padding=ft.padding.only(left=40, right=40, top=30, bottom=20),
    content=ft.Column([
      ft.Row([ft.Column([ft.Text("Matrix Dashboard", size=42, weight=ft.FontWeight.W_900, color="white"), ft.Text("原生 GPU 渲染 · 沉浸式极客体验", size=16, color=theme_color, weight=ft.FontWeight.W_600)])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
      ft.Container(height=30), ft.Text("CORE FUNCTIONS", size=12, color="#4B5568", weight=ft.FontWeight.BOLD), grid
    ], expand=True)
  )

def build_flash_page(page, theme_color):
  return ft.Container(expand=True, padding=30, content=ft.Text("一键刷机页 (保持原样)", color="white"))

def build_temp_root_page(page, theme_color):
  return ft.Container(expand=True, padding=30, content=ft.Text("临时Root页 (保持原样)", color="white"))

def build_history_page(page, theme_color):
  return ft.Container(expand=True, padding=30, content=ft.Text("历史页 (保持原样)", color="white"))

def build_settings_page(page, theme_color):
  current_color = CFG.get("theme_color", "#39C5BB")
  current_bg = CFG.get("bg_style", "gradient_teal")
  current_card_opacity = CFG.get("card_opacity", 0.6)
  current_bg_opacity = CFG.get("bg_opacity", 0.3)
  current_bg_blur = CFG.get("bg_blur", 0)
  # 读取全局UI模糊开关状态，默认开启
  ui_blur_enabled = CFG.get("ui_blur_enabled", True)

  color_input = ft.TextField(label="自定义 HEX 颜色", value=current_color, width=200, text_size=14, border_color="#222634", bgcolor="#0D1017", color="white")
  def apply_custom_color(e):
    c = color_input.value.strip()
    if not c.startswith("#"): c = "#" + c
    if len(c) in (4, 7):
      CFG.set("theme_color", c)
      page.snack_bar = ft.SnackBar(ft.Text("🎨 已保存，重启生效！"), bgcolor=c)
      page.snack_bar.open = True; page.update()
  color_apply_btn = ft.ElevatedButton("应用", on_click=apply_custom_color, bgcolor=current_color, color="#0B0E14")

  demo_card = ui_theme.create_glass_card("实时预览", "切换下方开关看效果", ft.Icons.VISIBILITY, is_main=True, theme_color=current_color)

  def on_ui_blur_switch(e):
    val = e.control.value
    CFG.set("ui_blur_enabled", val)
    if val:
      demo_card.blur = ft.Blur(10, 10, ft.BlurTileMode.MIRROR)
    else:
      demo_card.blur = None
    demo_card.update()
    page.update()

  def on_card_opacity_change(e):
    val = float(e.control.value)
    CFG.set("card_opacity", val)
    demo_card.bgcolor = ft.Colors.with_opacity(val, "#131722")
    demo_card.update()

  def on_bg_opacity_change(e):
    val = float(e.control.value)
    CFG.set("bg_opacity", val)
    if CFG.get("bg_image", ""):
      page.decoration.image.opacity = val
      page.update()

  def on_bg_blur_change(e):
    val = int(float(e.control.value))
    CFG.set("bg_blur", val)
    page.update()

  def open_crop_dialog(src_path):
    try:
      img = Image.open(src_path)
      orig_w, orig_h = img.size
      preview_w, preview_h = 640, 360
      scale = max(preview_w / orig_w, preview_h / orig_h)
      base_w, base_h = int(orig_w * scale), int(orig_h * scale)
      
      state = {"zoom": 1.0, "offset_x": 0, "offset_y": 0}
      image_ctrl = ft.Container(
        content=ft.Image(src=src_path, width=base_w, height=base_h, fit=ft.ImageFit.COVER),
        width=preview_w, height=preview_h, clip_behavior=ft.ClipBehavior.HARD_EDGE, border_radius=8, offset=ft.Offset(0, 0)
      )
      
      def update_preview(e=None):
        scaled_w, scaled_h = base_w * state["zoom"], base_h * state["zoom"]
        max_x, max_y = max(0, (scaled_w - preview_w) / 2), max(0, (scaled_h - preview_h) / 2)
        off_x, off_y = (state["offset_x"] / 100) * max_x, (state["offset_y"] / 100) * max_y
        image_ctrl.width, image_ctrl.height = scaled_w, scaled_h
        image_ctrl.offset = ft.Offset(off_x / scaled_w, off_y / scaled_h)
        image_ctrl.update()

      slider_zoom = ft.Slider(min=1.0, max=2.5, divisions=15, value=1.0, label="缩放 {value}x", on_change=lambda e: [state.update({"zoom": e.control.value}), update_preview()])
      slider_x = ft.Slider(min=-100, max=100, divisions=20, value=0, label="左右平移", on_change=lambda e: [state.update({"offset_x": e.control.value}), update_preview()])
      slider_y = ft.Slider(min=-100, max=100, divisions=20, value=0, label="上下平移", on_change=lambda e: [state.update({"offset_y": e.control.value}), update_preview()])

      def confirm_crop(e):
        final_scale = scale * state["zoom"]
        final_w, final_h = orig_w * final_scale, orig_h * final_scale
        max_x, max_y = max(0, (final_w - preview_w) / 2), max(0, (final_h - preview_h) / 2)
        real_off_x, real_off_y = (state["offset_x"] / 100) * max_x, (state["offset_y"] / 100) * max_y
        crop_w, crop_h = preview_w / final_scale, preview_h / final_scale
        center_x, center_y = orig_w / 2 - (real_off_x / final_scale), orig_h / 2 - (real_off_y / final_scale)
        left, top = max(0, center_x - crop_w / 2), max(0, center_y - crop_h / 2)
        right, bottom = min(orig_w, left + crop_w), min(orig_h, top + crop_h)
        cropped = img.crop((int(left), int(top), int(right), int(bottom)))
        cropped = cropped.resize((1920, 1080), Image.LANCZOS)
        dest = os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg")
        cropped.convert('RGB').save(dest, quality=90)
        CFG.set("bg_image", "custom_wallpaper.jpg")
        dlg.open = False
        page.snack_bar = ft.SnackBar(ft.Text("🖼️ 裁剪完成，重启生效！"), bgcolor=ft.Colors.GREEN_400); page.snack_bar.open = True; page.update()

      dlg = ft.AlertDialog(
        title=ft.Text("手动裁剪壁纸"),
        content=ft.Container(content=ft.Column([ft.Text("拖动下方滑块调整构图：", size=12, color="#8892B0"), image_ctrl, slider_zoom, slider_x, slider_y]), width=680),
        actions=[ft.TextButton("取消", on_click=lambda _: setattr(dlg, 'open', False) or page.update()), ft.ElevatedButton("确认裁剪", on_click=confirm_crop, bgcolor=current_color, color="#0B0E14")]
      )
      page.dialog = dlg; dlg.open = True; page.update()
    except Exception as ex:
      page.snack_bar = ft.SnackBar(ft.Text(f"❌ 裁剪器异常: {ex}"), bgcolor=ft.Colors.RED_400); page.snack_bar.open = True; page.update()

  def on_wallpaper_result(e: ft.FilePickerResultEvent):
    if e.files: open_crop_dialog(e.files[0].path)
      
  wp_picker = ft.FilePicker(on_result=on_wallpaper_result)
  page.overlay.append(wp_picker)

  def reset_bg(_):
    CFG.set("bg_image", "")
    page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#0F172A", "#1E1B4B", "#0F172A"]))
    page.snack_bar = ft.SnackBar(ft.Text("🔄 壁纸已清除，已恢复渐变背景"), bgcolor=ft.Colors.BLUE_400); page.snack_bar.open = True; page.update()

  settings_content = ft.Column([
    ft.Text("Settings", size=42, weight=ft.FontWeight.W_900, color="white"),
    ft.Text("个性化设置 · 定义你的专属引擎", size=16, color=theme_color, weight=ft.FontWeight.W_600), ft.Container(height=30),
    ft.Text("🎨 主题强调色", size=16, weight=ft.FontWeight.BOLD, color="white"),
    ft.Row([color_input, color_apply_btn], spacing=10), ft.Divider(color="#222634", height=30),
    ft.Text("🌌 动态背景预设", size=16, weight=ft.FontWeight.BOLD, color="white"),
    ft.Dropdown(options=[ft.dropdown.Option("gradient_teal", "深渊黑 (原版)"), ft.dropdown.Option("gradient_aurora", "极光深蓝紫"), ft.dropdown.Option("gradient_crimson", "赛博血红"), ft.dropdown.Option("solid_dark", "极简纯黑")], value=current_bg, width=300, text_size=14, on_change=lambda e: CFG.set("bg_style", e.control.value)),
    ft.Container(height=10),
    ft.Text("🖼️ 壁纸引擎 (支持手动裁剪)", size=16, weight=ft.FontWeight.BOLD, color="white"),
    ft.Row([ft.ElevatedButton("📁 选择本地壁纸", on_click=lambda _: wp_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png", "webp", "bmp"]), bgcolor=current_color, color="#0B0E14"), ft.OutlinedButton("🗑️ 清除壁纸", on_click=reset_bg, style=ft.ButtonStyle(color="#E05070", side=ft.BorderSide(1, "#E05070")))], spacing=10),
    ft.Text("壁纸暗角遮罩 (拖动实时生效)", size=12, color="#8892B0"),
    ft.Slider(min=0.0, max=0.9, divisions=9, value=current_bg_opacity, label="{value}", on_change=on_bg_opacity_change),
    ft.Text("全局壁纸模糊 (壁纸虚化，UI清晰)", size=12, color="#8892B0"),
    ft.Slider(min=0, max=30, divisions=30, value=current_bg_blur, label="{value}px", on_change=on_bg_blur_change),
    ft.Divider(color="#222634", height=30),
    ft.Text("💎 全局 UI 毛玻璃效果", size=16, weight=ft.FontWeight.BOLD, color="white"),
    ft.Container(content=demo_card, width=350, height=90, margin=ft.margin.only(bottom=10)),
    
    # ====== 这里的滑块已经彻底改成 Switch 开关 ======
    ft.Row([
      ft.Text("全局 UI 毛玻璃开关 (卡片/侧栏/导航栏)", size=12, color="#8892B0"),
      ft.Switch(value=ui_blur_enabled, on_change=on_ui_blur_switch, active_color=current_color)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
    # ===========================================
    
    ft.Text("卡片透明度", size=12, color="#8892B0"),
    ft.Slider(min=0.1, max=1.0, divisions=9, value=current_card_opacity, label="{value}", on_change=on_card_opacity_change),
    ft.Container(height=20), ft.Text("⚠️ 修改后请重启软件以应用新主题", size=12, color="#F0A030", weight=ft.FontWeight.BOLD),
  ], scroll=ft.ScrollMode.ADAPTIVE)

  return ft.Container(
    expand=True, padding=30,
    content=ft.Container(
      content=settings_content,
      bgcolor=ft.Colors.with_opacity(0.4, "#090A0F"),
      blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
      border_radius=16, padding=30,
      border=ft.border.all(1, ft.Colors.with_opacity(0.1, "white"))
    )
  )