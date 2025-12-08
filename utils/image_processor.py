"""
Image Processing Utilities for WearBlend
Handles background removal, image resizing, and clothing segmentation
"""

import io
from PIL import Image
import numpy as np

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False


class ImageProcessor:
    """Handles all image processing operations for clothing items"""

    def __init__(self):
        self.supported_formats = ['PNG', 'JPEG', 'JPG', 'WEBP']

    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove background from clothing image using rembg AI model

        Args:
            image: PIL Image object

        Returns:
            PIL Image with transparent background
        """
        if not REMBG_AVAILABLE:
            # Fallback: return image as-is with alpha channel
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            return image

        # Convert to bytes for rembg
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Remove background
        output = remove(img_byte_arr.getvalue())

        # Convert back to PIL Image
        return Image.open(io.BytesIO(output))

    def resize_clothing(self, image: Image.Image, target_size: tuple,
                        maintain_aspect: bool = True) -> Image.Image:
        """
        Resize clothing image to fit mannequin dimensions

        Args:
            image: PIL Image object
            target_size: (width, height) tuple
            maintain_aspect: Whether to maintain aspect ratio

        Returns:
            Resized PIL Image
        """
        if maintain_aspect:
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            # Create new image with target size and paste centered
            new_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
            paste_x = (target_size[0] - image.width) // 2
            paste_y = (target_size[1] - image.height) // 2
            new_img.paste(image, (paste_x, paste_y), image if image.mode == 'RGBA' else None)
            return new_img
        else:
            return image.resize(target_size, Image.Resampling.LANCZOS)

    def prepare_clothing_for_overlay(self, image: Image.Image,
                                      clothing_type: str,
                                      mannequin_size: tuple) -> Image.Image:
        """
        Prepare clothing item for overlay on mannequin

        Args:
            image: Original clothing image
            clothing_type: Type of clothing (shirt, pants, etc.)
            mannequin_size: Size of the mannequin image

        Returns:
            Processed image ready for overlay
        """
        # Remove background first
        processed = self.remove_background(image)

        # Define target sizes based on clothing type (relative to mannequin)
        size_ratios = {
            'shirt': (0.65, 0.35),
            'top': (0.65, 0.35),
            'pants': (0.55, 0.45),
            'bottom': (0.55, 0.45),
            'jacket': (0.70, 0.40),
            'tie': (0.15, 0.30),
            'shoes': (0.35, 0.15),
            'watch': (0.10, 0.10),
            'belt': (0.40, 0.05),
            'scarf': (0.30, 0.25),
            'accessory': (0.20, 0.20)
        }

        ratio = size_ratios.get(clothing_type.lower(), (0.5, 0.5))
        target_width = int(mannequin_size[0] * ratio[0])
        target_height = int(mannequin_size[1] * ratio[1])

        return self.resize_clothing(processed, (target_width, target_height))

    def extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> list:
        """
        Extract dominant colors from clothing image

        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract

        Returns:
            List of RGB tuples
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            # Handle RGBA by compositing on white background
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert('RGB')

        # Resize for faster processing
        image = image.resize((150, 150), Image.Resampling.LANCZOS)

        # Get pixel data
        pixels = list(image.getdata())

        # Simple color clustering (k-means lite)
        from collections import Counter

        # Quantize colors to reduce unique colors
        quantized = [(r // 32 * 32, g // 32 * 32, b // 32 * 32) for r, g, b in pixels]

        # Filter out near-white and near-black (often background)
        filtered = [c for c in quantized if not (
            (c[0] > 240 and c[1] > 240 and c[2] > 240) or
            (c[0] < 15 and c[1] < 15 and c[2] < 15)
        )]

        if not filtered:
            filtered = quantized

        # Get most common colors
        color_counts = Counter(filtered)
        dominant = color_counts.most_common(num_colors)

        return [color for color, count in dominant]

    def apply_color_transform(self, image: Image.Image,
                               target_color: tuple) -> Image.Image:
        """
        Transform clothing color while preserving texture and shadows

        Args:
            image: PIL Image with RGBA
            target_color: Target RGB color tuple

        Returns:
            Recolored PIL Image
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)

        # Separate channels
        r, g, b, a = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2], img_array[:, :, 3]

        # Calculate luminance (perceived brightness)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b

        # Normalize luminance to 0-1
        lum_normalized = luminance / 255.0

        # Apply target color with luminance preservation
        new_r = target_color[0] * lum_normalized
        new_g = target_color[1] * lum_normalized
        new_b = target_color[2] * lum_normalized

        # Clip values and convert back
        new_r = np.clip(new_r, 0, 255).astype(np.uint8)
        new_g = np.clip(new_g, 0, 255).astype(np.uint8)
        new_b = np.clip(new_b, 0, 255).astype(np.uint8)
        a = a.astype(np.uint8)

        # Stack channels
        result = np.stack([new_r, new_g, new_b, a], axis=2)

        return Image.fromarray(result, 'RGBA')

    def create_clothing_mask(self, image: Image.Image) -> Image.Image:
        """
        Create a binary mask of the clothing item

        Args:
            image: PIL Image (preferably with alpha channel)

        Returns:
            Binary mask as PIL Image
        """
        if image.mode == 'RGBA':
            # Use alpha channel as mask
            return image.split()[3]
        else:
            # Convert to grayscale and threshold
            gray = image.convert('L')
            return gray.point(lambda x: 255 if x > 10 else 0)
