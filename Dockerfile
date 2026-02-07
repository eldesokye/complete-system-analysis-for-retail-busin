FROM python:3.10-slim-bookworm

# Install system dependencies
# libgl1-mesa-glx is NOT needed for opencv-python-headless
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install CPU-only versions of PyTorch first to avoid downloading huge CUDA wheels
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install dependencies interactively to avoid timeouts, and use headless OpenCV
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port (Render will set PORT env var, but good for documentation)
EXPOSE 8000

# Run the application
# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Run the application via startup script
CMD ["./start.sh"]
