# fix_wallpaper_crop.py
import os

settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "settings.py")

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# ==================== 替换原有的 pick_wallpaper 逻辑为 PIL 智能裁剪版 ====================
old_pick_logic = '''    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                try:
                    if os.path.exists(wallpaper_path):
                        try: os.remove(wallpaper_path)
                        except: pass
                    shutil.copy2(src_path, wallpaper_path)
                    show_snackbar("壁纸已应用！高级材质已解锁！")
                    
                    # 🚨 核心：动态解锁后续卡片，而不是重载页面！
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    page.update()
                    
                    # 顺便刷新一下背景（如果在主页面）
                    if hasattr(page, "refresh_main_ui"):
                        page.refresh_main_ui(tab_index=4)
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])'''

new_pick_logic = '''    def pick_wallpaper(e):
        file_picker = ft.FilePicker()
        page.overlay.append(file_picker)
        page.update()
        
        def on_file_selected(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                try:
                    # 🚨 核心：引入 PIL 进行智能居中裁剪
                    try:
                        from PIL import Image
                        img = Image.open(src_path)
                        w, h = img.size
                        # 目标比例 16:10 (适合当前 1440x900 的窗口)
                        target_ratio = 16 / 10
                        
                        if w / h > target_ratio:
                            # 原图太宽，裁剪两边
                            new_w = int(h * target_ratio)
                            left = (w - new_w) // 2
                            img = img.crop((left, 0, left + new_w, h))
                        elif w / h < target_ratio:
                            # 原图太高，裁剪上下
                            new_h = int(w / target_ratio)
                            top = (h - new_h) // 2
                            img = img.crop((0, top, w, top + new_h))
                            
                        # 保存为适合当前分辨率的缩略图，并强制转为 RGB 防止透明通道报错
                        img = img.resize((1440, 900), Image.Resampling.LANCZOS).convert("RGB")
                        img.save(wallpaper_path, quality=95)
                        show_snackbar("壁纸已智能裁剪并应用！")
                    except ImportError:
                        # 如果没装 PIL，则退化为直接复制
                        if os.path.exists(wallpaper_path):
                            try: os.remove(wallpaper_path)
                            except: pass
                        shutil.copy2(src_path, wallpaper_path)
                        show_snackbar("壁纸已应用 (未安装Pillow无法裁剪)")
                    except Exception as pil_err:
                        raise Exception(f"图片处理失败: {pil_err}")

                    # 动态解锁后续卡片
                    card_step2.visible = True
                    card_step3.visible = True
                    card_step4.visible = True
                    page.update()
                    
                    # 刷新主界面
                    if hasattr(page, "refresh_main_ui"):
                        page.refresh_main_ui(tab_index=4)
                except Exception as ex:
                    show_snackbar(f"壁纸设置失败: {ex}")

        file_picker.on_result = on_file_selected
        file_picker.pick_files(allowed_extensions=["jpg", "jpeg", "png", "webp"])'''

if old_pick_logic in content:
    content = content.replace(old_pick_logic, new_pick_logic)
    print("✅ 成功替换为 PIL 智能居中裁剪逻辑！")
else:
    print("⚠️ 未完全匹配到旧代码，可能上一波修改有偏移，尝试逐行替换...")
    # 兜底替换：只替换核心的复制逻辑
    content = content.replace(
        'shutil.copy2(src_path, wallpaper_path)\n                    show_snackbar("壁纸已应用！高级材质已解锁！")',
        '''try:
                        from PIL import Image
                        img = Image.open(src_path)
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
                        img = img.resize((1440, 900), Image.Resampling.LANCZOS).convert("RGB")
                        img.save(wallpaper_path, quality=95)
                        show_snackbar("壁纸已智能裁剪并应用！")
                    except ImportError:
                        if os.path.exists(wallpaper_path):
                            try: os.remove(wallpaper_path)
                            except: pass
                        shutil.copy2(src_path, wallpaper_path)
                        show_snackbar("壁纸已应用 (未安装Pillow无法裁剪)")'''
    )

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🎉 壁纸裁剪逻辑注入完毕！")