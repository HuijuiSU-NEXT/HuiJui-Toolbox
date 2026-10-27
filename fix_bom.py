# fix_bom.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.join(BASE_DIR, "main_final.py")

print("⏳ 正在清洗文件中的 BOM 字符...")

try:
  # 使用 utf-8-sig 读取，它会自动吞掉 BOM 头
  with open(main_path, "r", encoding="utf-8-sig") as f:
    content = f.read()
  
  # 强制以标准的 utf-8 (无 BOM) 格式写回
  with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)
    
  print("✅ main_final.py 编码已完美洗底！BOM 消失！")
except Exception as e:
  print(f"❌ 清洗失败: {e}")