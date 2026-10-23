# fix_flicker_diagnostic.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# ==================== 1. 剥离背景层，缓存 Image 对象 ====================
# 在 main 函数里，全局初始化背景层
if "bg_layer = ft.Container(expand=True)" not in content:
    content = content.replace(
        "    main_container = ft.Container(expand=True)\n    page.add(main_container)",
        """    main_container = ft.Container(expand=True)
    bg_layer = ft.Container(expand=True) # 独立的背景层
    # 使用 Stack 把背景永远压在最底下
    page.add(ft.Stack([bg_layer, main_container], expand=True))"""
    )

# 修改 build_main_ui 内部，不再返回背景，而是更新 bg_layer
# 找到原有的 return ft.Stack(...)
old_return = '''        return ft.Stack(
            [wallpaper, overlay_layer, main_layout],
            expand=True
        )'''

new_return = '''        # 🚨 核心：动态更新底层背景，而不是让它跟着 UI 重建
        bg_layer.image = wallpaper.image
        bg_layer.bgcolor = wallpaper.bgcolor
        
        # 遮罩层也独立，或者直接给 main_container 加背景
        # 为了极简，遮罩直接作为主容器的半透明背景
        main_container.bgcolor = page.ui_style["overlay_bg"]
        main_container.blur = page.ui_style["overlay_blur"]

        return main_layout'''

content = content.replace(old_return, new_return)

# 把原本返回里的 wallpaper 和 overlay_layer 构造逻辑保留，但不要 return 它们
content = content.replace(
    "        return ft.Stack([wallpaper, overlay_layer, main_layout], expand=True)",
    new_return
)

# ==================== 2. 修复诊断日志 ====================
content = content.replace(
    'def apply_device_state(res, manual=False):',
    '''def apply_device_state(res, manual=False):
            # 诊断日志：只在状态变化时打印
            if res["state"] != last_state["state"]:
                print(f"[Debug] 设备状态改变: {last_state['state']} -> {res['state']}")'''
)

content = content.replace(
    'def refresh_main_ui(tab_index=0):',
    '''def refresh_main_ui(tab_index=0):
            print(f"[Debug] 触发 refresh_main_ui, tab={tab_index}")'''
)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 诊断补丁已注入！背景层已物理剥离，后台扫描加了日志。")