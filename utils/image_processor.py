"""
Image Processing Utilities for WearBlend
Handles background removal, image resizing, and clothing segmentation
"""

import io
from PIL import Image, ImageFilter, ImageEnhance
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
            # Fallback: attempt simple background removal
            return self._simple_background_removal(image)

        # Convert to bytes for rembg
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Remove background with high quality settings
        output = remove(
            img_byte_arr.getvalue(),
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )

        # Convert back to PIL Image
        result = Image.open(io.BytesIO(output))

        # Clean up edges
        result = self._refine_edges(result)

        return result

    def _simple_background_removal(self, image: Image.Image) -> Image.Image:
        """Simple background removal fallback when rembg is not available"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Get image data
        data = np.array(image)

        # Detect near-white or light gray backgrounds
        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

        # Create mask for background (light colors)
        brightness = (r.astype(float) + g.astype(float) + b.astype(float)) / 3
        bg_mask = brightness > 230

        # Also check for uniform color regions (likely background)
        color_variance = np.std([r, g, b], axis=0)
        uniform_mask = color_variance < 20

        # Combine masks
        combined_mask = bg_mask & uniform_mask

        # Set background to transparent
        data[:, :, 3] = np.where(combined_mask, 0, 255).astype(np.uint8)

        return Image.fromarray(data, 'RGBA')

    def _refine_edges(self, image: Image.Image) -> Image.Image:
        """Refine the edges of a cutout image for cleaner appearance"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Split channels
        r, g, b, a = image.split()

        # Slightly erode then dilate alpha to clean edges
        a = a.filter(ImageFilter.MinFilter(3))
        a = a.filter(ImageFilter.MaxFilter(3))

        # Smooth alpha edges
        a = a.filter(ImageFilter.GaussianBlur(1))

        # Threshold to remove semi-transparent pixels at edges
        a = a.point(lambda x: 255 if x > 128 else 0)

        return Image.merge('RGBA', (r, g, b, a))

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
            # Calculate aspect ratio preserving size
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

            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create new image with target size and paste centered
            new_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            new_img.paste(resized, (paste_x, paste_y), resized if resized.mode == 'RGBA' else None)
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

        # Enhance contrast slightly for better visibility
        enhancer = ImageEnhance.Contrast(processed)
        processed = enhancer.enhance(1.1)

        # Define target sizes based on clothing type (relative to mannequin)
        size_ratios = {
            'shirt': (0.55, 0.32),
            'top': (0.55, 0.32),
            'pants': (0.45, 0.52),
            'bottom': (0.45, 0.52),
            'jacket': (0.65, 0.40),
            'tie': (0.12, 0.28),
            'shoes': (0.38, 0.08),
            'watch': (0.08, 0.06),
            'belt': (0.28, 0.04),
            'scarf': (0.35, 0.14),
            'bag': (0.22, 0.25),
            'accessory': (0.18, 0.18)
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
            if image.mode == 'RGBA':
                # Only consider non-transparent pixels
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert('RGB')

        # Resize for faster processing
        image = image.resize((100, 100), Image.Resampling.LANCZOS)

        # Get pixel data
        pixels = list(image.getdata())

        from collections import Counter

        # Quantize colors to reduce unique colors
        quantized = [(r // 24 * 24, g // 24 * 24, b // 24 * 24) for r, g, b in pixels]

        # Filter out near-white and near-black (often background)
        filtered = [c for c in quantized if not (
            (c[0] > 230 and c[1] > 230 and c[2] > 230) or
            (c[0] < 20 and c[1] < 20 and c[2] < 20)
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
        # Add slight variation to preserve texture
        texture_factor = 0.85

        new_r = target_color[0] * (texture_factor * lum_normalized + (1 - texture_factor) * (r / 255))
        new_g = target_color[1] * (texture_factor * lum_normalized + (1 - texture_factor) * (g / 255))
        new_b = target_color[2] * (texture_factor * lum_normalized + (1 - texture_factor) * (b / 255))

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

    def enhance_clothing_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance clothing image for better display

        Args:
            image: PIL Image

        Returns:
            Enhanced PIL Image
        """
        # Slight sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=50))

        # Slight contrast boost
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.05)

        # Slight saturation boost
        if image.mode in ['RGB', 'RGBA']:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)

        return image
