# WearBlend - Virtual Try-On Application

A modern, AI-powered virtual try-on application that allows users to upload clothing images, visualize outfits on virtual mannequins, and receive intelligent color and style recommendations.

## Features

### Core Functionality
- **Virtual Mannequin Try-On**: See your uploaded clothes on male or female mannequin models
- **Multiple Clothing Support**: Upload shirts, pants, ties, jackets, shoes, and accessories
- **Background Removal**: AI-powered automatic background removal from clothing images
- **Realistic Overlay**: Clothing items are positioned and layered realistically

### AI-Powered Features
- **Color Analysis**: Automatic extraction of dominant colors from clothing
- **Color Variations**: Generate and preview your outfit in different color schemes
- **Style Recommendations**: AI suggestions for color combinations and outfit improvements
- **Outfit Scoring**: Get a comprehensive rating of your outfit's color harmony and style

### User Experience
- **Modern UI**: Clean, responsive design with gradient backgrounds
- **Step-by-Step Flow**: Guided onboarding from gender selection to final preview
- **Camera Support**: Take photos directly or upload from gallery
- **Download Options**: Export your virtual outfit images

## Installation

### Prerequisites
- Python 3.9+
- pip package manager

### Quick Start

1. **Clone the repository**
```bash
cd WearBlend
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open in browser**
Navigate to `http://localhost:8501`

## Project Structure

```
WearBlend/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── image_processor.py  # Background removal & image processing
│   ├── color_utils.py      # Color analysis & manipulation
│   ├── style_engine.py     # AI style recommendations
│   └── mannequin_renderer.py  # Mannequin rendering
│
├── assets/                 # Static assets
│   ├── mannequins/        # Mannequin base images (optional)
│   ├── icons/             # UI icons
│   └── samples/           # Sample clothing images
│
└── tests/                  # Test files
```

## Usage Guide

### Step 1: Welcome Screen
- Choose your mannequin type (Male or Female)
- Optionally select a skin tone

### Step 2: Upload Clothing
Upload images of your clothing items:
- **Essential**: Shirt/Top, Pants/Bottom
- **Optional**: Tie, Jacket, Shoes
- **Accessories**: Belt, Watch, Scarf

Tips for best results:
- Use clear, well-lit photos
- Front-facing views work best
- Plain backgrounds are ideal

### Step 3: Preview & Suggestions
- View your outfit on the virtual mannequin
- See your outfit analysis and score
- Explore color variations
- Get AI-powered style recommendations
- Download your virtual outfit image

## Technical Details

### AI Models Used

1. **Background Removal**: Uses `rembg` library with U2-Net model for accurate clothing segmentation

2. **Color Analysis**: Custom algorithm combining:
   - K-means clustering for dominant color extraction
   - HSV color space analysis
   - WCAG contrast ratio calculations

3. **Style Engine**: Rule-based AI with:
   - Color harmony analysis (complementary, analogous, triadic)
   - Style category classification (formal, casual, business casual)
   - Seasonal color palettes
   - Context-aware suggestions

### Color Transformation
- Luminance-preserving color transfer
- Maintains shadows and textures
- Supports realistic fabric appearance

## Configuration

### Environment Variables (Optional)
```env
# Create .env file for custom settings
STREAMLIT_THEME_BASE=light
STREAMLIT_SERVER_PORT=8501
```

### Customization
- Modify `MannequinRenderer.SKIN_TONES` for additional skin tones
- Adjust `ColorUtils.STANDARD_COLORS` for custom color palettes
- Update `StyleEngine.STYLE_RULES` for different style recommendations

## API Reference

### ImageProcessor
```python
processor = ImageProcessor()
processed_image = processor.remove_background(image)
colors = processor.extract_dominant_colors(image, num_colors=5)
recolored = processor.apply_color_transform(image, target_color)
```

### ColorUtils
```python
color_name = ColorUtils.get_color_name((255, 0, 0))  # "Red"
variations = ColorUtils.get_color_variations(rgb_color)
suggestions = ColorUtils.suggest_matching_colors(color, 'shirt')
```

### StyleEngine
```python
engine = StyleEngine()
analysis = engine.analyze_outfit(clothing_items)
rating = engine.rate_outfit(clothing_items)
recommendations = engine.get_outfit_recommendations(primary_color, 'formal')
```

### MannequinRenderer
```python
renderer = MannequinRenderer(gender='male', skin_tone='medium')
mannequin = renderer.create_base_mannequin()
outfit = renderer.render_outfit(processed_items)
```

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy with `app.py` as main file

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Streamlit](https://streamlit.io/) - Web framework
- [rembg](https://github.com/danielgatis/rembg) - Background removal
- [Pillow](https://pillow.readthedocs.io/) - Image processing
