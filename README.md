# Retail Analytics System - Computer Vision AI

A comprehensive retail analytics system powered by computer vision and AI to analyze customer behavior, optimize store operations, and provide intelligent business insights.

## 🎯 Features

### Computer Vision Analytics
- **People Counting**: Real-time visitor detection and counting using YOLOv8
- **Gender Classification**: Demographic analysis of store visitors
- **Heatmap Generation**: Visual representation of customer movement patterns
- **Queue Detection**: Cashier queue length and wait time estimation
- **Transaction Estimation**: Approximate transaction counts based on queue behavior

### AI-Powered Insights
- **Intelligent Chatbot**: Groq-powered AI assistant (bilingual: English & Arabic)
- **Traffic Prediction**: Time-series forecasting using Prophet
- **Automated Recommendations**: AI-generated suggestions for store optimization
- **Real-time Analytics**: Live dashboard data via REST API

### Data Management
- **PostgreSQL Database**: Robust data storage and retrieval
- **Multi-source Support**: Webcam + video file processing
- **Historical Analysis**: Track performance over time
- **Predictive Modeling**: Forecast future traffic patterns

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- Webcam (optional, for live processing)
- Groq API key

## 🚀 Installation

### 1. Clone or navigate to the project directory

```bash
cd "d:\365 projects\new project"
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

The `.env` file is already configured with your credentials:
- Database: localhost/supabase
- Groq API: Configured with your API key

### 6. Initialize database

```bash
python utils/init_db.py
```

### 7. Generate demo data (optional)

```bash
python utils/demo_data.py
```

This will populate your database with 7 days of historical data and 3 days of predictions.

## 🎮 Usage

### Start the System

```bash
python main.py
```

This will:
1. Initialize the computer vision module
2. Start processing video sources (webcam + uploaded videos)
3. Launch the FastAPI server at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Upload Videos

You can upload video files for processing:

```bash
curl -X POST "http://localhost:8000/api/upload/video" \
  -F "file=@your_video.mp4" \
  -F "role=section" \
  -F "section_name=Mens Clothing"
```

**Supported roles:**
- `entrance` - Entrance camera
- `section` - Section camera (specify section_name)
- `cashier` - Cashier camera

## 📡 API Endpoints

### Analytics
- `GET /api/analytics/live` - Real-time analytics summary
- `GET /api/analytics/sections` - Section-wise performance
- `GET /api/analytics/cashier` - Cashier analytics
- `GET /api/analytics/hourly` - Hourly visitor breakdown
- `GET /api/analytics/summary` - Daily summary
- `GET /api/analytics/timeline` - Traffic timeline (past N days)

### Chatbot
- `POST /api/chatbot/query` - Send query to AI chatbot
- `GET /api/chatbot/summary` - Get automated summary
- `GET /api/chatbot/recommendations` - Get AI recommendations

### Predictions
- `GET /api/predictions/traffic` - Traffic predictions
- `GET /api/predictions/peak-hours` - Predicted peak hours
- `POST /api/predictions/generate` - Generate new predictions

### Upload
- `POST /api/upload/video` - Upload video file
- `GET /api/upload/videos` - List uploaded videos
- `DELETE /api/upload/video/{filename}` - Delete video

## 💬 Chatbot Examples

### English Query
```bash
curl -X POST "http://localhost:8000/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the current store status?",
    "language": "en"
  }'
```

### Arabic Query
```bash
curl -X POST "http://localhost:8000/api/chatbot/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ما هي حالة المتجر الحالية؟",
    "language": "ar"
  }'
```

## 🗂️ Project Structure

```
new project/
├── api/                    # FastAPI application
│   ├── main.py            # API entry point
│   └── routes/            # API route handlers
├── analytics/             # Analytics engine
│   ├── aggregator.py      # Metrics calculation
│   └── predictor.py       # Traffic forecasting
├── chatbot/               # AI chatbot
│   ├── groq_client.py     # Groq API integration
│   ├── chatbot_service.py # Chatbot logic
│   └── prompts.py         # System prompts
├── cv_module/             # Computer vision
│   ├── people_counter.py  # YOLOv8 detection
│   ├── gender_classifier.py
│   ├── heatmap_generator.py
│   ├── queue_detector.py
│   └── video_processor.py # Main CV orchestrator
├── database/              # Database layer
│   ├── schema.sql         # PostgreSQL schema
│   ├── models.py          # Pydantic models
│   └── db_manager.py      # Database operations
├── utils/                 # Utilities
│   ├── init_db.py         # Database initialization
│   └── demo_data.py       # Demo data generator
├── uploads/               # Uploaded videos
├── config.py              # Configuration
├── main.py                # Main entry point
└── requirements.txt       # Dependencies
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Database
DB_HOST=localhost
DB_NAME=supabase
DB_USER=postgres
DB_PASSWORD=0155

# Groq API
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
WEBCAM_INDEX=0
```

## 📊 Database Schema

The system uses PostgreSQL with the following tables:
- `visitors` - Entrance camera data
- `section_analytics` - Per-section visitor data
- `cashier_analytics` - Queue and transaction data
- `traffic_predictions` - Forecasted traffic
- `recommendations` - AI-generated recommendations

## 🤖 Computer Vision Models

- **YOLOv8**: Person detection and counting
- **DeepFace** (optional): Gender classification
- **Custom Heatmap**: Movement tracking and density analysis
- **Queue Detection**: Cashier area monitoring

## 🧠 AI & Predictions

- **Groq LLM**: llama-3.3-70b-versatile for chatbot
- **Prophet**: Time-series forecasting
- **Exponential Smoothing**: Fallback prediction method
- **Pattern-based**: Demo data generation

## 📝 Notes

- The system works with demo data even without video sources
- Gender classification uses a simplified approach (can be enhanced with DeepFace)
- Predictions improve with more historical data
- The chatbot supports both English and Arabic

## 🔒 Security

- In production, update CORS settings in `api/main.py`
- Secure your database credentials
- Protect your Groq API key
- Use HTTPS for API endpoints

## 🐛 Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check credentials in `.env`
- Ensure database "supabase" exists

### Webcam Not Detected
- Check `WEBCAM_INDEX` in `.env`
- Verify camera permissions
- Upload video files as alternative

### Groq API Error
- Verify API key is correct
- Check internet connection
- Monitor API rate limits

## 📄 License

This project is for educational and commercial use in retail environments.

## 🤝 Support

For issues or questions, refer to the API documentation at `/docs` when the server is running.

---

**Built with ❤️ using Python, FastAPI, YOLOv8, and Groq AI**
