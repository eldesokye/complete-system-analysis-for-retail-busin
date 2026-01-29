"""
Heatmap generation for tracking movement patterns
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """Generates heatmaps showing movement density and patterns"""
    
    def __init__(self, frame_width: int, frame_height: int, history_size: int = 100):
        """
        Initialize heatmap generator
        
        Args:
            frame_width: Width of video frame
            frame_height: Height of video frame
            history_size: Number of frames to keep in history
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.history_size = history_size
        
        # Initialize heatmap accumulator
        self.heatmap = np.zeros((frame_height, frame_width), dtype=np.float32)
        
        # Track position history
        self.position_history = deque(maxlen=history_size)
        
        logger.info(f"Heatmap generator initialized ({frame_width}x{frame_height})")
    
    def update(self, centers: List[Tuple[int, int]]):
        """
        Update heatmap with new person positions
        
        Args:
            centers: List of (x, y) center coordinates of detected people
        """
        # Add current positions to history
        self.position_history.append(centers)
        
        # Decay existing heatmap
        self.heatmap *= 0.95
        
        # Add new positions
        for x, y in centers:
            if 0 <= x < self.frame_width and 0 <= y < self.frame_height:
                # Add Gaussian blob around each person
                cv2.circle(self.heatmap, (x, y), 30, 1.0, -1)
    
    def get_heatmap_image(self) -> np.ndarray:
        """
        Get heatmap as colored image
        
        Returns:
            Heatmap visualization (BGR format)
        """
        # Normalize heatmap
        normalized = cv2.normalize(self.heatmap, None, 0, 255, cv2.NORM_MINMAX)
        normalized = normalized.astype(np.uint8)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
        
        return heatmap_colored
    
    def get_heatmap_overlay(self, frame: np.ndarray, alpha: float = 0.6) -> np.ndarray:
        """
        Overlay heatmap on original frame
        
        Args:
            frame: Original video frame
            alpha: Transparency of heatmap overlay (0-1)
        
        Returns:
            Frame with heatmap overlay
        """
        heatmap_colored = self.get_heatmap_image()
        
        # Blend with original frame
        overlay = cv2.addWeighted(frame, 1 - alpha, heatmap_colored, alpha, 0)
        
        return overlay
    
    def get_zone_densities(self, num_zones: int = 9) -> Dict[str, int]:
        """
        Divide frame into zones and calculate density for each
        
        Args:
            num_zones: Number of zones (must be perfect square: 4, 9, 16, etc.)
        
        Returns:
            Dictionary mapping zone names to density values
        """
        grid_size = int(np.sqrt(num_zones))
        zone_height = self.frame_height // grid_size
        zone_width = self.frame_width // grid_size
        
        zones = {}
        
        for i in range(grid_size):
            for j in range(grid_size):
                zone_name = f"zone_{i}_{j}"
                
                # Extract zone from heatmap
                y1 = i * zone_height
                y2 = (i + 1) * zone_height
                x1 = j * zone_width
                x2 = (j + 1) * zone_width
                
                zone_data = self.heatmap[y1:y2, x1:x2]
                
                # Calculate average density
                density = int(np.mean(zone_data) * 100)
                zones[zone_name] = density
        
        return zones
    
    def get_hotspots(self, threshold: float = 0.7) -> List[Tuple[int, int]]:
        """
        Get coordinates of high-density hotspots
        
        Args:
            threshold: Minimum normalized value to be considered a hotspot
        
        Returns:
            List of (x, y) coordinates of hotspots
        """
        # Normalize heatmap
        normalized = cv2.normalize(self.heatmap, None, 0, 1, cv2.NORM_MINMAX)
        
        # Find hotspots
        hotspot_mask = normalized > threshold
        hotspot_coords = np.argwhere(hotspot_mask)
        
        # Convert to (x, y) format
        hotspots = [(int(coord[1]), int(coord[0])) for coord in hotspot_coords]
        
        return hotspots
    
    def reset(self):
        """Reset heatmap accumulator"""
        self.heatmap = np.zeros((self.frame_height, self.frame_width), dtype=np.float32)
        self.position_history.clear()
        logger.info("Heatmap reset")
