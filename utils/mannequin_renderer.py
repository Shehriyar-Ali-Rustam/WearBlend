"""
Advanced Mannequin Renderer for WearBlend
Creates realistic fashion-style mannequins similar to professional lookbook images
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
from typing import Dict, Tuple, Optional, List
import io
import math


class MannequinRenderer:
    """
    Renders realistic fashion mannequins with natural clothing overlay.
    Inspired by professional fashion flat-lay and lookbook styling.
    """

    MANNEQUIN_SIZE = (600, 900)

    # Realistic body shape coordinates for smooth silhouette
    # These define the outline for a natural human form
    BODY_SHAPES = {
        'female': {
            # Head and neck
            'head_top': (300, 25),
            'head_right': (340, 60),
            'head_bottom_right': (330, 110),
            'neck_right': (320, 130),
            'neck_bottom_right': (325, 155),

            # Shoulders and arms (right side)
            'shoulder_right': (395, 165),
            'arm_outer_right_1': (420, 200),
            'arm_outer_right_2': (435, 280),
            'arm_outer_right_3': (445, 360),
            'hand_right': (450, 420),
            'arm_inner_right_3': (420, 410),
            'arm_inner_right_2': (405, 340),
            'arm_inner_right_1': (390, 260),
            'armpit_right': (375, 200),

            # Torso right side
            'bust_right': (380, 240),
            'waist_right': (355, 340),
            'hip_right': (385, 420),
            'hip_outer_right': (390, 480),

            # Legs right side
            'thigh_outer_right': (380, 550),
            'knee_outer_right': (370, 650),
            'calf_outer_right': (365, 750),
            'ankle_right': (360, 830),
            'foot_right': (380, 865),
            'foot_inner_right': (340, 865),
            'ankle_inner_right': (335, 830),
            'calf_inner_right': (340, 750),
            'knee_inner_right': (345, 650),
            'thigh_inner_right': (340, 550),
            'crotch': (300, 500),

            # Legs left side (mirror)
            'thigh_inner_left': (260, 550),
            'knee_inner_left': (255, 650),
            'calf_inner_left': (260, 750),
            'ankle_inner_left': (265, 830),
            'foot_inner_left': (260, 865),
            'foot_left': (220, 865),
            'ankle_left': (240, 830),
            'calf_outer_left': (235, 750),
            'knee_outer_left': (230, 650),
            'thigh_outer_left': (220, 550),

            # Hip and torso left side
            'hip_outer_left': (210, 480),
            'hip_left': (215, 420),
            'waist_left': (245, 340),
            'bust_left': (220, 240),

            # Arms left side
            'armpit_left': (225, 200),
            'arm_inner_left_1': (210, 260),
            'arm_inner_left_2': (195, 340),
            'arm_inner_left_3': (180, 410),
            'hand_left': (150, 420),
            'arm_outer_left_3': (155, 360),
            'arm_outer_left_2': (165, 280),
            'arm_outer_left_1': (180, 200),
            'shoulder_left': (205, 165),

            # Back to neck and head
            'neck_bottom_left': (275, 155),
            'neck_left': (280, 130),
            'head_bottom_left': (270, 110),
            'head_left': (260, 60),
        },
        'male': {
            # Head and neck
            'head_top': (300, 20),
            'head_right': (345, 55),
            'head_bottom_right': (338, 105),
            'neck_right': (330, 125),
            'neck_bottom_right': (340, 155),

            # Shoulders and arms (right side) - broader for male
            'shoulder_right': (420, 165),
            'arm_outer_right_1': (450, 210),
            'arm_outer_right_2': (465, 300),
            'arm_outer_right_3': (470, 390),
            'hand_right': (475, 450),
            'arm_inner_right_3': (445, 440),
            'arm_inner_right_2': (425, 360),
            'arm_inner_right_1': (405, 280),
            'armpit_right': (395, 210),

            # Torso right side - more straight/angular
            'chest_right': (395, 250),
            'waist_right': (375, 350),
            'hip_right': (380, 420),
            'hip_outer_right': (375, 470),

            # Legs right side
            'thigh_outer_right': (370, 540),
            'knee_outer_right': (365, 650),
            'calf_outer_right': (360, 760),
            'ankle_right': (355, 840),
            'foot_right': (375, 875),
            'foot_inner_right': (335, 875),
            'ankle_inner_right': (330, 840),
            'calf_inner_right': (335, 760),
            'knee_inner_right': (340, 650),
            'thigh_inner_right': (335, 540),
            'crotch': (300, 490),

            # Legs left side
            'thigh_inner_left': (265, 540),
            'knee_inner_left': (260, 650),
            'calf_inner_left': (265, 760),
            'ankle_inner_left': (270, 840),
            'foot_inner_left': (265, 875),
            'foot_left': (225, 875),
            'ankle_left': (245, 840),
            'calf_outer_left': (240, 760),
            'knee_outer_left': (235, 650),
            'thigh_outer_left': (230, 540),

            # Hip and torso left side
            'hip_outer_left': (225, 470),
            'hip_left': (220, 420),
            'waist_left': (225, 350),
            'chest_left': (205, 250),

            # Arms left side
            'armpit_left': (205, 210),
            'arm_inner_left_1': (195, 280),
            'arm_inner_left_2': (175, 360),
            'arm_inner_left_3': (155, 440),
            'hand_left': (125, 450),
            'arm_outer_left_3': (130, 390),
            'arm_outer_left_2': (135, 300),
            'arm_outer_left_1': (150, 210),
            'shoulder_left': (180, 165),

            # Back to neck and head
            'neck_bottom_left': (260, 155),
            'neck_left': (270, 125),
            'head_bottom_left': (262, 105),
            'head_left': (255, 55),
        }
    }

    # Clothing placement regions with body-aware boundaries
    CLOTHING_REGIONS = {
        'female': {
            'shirt': {
                'top': 155,
                'bottom': 420,
                'left': 150,
                'right': 450,
                'body_width_at_top': 190,
                'body_width_at_bottom': 170,
                'center_x': 300
            },
            'top': {
                'top': 155,
                'bottom': 420,
                'left': 150,
                'right': 450,
                'body_width_at_top': 190,
                'body_width_at_bottom': 170,
                'center_x': 300
            },
            'pants': {
                'top': 400,
                'bottom': 860,
                'left': 180,
                'right': 420,
                'body_width_at_top': 180,
                'body_width_at_bottom': 120,
                'center_x': 300
            },
            'bottom': {
                'top': 400,
                'bottom': 860,
                'left': 180,
                'right': 420,
                'body_width_at_top': 180,
                'body_width_at_bottom': 120,
                'center_x': 300
            },
            'jacket': {
                'top': 150,
                'bottom': 480,
                'left': 120,
                'right': 480,
                'body_width_at_top': 220,
                'body_width_at_bottom': 200,
                'center_x': 300
            },
            'shoes': {
                'top': 850,
                'bottom': 895,
                'left': 200,
                'right': 400,
                'center_x': 300
            },
            'tie': {
                'top': 160,
                'bottom': 380,
                'left': 270,
                'right': 330,
                'center_x': 300
            },
            'belt': {
                'top': 335,
                'bottom': 365,
                'left': 230,
                'right': 370,
                'center_x': 300
            },
            'scarf': {
                'top': 120,
                'bottom': 220,
                'left': 200,
                'right': 400,
                'center_x': 300
            },
            'bag': {
                'top': 250,
                'bottom': 450,
                'left': 400,
                'right': 520,
                'center_x': 460
            },
            'watch': {
                'top': 380,
                'bottom': 420,
                'left': 140,
                'right': 180,
                'center_x': 160
            }
        },
        'male': {
            'shirt': {
                'top': 155,
                'bottom': 430,
                'left': 125,
                'right': 475,
                'body_width_at_top': 240,
                'body_width_at_bottom': 170,
                'center_x': 300
            },
            'top': {
                'top': 155,
                'bottom': 430,
                'left': 125,
                'right': 475,
                'body_width_at_top': 240,
                'body_width_at_bottom': 170,
                'center_x': 300
            },
            'pants': {
                'top': 410,
                'bottom': 870,
                'left': 190,
                'right': 410,
                'body_width_at_top': 160,
                'body_width_at_bottom': 110,
                'center_x': 300
            },
            'bottom': {
                'top': 410,
                'bottom': 870,
                'left': 190,
                'right': 410,
                'body_width_at_top': 160,
                'body_width_at_bottom': 110,
                'center_x': 300
            },
            'jacket': {
                'top': 150,
                'bottom': 490,
                'left': 100,
                'right': 500,
                'body_width_at_top': 260,
                'body_width_at_bottom': 200,
                'center_x': 300
            },
            'shoes': {
                'top': 860,
                'bottom': 900,
                'left': 200,
                'right': 400,
                'center_x': 300
            },
            'tie': {
                'top': 165,
                'bottom': 400,
                'left': 265,
                'right': 335,
                'center_x': 300
            },
            'belt': {
                'top': 345,
                'bottom': 375,
                'left': 220,
                'right': 380,
                'center_x': 300
            },
            'scarf': {
                'top': 120,
                'bottom': 220,
                'left': 200,
                'right': 400,
                'center_x': 300
            },
            'bag': {
                'top': 260,
                'bottom': 460,
                'left': 420,
                'right': 550,
                'center_x': 485
            },
            'watch': {
                'top': 400,
                'bottom': 445,
                'left': 130,
                'right': 175,
                'center_x': 152
            }
        }
    }

    LAYER_ORDER = {
        'pants': 1, 'bottom': 1,
        'shirt': 2, 'top': 2,
        'belt': 3,
        'tie': 4,
        'jacket': 5,
        'scarf': 6,
        'watch': 7,
        'bag': 8,
        'shoes': 0
    }

    # Skin tone colors - muted, realistic tones
    SKIN_TONES = {
        'light': (245, 235, 225),
        'medium': (225, 205, 185),
        'tan': (200, 170, 140),
        'dark': (150, 110, 80),
        'deep': (100, 70, 50)
    }

    def __init__(self, gender: str = 'female', skin_tone: str = 'medium'):
        self.gender = gender.lower()
        self.skin_tone = skin_tone.lower()
        self.body_shape = self.BODY_SHAPES.get(self.gender, self.BODY_SHAPES['female'])
        self.regions = self.CLOTHING_REGIONS.get(self.gender, self.CLOTHING_REGIONS['female'])
        self.base_color = self.SKIN_TONES.get(self.skin_tone, self.SKIN_TONES['medium'])

    def _get_body_outline_points(self) -> List[Tuple[int, int]]:
        """Get ordered points for body outline polygon"""
        shape = self.body_shape

        if self.gender == 'female':
            points = [
                shape['head_top'],
                shape['head_right'],
                shape['head_bottom_right'],
                shape['neck_right'],
                shape['neck_bottom_right'],
                shape['shoulder_right'],
                shape['arm_outer_right_1'],
                shape['arm_outer_right_2'],
                shape['arm_outer_right_3'],
                shape['hand_right'],
                shape['arm_inner_right_3'],
                shape['arm_inner_right_2'],
                shape['arm_inner_right_1'],
                shape['armpit_right'],
                shape['bust_right'],
                shape['waist_right'],
                shape['hip_right'],
                shape['hip_outer_right'],
                shape['thigh_outer_right'],
                shape['knee_outer_right'],
                shape['calf_outer_right'],
                shape['ankle_right'],
                shape['foot_right'],
                shape['foot_inner_right'],
                shape['ankle_inner_right'],
                shape['calf_inner_right'],
                shape['knee_inner_right'],
                shape['thigh_inner_right'],
                shape['crotch'],
                shape['thigh_inner_left'],
                shape['knee_inner_left'],
                shape['calf_inner_left'],
                shape['ankle_inner_left'],
                shape['foot_inner_left'],
                shape['foot_left'],
                shape['ankle_left'],
                shape['calf_outer_left'],
                shape['knee_outer_left'],
                shape['thigh_outer_left'],
                shape['hip_outer_left'],
                shape['hip_left'],
                shape['waist_left'],
                shape['bust_left'],
                shape['armpit_left'],
                shape['arm_inner_left_1'],
                shape['arm_inner_left_2'],
                shape['arm_inner_left_3'],
                shape['hand_left'],
                shape['arm_outer_left_3'],
                shape['arm_outer_left_2'],
                shape['arm_outer_left_1'],
                shape['shoulder_left'],
                shape['neck_bottom_left'],
                shape['neck_left'],
                shape['head_bottom_left'],
                shape['head_left'],
            ]
        else:  # male
            points = [
                shape['head_top'],
                shape['head_right'],
                shape['head_bottom_right'],
                shape['neck_right'],
                shape['neck_bottom_right'],
                shape['shoulder_right'],
                shape['arm_outer_right_1'],
                shape['arm_outer_right_2'],
                shape['arm_outer_right_3'],
                shape['hand_right'],
                shape['arm_inner_right_3'],
                shape['arm_inner_right_2'],
                shape['arm_inner_right_1'],
                shape['armpit_right'],
                shape['chest_right'],
                shape['waist_right'],
                shape['hip_right'],
                shape['hip_outer_right'],
                shape['thigh_outer_right'],
                shape['knee_outer_right'],
                shape['calf_outer_right'],
                shape['ankle_right'],
                shape['foot_right'],
                shape['foot_inner_right'],
                shape['ankle_inner_right'],
                shape['calf_inner_right'],
                shape['knee_inner_right'],
                shape['thigh_inner_right'],
                shape['crotch'],
                shape['thigh_inner_left'],
                shape['knee_inner_left'],
                shape['calf_inner_left'],
                shape['ankle_inner_left'],
                shape['foot_inner_left'],
                shape['foot_left'],
                shape['ankle_left'],
                shape['calf_outer_left'],
                shape['knee_outer_left'],
                shape['thigh_outer_left'],
                shape['hip_outer_left'],
                shape['hip_left'],
                shape['waist_left'],
                shape['chest_left'],
                shape['armpit_left'],
                shape['arm_inner_left_1'],
                shape['arm_inner_left_2'],
                shape['arm_inner_left_3'],
                shape['hand_left'],
                shape['arm_outer_left_3'],
                shape['arm_outer_left_2'],
                shape['arm_outer_left_1'],
                shape['shoulder_left'],
                shape['neck_bottom_left'],
                shape['neck_left'],
                shape['head_bottom_left'],
                shape['head_left'],
            ]

        return points

    def create_body_mask(self) -> Image.Image:
        """Create a mask of the body silhouette"""
        mask = Image.new('L', self.MANNEQUIN_SIZE, 0)
        draw = ImageDraw.Draw(mask)

        points = self._get_body_outline_points()
        draw.polygon(points, fill=255)

        # Smooth the mask
        mask = mask.filter(ImageFilter.GaussianBlur(2))
        mask = mask.point(lambda x: 255 if x > 128 else 0)

        return mask

    def create_base_mannequin(self) -> Image.Image:
        """Create a realistic mannequin silhouette"""
        mannequin = Image.new('RGBA', self.MANNEQUIN_SIZE, (0, 0, 0, 0))

        # Create body mask
        body_mask = self.create_body_mask()

        # Create base body color with subtle gradient
        body_layer = self._create_body_with_shading()

        # Apply mask to body
        mannequin.paste(body_layer, (0, 0), body_mask)

        # Smooth edges
        mannequin = self._smooth_edges(mannequin)

        return mannequin

    def _create_body_with_shading(self) -> Image.Image:
        """Create body with natural shading"""
        width, height = self.MANNEQUIN_SIZE
        body = Image.new('RGB', (width, height), self.base_color)
        draw = ImageDraw.Draw(body)

        # Add subtle vertical gradient for 3D effect
        base_r, base_g, base_b = self.base_color

        for y in range(height):
            # Darker at edges, lighter in center vertically
            factor = 1.0 - abs(y / height - 0.5) * 0.15

            for x in range(width):
                # Horizontal shading - lighter in center
                x_factor = 1.0 - abs(x / width - 0.5) * 0.1
                combined_factor = factor * x_factor

                r = int(min(255, base_r * combined_factor))
                g = int(min(255, base_g * combined_factor))
                b = int(min(255, base_b * combined_factor))

                draw.point((x, y), fill=(r, g, b))

        # Apply slight blur for smooth gradient
        body = body.filter(ImageFilter.GaussianBlur(3))

        return body

    def _smooth_edges(self, image: Image.Image) -> Image.Image:
        """Smooth the edges of the mannequin for realistic appearance"""
        # Get alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        r, g, b, a = image.split()

        # Blur alpha slightly for anti-aliasing
        a = a.filter(ImageFilter.GaussianBlur(1))

        # Recombine
        return Image.merge('RGBA', (r, g, b, a))

    def _fit_clothing_to_body(self, clothing: Image.Image,
                               clothing_type: str) -> Image.Image:
        """
        Fit clothing to body shape with natural draping effect
        """
        if clothing_type.lower() not in self.regions:
            return clothing

        region = self.regions[clothing_type.lower()]

        # Calculate target dimensions
        target_width = region['right'] - region['left']
        target_height = region['bottom'] - region['top']

        # Ensure clothing has alpha channel
        if clothing.mode != 'RGBA':
            clothing = clothing.convert('RGBA')

        # Resize clothing to fit region
        clothing = clothing.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Apply body-conforming warp for shirts/pants
        if clothing_type.lower() in ['shirt', 'top', 'pants', 'bottom', 'jacket']:
            clothing = self._apply_body_contour_warp(clothing, region)

        # Add natural fabric shadows
        clothing = self._add_fabric_shadows(clothing)

        return clothing

    def _apply_body_contour_warp(self, image: Image.Image,
                                   region: dict) -> Image.Image:
        """Apply warp to make clothing follow body contours"""
        width, height = image.size
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Get body width variation
        top_width = region.get('body_width_at_top', width)
        bottom_width = region.get('body_width_at_bottom', width)
        center_x = width // 2

        for y in range(height):
            # Calculate body width at this height (linear interpolation)
            progress = y / height
            body_width = top_width + (bottom_width - top_width) * progress

            # Scale factor for this row
            scale = body_width / width

            for x in range(width):
                # Calculate source x position
                x_offset = x - center_x
                source_x = int(center_x + x_offset / scale) if scale > 0 else x

                # Apply subtle curve for body roundness
                curve_amount = 0.03
                normalized_x = (x - center_x) / (width / 2) if width > 0 else 0
                curve_offset = int(curve_amount * height * (1 - normalized_x ** 2) * (0.5 - abs(progress - 0.5)))
                source_y = y - curve_offset

                # Clamp source coordinates
                source_x = max(0, min(width - 1, source_x))
                source_y = max(0, min(height - 1, source_y))

                # Copy pixel
                pixel = image.getpixel((source_x, source_y))
                if pixel[3] > 0:
                    result.putpixel((x, y), pixel)

        return result

    def _add_fabric_shadows(self, image: Image.Image,
                             intensity: float = 0.15) -> Image.Image:
        """Add subtle shadows to simulate fabric folds"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        width, height = image.size

        # Create shadow overlay
        shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Add vertical fold shadows
        for x in range(width):
            # Create wave pattern for fold simulation
            fold_factor = math.sin(x / width * math.pi * 4) * 0.5 + 0.5
            shadow_alpha = int(30 * fold_factor * intensity)

            for y in range(height):
                current = image.getpixel((x, y))
                if current[3] > 0:  # Only apply to non-transparent pixels
                    shadow.putpixel((x, y), (0, 0, 0, shadow_alpha))

        # Blur shadows for natural look
        shadow = shadow.filter(ImageFilter.GaussianBlur(5))

        # Composite shadow onto image
        return Image.alpha_composite(image, shadow)

    def overlay_clothing(self, mannequin: Image.Image,
                          clothing_items: Dict[str, Image.Image]) -> Image.Image:
        """Overlay clothing items with realistic fitting"""
        result = mannequin.copy()

        # Sort by layer order
        sorted_items = sorted(
            clothing_items.items(),
            key=lambda x: self.LAYER_ORDER.get(x[0].lower(), 5)
        )

        for clothing_type, clothing_img in sorted_items:
            clothing_type_lower = clothing_type.lower()

            if clothing_type_lower not in self.regions:
                continue

            region = self.regions[clothing_type_lower]

            # Fit clothing to body
            fitted = self._fit_clothing_to_body(clothing_img, clothing_type_lower)

            # Calculate paste position
            paste_x = region['left']
            paste_y = region['top']

            # Ensure RGBA
            if fitted.mode != 'RGBA':
                fitted = fitted.convert('RGBA')

            # Paste with transparency
            result.paste(fitted, (paste_x, paste_y), fitted)

        return result

    def render_outfit(self, clothing_items: Dict[str, Image.Image],
                       background_color: Tuple[int, int, int] = (245, 243, 240)) -> Image.Image:
        """Render complete outfit with clean background"""
        # Create mannequin
        mannequin = self.create_base_mannequin()

        # Overlay clothing
        dressed = self.overlay_clothing(mannequin, clothing_items)

        # Create clean background
        final = Image.new('RGB', self.MANNEQUIN_SIZE, background_color)

        # Add very subtle gradient
        final = self._add_subtle_background_gradient(final, background_color)

        # Paste dressed mannequin
        final.paste(dressed, (0, 0), dressed)

        # Add subtle ground shadow
        final = self._add_ground_shadow(final)

        return final

    def _add_subtle_background_gradient(self, image: Image.Image,
                                          base_color: Tuple[int, int, int]) -> Image.Image:
        """Add very subtle radial gradient to background"""
        width, height = image.size
        draw = ImageDraw.Draw(image)

        center_x, center_y = width // 2, height // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)

        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                factor = 1 - (dist / max_dist) * 0.05  # Very subtle

                r = int(base_color[0] * factor)
                g = int(base_color[1] * factor)
                b = int(base_color[2] * factor)

                draw.point((x, y), fill=(r, g, b))

        return image

    def _add_ground_shadow(self, image: Image.Image) -> Image.Image:
        """Add subtle shadow at the feet for grounding"""
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Shadow ellipse at bottom
        shadow_y = height - 40
        for i in range(20):
            alpha = int(25 * (1 - i / 20))
            gray = 200 - alpha // 2

            ellipse_width = 80 + i * 3
            draw.ellipse(
                [width // 2 - ellipse_width, shadow_y + i - 5,
                 width // 2 + ellipse_width, shadow_y + i + 5],
                fill=(gray, gray, gray)
            )

        return image

    def render_with_color_variation(self, clothing_items: Dict[str, Image.Image],
                                      item_to_change: str,
                                      new_color: Tuple[int, int, int],
                                      image_processor) -> Image.Image:
        """Render with color variation applied"""
        modified_items = clothing_items.copy()

        if item_to_change in modified_items:
            original = modified_items[item_to_change]
            recolored = image_processor.apply_color_transform(original, new_color)
            modified_items[item_to_change] = recolored

        return self.render_outfit(modified_items)

    def create_comparison_image(self, original: Image.Image,
                                 variations: list,
                                 labels: list = None) -> Image.Image:
        """Create side-by-side comparison"""
        num_images = 1 + len(variations)
        gap = 30
        total_width = self.MANNEQUIN_SIZE[0] * num_images + gap * (num_images - 1)
        label_height = 50
        total_height = self.MANNEQUIN_SIZE[1] + label_height

        comparison = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(comparison)

        # Paste original
        comparison.paste(original, (0, label_height))
        if labels and len(labels) > 0:
            text_x = self.MANNEQUIN_SIZE[0] // 2
            draw.text((text_x, 20), labels[0], fill=(60, 60, 60), anchor="mm")

        # Paste variations
        x_offset = self.MANNEQUIN_SIZE[0] + gap
        for idx, variation in enumerate(variations):
            comparison.paste(variation, (x_offset, label_height))
            if labels and idx + 1 < len(labels):
                text_x = x_offset + self.MANNEQUIN_SIZE[0] // 2
                draw.text((text_x, 20), labels[idx + 1], fill=(60, 60, 60), anchor="mm")
            x_offset += self.MANNEQUIN_SIZE[0] + gap

        return comparison

    def get_image_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """Convert image to bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    def set_gender(self, gender: str):
        """Update gender setting"""
        self.gender = gender.lower()
        self.body_shape = self.BODY_SHAPES.get(self.gender, self.BODY_SHAPES['female'])
        self.regions = self.CLOTHING_REGIONS.get(self.gender, self.CLOTHING_REGIONS['female'])

    def set_skin_tone(self, skin_tone: str):
        """Update skin tone"""
        self.skin_tone = skin_tone.lower()
        self.base_color = self.SKIN_TONES.get(self.skin_tone, self.SKIN_TONES['medium'])
