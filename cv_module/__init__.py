"""Computer Vision module initialization"""
from .people_counter import PeopleCounter
from .gender_classifier import GenderClassifier
from .heatmap_generator import HeatmapGenerator
from .queue_detector import QueueDetector
from .video_processor import VideoProcessor, VideoSource

__all__ = [
    'PeopleCounter',
    'GenderClassifier',
    'HeatmapGenerator',
    'QueueDetector',
    'VideoProcessor',
    'VideoSource'
]
