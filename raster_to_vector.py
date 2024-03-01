import numpy as np
import rasterio
# from rasterio.windows import Window
import Vectorization
from skimage.morphology import skeletonize, remove_small_holes, remove_small_objects
from tqdm import tqdm
import rasterio.mask
import rasterio
from rasterio import windows
from itertools import product
import os
import  cv2
import pandas as pd
import geopandas as gpd
import shutil
import random
def get_tiles(ds, width, height, stride):
    nols, nrows = ds.meta['width'], ds.meta['height']
    offsets = product(range(0, nols, stride), range(0, nrows, stride))
    big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
    for col_off, row_off in offsets:
        recent_x = nols - col_off
        recent_y = nrows - row_off
        xrange = min(width,recent_x)
        yrange = min(height,recent_y)
        window=windows.Window(col_off=col_off, row_off=row_off, width=xrange, height=yrange).intersection(big_window)
        transform = windows.transform(window, ds.transform)
        yield window, transform

def split_image(path_img,out_path_image):
    img_name = os.path.basename(path_img).replace('.tif', '')
    with rasterio.open(path_img) as inds:
        stride = 30000-256 # ban dau 256
        tile_width, tile_height = 30000,30000 # m30000, 30000
        projstr = inds.crs.to_string()
        height = inds.height
        width = inds.width
        print(height, width)
        out_meta = inds.meta
        transformss = inds.transform
        
        for window, transform in get_tiles(inds, tile_width, tile_height, stride):
            outpath_image = os.path.join(out_path_image, img_name + "_{}_{}.tif".format(window.col_off, window.row_off))
            out_image = inds.read(window=window)
            out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": transform})
            with rasterio.open(outpath_image, "w", compress='lzw', **out_meta) as dest:
                dest.write(out_image)
        # out_image = inds.read()
        # outpath_image = os.path.join(out_path_image, img_name + '.tif')
        # with rasterio.open( outpath_image,"w", compress='lzw', **out_meta) as dest:
        #     dest.write(out_image)
        print("DONE SPLIT!!!")

threshold_distance = 3 #ngưỡng làm mượt polygon
threshold_connect = 7
def Morphology(image):
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # dilation  

    # opening
    #     img = cv2.morphologyEx(data, cv2.MORPH_OPEN, kernel)
    # for i in range(10):
    #     img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel2)
    # closing
    #     for _ in range(2):
    img = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel2)
    return img
def raster_to_vector(path_in, path_out, threshold_distance, threshold_connect):
    print('start convert raster to vector ...')
    tmp_folder_img = path_out.replace('.shp','_tmp')
    tmp_folder_result = path_out.replace(".shp","_result_tmp")
    print(path_out,tmp_folder_result)
    if not os.path.exists(tmp_folder_img):
        os.makedirs(tmp_folder_img)
    if not os.path.exists(tmp_folder_result):
        os.makedirs(tmp_folder_result)
    split_image(path_in,tmp_folder_img)
    # raise Exception()
    list_tmp_input = create_list_id(tmp_folder_img)
    for tmp_image in list_tmp_input:
        image_tmp_path=os.path.join(tmp_folder_img,tmp_image)
        output_tmp_path=os.path.join(tmp_folder_result,tmp_image.replace('.tif','.geojson'))
        print("start reading img")
        with rasterio.open(image_tmp_path) as inds:  
            data = inds.read()[0]
            transform = inds.transform
            projstr = inds.crs.to_string()
        data = (data==1).astype(np.uint8)
        print("done reading img")
