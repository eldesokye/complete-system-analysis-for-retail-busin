# 🚀 Quick Start Guide - Retail Analytics System

## Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

This will install all necessary packages including FastAPI, OpenCV, YOLOv8, Groq, and more.

---

## Step 2: Initialize Database

Run the database initialization script:

```powershell
python utils/init_db.py
```

This creates all necessary tables in your PostgreSQL database.

---

## Step 3: Generate Demo Data

Populate the database with realistic demo data:

```powershell
python utils/demo_data.py
```

This generates:
- 7 days of historical visitor data
- Section analytics with gender distribution
- Cashier queue and transaction data
- 3 days of traffic predictions
- Sample AI recommendations

---

## Step 4: Start the System

Launch the complete system:

```powershell
python main.py
```

This will:
- ✅ Initialize computer vision module
- ✅ Start processing video sources (if available)
- ✅ Launch FastAPI server at http://localhost:8000
- ✅ Serve the frontend dashboard

---

## Step 5: Access the Dashboard

Open your browser and navigate to:

**http://localhost:8000**

You'll see a beautiful dashboard with:
- 📊 Real-time analytics
- 💬 AI chatbot assistant
- 📹 Video upload interface

---

## 🎯 Using the Dashboard

### Dashboard Tab
- View live visitor counts
- Monitor queue length
- Check conversion rates
- See hourly traffic charts
- Analyze section performance
- Review traffic predictions
- Get AI recommendations

### AI Assistant Tab
- Ask questions in English or Arabic
- Get real-time insights
- Receive optimization suggestions
- Use quick question buttons

### Upload Tab
- Upload video files from your cameras
- Specify camera role (entrance/section/cashier)
- View uploaded videos
- Delete videos when needed

---

## 📹 Uploading Videos

1. Go to the **Upload** tab
2. Click the upload zone or drag & drop video files
3. Select the camera role:
   - **Entrance Camera** - Tracks total visitors
   - **Section Camera** - Monitors specific sections
   - **Cashier Camera** - Analyzes queue and transactions
4. For section cameras, enter the section name
5. Click upload and wait for processing

---

## 💬 Using the AI Chatbot

### Example Questions (English):
- "What is the current store status?"
- "Which section needs more attention?"
- "What are the peak hours today?"
- "How can I improve conversion rate?"

### Example Questions (Arabic):
- "ما هي حالة المتجر الحالية؟"
- "أي قسم يحتاج إلى مزيد من الاهتمام؟"
- "ما هي ساعات الذروة اليوم؟"

---

## 🔧 API Documentation

While the system is running, you can also access:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## 📊 Understanding the Dashboard

### Stats Cards
1. **Total Visitors** - Today's visitor count
2. **Queue Length** - Current cashier queue
3. **Conversion Rate** - Visitors who made purchases
4. **Peak Hour** - Busiest time of day

### Charts
- **Hourly Traffic** - Visitor distribution throughout the day
- **Section Performance** - Comparison of all sections

### Predictions
- Shows expected visitor counts for upcoming hours
- Helps with staffing decisions

### Recommendations
- AI-generated suggestions
- Priority levels: High, Medium, Low
- Actionable insights for improvement

---

## 🎨 Features

### Modern Design
- Dark theme with vibrant gradients
- Smooth animations and transitions
- Responsive layout (works on mobile)
- Glassmorphism effects

### Real-time Updates
- Dashboard refreshes every 30 seconds
- Live analytics from CV processing
- Instant chatbot responses

### Bilingual Support
- English and Arabic interfaces
- Toggle language in chatbot

---

## 🐛 Troubleshooting

### Dashboard not loading?
- Make sure the backend is running (`python main.py`)
- Check that you're accessing http://localhost:8000
- Clear browser cache and refresh

### No data showing?
- Run `python utils/demo_data.py` to generate demo data
- Wait a few seconds for data to load

### Chatbot not responding?
- Verify your Groq API key in `.env`
- Check internet connection
- Look for errors in the console

### Video upload failing?
- Ensure video format is supported (MP4, AVI, MOV)
- Check file size (large files may take time)
- Verify uploads directory exists

---

## 🎯 Next Steps

1. **Upload Your Videos**: Add real footage from your store
2. **Customize Sections**: Modify section names in the code
3. **Adjust Predictions**: Train with more historical data
4. **Deploy**: Host on a cloud server for production use

---

## 📝 Notes

- The system works perfectly with demo data even without videos
- Gender classification uses a simplified approach (can be enhanced)
- Predictions improve with more historical data
- All data is stored in your local PostgreSQL database

---

**Enjoy your Retail Analytics System! 🎉**

For questions or issues, check the API documentation or review the code.
