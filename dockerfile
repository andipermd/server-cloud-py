FROM python:3.11.7

# Set working directory
WORKDIR /app

# Buat virtual environment
RUN python -m venv /app/myvenv

# Set environment variable untuk menggunakan virtual environmen
ENV PATH="/app/myvenv/bin:$PATH"

# Copy requirements.txt dan install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# Jalankan aplikasi dengan uvicorn
CMD ["/opt/venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
