"""
People counting using YOLOv8 object detection
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeopleCounter:
    """Detects and counts people in video frames using YOLOv8"""
    
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5, classes: List[int] = None):
        """
        Initialize people counter (and object detector)
        
        Args:
            model_name: YOLOv8 model to use
            confidence_threshold: Minimum confidence
            classes: List of COCO class IDs to detect (Default: [0] for persons)
        """
        self.confidence_threshold = confidence_threshold
        self.classes = classes if classes is not None else [0]  # Default to person only
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
            # Run inference with tracking
            # persist=True is important for tracking to work across frames
            results = self.model.track(frame, persist=True, verbose=False, classes=self.classes, conf=self.confidence_threshold)
            
            detected_objects = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Get class ID
                    cls_id = int(box.cls[0])
                    # Get confidence
                    conf = float(box.conf[0])
                    
                    if conf >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get Track ID (if available)
                        track_id = int(box.id[0]) if box.id is not None else -1
                        
                        detected_objects.append({
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'class_id': cls_id,
                            'track_id': track_id,
                            'conf': conf
                        })
            
            return len(detected_objects), detected_objects
        
        except Exception as e:
            logger.error(f"Error in people counting: {e}")
            return 0, []
    
    def draw_detections(self, frame: np.ndarray, objects: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes on frame
        """
        output_frame = frame.copy()
        
        # Define colors for different classes
        colors = {
            0: (0, 255, 0),    # Person: Green
            67: (255, 0, 0),   # Cell phone: Blue
            56: (0, 0, 255)    # Chair: Red
        }
        
        names = self.model.names
        
        for obj in objects:
            x1, y1, x2, y2 = obj['bbox']
            cls_id = obj['class_id']
            track_id = obj['track_id']
            
            color = colors.get(cls_id, (255, 255, 255))
            
            # Draw rectangle
            cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{names[cls_id]}"
            if track_id != -1:
                label += f" #{track_id}"
                
            cv2.putText(output_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw count summary
        counts = {}
        for obj in objects:
            name = names[obj['class_id']]
            counts[name] = counts.get(name, 0) + 1
            
        y_offset = 30
        for name, count in counts.items():
            text = f"{name}: {count}"
            cv2.putText(output_frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            y_offset += 30
        
        return output_frame

    def get_person_centers(self, objects: List[Dict]) -> List[Tuple[int, int]]:
        """Get centers for persons only"""
        centers = []
        for obj in objects:
            if obj['class_id'] == 0: # Only persons
                x1, y1, x2, y2 = obj['bbox']
                centers.append(((x1 + x2) // 2, (y1 + y2) // 2))
        return centers
