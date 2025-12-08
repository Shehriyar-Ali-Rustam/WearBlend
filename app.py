"""
WearBlend - Virtual Try-On Application
Professional Streamlit Interface
"""

import streamlit as st
from PIL import Image
import io
from typing import Dict, Optional, Tuple

from utils.image_processor import ImageProcessor
from utils.color_utils import ColorUtils
from utils.style_engine import StyleEngine
from utils.mannequin_renderer import MannequinRenderer

# Page configuration
st.set_page_config(
    page_title="WearBlend | Virtual Try-On",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Professional Color Palette
COLORS = {
    'primary': '#1a1a2e',        # Deep navy
    'secondary': '#16213e',      # Dark blue
    'accent': '#0f3460',         # Medium blue
    'highlight': '#e94560',      # Coral accent (used sparingly)
    'background': '#f8f9fa',     # Light grey
    'surface': '#ffffff',        # White
    'text_primary': '#1a1a2e',   # Dark text
    'text_secondary': '#6c757d', # Grey text
    'border': '#dee2e6',         # Light border
    'success': '#28a745',        # Green
    'warning': '#ffc107',        # Yellow
    'muted': '#adb5bd',          # Muted grey
}


def load_custom_css():
    """Load professional CSS styles"""
    st.markdown(f"""
    <style>
    /* Import Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: {COLORS['background']};
    }}

    /* Hide Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    /* Header Styling */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 3rem 2rem;
        border-radius: 0 0 24px 24px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
    }}

    .main-header h1 {{
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    .main-header p {{
        color: rgba(255,255,255,0.8);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }}

    /* Card Styling */
    .card {{
        background: {COLORS['surface']};
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }}

    .card:hover {{
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        border-color: {COLORS['accent']};
    }}

    .card-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 0.75rem;
    }}

    /* Button Styling */
    .stButton > button {{
        background: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }}

    .stButton > button:hover {{
        background: {COLORS['accent']};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(26,26,46,0.2);
    }}

    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Secondary Button */
    .secondary-btn > button {{
        background: transparent;
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
    }}

    .secondary-btn > button:hover {{
        background: {COLORS['background']};
        border-color: {COLORS['text_primary']};
    }}

    /* Selection Cards */
    .selection-card {{
        background: {COLORS['surface']};
        border: 2px solid {COLORS['border']};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .selection-card:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 16px rgba(26,26,46,0.1);
    }}

    .selection-card.selected {{
        border-color: {COLORS['primary']};
        background: linear-gradient(135deg, {COLORS['primary']}08 0%, {COLORS['accent']}08 100%);
    }}

    .selection-card h3 {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin: 0.5rem 0;
    }}

    .selection-card p {{
        color: {COLORS['text_secondary']};
        font-size: 0.9rem;
        margin: 0;
    }}

    /* Progress Steps */
    .steps-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2rem 0;
        gap: 0;
    }}

    .step {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    .step-number {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
        background: {COLORS['border']};
        color: {COLORS['text_secondary']};
    }}

    .step-number.active {{
        background: {COLORS['primary']};
        color: white;
    }}

    .step-number.completed {{
        background: {COLORS['success']};
        color: white;
    }}

    .step-label {{
        font-size: 0.85rem;
        color: {COLORS['text_secondary']};
        font-weight: 500;
    }}

    .step-connector {{
        width: 60px;
        height: 2px;
        background: {COLORS['border']};
        margin: 0 0.5rem;
    }}

    .step-connector.completed {{
        background: {COLORS['success']};
    }}

    /* Upload Area */
    .upload-area {{
        border: 2px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: {COLORS['background']};
        transition: all 0.2s ease;
    }}

    .upload-area:hover {{
        border-color: {COLORS['accent']};
        background: {COLORS['surface']};
    }}

    /* Color Swatches */
    .color-swatch {{
        width: 48px;
        height: 48px;
        border-radius: 8px;
        border: 2px solid {COLORS['border']};
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .color-swatch:hover {{
        transform: scale(1.1);
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    /* Score Display */
    .score-card {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        color: white;
    }}

    .score-value {{
        font-size: 3rem;
        font-weight: 700;
        line-height: 1;
    }}

    .score-label {{
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }}

    /* Suggestion Item */
    .suggestion-item {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        background: {COLORS['background']};
        border-radius: 10px;
        margin: 0.75rem 0;
        border-left: 3px solid {COLORS['accent']};
    }}

    .suggestion-item p {{
        margin: 0;
        color: {COLORS['text_primary']};
        font-size: 0.95rem;
    }}

    .suggestion-item small {{
        color: {COLORS['text_secondary']};
        font-size: 0.85rem;
    }}

    /* Mannequin Display */
    .mannequin-container {{
        background: linear-gradient(180deg, {COLORS['background']} 0%, #e9ecef 100%);
        border-radius: 20px;
        padding: 2rem;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 500px;
        border: 1px solid {COLORS['border']};
    }}

    /* Skin Tone Selector */
    .skin-tone-btn {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 3px solid transparent;
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .skin-tone-btn:hover {{
        transform: scale(1.1);
    }}

    .skin-tone-btn.selected {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(26,26,46,0.2);
    }}

    /* File Uploader Customization */
    .stFileUploader > div > div {{
        border: 2px dashed {COLORS['border']};
        border-radius: 12px;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['surface']};
        border-radius: 8px;
        border: 1px solid {COLORS['border']};
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']};
        color: white;
        border-color: {COLORS['primary']};
    }}

    /* Progress Bar */
    .stProgress > div > div > div {{
        background: {COLORS['primary']};
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}

    /* Divider */
    .divider {{
        height: 1px;
        background: {COLORS['border']};
        margin: 2rem 0;
    }}

    /* Section Title */
    .section-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['primary']};
        display: inline-block;
    }}

    /* Info Text */
    .info-text {{
        color: {COLORS['text_secondary']};
        font-size: 0.9rem;
        line-height: 1.6;
    }}

    /* Rating Display */
    .rating-bar {{
        height: 8px;
        background: {COLORS['border']};
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }}

    .rating-fill {{
        height: 100%;
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        border-radius: 4px;
        transition: width 0.5s ease;
    }}
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'page': 'welcome',
        'gender': None,
        'skin_tone': 'medium',
        'clothing_items': {},
        'processed_items': {},
        'dominant_colors': {},
        'selected_variation': None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_progress_steps(current_step: int):
    """Render progress indicator"""
    steps = ['Select Model', 'Upload Items', 'Preview & Style']

    html = '<div class="steps-container">'
    for i, step in enumerate(steps, 1):
        num_class = 'completed' if i < current_step else ('active' if i == current_step else '')
        html += f'''
        <div class="step">
            <div class="step-number {num_class}">{i}</div>
            <span class="step-label">{step}</span>
        </div>
        '''
        if i < len(steps):
            conn_class = 'completed' if i < current_step else ''
            html += f'<div class="step-connector {conn_class}"></div>'
    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)


def render_welcome_page():
    """Render welcome and model selection page"""
    st.markdown("""
    <div class="main-header">
        <h1>WearBlend</h1>
        <p>Professional Virtual Try-On Experience</p>
    </div>
    """, unsafe_allow_html=True)

    render_progress_steps(1)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Introduction
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Upload Clothing</div>
            <p class="info-text">
                Upload images of shirts, pants, jackets, and accessories.
                Our AI removes backgrounds automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Virtual Preview</div>
            <p class="info-text">
                See your outfit on a realistic 3D mannequin.
                Clothing items are fitted with natural draping.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <div class="card-title">Style Analysis</div>
            <p class="info-text">
                Get AI-powered color suggestions and style
                recommendations to perfect your look.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Model Selection
    st.markdown('<p class="section-title">Select Mannequin Model</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        gcol1, gcol2 = st.columns(2)

        with gcol1:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; color: #1a1a2e; margin-bottom: 1rem;">M</div>
                <div class="card-title">Male Model</div>
                <p class="info-text">Standard male proportions</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Male", key="male_btn", use_container_width=True):
                st.session_state.gender = 'male'
                st.session_state.page = 'upload'
                st.rerun()

        with gcol2:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; color: #1a1a2e; margin-bottom: 1rem;">F</div>
                <div class="card-title">Female Model</div>
                <p class="info-text">Standard female proportions</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Select Female", key="female_btn", use_container_width=True):
                st.session_state.gender = 'female'
                st.session_state.page = 'upload'
                st.rerun()

    # Skin Tone Selection
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">Skin Tone (Optional)</p>', unsafe_allow_html=True)

    skin_tones = {
        'light': '#ebe1d6',
        'medium': '#d7c3ab',
        'tan': '#c3a589',
        'dark': '#826046',
        'deep': '#553723'
    }

    cols = st.columns(5)
    for col, (tone, color) in zip(cols, skin_tones.items()):
        with col:
            selected = st.session_state.skin_tone == tone
            border_style = f"border: 3px solid {COLORS['primary']};" if selected else "border: 3px solid transparent;"
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="width: 50px; height: 50px; background: {color};
                            border-radius: 50%; margin: 0 auto; {border_style}
                            cursor: pointer;"></div>
                <p style="font-size: 0.8rem; color: {COLORS['text_secondary']}; margin-top: 0.5rem;">
                    {tone.capitalize()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(tone.capitalize(), key=f"skin_{tone}",
                        use_container_width=True,
                        type="primary" if selected else "secondary"):
                st.session_state.skin_tone = tone
                st.rerun()


def render_upload_page():
    """Render clothing upload page"""
    st.markdown("""
    <div class="main-header">
        <h1>Upload Your Outfit</h1>
        <p>Add clothing items to create your virtual look</p>
    </div>
    """, unsafe_allow_html=True)

    render_progress_steps(2)

    # Navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Back", key="back_btn"):
            st.session_state.page = 'welcome'
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Clothing upload sections
    clothing_config = {
        'Essential Items': [
            ('shirt', 'Shirt / Top', 'Button-down, t-shirt, blouse, etc.'),
            ('pants', 'Pants / Bottom', 'Trousers, jeans, skirt, etc.'),
        ],
        'Outerwear': [
            ('jacket', 'Jacket / Blazer', 'Coat, cardigan, suit jacket'),
        ],
        'Accessories': [
            ('tie', 'Tie / Neckwear', 'Necktie, bow tie, scarf'),
            ('shoes', 'Footwear', 'Dress shoes, sneakers, heels'),
            ('belt', 'Belt', 'Leather or fabric belt'),
        ]
    }

    image_processor = ImageProcessor()

    for section, items in clothing_config.items():
        st.markdown(f'<p class="section-title">{section}</p>', unsafe_allow_html=True)

        cols = st.columns(len(items))

        for col, (item_key, item_label, item_desc) in zip(cols, items):
            with col:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{item_label}</div>
                    <p class="info-text" style="margin-bottom: 1rem;">{item_desc}</p>
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

                    # Show preview
                    st.image(image, caption=f"Uploaded: {item_label}", use_container_width=True)

                    # Process image
                    with st.spinner("Processing..."):
                        processed = image_processor.prepare_clothing_for_overlay(
                            image, item_key, MannequinRenderer.MANNEQUIN_SIZE
                        )
                        st.session_state.processed_items[item_key] = processed

                        colors = image_processor.extract_dominant_colors(image, 3)
                        st.session_state.dominant_colors[item_key] = colors

                    st.success("Processed successfully")

                elif item_key in st.session_state.clothing_items:
                    st.image(
                        st.session_state.clothing_items[item_key],
                        caption=f"Current: {item_label}",
                        use_container_width=True
                    )
                    if st.button(f"Remove", key=f"remove_{item_key}"):
                        del st.session_state.clothing_items[item_key]
                        if item_key in st.session_state.processed_items:
                            del st.session_state.processed_items[item_key]
                        if item_key in st.session_state.dominant_colors:
                            del st.session_state.dominant_colors[item_key]
                        st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Continue button
    if st.session_state.processed_items:
        st.markdown(f"""
        <div class="card" style="text-align: center; background: {COLORS['background']};">
            <p style="color: {COLORS['success']}; font-weight: 600;">
                {len(st.session_state.processed_items)} item(s) ready for preview
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Continue to Preview", type="primary", use_container_width=True):
            st.session_state.page = 'preview'
            st.rerun()
    else:
        st.info("Upload at least one clothing item to continue")


def render_preview_page():
    """Render outfit preview and analysis page"""
    st.markdown("""
    <div class="main-header">
        <h1>Your Virtual Outfit</h1>
        <p>Preview, analyze, and explore style variations</p>
    </div>
    """, unsafe_allow_html=True)

    render_progress_steps(3)

    # Navigation
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Back", key="back_preview"):
            st.session_state.page = 'upload'
            st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Initialize components
    renderer = MannequinRenderer(
        gender=st.session_state.gender,
        skin_tone=st.session_state.skin_tone
    )
    style_engine = StyleEngine()
    image_processor = ImageProcessor()
    color_utils = ColorUtils()

    # Main layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<p class="section-title">Outfit Preview</p>', unsafe_allow_html=True)

        if st.session_state.processed_items:
            # Render mannequin
            outfit_render = renderer.render_outfit(st.session_state.processed_items)

            st.markdown('<div class="mannequin-container">', unsafe_allow_html=True)
            st.image(outfit_render, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Download button
            img_bytes = renderer.get_image_bytes(outfit_render)
            st.download_button(
                label="Download Image",
                data=img_bytes,
                file_name="wearblend_outfit.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            st.warning("No clothing items to display")

    with col2:
        st.markdown('<p class="section-title">Style Analysis</p>', unsafe_allow_html=True)

        # Get dominant colors for analysis
        outfit_colors = {}
        for item_key, colors in st.session_state.dominant_colors.items():
            if colors:
                outfit_colors[item_key] = colors[0]

        if outfit_colors:
            analysis = style_engine.analyze_outfit(outfit_colors)
            rating = style_engine.rate_outfit(outfit_colors)

            # Score display
            st.markdown(f"""
            <div class="score-card">
                <div class="score-value">{rating['overall']}</div>
                <div class="score-label">Overall Score</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Category scores
            st.markdown("**Category Breakdown**")
            for category, score in rating['categories'].items():
                label = category.replace('_', ' ').title()
                st.markdown(f"""
                <div style="margin: 0.75rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-size: 0.9rem; color: {COLORS['text_primary']};">{label}</span>
                        <span style="font-size: 0.9rem; font-weight: 600; color: {COLORS['primary']};">{score}%</span>
                    </div>
                    <div class="rating-bar">
                        <div class="rating-fill" style="width: {score}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Style verdict
            st.markdown(f"""
            <div class="card">
                <div class="card-title">Style Category</div>
                <p style="font-size: 1.1rem; font-weight: 600; color: {COLORS['primary']};">
                    {analysis['style_category'].replace('_', ' ').title()}
                </p>
                <p class="info-text">{rating['verdict']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Strengths & Improvements
            if analysis['strengths']:
                st.markdown("**Strengths**")
                for strength in analysis['strengths']:
                    st.markdown(f"""
                    <div class="suggestion-item">
                        <p>{strength}</p>
                    </div>
                    """, unsafe_allow_html=True)

            if analysis['improvements']:
                st.markdown("**Suggestions**")
                for improvement in analysis['improvements']:
                    st.markdown(f"""
                    <div class="suggestion-item">
                        <p>{improvement}</p>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Color Variations Section
    st.markdown('<p class="section-title">Color Variations</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="info-text">Select an item and explore alternative colors</p>',
                unsafe_allow_html=True)

    if st.session_state.processed_items:
        item_options = list(st.session_state.processed_items.keys())
        selected_item = st.selectbox(
            "Select item to recolor:",
            item_options,
            format_func=lambda x: x.replace('_', ' ').title()
        )

        if selected_item and selected_item in st.session_state.dominant_colors:
            original_color = st.session_state.dominant_colors[selected_item][0]
            variations = color_utils.get_color_variations(original_color, 6)

            st.markdown("<br>", unsafe_allow_html=True)

            # Color swatches
            var_cols = st.columns(len(variations))
            for idx, (col, var) in enumerate(zip(var_cols, variations)):
                with col:
                    color_hex = '#{:02x}{:02x}{:02x}'.format(*var['rgb'])
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="color-swatch" style="background: {color_hex};
                                    margin: 0 auto;"></div>
                        <p style="font-size: 0.75rem; color: {COLORS['text_secondary']};
                                  margin-top: 0.5rem;">{var['name'][:12]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Apply", key=f"var_{idx}", use_container_width=True):
                        st.session_state.selected_variation = (selected_item, var['rgb'], var['name'])
                        st.rerun()

            # Show variation preview
            if st.session_state.selected_variation:
                item, new_color, color_name = st.session_state.selected_variation
                if item == selected_item:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"**Preview: {color_name}**")

                    variation_render = renderer.render_with_color_variation(
                        st.session_state.processed_items,
                        selected_item,
                        new_color,
                        image_processor
                    )

                    comp_col1, comp_col2 = st.columns(2)
                    with comp_col1:
                        st.markdown("**Original**")
                        original_render = renderer.render_outfit(st.session_state.processed_items)
                        st.image(original_render, use_container_width=True)
                    with comp_col2:
                        st.markdown(f"**{color_name}**")
                        st.image(variation_render, use_container_width=True)

                    var_bytes = renderer.get_image_bytes(variation_render)
                    st.download_button(
                        label=f"Download {color_name} Version",
                        data=var_bytes,
                        file_name=f"wearblend_{color_name.lower().replace(' ', '_')}.png",
                        mime="image/png"
                    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Style Recommendations
    st.markdown('<p class="section-title">Color Recommendations</p>', unsafe_allow_html=True)

    if outfit_colors:
        tabs = st.tabs(["By Item", "Seasonal Palettes"])

        with tabs[0]:
            for item_key, color in outfit_colors.items():
                color_name = color_utils.get_color_name(color)

                with st.expander(f"{item_key.replace('_', ' ').title()} - {color_name}"):
                    suggestions = color_utils.suggest_matching_colors(color, item_key)

                    for suggestion in suggestions:
                        sug_hex = '#{:02x}{:02x}{:02x}'.format(*suggestion['color'])
                        st.markdown(f"""
                        <div class="suggestion-item">
                            <div class="color-swatch" style="background: {sug_hex};
                                        min-width: 40px; height: 40px;"></div>
                            <div>
                                <p><strong>{suggestion['name']}</strong></p>
                                <small>{suggestion['reason']}</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        with tabs[1]:
            season_cols = st.columns(4)
            seasons = [('Summer', 'summer'), ('Winter', 'winter'),
                      ('Formal', 'formal'), ('Casual', 'casual')]

            for col, (label, season) in zip(season_cols, seasons):
                with col:
                    st.markdown(f"**{label}**")
                    palette = color_utils.get_seasonal_palette(season)

                    for pal_color in palette[:4]:
                        hex_color = '#{:02x}{:02x}{:02x}'.format(*pal_color['rgb'])
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin: 0.5rem 0;">
                            <div style="width: 24px; height: 24px; background: {hex_color};
                                        border-radius: 4px;"></div>
                            <span style="font-size: 0.8rem;">{pal_color['name']}</span>
                        </div>
                        """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem 0;">
            <h2 style="color: {COLORS['primary']}; font-weight: 700; margin: 0;">WearBlend</h2>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.85rem;">Virtual Try-On</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.session_state.gender:
            st.markdown(f"""
            <div class="card">
                <p style="margin: 0.25rem 0;"><strong>Model:</strong> {st.session_state.gender.title()}</p>
                <p style="margin: 0.25rem 0;"><strong>Skin Tone:</strong> {st.session_state.skin_tone.title()}</p>
                <p style="margin: 0.25rem 0;"><strong>Items:</strong> {len(st.session_state.processed_items)}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("**How It Works**")
        st.markdown(f"""
        <ol style="color: {COLORS['text_secondary']}; font-size: 0.9rem; padding-left: 1.25rem;">
            <li style="margin: 0.5rem 0;">Select mannequin model</li>
            <li style="margin: 0.5rem 0;">Upload clothing images</li>
            <li style="margin: 0.5rem 0;">View virtual preview</li>
            <li style="margin: 0.5rem 0;">Explore color options</li>
            <li style="margin: 0.5rem 0;">Get style recommendations</li>
        </ol>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("**Tips**")
        st.markdown(f"""
        <ul style="color: {COLORS['text_secondary']}; font-size: 0.85rem; padding-left: 1.25rem;">
            <li style="margin: 0.4rem 0;">Use clear, well-lit photos</li>
            <li style="margin: 0.4rem 0;">Plain backgrounds work best</li>
            <li style="margin: 0.4rem 0;">Front-facing views preferred</li>
            <li style="margin: 0.4rem 0;">Higher resolution = better results</li>
        </ul>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.button("Start Over", use_container_width=True):
            for key in ['clothing_items', 'processed_items', 'dominant_colors', 'selected_variation']:
                st.session_state[key] = {} if 'items' in key or 'colors' in key else None
            st.session_state.page = 'welcome'
            st.session_state.gender = None
            st.rerun()


def main():
    """Main application entry point"""
    load_custom_css()
    initialize_session_state()
    render_sidebar()

    # Route to appropriate page
    if st.session_state.page == 'welcome':
        render_welcome_page()
    elif st.session_state.page == 'upload':
        render_upload_page()
    elif st.session_state.page == 'preview':
        render_preview_page()


if __name__ == "__main__":
    main()
