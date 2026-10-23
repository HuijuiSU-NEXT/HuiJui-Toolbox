# catch_flicker.py
import mss
import time
import os

# 如果没有 mss 库，请先执行：pip install mss
try:
    import mss
except ImportError:
    print("请先在终端运行: pip install mss")
    exit()

save_dir = "flicker_frames"
os.makedirs(save_dir, exist_ok=True)
print(f"开始截图，存放到 {save_dir} 目录...")
print("请现在去操作界面，直到你看到闪烁，然后按 Ctrl+C 停止。")

try:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        count = 0
        while True:
            count += 1
            filename = os.path.join(save_dir, f"frame_{count:04d}.png")
            sct.shot(mon=monitor, output=filename)
            # 每秒截10张，如果你觉得不够快，可以改成0.05
            time.sleep(0.1)
except KeyboardInterrupt:
    print(f"抓取结束！共截取 {count} 张图片。请去 {save_dir} 文件夹里找找哪一张是闪烁的。")