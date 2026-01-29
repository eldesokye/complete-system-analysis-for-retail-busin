"""
People counting using YOLOv8 object detection
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeopleCounter:
    """Detects and counts people in video frames using YOLOv8"""
    
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        """
        Initialize people counter
        
        Args:
            model_name: YOLOv8 model to use (yolov8n, yolov8s, yolov8m, etc.)
            confidence_threshold: Minimum confidence for detection
        """
        self.confidence_threshold = confidence_threshold
        try:
            self.model = YOLO(model_name)
            logger.info(f"YOLOv8 model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise
    
    def count_people(self, frame: np.ndarray) -> Tuple[int, List[Tuple[int, int, int, int]]]:
        """
        Count people in a frame
        
        Args:
            frame: Input video frame (BGR format)
        
        Returns:
            Tuple of (count, bounding_boxes)
            - count: Number of people detected
            - bounding_boxes: List of (x1, y1, x2, y2) coordinates
        """
        try:
            # Run inference
            results = self.model(frame, verbose=False)
            
            people_boxes = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Class 0 is 'person' in COCO dataset
                    if int(box.cls[0]) == 0 and float(box.conf[0]) >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        people_boxes.append((int(x1), int(y1), int(x2), int(y2)))
            
            return len(people_boxes), people_boxes
        
        except Exception as e:
            logger.error(f"Error in people counting: {e}")
            return 0, []
    
    def draw_detections(self, frame: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Draw bounding boxes on frame
        
        Args:
            frame: Input frame
            boxes: List of bounding boxes
        
        Returns:
            Frame with drawn boxes
        """
        output_frame = frame.copy()
        
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            # Draw rectangle
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"Person {i+1}"
            cv2.putText(output_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw count
        count_text = f"People Count: {len(boxes)}"
        cv2.putText(output_frame, count_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return output_frame
    
    def get_person_centers(self, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int]]:
        """
        Get center points of detected people
        
        Args:
            boxes: List of bounding boxes
        
        Returns:
            List of (x, y) center coordinates
        """
        centers = []
        for x1, y1, x2, y2 in boxes:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            centers.append((center_x, center_y))
        return centers
