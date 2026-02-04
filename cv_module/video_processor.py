"""
Main video processor that orchestrates all CV models
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
import threading
import time
from datetime import datetime, date
import logging

from .people_counter import PeopleCounter
from .gender_classifier import GenderClassifier
from .heatmap_generator import HeatmapGenerator
from .queue_detector import QueueDetector
from .dwell_time_tracker import DwellTimeTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoSource:
    """Represents a video source (camera or file)"""
    
    def __init__(self, source_id, source_type: str, name: str):
        """
        Initialize video source
        
        Args:
            source_id: Camera index or video file path
            source_type: 'webcam' or 'video'
            name: Descriptive name for this source
        """
        self.source_id = source_id
        self.source_type = source_type
        self.name = name
        self.cap = None
        self.is_active = False
    
    def start(self) -> bool:
        """Start video capture"""
        try:
            self.cap = cv2.VideoCapture(self.source_id)
            if self.cap.isOpened():
                self.is_active = True
                logger.info(f"Video source '{self.name}' started successfully")
                return True
            else:
                logger.error(f"Failed to open video source '{self.name}'")
                return False
        except Exception as e:
            logger.error(f"Error starting video source '{self.name}': {e}")
            return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the source"""
        if self.cap and self.is_active:
            return self.cap.read()
        return False, None
    
    def stop(self):
        """Stop video capture"""
        if self.cap:
            self.cap.release()
            self.is_active = False
            logger.info(f"Video source '{self.name}' stopped")
    
    def get_frame_size(self) -> Tuple[int, int]:
        """Get frame dimensions"""
        if self.cap and self.is_active:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return 640, 480


