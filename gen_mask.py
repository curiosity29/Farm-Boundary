import rasterio.mask
import rasterio
import numpy as np
import glob, os
import geopandas as gp


"""
gen mask from geodataframe of polygons

INPUT:
    image: path image. VD: $PATH_IMAGE/xxx.tif
    shp: path shapefile
OUTPUT:
    out_label: output image mask. VD: $PATH_IMAGE/xxx_mask.tif

Note:
    "image", "out_label" in the same folder, "image" name is xxx then "out_label" name is xxx_mask
"""
# path_dir_out = r'/home/skymap/big_data/Dao_work_space/OpenLandstraindata/Water_v3/mask'
# list_fp_img = glob.glob(os.path.join(r"/home/skymap/data/MRSAC/label_train/DATRA_TRAIN_LAST/GREEN/img_cut/tmp/stack_cut_img", "*.tif"))
list_fp_img = glob.glob('/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/anh_ro/train_region.tif')
for image in list_fp_img:
    image = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/anh_ro/train_region.tif'
    for img in glob.glob(image):
        print('hello')
        name = os.path.basename(img)
        print(f'dang xu li anh {name}')
        with rasterio.open(img, mode='r+') as src:
            projstr = src.crs.to_string()
            
            
            print(projstr)
        file_path = '/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/anh_ro/' + name.replace('tif','shp')
        print(file_path)
        if os.path.isfile(file_path):
            # shp = os.path.join(r"/home/skymap/data/MRSAC/label_train/DATRA_TRAIN_LAST/GREEN/img_cut/tmp/stack_cut_img_shape/",os.path.basename(img).replace('tif','shp'))
            shp = file_path
            # shp = "/home/skm/SKM/WORK/Demo_Kuwait/Kuwait_Planet_project/Label/open_land/label/v2/open_land_32638_fix.shp"
            bound_shp = gp.read_file(shp)
            # bound_shp = bound_shp[bound_shp['geometry'].type=='LineString']
            # bound_shp = bound_shp[bound_shp['geometry'].type=='Polygon']
            bound_shp = bound_shp.to_crs(projstr)


            #bound_shp.crs.to_epsg = projstr
            #print(bound_shp.crs)
            #for img in glob.glob('/mnt/Nam/public/hanoi_sen2/data/data_z18/*.tif'):
            with rasterio.open(img) as src:
                height = src.height
                width = src.width
                src_transform = src.transform
                out_meta = src.meta
                # mask_nodata = np.ones([height, width], dtype=np.uint8)
                # for i in range(src.count):
                #     mask_nodata = mask_nodata & src.read_masks(i+1)
            out_meta.update({"count": 1, "dtype": 'uint8', 'nodata': 0})
            if len(bound_shp) < 1:
                # out_label = img.replace('.tif', '_mask.tif')
                # img = np.zeros((1,height,width))
                # with rasterio.open(out_label, 'w', compress='lzw', **out_meta) as ras:
                #     ras.write(img)

                pass

            else:
                #region create geoseries from polygons and create mask. comment this region if dataframe contains linestring only
                # exterior_rings = []
                # from shapely.geometry import Polygon, MultiLineString

                # for x in [*bound_shp['geometry']]:
                #     if type(x)!= Polygon:
                #         rings = [*x.boundary.geoms]
                #         exterior_rings += rings
                #         # raise Exception()
                #     else:
                #         exterior_rings.append(x.boundary)
                # data = gp.GeoSeries(exterior_rings)
                # print(set([type(x) for x in data.geometry]))
                # mask = rasterio.features.geometry_mask(data, (height, width), src_transform, invert=True, all_touched=True).astype('uint8')

                #endregion

                mask = rasterio.features.geometry_mask(bound_shp['geometry'], (height, width), src_transform, invert=True, all_touched=True).astype('uint8') # uncomment this if shp file contain linestrings only

                # print(np.unique(mask))
                # mask = mask & mask_nodata
                out_label = img.replace('.tif', '_mask.tif')
                # out_label = os.path.join(path_dir_out,name)
                print(out_label)
                with rasterio.open(out_label, 'w', compress='lzw', **out_meta) as ras:
                    ras.write(mask[np.newaxis, :, :])
            print('da lu xong anh')
        else:
                # out_label = img.replace('.tif', '_mask.tif')
                # img = np.zeros((1,height,width))
                # with rasterio.open(out_label, 'w', compress='lzw', **out_meta) as ras:
                #     ras.write(img)
                pass


# image = '/mnt/Nam/bairac/classification_data/data_train/*.tif'
# for img in glob.glob(image):
#     with rasterio.open(img, mode='r+') as src:
#         projstr = src.crs.to_string()
#         height = src.height
#         width = src.width
#         src_transform = src.transform
#         out_meta = src.meta
    
#     shp = '/mnt/Nam/bairac/classification_data/landfill_training/'+ os.path.basename(img).replace('tif','shp')
#     bound_shp = gp.read_file(shp)
#     bound_shp = bound_shp.to_crs(projstr)

#     src1 = []
#     src2 = []
#     for i in range(len(bound_shp)):
#         if bound_shp.iloc[i]['id'] == 1:
#             src1.append(bound_shp.iloc[i]['geometry'])
#         else:
#             src2.append(bound_shp.iloc[i]['geometry'])

#     mask_paddy = rasterio.features.geometry_mask(src1, (height, width), src_transform,invert=True, all_touched=True).astype("uint8")
#     mask_background = rasterio.features.geometry_mask(src2, (height, width), src_transform,invert=True, all_touched=True).astype("uint8")
#     mask = mask_paddy+2*mask_background

#     out_meta.update({"count": 1, "dtype": 'uint8', 'nodata': 0})
#     label = img.replace('.tif', '_mask.tif')
#     print(label)
#     with rasterio.open(label, 'w', compress='lzw', **out_meta) as ras:
#         ras.write(mask[np.newaxis, :, :])