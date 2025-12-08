"""
Unit tests for WearBlend utility modules
"""

import pytest
from PIL import Image
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.color_utils import ColorUtils
from utils.style_engine import StyleEngine
from utils.image_processor import ImageProcessor
from utils.mannequin_renderer import MannequinRenderer


class TestColorUtils:
    """Tests for ColorUtils class"""

    def test_rgb_to_hsv_conversion(self):
        """Test RGB to HSV conversion"""
        # Red
        hsv = ColorUtils.rgb_to_hsv((255, 0, 0))
        assert hsv[0] == 0.0  # Hue should be 0 for red
        assert hsv[1] == 1.0  # Full saturation
        assert hsv[2] == 1.0  # Full value

    def test_get_color_name(self):
        """Test color naming"""
        # Pure red should be close to red
        name = ColorUtils.get_color_name((255, 0, 0))
        assert 'red' in name.lower()

        # Pure white
        name = ColorUtils.get_color_name((255, 255, 255))
        assert 'white' in name.lower()

    def test_complementary_color(self):
        """Test complementary color calculation"""
        # Red's complement is cyan
        comp = ColorUtils.get_complementary_color((255, 0, 0))
        # Should have high G and B, low R
        assert comp[1] > 200  # Green
        assert comp[2] > 200  # Blue

    def test_is_warm_color(self):
        """Test warm color detection"""
        assert ColorUtils.is_warm_color((255, 0, 0))  # Red is warm
        assert ColorUtils.is_warm_color((255, 165, 0))  # Orange is warm
        assert not ColorUtils.is_warm_color((0, 0, 255))  # Blue is cool

    def test_is_neutral_color(self):
        """Test neutral color detection"""
        assert ColorUtils.is_neutral_color((128, 128, 128))  # Grey
        assert ColorUtils.is_neutral_color((200, 200, 200))  # Light grey
        assert not ColorUtils.is_neutral_color((255, 0, 0))  # Red is not neutral

    def test_get_color_variations(self):
        """Test color variation generation"""
        variations = ColorUtils.get_color_variations((100, 50, 50), 6)
        assert len(variations) == 6
        assert variations[0]['type'] == 'original'

    def test_seasonal_palette(self):
        """Test seasonal palette generation"""
        summer = ColorUtils.get_seasonal_palette('summer')
        winter = ColorUtils.get_seasonal_palette('winter')

        assert len(summer) > 0
        assert len(winter) > 0
        # Summer should have lighter colors
        # Winter should have darker colors


class TestStyleEngine:
    """Tests for StyleEngine class"""

    def test_analyze_outfit(self):
        """Test outfit analysis"""
        engine = StyleEngine()
        outfit = {
            'shirt': (255, 255, 255),  # White
            'pants': (0, 0, 128)  # Navy
        }
        analysis = engine.analyze_outfit(outfit)

        assert 'overall_score' in analysis
        assert 'color_harmony' in analysis
        assert 'style_category' in analysis
        assert analysis['overall_score'] >= 0
        assert analysis['overall_score'] <= 100

    def test_rate_outfit(self):
        """Test outfit rating"""
        engine = StyleEngine()
        outfit = {
            'shirt': (255, 255, 255),
            'pants': (50, 50, 50)
        }
        rating = engine.rate_outfit(outfit)

        assert 'overall' in rating
        assert 'categories' in rating
        assert 'verdict' in rating
        assert 0 <= rating['overall'] <= 100

    def test_outfit_recommendations(self):
        """Test getting outfit recommendations"""
        engine = StyleEngine()
        recommendations = engine.get_outfit_recommendations(
            (0, 0, 128),  # Navy blue
            'formal'
        )

        assert len(recommendations) > 0
        assert 'items' in recommendations[0]
        assert 'tips' in recommendations[0]


class TestImageProcessor:
    """Tests for ImageProcessor class"""

    def test_create_instance(self):
        """Test ImageProcessor instantiation"""
        processor = ImageProcessor()
        assert processor.supported_formats == ['PNG', 'JPEG', 'JPG', 'WEBP']

    def test_resize_clothing(self):
        """Test clothing resize functionality"""
        processor = ImageProcessor()

        # Create test image
        test_image = Image.new('RGBA', (200, 300), (255, 0, 0, 255))
        resized = processor.resize_clothing(test_image, (100, 150))

        assert resized.size == (100, 150)
        assert resized.mode == 'RGBA'

    def test_extract_dominant_colors(self):
        """Test dominant color extraction"""
        processor = ImageProcessor()

        # Create solid red image
        test_image = Image.new('RGB', (100, 100), (255, 0, 0))
        colors = processor.extract_dominant_colors(test_image, 3)

        assert len(colors) <= 3
        # Dominant color should be close to red
        if colors:
            assert colors[0][0] > 200  # Red channel high

    def test_apply_color_transform(self):
        """Test color transformation"""
        processor = ImageProcessor()

        # Create test image
        test_image = Image.new('RGBA', (50, 50), (255, 0, 0, 255))
        transformed = processor.apply_color_transform(test_image, (0, 0, 255))

        assert transformed.mode == 'RGBA'
        assert transformed.size == test_image.size


class TestMannequinRenderer:
    """Tests for MannequinRenderer class"""

    def test_create_male_mannequin(self):
        """Test male mannequin creation"""
        renderer = MannequinRenderer(gender='male')
        mannequin = renderer.create_base_mannequin()

        assert mannequin.mode == 'RGBA'
        assert mannequin.size == MannequinRenderer.MANNEQUIN_SIZE

    def test_create_female_mannequin(self):
        """Test female mannequin creation"""
        renderer = MannequinRenderer(gender='female')
        mannequin = renderer.create_base_mannequin()

        assert mannequin.mode == 'RGBA'
        assert mannequin.size == MannequinRenderer.MANNEQUIN_SIZE

    def test_skin_tones(self):
        """Test different skin tones"""
        for tone in ['light', 'medium', 'tan', 'dark', 'deep']:
            renderer = MannequinRenderer(gender='male', skin_tone=tone)
            mannequin = renderer.create_base_mannequin()
            assert mannequin is not None

    def test_render_outfit(self):
        """Test outfit rendering"""
        renderer = MannequinRenderer(gender='male')

        # Create simple test clothing
        shirt = Image.new('RGBA', (100, 100), (0, 0, 255, 255))
        clothing = {'shirt': shirt}

        result = renderer.render_outfit(clothing)
        assert result.mode == 'RGB'
        assert result.size == MannequinRenderer.MANNEQUIN_SIZE

    def test_overlay_clothing(self):
        """Test clothing overlay"""
        renderer = MannequinRenderer(gender='female')
        mannequin = renderer.create_base_mannequin()

        shirt = Image.new('RGBA', (80, 80), (255, 0, 0, 128))
        pants = Image.new('RGBA', (60, 100), (0, 0, 255, 128))

        clothing = {'shirt': shirt, 'pants': pants}
        result = renderer.overlay_clothing(mannequin, clothing)

        assert result.mode == 'RGBA'

    def test_get_image_bytes(self):
        """Test image to bytes conversion"""
        renderer = MannequinRenderer()
        mannequin = renderer.create_base_mannequin()

        img_bytes = renderer.get_image_bytes(mannequin)
        assert isinstance(img_bytes, bytes)
        assert len(img_bytes) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
