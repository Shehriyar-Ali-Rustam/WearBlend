"""
AI-Powered Virtual Try-On for WearBlend
Supports both OpenAI (GPT-4 Vision + DALL-E) and Google Gemini/Imagen APIs
"""

import os
import openai
from PIL import Image
import io
import base64
from typing import Dict, Optional, Tuple, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


class AITryOn:
    """
    AI-powered virtual try-on supporting both OpenAI and Gemini APIs.
    """

    def __init__(self, provider: str = 'openai'):
        """
        Initialize AI Try-On with specified provider.

        Args:
            provider: 'openai' or 'gemini'
        """
        self.provider = provider.lower()
        self.is_configured = False
        self.client = None
        self.gemini_client = None

        self._configure()

    def _configure(self):
        """Configure the API based on provider"""
        if self.provider == 'openai':
            if OPENAI_API_KEY:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                self.is_configured = True
        elif self.provider == 'gemini':
            if GEMINI_API_KEY:
                try:
                    from google import genai
                    self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                    self.is_configured = True
                except ImportError:
                    self.is_configured = False
                except Exception:
                    self.is_configured = False

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        if image.mode == 'RGBA':
            bg = Image.new('RGB', image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[3])
            image = bg
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _analyze_clothing_with_vision(self, clothing_items: Dict[str, Image.Image]) -> str:
        """Use AI Vision to analyze and describe the clothing items"""
        if not self.is_configured:
            return ""

        try:
            if self.provider == 'openai':
                return self._analyze_with_openai(clothing_items)
            elif self.provider == 'gemini':
                return self._analyze_with_gemini(clothing_items)
        except Exception as e:
            return f"Clothing items: {', '.join(clothing_items.keys())}"

    def _analyze_with_openai(self, clothing_items: Dict[str, Image.Image]) -> str:
        """Analyze clothing with OpenAI GPT-4 Vision"""
        content = [
            {
                "type": "text",
                "text": "Describe these clothing items in detail for generating an image of someone wearing them. Include: colors, patterns, style, fabric type, and any distinctive features. Be specific and concise."
            }
        ]

        for item_type, image in clothing_items.items():
            base64_image = self._image_to_base64(image)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}",
                    "detail": "high"
                }
            })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=500
        )

        return response.choices[0].message.content

    def _analyze_with_gemini(self, clothing_items: Dict[str, Image.Image]) -> str:
        """Analyze clothing with Google Gemini Vision"""
        from google import genai
        from google.genai import types

        prompt = "Describe these clothing items in detail for generating an image of someone wearing them. Include: colors, patterns, style, fabric type, and any distinctive features. Be specific and concise."

        # Prepare parts with images
        parts = [prompt]
        for item_type, image in clothing_items.items():
            if image.mode == 'RGBA':
                bg = Image.new('RGB', image.size, (255, 255, 255))
                bg.paste(image, mask=image.split()[3])
                image = bg
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert image to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            image_bytes = buffer.getvalue()

            parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

        response = self.gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=parts
        )
        return response.text if hasattr(response, 'text') else str(response)

    def generate_with_custom_prompt(
        self,
        clothing_items: Dict[str, Image.Image],
        user_prompt: str
    ) -> Tuple[Optional[Image.Image], str]:
        """
        Generate AI try-on image with a custom user prompt.
        """
        if not self.is_configured:
            return None, f"API not configured for {self.provider}. Check your API keys."

        if not clothing_items:
            return None, "No clothing items provided."

        if not user_prompt:
            return None, "Please provide a prompt describing how you want to see the outfit."

        try:
            # First, analyze the clothing items using Vision API
            clothing_description = self._analyze_clothing_with_vision(clothing_items)

            # Combine user prompt with clothing description
            full_prompt = f"""Create a high-quality, photorealistic fashion photograph based on this request:

USER REQUEST: {user_prompt}

THE OUTFIT CONSISTS OF:
{clothing_description}

IMPORTANT REQUIREMENTS:
- The person must be wearing EXACTLY the clothing items described above
- Match the colors, patterns, and styles precisely as described
- Full body shot showing the complete outfit from head to toe
- Realistic fabric draping and natural fit
- Professional fashion photography quality
- Sharp focus, proper lighting, magazine-quality image"""

            if self.provider == 'openai':
                return self._generate_with_dalle(full_prompt)
            elif self.provider == 'gemini':
                return self._generate_with_gemini(full_prompt, clothing_items)

        except Exception as e:
            return None, f"Error generating image: {str(e)[:200]}"

    def _generate_with_dalle(self, prompt: str) -> Tuple[Optional[Image.Image], str]:
        """Generate image with DALL-E 3"""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792",
                quality="hd",
                n=1,
            )

            image_url = response.data[0].url
            image_response = requests.get(image_url)

            if image_response.status_code == 200:
                generated_image = Image.open(io.BytesIO(image_response.content))
                return generated_image, "Success! AI outfit generated with OpenAI DALL-E."
            else:
                return None, "Failed to download generated image."

        except openai.BadRequestError as e:
            error_msg = str(e)
            if "safety" in error_msg.lower() or "content_policy" in error_msg.lower():
                return None, "Request blocked by content policy. Try a different prompt."
            elif "billing" in error_msg.lower() or "limit" in error_msg.lower():
                return None, "OpenAI billing limit reached. Please add credits to your OpenAI account."
            return None, f"Request error: {error_msg[:200]}"
        except openai.AuthenticationError:
            return None, "Invalid OpenAI API key."
        except openai.RateLimitError:
            return None, "OpenAI rate limit exceeded. Try again later."
        except Exception as e:
            error_msg = str(e)
            if "billing" in error_msg.lower():
                return None, "OpenAI billing limit reached. Please add credits to your OpenAI account."
            return None, f"OpenAI error: {error_msg[:200]}"

    def _generate_with_gemini(self, prompt: str, clothing_items: Dict[str, Image.Image]) -> Tuple[Optional[Image.Image], str]:
        """Generate image with Gemini 2.0 Flash (native image generation)"""
        try:
            from google import genai
            from google.genai import types

            # Use Gemini 2.0 Flash Experimental with native image generation
            # This model can generate images directly without needing Imagen
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                )
            )

            # Check if response contains an image
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Decode the image
                        image_bytes = part.inline_data.data
                        if isinstance(image_bytes, str):
                            image_bytes = base64.b64decode(image_bytes)
                        generated_image = Image.open(io.BytesIO(image_bytes))
                        return generated_image, "Success! AI outfit generated with Gemini."

                # If no image found, check for text response
                text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]
                if text_parts:
                    return None, f"Gemini couldn't generate an image. Response: {text_parts[0][:200]}"

            return None, "No image generated by Gemini."

        except Exception as e:
            error_msg = str(e)
            if "PERMISSION_DENIED" in error_msg or "403" in error_msg:
                return None, "Gemini API access denied. Check your API key permissions."
            elif "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                return None, "Gemini rate limit exceeded. Try again later."
            elif "safety" in error_msg.lower() or "blocked" in error_msg.lower():
                return None, "Request blocked by safety filter. Try a different prompt."
            elif "not supported" in error_msg.lower():
                return None, "Image generation not supported with this API key."
            return None, f"Gemini error: {error_msg[:200]}"

    def analyze_outfit(
        self,
        clothing_items: Dict[str, Image.Image]
    ) -> Tuple[Optional[str], str]:
        """Use AI to analyze the outfit and provide styling advice."""
        if not self.is_configured:
            return None, "API not configured."

        if not clothing_items:
            return None, "No clothing items provided."

        try:
            analysis_prompt = """Analyze these clothing items as a professional fashion stylist. Provide:

1. COLOR HARMONY: How well do the colors work together? Score out of 10.
2. STYLE COHESION: Do the pieces create a cohesive look? Score out of 10.
3. OCCASION: What occasions would this outfit be suitable for?
4. SUGGESTIONS: What could be added or changed to improve the outfit?
5. OVERALL RATING: Give an overall style rating out of 10.

Be concise and specific in your analysis."""

            if self.provider == 'openai':
                content = [{"type": "text", "text": analysis_prompt}]
                for item_type, image in clothing_items.items():
                    base64_image = self._image_to_base64(image)
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}
                    })

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=800
                )
                return response.choices[0].message.content, "Analysis complete."

            elif self.provider == 'gemini':
                from google import genai
                from google.genai import types

                parts = [analysis_prompt]
                for item_type, image in clothing_items.items():
                    if image.mode == 'RGBA':
                        bg = Image.new('RGB', image.size, (255, 255, 255))
                        bg.paste(image, mask=image.split()[3])
                        image = bg
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')

                    buffer = io.BytesIO()
                    image.save(buffer, format='PNG')
                    buffer.seek(0)
                    image_bytes = buffer.getvalue()

                    parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=parts
                )
                return response.text if hasattr(response, 'text') else str(response), "Analysis complete."

        except Exception as e:
            return None, f"Error analyzing outfit: {str(e)[:200]}"

    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of configured providers"""
        providers = []
        if OPENAI_API_KEY:
            providers.append('openai')
        if GEMINI_API_KEY:
            try:
                from google import genai
                providers.append('gemini')
            except ImportError:
                pass
        return providers

    @staticmethod
    def is_any_configured() -> bool:
        """Check if any API is configured"""
        return bool(OPENAI_API_KEY or GEMINI_API_KEY)
