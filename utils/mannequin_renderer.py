"""
Advanced Mannequin Renderer for WearBlend
Creates realistic 3D-looking mannequins with proper clothing overlay
"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import Dict, Tuple, Optional, List
import io
import math


class MannequinRenderer:
    """Renders realistic 3D-looking mannequins with natural clothing overlay"""

    # Mannequin dimensions
    MANNEQUIN_SIZE = (500, 800)

    # Body segment definitions for realistic proportions
    BODY_SEGMENTS = {
        'male': {
            'head': {'center': (250, 60), 'width': 70, 'height': 85},
            'neck': {'center': (250, 115), 'width': 35, 'height': 30},
            'shoulders': {'center': (250, 145), 'width': 180, 'height': 25},
            'chest': {'center': (250, 200), 'width': 160, 'height': 100},
            'waist': {'center': (250, 310), 'width': 130, 'height': 40},
            'hips': {'center': (250, 360), 'width': 140, 'height': 50},
            'left_arm_upper': {'start': (170, 145), 'end': (130, 260), 'width': 35},
            'right_arm_upper': {'start': (330, 145), 'end': (370, 260), 'width': 35},
            'left_arm_lower': {'start': (130, 260), 'end': (110, 380), 'width': 28},
            'right_arm_lower': {'start': (370, 260), 'end': (390, 380), 'width': 28},
            'left_leg_upper': {'start': (210, 380), 'end': (200, 550), 'width': 50},
            'right_leg_upper': {'start': (290, 380), 'end': (300, 550), 'width': 50},
            'left_leg_lower': {'start': (200, 550), 'end': (195, 720), 'width': 38},
            'right_leg_lower': {'start': (300, 550), 'end': (305, 720), 'width': 38},
            'left_foot': {'center': (190, 750), 'width': 55, 'height': 25},
            'right_foot': {'center': (310, 750), 'width': 55, 'height': 25},
        },
        'female': {
            'head': {'center': (250, 55), 'width': 65, 'height': 80},
            'neck': {'center': (250, 108), 'width': 30, 'height': 28},
            'shoulders': {'center': (250, 138), 'width': 155, 'height': 22},
            'chest': {'center': (250, 190), 'width': 145, 'height': 90},
            'waist': {'center': (250, 290), 'width': 100, 'height': 35},
            'hips': {'center': (250, 345), 'width': 150, 'height': 55},
            'left_arm_upper': {'start': (172, 138), 'end': (140, 248), 'width': 28},
            'right_arm_upper': {'start': (328, 138), 'end': (360, 248), 'width': 28},
            'left_arm_lower': {'start': (140, 248), 'end': (125, 365), 'width': 22},
            'right_arm_lower': {'start': (360, 248), 'end': (375, 365), 'width': 22},
            'left_leg_upper': {'start': (215, 375), 'end': (208, 545), 'width': 45},
            'right_leg_upper': {'start': (285, 375), 'end': (292, 545), 'width': 45},
            'left_leg_lower': {'start': (208, 545), 'end': (205, 715), 'width': 32},
            'right_leg_lower': {'start': (292, 545), 'end': (295, 715), 'width': 32},
            'left_foot': {'center': (200, 745), 'width': 48, 'height': 22},
            'right_foot': {'center': (300, 745), 'width': 48, 'height': 22},
        }
    }

    # Clothing regions for overlay mapping
    CLOTHING_REGIONS = {
        'male': {
            'shirt': {
                'bounds': (90, 130, 410, 350),
                'anchor': (250, 240),
                'scale': (0.75, 0.55),
                'perspective': 0.08,
                'curve_intensity': 0.15
            },
            'top': {
                'bounds': (90, 130, 410, 350),
                'anchor': (250, 240),
                'scale': (0.75, 0.55),
                'perspective': 0.08,
                'curve_intensity': 0.15
            },
            'pants': {
                'bounds': (140, 320, 360, 720),
                'anchor': (250, 520),
                'scale': (0.55, 0.60),
                'perspective': 0.05,
                'curve_intensity': 0.10
            },
            'bottom': {
                'bounds': (140, 320, 360, 720),
                'anchor': (250, 520),
                'scale': (0.55, 0.60),
                'perspective': 0.05,
                'curve_intensity': 0.10
            },
            'jacket': {
                'bounds': (80, 125, 420, 380),
                'anchor': (250, 250),
                'scale': (0.80, 0.60),
                'perspective': 0.10,
                'curve_intensity': 0.12
            },
            'tie': {
                'bounds': (220, 150, 280, 320),
                'anchor': (250, 235),
                'scale': (0.15, 0.40),
                'perspective': 0.02,
                'curve_intensity': 0.05
            },
            'shoes': {
                'bounds': (150, 720, 350, 780),
                'anchor': (250, 750),
                'scale': (0.45, 0.12),
                'perspective': 0.0,
                'curve_intensity': 0.0
            },
            'belt': {
                'bounds': (150, 305, 350, 335),
                'anchor': (250, 320),
                'scale': (0.50, 0.08),
                'perspective': 0.03,
                'curve_intensity': 0.08
            },
            'watch': {
                'bounds': (95, 340, 135, 390),
                'anchor': (115, 365),
                'scale': (0.10, 0.12),
                'perspective': 0.0,
                'curve_intensity': 0.0
            },
            'scarf': {
                'bounds': (180, 110, 320, 200),
                'anchor': (250, 155),
                'scale': (0.35, 0.22),
                'perspective': 0.05,
                'curve_intensity': 0.10
            },
        },
        'female': {
            'shirt': {
                'bounds': (105, 125, 395, 320),
                'anchor': (250, 222),
                'scale': (0.70, 0.50),
                'perspective': 0.06,
                'curve_intensity': 0.18
            },
            'top': {
                'bounds': (105, 125, 395, 320),
                'anchor': (250, 222),
                'scale': (0.70, 0.50),
                'perspective': 0.06,
                'curve_intensity': 0.18
            },
            'pants': {
                'bounds': (145, 310, 355, 715),
                'anchor': (250, 512),
                'scale': (0.52, 0.58),
                'perspective': 0.04,
                'curve_intensity': 0.08
            },
            'bottom': {
                'bounds': (145, 310, 355, 715),
                'anchor': (250, 512),
                'scale': (0.52, 0.58),
                'perspective': 0.04,
                'curve_intensity': 0.08
            },
            'jacket': {
                'bounds': (95, 120, 405, 360),
                'anchor': (250, 240),
                'scale': (0.75, 0.55),
                'perspective': 0.08,
                'curve_intensity': 0.14
            },
            'tie': {
                'bounds': (225, 145, 275, 290),
                'anchor': (250, 218),
                'scale': (0.12, 0.35),
                'perspective': 0.02,
                'curve_intensity': 0.05
            },
            'shoes': {
                'bounds': (160, 715, 340, 770),
                'anchor': (250, 742),
                'scale': (0.40, 0.11),
                'perspective': 0.0,
                'curve_intensity': 0.0
            },
            'belt': {
                'bounds': (160, 285, 340, 312),
                'anchor': (250, 298),
                'scale': (0.45, 0.07),
                'perspective': 0.03,
                'curve_intensity': 0.10
            },
            'watch': {
                'bounds': (110, 330, 145, 375),
                'anchor': (128, 352),
                'scale': (0.09, 0.10),
                'perspective': 0.0,
                'curve_intensity': 0.0
            },
            'scarf': {
                'bounds': (185, 105, 315, 185),
                'anchor': (250, 145),
                'scale': (0.32, 0.20),
                'perspective': 0.05,
                'curve_intensity': 0.12
            },
        }
    }

    # Layer order (lower = rendered first/behind)
    LAYER_ORDER = {
        'pants': 1, 'bottom': 1,
        'shirt': 2, 'top': 2,
        'belt': 3,
        'tie': 4,
        'jacket': 5,
        'scarf': 6,
        'watch': 7,
        'shoes': 0
    }

    # Mannequin surface colors for 3D effect
    MANNEQUIN_COLORS = {
        'light': {
            'base': (235, 225, 215),
            'highlight': (250, 245, 240),
            'shadow': (195, 185, 175),
            'deep_shadow': (165, 155, 145)
        },
        'medium': {
            'base': (215, 195, 175),
            'highlight': (235, 220, 205),
            'shadow': (175, 155, 135),
            'deep_shadow': (145, 125, 105)
        },
        'tan': {
            'base': (195, 165, 135),
            'highlight': (220, 195, 170),
            'shadow': (155, 125, 95),
            'deep_shadow': (125, 95, 65)
        },
        'dark': {
            'base': (130, 95, 70),
            'highlight': (160, 125, 100),
            'shadow': (100, 65, 40),
            'deep_shadow': (70, 45, 25)
        },
        'deep': {
            'base': (85, 55, 35),
            'highlight': (115, 85, 65),
            'shadow': (55, 35, 20),
            'deep_shadow': (35, 20, 10)
        }
    }

    def __init__(self, gender: str = 'male', skin_tone: str = 'medium'):
        self.gender = gender.lower()
        self.skin_tone = skin_tone.lower()
        self.segments = self.BODY_SEGMENTS.get(self.gender, self.BODY_SEGMENTS['male'])
        self.regions = self.CLOTHING_REGIONS.get(self.gender, self.CLOTHING_REGIONS['male'])
        self.colors = self.MANNEQUIN_COLORS.get(self.skin_tone, self.MANNEQUIN_COLORS['medium'])

    def create_base_mannequin(self) -> Image.Image:
        """Create a realistic 3D-looking mannequin"""
        width, height = self.MANNEQUIN_SIZE
        mannequin = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Draw body parts with 3D shading
        self._draw_body_3d(mannequin)

        return mannequin

    def _draw_body_3d(self, image: Image.Image):
        """Draw the mannequin body with 3D shading effects"""
        draw = ImageDraw.Draw(image)

        # Draw in order: legs, arms, torso, head
        self._draw_legs_3d(draw, image)
        self._draw_arms_3d(draw, image)
        self._draw_torso_3d(draw, image)
        self._draw_head_3d(draw, image)

        # Apply overall smoothing
        smoothed = image.filter(ImageFilter.SMOOTH_MORE)
        image.paste(smoothed)

    def _draw_ellipse_3d(self, draw: ImageDraw.Draw, bbox: tuple,
                          direction: str = 'center'):
        """Draw an ellipse with 3D gradient effect"""
        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        rx, ry = (x2 - x1) // 2, (y2 - y1) // 2

        # Draw base shape
        draw.ellipse(bbox, fill=self.colors['base'])

        # Add highlight (top-left)
        highlight_offset = -rx // 4, -ry // 4
        highlight_bbox = (
            cx + highlight_offset[0] - rx // 3,
            cy + highlight_offset[1] - ry // 3,
            cx + highlight_offset[0] + rx // 3,
            cy + highlight_offset[1] + ry // 3
        )
        draw.ellipse(highlight_bbox, fill=self.colors['highlight'])

        # Add shadow (bottom-right)
        shadow_offset = rx // 4, ry // 4
        shadow_bbox = (
            cx + shadow_offset[0] - rx // 2,
            cy + shadow_offset[1] - ry // 2,
            cx + shadow_offset[0] + rx // 2,
            cy + shadow_offset[1] + ry // 2
        )

    def _draw_limb_3d(self, draw: ImageDraw.Draw, start: tuple, end: tuple,
                       width: int, image: Image.Image):
        """Draw a limb segment with 3D cylindrical shading"""
        x1, y1 = start
        x2, y2 = end

        # Calculate perpendicular direction
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return

        nx, ny = -dy / length, dx / length

        # Create polygon points for limb
        hw = width // 2
        points = [
            (x1 + nx * hw, y1 + ny * hw),
            (x2 + nx * hw, y2 + ny * hw),
            (x2 - nx * hw, y2 - ny * hw),
            (x1 - nx * hw, y1 - ny * hw)
        ]

        # Draw base limb
        draw.polygon(points, fill=self.colors['base'])

        # Draw highlight stripe (shifted left)
        highlight_points = [
            (x1 + nx * hw * 0.7, y1 + ny * hw * 0.7),
            (x2 + nx * hw * 0.7, y2 + ny * hw * 0.7),
            (x2 + nx * hw * 0.2, y2 + ny * hw * 0.2),
            (x1 + nx * hw * 0.2, y1 + ny * hw * 0.2)
        ]
        draw.polygon(highlight_points, fill=self.colors['highlight'])

        # Draw shadow stripe (shifted right)
        shadow_points = [
            (x1 - nx * hw * 0.2, y1 - ny * hw * 0.2),
            (x2 - nx * hw * 0.2, y2 - ny * hw * 0.2),
            (x2 - nx * hw * 0.8, y2 - ny * hw * 0.8),
            (x1 - nx * hw * 0.8, y1 - ny * hw * 0.8)
        ]
        draw.polygon(shadow_points, fill=self.colors['shadow'])

        # Round the ends
        draw.ellipse([x1 - hw, y1 - hw, x1 + hw, y1 + hw], fill=self.colors['base'])
        draw.ellipse([x2 - hw, y2 - hw, x2 + hw, y2 + hw], fill=self.colors['base'])

    def _draw_head_3d(self, draw: ImageDraw.Draw, image: Image.Image):
        """Draw head with 3D shading"""
        head = self.segments['head']
        cx, cy = head['center']
        w, h = head['width'], head['height']

        # Head base (oval)
        head_bbox = (cx - w, cy - h, cx + w, cy + h)
        draw.ellipse(head_bbox, fill=self.colors['base'])

        # Highlight on forehead
        highlight_bbox = (cx - w * 0.5, cy - h * 0.8, cx + w * 0.3, cy - h * 0.2)
        draw.ellipse(highlight_bbox, fill=self.colors['highlight'])

        # Shadow on sides
        left_shadow = (cx - w * 0.95, cy - h * 0.3, cx - w * 0.6, cy + h * 0.5)
        draw.ellipse(left_shadow, fill=self.colors['shadow'])

        # Neck
        neck = self.segments['neck']
        nx, ny = neck['center']
        nw, nh = neck['width'], neck['height']
        draw.rectangle([nx - nw, ny - nh, nx + nw, ny + nh], fill=self.colors['base'])

        # Neck shadow
        draw.rectangle([nx + nw * 0.3, ny - nh, nx + nw, ny + nh], fill=self.colors['shadow'])

    def _draw_torso_3d(self, draw: ImageDraw.Draw, image: Image.Image):
        """Draw torso with 3D muscular/curved shading"""
        # Shoulders
        shoulders = self.segments['shoulders']
        sx, sy = shoulders['center']
        sw, sh = shoulders['width'], shoulders['height']

        # Shoulder bar
        draw.rounded_rectangle(
            [sx - sw, sy - sh, sx + sw, sy + sh],
            radius=sh,
            fill=self.colors['base']
        )

        # Chest
        chest = self.segments['chest']
        cx, cy = chest['center']
        cw, ch = chest['width'], chest['height']

        # Main chest shape
        chest_points = [
            (cx - sw, sy),
            (cx + sw, sy),
            (cx + cw, cy + ch * 0.3),
            (cx + cw * 0.8, cy + ch),
            (cx - cw * 0.8, cy + ch),
            (cx - cw, cy + ch * 0.3)
        ]
        draw.polygon(chest_points, fill=self.colors['base'])

        # Chest highlight (center)
        draw.ellipse(
            [cx - cw * 0.4, cy - ch * 0.3, cx + cw * 0.4, cy + ch * 0.4],
            fill=self.colors['highlight']
        )

        # Side shadows
        draw.polygon([
            (cx - cw, cy + ch * 0.3),
            (cx - cw * 0.7, cy - ch * 0.2),
            (cx - cw * 0.7, cy + ch * 0.8),
            (cx - cw * 0.8, cy + ch)
        ], fill=self.colors['shadow'])

        draw.polygon([
            (cx + cw, cy + ch * 0.3),
            (cx + cw * 0.7, cy - ch * 0.2),
            (cx + cw * 0.7, cy + ch * 0.8),
            (cx + cw * 0.8, cy + ch)
        ], fill=self.colors['shadow'])

        # Waist
        waist = self.segments['waist']
        wx, wy = waist['center']
        ww, wh = waist['width'], waist['height']

        draw.rounded_rectangle(
            [wx - ww, wy - wh, wx + ww, wy + wh],
            radius=10,
            fill=self.colors['base']
        )

        # Hips
        hips = self.segments['hips']
        hx, hy = hips['center']
        hw, hh = hips['width'], hips['height']

        hip_points = [
            (hx - ww, wy),
            (hx + ww, wy),
            (hx + hw, hy + hh * 0.5),
            (hx + hw * 0.7, hy + hh),
            (hx - hw * 0.7, hy + hh),
            (hx - hw, hy + hh * 0.5)
        ]
        draw.polygon(hip_points, fill=self.colors['base'])

    def _draw_arms_3d(self, draw: ImageDraw.Draw, image: Image.Image):
        """Draw arms with 3D shading"""
        for side in ['left', 'right']:
            # Upper arm
            upper = self.segments[f'{side}_arm_upper']
            self._draw_limb_3d(draw, upper['start'], upper['end'], upper['width'], image)

            # Lower arm
            lower = self.segments[f'{side}_arm_lower']
            self._draw_limb_3d(draw, lower['start'], lower['end'], lower['width'], image)

            # Hand
            hx, hy = lower['end']
            hw = lower['width']
            draw.ellipse([hx - hw, hy - hw * 0.5, hx + hw, hy + hw * 1.2],
                         fill=self.colors['base'])

    def _draw_legs_3d(self, draw: ImageDraw.Draw, image: Image.Image):
        """Draw legs with 3D shading"""
        for side in ['left', 'right']:
            # Upper leg
            upper = self.segments[f'{side}_leg_upper']
            self._draw_limb_3d(draw, upper['start'], upper['end'], upper['width'], image)

            # Lower leg
            lower = self.segments[f'{side}_leg_lower']
            self._draw_limb_3d(draw, lower['start'], lower['end'], lower['width'], image)

            # Foot
            foot = self.segments[f'{side}_foot']
            fx, fy = foot['center']
            fw, fh = foot['width'], foot['height']
            draw.ellipse([fx - fw, fy - fh, fx + fw, fy + fh], fill=self.colors['base'])

    def apply_clothing_warp(self, clothing: Image.Image, clothing_type: str) -> Image.Image:
        """Apply perspective warp to make clothing look naturally worn"""
        if clothing_type.lower() not in self.regions:
            return clothing

        region = self.regions[clothing_type.lower()]
        bounds = region['bounds']
        target_width = bounds[2] - bounds[0]
        target_height = bounds[3] - bounds[1]

        # Resize to target dimensions
        clothing = clothing.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Apply perspective transformation
        perspective = region.get('perspective', 0)
        curve = region.get('curve_intensity', 0)

        if perspective > 0 or curve > 0:
            clothing = self._apply_body_curve(clothing, perspective, curve)

        return clothing

    def _apply_body_curve(self, image: Image.Image, perspective: float,
                           curve_intensity: float) -> Image.Image:
        """Apply subtle curve to simulate clothing wrapping around body"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        width, height = image.size
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # Create curved displacement
        for y in range(height):
            # Calculate horizontal displacement based on vertical position
            # Creates a subtle barrel/pincushion effect
            y_normalized = (y / height - 0.5) * 2  # -1 to 1

            for x in range(width):
                x_normalized = (x / width - 0.5) * 2  # -1 to 1

                # Apply curve (makes center bulge slightly)
                curve_factor = 1 - curve_intensity * (x_normalized ** 2)
                new_x = int((x_normalized * curve_factor + 1) * width / 2)

                # Apply perspective (slight trapezoid effect)
                persp_scale = 1 - perspective * abs(y_normalized)
                new_x = int(width / 2 + (new_x - width / 2) * persp_scale)

                # Clamp coordinates
                new_x = max(0, min(width - 1, new_x))

                # Copy pixel
                if 0 <= new_x < width:
                    pixel = image.getpixel((x, y))
                    if pixel[3] > 0:  # Only copy non-transparent pixels
                        result.putpixel((new_x, y), pixel)

        # Smooth the result to reduce artifacts
        result = result.filter(ImageFilter.SMOOTH)

        return result

    def _add_clothing_shadows(self, clothing: Image.Image,
                               intensity: float = 0.3) -> Image.Image:
        """Add shadows to clothing edges for depth"""
        if clothing.mode != 'RGBA':
            clothing = clothing.convert('RGBA')

        # Create shadow layer
        shadow = Image.new('RGBA', clothing.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)

        # Get alpha channel
        alpha = clothing.split()[3]

        # Create edge shadow
        edge_shadow = alpha.filter(ImageFilter.FIND_EDGES)
        edge_shadow = edge_shadow.filter(ImageFilter.GaussianBlur(3))

        # Apply shadow
        shadow_array = list(edge_shadow.getdata())
        shadow_pixels = [(0, 0, 0, int(p * intensity)) for p in shadow_array]
        shadow.putdata(shadow_pixels)

        # Composite
        result = Image.alpha_composite(clothing, shadow)

        return result

    def overlay_clothing(self, mannequin: Image.Image,
                          clothing_items: Dict[str, Image.Image]) -> Image.Image:
        """Overlay clothing items with realistic positioning and warping"""
        result = mannequin.copy()

        # Sort by layer order
        sorted_items = sorted(clothing_items.items(),
                               key=lambda x: self.LAYER_ORDER.get(x[0].lower(), 5))

        for clothing_type, clothing_img in sorted_items:
            clothing_type_lower = clothing_type.lower()

            if clothing_type_lower not in self.regions:
                continue

            region = self.regions[clothing_type_lower]

            # Apply warping for realistic fit
            warped = self.apply_clothing_warp(clothing_img, clothing_type_lower)

            # Add shadows for depth
            warped = self._add_clothing_shadows(warped, 0.2)

            # Calculate position
            bounds = region['bounds']
            paste_x = bounds[0]
            paste_y = bounds[1]

            # Ensure RGBA mode
            if warped.mode != 'RGBA':
                warped = warped.convert('RGBA')

            # Paste with transparency
            result.paste(warped, (paste_x, paste_y), warped)

        return result

    def render_outfit(self, clothing_items: Dict[str, Image.Image],
                       background_color: Tuple[int, int, int] = (248, 249, 250)) -> Image.Image:
        """Render complete outfit with professional background"""
        # Create mannequin
        mannequin = self.create_base_mannequin()

        # Overlay clothing
        dressed = self.overlay_clothing(mannequin, clothing_items)

        # Create gradient background
        final = self._create_gradient_background(background_color)

        # Add subtle shadow under mannequin
        final = self._add_floor_shadow(final)

        # Paste dressed mannequin
        final.paste(dressed, (0, 0), dressed)

        return final

    def _create_gradient_background(self,
                                     base_color: Tuple[int, int, int]) -> Image.Image:
        """Create subtle gradient background"""
        width, height = self.MANNEQUIN_SIZE
        bg = Image.new('RGB', (width, height), base_color)
        draw = ImageDraw.Draw(bg)

        # Create vertical gradient (lighter at top)
        for y in range(height):
            factor = 1 - (y / height) * 0.08
            color = tuple(int(c * factor) for c in base_color)
            draw.line([(0, y), (width, y)], fill=color)

        return bg

    def _add_floor_shadow(self, image: Image.Image) -> Image.Image:
        """Add subtle floor shadow for grounding effect"""
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Elliptical shadow at bottom
        shadow_y = height - 60
        for i in range(30):
            alpha = int(40 * (1 - i / 30))
            y_offset = shadow_y + i
            ellipse_width = 120 + i * 2
            draw.ellipse(
                [width // 2 - ellipse_width, y_offset - 10,
                 width // 2 + ellipse_width, y_offset + 10],
                fill=(200, 200, 200)
            )

        return image

    def render_with_color_variation(self, clothing_items: Dict[str, Image.Image],
                                      item_to_change: str,
                                      new_color: Tuple[int, int, int],
                                      image_processor) -> Image.Image:
        """Render with color variation applied to specific item"""
        modified_items = clothing_items.copy()

        if item_to_change in modified_items:
            original = modified_items[item_to_change]
            recolored = image_processor.apply_color_transform(original, new_color)
            modified_items[item_to_change] = recolored

        return self.render_outfit(modified_items)

    def create_comparison_image(self, original: Image.Image,
                                 variations: list,
                                 labels: list = None) -> Image.Image:
        """Create side-by-side comparison with labels"""
        num_images = 1 + len(variations)
        gap = 20
        total_width = self.MANNEQUIN_SIZE[0] * num_images + gap * (num_images - 1)
        label_height = 40
        total_height = self.MANNEQUIN_SIZE[1] + label_height

        comparison = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        draw = ImageDraw.Draw(comparison)

        # Paste original
        comparison.paste(original, (0, label_height))
        if labels:
            draw.text((self.MANNEQUIN_SIZE[0] // 2, 15), labels[0] if labels else "Original",
                      fill=(60, 60, 60), anchor="mm")

        # Paste variations
        x_offset = self.MANNEQUIN_SIZE[0] + gap
        for idx, variation in enumerate(variations):
            comparison.paste(variation, (x_offset, label_height))
            if labels and idx + 1 < len(labels):
                draw.text((x_offset + self.MANNEQUIN_SIZE[0] // 2, 15),
                          labels[idx + 1], fill=(60, 60, 60), anchor="mm")
            x_offset += self.MANNEQUIN_SIZE[0] + gap

        return comparison

    def get_image_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """Convert image to bytes"""
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=95)
        buffer.seek(0)
        return buffer.getvalue()

    def set_gender(self, gender: str):
        """Update gender"""
        self.gender = gender.lower()
        self.segments = self.BODY_SEGMENTS.get(self.gender, self.BODY_SEGMENTS['male'])
        self.regions = self.CLOTHING_REGIONS.get(self.gender, self.CLOTHING_REGIONS['male'])

    def set_skin_tone(self, skin_tone: str):
        """Update skin tone"""
        self.skin_tone = skin_tone.lower()
        self.colors = self.MANNEQUIN_COLORS.get(self.skin_tone, self.MANNEQUIN_COLORS['medium'])
