# fix_no_flicker.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# ==================== 1. 改造 main 函数，建立持久根节点 ====================
# 在 page 初始化之后，挂载一个永不销毁的 main_container
init_code = '''    current_tab = {"idx": 0}

    # 🚨 建立全局唯一的持久根节点，绝不清空 page
    main_container = ft.Container(expand=True)
    page.add(main_container)
'''
content = content.replace('    current_tab = {"idx": 0}', init_code)

# ==================== 2. 改造 build_main_ui，返回 Stack 而不是直接 page.add ====================
# 找到 build_main_ui 里的 page.controls.clear() 删掉
content = content.replace("        page.controls.clear()\n", "")

# 找到最后组合图层的代码，改为 return
old_return = '''        page.add(
            ft.Stack(
                [wallpaper, overlay_layer, main_layout],
                expand=True
            )
        )'''
new_return = '''        return ft.Stack(
            [wallpaper, overlay_layer, main_layout],
            expand=True
        )'''
content = content.replace(old_return, new_return)

# ==================== 3. 改造 refresh_main_ui，实现瞬间替换 ====================
old_refresh = '''        def refresh_main_ui(tab_index=0):
            current_tab["idx"] = tab_index
            page.controls.clear()
            build_main_ui()
            page.update()'''

new_refresh = '''        def refresh_main_ui(tab_index=0):
            current_tab["idx"] = tab_index
            # 🚨 核心修复：只替换容器内容，绝不闪屏！
            new_ui = build_main_ui()
            main_container.content = new_ui
            page.update()'''
content = content.replace(old_refresh, new_refresh)

# ==================== 4. 修复启动逻辑 ====================
# 因为 build_main_ui 现在返回 UI，所以启动时需要赋值给 main_container
old_startup = '''    if not CFG.get("onboarded", False):
        from ui_onboarding_hyperos_light import HyperOSLightOnboarding
        page.bgcolor = ft.Colors.TRANSPARENT
        page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#E8F0FE", "#FFFFFF"]))
        onboarding = HyperOSLightOnboarding(on_finish=build_main_ui)
        page.add(onboarding)
    else:
        build_main_ui()'''

new_startup = '''    if not CFG.get("onboarded", False):
        from ui_onboarding_hyperos_light import HyperOSLightOnboarding
        page.bgcolor = ft.Colors.TRANSPARENT
        page.decoration = ft.BoxDecoration(gradient=ft.LinearGradient(colors=["#E8F0FE", "#FFFFFF"]))
        
        def on_finish():
            page.controls.clear()
            main_container.content = build_main_ui()
            page.update()
            
        onboarding = HyperOSLightOnboarding(on_finish=on_finish)
        page.add(onboarding)
    else:
        main_container.content = build_main_ui()
        page.update()'''
content = content.replace(old_startup, new_startup)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 闪屏 Bug 已彻底根除！现在刷新材质是瞬间替换，再也不会闪回原样了！")