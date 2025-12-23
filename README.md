# WearBlend - Virtual Try-On Application

A modern, AI-powered virtual try-on application that allows users to upload clothing images, visualize outfits, and generate AI-powered fashion images using OpenAI DALL-E or Google Gemini.

## Features

### Two Modes of Operation

#### Classic Mode (Flat-Lay Composer)
- **Outfit Composition**: Professional flat-lay style outfit arrangements
- **Multiple Clothing Support**: Upload shirts, pants, ties, jackets, shoes, and accessories
- **Background Removal**: AI-powered automatic background removal from clothing images
- **Color Analysis**: Automatic extraction of dominant colors from clothing
- **Style Recommendations**: AI suggestions for color combinations and outfit improvements

#### AI Mode (Generate with AI)
- **AI-Powered Image Generation**: Generate realistic fashion photos using AI
- **Dual Provider Support**: Choose between OpenAI (DALL-E 3) or Google Gemini
- **Custom Prompts**: Describe how you want to see your outfit worn
- **Vision Analysis**: AI analyzes your clothing items for accurate generation

### Core Features
- **Modern UI**: Clean, responsive design with mode selector
- **Download Options**: Export your virtual outfit images
- **Secure API Storage**: API keys stored in backend (not visible to users)

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- API keys for AI mode (OpenAI and/or Google Gemini)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/Shehriyar-Ali-Rustam/WearBlend.git
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

4. **Configure API Keys** (for AI Mode)
```bash
# Create .env file in project root
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Open in browser**
Navigate to `http://localhost:8501`

## Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API Key (for DALL-E 3 image generation)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (alternative provider)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note**: You need at least one API key for AI Mode to work. Both are optional but recommended for flexibility.

## Project Structure

```
WearBlend/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed to git)
├── .env.example           # Example environment file
├── README.md              # This file
│
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── image_processor.py  # Background removal & image processing
│   ├── color_utils.py      # Color analysis & manipulation
│   ├── style_engine.py     # AI style recommendations
│   ├── outfit_composer.py  # Flat-lay outfit composition
│   ├── mannequin_renderer.py  # Mannequin rendering
│   └── ai_tryon.py         # AI-powered try-on (OpenAI/Gemini)
│
└── assets/                 # Static assets (optional)
```

## Usage Guide

### Classic Mode
1. Click "Classic Mode" at the top
2. Upload clothing items (shirt, pants, shoes, etc.)
3. Background is automatically removed
4. View the flat-lay outfit composition
5. Explore color variations and style recommendations
6. Download your outfit image

### AI Mode (Generate with AI)
1. Click "Generate with AI" at the top
2. Upload one or more clothing images
3. Write a custom prompt describing how you want to see the outfit:
   - "Make a male model wear this outfit in a studio setting"
   - "Show a female model wearing these clothes casually"
   - "Create a fashion photoshoot with this outfit"
4. Select AI provider (OpenAI or Gemini)
5. Click "Generate with AI"
6. Wait 30-60 seconds for the AI to generate your image
7. Download the generated image

## Technical Details

### AI Providers

#### OpenAI (DALL-E 3)
- Uses GPT-4 Vision to analyze clothing items
- Generates images using DALL-E 3 (1024x1792, HD quality)
- Best for photorealistic fashion images
- Requires paid OpenAI API credits

#### Google Gemini
- Uses Gemini 2.0 Flash for vision and generation
- Native image generation capability
- Free tier available with rate limits

### Background Removal
Uses `rembg` library with U2-Net model for accurate clothing segmentation

### Color Analysis
- K-means clustering for dominant color extraction
- HSV color space analysis
- Color harmony recommendations

## API Reference

### AITryOn
```python
from utils.ai_tryon import AITryOn

# Initialize with provider
ai = AITryOn(provider='openai')  # or 'gemini'

# Generate outfit image
image, status = ai.generate_with_custom_prompt(
    clothing_items={'shirt': shirt_image, 'pants': pants_image},
    user_prompt="A male model wearing this outfit in a studio"
)

# Analyze outfit
analysis, status = ai.analyze_outfit(clothing_items)

# Check available providers
providers = AITryOn.get_available_providers()  # ['openai', 'gemini']
```

### OutfitComposer
```python
from utils.outfit_composer import OutfitComposer

composer = OutfitComposer(style='classic')  # or 'casual', 'formal'
outfit_image = composer.compose_outfit(processed_items, background='neutral')
```

## Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit dashboard:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
4. Deploy with `app.py` as main file

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Troubleshooting

### Common Issues

**"OpenAI billing limit reached"**
- Add credits to your OpenAI account at https://platform.openai.com/account/billing

**"Gemini rate limit exceeded"**
- Wait a few minutes and try again
- Consider upgrading to a paid tier

**"No API keys configured"**
- Create a `.env` file with your API keys
- Ensure the file is in the project root directory

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
- [OpenAI](https://openai.com/) - DALL-E 3 & GPT-4 Vision
- [Google Gemini](https://ai.google.dev/) - Gemini AI
- [rembg](https://github.com/danielgatis/rembg) - Background removal
- [Pillow](https://pillow.readthedocs.io/) - Image processing
