"""
Color Utilities for WearBlend
Handles color analysis, harmony calculations, and color transformations
"""

from typing import List, Tuple, Dict
import colorsys


class ColorUtils:
    """Utilities for color analysis and manipulation"""

    # Predefined color palettes for suggestions
    STANDARD_COLORS = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'navy_blue': (0, 0, 128),
        'royal_blue': (65, 105, 225),
        'light_blue': (173, 216, 230),
        'beige': (245, 245, 220),
        'khaki': (240, 230, 140),
        'olive': (128, 128, 0),
        'maroon': (128, 0, 0),
        'burgundy': (128, 0, 32),
        'red': (255, 0, 0),
        'pink': (255, 192, 203),
        'coral': (255, 127, 80),
        'orange': (255, 165, 0),
        'yellow': (255, 255, 0),
        'gold': (255, 215, 0),
        'green': (0, 128, 0),
        'forest_green': (34, 139, 34),
        'teal': (0, 128, 128),
        'purple': (128, 0, 128),
        'lavender': (230, 230, 250),
        'grey': (128, 128, 128),
        'charcoal': (54, 69, 79),
        'silver': (192, 192, 192),
        'brown': (139, 69, 19),
        'tan': (210, 180, 140),
        'cream': (255, 253, 208),
    }

    # Color harmony rules
    FORMAL_COLORS = ['black', 'white', 'navy_blue', 'charcoal', 'grey', 'burgundy']
    CASUAL_COLORS = ['beige', 'khaki', 'light_blue', 'olive', 'tan', 'coral']
    SUMMER_COLORS = ['white', 'light_blue', 'pink', 'coral', 'yellow', 'lavender', 'cream']
    WINTER_COLORS = ['black', 'navy_blue', 'burgundy', 'forest_green', 'charcoal', 'maroon']

    @staticmethod
    def rgb_to_hsv(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert RGB to HSV color space"""
        r, g, b = rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
        return colorsys.rgb_to_hsv(r, g, b)

    @staticmethod
    def hsv_to_rgb(hsv: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """Convert HSV to RGB color space"""
        r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
        return (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def get_color_name(rgb: Tuple[int, int, int]) -> str:
        """
        Get the closest named color for an RGB value

        Args:
            rgb: RGB tuple

        Returns:
            Color name string
        """
        min_distance = float('inf')
        closest_name = 'unknown'

        for name, color in ColorUtils.STANDARD_COLORS.items():
            distance = sum((a - b) ** 2 for a, b in zip(rgb, color)) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_name = name

        return closest_name.replace('_', ' ').title()

    @staticmethod
    def get_complementary_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Get the complementary color"""
        h, s, v = ColorUtils.rgb_to_hsv(rgb)
        h = (h + 0.5) % 1.0
        return ColorUtils.hsv_to_rgb((h, s, v))

    @staticmethod
    def get_analogous_colors(rgb: Tuple[int, int, int],
                             angle: float = 30) -> List[Tuple[int, int, int]]:
        """Get analogous colors (adjacent on color wheel)"""
        h, s, v = ColorUtils.rgb_to_hsv(rgb)
        angle_norm = angle / 360

        colors = [
            ColorUtils.hsv_to_rgb(((h - angle_norm) % 1.0, s, v)),
            rgb,
            ColorUtils.hsv_to_rgb(((h + angle_norm) % 1.0, s, v))
        ]
        return colors

    @staticmethod
    def get_triadic_colors(rgb: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get triadic colors (120 degrees apart)"""
        h, s, v = ColorUtils.rgb_to_hsv(rgb)
        return [
            rgb,
            ColorUtils.hsv_to_rgb(((h + 1 / 3) % 1.0, s, v)),
            ColorUtils.hsv_to_rgb(((h + 2 / 3) % 1.0, s, v))
        ]

    @staticmethod
    def calculate_contrast_ratio(color1: Tuple[int, int, int],
                                  color2: Tuple[int, int, int]) -> float:
        """
        Calculate contrast ratio between two colors (WCAG formula)
        """

        def luminance(rgb):
            r, g, b = [x / 255 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = luminance(color1)
        l2 = luminance(color2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def is_warm_color(rgb: Tuple[int, int, int]) -> bool:
        """Check if color is warm (red, orange, yellow range)"""
        h, s, v = ColorUtils.rgb_to_hsv(rgb)
        # Warm colors: hue between 0-60 degrees and 300-360 degrees
        return h < 0.17 or h > 0.83

    @staticmethod
    def is_neutral_color(rgb: Tuple[int, int, int]) -> bool:
        """Check if color is neutral (low saturation)"""
        h, s, v = ColorUtils.rgb_to_hsv(rgb)
        return s < 0.15

    @staticmethod
    def get_color_variations(rgb: Tuple[int, int, int],
                              num_variations: int = 6) -> List[Dict]:
        """
        Generate color variations for a given color

        Returns list of dictionaries with color name, RGB, and type
        """
        variations = []
        h, s, v = ColorUtils.rgb_to_hsv(rgb)

        # Original color
        color_name = ColorUtils.get_color_name(rgb)
        variations.append({
            'name': f'Original ({color_name})',
            'rgb': rgb,
            'type': 'original'
        })

        # Lighter version
        lighter_v = min(1.0, v + 0.2)
        lighter_rgb = ColorUtils.hsv_to_rgb((h, max(0, s - 0.1), lighter_v))
        variations.append({
            'name': 'Lighter Shade',
            'rgb': lighter_rgb,
            'type': 'lighter'
        })

        # Darker version
        darker_v = max(0, v - 0.2)
        darker_rgb = ColorUtils.hsv_to_rgb((h, min(1, s + 0.1), darker_v))
        variations.append({
            'name': 'Darker Shade',
            'rgb': darker_rgb,
            'type': 'darker'
        })

        # More saturated
        sat_s = min(1.0, s + 0.3)
        saturated_rgb = ColorUtils.hsv_to_rgb((h, sat_s, v))
        variations.append({
            'name': 'More Vibrant',
            'rgb': saturated_rgb,
            'type': 'saturated'
        })

        # Complementary
        comp_rgb = ColorUtils.get_complementary_color(rgb)
        variations.append({
            'name': f'Complementary ({ColorUtils.get_color_name(comp_rgb)})',
            'rgb': comp_rgb,
            'type': 'complementary'
        })

        # Add standard colors that complement
        if ColorUtils.is_warm_color(rgb):
            # Add a cool color
            variations.append({
                'name': 'Navy Blue',
                'rgb': ColorUtils.STANDARD_COLORS['navy_blue'],
                'type': 'standard'
            })
        else:
            # Add a warm color
            variations.append({
                'name': 'Burgundy',
                'rgb': ColorUtils.STANDARD_COLORS['burgundy'],
                'type': 'standard'
            })

        return variations[:num_variations]

    @staticmethod
    def suggest_matching_colors(primary_color: Tuple[int, int, int],
                                 clothing_type: str) -> List[Dict]:
        """
        Suggest matching colors based on primary color and clothing type

        Args:
            primary_color: RGB tuple of the primary clothing item
            clothing_type: Type of clothing to match

        Returns:
            List of color suggestions with reasoning
        """
        suggestions = []
        color_name = ColorUtils.get_color_name(primary_color)
        is_neutral = ColorUtils.is_neutral_color(primary_color)
        is_warm = ColorUtils.is_warm_color(primary_color)

        if clothing_type.lower() in ['tie', 'scarf', 'accessory']:
            if is_neutral:
                # Neutral shirts/pants pair well with bold ties
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['burgundy'],
                    'name': 'Burgundy',
                    'reason': f'A burgundy {clothing_type} adds sophistication to your neutral {color_name} outfit'
                })
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['navy_blue'],
                    'name': 'Navy Blue',
                    'reason': f'Navy blue creates a classic, professional look with {color_name}'
                })
            else:
                # Colored items pair with complementary or neutral
                comp = ColorUtils.get_complementary_color(primary_color)
                suggestions.append({
                    'color': comp,
                    'name': ColorUtils.get_color_name(comp),
                    'reason': f'A complementary color creates visual interest with your {color_name}'
                })
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['charcoal'],
                    'name': 'Charcoal',
                    'reason': f'Charcoal is a safe, elegant choice that works with any color'
                })

        elif clothing_type.lower() in ['pants', 'bottom']:
            if is_warm:
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['khaki'],
                    'name': 'Khaki',
                    'reason': f'Khaki pants complement warm {color_name} tones beautifully'
                })
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['navy_blue'],
                    'name': 'Navy Blue',
                    'reason': f'Navy creates a classic contrast with warm {color_name}'
                })
            else:
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['charcoal'],
                    'name': 'Charcoal',
                    'reason': f'Charcoal pants provide a sophisticated base for cool {color_name}'
                })
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['tan'],
                    'name': 'Tan',
                    'reason': f'Tan adds warmth to balance cool {color_name} tones'
                })

        elif clothing_type.lower() in ['shirt', 'top']:
            if is_neutral:
                suggestions.append({
                    'color': ColorUtils.STANDARD_COLORS['light_blue'],
                    'name': 'Light Blue',
                    'reason': f'Light blue is universally flattering and works with neutral {color_name}'
                })
            suggestions.append({
                'color': ColorUtils.STANDARD_COLORS['white'],
                'name': 'White',
                'reason': 'White is the most versatile shirt color for any outfit'
            })

        # Always add some universal suggestions
        suggestions.append({
            'color': ColorUtils.STANDARD_COLORS['black'],
            'name': 'Black',
            'reason': 'Black is timeless and matches everything'
        })

        return suggestions[:5]

    @staticmethod
    def get_seasonal_palette(season: str) -> List[Dict]:
        """Get color palette for a specific season"""
        if season.lower() == 'summer':
            colors = ColorUtils.SUMMER_COLORS
        elif season.lower() == 'winter':
            colors = ColorUtils.WINTER_COLORS
        elif season.lower() == 'formal':
            colors = ColorUtils.FORMAL_COLORS
        else:
            colors = ColorUtils.CASUAL_COLORS

        return [{
            'name': name.replace('_', ' ').title(),
            'rgb': ColorUtils.STANDARD_COLORS[name]
        } for name in colors if name in ColorUtils.STANDARD_COLORS]
