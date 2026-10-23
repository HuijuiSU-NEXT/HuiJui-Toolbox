# add_author_links.py
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(BASE_DIR, "pages", "settings.py")

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# 定义要注入的UI代码块
links_block = '''
    # 🚨 作者主页链接
    author_links = ft.Container(
        content=ft.Row([
            ft.TextButton(
                "酷安主页", icon=ft.Icons.ANDROID, 
                on_click=lambda e: page.launch_url("https://www.coolapk.com/u/43549687"),
                style=ft.ButtonStyle(color=theme_color)
            ),
            ft.TextButton(
                "GitHub", icon=ft.Icons.CODE, 
                on_click=lambda e: page.launch_url("https://github.com/hhcdxii-ship-it"),
                style=ft.ButtonStyle(color=theme_color)
            ),
            ft.TextButton(
                "QQ 群", icon=ft.Icons.GROUP, 
                on_click=lambda e: page.launch_url("https://qm.qq.com/q/bVWVFT0PYY"),
                style=ft.ButtonStyle(color=theme_color)
            ),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        padding=ft.padding.only(top=20, bottom=10)
    )
'''

# 找到 return 的代码块，把链接区块插在它前面
# 构建完整的 return 语句
old_return = '''    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            ft.Container(height=10),
            ft.Column([card_step1, ft.Container(height=10), card_step2, ft.Container(height=10), card_step3, ft.Container(height=10), card_step4], scroll=ft.ScrollMode.AUTO, expand=True)
        ], expand=True),
        expand=True, padding=20
    )'''

new_return = f'''{links_block}
    return ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.Icons.PALETTE, color=theme_color, size=28), ft.Text("个性化设置", size=24, weight=ft.FontWeight.BOLD, color="white")]),
            ft.Container(height=10),
            ft.Column([card_step1, ft.Container(height=10), card_step2, ft.Container(height=10), card_step3, ft.Container(height=10), card_step4], scroll=ft.ScrollMode.AUTO, expand=True),
            author_links  # 🚨 注入到底部
        ], expand=True),
        expand=True, padding=20
    )'''

if old_return in content:
    content = content.replace(old_return, new_return)
    print("✅ 成功将作者主页链接注入到个性化页面底部！")
else:
    # 兜底正则：匹配几乎所有的 return ft.Container 结构
    pattern = r'(    return ft\.Container\(\s*content=ft\.Column\(\[.*?\]\s*\),\s*expand=True,\s*padding=20\s*\))'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(1), new_return)
        print("✅ 已通过正则成功注入作者主页链接！")
    else:
        print("⚠️ 未找到插入位置，请手动在 settings.py 的 return 前加入 author_links 代码。")

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(content)

print("🚀 注入完毕！请运行 python main_final.py 查看底部链接。")