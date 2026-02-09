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
        """"Gracefully shutdown the system"""
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
    
    system.run()


if __name__ == "__main__":
    main()
