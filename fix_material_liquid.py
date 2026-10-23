# fix_material_liquid.py
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 1. 重写 ui_theme.py (真实液态玻璃参数) ====================
ui_theme_code = '''import flet as ft
from core_api import CFG

def get_ui_styles(theme_color):
    material = CFG.get("ui_material", "default")
    
    if material == "frosted":
        # 毛玻璃：保持你喜欢的完美效果
        return {
            "type": "frosted",
            "overlay_bg": ft.Colors.with_opacity(0.5, "#0D1017"),
            "overlay_blur": ft.Blur(30, 30, ft.BlurTileMode.MIRROR),
            "nav_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "side_bg": ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }
    elif material == "liquid":
        # 液态玻璃：极致清透 + 边缘高光 + 微弱渐变反光
        # 放弃大面积主题色，改用纯白/浅灰渐变
        return {
            "type": "liquid",
            "overlay_bg": ft.Colors.with_opacity(0.2, "#000000"), # 极低的不透明度，保留壁纸色彩
            "overlay_blur": ft.Blur(40, 40, ft.BlurTileMode.MIRROR), # 超强模糊，像水一样
            "nav_bg": ft.LinearGradient(colors=[ft.Colors.with_opacity(0.2, "#FFFFFF"), ft.Colors.with_opacity(0.05, "#FFFFFF")]),
            "side_bg": ft.LinearGradient(colors=[ft.Colors.with_opacity(0.2, "#FFFFFF"), ft.Colors.with_opacity(0.05, "#FFFFFF")]),
            # 模拟玻璃边缘反光的渐变
            "card_bg": ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(0.15, "#FFFFFF"), ft.Colors.with_opacity(0.02, "#FFFFFF")]
            ),
            # 纯白色细边框，模拟高光
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.1, "#000000"),
            "log_color": theme_color
        }
    else:
        # 默认
        return {
            "type": "default",
            "overlay_bg": ft.Colors.with_opacity(0.4, "#0D1017"),
            "overlay_blur": None,
            "nav_bg": ft.Colors.with_opacity(0.2, "#0D1017"),
            "side_bg": ft.Colors.with_opacity(0.2, "#0D1017"),
            "card_bg": ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
            "card_border": ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            "log_bg": ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            "log_color": "#00FFD1"
        }

def setup_page_style(page: ft.Page):
    theme_color = CFG.get("theme_color", "#39C5BB")
    page.bgcolor = ft.Colors.TRANSPARENT
    return theme_color
'''

# ==================== 2. 重写 settings.py (壁纸引擎前置) ====================
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 把壁纸卡片的代码块提取出来，挪到材质风格上面
# 这里我们直接重新生成那一部分逻辑以确保干净
new_cards_logic = '''    scrollable_content = ft.Column([
        make_card("壁纸引擎", ft.Icons.IMAGE, [
            ft.Row([
                ft.Column([
                    ft.Text("自定义壁纸", size=14, color="white"),
                    ft.Text("由于材质依赖壁纸，请先设置壁纸 (需重启生效)", size=11, color=ft.Colors.GREY_500)
                ]),
                ft.Container(expand=True),
                ft.ElevatedButton("选择图片", icon=ft.Icons.UPLOAD, on_click=pick_wallpaper, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), color="white"),
                ft.ElevatedButton("清除壁纸", icon=ft.Icons.DELETE, on_click=clear_wallpaper, bgcolor=ft.Colors.RED_900, color="white")
            ])
        ]),
        ft.Container(height=10),
        make_card("主题色强化", ft.Icons.COLOR_LENS, [
            ft.Row([color_input, color_preview, ft.ElevatedButton("应用", on_click=apply_color, bgcolor=theme_color, color="black")]),
        ]),
        ft.Container(height=10),
        make_card("UI 材质风格", ft.Icons.LAYERS, [
            ft.Text("选择全局界面渲染材质，切换后立即生效。", size=12, color=ft.Colors.GREY_400),
            ft.Row([material_dropdown]),
        ]),
        ft.Container(height=10),
        make_card("视觉特效", ft.Icons.AUTO_AWESOME, [
            ft.Row([
                ft.Column([
                    ft.Text("卡片透明度", size=14, color="white"),
                    ft.Text("调节卡片背景透明度", size=11, color=ft.Colors.GREY_500)
                ]),
                ft.Container(expand=True),
                ft.Container(content=opacity_slider, width=300)
            ])
        ]),
        ft.Container(height=20),
    ], scroll=ft.ScrollMode.AUTO, spacing=10)'''

# 使用正则替换掉旧的 scrollable_content 块
import re
pattern = r'scrollable_content = ft\.Column\(\[.*?\], scroll=ft\.ScrollMode\.AUTO, spacing=10\)'
settings_content = re.sub(pattern, new_cards_logic, settings_content, flags=re.DOTALL)

# 确保 pick_wallpaper 函数里有正确的逻辑（这里简单保留原有的）
def backup_and_write(filepath, content):
    if os.path.exists(filepath):
        shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已成功更新: {filepath}")

print("=== 🚀 开始执行液态玻璃质变与壁纸前置 ===")
backup_and_write(os.path.join(BASE_DIR, "ui_theme.py"), ui_theme_code)
backup_and_write(settings_path, settings_content)

print("🎉 调优完毕！请运行 python main_final.py。切到液态玻璃看看是不是晶莹剔透了！")