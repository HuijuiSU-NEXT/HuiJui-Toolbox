# fix_dynamic_wallpaper_gif.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

# ==================== 1. 修复 main_final.py：用 ft.Image 替代 RawImage ====================
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 替换背景层定义
old_bg = '''    # 🚨 动态壁纸渲染器
    raw_bg_image = ft.RawImage(
        fit=ft.BoxFit.COVER,
        expand=True,
        visible=False
    )
    # 静态壁纸渲染器
    static_bg_image = ft.Image(
        src=None,
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )
    bg_layer.content = ft.Stack([static_bg_image, raw_bg_image], expand=True)'''

new_bg = '''    # 🚨 统一使用 ft.Image，支持 GIF 动图
    bg_image = ft.Image(
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=False
    )'''
content = content.replace(old_bg, new_bg)

# 替换整个播放逻辑为直接加载 GIF
old_play = '''    async def play_dynamic_wallpaper():
        """在后台异步循环中，用 FFmpeg 解码并渲染动态壁纸帧"""
        import glob
        
        # 查找最新的动态壁纸文件 (gif / mp4)
        wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.mp4"))
        
        if not wallpaper_files:
            raw_bg_image.visible = False
            raw_bg_image.update()
            return
        
        latest_wp = max(wallpaper_files, key=os.path.getctime)
        
        # 强制将视频缩放并输出为 1440x900 的 RGBA 原始数据流
        cmd = [
            os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe"),
            "-i", latest_wp,
            "-vf", "scale=1440:900",
            "-f", "image2pipe",
            "-pix_fmt", "rgba",
            "-vcodec", "rawvideo",
            "-"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        
        raw_bg_image.visible = True
        raw_bg_image.update()
        
        try:
            while True:
                # 精确读取一帧：1440 * 900 * 4 bytes (RGBA)
                frame_data = await process.stdout.read(1440 * 900 * 4)
                if not frame_data or len(frame_data) < 1440 * 900 * 4:
                    break # 视频播放结束
                
                # 将原始字节转换为 Pillow 图像，然后交给 RawImage 渲染
                frame = Image.frombytes('RGBA', (1440, 900), frame_data, 'raw', 'RGBA')
                # 用 to_thread 防止阻塞 Flet 的 UI 线程
                await asyncio.to_thread(raw_bg_image.render, frame)
                
                # 控制帧率（30 FPS，防止 CPU 占用过高）
                await asyncio.sleep(1 / 30)
                
        except asyncio.CancelledError:
            print("动态壁纸播放被取消。")
        except Exception as e:
            print(f"动态壁纸播放出错: {e}")
        finally:
            if process and process.returncode is None:
                try:
                    process.terminate()
                except ProcessLookupError:
                    pass
            raw_bg_image.visible = False
            raw_bg_image.update()

    def update_wallpaper_hot():
        """当用户更换壁纸时，取消旧的播放任务并启动新的"""
        import glob
        
        # 1. 先清理可能正在跑的任务
        if hasattr(page, "wallpaper_task") and page.wallpaper_task:
            page.wallpaper_task.cancel()
            
        # 2. 检查是否有动态壁纸
        dyn_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.mp4"))
        if dyn_files:
            # 播放动态壁纸，关闭静态
            static_bg_image.visible = False
            page.wallpaper_task = asyncio.create_task(play_dynamic_wallpaper())
        else:
            # 3. 如果没有动态，检查是否有静态
            static_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
            if static_files:
                latest_static = max(static_files, key=os.path.getctime)
                static_bg_image.src = os.path.basename(latest_static)
                static_bg_image.visible = True
                raw_bg_image.visible = False
            else:
                # 都没了
                static_bg_image.visible = False
                raw_bg_image.visible = False
                
        static_bg_image.update()
        raw_bg_image.update()

    page.update_wallpaper_hot = update_wallpaper_hot
    update_wallpaper_hot()'''

new_play = '''    def update_wallpaper_hot():
        """直接加载最新的 GIF 或静态图片，Flet 原生支持 GIF 播放"""
        import glob
        
        # 优先查找 GIF
        gif_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
        jpg_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg"))
        
        if gif_files:
            latest = max(gif_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
        elif jpg_files:
            latest = max(jpg_files, key=os.path.getctime)
            bg_image.src = os.path.basename(latest)
            bg_image.visible = True
        else:
            bg_image.visible = False
            
        bg_image.update()

    page.update_wallpaper_hot = update_wallpaper_hot
    update_wallpaper_hot()'''
content = content.replace(old_play, new_play)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ main_final.py 已改为 ft.Image + GIF 方案！")

# ==================== 2. 修复 settings.py：用 FFmpeg 将视频/动图统一转为 GIF ====================
with open(settings_path, "r", encoding="utf-8") as f:
    settings_content = f.read()

# 替换 on_file_selected 中的处理逻辑
old_process = '''                    is_gif = src_path.lower().endswith(".gif")
                    
                    if is_gif:
                        new_filename = f"wallpaper_{int(time.time())}.gif"
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)
                        shutil.copy2(src_path, new_filepath)
                    else:
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
                        new_filename = f"wallpaper_{int(time.time())}.jpg"
                        new_filepath = os.path.join(BASE_DIR, "assets", new_filename)

                    # 清理旧壁纸
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
                    old_files.append(os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg"))
                    for old_f in old_files:
                        if os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass
                    
                    if not is_gif:
                        img.save(new_filepath, quality=95)
                    elif is_gif and os.path.exists(new_filepath):
                        pass # 已经在上面 copy2 保存了
                    else:
                        # 兜底，如果是 gif 但文件没复制成功
                        img.save(new_filepath, quality=95)'''

new_process = '''                    # 🚨 统一使用 FFmpeg 转为 1440x900 的高质量 GIF
                    new_filename = f"wallpaper_{int(time.time())}.gif"
                    new_filepath = os.path.join(BASE_DIR, "assets", new_filename)
                    
                    # 清理旧壁纸
                    old_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.jpg")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif"))
                    old_files.append(os.path.join(BASE_DIR, "assets", "custom_wallpaper.jpg"))
                    for old_f in old_files:
                        if os.path.exists(old_f):
                            try: os.remove(old_f)
                            except: pass
                    
                    # 调用 FFmpeg 进行转换和裁剪
                    ffmpeg_exe = os.path.join(BASE_DIR, "bin", "ffmpeg", "ffmpeg.exe")
                    if not os.path.exists(ffmpeg_exe):
                        raise Exception("FFmpeg 未找到，请先运行 setup_ffmpeg_fast.py")
                    
                    # 使用 scale 和 crop 滤镜保证 16:10 比例且居中裁剪
                    cmd = [
                        ffmpeg_exe,
                        "-i", src_path,
                        "-vf", "scale=1440:900:force_original_aspect_ratio=increase,crop=1440:900",
                        "-r", "30",          # 限制帧率为 30fps
                        "-pix_fmt", "rgb24", # 兼容性更好的像素格式
                        "-y",                # 覆盖输出文件
                        new_filepath
                    ]
                    
                    import subprocess
                    subprocess.run(cmd, check=True, capture_output=True)'''

settings_content = settings_content.replace(old_process, new_process)

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(settings_content)
print("✅ settings.py 已改为 FFmpeg 统一转 GIF 方案！")

print("🎉 修复完毕！请重新运行 main_final.py，动态壁纸将使用原生 GIF 播放。")