"""
Gender classification using DeepFace
"""
import cv2
import numpy as np
from typing import List, Tuple, Dict
import logging

# DeepFace can be slow, so we'll use a simpler approach with pre-trained models
# For production, you might want to use DeepFace or a custom model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenderClassifier:
    """Classifies gender of detected people"""
    
    def __init__(self):
        """Initialize gender classifier"""
        try:
            # Using OpenCV's DNN module with pre-trained gender model
            # You can download these models from:
            # https://github.com/GilLevi/AgeGenderDeepLearning
            
            # For now, we'll use a simplified approach
            # In production, load actual gender classification model
            self.model_loaded = False
            logger.info("Gender classifier initialized (using simplified detection)")
            
        except Exception as e:
            logger.error(f"Failed to initialize gender classifier: {e}")
            self.model_loaded = False
    
    def classify_gender(self, frame: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> Dict[str, int]:
        """
        Classify gender for detected people
        
        Args:
            frame: Input video frame
            boxes: List of bounding boxes for detected people
        
        Returns:
            Dictionary with counts: {'male': count, 'female': count}
        """
        try:
            # Simplified gender detection for demo
            # In production, use actual gender classification model
            
            male_count = 0
            female_count = 0
            
            for box in boxes:
                x1, y1, x2, y2 = box
                
                # Extract person ROI
                person_roi = frame[y1:y2, x1:x2]
                
                if person_roi.size == 0:
                    continue
                
                # Simplified heuristic (for demo purposes)
                # In production, use actual model inference
                # This is just a placeholder that randomly assigns gender
                avg_color = np.mean(person_roi)
                
                # Simple heuristic based on image properties
                # This is NOT accurate and should be replaced with actual model
                if avg_color > 127:
                    male_count += 1
                else:
                    female_count += 1
            
            return {
                'male': male_count,
                'female': female_count
            }
        
        except Exception as e:
            logger.error(f"Error in gender classification: {e}")
            return {'male': 0, 'female': 0}
    
    def classify_with_deepface(self, frame: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> Dict[str, int]:
        """
        Alternative method using DeepFace (more accurate but slower)
        
        Args:
            frame: Input video frame
            boxes: List of bounding boxes
        
        Returns:
            Dictionary with gender counts
        """
        try:
            from deepface import DeepFace
            
            male_count = 0
            female_count = 0
            
            for box in boxes:
                x1, y1, x2, y2 = box
                person_roi = frame[y1:y2, x1:x2]
                
                if person_roi.size == 0:
                    continue
                
                try:
                    # Analyze gender using DeepFace
                    result = DeepFace.analyze(person_roi, actions=['gender'], enforce_detection=False)
                    
                    if isinstance(result, list):
                        result = result[0]
                    
                    gender = result.get('dominant_gender', 'Man')
                    
                    if gender == 'Man':
                        male_count += 1
                    else:
                        female_count += 1
                
                except Exception as e:
                    logger.debug(f"DeepFace analysis failed for one person: {e}")
                    # Default to male if detection fails
                    male_count += 1
            
            return {
                'male': male_count,
                'female': female_count
            }
        
        except ImportError:
            logger.warning("DeepFace not available, using simplified method")
            return self.classify_gender(frame, boxes)
        except Exception as e:
            logger.error(f"Error in DeepFace classification: {e}")
            return {'male': 0, 'female': 0}
