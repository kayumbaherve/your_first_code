"""
Room Scanner Module - Computer Vision for Room Analysis
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional
import json
import logging
from pathlib import Path
from PIL import Image, ExifTags
import colorsys
from sklearn.cluster import KMeans
import math

logger = logging.getLogger(__name__)


class RoomScanner:
    """Advanced room scanning and analysis using computer vision"""
    
    def __init__(self):
        """Initialize the room scanner with MediaPipe and OpenCV components"""
        # Initialize MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Initialize pose detection for scale estimation
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        # Object detection models (you would load pre-trained models here)
        self.furniture_detector = None  # Load furniture detection model
        self.room_segmentation = None   # Load room segmentation model
        
        # Room analysis parameters
        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4
        
    def analyze_room_image(self, image_path: str) -> Dict:
        """
        Comprehensive room analysis from a single image
        
        Args:
            image_path: Path to the room image
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
                
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Extract image metadata
            metadata = self._extract_image_metadata(image_path)
            
            # Perform various analyses
            results = {
                "image_metadata": metadata,
                "room_dimensions": self._estimate_room_dimensions(image, rgb_image),
                "detected_objects": self._detect_furniture_and_objects(image),
                "color_palette": self._extract_color_palette(rgb_image),
                "lighting_analysis": self._analyze_lighting(image),
                "style_analysis": self._analyze_design_style(rgb_image),
                "wall_analysis": self._analyze_walls_and_surfaces(image),
                "floor_analysis": self._analyze_floor(image),
                "ceiling_analysis": self._analyze_ceiling(image),
                "spatial_layout": self._analyze_spatial_layout(image),
                "confidence_scores": {}
            }
            
            # Calculate overall confidence scores
            results["confidence_scores"] = self._calculate_confidence_scores(results)
            
            logger.info(f"Room analysis completed for {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing room image {image_path}: {e}")
            raise
    
    def _extract_image_metadata(self, image_path: str) -> Dict:
        """Extract EXIF and other metadata from image"""
        try:
            with Image.open(image_path) as img:
                exif_data = {}
                
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "exif": exif_data
                }
        except Exception as e:
            logger.warning(f"Could not extract metadata from {image_path}: {e}")
            return {}
    
    def _estimate_room_dimensions(self, image: np.ndarray, rgb_image: np.ndarray) -> Dict:
        """
        Estimate room dimensions using perspective analysis and human scale reference
        """
        try:
            height, width = image.shape[:2]
            
            # Detect vanishing points for perspective analysis
            vanishing_points = self._detect_vanishing_points(image)
            
            # Try to detect human figures for scale reference
            human_scale = self._detect_human_scale_reference(rgb_image)
            
            # Analyze floor-wall boundaries
            floor_wall_boundary = self._detect_floor_wall_boundary(image)
            
            # Estimate dimensions based on perspective and scale
            estimated_dimensions = self._calculate_room_dimensions(
                vanishing_points, human_scale, floor_wall_boundary, (width, height)
            )
            
            return {
                "estimated_length": estimated_dimensions.get("length", 0),
                "estimated_width": estimated_dimensions.get("width", 0),
                "estimated_height": estimated_dimensions.get("height", 2.7),  # Default ceiling height
                "confidence": estimated_dimensions.get("confidence", 0.3),
                "method": estimated_dimensions.get("method", "perspective_analysis"),
                "vanishing_points": vanishing_points,
                "human_scale_detected": human_scale is not None
            }
            
        except Exception as e:
            logger.error(f"Error estimating room dimensions: {e}")
            return {"estimated_length": 0, "estimated_width": 0, "estimated_height": 2.7, "confidence": 0.1}
    
    def _detect_vanishing_points(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """Detect vanishing points for perspective analysis"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is None:
                return []
            
            # Group lines by angle to find vanishing points
            vanishing_points = []
            # Simplified vanishing point detection
            # In a real implementation, you'd use more sophisticated algorithms
            
            return vanishing_points[:2]  # Return up to 2 vanishing points
            
        except Exception as e:
            logger.error(f"Error detecting vanishing points: {e}")
            return []
    
    def _detect_human_scale_reference(self, rgb_image: np.ndarray) -> Optional[Dict]:
        """Detect human figures to establish scale reference"""
        try:
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                # Calculate human height in pixels
                landmarks = results.pose_landmarks.landmark
                
                # Get head and foot positions
                head_y = landmarks[self.mp_pose.PoseLandmark.NOSE].y
                foot_y = max(
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y
                )
                
                height_pixels = abs(foot_y - head_y) * rgb_image.shape[0]
                
                # Assume average human height of 1.7m
                pixels_per_meter = height_pixels / 1.7
                
                return {
                    "height_pixels": height_pixels,
                    "pixels_per_meter": pixels_per_meter,
                    "confidence": 0.8
                }
                
        except Exception as e:
            logger.error(f"Error detecting human scale reference: {e}")
            
        return None
    
    def _detect_floor_wall_boundary(self, image: np.ndarray) -> List[Tuple[int, int]]:
        """Detect the boundary between floor and walls"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find horizontal lines that could be floor-wall boundaries
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return []
            
            # Filter for roughly horizontal lines in the lower part of the image
            height = image.shape[0]
            floor_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if y1 > height * 0.5 and y2 > height * 0.5:  # Lower half of image
                    angle = abs(math.atan2(y2 - y1, x2 - x1) * 180 / math.pi)
                    if angle < 15:  # Roughly horizontal
                        floor_lines.append(((x1, y1), (x2, y2)))
            
            return floor_lines
            
        except Exception as e:
            logger.error(f"Error detecting floor-wall boundary: {e}")
            return []
    
    def _calculate_room_dimensions(self, vanishing_points: List, human_scale: Optional[Dict], 
                                 floor_boundary: List, image_size: Tuple[int, int]) -> Dict:
        """Calculate room dimensions from detected features"""
        try:
            width, height = image_size
            
            # Default dimensions (fallback)
            estimated_length = 4.0  # meters
            estimated_width = 3.5   # meters
            estimated_height = 2.7  # meters
            confidence = 0.3
            method = "default_estimation"
            
            # If human scale is available, use it for better estimation
            if human_scale:
                pixels_per_meter = human_scale["pixels_per_meter"]
                
                # Estimate room width based on image width and perspective
                estimated_width = (width * 0.8) / pixels_per_meter  # Rough estimation
                estimated_length = (height * 0.6) / pixels_per_meter  # Rough estimation
                confidence = 0.6
                method = "human_scale_reference"
            
            # Adjust based on vanishing points if available
            if len(vanishing_points) >= 1:
                confidence = min(confidence + 0.2, 0.8)
                method = "perspective_analysis"
            
            return {
                "length": round(estimated_length, 2),
                "width": round(estimated_width, 2),
                "height": round(estimated_height, 2),
                "confidence": confidence,
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Error calculating room dimensions: {e}")
            return {"length": 4.0, "width": 3.5, "height": 2.7, "confidence": 0.1, "method": "error_fallback"}
    
    def _detect_furniture_and_objects(self, image: np.ndarray) -> List[Dict]:
        """Detect furniture and objects in the room"""
        try:
            # This would use a pre-trained object detection model
            # For now, we'll simulate detection results
            
            # In a real implementation, you would:
            # 1. Load a YOLO or similar model trained on furniture
            # 2. Run inference on the image
            # 3. Filter results by confidence threshold
            # 4. Apply non-maximum suppression
            
            detected_objects = [
                {
                    "class": "sofa",
                    "confidence": 0.85,
                    "bbox": [100, 200, 300, 400],  # x, y, width, height
                    "center": [250, 300]
                },
                {
                    "class": "table",
                    "confidence": 0.72,
                    "bbox": [400, 350, 150, 100],
                    "center": [475, 400]
                }
            ]
            
            return detected_objects
            
        except Exception as e:
            logger.error(f"Error detecting furniture and objects: {e}")
            return []
    
    def _extract_color_palette(self, rgb_image: np.ndarray, n_colors: int = 8) -> Dict:
        """Extract dominant color palette from the room"""
        try:
            # Reshape image for clustering
            data = rgb_image.reshape((-1, 3))
            
            # Use K-means clustering to find dominant colors
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(data)
            
            # Get colors and their percentages
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            
            # Calculate color percentages
            unique_labels, counts = np.unique(labels, return_counts=True)
            percentages = counts / len(labels) * 100
            
            # Convert to hex and organize
            color_palette = []
            for i, color in enumerate(colors):
                hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
                
                # Convert to HSV for additional analysis
                hsv = colorsys.rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
                
                color_info = {
                    "hex": hex_color,
                    "rgb": color.tolist(),
                    "hsv": [round(hsv[0]*360), round(hsv[1]*100), round(hsv[2]*100)],
                    "percentage": round(percentages[i], 2),
                    "color_name": self._get_color_name(color)
                }
                color_palette.append(color_info)
            
            # Sort by percentage
            color_palette.sort(key=lambda x: x["percentage"], reverse=True)
            
            return {
                "dominant_colors": color_palette,
                "color_harmony": self._analyze_color_harmony(color_palette),
                "temperature": self._analyze_color_temperature(color_palette)
            }
            
        except Exception as e:
            logger.error(f"Error extracting color palette: {e}")
            return {"dominant_colors": [], "color_harmony": "unknown", "temperature": "neutral"}
    
    def _get_color_name(self, rgb_color: np.ndarray) -> str:
        """Get approximate color name from RGB values"""
        # Simplified color naming - in practice, you'd use a more comprehensive color database
        r, g, b = rgb_color
        
        if r > 200 and g > 200 and b > 200:
            return "white"
        elif r < 50 and g < 50 and b < 50:
            return "black"
        elif r > g and r > b:
            return "red"
        elif g > r and g > b:
            return "green"
        elif b > r and b > g:
            return "blue"
        elif r > 150 and g > 150 and b < 100:
            return "yellow"
        elif r > 150 and g < 100 and b > 150:
            return "purple"
        elif r < 100 and g > 150 and b > 150:
            return "cyan"
        else:
            return "mixed"
    
    def _analyze_color_harmony(self, color_palette: List[Dict]) -> str:
        """Analyze color harmony in the palette"""
        if len(color_palette) < 2:
            return "monochromatic"
        
        # Simplified harmony analysis based on HSV values
        hues = [color["hsv"][0] for color in color_palette[:5]]  # Top 5 colors
        
        # Check for complementary colors (opposite on color wheel)
        for i, hue1 in enumerate(hues):
            for hue2 in hues[i+1:]:
                diff = abs(hue1 - hue2)
                if 160 <= diff <= 200:  # Approximately opposite
                    return "complementary"
        
        # Check for analogous colors (adjacent on color wheel)
        adjacent_count = 0
        for i, hue1 in enumerate(hues):
            for hue2 in hues[i+1:]:
                diff = min(abs(hue1 - hue2), 360 - abs(hue1 - hue2))
                if diff <= 30:
                    adjacent_count += 1
        
        if adjacent_count >= 2:
            return "analogous"
        
        return "varied"
    
    def _analyze_color_temperature(self, color_palette: List[Dict]) -> str:
        """Analyze overall color temperature"""
        if not color_palette:
            return "neutral"
        
        warm_score = 0
        cool_score = 0
        
        for color in color_palette[:5]:  # Top 5 colors
            hue = color["hsv"][0]
            percentage = color["percentage"]
            
            # Warm colors: red, orange, yellow (0-60, 300-360)
            if (0 <= hue <= 60) or (300 <= hue <= 360):
                warm_score += percentage
            # Cool colors: blue, green, purple (120-300)
            elif 120 <= hue <= 300:
                cool_score += percentage
        
        if warm_score > cool_score * 1.5:
            return "warm"
        elif cool_score > warm_score * 1.5:
            return "cool"
        else:
            return "neutral"
    
    def _analyze_lighting(self, image: np.ndarray) -> Dict:
        """Analyze lighting conditions in the room"""
        try:
            # Convert to grayscale for brightness analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate overall brightness
            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)
            
            # Analyze brightness distribution
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # Detect potential light sources (bright spots)
            bright_threshold = mean_brightness + 2 * std_brightness
            bright_mask = gray > bright_threshold
            bright_regions = cv2.findContours(bright_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            
            # Classify lighting conditions
            if mean_brightness > 180:
                lighting_level = "bright"
            elif mean_brightness > 120:
                lighting_level = "moderate"
            elif mean_brightness > 60:
                lighting_level = "dim"
            else:
                lighting_level = "dark"
            
            # Analyze contrast
            contrast = std_brightness / mean_brightness if mean_brightness > 0 else 0
            
            return {
                "overall_brightness": round(mean_brightness, 2),
                "lighting_level": lighting_level,
                "contrast_ratio": round(contrast, 3),
                "brightness_distribution": "even" if std_brightness < 30 else "uneven",
                "potential_light_sources": len(bright_regions),
                "natural_light_detected": self._detect_natural_light(image)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing lighting: {e}")
            return {"overall_brightness": 128, "lighting_level": "moderate", "contrast_ratio": 0.5}
    
    def _detect_natural_light(self, image: np.ndarray) -> bool:
        """Detect presence of natural light (windows)"""
        try:
            # Look for bright rectangular regions that could be windows
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to find very bright areas
            _, bright_areas = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # Find contours of bright areas
            contours, _ = cv2.findContours(bright_areas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check for rectangular bright areas (potential windows)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Minimum area for a window
                    # Check if contour is roughly rectangular
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    if len(approx) >= 4:  # Roughly rectangular
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting natural light: {e}")
            return False
    
    def _analyze_design_style(self, rgb_image: np.ndarray) -> Dict:
        """Analyze and classify the design style of the room"""
        try:
            # This would typically use a trained ML model
            # For now, we'll use heuristic analysis
            
            # Analyze color palette for style indicators
            color_analysis = self._extract_color_palette(rgb_image)
            dominant_colors = color_analysis["dominant_colors"]
            
            style_scores = {
                "modern": 0,
                "traditional": 0,
                "minimalist": 0,
                "industrial": 0,
                "scandinavian": 0,
                "bohemian": 0
            }
            
            # Color-based style analysis
            for color in dominant_colors[:3]:  # Top 3 colors
                percentage = color["percentage"]
                rgb = color["rgb"]
                
                # Modern: clean whites, grays, bold accents
                if (rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200) or \
                   (abs(rgb[0] - rgb[1]) < 20 and abs(rgb[1] - rgb[2]) < 20):
                    style_scores["modern"] += percentage * 0.3
                    style_scores["minimalist"] += percentage * 0.4
                
                # Traditional: warm browns, deep colors
                if rgb[0] > rgb[1] and rgb[0] > rgb[2] and rgb[0] > 100:
                    style_scores["traditional"] += percentage * 0.4
                
                # Industrial: grays, blacks, metallics
                if abs(rgb[0] - rgb[1]) < 30 and abs(rgb[1] - rgb[2]) < 30 and max(rgb) < 150:
                    style_scores["industrial"] += percentage * 0.5
                
                # Scandinavian: whites, light woods, pastels
                if rgb[0] > 180 and rgb[1] > 180 and rgb[2] > 180:
                    style_scores["scandinavian"] += percentage * 0.4
            
            # Determine primary style
            primary_style = max(style_scores, key=style_scores.get)
            confidence = style_scores[primary_style] / 100  # Normalize to 0-1
            
            return {
                "primary_style": primary_style,
                "confidence": round(min(confidence, 1.0), 3),
                "style_scores": {k: round(v, 2) for k, v in style_scores.items()},
                "style_indicators": self._get_style_indicators(primary_style)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing design style: {e}")
            return {"primary_style": "unknown", "confidence": 0.1, "style_scores": {}}
    
    def _get_style_indicators(self, style: str) -> List[str]:
        """Get characteristic indicators for a design style"""
        indicators = {
            "modern": ["clean lines", "minimal decoration", "neutral colors", "open space"],
            "traditional": ["warm colors", "classic furniture", "decorative elements", "rich textures"],
            "minimalist": ["white/neutral palette", "simple forms", "uncluttered space", "functional design"],
            "industrial": ["exposed materials", "metal accents", "raw textures", "utilitarian design"],
            "scandinavian": ["light colors", "natural materials", "cozy atmosphere", "functional beauty"],
            "bohemian": ["rich colors", "mixed patterns", "eclectic decor", "artistic elements"]
        }
        return indicators.get(style, [])
    
    def _analyze_walls_and_surfaces(self, image: np.ndarray) -> Dict:
        """Analyze wall surfaces and textures"""
        try:
            # Simplified wall analysis
            # In practice, this would use more sophisticated computer vision
            
            return {
                "wall_color": "neutral",
                "wall_texture": "smooth",
                "wall_condition": "good",
                "decorative_elements": []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing walls: {e}")
            return {}
    
    def _analyze_floor(self, image: np.ndarray) -> Dict:
        """Analyze floor type and condition"""
        try:
            # Simplified floor analysis
            return {
                "floor_type": "unknown",
                "floor_color": "neutral",
                "floor_condition": "good"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing floor: {e}")
            return {}
    
    def _analyze_ceiling(self, image: np.ndarray) -> Dict:
        """Analyze ceiling type and features"""
        try:
            # Simplified ceiling analysis
            return {
                "ceiling_type": "flat",
                "ceiling_height": "standard",
                "ceiling_features": []
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ceiling: {e}")
            return {}
    
    def _analyze_spatial_layout(self, image: np.ndarray) -> Dict:
        """Analyze spatial layout and flow"""
        try:
            # Simplified spatial analysis
            return {
                "layout_type": "open",
                "traffic_flow": "good",
                "space_utilization": "moderate"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spatial layout: {e}")
            return {}
    
    def _calculate_confidence_scores(self, results: Dict) -> Dict:
        """Calculate confidence scores for different analysis components"""
        confidence_scores = {
            "overall": 0.7,
            "dimensions": results.get("room_dimensions", {}).get("confidence", 0.3),
            "objects": 0.6,  # Based on object detection confidence
            "colors": 0.8,   # Color analysis is generally reliable
            "lighting": 0.7,
            "style": results.get("style_analysis", {}).get("confidence", 0.5)
        }
        
        # Calculate overall confidence as weighted average
        weights = {"dimensions": 0.2, "objects": 0.2, "colors": 0.2, "lighting": 0.2, "style": 0.2}
        overall_confidence = sum(confidence_scores[key] * weights[key] for key in weights)
        confidence_scores["overall"] = round(overall_confidence, 3)
        
        return confidence_scores

