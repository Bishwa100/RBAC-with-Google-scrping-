FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# Avoid prompt during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.10 and system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure pip is up to date
RUN python3.10 -m pip install --upgrade pip

# Install PyTorch with CUDA 12.1 support
RUN python3.10 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install bitsandbytes separately to ensure GPU support
RUN python3.10 -m pip install bitsandbytes

# Copy requirements and install the rest
COPY requirements.txt .
RUN python3.10 -m pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Set up local model weight directory (default in config is models/pretrained_weights)
ENV TRANSFORMERS_CACHE=/app/models/pretrained_weights
ENV HF_HOME=/app/models/pretrained_weights

# Download models during build for faster startup
RUN python3.10 download_models.py

EXPOSE 8001

CMD ["python3.10", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]