"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from api.routes import analytics, chatbot, predictions, upload, video_feed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Retail Analytics System API",
    description="Computer Vision powered retail analytics with AI chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads/videos", exist_ok=True)

# Mount static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(video_feed.router, prefix="/api/video_feed", tags=["Video Feed"])




@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Mount frontend at root (must be last)
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        "api.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
