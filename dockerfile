# Gunakan image Python yang sesuai
FROM python:3.11.7

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin semua file proyek ke dalam container
COPY . .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Pastikan path aplikasi benar
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8000"]