#region set image edge to 1 
        # set 99% of edge
        # one_col_index = np.ones(data.shape[1], dtype = data.dtype)
        # zero_col_index = random.randint(0, int(data.shape[1]*0.99))
        # one_col_index[zero_col_index]=0
        # data[0, :] = np.logical_or(data[0, :], one_col_index).astype(int)
        # data[-1, :] = np.logical_or(data[-1, :], one_col_index).astype(int)



        # one_row_index = np.ones(data.shape[0], dtype = data.dtype)
        # zero_row_index = random.randint(0, int(data.shape[0]*0.99))
        # one_row_index[zero_row_index]=0
        # # Set the first and last columns to 1
        # data[:, 0] = np.logical_or(data[:, 0], one_row_index).astype(int)
        # data[:, -1] = np.logical_or(data[:, -1], one_row_index).astype(int)

        # set 100% of edge
        # data[0, :] = 1
        # data[-1, :] = 1

        # data[:, 0] = 1
        # data[:, -1] = 1
#endregion
        data = Morphology(data)
        data = remove_small_holes(data.astype(bool), area_threshold=80)
        data = remove_small_objects(data, min_size=80)
        skeleton = skeletonize(data.astype(np.uint8))
        # from PIL import Image
        # skeleton_image = Image.fromarray((skeleton * 255).astype(np.uint8))

        # # Save the image
        # skeleton_image.save('/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/shape/box_620_tmp/skeleton_image.png')

        print("START SAVE SHAPEFILE!!!")
        try:
            Vectorization.save_polygon(np.pad(skeleton, pad_width=1).astype(np.intc), threshold_distance, threshold_connect, transform, projstr, output_tmp_path)
        except Exception as e:
            print("ERROR OCCURING!!!")
            print(e)
    list_geo_json = create_list_geojson(tmp_folder_result)
    if len(list_geo_json)<1:
        shutil.rmtree(tmp_folder_img)
        shutil.rmtree(tmp_folder_result)
        return os.path.basename(image_tmp_path)
    else:
        gdf = pd.concat([gpd.read_file(shp_path).to_crs(4326) for shp_path in list_geo_json]).pipe(gpd.GeoDataFrame)
        # gdf = pd.concat([gpd.read_file(shp_path) for shp_path in list_geo_json]).pipe(gpd.GeoDataFrame)

        # gdf = gdf.set_crs(epsg = '32648', inplace=True)
        gdf.crs = "EPSG:4326"
        gdf.to_file(path_out,driver='ESRI Shapefile')
        shutil.rmtree(tmp_folder_img)
        shutil.rmtree(tmp_folder_result)
        print("Done!!!")
        return ''

def create_list_geojson(dir_path):
    list_id = []
    print(dir_path)
    for file in os.listdir(dir_path):
        if file.endswith(".geojson"):
            list_id.append(os.path.join(dir_path,file))
    return list_id


def create_list_id(dir_path):
    list_id = []
    for file in os.listdir(dir_path):
        if file.endswith(".tif"):
            list_id.append(file)
    return list_id

if __name__=="__main__":
    # import argparse
    # args_parser = argparse.ArgumentParser()
    # args_parser.add_argument(
    #     '-i',
    #     help='Input folder!',
    #     required=True
    # )

    # args_parser.add_argument(
    #     '-o',
    #     help='Output path',
    #     required=True
    # )

    # param = args_parser.parse_args()
    
    # folder_image_path = param.i
    # folder_output_path =param.o
    folder_image_path = "/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/result/new/storage"
    # list_image=create_list_id(folder_image_path)
    folder_output_path = "/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/result/shp2"
    # with open('/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/shape/blank.txt', 'w') as file:
    list_image = ["/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/result/new/storage/Karnataka_13.tif"]
    # for i in range(3,12):
    #     list_image = ["/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/code/google_download/output/result/Karnataka_{}.tif".format(i)]
    for image_name in tqdm(list_image):
        iamge_path=os.path.join(folder_image_path,image_name)
        output_path=os.path.join(folder_output_path,image_name.replace('.tif','.shp'))
        empty_poly_name = raster_to_vector(iamge_path, output_path, threshold_distance, threshold_connect)
                # if empty_poly_name:
                    # file.write(empty_poly_name+ '\n')
        