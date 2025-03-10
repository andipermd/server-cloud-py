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

# from fastapi import FastAPI, HTTPException
# import rasterio
# import numpy as np
# import os

# app = FastAPI()

# # Fungsi untuk memproses raster sesuai dengan tipe analisis
# def process_raster(file_path, analysis_type):
#     try:
#         with rasterio.open(file_path) as raster:
#             if analysis_type == "NDVI":
#                 red = raster.read(3)
#                 nir = raster.read(4)
#                 result = (nir.astype(float) - red.astype(float)) / (nir + red)
#             elif analysis_type == "NDBI":
#                 swir = raster.read(5)
#                 nir = raster.read(4)
#                 result = (swir.astype(float) - nir.astype(float)) / (swir + nir)
#             else:
#                 raise HTTPException(status_code=400, detail="Tipe analisis tidak dikenali")
            
#             output_file = f"temp_files/{analysis_type}_result.tif"
#             with rasterio.open(
#                 output_file, "w", driver="GTiff", width=raster.width,
#                 height=raster.height, count=1, transform=raster.transform,
#                 crs=raster.crs, dtype=np.float32
#             ) as dst:
#                 dst.write(result, 1)

#             return output_file
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error dalam analisis: {str(e)}")

# # Endpoint utama untuk semua analisis raster
# @app.post("/process-raster")
# async def process_raster_endpoint(data: dict):
#     file_path = data.get("filePath")
#     analysis_type = data.get("analysisType")

#     if not file_path or not analysis_type:
#         raise HTTPException(status_code=400, detail="filePath dan analysisType diperlukan!")

#     return process_raster(file_path, analysis_type)


# @app.post("/process-ndvi")
# async def process_ndvi(file: UploadFile = File(...)):
#     file_location = f"temp_files/{file.filename}"
    
#     # Simpan file sementara
#     os.makedirs("temp_files", exist_ok=True)
#     with open(file_location, "wb") as buffer:
#         buffer.write(await file.read())

#     # 🔍 Cek apakah file raster tersedia
#     if not os.path.exists(file_location):
#         raise HTTPException(status_code=400, detail="File raster tidak ditemukan")

#     try:
#         with rasterio.open(file_location) as raster:
#             # 🔍 Pastikan raster memiliki cukup band untuk NDVI (minimal 4 band)
#             if raster.count < 4:
#                 raise HTTPException(status_code=400, detail="File raster tidak memiliki cukup band (minimal 4 band)")

#             # 🔍 Cek apakah band sesuai format yang diharapkan
#             red = raster.read(3)
#             nir = raster.read(4)

#             if red is None or nir is None:
#                 raise HTTPException(status_code=400, detail="Band Red/NIR tidak ditemukan di raster")

#             # 🔥 Proses NDVI
#             ndvi = (nir.astype(float) - red.astype(float)) / (nir + red)

#             # Debug NDVI hasil
#             print("NDVI berhasil diproses!")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Terjadi kesalahan dalam membaca raster: {str(e)}")

#     finally:
#         # Hapus file setelah diproses
#         if os.path.exists(file_location):
#             os.remove(file_location)

#     return {"message": "NDVI processed successfully"}




# @app.post("/process-raster")
# async def process_raster(file: UploadFile = File(...)):
#     file_location = f"temp_files/{file.filename}"
    
#     os.makedirs("temp_files", exist_ok=True)
#     with open(file_location, "wb") as buffer:
#         buffer.write(await file.read())

#     metadata = {}
#     try:
#         with rasterio.open(file_location) as src:
#             metadata = src.meta
#             metadata["crs"] = str(metadata["crs"])  # Convert CRS ke string
#             metadata["transform"] = str(metadata["transform"])  # Convert Transform ke string
            
            
        
#     except Exception as e:
#         metadata = {"error": f"Failed to read raster: {str(e)}"}

   
#     os.remove(file_location)



#     return {"message": "Raster processed successfully", "metadata": metadata}

    