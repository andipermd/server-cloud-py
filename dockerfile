# Gunakan base image resmi Python
FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /app

# Install dependencies sistem yang diperlukan oleh Rasterio dan GDAL
RUN apt-get update && apt-get install -y \
    libexpat1 \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Buat symlink untuk libexpat jika tidak ditemukan
RUN ln -s /usr/lib/x86_64-linux-gnu/libexpat.so /usr/lib/x86_64-linux-gnu/libexpat.so.1 || true

# Copy semua file proyek ke dalam container
COPY . .

# Install dependencies Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose port aplikasi
EXPOSE 8000

# Jalankan aplikasi menggunakan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
