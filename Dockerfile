FROM python:3.10-slim

# Install system dependencies for OpenCV and other potential needs
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port (Render will set PORT env var, but good for documentation)
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
