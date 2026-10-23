# ui_onboarding_gradients.py
# HyperOS 4 风格动态渐变与配色方案

PALETTES = {
    "dynamic_teal": {
        "name": "官方动态墨绿",
        "bg_gradient": ["#0A1929", "#1B3A4B", "#0D2818"],
        "orb1": "#26A69A", "orb2": "#4DB6AC", "orb3": "#00897B",
        "orb_opacity": 0.25,
        "text_main": "#E0F2F1", "text_sub": "#B2DFDB",
        "btn_bg": "#26A69A", "btn_icon": "#FFFFFF",
    },
    "lavender_gold": {
        "name": "薰衣草与柔金",
        "bg_gradient": ["#F3E5F5", "#FCE4EC", "#FFF8E1"],
        "orb1": "#CE93D8", "orb2": "#FFD54F", "orb3": "#B39DDB",
        "orb_opacity": 0.35,
        "text_main": "#4A148C", "text_sub": "#7B1FA2",
        "btn_bg": "#CE93D8", "btn_icon": "#FFFFFF",
    },
    "serene_blue": {
        "name": "宁静蓝与石板灰",
        "bg_gradient": ["#E3F2FD", "#ECEFF1", "#F5F7FA"],
        "orb1": "#42A5F5", "orb2": "#78909C", "orb3": "#90CAF9",
        "orb_opacity": 0.3,
        "text_main": "#0D47A1", "text_sub": "#455A64",
        "btn_bg": "#42A5F5", "btn_icon": "#FFFFFF",
    },
    "organic_green": {
        "name": "有机绿与橄榄",
        "bg_gradient": ["#E8F5E9", "#F1F8E9", "#F9FBE7"],
        "orb1": "#66BB6A", "orb2": "#D4E157", "orb3": "#A5D6A7",
        "orb_opacity": 0.35,
        "text_main": "#1B5E20", "text_sub": "#558B2F",
        "btn_bg": "#66BB6A", "btn_icon": "#FFFFFF",
    },
}
ACTIVE_PALETTE = "dynamic_teal"
def get_palette():
    return PALETTES[ACTIVE_PALETTE]
