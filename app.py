"""
WearBlend - Virtual Try-On Application
Realistic Mannequin Visualization
"""

import streamlit as st
from PIL import Image
import io
from typing import Dict, Optional, Tuple

from utils.image_processor import ImageProcessor
from utils.color_utils import ColorUtils
from utils.style_engine import StyleEngine
from utils.realistic_mannequin import RealisticMannequin

# Page configuration
st.set_page_config(
    page_title="WearBlend | Virtual Try-On",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern design tokens — inspired by Framer / 21st.dev
COLORS = {
    'bg':            '#0a0a0f',
    'bg_alt':        '#0e0e15',
    'surface':       'rgba(255,255,255,0.04)',
    'surface_hi':    'rgba(255,255,255,0.06)',
    'border':        'rgba(255,255,255,0.08)',
    'border_hi':     'rgba(255,255,255,0.14)',
    'text':          '#f5f5f7',
    'text_mute':     '#a1a1aa',
    'text_dim':      '#71717a',
    'accent':        '#8b5cf6',
    'accent_2':      '#ec4899',
    'accent_3':      '#3b82f6',
    'success':       '#10b981',
    'warning':       '#f59e0b',
}


def load_custom_css():
    """Load a modern, Framer-inspired design system with full mobile responsiveness."""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {{
        --bg: {COLORS['bg']};
        --bg-alt: {COLORS['bg_alt']};
        --surface: {COLORS['surface']};
        --surface-hi: {COLORS['surface_hi']};
        --border: {COLORS['border']};
        --border-hi: {COLORS['border_hi']};
        --text: {COLORS['text']};
        --mute: {COLORS['text_mute']};
        --dim: {COLORS['text_dim']};
        --accent: {COLORS['accent']};
        --accent-2: {COLORS['accent_2']};
        --accent-3: {COLORS['accent_3']};
        --grad: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #3b82f6 100%);
        --grad-soft: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(236,72,153,0.10) 50%, rgba(59,130,246,0.15) 100%);
    }}

    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    html, body, [class*="css"] {{
        color: var(--text);
    }}

    .stApp {{
        background: var(--bg);
        background-image:
            radial-gradient(at 8% 0%,  rgba(139,92,246,0.18) 0px, transparent 50%),
            radial-gradient(at 92% 6%, rgba(236,72,153,0.14) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(59,130,246,0.12) 0px, transparent 55%);
        background-attachment: fixed;
    }}

    /* hide Streamlit chrome (scoped selectors only — never bare header/footer) */
    #MainMenu {{ visibility: hidden !important; }}
    .stDeployButton {{ display: none !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stDecoration"] {{ display: none !important; }}
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{
        color: var(--text);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        backdrop-filter: blur(16px);
    }}

    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px;
    }}

    /* ─────────────── HERO ─────────────── */
    .hero {{
        position: relative;
        padding: 3.5rem 2rem 2.5rem;
        margin: 0.5rem 0 1.75rem;
        text-align: center;
        border-radius: 28px;
        overflow: hidden;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)),
            radial-gradient(120% 100% at 50% 0%, rgba(139,92,246,0.22), transparent 60%);
        border: 1px solid var(--border);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }}
    .hero::before {{
        content: "";
        position: absolute; inset: -1px;
        background: var(--grad);
        opacity: 0.22;
        filter: blur(60px);
        z-index: 0;
    }}
    .hero-inner {{ position: relative; z-index: 1; }}

    .badge {{
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 14px;
        font-size: 12px; font-weight: 500;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--mute);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 999px;
        margin-bottom: 1.25rem;
    }}
    .badge .dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--success); box-shadow: 0 0 10px var(--success);
        animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.6; transform: scale(1.3); }}
    }}

    .hero h1 {{
        font-family: 'Space Grotesk', 'Inter', sans-serif;
        font-size: clamp(2.4rem, 7vw, 4.5rem);
        font-weight: 700;
        line-height: 1.02;
        letter-spacing: -0.04em;
        margin: 0;
        background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero h1 .grad {{
        background: var(--grad);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }}
    .hero p {{
        color: var(--mute);
        font-size: clamp(0.95rem, 1.6vw, 1.15rem);
        margin: 1rem auto 0;
        max-width: 600px;
        line-height: 1.55;
        font-weight: 400;
    }}

    /* ─────────────── PANELS / CARDS ─────────────── */
    .panel {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: border-color 0.3s ease, transform 0.3s ease;
    }}
    .panel:hover {{ border-color: var(--border-hi); }}

    .panel-head {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 1.25rem;
    }}
    .panel-title {{
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--mute);
    }}
    .panel-num {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 22px; height: 22px;
        font-size: 11px; font-weight: 600;
        color: var(--text);
        background: var(--surface-hi);
        border: 1px solid var(--border);
        border-radius: 7px;
    }}

    .dev-pill {{
        display: inline-flex; align-items: center; gap: 7px;
        padding: 5px 10px 5px 9px;
        font-size: 10.5px; font-weight: 500;
        letter-spacing: 0.04em;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.10);
        border: 1px solid rgba(245, 158, 11, 0.30);
        border-radius: 999px;
        white-space: nowrap;
    }}
    .dev-pill .dev-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: #fbbf24;
        box-shadow: 0 0 8px #fbbf24;
        animation: pulse 2s ease-in-out infinite;
    }}
    @media (max-width: 480px) {{
        .dev-pill {{ font-size: 9.5px; padding: 4px 8px; }}
    }}

    .section-label {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text);
        letter-spacing: -0.01em;
        margin: 0 0 1rem;
        display: flex; align-items: center; gap: 10px;
    }}
    .section-label::before {{
        content: "";
        width: 4px; height: 18px;
        background: var(--grad);
        border-radius: 4px;
    }}

    /* ─────────────── BUTTONS ─────────────── */
    .stButton > button, .stDownloadButton > button {{
        background: var(--surface-hi) !important;
        color: var(--text) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset !important;
        width: 100% !important;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: rgba(255,255,255,0.10) !important;
        border-color: rgba(255,255,255,0.22) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 20px -8px rgba(139,92,246,0.35) !important;
    }}
    .stButton > button[kind="primary"] {{
        background: var(--grad) !important;
        border: 1px solid transparent !important;
        color: white !important;
        box-shadow: 0 8px 28px -8px rgba(139,92,246,0.65) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        filter: brightness(1.08) !important;
        box-shadow: 0 12px 36px -8px rgba(139,92,246,0.85) !important;
    }}
    .stDownloadButton > button {{
        background: var(--grad) !important;
        border: 1px solid transparent !important;
        font-weight: 600 !important;
        padding: 0.85rem 1.25rem !important;
        box-shadow: 0 10px 28px -10px rgba(139,92,246,0.7) !important;
    }}

    /* ─────────────── INPUTS / SELECT / FILE ─────────────── */
    .stSelectbox [data-baseweb="select"] > div {{
        background: var(--surface-hi) !important;
        border: 1px solid var(--border-hi) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }}
    .stSelectbox label, .stFileUploader label, .stTextInput label {{
        color: var(--mute) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background: var(--surface) !important;
        border: 1.5px dashed var(--border-hi) !important;
        border-radius: 14px !important;
        padding: 1.1rem !important;
        transition: all 0.25s ease !important;
        min-height: 110px !important;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{
        background: var(--surface-hi) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 4px rgba(139,92,246,0.10) !important;
    }}
    [data-testid="stFileUploaderDropzone"] section {{ color: var(--mute) !important; }}
    [data-testid="stFileUploaderDropzone"] button {{
        background: var(--surface-hi) !important;
        color: var(--text) !important;
        border: 1px solid var(--border-hi) !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: var(--mute) !important;
    }}

    /* ─────────────── ITEM CARDS ─────────────── */
    .item-row {{
        display: flex; align-items: center; gap: 14px;
        padding: 14px;
        margin: 12px 0;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        transition: all 0.25s ease;
    }}
    .item-row:hover {{ background: var(--surface-hi); border-color: var(--border-hi); }}
    .item-thumb {{
        width: 56px; height: 56px;
        border-radius: 10px;
        background: var(--surface-hi);
        border: 1px solid var(--border);
        overflow: hidden;
        flex-shrink: 0;
    }}
    .item-name {{ font-weight: 600; font-size: 0.92rem; color: var(--text); }}
    .item-meta {{ font-size: 0.78rem; color: var(--dim); }}
    .item-status {{
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.72rem; font-weight: 500;
        color: var(--success);
    }}
    .item-status::before {{
        content: ""; width: 6px; height: 6px;
        background: var(--success); border-radius: 50%;
        box-shadow: 0 0 8px var(--success);
    }}

    .upload-tile {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
    }}
    .upload-tile-left {{ display: flex; align-items: center; gap: 12px; }}
    .upload-icon {{
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        background: var(--surface-hi);
        border: 1px solid var(--border);
        border-radius: 10px;
        font-size: 16px;
    }}
    .upload-label {{ font-weight: 600; font-size: 0.9rem; color: var(--text); margin: 0; }}
    .upload-desc  {{ font-size: 0.75rem; color: var(--dim); margin: 0; }}

    /* ─────────────── PREVIEW STAGE ─────────────── */
    .stage {{
        position: relative;
        border-radius: 24px;
        padding: 1.5rem;
        background:
            radial-gradient(120% 80% at 50% 0%, rgba(139,92,246,0.18), transparent 60%),
            linear-gradient(180deg, #14141c 0%, #0c0c12 100%);
        border: 1px solid var(--border);
        min-height: 460px;
        overflow: hidden;
    }}
    .stage::before {{
        content: "";
        position: absolute; inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 28px 28px;
        mask-image: radial-gradient(ellipse at center, black 0%, transparent 75%);
        -webkit-mask-image: radial-gradient(ellipse at center, black 0%, transparent 75%);
        pointer-events: none;
    }}

    .stage [data-testid="stImage"] {{ position: relative; z-index: 1; }}
    .stage img {{
        max-height: 540px;
        object-fit: contain;
        filter: drop-shadow(0 30px 60px rgba(139,92,246,0.18));
    }}

    .empty-cta {{
        text-align: center;
        color: var(--mute);
        font-size: 0.9rem;
        padding: 1rem 0 0;
    }}

    .empty-state {{
        position: relative; z-index: 1;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 380px;
        text-align: center;
        padding: 2rem 1rem;
    }}
    .empty-icon {{
        width: 64px; height: 64px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; color: var(--text);
        background: var(--surface-hi);
        border: 1px solid var(--border-hi);
        border-radius: 18px;
        margin-bottom: 1rem;
        box-shadow: 0 0 0 6px rgba(139,92,246,0.06), inset 0 0 0 1px rgba(255,255,255,0.04);
    }}
    .empty-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem; font-weight: 600;
        color: var(--text);
        margin: 0;
    }}
    .empty-sub {{
        font-size: 0.85rem;
        color: var(--mute);
        margin: 6px 0 0;
        line-height: 1.55;
    }}

    /* ─────────────── SCORE / METRIC ─────────────── */
    .score-card {{
        position: relative;
        background: linear-gradient(135deg, rgba(139,92,246,0.10), rgba(236,72,153,0.08));
        border: 1px solid var(--border-hi);
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        overflow: hidden;
    }}
    .score-card::before {{
        content: "";
        position: absolute; inset: 0;
        background: var(--grad);
        opacity: 0.10;
        filter: blur(40px);
        pointer-events: none;
    }}
    .score-num {{
        position: relative;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        line-height: 1;
        background: var(--grad);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
    }}
    .score-cap {{
        position: relative;
        font-size: 0.72rem; font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--mute);
        margin-top: 0.4rem;
    }}

    .metric-row {{ margin: 12px 0; }}
    .metric-top  {{
        display: flex; justify-content: space-between;
        font-size: 0.82rem;
    }}
    .metric-top span:first-child {{ color: var(--mute); }}
    .metric-top span:last-child  {{ color: var(--text); font-weight: 600; }}
    .bar {{
        height: 5px;
        background: rgba(255,255,255,0.06);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 6px;
    }}
    .bar-fill {{
        height: 100%;
        background: var(--grad);
        border-radius: 999px;
        transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
    }}

    /* ─────────────── CHIPS / SWATCHES ─────────────── */
    .chip-row {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .chip {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 7px 12px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 999px;
        font-size: 0.78rem;
        color: var(--mute);
    }}

    .swatch {{
        width: 44px; height: 44px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.14);
        margin: 0 auto;
        box-shadow: 0 6px 14px -6px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.04);
        transition: transform 0.2s ease;
    }}
    .swatch:hover {{ transform: scale(1.08); }}

    .skin-dot {{
        width: 36px; height: 36px; border-radius: 50%;
        margin: 0 auto;
        box-shadow: 0 4px 12px -4px rgba(0,0,0,0.5);
        transition: transform 0.2s ease;
    }}
    .skin-dot.active {{
        box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--accent), 0 6px 14px -4px rgba(139,92,246,0.6);
        transform: scale(1.05);
    }}

    /* ─────────────── SEGMENTED ─────────────── */
    .seg-wrap {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 6px;
        padding: 4px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
    }}

    /* ─────────────── SUGGESTIONS ─────────────── */
    .sug-card {{
        display: flex; align-items: center; gap: 12px;
        padding: 14px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        transition: all 0.25s ease;
    }}
    .sug-card:hover {{ background: var(--surface-hi); border-color: var(--border-hi); transform: translateY(-2px); }}
    .sug-color {{
        width: 38px; height: 38px;
        border-radius: 10px;
        flex-shrink: 0;
        border: 1px solid rgba(255,255,255,0.14);
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
    }}
    .sug-name {{ font-weight: 600; font-size: 0.9rem; color: var(--text); margin: 0; }}
    .sug-reason {{ font-size: 0.74rem; color: var(--dim); margin: 2px 0 0; line-height: 1.4; }}

    /* ─────────────── EXPANDER ─────────────── */
    .streamlit-expanderHeader, [data-testid="stExpander"] summary {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        font-weight: 500 !important;
    }}
    [data-testid="stExpander"] {{
        border: none !important;
        background: transparent !important;
    }}

    /* ─────────────── SIDEBAR ─────────────── */
    [data-testid="stSidebar"] {{
        background: rgba(10,10,15,0.85) !important;
        border-right: 1px solid var(--border) !important;
        backdrop-filter: blur(20px);
    }}
    [data-testid="stSidebar"] * {{ color: var(--text); }}
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {{ color: var(--mute); font-size: 0.85rem; }}

    /* ─────────────── ALERTS / TOASTS ─────────────── */
    .stAlert, [data-testid="stNotification"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
    }}
    [data-testid="stSpinner"] > div {{ border-top-color: var(--accent) !important; }}

    /* ─────────────── DIVIDER ─────────────── */
    .div-line {{
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-hi), transparent);
        margin: 1.75rem 0;
    }}

    /* ─────────────── CAPTIONS / TEXT ─────────────── */
    .stCaption, [data-testid="stCaptionContainer"] {{ color: var(--dim) !important; }}
    .stMarkdown p {{ color: var(--mute); }}
    .stMarkdown strong {{ color: var(--text); }}

    label[data-testid="stWidgetLabel"] p {{ color: var(--mute) !important; font-size: 0.85rem !important; }}

    /* ─────────────── FEATURE STRIP ─────────────── */
    .feat-strip {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 1.25rem 0 1.75rem;
    }}
    .feat {{
        padding: 14px 16px;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        display: flex; align-items: center; gap: 12px;
        transition: all 0.25s ease;
    }}
    .feat:hover {{ border-color: var(--border-hi); transform: translateY(-2px); }}
    .feat-icon {{
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: var(--grad-soft);
        border: 1px solid var(--border);
        font-size: 16px;
    }}
    .feat-text {{ display: flex; flex-direction: column; }}
    .feat-title {{ font-weight: 600; font-size: 0.85rem; color: var(--text); }}
    .feat-sub   {{ font-size: 0.72rem; color: var(--dim); }}

    /* ─────────────── MOBILE RESPONSIVE ─────────────── */
    @media (max-width: 768px) {{
        .block-container {{
            padding: 0.5rem 0.75rem 3rem !important;
        }}
        .hero {{
            padding: 2.5rem 1.25rem 2rem;
            border-radius: 22px;
            margin: 0.25rem 0 1.25rem;
        }}
        .hero h1 {{ font-size: 2.4rem; }}
        .hero p  {{ font-size: 0.95rem; }}
        .panel {{
            padding: 1.1rem;
            border-radius: 18px;
        }}
        .stage {{
            min-height: 360px;
            padding: 1rem;
            border-radius: 20px;
        }}
        .feat-strip {{
            grid-template-columns: 1fr;
            gap: 8px;
        }}
        .feat {{ padding: 12px 14px; }}
        .stColumn, [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }}
        [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap !important;
            gap: 12px !important;
        }}
        .score-num {{ font-size: 2.8rem; }}
        .stage img {{ max-height: 420px; }}
        .section-label {{ font-size: 0.98rem; }}
    }}
    @media (max-width: 480px) {{
        .hero {{ padding: 2rem 1rem 1.5rem; }}
        .hero h1 {{ font-size: 2rem; }}
        .badge {{ font-size: 10px; padding: 5px 12px; }}
        .panel {{ padding: 1rem; }}
        .item-row, .upload-tile {{ padding: 12px; gap: 10px; }}
        .item-thumb {{ width: 48px; height: 48px; }}
    }}

    /* fade-in */
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .panel, .hero, .feat, .item-row, .sug-card {{
        animation: fadeUp 0.5s cubic-bezier(0.4,0,0.2,1) backwards;
    }}
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'page': 'main',
        'clothing_items': {},
        'processed_items': {},
        'dominant_colors': {},
        'selected_variation': None,
        'gender': 'male',
        'skin_tone': 'medium',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_hero():
    """Hero section with animated badge and gradient headline."""
    item_count = len(st.session_state.processed_items)
    st.markdown(f"""
    <div class="hero">
      <div class="hero-inner">
        <div class="badge">
          <span class="dot"></span>
          <span>AI Virtual Try-On · Live</span>
        </div>
        <h1>Try clothes on a<br/><span class="grad">realistic mannequin.</span></h1>
        <p>Upload garments and instantly visualize complete outfits with intelligent
        background removal, style scoring, and color recommendations.</p>
      </div>
    </div>

    <div class="feat-strip">
      <div class="feat">
        <div class="feat-icon">✦</div>
        <div class="feat-text">
          <span class="feat-title">Auto Background Removal</span>
          <span class="feat-sub">Clean cutouts in seconds</span>
        </div>
      </div>
      <div class="feat">
        <div class="feat-icon">◈</div>
        <div class="feat-text">
          <span class="feat-title">Style Intelligence</span>
          <span class="feat-sub">Outfit scoring & analysis</span>
        </div>
      </div>
      <div class="feat">
        <div class="feat-icon">◐</div>
        <div class="feat-text">
          <span class="feat-title">Color Variations</span>
          <span class="feat-sub">Recolor anything live</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_main_page():
    """Render main application page"""
    render_hero()

    # Initialize components
    image_processor = ImageProcessor()
    style_engine = StyleEngine()
    color_utils = ColorUtils()
    mannequin = RealisticMannequin(gender=st.session_state.gender, skin_tone=st.session_state.skin_tone)

    # Main layout - controls + stage
    col_upload, col_preview = st.columns([1, 1.15], gap="large")

    with col_upload:
        # ─── MANNEQUIN PANEL ────────────────────────────────
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">01 · Mannequin</span>
            <span class="panel-num">M</span>
          </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Gender</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2, gap="small")
        with g1:
            if st.button("◧  Male", use_container_width=True,
                        type="primary" if st.session_state.gender == 'male' else "secondary",
                        key="btn_gender_male"):
                st.session_state.gender = 'male'
                st.rerun()
        with g2:
            if st.button("◨  Female", use_container_width=True,
                        type="primary" if st.session_state.gender == 'female' else "secondary",
                        key="btn_gender_female"):
                st.session_state.gender = 'female'
                st.rerun()

        st.markdown('<div style="height: 1.25rem"></div><div class="section-label">Skin Tone</div>', unsafe_allow_html=True)
        skin_tones = {
            'light':  '#f0dfcf',
            'medium': '#ddc3ac',
            'tan':    '#c39e80',
            'dark':   '#8c644b',
            'deep':   '#5a3c2d',
        }
        tone_cols = st.columns(5, gap="small")
        for col, (tone, color) in zip(tone_cols, skin_tones.items()):
            with col:
                active = "active" if st.session_state.skin_tone == tone else ""
                st.markdown(f"""
                <div style="text-align:center; margin-bottom: 6px;">
                  <div class="skin-dot {active}" style="background:{color};"></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(tone.title(), key=f"tone_{tone}", use_container_width=True):
                    st.session_state.skin_tone = tone
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # ─── UPLOAD PANEL ───────────────────────────────────
        st.markdown('<div style="height: 1rem"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">02 · Wardrobe</span>
            <span class="panel-num">W</span>
          </div>
        """, unsafe_allow_html=True)

        clothing_config = [
            ('shirt',  'Shirt / Top',         'Main upper garment',  '◇'),
            ('pants',  'Pants / Bottom',      'Lower body garment',  '◈'),
            ('jacket', 'Jacket / Outerwear',  'Optional layer',      '◊'),
            ('shoes',  'Shoes / Footwear',    'Complete the look',   '◉'),
        ]
        accessory_config = [
            ('tie',  'Tie / Neckwear', 'Formal accent'),
            ('belt', 'Belt',           'Waist accessory'),
        ]

        for item_key, item_label, item_desc, icon in clothing_config:
            st.markdown(f"""
            <div class="upload-tile">
              <div class="upload-tile-left">
                <div class="upload-icon">{icon}</div>
                <div>
                  <p class="upload-label">{item_label}</p>
                  <p class="upload-desc">{item_desc}</p>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                f"Upload {item_label}",
                type=['png', 'jpg', 'jpeg', 'webp'],
                key=f"upload_{item_key}",
                label_visibility="collapsed"
            )

            if uploaded_file:
                image = Image.open(uploaded_file)
                st.session_state.clothing_items[item_key] = image
                with st.spinner("Processing image…"):
                    processed = image_processor.remove_background(image)
                    st.session_state.processed_items[item_key] = processed
                    colors = image_processor.extract_dominant_colors(image, 3)
                    st.session_state.dominant_colors[item_key] = colors

            if item_key in st.session_state.clothing_items:
                c1, c2 = st.columns([1, 3], gap="small")
                with c1:
                    st.image(st.session_state.clothing_items[item_key], width=72)
                with c2:
                    st.markdown('<div class="item-status">Ready to wear</div>', unsafe_allow_html=True)
                    if st.button("Remove", key=f"remove_{item_key}", use_container_width=True):
                        for d in (st.session_state.clothing_items,
                                  st.session_state.processed_items,
                                  st.session_state.dominant_colors):
                            d.pop(item_key, None)
                        st.rerun()

        with st.expander("Accessories (optional)"):
            for item_key, item_label, item_desc in accessory_config:
                uploaded_file = st.file_uploader(
                    item_label,
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    key=f"upload_{item_key}",
                    help=item_desc
                )
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    st.session_state.clothing_items[item_key] = image
                    with st.spinner("Processing…"):
                        processed = image_processor.remove_background(image)
                        st.session_state.processed_items[item_key] = processed
                        colors = image_processor.extract_dominant_colors(image, 3)
                        st.session_state.dominant_colors[item_key] = colors
                    st.success(f"{item_label} added")

        st.markdown("</div>", unsafe_allow_html=True)

    # ─── PREVIEW STAGE ─────────────────────────────────────
    with col_preview:
        st.markdown("""
        <div class="panel" style="padding: 1rem;">
          <div class="panel-head" style="padding: 0.5rem 0.5rem 0;">
            <span class="panel-title">03 · Live Preview</span>
            <span class="dev-pill">
              <span class="dev-dot"></span>
              Development mode · render under refinement
            </span>
          </div>
        """, unsafe_allow_html=True)

        mannequin = RealisticMannequin(
            gender=st.session_state.gender,
            skin_tone=st.session_state.skin_tone
        )

        st.markdown('<div class="stage">', unsafe_allow_html=True)
        if st.session_state.processed_items:
            outfit_image = mannequin.render_outfit(st.session_state.processed_items)
            st.image(outfit_image, use_container_width=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">◇</div>
              <p class="empty-title">No outfit yet</p>
              <p class="empty-sub">Upload a shirt, pants, and shoes —<br/>they'll stack into a clean flat-lay preview.</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.processed_items:
            outfit_image = mannequin.render_outfit(st.session_state.processed_items)
            img_bytes = mannequin.get_image_bytes(outfit_image)
            st.markdown('<div style="height: 0.75rem"></div>', unsafe_allow_html=True)
            st.download_button(
                label="↓  Download outfit as PNG",
                data=img_bytes,
                file_name="wearblend_outfit.png",
                mime="image/png",
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ─── STYLE ANALYSIS ────────────────────────────────────
    if st.session_state.processed_items:
        st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)

        outfit_colors = {}
        for item_key, colors in st.session_state.dominant_colors.items():
            if colors:
                outfit_colors[item_key] = colors[0]

        analysis_col1, analysis_col2 = st.columns([1, 1], gap="large")

        with analysis_col1:
            st.markdown("""
            <div class="panel">
              <div class="panel-head">
                <span class="panel-title">04 · Style Analysis</span>
                <span class="panel-num">★</span>
              </div>
            """, unsafe_allow_html=True)

            if outfit_colors:
                analysis = style_engine.analyze_outfit(outfit_colors)
                rating = style_engine.rate_outfit(outfit_colors)

                st.markdown(f"""
                <div class="score-card">
                  <div class="score-num">{rating['overall']}</div>
                  <div class="score-cap">Overall Score</div>
                </div>
                <div style="height: 1.25rem"></div>
                """, unsafe_allow_html=True)

                for category, score in rating['categories'].items():
                    label = category.replace('_', ' ').title()
                    st.markdown(f"""
                    <div class="metric-row">
                      <div class="metric-top"><span>{label}</span><span>{score}%</span></div>
                      <div class="bar"><div class="bar-fill" style="width:{score}%"></div></div>
                    </div>
                    """, unsafe_allow_html=True)

                if analysis['strengths']:
                    st.markdown('<div style="height: 1rem"></div><div class="section-label">Strengths</div>', unsafe_allow_html=True)
                    for strength in analysis['strengths'][:2]:
                        st.markdown(f"""
                        <div class="sug-card">
                          <div class="sug-color" style="background: var(--grad);"></div>
                          <div>
                            <p class="sug-name">{strength}</p>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with analysis_col2:
            st.markdown("""
            <div class="panel">
              <div class="panel-head">
                <span class="panel-title">05 · Color Lab</span>
                <span class="panel-num">◐</span>
              </div>
            """, unsafe_allow_html=True)

            item_options = list(st.session_state.processed_items.keys())
            if item_options:
                selected_item = st.selectbox(
                    "Select item to recolor",
                    item_options,
                    format_func=lambda x: x.replace('_', ' ').title()
                )

                if selected_item and selected_item in st.session_state.dominant_colors:
                    original_color = st.session_state.dominant_colors[selected_item][0]
                    variations = color_utils.get_color_variations(original_color, 5)

                    swatch_cols = st.columns(len(variations), gap="small")
                    for idx, (col, var) in enumerate(zip(swatch_cols, variations)):
                        with col:
                            color_hex = '#{:02x}{:02x}{:02x}'.format(*var['rgb'])
                            st.markdown(f"""
                            <div style="text-align:center; margin-bottom: 6px;">
                              <div class="swatch" style="background:{color_hex};"></div>
                              <p style="font-size: 0.68rem; color: var(--dim); margin: 6px 0 0;">{var['name'][:10]}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button("Apply", key=f"var_{idx}", use_container_width=True):
                                recolored = image_processor.apply_color_transform(
                                    st.session_state.processed_items[selected_item],
                                    var['rgb']
                                )
                                st.session_state.processed_items[selected_item] = recolored
                                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # ─── RECOMMENDATIONS ───────────────────────────────
        if outfit_colors:
            st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="panel">
              <div class="panel-head">
                <span class="panel-title">06 · Recommendations</span>
                <span class="panel-num">✦</span>
              </div>
            """, unsafe_allow_html=True)

            all_suggestions = []
            for item_key, color in outfit_colors.items():
                suggestions = color_utils.suggest_matching_colors(color, item_key)
                all_suggestions.extend(suggestions[:1])

            rec_cols = st.columns(3, gap="medium")
            for idx, col in enumerate(rec_cols):
                if idx < len(all_suggestions):
                    sug = all_suggestions[idx]
                    sug_hex = '#{:02x}{:02x}{:02x}'.format(*sug['color'])
                    with col:
                        reason = sug['reason']
                        if len(reason) > 60:
                            reason = reason[:60] + "…"
                        st.markdown(f"""
                        <div class="sug-card">
                          <div class="sug-color" style="background:{sug_hex};"></div>
                          <div>
                            <p class="sug-name">{sug['name']}</p>
                            <p class="sug-reason">{reason}</p>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem 0 1.5rem;">
          <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:32px; height:32px; border-radius:9px; background:var(--grad);
                        display:flex; align-items:center; justify-content:center;
                        font-weight:700; color:white; font-family:'Space Grotesk';">W</div>
            <div>
              <div style="font-family:'Space Grotesk'; font-weight:700; font-size:1.1rem; color:var(--text);">WearBlend</div>
              <div style="font-size:0.7rem; color:var(--dim); letter-spacing:0.1em; text-transform:uppercase;">Virtual Try-On</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.processed_items:
            st.markdown(f"""
            <div class="panel" style="padding: 1rem;">
              <div class="panel-title" style="margin-bottom: 0.75rem;">Session</div>
              <div style="display:flex; justify-content:space-between; padding:6px 0; font-size:0.85rem;">
                <span style="color:var(--mute);">Items</span>
                <span style="color:var(--text); font-weight:600;">{len(st.session_state.processed_items)}</span>
              </div>
              <div style="display:flex; justify-content:space-between; padding:6px 0; font-size:0.85rem;">
                <span style="color:var(--mute);">Gender</span>
                <span style="color:var(--text); font-weight:600;">{st.session_state.gender.title()}</span>
              </div>
              <div style="display:flex; justify-content:space-between; padding:6px 0; font-size:0.85rem;">
                <span style="color:var(--mute);">Skin</span>
                <span style="color:var(--text); font-weight:600;">{st.session_state.skin_tone.title()}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
        st.markdown("""
        <ol style="padding-left: 1.1rem; margin: 0; color: var(--mute); font-size: 0.85rem; line-height: 1.7;">
          <li>Pick mannequin gender + skin tone</li>
          <li>Upload your clothing photos</li>
          <li>Backgrounds removed automatically</li>
          <li>Outfit rendered on the mannequin</li>
          <li>Score, recolor, and download</li>
        </ol>
        """, unsafe_allow_html=True)

        st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Tips</div>', unsafe_allow_html=True)
        st.markdown("""
        <ul style="padding-left: 1.1rem; margin: 0; color: var(--mute); font-size: 0.8rem; line-height: 1.7;">
          <li>Use clear, well-lit photos</li>
          <li>Plain backgrounds work best</li>
          <li>Front-facing views preferred</li>
        </ul>
        """, unsafe_allow_html=True)

        st.markdown('<div class="div-line"></div>', unsafe_allow_html=True)
        if st.button("Clear all items", use_container_width=True):
            for key in ['clothing_items', 'processed_items', 'dominant_colors']:
                st.session_state[key] = {}
            st.rerun()


def main():
    """Main application entry point"""
    load_custom_css()
    initialize_session_state()
    render_sidebar()
    render_main_page()


if __name__ == "__main__":
    main()
