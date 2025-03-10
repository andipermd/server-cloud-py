# Gunakan image Python yang sesuai
FROM python:3.11.7

# Install dependencies sistem yang diperlukan oleh Rasterio
RUN apt-get update && apt-get install -y \
    libexpat1 \
    libgdal30 \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin semua file proyek ke dalam container
COPY . .

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan aplikasi dengan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
