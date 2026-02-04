from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import StreamingResponse
import cv2
import time
import logging

from api.dependencies import get_video_processor

router = APIRouter()
logger = logging.getLogger(__name__)

def generate_frames(source_name: str):
    """Generator function for video streaming"""
    video_processor = get_video_processor()
    if not video_processor:
        logger.error("Video processor not initialized")
        return

    while True:
        frame_bytes = video_processor.get_latest_frame(source_name)
        
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # If no frame is available, wait a bit
            time.sleep(0.1)
        
        # Control frame rate
        time.sleep(0.04) # ~25 FPS

@router.get("/{source_name}")
async def video_feed(source_name: str):
    """
    Video streaming route. Put this in the src attribute of an img tag.
    Example: <img src="/api/video_feed/Entrance Camera">
    """
    video_processor = get_video_processor()
    if not video_processor:
        raise HTTPException(status_code=503, detail="Video processor not ready")
        
    if source_name not in video_processor.sources:
        raise HTTPException(status_code=404, detail=f"Source '{source_name}' not found")

    return StreamingResponse(
        generate_frames(source_name), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
