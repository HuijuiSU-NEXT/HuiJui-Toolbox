from .page_welcome import build_welcome
from .page_features import build_features
from .page_disclaimer import build_disclaimer
def get_page(idx, t, core):
    if idx == 0: return build_welcome(t)
    elif idx == 1: return build_features(t)
    else: return build_disclaimer(t, core)
