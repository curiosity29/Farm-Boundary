import numpy as np
from osgeo import gdal
import geopandas as gpd
import os 
import glob
import shutil
# set the input file path
in_filepath = r"I:\Skymap\Task_070623_Building_footprint_pipeline\Data\Jupem_langkawi\image\jupem_dg.tif"

from osgeo import gdal

# def remove_band_from_rgb_image(input_image_path, output_image_path, band_to_remove):
#     # Open the input RGB image
#     dataset = gdal.Open(input_image_path)

#     # Get the number of bands in the image
#     band_count = dataset.RasterCount

#     # Create a new dataset with the band to remove excluded
#     output_dataset = gdal.GetDriverByName("GTiff").Create(output_image_path, dataset.RasterXSize, dataset.RasterYSize, band_count - 1, gdal.GDT_Byte)

#     # Iterate over the bands and copy them to the output dataset, except for the band to remove
#     output_band_index = 1
#     for band_index in range(1, band_count + 1):
#         if band_index != band_to_remove:
#             band = dataset.GetRasterBand(band_index)
#             output_band = output_dataset.GetRasterBand(output_band_index)
#             output_band.WriteArray(band.ReadAsArray())
#             output_band_index += 1

#     # Set the spatial reference and geotransform information of the output dataset
#     output_dataset.SetProjection(dataset.GetProjection())
#     output_dataset.SetGeoTransform(dataset.GetGeoTransform())


#     # Clean up by closing the datasets
#     dataset = None
#     output_dataset = None


# root_directory = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/uint8_rgb/'

# # band_arr = []
# # for foldername, subfolders, filenames in os.walk(root_directory):
# #     if "image" in subfolders:
# #         image_folder = os.path.join(foldername, "image/")

#         # for image_path in glob.glob(image_folder+ "*.tif"):

#         #     dataset = gdal.Open(image_path)
#         #     band_count = dataset.RasterCount
#         #     # band_arr.append(band_count)
#         # # from collections import Counter
#         # # print(dict(Counter(band_arr)))
#         #     output_image_path = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/rgb/' + os.path.basename(image_path)

#         #     if band_count == 4:
#         #         print(f'{os.path.basename(image_path)} has 4 bands.')
#         #         band_to_remove = 4
#         #         # Remove the specified band from the RGB image
#         #         remove_band_from_rgb_image(image_path, output_image_path, band_to_remove)
#         #     else:
#         #         shutil.copy(image_path, output_image_path)

# for image_path in glob.glob(root_directory+ "*.tif"):

#     dataset = gdal.Open(image_path)
#     band_count = dataset.RasterCount
#     # band_arr.append(band_count)
# # from collections import Counter
# # print(dict(Counter(band_arr)))
#     output_image_path = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/rgb/' + os.path.basename(image_path)

#     if band_count == 4:
#         print(f'{os.path.basename(image_path)} has 4 bands.')
#         band_to_remove = 4
#         # Remove the specified band from the RGB image
#         remove_band_from_rgb_image(image_path, output_image_path, band_to_remove)
#     else:
#         shutil.copy(image_path, output_image_path)

import numpy as np
from osgeo import gdal

# Specify the input and output file paths
input_path = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/CAPELLA_C02_SM_GEO_HH_20221216093623_20221216093627.tif'
output_path = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/3bands/CAPELLA_C02_SM_GEO_HH_20221216093623_20221216093627.tif'

# Open the input single-band TIFF image
input_ds = gdal.Open(input_path, gdal.GA_ReadOnly)

if input_ds is None:
    print("Failed to open the input TIFF file.")
    exit(1)

# Read the band data
input_band = input_ds.GetRasterBand(1)
data = input_band.ReadAsArray()

# Create a 3-band output dataset
driver = gdal.GetDriverByName("GTiff")
output_ds = driver.Create(output_path, input_ds.RasterXSize, input_ds.RasterYSize, 3, gdal.GDT_UInt16)

if output_ds is None:
    print("Failed to create the output TIFF file.")
    exit(1)

# Duplicate the single band to all three RGB channels
for band_num in range(1, 4):
    output_band = output_ds.GetRasterBand(band_num)
    output_band.WriteArray(data)

# Set the color interpretation for each band
output_ds.GetRasterBand(1).SetRasterColorInterpretation(gdal.GCI_RedBand)
output_ds.GetRasterBand(2).SetRasterColorInterpretation(gdal.GCI_GreenBand)
output_ds.GetRasterBand(3).SetRasterColorInterpretation(gdal.GCI_BlueBand)

# Set geotransform and projection information
output_ds.SetGeoTransform(input_ds.GetGeoTransform())
output_ds.SetProjection(input_ds.GetProjection())

# Close both datasets
input_ds = None
output_ds = None

print(f"Conversion completed. The 3-band duplicated image is saved as '{output_path}'.")
