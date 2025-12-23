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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Color Palette
COLORS = {
    'primary': '#2d3436',
    'secondary': '#636e72',
    'accent': '#74b9ff',
    'background': '#fafafa',
    'surface': '#ffffff',
    'text_primary': '#2d3436',
    'text_secondary': '#636e72',
    'border': '#dfe6e9',
    'success': '#00b894',
    'muted': '#b2bec3',
}


def load_custom_css():
    """Load professional CSS styles"""
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: {COLORS['background']};
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display: none;}}

    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2.5rem 2rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
    }}

    .main-header h1 {{
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}

    .main-header p {{
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }}

    .card {{
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .card-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 0.5rem;
    }}

    .stButton > button {{
        background: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background: {COLORS['secondary']};
        transform: translateY(-1px);
    }}

    .section-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS['primary']};
        display: inline-block;
    }}

    .info-text {{
        color: {COLORS['text_secondary']};
        font-size: 0.85rem;
        line-height: 1.5;
    }}

    .divider {{
        height: 1px;
        background: {COLORS['border']};
        margin: 1.5rem 0;
    }}

    .outfit-preview {{
        background: linear-gradient(180deg, #fafafa 0%, #f0f0f0 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid {COLORS['border']};
        min-height: 400px;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .score-display {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        color: white;
    }}

    .score-value {{
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
    }}

    .score-label {{
        font-size: 0.85rem;
        opacity: 0.85;
        margin-top: 0.25rem;
    }}

    .color-swatch {{
        width: 40px;
        height: 40px;
        border-radius: 8px;
        border: 2px solid {COLORS['border']};
        cursor: pointer;
        transition: all 0.2s ease;
    }}

    .color-swatch:hover {{
        transform: scale(1.1);
        border-color: {COLORS['primary']};
    }}

    .suggestion-item {{
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem;
        background: {COLORS['background']};
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid {COLORS['accent']};
    }}

    .rating-bar {{
        height: 6px;
        background: {COLORS['border']};
        border-radius: 3px;
        overflow: hidden;
        margin: 0.4rem 0;
    }}

    .rating-fill {{
        height: 100%;
        background: linear-gradient(90deg, {COLORS['primary']} 0%, {COLORS['accent']} 100%);
        border-radius: 3px;
    }}

    .upload-zone {{
        border: 2px dashed {COLORS['border']};
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }}

    .upload-zone:hover {{
        border-color: {COLORS['accent']};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['surface']};
        border-radius: 6px;
        border: 1px solid {COLORS['border']};
        padding: 0.5rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']};
        color: white;
        border-color: {COLORS['primary']};
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


def render_main_page():
    """Render main application page"""
    st.markdown("""
    <div class="main-header">
        <h1>WearBlend</h1>
        <p>Virtual Try-On - See how clothes look on a realistic mannequin</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize components
    image_processor = ImageProcessor()
    style_engine = StyleEngine()
    color_utils = ColorUtils()
    mannequin = RealisticMannequin(gender=st.session_state.gender, skin_tone=st.session_state.skin_tone)

    # Main layout - two columns
    col_upload, col_preview = st.columns([1, 1.2])

    with col_upload:
        # Mannequin Settings Section
        st.markdown('<p class="section-title">Mannequin Settings</p>', unsafe_allow_html=True)

        # Gender selection
        gender_col1, gender_col2 = st.columns(2)
        with gender_col1:
            if st.button("Male", use_container_width=True,
                        type="primary" if st.session_state.gender == 'male' else "secondary"):
                st.session_state.gender = 'male'
                st.rerun()
        with gender_col2:
            if st.button("Female", use_container_width=True,
                        type="primary" if st.session_state.gender == 'female' else "secondary"):
                st.session_state.gender = 'female'
                st.rerun()

        # Skin tone selection
        st.markdown("**Skin Tone**")
        skin_tones = {
            'light': '#f0dfcf',
            'medium': '#ddc3ac',
            'tan': '#c39e80',
            'dark': '#8c644b',
            'deep': '#5a3c2d'
        }

        tone_cols = st.columns(5)
        for col, (tone, color) in zip(tone_cols, skin_tones.items()):
            with col:
                selected = st.session_state.skin_tone == tone
                border = f"3px solid {COLORS['primary']}" if selected else "3px solid transparent"
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="width: 36px; height: 36px; background: {color};
                                border-radius: 50%; margin: 0 auto; border: {border};"></div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(tone.title(), key=f"tone_{tone}", use_container_width=True):
                    st.session_state.skin_tone = tone
                    st.rerun()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown('<p class="section-title">Upload Clothing Items</p>', unsafe_allow_html=True)

        # Clothing categories
        clothing_config = [
            ('shirt', 'Shirt / Top', 'Main upper garment'),
            ('pants', 'Pants / Bottom', 'Lower body garment'),
            ('jacket', 'Jacket / Outerwear', 'Optional layer'),
            ('shoes', 'Shoes / Footwear', 'Complete the look'),
        ]

        # Additional accessories in expandable section
        accessory_config = [
            ('tie', 'Tie / Neckwear', 'Formal accent'),
            ('belt', 'Belt', 'Waist accessory'),
        ]

        # Main clothing items
        for item_key, item_label, item_desc in clothing_config:
            with st.container():
                st.markdown(f"**{item_label}**")
                st.caption(item_desc)

                uploaded_file = st.file_uploader(
                    f"Upload {item_label}",
                    type=['png', 'jpg', 'jpeg', 'webp'],
                    key=f"upload_{item_key}",
                    label_visibility="collapsed"
                )

                if uploaded_file:
                    image = Image.open(uploaded_file)
                    st.session_state.clothing_items[item_key] = image

                    # Show thumbnail
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(image, width=80)
                    with col2:
                        # Process image
                        with st.spinner("Processing..."):
                            processed = image_processor.remove_background(image)
                            st.session_state.processed_items[item_key] = processed
                            colors = image_processor.extract_dominant_colors(image, 3)
                            st.session_state.dominant_colors[item_key] = colors
                        st.success("Ready")
                        if st.button("Remove", key=f"remove_{item_key}"):
                            del st.session_state.clothing_items[item_key]
                            if item_key in st.session_state.processed_items:
                                del st.session_state.processed_items[item_key]
                            if item_key in st.session_state.dominant_colors:
                                del st.session_state.dominant_colors[item_key]
                            st.rerun()

                elif item_key in st.session_state.clothing_items:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(st.session_state.clothing_items[item_key], width=80)
                    with col2:
                        st.success("Uploaded")
                        if st.button("Remove", key=f"remove_{item_key}"):
                            del st.session_state.clothing_items[item_key]
                            if item_key in st.session_state.processed_items:
                                del st.session_state.processed_items[item_key]
                            if item_key in st.session_state.dominant_colors:
                                del st.session_state.dominant_colors[item_key]
                            st.rerun()

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Accessories section
        with st.expander("Accessories (Optional)"):
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
                    with st.spinner("Processing..."):
                        processed = image_processor.remove_background(image)
                        st.session_state.processed_items[item_key] = processed
                        colors = image_processor.extract_dominant_colors(image, 3)
                        st.session_state.dominant_colors[item_key] = colors
                    st.success(f"{item_label} added")

    with col_preview:
        st.markdown('<p class="section-title">Mannequin Preview</p>', unsafe_allow_html=True)

        # Update mannequin with current settings
        mannequin = RealisticMannequin(
            gender=st.session_state.gender,
            skin_tone=st.session_state.skin_tone
        )

        # Generate preview
        if st.session_state.processed_items:
            # Render outfit on mannequin
            outfit_image = mannequin.render_outfit(st.session_state.processed_items)

            # Display
            st.image(outfit_image, use_container_width=True)

            # Download button
            img_bytes = mannequin.get_image_bytes(outfit_image)
            st.download_button(
                label="Download Outfit Image",
                data=img_bytes,
                file_name="wearblend_outfit.png",
                mime="image/png",
                use_container_width=True
            )
        else:
            # Show empty mannequin
            empty_mannequin = mannequin.render_outfit({})
            st.image(empty_mannequin, use_container_width=True)
            st.caption("Upload clothing items to dress the mannequin")

    # Style Analysis Section
    if st.session_state.processed_items:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        analysis_col1, analysis_col2 = st.columns([1, 1])

        # Get dominant colors for analysis
        outfit_colors = {}
        for item_key, colors in st.session_state.dominant_colors.items():
            if colors:
                outfit_colors[item_key] = colors[0]

        with analysis_col1:
            st.markdown('<p class="section-title">Style Analysis</p>', unsafe_allow_html=True)

            if outfit_colors:
                analysis = style_engine.analyze_outfit(outfit_colors)
                rating = style_engine.rate_outfit(outfit_colors)

                # Score display
                st.markdown(f"""
                <div class="score-display">
                    <div class="score-value">{rating['overall']}</div>
                    <div class="score-label">Overall Score</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Category scores
                for category, score in rating['categories'].items():
                    label = category.replace('_', ' ').title()
                    st.markdown(f"""
                    <div style="margin: 0.5rem 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                            <span>{label}</span>
                            <span style="font-weight: 600;">{score}%</span>
                        </div>
                        <div class="rating-bar">
                            <div class="rating-fill" style="width: {score}%;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Strengths
                if analysis['strengths']:
                    st.markdown("**Strengths**")
                    for strength in analysis['strengths'][:2]:
                        st.markdown(f"""
                        <div class="suggestion-item">
                            <p style="margin: 0; font-size: 0.9rem;">{strength}</p>
                        </div>
                        """, unsafe_allow_html=True)

        with analysis_col2:
            st.markdown('<p class="section-title">Color Variations</p>', unsafe_allow_html=True)

            if st.session_state.processed_items:
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

                        # Display color swatches
                        swatch_cols = st.columns(len(variations))
                        for idx, (col, var) in enumerate(zip(swatch_cols, variations)):
                            with col:
                                color_hex = '#{:02x}{:02x}{:02x}'.format(*var['rgb'])
                                st.markdown(f"""
                                <div style="text-align: center;">
                                    <div class="color-swatch" style="background: {color_hex}; margin: 0 auto;"></div>
                                    <p style="font-size: 0.7rem; color: #636e72; margin-top: 0.25rem;">
                                        {var['name'][:10]}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)

                                if st.button("Apply", key=f"var_{idx}", use_container_width=True):
                                    # Apply color variation
                                    recolored = image_processor.apply_color_transform(
                                        st.session_state.processed_items[selected_item],
                                        var['rgb']
                                    )
                                    st.session_state.processed_items[selected_item] = recolored
                                    st.rerun()

        # Recommendations
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Style Recommendations</p>', unsafe_allow_html=True)

        if outfit_colors:
            rec_cols = st.columns(3)

            all_suggestions = []
            for item_key, color in outfit_colors.items():
                suggestions = color_utils.suggest_matching_colors(color, item_key)
                all_suggestions.extend(suggestions[:1])

            for idx, col in enumerate(rec_cols):
                if idx < len(all_suggestions):
                    sug = all_suggestions[idx]
                    sug_hex = '#{:02x}{:02x}{:02x}'.format(*sug['color'])
                    with col:
                        st.markdown(f"""
                        <div class="card">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div style="width: 35px; height: 35px; background: {sug_hex};
                                            border-radius: 6px;"></div>
                                <div>
                                    <p style="margin: 0; font-weight: 600; font-size: 0.9rem;">{sug['name']}</p>
                                    <p style="margin: 0; font-size: 0.75rem; color: #636e72;">
                                        {sug['reason'][:50]}...
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar content"""
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 1rem 0;">
            <h2 style="color: {COLORS['primary']}; font-weight: 700; margin: 0;">WearBlend</h2>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Virtual Try-On</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Stats
        if st.session_state.processed_items:
            st.markdown(f"""
            <div class="card">
                <p style="margin: 0.2rem 0;"><strong>Items:</strong> {len(st.session_state.processed_items)}</p>
                <p style="margin: 0.2rem 0;"><strong>Gender:</strong> {st.session_state.gender.title()}</p>
                <p style="margin: 0.2rem 0;"><strong>Skin:</strong> {st.session_state.skin_tone.title()}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("**How It Works**")
        st.markdown(f"""
        <ol style="color: {COLORS['text_secondary']}; font-size: 0.85rem; padding-left: 1.25rem;">
            <li style="margin: 0.4rem 0;">Select mannequin gender and skin tone</li>
            <li style="margin: 0.4rem 0;">Upload clothing images</li>
            <li style="margin: 0.4rem 0;">Background is removed automatically</li>
            <li style="margin: 0.4rem 0;">Clothes appear on the mannequin</li>
            <li style="margin: 0.4rem 0;">Download your outfit image</li>
        </ol>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown("**Tips**")
        st.markdown(f"""
        <ul style="color: {COLORS['text_secondary']}; font-size: 0.8rem; padding-left: 1.25rem;">
            <li style="margin: 0.3rem 0;">Use clear, well-lit photos</li>
            <li style="margin: 0.3rem 0;">Plain backgrounds work best</li>
            <li style="margin: 0.3rem 0;">Front-facing views preferred</li>
        </ul>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        if st.button("Clear All", use_container_width=True):
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
