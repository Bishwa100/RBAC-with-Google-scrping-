FROM python:3.10-slim

# Avoid prompt during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure pip is up to date
RUN pip install --upgrade pip

# Install PyTorch CPU-only (much smaller ~200MB vs 780MB)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install the rest
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Set up local model weight directory (default in config is models/pretrained_weights)
ENV TRANSFORMERS_CACHE=/app/models/pretrained_weights
ENV HF_HOME=/app/models/pretrained_weights

# Download models during build for faster startup
RUN python download_models.py

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]