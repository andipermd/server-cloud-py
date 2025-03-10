# Gunakan base image resmi Python
FROM python:3.11.7

# Set working directory di dalam container
WORKDIR /app

# Copy semua file proyek ke dalam container
COPY requirements.txt .

# Buat virtual environment dan install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy seluruh kode ke dalam container
COPY . .

# Jalankan aplikasi dengan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

