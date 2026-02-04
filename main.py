"""
Main application entry point
Orchestrates CV processing and FastAPI server
"""
import uvicorn
import threading
import time
import logging
import torch
import warnings

# Patch torch.load to handle PyTorch 2.6+ security changes for YOLOv8
import torch
_original_load = torch.load
def _patched_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load

# Suppress Pydantic v2 protected namespace warnings and others
warnings.filterwarnings("ignore", message='Field "model_used" has conflict with protected namespace "model_"')
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from config import settings
from database import get_db_manager
from cv_module import VideoProcessor
from analytics import AnalyticsAggregator, TrafficPredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RetailAnalyticsSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        """Initialize the retail analytics system"""
        logger.info("Initializing Retail Analytics System...")
        
        # Get database manager
        self.db_manager = get_db_manager()
        
        # Initialize video processor
        self.video_processor = VideoProcessor(self.db_manager)
        
        # Initialize analytics
        self.analytics_aggregator = AnalyticsAggregator(self.db_manager)
        self.traffic_predictor = TrafficPredictor(self.db_manager)
        
        # Server thread
        self.server_thread = None
        
        logger.info("System initialized successfully")
    
    def setup_video_sources(self):
        """Set up video sources (webcam and uploaded videos)"""
        logger.info("Setting up video sources...")
        
        # Add webcam as entrance camera
        webcam_added = self.video_processor.add_source(
            source_id=settings.WEBCAM_INDEX,
            source_type="webcam",
            name="Entrance Camera",
            role="entrance"
        )
        
        if webcam_added:
            logger.info("Webcam added as entrance camera")
        else:
            logger.warning("Failed to add webcam. Make sure a camera is connected.")
        
        # Check for uploaded videos
        import os
        video_dir = settings.VIDEO_UPLOAD_DIR
        
        if os.path.exists(video_dir):
            video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
            
            for video_file in video_files:
                video_path = os.path.join(video_dir, video_file)
                
                # Determine role from filename
                if 'entrance' in video_file.lower():
                    role = 'entrance'
                    name = 'Entrance Video'
                elif 'cashier' in video_file.lower():
                    role = 'cashier'
                    name = 'Cashier Video'
                else:
                    role = 'section'
                    # Extract section name from filename
                    name = video_file.split('_')[1] if '_' in video_file else 'Section Video'
                
                self.video_processor.add_source(
                    source_id=video_path,
                    source_type="video",
                    name=name,
                    role=role
                )
                
                logger.info(f"Added video source: {name} ({video_file})")
    
    def start_cv_processing(self):
        """Start computer vision processing for all sources"""
        logger.info("Starting CV processing...")
        
        for source_name, source in self.video_processor.sources.items():
            # Determine role based on source name
            if 'entrance' in source_name.lower():
                role = 'entrance'
            elif 'cashier' in source_name.lower():
                role = 'cashier'
            else:
                role = 'section'
            
            self.video_processor.start_processing(source_name, role)
        
        logger.info("CV processing started for all sources")
    
    def start_api_server(self):
        """Start FastAPI server in a separate thread"""
        logger.info("Starting API server...")
        
        def run_server():
            uvicorn.run(
                "api.main:app",
                host=settings.APP_HOST,
                port=settings.APP_PORT,
                reload=False,
                log_level="info"
            )
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        logger.info(f"API server started at http://{settings.APP_HOST}:{settings.APP_PORT}")
        logger.info(f"API documentation available at http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    
    def run(self):
        """Run the complete system"""
        try:
            # Setup video sources
            self.setup_video_sources()
            
            # Start CV processing
            if self.video_processor.sources:
                self.start_cv_processing()
            else:
                logger.warning("No video sources available. CV processing will not start.")
                logger.info("You can upload videos using the API at /api/upload/video")
            
            # Start API server
            self.start_api_server()
            
            # Keep main thread alive
            logger.info("\n" + "="*60)
            logger.info("Retail Analytics System is running!")
            logger.info("="*60)
            logger.info(f"API Server: http://{settings.APP_HOST}:{settings.APP_PORT}")
            logger.info(f"API Docs: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
            logger.info("Press Ctrl+C to stop")
            logger.info("="*60 + "\n")
            
            # Keep running
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\nShutting down system...")
            self.shutdown()
        except Exception as e:
            logger.error(f"Error running system: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Stopping CV processing...")
        self.video_processor.stop_all()
        
        logger.info("Closing database connections...")
        self.db_manager.close()
        
        logger.info("System shutdown complete")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Retail Analytics System - Computer Vision AI        ║
    ║                                                          ║
    ║  Features:                                               ║
    ║  • Real-time visitor tracking                            ║
    ║  • Gender classification                                 ║
    ║  • Heatmap generation                                    ║
    ║  • Queue detection & wait time estimation                ║
    ║  • Traffic prediction                                    ║
    ║  • AI-powered chatbot (Groq)                             ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Create and run system
    system = RetailAnalyticsSystem()
    
    # Inject video processor into API
    import api.dependencies
    api.dependencies.video_processor_instance = system.video_processor
    
    system.run()


if __name__ == "__main__":
    main()
