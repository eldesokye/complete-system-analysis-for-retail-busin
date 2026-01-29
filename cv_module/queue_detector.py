"""
Queue detection and wait time estimation for cashier
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
from collections import deque
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueDetector:
    """Detects queue length and estimates wait times at cashier"""
    
    def __init__(self, roi: Tuple[int, int, int, int] = None, avg_service_time: float = 120.0):
        """
        Initialize queue detector
        
        Args:
            roi: Region of interest (x1, y1, x2, y2) for cashier area
            avg_service_time: Average service time per customer in seconds
        """
        self.roi = roi  # Region of interest for cashier area
        self.avg_service_time = avg_service_time
        
        # Track queue history
        self.queue_history = deque(maxlen=30)
        
        # Track transaction estimation
        self.last_queue_size = 0
        self.transaction_count = 0
        self.last_transaction_time = time.time()
        
        logger.info("Queue detector initialized")
    
    def detect_queue(self, boxes: List[Tuple[int, int, int, int]]) -> int:
        """
        Detect number of people in queue
        
        Args:
            boxes: List of bounding boxes for all detected people
        
        Returns:
            Number of people in queue
        """
        if self.roi is None:
            # If no ROI specified, count all people
            return len(boxes)
        
        roi_x1, roi_y1, roi_x2, roi_y2 = self.roi
        queue_count = 0
        
        # Count people whose centers are within ROI
        for x1, y1, x2, y2 in boxes:
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            if roi_x1 <= center_x <= roi_x2 and roi_y1 <= center_y <= roi_y2:
                queue_count += 1
        
        # Update history
        self.queue_history.append(queue_count)
        
        return queue_count
    
    def estimate_wait_time(self, queue_length: int) -> float:
        """
        Estimate wait time based on queue length
        
        Args:
            queue_length: Current queue length
        
        Returns:
            Estimated wait time in seconds
        """
        return queue_length * self.avg_service_time
    
    def is_busy(self, queue_length: int, threshold: int = 3) -> bool:
        """
        Determine if cashier is busy
        
        Args:
            queue_length: Current queue length
            threshold: Minimum queue length to be considered busy
        
        Returns:
            True if busy, False otherwise
        """
        return queue_length >= threshold
    
    def estimate_transactions(self) -> int:
        """
        Estimate number of transactions based on queue changes
        
        Returns:
            Estimated number of transactions
        """
        if len(self.queue_history) < 2:
            return 0
        
        current_time = time.time()
        current_queue = self.queue_history[-1]
        
        # Detect transaction (queue decreased)
        if current_queue < self.last_queue_size:
            # Check if enough time has passed for a transaction
            time_elapsed = current_time - self.last_transaction_time
            if time_elapsed >= self.avg_service_time * 0.5:  # At least half the avg service time
                self.transaction_count += 1
                self.last_transaction_time = current_time
        
        self.last_queue_size = current_queue
        
        return self.transaction_count
    
    def get_average_queue_length(self) -> float:
        """
        Get average queue length over recent history
        
        Returns:
            Average queue length
        """
        if not self.queue_history:
            return 0.0
        return sum(self.queue_history) / len(self.queue_history)
    
    def draw_roi(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw ROI on frame
        
        Args:
            frame: Input frame
        
        Returns:
            Frame with ROI drawn
        """
        if self.roi is None:
            return frame
        
        output = frame.copy()
        x1, y1, x2, y2 = self.roi
        
        # Draw ROI rectangle
        cv2.rectangle(output, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
        # Draw label
        cv2.putText(output, "Cashier Area", (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return output
    
    def get_queue_analytics(self, queue_length: int) -> Dict:
        """
        Get comprehensive queue analytics
        
        Args:
            queue_length: Current queue length
        
        Returns:
            Dictionary with queue analytics
        """
        return {
            'current_queue_length': queue_length,
            'average_queue_length': self.get_average_queue_length(),
            'estimated_wait_time': self.estimate_wait_time(queue_length),
            'is_busy': self.is_busy(queue_length),
            'estimated_transactions': self.estimate_transactions()
        }
    
    def reset_transactions(self):
        """Reset transaction counter"""
        self.transaction_count = 0
        self.last_transaction_time = time.time()