class VideoProcessor:
    """Main video processor that coordinates all CV models"""
    
    def __init__(self, db_manager):
        """
        Initialize video processor
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        
        # Initialize CV models
        # Classes: 0 (Person), 56 (Chair), 67 (Cell Phone)
        self.people_counter = PeopleCounter(classes=[0, 56, 67])
        self.gender_classifier = GenderClassifier()
        self.dwell_tracker = DwellTimeTracker(db_manager)
        
        # Video sources
        self.sources: Dict[str, VideoSource] = {}
        
        # Heatmap generators (one per source)
        self.heatmap_generators: Dict[str, HeatmapGenerator] = {}
        
        # Queue detector (for cashier camera)
        self.queue_detector = None
        
        # Processing threads
        self.processing_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        
        # Statistics
        self.stats = {
            'total_visitors': 0,
            'sections': {},
            'cashier': {}
        }
        
        # Frame storage for streaming
        self.latest_frames: Dict[str, bytes] = {}
        self.frame_lock = threading.Lock()
        
        logger.info("Video processor initialized")
    
    def add_source(self, source_id, source_type: str, name: str, role: str = "section"):
        """
        Add a video source
        
        Args:
            source_id: Camera index or video file path
            source_type: 'webcam' or 'video'
            name: Descriptive name
            role: 'entrance', 'section', or 'cashier'
        """
        source = VideoSource(source_id, source_type, name)
        if source.start():
            self.sources[name] = source
            
            # Initialize heatmap generator
            width, height = source.get_frame_size()
            self.heatmap_generators[name] = HeatmapGenerator(width, height)
            
            # Initialize queue detector for cashier
            if role == "cashier":
                # Define ROI for cashier area (can be adjusted)
                roi = (width // 4, height // 4, 3 * width // 4, 3 * height // 4)
                self.queue_detector = QueueDetector(roi=roi)
            
            logger.info(f"Added video source: {name} (role: {role})")
            return True
        return False
    
    def process_frame(self, frame: np.ndarray, source_name: str, role: str) -> Dict:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            source_name: Name of video source
            role: Source role (entrance, section, cashier)
        
        Returns:
            Dictionary with analytics data
        """
        # Count people and objects
        count, detected_objects = self.people_counter.count_people(frame)
        
        # Extract just person boxes for gender classifier/heatmap
        person_objects = [obj for obj in detected_objects if obj['class_id'] == 0]
        person_boxes = [obj['bbox'] for obj in person_objects]
        
        # Classify gender
        gender_data = self.gender_classifier.classify_gender(frame, person_boxes)
        
        # Update heatmap
        centers = self.people_counter.get_person_centers(detected_objects)
        heatmap_gen = self.heatmap_generators.get(source_name)
        if heatmap_gen:
            heatmap_gen.update(centers)
            zone_densities = heatmap_gen.get_zone_densities()
        else:
            zone_densities = {}
            
        # Update Dwell Time Tracker
        self.dwell_tracker.update(detected_objects, source_name, date.today(), datetime.now().hour)
        
        # Calculate object counts
        object_counts = {}
        names = self.people_counter.model.names
        for obj in detected_objects:
            name = names[obj['class_id']]
            object_counts[name] = object_counts.get(name, 0) + 1
        
        # Prepare analytics data
        analytics = {
            'source_name': source_name,
            'role': role,
            'count': len(person_boxes),
            'object_counts': object_counts,
            'male_count': gender_data['male'],
            'female_count': gender_data['female'],
            'heatmap_zones': zone_densities,
            'timestamp': datetime.now(),
            'date': date.today(),
            'hour': datetime.now().hour,
            'boxes': detected_objects  # Pass full object list for drawing
        }
        
        # Additional processing for cashier
        if role == "cashier" and self.queue_detector:
            # Only check queue len based on people
            queue_length = self.queue_detector.detect_queue(person_boxes)
            queue_analytics = self.queue_detector.get_queue_analytics(queue_length)
            analytics['queue'] = queue_analytics
        
        return analytics
    
    def get_latest_frame(self, source_name: str) -> bytes:
        """Get the latest processed frame for a source"""
        with self.frame_lock:
            return self.latest_frames.get(source_name)

    def save_analytics_to_db(self, analytics: Dict):
        """
        Save analytics data to database
        
        Args:
            analytics: Analytics dictionary
        """
        try:
            role = analytics['role']
            
            if role == "entrance":
                # Save visitor data
                self.db_manager.insert_visitor_data(
                    visitor_count=analytics['count'],
                    timestamp=analytics['timestamp'],
                    date_val=analytics['date'],
                    hour=analytics['hour']
                )
            
            elif role == "section":
                # Save section analytics
                self.db_manager.insert_section_analytics(
                    section_name=analytics['source_name'],
                    visitor_count=analytics['count'],
                    male_count=analytics['male_count'],
                    female_count=analytics['female_count'],
                    heatmap_data=analytics['heatmap_zones'],
                    object_counts=analytics['object_counts'],
                    timestamp=analytics['timestamp'],
                    date_val=analytics['date'],
                    hour=analytics['hour']
                )
            
            elif role == "cashier":
                # Save cashier analytics
                queue_data = analytics.get('queue', {})
                self.db_manager.insert_cashier_analytics(
                    queue_length=queue_data.get('current_queue_length', 0),
                    estimated_wait_time=queue_data.get('estimated_wait_time', 0.0),
                    is_busy=queue_data.get('is_busy', False),
                    estimated_transactions=queue_data.get('estimated_transactions', 0),
                    timestamp=analytics['timestamp'],
                    date_val=analytics['date'],
                    hour=analytics['hour']
                )
        
        except Exception as e:
            logger.error(f"Error saving analytics to database: {e}")
    
    def process_source(self, source_name: str, role: str, save_interval: int = 30):
        """
        Process video source in a loop
        
        Args:
            source_name: Name of video source
            role: Source role
            save_interval: Interval (in frames) to save data to database
        """
        source = self.sources.get(source_name)
        if not source:
            logger.error(f"Source '{source_name}' not found")
            return
        
        stop_flag = self.stop_flags[source_name]
        frame_count = 0
        
        logger.info(f"Started processing source: {source_name}")
        
        while not stop_flag.is_set():
            ret, frame = source.read()
            
            if not ret:
                if source.source_type == "video":
                    # Restart video file
                    source.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    logger.warning(f"Failed to read frame from {source_name}")
                    break
            
            # Process frame
            analytics = self.process_frame(frame, source_name, role)
            
            # Draw detections and update frame storage
            annotated_frame = self.people_counter.draw_detections(frame, analytics.get('boxes', []))
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if ret:
                with self.frame_lock:
                    self.latest_frames[source_name] = buffer.tobytes()
            
            # Save to database periodically
            if frame_count % save_interval == 0:
                self.save_analytics_to_db(analytics)
            
            frame_count += 1
            
            # Small delay to prevent overwhelming the system
            time.sleep(0.033)  # ~30 FPS
        
        logger.info(f"Stopped processing source: {source_name}")
    
    def start_processing(self, source_name: str, role: str):
        """
        Start processing a video source in a separate thread
        
        Args:
            source_name: Name of video source
            role: Source role
        """
        if source_name not in self.sources:
            logger.error(f"Source '{source_name}' not found")
            return
        
        # Create stop flag
        self.stop_flags[source_name] = threading.Event()
        
        # Create and start thread
        thread = threading.Thread(
            target=self.process_source,
            args=(source_name, role),
            daemon=True
        )
        self.processing_threads[source_name] = thread
        thread.start()
        
        logger.info(f"Started processing thread for: {source_name}")
    
    def stop_processing(self, source_name: str):
        """Stop processing a video source"""
        if source_name in self.stop_flags:
            self.stop_flags[source_name].set()
        
        if source_name in self.processing_threads:
            self.processing_threads[source_name].join(timeout=5)
    
    def stop_all(self):
        """Stop all video processing"""
        logger.info("Stopping all video processing...")
        
        for source_name in list(self.sources.keys()):
            self.stop_processing(source_name)
            self.sources[source_name].stop()
        
        logger.info("All video processing stopped")
