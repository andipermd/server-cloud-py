from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import numpy as np
import rasterio

app = FastAPI()

# ===================== NDVI ANALYSIS =====================

@app.post("/process-raster-ndvi")   
async def process_raster(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    file_location = f"temp_files/{file.filename}"
    
    # Simpan file sementara
    os.makedirs("temp_files", exist_ok=True)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Buka raster user
        with rasterio.open(file_location) as raster:
            red = raster.read(3)
            nir = raster.read(4)

            # 🔥 Hitung NDVI
            ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

            # Klasifikasi NDVI
            def classify_ndvi(ndvi):
                classified = np.zeros(ndvi.shape, dtype=np.uint8)
                classified[np.where(ndvi < 0)] = 1  # Air
                classified[np.where((ndvi >= 0) & (ndvi < 0.2))] = 2  # Tanah
                classified[np.where((ndvi >= 0.2) & (ndvi < 0.5))] = 3  # Semak atau rumput
                classified[np.where(ndvi >= 0.5)] = 4  # Hutan atau vegetasi lebat
                return classified

            classified_ndvi = classify_ndvi(ndvi)

            # Simpan hasil NDVI
            output_file = "temp_files/classified_ndvi.tif"
            with rasterio.open(
                output_file, "w",
                driver="GTiff",
                width=raster.width,
                height=raster.height,
                count=1,
                transform=raster.transform,
                crs=raster.crs,
                dtype=np.uint8
            ) as dst:
                dst.write(classified_ndvi, 1)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan dalam membaca raster: {str(e)}")

    finally:
        # Hapus file input setelah diproses
        if os.path.exists(file_location):
            os.remove(file_location)

    # Hapus hasil NDVI setelah dikirim ke frontend
    background_tasks.add_task(os.remove, output_file)

    return FileResponse(output_file, filename="classified_ndvi.tif", media_type="image/tiff")


# ===================== NDBI ANALYSIS =====================
@app.post("/process-raster-ndbi")
async def process_ndbi(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    file_location = f"temp_files/{file.filename}"

    # Simpan file sementara
    os.makedirs("temp_files", exist_ok=True)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Buka raster user
        with rasterio.open(file_location) as raster:
            swir = raster.read(6)  # SWIR-1 (Band 6 pada Landsat)
            nir = raster.read(4)

            # 🔥 Hitung NDBI
            ndbi = (swir.astype(float) - nir.astype(float)) / (swir + nir)

            # Klasifikasi NDBI
            def classify_ndbi(ndbi):
                classified = np.zeros(ndbi.shape, dtype=np.uint8)
                classified[np.where(ndbi < -0.2)] = 1  # Air
                classified[np.where((ndbi >= -0.2) & (ndbi < 0.1))] = 2  # Vegetasi
                classified[np.where((ndbi >= 0.1) & (ndbi < 0.3))] = 3  # Tanah kosong
                classified[np.where(ndbi >= 0.3)] = 4  # Area terbangun
                return classified

            classified_ndbi = classify_ndbi(ndbi)

            # Simpan hasil NDBI
            output_file = "temp_files/classified_ndbi.tif"
            with rasterio.open(
                output_file, "w",
                driver="GTiff",
                width=raster.width,
                height=raster.height,
                count=1,
                transform=raster.transform,
                crs=raster.crs,
                dtype=np.uint8
            ) as dst:
                dst.write(classified_ndbi, 1)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan dalam membaca raster: {str(e)}")

    finally:
        # Hapus file input setelah diproses
        if os.path.exists(file_location):
            os.remove(file_location)

    # Hapus hasil NDBI setelah dikirim ke frontend
    background_tasks.add_task(os.remove, output_file)

    return FileResponse(output_file, filename="classified_ndbi.tif", media_type="image/tiff")

