FROM python:3.11

# Set WORKDIR ke /app
WORKDIR /app

# Tambahkan --fix-missing pada apt-get update dan install dependencies dalam satu layer
# Diakhiri dengan pembersihan cache untuk menjaga image tetap kecil
RUN apt-get update --fix-missing && apt-get install -y \
    curl \
    build-essential \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Instal Poetry menggunakan script resmi lewat curl
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Konfigurasi agar Poetry tidak membuat virtual environment
RUN poetry config virtualenvs.create false

# Copy file pyproject.toml dan poetry.lock terlebih dahulu (untuk memanfaatkan cache Docker)
COPY pyproject.toml poetry.lock* ./

# Instal hanya dependensi utama tanpa interaksi user
RUN poetry install --only main --no-interaction

# Copy folder src dan dataset ke dalam container
COPY src/ ./src/
COPY dataset/ ./dataset/

# Set PYTHONPATH agar Python dapat menemukan module "agent" yang berada di dalam "src"
ENV PYTHONPATH="/app/src"

# Cloud Run by default injects the PORT environment variable.
ENV PORT=8080
EXPOSE 8080

# Gunakan uvicorn dengan shell format agar variable $PORT diparsing dari environment.
CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
