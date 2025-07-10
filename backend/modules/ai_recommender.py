"""
AI Recommendation Engine - Machine Learning for Interior Design Suggestions
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import json
import logging
from pathlib import Path
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
import colorsys
import math

logger = logging.getLogger(__name__)


class AIRecommender:
    """AI-powered recommendation engine for interior design"""
    
    def __init__(self, model_dir: str = "models"):
        """Initialize the AI recommender with pre-trained models"""
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Initialize models (would be loaded from saved files in production)
        self.style_classifier = None
        self.furniture_recommender = None
        self.color_harmony_model = None
        
        # Load furniture database
        self.furniture_database = self._load_furniture_database()
        self.color_database = self._load_color_database()
        self.style_templates = self._load_style_templates()
        
        # Initialize vectorizers for text-based recommendations
        self.style_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.furniture_vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        
        logger.info("AI Recommender initialized successfully")
    
    def generate_comprehensive_recommendations(self, room_analysis: Dict, user_preferences: Dict = None) -> Dict:
        """
        Generate comprehensive design recommendations based on room analysis
        
        Args:
            room_analysis: Results from room scanning analysis
            user_preferences: User style preferences and constraints
            
        Returns:
            Dictionary containing all recommendation categories
        """
        try:
            # Extract key features from room analysis
            room_features = self._extract_room_features(room_analysis)
            
            # Apply user preferences if provided
            if user_preferences:
                room_features.update(user_preferences)
            
            # Generate different types of recommendations
            recommendations = {
                "furniture_recommendations": self._recommend_furniture(room_features, room_analysis),
                "color_recommendations": self._recommend_colors(room_features, room_analysis),
                "layout_recommendations": self._recommend_layout(room_features, room_analysis),
                "style_recommendations": self._recommend_style_improvements(room_features, room_analysis),
                "lighting_recommendations": self._recommend_lighting(room_features, room_analysis),
                "decor_recommendations": self._recommend_decor(room_features, room_analysis),
                "budget_options": self._generate_budget_options(room_features),
                "priority_ranking": self._rank_recommendations_by_priority(room_features)
            }
            
            # Calculate confidence scores for each recommendation type
            recommendations["confidence_scores"] = self._calculate_recommendation_confidence(
                recommendations, room_analysis
            )
            
            logger.info("Comprehensive recommendations generated successfully")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _extract_room_features(self, room_analysis: Dict) -> Dict:
        """Extract key features from room analysis for ML models"""
        try:
            features = {
                # Room dimensions
                "room_area": room_analysis.get("room_dimensions", {}).get("estimated_length", 4) * 
                           room_analysis.get("room_dimensions", {}).get("estimated_width", 3.5),
                "room_height": room_analysis.get("room_dimensions", {}).get("estimated_height", 2.7),
                "room_aspect_ratio": self._calculate_aspect_ratio(room_analysis.get("room_dimensions", {})),
                
                # Color features
                "dominant_color_hue": self._get_dominant_hue(room_analysis.get("color_palette", {})),
                "color_temperature": room_analysis.get("color_palette", {}).get("temperature", "neutral"),
                "color_harmony": room_analysis.get("color_palette", {}).get("color_harmony", "varied"),
                
                # Lighting features
                "brightness_level": room_analysis.get("lighting_analysis", {}).get("overall_brightness", 128),
                "natural_light": room_analysis.get("lighting_analysis", {}).get("natural_light_detected", False),
                "lighting_level": room_analysis.get("lighting_analysis", {}).get("lighting_level", "moderate"),
                
                # Style features
                "current_style": room_analysis.get("style_analysis", {}).get("primary_style", "unknown"),
                "style_confidence": room_analysis.get("style_analysis", {}).get("confidence", 0.5),
                
                # Object features
                "existing_furniture": [obj["class"] for obj in room_analysis.get("detected_objects", [])],
                "furniture_count": len(room_analysis.get("detected_objects", [])),
                
                # Space utilization
                "space_density": self._calculate_space_density(room_analysis)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting room features: {e}")
            return {}
    
    def _recommend_furniture(self, room_features: Dict, room_analysis: Dict) -> List[Dict]:
        """Recommend furniture based on room analysis and user preferences"""
        try:
            recommendations = []
            
            # Analyze current furniture gaps
            existing_furniture = room_features.get("existing_furniture", [])
            room_area = room_features.get("room_area", 14)  # Default 4x3.5m room
            
            # Essential furniture recommendations based on room type and size
            essential_items = self._get_essential_furniture(room_area, existing_furniture)
            
            for item_type in essential_items:
                # Find suitable furniture items from database
                suitable_items = self._find_suitable_furniture(
                    item_type, room_features, room_analysis
                )
                
                if suitable_items:
                    # Rank items by suitability score
                    ranked_items = self._rank_furniture_items(suitable_items, room_features)
                    
                    # Add top recommendations
                    for item in ranked_items[:3]:  # Top 3 per category
                        recommendation = {
                            "item_type": item_type,
                            "item_name": item["name"],
                            "description": item["description"],
                            "style": item["style"],
                            "dimensions": item["dimensions"],
                            "price_range": item["price_range"],
                            "suitability_score": item["suitability_score"],
                            "reasoning": self._generate_furniture_reasoning(item, room_features),
                            "placement_suggestion": self._suggest_placement(item, room_analysis),
                            "alternatives": self._find_alternative_items(item, suitable_items)
                        }
                        recommendations.append(recommendation)
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error recommending furniture: {e}")
            return []
    
    def _recommend_colors(self, room_features: Dict, room_analysis: Dict) -> Dict:
        """Recommend color schemes and palettes"""
        try:
            current_colors = room_analysis.get("color_palette", {}).get("dominant_colors", [])
            color_temperature = room_features.get("color_temperature", "neutral")
            lighting_level = room_features.get("lighting_level", "moderate")
            current_style = room_features.get("current_style", "unknown")
            
            # Generate color recommendations based on different strategies
            recommendations = {
                "complementary_scheme": self._generate_complementary_colors(current_colors),
                "analogous_scheme": self._generate_analogous_colors(current_colors),
                "monochromatic_scheme": self._generate_monochromatic_colors(current_colors),
                "style_based_scheme": self._generate_style_based_colors(current_style),
                "lighting_optimized_scheme": self._generate_lighting_optimized_colors(lighting_level),
                "accent_colors": self._recommend_accent_colors(current_colors),
                "wall_colors": self._recommend_wall_colors(room_features),
                "color_psychology": self._analyze_color_psychology(current_colors)
            }
            
            # Add implementation suggestions
            for scheme_name, scheme in recommendations.items():
                if isinstance(scheme, dict) and "colors" in scheme:
                    scheme["implementation"] = self._suggest_color_implementation(scheme["colors"])
                    scheme["confidence"] = self._calculate_color_confidence(scheme, room_features)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending colors: {e}")
            return {}
    
    def _recommend_layout(self, room_features: Dict, room_analysis: Dict) -> List[Dict]:
        """Recommend room layout and furniture arrangement"""
        try:
            room_dimensions = room_analysis.get("room_dimensions", {})
            existing_objects = room_analysis.get("detected_objects", [])
            room_area = room_features.get("room_area", 14)
            
            layout_recommendations = []
            
            # Analyze current layout efficiency
            current_efficiency = self._analyze_layout_efficiency(existing_objects, room_dimensions)
            
            # Generate layout suggestions
            layout_types = ["conversation_focused", "traffic_optimized", "multifunctional", "minimalist"]
            
            for layout_type in layout_types:
                layout_plan = self._generate_layout_plan(layout_type, room_dimensions, room_area)
                
                recommendation = {
                    "layout_type": layout_type,
                    "description": layout_plan["description"],
                    "furniture_arrangement": layout_plan["arrangement"],
                    "traffic_flow": layout_plan["traffic_flow"],
                    "space_utilization": layout_plan["space_utilization"],
                    "suitability_score": self._calculate_layout_suitability(layout_plan, room_features),
                    "implementation_steps": layout_plan["steps"],
                    "pros_and_cons": layout_plan["pros_cons"]
                }
                layout_recommendations.append(recommendation)
            
            # Sort by suitability score
            layout_recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
            
            return layout_recommendations
            
        except Exception as e:
            logger.error(f"Error recommending layout: {e}")
            return []
    
    def _recommend_style_improvements(self, room_features: Dict, room_analysis: Dict) -> List[Dict]:
        """Recommend style improvements and cohesion enhancements"""
        try:
            current_style = room_features.get("current_style", "unknown")
            style_confidence = room_features.get("style_confidence", 0.5)
            
            improvements = []
            
            # If style confidence is low, suggest style definition
            if style_confidence < 0.6:
                style_suggestions = self._suggest_style_definition(room_features)
                improvements.extend(style_suggestions)
            
            # Suggest style consistency improvements
            consistency_improvements = self._suggest_style_consistency(current_style, room_analysis)
            improvements.extend(consistency_improvements)
            
            # Suggest style evolution options
            evolution_options = self._suggest_style_evolution(current_style, room_features)
            improvements.extend(evolution_options)
            
            return improvements[:8]  # Limit to top 8 suggestions
            
        except Exception as e:
            logger.error(f"Error recommending style improvements: {e}")
            return []
    
    def _recommend_lighting(self, room_features: Dict, room_analysis: Dict) -> Dict:
        """Recommend lighting improvements and solutions"""
        try:
            lighting_analysis = room_analysis.get("lighting_analysis", {})
            current_brightness = lighting_analysis.get("overall_brightness", 128)
            natural_light = lighting_analysis.get("natural_light_detected", False)
            room_area = room_features.get("room_area", 14)
            
            recommendations = {
                "ambient_lighting": self._recommend_ambient_lighting(current_brightness, room_area),
                "task_lighting": self._recommend_task_lighting(room_features),
                "accent_lighting": self._recommend_accent_lighting(room_features),
                "natural_light_optimization": self._recommend_natural_light_optimization(natural_light),
                "lighting_fixtures": self._recommend_lighting_fixtures(room_features),
                "smart_lighting": self._recommend_smart_lighting_solutions(room_features)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error recommending lighting: {e}")
            return {}
    
    def _recommend_decor(self, room_features: Dict, room_analysis: Dict) -> List[Dict]:
        """Recommend decorative elements and accessories"""
        try:
            current_style = room_features.get("current_style", "unknown")
            color_palette = room_analysis.get("color_palette", {})
            room_area = room_features.get("room_area", 14)
            
            decor_recommendations = []
            
            # Wall decor
            wall_decor = self._recommend_wall_decor(current_style, color_palette)
            decor_recommendations.extend(wall_decor)
            
            # Textiles and soft furnishings
            textiles = self._recommend_textiles(current_style, color_palette)
            decor_recommendations.extend(textiles)
            
            # Plants and natural elements
            plants = self._recommend_plants(room_features)
            decor_recommendations.extend(plants)
            
            # Decorative objects
            objects = self._recommend_decorative_objects(current_style, room_area)
            decor_recommendations.extend(objects)
            
            return decor_recommendations[:12]  # Limit to top 12 items
            
        except Exception as e:
            logger.error(f"Error recommending decor: {e}")
            return []
    
    def _generate_budget_options(self, room_features: Dict) -> Dict:
        """Generate recommendations for different budget levels"""
        try:
            budget_options = {
                "low_budget": {
                    "range": "$0 - $500",
                    "focus": "DIY improvements and small changes",
                    "recommendations": self._generate_low_budget_recommendations(room_features)
                },
                "medium_budget": {
                    "range": "$500 - $2000",
                    "focus": "Key furniture pieces and moderate updates",
                    "recommendations": self._generate_medium_budget_recommendations(room_features)
                },
                "high_budget": {
                    "range": "$2000+",
                    "focus": "Complete room transformation",
                    "recommendations": self._generate_high_budget_recommendations(room_features)
                }
            }
            
            return budget_options
            
        except Exception as e:
            logger.error(f"Error generating budget options: {e}")
            return {}
    
    def _rank_recommendations_by_priority(self, room_features: Dict) -> List[Dict]:
        """Rank all recommendations by priority and impact"""
        try:
            priorities = [
                {
                    "category": "lighting",
                    "priority": 1,
                    "impact": "high",
                    "reasoning": "Lighting affects the entire room atmosphere and functionality"
                },
                {
                    "category": "color_scheme",
                    "priority": 2,
                    "impact": "high",
                    "reasoning": "Colors set the mood and style foundation"
                },
                {
                    "category": "layout",
                    "priority": 3,
                    "impact": "medium",
                    "reasoning": "Good layout improves functionality and flow"
                },
                {
                    "category": "key_furniture",
                    "priority": 4,
                    "impact": "medium",
                    "reasoning": "Essential furniture pieces for comfort and function"
                },
                {
                    "category": "decor_accessories",
                    "priority": 5,
                    "impact": "low",
                    "reasoning": "Accessories add personality and finishing touches"
                }
            ]
            
            return priorities
            
        except Exception as e:
            logger.error(f"Error ranking recommendations: {e}")
            return []
    
    # Helper methods for specific recommendation types
    
    def _load_furniture_database(self) -> List[Dict]:
        """Load furniture database (would be from external source in production)"""
        # Simplified furniture database
        return [
            {
                "name": "Modern Sectional Sofa",
                "type": "sofa",
                "style": "modern",
                "dimensions": {"width": 2.5, "depth": 1.8, "height": 0.8},
                "price_range": "medium",
                "description": "Clean lines, neutral colors, comfortable seating",
                "materials": ["fabric", "metal"],
                "colors": ["gray", "beige", "navy"]
            },
            {
                "name": "Industrial Coffee Table",
                "type": "table",
                "style": "industrial",
                "dimensions": {"width": 1.2, "depth": 0.6, "height": 0.4},
                "price_range": "low",
                "description": "Metal frame with wood top, sturdy construction",
                "materials": ["metal", "wood"],
                "colors": ["black", "brown"]
            }
            # ... more furniture items would be loaded here
        ]
    
    def _load_color_database(self) -> Dict:
        """Load color harmony and psychology database"""
        return {
            "harmonies": {
                "complementary": {"description": "Colors opposite on color wheel"},
                "analogous": {"description": "Adjacent colors on color wheel"},
                "triadic": {"description": "Three evenly spaced colors"}
            },
            "psychology": {
                "blue": {"mood": "calm", "effect": "relaxing"},
                "red": {"mood": "energetic", "effect": "stimulating"},
                "green": {"mood": "natural", "effect": "refreshing"}
            }
        }
    
    def _load_style_templates(self) -> Dict:
        """Load design style templates"""
        return {
            "modern": {
                "colors": ["white", "gray", "black"],
                "materials": ["metal", "glass", "concrete"],
                "characteristics": ["clean lines", "minimal decoration"]
            },
            "traditional": {
                "colors": ["warm browns", "deep reds", "gold"],
                "materials": ["wood", "fabric", "leather"],
                "characteristics": ["ornate details", "classic patterns"]
            }
            # ... more style templates
        }
    
    def _calculate_aspect_ratio(self, dimensions: Dict) -> float:
        """Calculate room aspect ratio"""
        length = dimensions.get("estimated_length", 4)
        width = dimensions.get("estimated_width", 3.5)
        return length / width if width > 0 else 1.0
    
    def _get_dominant_hue(self, color_palette: Dict) -> float:
        """Get dominant hue from color palette"""
        dominant_colors = color_palette.get("dominant_colors", [])
        if dominant_colors:
            return dominant_colors[0].get("hsv", [0, 0, 0])[0]
        return 0
    
    def _calculate_space_density(self, room_analysis: Dict) -> float:
        """Calculate how densely furnished the space is"""
        objects = room_analysis.get("detected_objects", [])
        dimensions = room_analysis.get("room_dimensions", {})
        area = dimensions.get("estimated_length", 4) * dimensions.get("estimated_width", 3.5)
        return len(objects) / area if area > 0 else 0
    
    def _calculate_recommendation_confidence(self, recommendations: Dict, room_analysis: Dict) -> Dict:
        """Calculate confidence scores for different recommendation types"""
        base_confidence = room_analysis.get("confidence_scores", {}).get("overall", 0.7)
        
        return {
            "furniture": min(base_confidence + 0.1, 0.9),
            "colors": min(base_confidence + 0.2, 0.95),
            "layout": min(base_confidence, 0.8),
            "style": min(base_confidence - 0.1, 0.7),
            "lighting": min(base_confidence + 0.15, 0.85),
            "decor": min(base_confidence, 0.75)
        }
    
    # Placeholder methods for specific recommendation logic
    # These would contain the actual ML algorithms and business logic
    
    def _get_essential_furniture(self, room_area: float, existing: List[str]) -> List[str]:
        """Determine essential furniture based on room size and existing items"""
        essential = ["sofa", "coffee_table", "lighting"]
        return [item for item in essential if item not in existing]
    
    def _find_suitable_furniture(self, item_type: str, room_features: Dict, room_analysis: Dict) -> List[Dict]:
        """Find furniture items suitable for the room"""
        # Filter furniture database by type and suitability
        suitable = []
        for item in self.furniture_database:
            if item["type"] == item_type:
                # Add suitability scoring logic here
                item["suitability_score"] = 0.8  # Placeholder
                suitable.append(item)
        return suitable
    
    def _rank_furniture_items(self, items: List[Dict], room_features: Dict) -> List[Dict]:
        """Rank furniture items by suitability"""
        return sorted(items, key=lambda x: x.get("suitability_score", 0), reverse=True)
    
    def _generate_furniture_reasoning(self, item: Dict, room_features: Dict) -> str:
        """Generate explanation for furniture recommendation"""
        return f"This {item['name']} fits well with your {room_features.get('current_style', 'current')} style and room dimensions."
    
    def _suggest_placement(self, item: Dict, room_analysis: Dict) -> str:
        """Suggest optimal placement for furniture item"""
        return f"Place near the main seating area for optimal functionality."
    
    def _find_alternative_items(self, item: Dict, all_items: List[Dict]) -> List[Dict]:
        """Find alternative items similar to the recommended one"""
        return [alt for alt in all_items if alt != item][:2]
    
    # Additional placeholder methods for other recommendation types...
    # In a real implementation, these would contain sophisticated algorithms
    
    def _generate_complementary_colors(self, current_colors: List[Dict]) -> Dict:
        """Generate complementary color scheme"""
        return {"colors": ["#FF5733", "#33FF57"], "description": "Complementary color scheme"}
    
    def _generate_analogous_colors(self, current_colors: List[Dict]) -> Dict:
        """Generate analogous color scheme"""
        return {"colors": ["#FF5733", "#FF8C33"], "description": "Analogous color scheme"}
    
    def _generate_monochromatic_colors(self, current_colors: List[Dict]) -> Dict:
        """Generate monochromatic color scheme"""
        return {"colors": ["#FF5733", "#FF8C66"], "description": "Monochromatic color scheme"}
    
    def _generate_style_based_colors(self, style: str) -> Dict:
        """Generate colors based on design style"""
        style_colors = self.style_templates.get(style, {}).get("colors", ["white", "gray"])
        return {"colors": style_colors, "description": f"Colors for {style} style"}
    
    def _generate_lighting_optimized_colors(self, lighting_level: str) -> Dict:
        """Generate colors optimized for lighting conditions"""
        if lighting_level == "dim":
            return {"colors": ["#FFFFFF", "#F5F5F5"], "description": "Light colors to brighten the space"}
        return {"colors": ["#E0E0E0", "#D0D0D0"], "description": "Balanced colors for current lighting"}
    
    def _recommend_accent_colors(self, current_colors: List[Dict]) -> Dict:
        """Recommend accent colors"""
        return {"colors": ["#FF6B6B", "#4ECDC4"], "description": "Vibrant accent colors"}
    
    def _recommend_wall_colors(self, room_features: Dict) -> Dict:
        """Recommend wall colors"""
        return {"colors": ["#F8F8F8", "#E8E8E8"], "description": "Neutral wall colors"}
    
    def _analyze_color_psychology(self, colors: List[Dict]) -> Dict:
        """Analyze psychological effects of colors"""
        return {"mood": "calm", "energy": "moderate", "description": "Balanced psychological impact"}
    
    def _suggest_color_implementation(self, colors: List[str]) -> List[str]:
        """Suggest how to implement color scheme"""
        return ["Use as wall color", "Apply to accent pieces", "Incorporate through textiles"]
    
    def _calculate_color_confidence(self, scheme: Dict, room_features: Dict) -> float:
        """Calculate confidence for color recommendation"""
        return 0.8
    
    # More placeholder methods would continue here for layout, lighting, decor, etc.
    # Each would implement specific recommendation logic for their domain

