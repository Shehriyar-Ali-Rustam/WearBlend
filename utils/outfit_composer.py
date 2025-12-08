"""
Outfit Composer for WearBlend
Creates professional flat-lay style outfit arrangements
Similar to fashion lookbook/catalog images where clothes are arranged
to suggest a human form without showing any visible body/mannequin
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import Dict, Tuple, Optional, List
import io
import math


class OutfitComposer:
    """
    Creates flat-lay style outfit compositions where clothing items
    are arranged to suggest a human form without any visible mannequin.
    Inspired by professional fashion photography flat-lay styling.
    """

    CANVAS_SIZE = (800, 1000)

    # Clothing placement zones - positions where each item should be placed
    # These are designed to create a natural "outfit" appearance
    PLACEMENT_ZONES = {
        'shirt': {
            'x': 0.5,           # Center horizontally
            'y': 0.22,          # Upper portion
            'width': 0.55,      # 55% of canvas width
            'height': 0.32,     # 32% of canvas height
            'z_order': 2,
            'rotation': 0,
            'shadow_offset': (8, 12)
        },
        'top': {
            'x': 0.5,
            'y': 0.22,
            'width': 0.55,
            'height': 0.32,
            'z_order': 2,
            'rotation': 0,
            'shadow_offset': (8, 12)
        },
        'pants': {
            'x': 0.5,
            'y': 0.62,
            'width': 0.42,
            'height': 0.45,
            'z_order': 1,
            'rotation': 0,
            'shadow_offset': (6, 10)
        },
        'bottom': {
            'x': 0.5,
            'y': 0.62,
            'width': 0.42,
            'height': 0.45,
            'z_order': 1,
            'rotation': 0,
            'shadow_offset': (6, 10)
        },
        'jacket': {
            'x': 0.5,
            'y': 0.26,
            'width': 0.65,
            'height': 0.40,
            'z_order': 3,
            'rotation': 0,
            'shadow_offset': (10, 14)
        },
        'shoes': {
            'x': 0.5,
            'y': 0.92,
            'width': 0.35,
            'height': 0.10,
            'z_order': 0,
            'rotation': 0,
            'shadow_offset': (4, 6)
        },
        'tie': {
            'x': 0.5,
            'y': 0.32,
            'width': 0.12,
            'height': 0.25,
            'z_order': 4,
            'rotation': 0,
            'shadow_offset': (3, 5)
        },
        'belt': {
            'x': 0.5,
            'y': 0.42,
            'width': 0.30,
            'height': 0.04,
            'z_order': 5,
            'rotation': 0,
            'shadow_offset': (2, 3)
        },
        'scarf': {
            'x': 0.5,
            'y': 0.12,
            'width': 0.40,
            'height': 0.15,
            'z_order': 6,
            'rotation': -5,
            'shadow_offset': (5, 7)
        },
        'bag': {
            'x': 0.18,
            'y': 0.45,
            'width': 0.22,
            'height': 0.25,
            'z_order': 7,
            'rotation': 5,
            'shadow_offset': (6, 8)
        },
        'watch': {
            'x': 0.82,
            'y': 0.38,
            'width': 0.10,
            'height': 0.08,
            'z_order': 8,
            'rotation': -10,
            'shadow_offset': (2, 3)
        }
    }

    # Alternative arrangements for different outfit styles
    STYLE_ARRANGEMENTS = {
        'classic': {
            # Standard vertical arrangement
            'shirt_overlap': 0.08,  # How much shirt overlaps into pants area
            'accessories_spread': 1.0
        },
        'casual': {
            # Slightly angled, more relaxed
            'shirt_overlap': 0.12,
            'accessories_spread': 1.2
        },
        'formal': {
            # Precise, centered alignment
            'shirt_overlap': 0.05,
            'accessories_spread': 0.8
        }
    }

    def __init__(self, style: str = 'classic'):
        self.style = style
        self.arrangement = self.STYLE_ARRANGEMENTS.get(style, self.STYLE_ARRANGEMENTS['classic'])

    def compose_outfit(self, clothing_items: Dict[str, Image.Image],
                        background_color: Tuple[int, int, int] = (245, 242, 238)) -> Image.Image:
        """
        Compose clothing items into a flat-lay style outfit image.

        Args:
            clothing_items: Dictionary mapping clothing type to PIL Image
            background_color: RGB tuple for background

        Returns:
            Composed outfit image
        """
        # Create canvas with subtle gradient background
        canvas = self._create_background(background_color)

        # Sort items by z-order (layer order)
        sorted_items = sorted(
            clothing_items.items(),
            key=lambda x: self.PLACEMENT_ZONES.get(x[0].lower(), {}).get('z_order', 5)
        )

        # Place each item
        for item_type, item_image in sorted_items:
            item_type_lower = item_type.lower()

            if item_type_lower not in self.PLACEMENT_ZONES:
                continue

            zone = self.PLACEMENT_ZONES[item_type_lower]

            # Process and place the item
            canvas = self._place_item(canvas, item_image, zone, item_type_lower)

        # Add final touches
        canvas = self._add_finishing_touches(canvas)

        return canvas

    def _create_background(self, base_color: Tuple[int, int, int]) -> Image.Image:
        """Create a professional flat-lay background with subtle gradient"""
        width, height = self.CANVAS_SIZE
        canvas = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(canvas)

        # Create very subtle radial gradient (lighter in center)
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                # Very subtle gradient - 3% variation
                factor = 1 + (1 - dist / max_dist) * 0.03

                r = min(255, int(base_color[0] * factor))
                g = min(255, int(base_color[1] * factor))
                b = min(255, int(base_color[2] * factor))

                draw.point((x, y), fill=(r, g, b))

        # Apply subtle texture/grain for realism
        canvas = canvas.filter(ImageFilter.GaussianBlur(1))

        return canvas

    def _place_item(self, canvas: Image.Image, item: Image.Image,
                     zone: dict, item_type: str) -> Image.Image:
        """Place a clothing item on the canvas with proper sizing and effects"""
        canvas_width, canvas_height = self.CANVAS_SIZE

        # Calculate target size
        target_width = int(canvas_width * zone['width'])
        target_height = int(canvas_height * zone['height'])

        # Ensure item has alpha channel
        if item.mode != 'RGBA':
            item = item.convert('RGBA')

        # Resize item maintaining aspect ratio
        item = self._resize_maintain_aspect(item, (target_width, target_height))

        # Apply rotation if specified
        rotation = zone.get('rotation', 0)
        if rotation != 0:
            item = item.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)

        # Calculate position (centered on zone coordinates)
        pos_x = int(canvas_width * zone['x'] - item.width // 2)
        pos_y = int(canvas_height * zone['y'] - item.height // 2)

        # Adjust for shirt-pants overlap
        if item_type in ['pants', 'bottom']:
            overlap = int(canvas_height * self.arrangement['shirt_overlap'])
            pos_y -= overlap

        # Create shadow
        shadow = self._create_drop_shadow(item, zone.get('shadow_offset', (5, 8)))

        # Paste shadow first
        shadow_x = pos_x + zone.get('shadow_offset', (5, 8))[0]
        shadow_y = pos_y + zone.get('shadow_offset', (5, 8))[1]
        canvas.paste(shadow, (shadow_x, shadow_y), shadow)

        # Paste item
        canvas.paste(item, (pos_x, pos_y), item)

        return canvas

    def _resize_maintain_aspect(self, image: Image.Image,
                                  target_size: Tuple[int, int]) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            # Image is wider - fit to width
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
        else:
            # Image is taller - fit to height
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _create_drop_shadow(self, image: Image.Image,
                             offset: Tuple[int, int] = (5, 8),
                             blur_radius: int = 15,
                             opacity: float = 0.25) -> Image.Image:
        """Create a realistic drop shadow for an image"""
        # Create shadow from alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Get alpha channel
        _, _, _, alpha = image.split()

        # Create shadow image (black with alpha from original)
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))

        # Apply alpha as shadow
        shadow_alpha = alpha.point(lambda x: int(x * opacity))
        shadow.putalpha(shadow_alpha)

        # Blur the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

        return shadow

    def _add_finishing_touches(self, canvas: Image.Image) -> Image.Image:
        """Add final touches to make the composition look professional"""
        # Slight vignette effect (darker edges)
        canvas = self._add_vignette(canvas, strength=0.08)

        # Very subtle sharpening
        enhancer = ImageEnhance.Sharpness(canvas)
        canvas = enhancer.enhance(1.05)

        return canvas

    def _add_vignette(self, image: Image.Image, strength: float = 0.1) -> Image.Image:
        """Add subtle vignette effect"""
        width, height = image.size
        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Create radial gradient for vignette
        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        # Only darken outer 30% of the image
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                dist_ratio = dist / max_dist

                if dist_ratio > 0.7:
                    # Gradually darken from 70% to edge
                    darken = (dist_ratio - 0.7) / 0.3 * strength
                    current = result.getpixel((x, y))
                    new_color = tuple(int(c * (1 - darken)) for c in current[:3])
                    draw.point((x, y), fill=new_color)

        return result

    def get_image_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """Convert image to bytes for download"""
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    def create_comparison(self, compositions: List[Image.Image],
                           labels: List[str] = None) -> Image.Image:
        """Create side-by-side comparison of multiple compositions"""
        if not compositions:
            return Image.new('RGB', self.CANVAS_SIZE, (255, 255, 255))

        num_images = len(compositions)
        gap = 20
        total_width = self.CANVAS_SIZE[0] * num_images + gap * (num_images - 1)
        total_height = self.CANVAS_SIZE[1] + 50  # Extra space for labels

        comparison = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(comparison)

        for idx, comp in enumerate(compositions):
            x_offset = idx * (self.CANVAS_SIZE[0] + gap)
            comparison.paste(comp, (x_offset, 50))

            if labels and idx < len(labels):
                # Center label above image
                label_x = x_offset + self.CANVAS_SIZE[0] // 2
                draw.text((label_x, 20), labels[idx], fill=(60, 60, 60), anchor="mm")

        return comparison


class OutfitStyler:
    """
    Additional styling options for outfit compositions.
    Handles color variations and style suggestions.
    """

    # Preset background colors for different aesthetics
    BACKGROUND_PRESETS = {
        'minimal': (250, 250, 248),      # Off-white
        'warm': (248, 244, 236),          # Warm cream
        'cool': (242, 246, 250),          # Cool grey-blue
        'neutral': (245, 242, 238),       # Neutral beige
        'pure_white': (255, 255, 255),    # Pure white
        'soft_grey': (240, 240, 240),     # Soft grey
    }

    @staticmethod
    def get_background_color(preset: str) -> Tuple[int, int, int]:
        """Get background color from preset name"""
        return OutfitStyler.BACKGROUND_PRESETS.get(
            preset, OutfitStyler.BACKGROUND_PRESETS['neutral']
        )

    @staticmethod
    def suggest_background(dominant_colors: List[Tuple[int, int, int]]) -> str:
        """Suggest best background preset based on clothing colors"""
        if not dominant_colors:
            return 'neutral'

        # Calculate average warmth of colors
        total_warmth = 0
        for color in dominant_colors:
            # Warm colors have more red than blue
            warmth = color[0] - color[2]
            total_warmth += warmth

        avg_warmth = total_warmth / len(dominant_colors)

        if avg_warmth > 30:
            return 'cool'  # Use cool background for warm clothes
        elif avg_warmth < -30:
            return 'warm'  # Use warm background for cool clothes
        else:
            return 'neutral'
