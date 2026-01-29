"""
Video upload API routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import List
import os
import shutil
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/video")
async def upload_video(
    file: UploadFile = File(...),
    role: str = Form(..., description="Video role: entrance, section, or cashier"),
    section_name: str = Form(None, description="Section name (if role is section)")
):
    """Upload a video file for processing"""
    try:
        # Validate file type
        if not file.content_type.startswith("video/"):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        
        if role == "section" and section_name:
            filename = f"{role}_{section_name}_{timestamp}{file_extension}"
        else:
            filename = f"{role}_{timestamp}{file_extension}"
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Video uploaded: {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "path": file_path,
            "role": role,
            "section_name": section_name,
            "message": "Video uploaded successfully. You can now add this as a video source."
        }
    
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos")
async def list_uploaded_videos():
    """List all uploaded videos"""
    try:
        videos = []
        
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    videos.append({
                        "filename": filename,
                        "path": file_path,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        
        return {
            "success": True,
            "count": len(videos),
            "data": videos
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/video/{filename}")
async def delete_video(filename: str):
    """Delete an uploaded video"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Video not found")
        
        os.remove(file_path)
        logger.info(f"Video deleted: {filename}")
        
        return {
            "success": True,
            "message": f"Video '{filename}' deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
