# fix_smart_ui.py
import os

settings_path = "pages/settings.py"

with open(settings_path, "r", encoding="utf-8") as f:
  content = f.read()

# 找到 on_file_selected 的逻辑，在保存图片后插入智能分析逻辑
old_logic = '''          # 刷新主界面
          if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()
          if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)
            
          show_snackbar("高清壁纸已应用！")'''

new_logic = '''          # 🚨 核心：智能 UI 调参引擎
          if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif']:
            try:
              from PIL import ImageStat
              # 快速分析图片平均亮度
              img_small = img.resize((50, 50), Image.Resampling.BILINEAR)
              stat = ImageStat.Stat(img_small)
              avg_brightness = sum(stat.mean) / 3.0
              
              print(f"🧠 [智能UI] 检测到壁纸平均亮度: {avg_brightness:.1f}")
              
              if avg_brightness > 160:
                # 亮色壁纸：高对比度模式
                CFG.set("ui_material", "default")
                CFG.set("card_opacity", 0.45)
                CFG.set("blur_radius", 0)
                print("🧠 [智能UI] 亮色壁纸 -> 已切换为: 默认材质 + 高透明度暗色卡片 + 无模糊")
                show_snackbar("检测到壁纸较亮，已自动切换至高对比度模式！")
              elif avg_brightness < 80:
                # 暗色壁纸：玻璃质感模式
                CFG.set("ui_material", "liquid")
                CFG.set("card_opacity", 0.12)
                CFG.set("blur_radius", 15)
                print("🧠 [智能UI] 暗色壁纸 -> 已切换为: 液态玻璃 + 低透明度卡片 + 高模糊")
                show_snackbar("检测到壁纸较暗，已自动切换至沉浸玻璃模式！")
              else:
                # 中等亮度：标准毛玻璃
                CFG.set("ui_material", "frosted")
                CFG.set("card_opacity", 0.25)
                CFG.set("blur_radius", 10)
                print("🧠 [智能UI] 中等壁纸 -> 已切换为: 毛玻璃 + 平衡透明度")
                show_snackbar("已为您自动适配最佳毛玻璃参数！")
              
              CFG.save()
            except Exception as e:
              print(f"智能分析失败: {e}")

          # 刷新主界面
          if hasattr(page, "update_wallpaper_hot"):
            page.update_wallpaper_hot()
          if hasattr(page, "refresh_main_ui"):
            page.refresh_main_ui(tab_index=4)
            
          show_snackbar("高清壁纸已应用并智能适配！")'''

if old_logic in content:
  content = content.replace(old_logic, new_logic)
  print("✅ 智能环境光感知引擎注入成功！")
else:
  print("⚠️ 未找到精确匹配的代码，尝试正则替换...")
  import re
  pattern = r'          # 刷新主界面\s*if hasattr\(page, "update_wallpaper_hot"\):\s*page\.update_wallpaper_hot\(\)\s*if hasattr\(page, "refresh_main_ui"\):\s*page\.refresh_main_ui\(tab_index=4\)\s*show_snackbar\("高清壁纸已应用！"\)'
  content = re.sub(pattern, new_logic, content)
  print("✅ 已通过正则完成兜底注入！")

with open(settings_path, "w", encoding="utf-8") as f:
  f.write(content)