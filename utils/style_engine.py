"""
Style Recommendation Engine for WearBlend
Provides AI-powered outfit suggestions and style analysis
"""

from typing import List, Dict, Tuple, Optional
from .color_utils import ColorUtils


class StyleEngine:
    """AI-powered style recommendation engine"""

    # Style rules and combinations
    FORMAL_COMBINATIONS = [
        {'shirt': 'white', 'pants': 'charcoal', 'tie': 'navy_blue'},
        {'shirt': 'light_blue', 'pants': 'navy_blue', 'tie': 'burgundy'},
        {'shirt': 'white', 'pants': 'black', 'tie': 'red'},
        {'shirt': 'cream', 'pants': 'charcoal', 'tie': 'forest_green'},
    ]

    CASUAL_COMBINATIONS = [
        {'shirt': 'light_blue', 'pants': 'khaki'},
        {'shirt': 'white', 'pants': 'navy_blue'},
        {'shirt': 'olive', 'pants': 'tan'},
        {'shirt': 'coral', 'pants': 'white'},
    ]

    STYLE_RULES = {
        'formal': {
            'description': 'Professional and elegant for business settings',
            'key_pieces': ['Tailored shirt', 'Dress pants', 'Tie', 'Dress shoes'],
            'avoid': ['Bright colors', 'Casual patterns', 'Sneakers']
        },
        'business_casual': {
            'description': 'Smart yet relaxed for modern workplaces',
            'key_pieces': ['Button-down shirt', 'Chinos or dress pants', 'Loafers'],
            'avoid': ['Ties (usually)', 'Overly casual items', 'Athletic wear']
        },
        'casual': {
            'description': 'Relaxed and comfortable for everyday wear',
            'key_pieces': ['T-shirts or polos', 'Jeans or chinos', 'Sneakers or loafers'],
            'avoid': ['Overly formal pieces', 'Stiff fabrics']
        },
        'smart_casual': {
            'description': 'Polished casual look for social events',
            'key_pieces': ['Nice shirt or sweater', 'Fitted pants', 'Clean shoes'],
            'avoid': ['Gym clothes', 'Overly casual items']
        }
    }

    def __init__(self):
        self.color_utils = ColorUtils()

    def analyze_outfit(self, clothing_items: Dict[str, Tuple[int, int, int]]) -> Dict:
        """
        Analyze an outfit and provide comprehensive feedback

        Args:
            clothing_items: Dictionary of clothing type to dominant color (RGB)

        Returns:
            Analysis dictionary with scores and suggestions
        """
        analysis = {
            'overall_score': 0,
            'color_harmony': 0,
            'style_category': '',
            'strengths': [],
            'improvements': [],
            'suggestions': []
        }

        if not clothing_items:
            return analysis

        colors = list(clothing_items.values())
        items = list(clothing_items.keys())

        # Calculate color harmony
        analysis['color_harmony'] = self._calculate_color_harmony(colors)

        # Determine style category
        analysis['style_category'] = self._determine_style_category(items, colors)

        # Generate strengths
        analysis['strengths'] = self._identify_strengths(clothing_items)

        # Generate improvements
        analysis['improvements'] = self._identify_improvements(clothing_items)

        # Generate specific suggestions
        analysis['suggestions'] = self._generate_suggestions(clothing_items)

        # Calculate overall score (weighted average)
        analysis['overall_score'] = int(
            analysis['color_harmony'] * 0.4 +
            len(analysis['strengths']) * 10 +
            max(0, 50 - len(analysis['improvements']) * 10)
        )
        analysis['overall_score'] = min(100, max(0, analysis['overall_score']))

        return analysis

    def _calculate_color_harmony(self, colors: List[Tuple[int, int, int]]) -> int:
        """Calculate how well the colors work together (0-100)"""
        if len(colors) < 2:
            return 80  # Single item, neutral score

        harmony_score = 70  # Base score

        # Check for neutral colors (always harmonious)
        neutral_count = sum(1 for c in colors if ColorUtils.is_neutral_color(c))
        harmony_score += neutral_count * 5

        # Check contrast ratios between adjacent items
        for i in range(len(colors) - 1):
            contrast = ColorUtils.calculate_contrast_ratio(colors[i], colors[i + 1])
            if 2 < contrast < 7:  # Good contrast range
                harmony_score += 5
            elif contrast > 10:  # Too much contrast
                harmony_score -= 5

        # Check color temperature consistency
        warm_count = sum(1 for c in colors if ColorUtils.is_warm_color(c))
        cold_count = len(colors) - warm_count - neutral_count

        # Consistent temperature is good
        if warm_count == 0 or cold_count == 0:
            harmony_score += 10

        return min(100, max(0, harmony_score))

    def _determine_style_category(self, items: List[str],
                                   colors: List[Tuple[int, int, int]]) -> str:
        """Determine the style category of the outfit"""
        has_tie = 'tie' in [i.lower() for i in items]
        has_jacket = 'jacket' in [i.lower() for i in items]

        # Check for formal indicators
        formal_colors = ['black', 'white', 'navy_blue', 'charcoal', 'grey']
        formal_color_count = sum(1 for c in colors
                                  if ColorUtils.get_color_name(c).lower().replace(' ', '_')
                                  in formal_colors)

        if has_tie and has_jacket:
            return 'formal'
        elif has_tie or (has_jacket and formal_color_count >= 2):
            return 'business_casual'
        elif formal_color_count >= len(colors) // 2:
            return 'smart_casual'
        else:
            return 'casual'

    def _identify_strengths(self, clothing_items: Dict) -> List[str]:
        """Identify strengths in the outfit"""
        strengths = []
        colors = list(clothing_items.values())
        items = list(clothing_items.keys())

        # Check for classic combinations
        if 'shirt' in items or 'top' in items:
            shirt_color = clothing_items.get('shirt') or clothing_items.get('top')
            if shirt_color:
                color_name = ColorUtils.get_color_name(shirt_color)
                if 'white' in color_name.lower() or 'blue' in color_name.lower():
                    strengths.append("Classic shirt color choice - versatile and professional")

        # Check for good neutral base
        neutral_count = sum(1 for c in colors if ColorUtils.is_neutral_color(c))
        if neutral_count >= 1:
            strengths.append("Good use of neutral colors as a base")

        # Check for coordinated color temperature
        warm_count = sum(1 for c in colors if ColorUtils.is_warm_color(c))
        if warm_count == len(colors) or warm_count == 0:
            strengths.append("Consistent color temperature throughout outfit")

        # Check for contrast
        if len(colors) >= 2:
            contrast = ColorUtils.calculate_contrast_ratio(colors[0], colors[1])
            if 3 < contrast < 8:
                strengths.append("Excellent contrast between main pieces")

        return strengths

    def _identify_improvements(self, clothing_items: Dict) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        colors = list(clothing_items.values())

        # Check for too many colors
        unique_color_families = set()
        for color in colors:
            h, s, v = ColorUtils.rgb_to_hsv(color)
            # Group by hue sectors
            hue_family = int(h * 6) if s > 0.2 else 'neutral'
            unique_color_families.add(hue_family)

        if len(unique_color_families) > 3:
            improvements.append("Consider reducing the number of different colors for a more cohesive look")

        # Check for clashing colors
        if len(colors) >= 2:
            for i in range(len(colors) - 1):
                contrast = ColorUtils.calculate_contrast_ratio(colors[i], colors[i + 1])
                if contrast > 15:
                    improvements.append("Some colors have very high contrast - consider adding a transition color")
                    break

        # Check for all dark or all light
        avg_brightness = sum(ColorUtils.rgb_to_hsv(c)[2] for c in colors) / len(colors)
        if avg_brightness < 0.3:
            improvements.append("Outfit appears quite dark - consider adding a lighter accent piece")
        elif avg_brightness > 0.85:
            improvements.append("Outfit is very light - a darker piece could add definition")

        return improvements

    def _generate_suggestions(self, clothing_items: Dict) -> List[Dict]:
        """Generate specific improvement suggestions"""
        suggestions = []

        for item_type, color in clothing_items.items():
            color_name = ColorUtils.get_color_name(color)

            # Suggest matching items for each piece
            matching = ColorUtils.suggest_matching_colors(color, item_type)
            for match in matching[:2]:  # Top 2 suggestions per item
                suggestions.append({
                    'for_item': item_type,
                    'current_color': color_name,
                    'suggestion': match['name'],
                    'reason': match['reason']
                })

        return suggestions

    def get_outfit_recommendations(self, primary_color: Tuple[int, int, int],
                                    occasion: str = 'casual') -> List[Dict]:
        """
        Get complete outfit recommendations based on a primary piece

        Args:
            primary_color: RGB color of the primary clothing item
            occasion: Type of occasion (formal, casual, business_casual)

        Returns:
            List of outfit recommendations
        """
        recommendations = []
        color_name = ColorUtils.get_color_name(primary_color)

        if occasion == 'formal':
            combos = self.FORMAL_COMBINATIONS
            desc = "Professional look for business meetings and formal events"
        else:
            combos = self.CASUAL_COMBINATIONS
            desc = "Relaxed yet put-together look for everyday occasions"

        # Find best matching combinations
        for combo in combos:
            recommendation = {
                'name': f"Outfit with {color_name} as base",
                'description': desc,
                'items': {},
                'tips': []
            }

            for item, color in combo.items():
                if color in ColorUtils.STANDARD_COLORS:
                    recommendation['items'][item] = {
                        'color_name': color.replace('_', ' ').title(),
                        'rgb': ColorUtils.STANDARD_COLORS[color]
                    }

            # Add styling tips
            recommendation['tips'] = self._get_styling_tips(occasion)
            recommendations.append(recommendation)

        return recommendations[:3]  # Return top 3

    def _get_styling_tips(self, occasion: str) -> List[str]:
        """Get styling tips for an occasion"""
        tips = {
            'formal': [
                "Ensure your shirt is well-pressed and tucked in",
                "Match your belt color with your shoes",
                "Keep accessories minimal and elegant",
                "A pocket square can add a sophisticated touch"
            ],
            'business_casual': [
                "You can skip the tie but keep the look polished",
                "Chinos or dress pants both work well",
                "Loafers or clean dress shoes complete the look",
                "A nice watch adds a professional touch"
            ],
            'casual': [
                "Focus on fit - well-fitted casual clothes look more put-together",
                "Clean, white sneakers are versatile and stylish",
                "Don't be afraid to add a pop of color",
                "Layer with a light jacket for added dimension"
            ]
        }
        return tips.get(occasion, tips['casual'])

    def suggest_seasonal_outfit(self, current_items: Dict,
                                 season: str) -> Dict:
        """
        Suggest seasonal adjustments to an outfit

        Args:
            current_items: Current outfit items with colors
            season: Target season (summer, winter, spring, fall)

        Returns:
            Seasonal suggestions dictionary
        """
        seasonal_palette = ColorUtils.get_seasonal_palette(season)
        palette_colors = [c['name'] for c in seasonal_palette]

        suggestions = {
            'season': season,
            'recommended_colors': seasonal_palette[:5],
            'adjustments': [],
            'additions': []
        }

        # Check current items against seasonal palette
        for item, color in current_items.items():
            color_name = ColorUtils.get_color_name(color)
            if color_name.lower().replace(' ', '_') not in [p['name'].lower().replace(' ', '_')
                                                              for p in seasonal_palette]:
                # Suggest a seasonal alternative
                alt = seasonal_palette[0]
                suggestions['adjustments'].append({
                    'item': item,
                    'current': color_name,
                    'suggested': alt['name'],
                    'reason': f"{alt['name']} is a great {season} color that would work well here"
                })

        # Season-specific additions
        if season.lower() == 'winter':
            suggestions['additions'].extend([
                "Consider adding a scarf in a complementary color",
                "A wool jacket or coat would complete the winter look",
                "Darker shoes work better in winter months"
            ])
        elif season.lower() == 'summer':
            suggestions['additions'].extend([
                "Light, breathable fabrics are essential",
                "Consider lighter colored shoes",
                "Sunglasses make a great accessory"
            ])

        return suggestions

    def rate_outfit(self, clothing_items: Dict) -> Dict:
        """
        Rate an outfit with detailed scoring

        Returns:
            Rating dictionary with scores and feedback
        """
        analysis = self.analyze_outfit(clothing_items)

        rating = {
            'overall': analysis['overall_score'],
            'categories': {
                'color_coordination': analysis['color_harmony'],
                'style_coherence': self._rate_style_coherence(clothing_items),
                'versatility': self._rate_versatility(clothing_items),
                'completeness': self._rate_completeness(clothing_items)
            },
            'verdict': '',
            'emoji': ''
        }

        # Generate verdict based on overall score
        if rating['overall'] >= 85:
            rating['verdict'] = "Excellent outfit! Great color coordination and style."
            rating['emoji'] = "⭐⭐⭐⭐⭐"
        elif rating['overall'] >= 70:
            rating['verdict'] = "Good outfit with room for small improvements."
            rating['emoji'] = "⭐⭐⭐⭐"
        elif rating['overall'] >= 55:
            rating['verdict'] = "Decent outfit. Consider the suggestions below."
            rating['emoji'] = "⭐⭐⭐"
        elif rating['overall'] >= 40:
            rating['verdict'] = "This outfit needs some adjustments."
            rating['emoji'] = "⭐⭐"
        else:
            rating['verdict'] = "Consider revising the color combinations."
            rating['emoji'] = "⭐"

        return rating

    def _rate_style_coherence(self, items: Dict) -> int:
        """Rate how coherent the style is"""
        # More items = potentially more coherent if they match
        base_score = 60
        if len(items) >= 3:
            base_score += 20
        if len(items) >= 5:
            base_score += 10
        return min(100, base_score)

    def _rate_versatility(self, items: Dict) -> int:
        """Rate how versatile the outfit is"""
        colors = list(items.values())
        neutral_count = sum(1 for c in colors if ColorUtils.is_neutral_color(c))

        # More neutrals = more versatile
        versatility = 50 + (neutral_count / len(colors)) * 50 if colors else 50
        return int(versatility)

    def _rate_completeness(self, items: Dict) -> int:
        """Rate how complete the outfit is"""
        essential_items = {'shirt', 'top', 'pants', 'bottom'}
        present = set(k.lower() for k in items.keys())

        completeness = 0
        if present & {'shirt', 'top'}:
            completeness += 40
        if present & {'pants', 'bottom'}:
            completeness += 40
        if present & {'shoes'}:
            completeness += 10
        if present & {'tie', 'jacket', 'accessory', 'belt', 'watch', 'scarf'}:
            completeness += 10

        return min(100, completeness)
