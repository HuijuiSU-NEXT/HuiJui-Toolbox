# fix_dynamic_wallpaper_v2.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

# 确保有必要的导入
if "import asyncio" not in content:
    content = content.replace("import os", "import os\nimport asyncio\nimport subprocess\nfrom PIL import Image")

# 1. 替换背景层为支持 RawImage 和普通 Image 的混合层
old_bg = '''    bg_image = ft.Image(
        src=bg_src,
        fit=ft.ImageFit.COVER,
        expand=True,
        visible=bool(bg_src)
    )'''
new_bg = '''    # 🚨 动态壁纸渲染器
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
content = content.replace(old_bg, new_bg)

# 2. 替换热更新逻辑，加入 FFmpeg 解码与动态播放
old_hot = '''    async def play_dynamic_wallpaper():
        """在后台异步循环中，用 FFmpeg 解码并渲染动态壁纸帧"""
        import glob
        import subprocess
        
        # 在后台任务中查找最新的动态壁纸文件
        wallpaper_files = glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.gif")) + glob.glob(os.path.join(BASE_DIR, "assets", "wallpaper_*.mp4"))
        
        if not wallpaper_files:
            bg_image.visible = False
            bg_image.update()
            return
        
        latest_wp = max(wallpaper_files, key=os.path.getctime)
        
        # 使用 FFmpeg 将动态素材处理成连续的原始图像帧
        # 这里的关键是输出 rawvideo 格式，直接交给 RawImage 渲染
        cmd = [
            "ffmpeg",
            "-i", latest_wp,       # 输入文件
            "-f", "image2pipe",    # 输出格式为图像管道
            "-pix_fmt", "rgba",    # 像素格式为 RGBA
            "-vcodec", "rawvideo", # 视频编解码器为 rawvideo
            "-"                    # 输出到标准输出
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        
        bg_image.visible = True
        bg_image.update()
        
        try:
            while True:
                # 从管道中读取一帧数据（假设是 1440x900 的 RGBA 数据）
                frame_data = await process.stdout.read(1440 * 900 * 4)
                if not frame_data:
                    break # 视频播放结束
                
                # 将原始字节数据包装成 Pillow 图像，然后直接渲染
                from PIL import Image
                frame = Image.frombytes('RGBA', (1440, 900), frame_data, 'raw', 'RGBA')
                await bg_image.render(frame, premultiplied=True)
                
                # 控制帧率，避免占满 CPU（比如 30 FPS）
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
            bg_image.visible = False
            bg_image.update()
    
    # 将播放函数暴露给 page 对象，方便后续切换壁纸时调用
    page.play_dynamic_wallpaper = play_dynamic_wallpaper
    
    def update_wallpaper_hot():
        """当用户更换壁纸时，取消旧的播放任务并启动新的"""
        if hasattr(page, "wallpaper_task") and page.wallpaper_task:
            page.wallpaper_task.cancel()
        # 创建并保存新的播放任务
        page.wallpaper_task = asyncio.create_task(play_dynamic_wallpaper())
    
    page.update_wallpaper_hot = update_wallpaper_hot'''

new_hot = '''    async def play_dynamic_wallpaper():
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

content = content.replace(old_hot, new_hot)

# 3. 修复 startup 时的调用
if "asyncio.create_task(play_dynamic_wallpaper())" in content:
    content = content.replace("asyncio.create_task(play_dynamic_wallpaper())", "update_wallpaper_hot()")

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 动态壁纸引擎注入完毕！支持 GIF 和 MP4 格式。")