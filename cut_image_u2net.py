import rasterio.mask
import rasterio
from rasterio import windows
from itertools import product
import numpy as np
import glob, os
from tqdm import tqdm

"""
path_img: folder containing the input data
*Note:  + in folder have both image original xxx.tif and image mask xxx_mask.tif
        + path image passed in is the format  $PATH_IMAGE/*_mask.tif

out_path: folder containing the output data
├── train
│   ├── image
│   │   ├── file .tif
│   ├── label
│   │   ├── file .tif
├── val
│   ├── image
│   │   ├── file .tif
│   ├── label
│   │   ├── file .tif
"""

def get_tiles(ds, width, height, stride):
    nols, nrows = ds.meta['width'], ds.meta['height']
    offsets = product(range(0, nols, stride), range(0, nrows, stride))
    big_window = windows.Window(col_off=0, row_off=0, width=nols, height=nrows)
    offset = []
    for col_off, row_off in offsets:
        if row_off + width > nrows:
            row_off = nrows - width
        if  col_off + height > nols:
            col_off = nols - height
        offset.append((col_off, row_off))
    offset = set(offset)
    for col_off, row_off in tqdm(offset): 
        window =windows.Window(col_off=col_off, row_off=row_off, width=width, height=height).intersection(big_window)
        transform = windows.transform(window, ds.transform)
        yield window, transform
        
        
# path_img = '/home/skm/SKM/WORK/Demo_Kuwait/Data_Train_and_Model/openland_dstraining_v3_u2net/Img_cut_img/*_mask.tif'
# out_path = '/home/skm/SKM/WORK/Demo_Kuwait/Data_Train_and_Model/openland_dstraining_v3_u2net/dataset_training_u2net/'

path_img = r'/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/anh_ro/*_mask.tif'
out_path = r'/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/train_data_v4_800/'


def mk_dir(path_image, name1, name2):
    if not os.path.exists(path_image+name1):
        os.mkdir(path_image+name1)
    if not os.path.exists(path_image+name2):
        os.mkdir(path_image+name2)
    return path_image+name1, path_image+name2

if not os.path.exists(out_path):
    os.mkdir(out_path)
path_train, path_val = mk_dir(out_path, 'train/', 'val/')
train_image, train_label = mk_dir(path_train, 'image/', 'label/')
val_image, val_label = mk_dir(path_val, 'image/', 'label/')
    
#output_box = 'box_{}'

n=0
k  = 0
for image in glob.glob(path_img):
    name_ = os.path.basename(image)
    name1 = name_.split()
    name2 = name1[0].split(".")[0]
    with rasterio.open(image) as ras:
        with rasterio.open(image.replace('_mask', '')) as inds:
            tile_width, tile_height = 800,800
            stride = 128
            height = inds.height
            width = inds.width
            

            for window, transform in get_tiles(inds, tile_width, tile_height, stride):
                if np.random.random_sample()>0.2:
                    outpath_label = os.path.join(train_label, f'{name2}_box_2_{n}'+".tif")
                    outpath_image = os.path.join(train_image, f'{name2}_box_2_{n}'+".tif")
                else:
                    outpath_label = os.path.join(val_label, f'{name2}_box_2_{n}'+".tif")
                    outpath_image = os.path.join(val_image, f'{name2}_box_2_{n}'+".tif")
                img = inds.read(window=window)
                lab = ras.read(window=window)
                # print((img[0]-1).min(), (img[0]-1).max())
                # raise Exception()
                # if np.amax(rband)>0 and np.count_nonzero(img[0]-1)>0.9*tile_width* tile_height: 
                blank_condition = np.count_nonzero(img[0])>0.9*tile_width* tile_height and np.count_nonzero(img[0]-1)>0.9*tile_width* tile_height
                if np.count_nonzero(lab) and blank_condition:

                #write image
                    out_meta = inds.meta
                    out_meta.update({"driver": "GTiff",
                            "height": img.shape[1],
                            "width": img.shape[2],
                            "transform": transform,
                            "nodata": 0})
                    with rasterio.open(outpath_image, "w", compress='lzw', **out_meta) as dest:
                        dest.write(img)

                    #write mask label
                    out_meta1 = ras.meta
                    out_meta1.update({"driver": "GTiff",
                            "height": img.shape[1],
                            "width": img.shape[2],
                            "transform": transform,
                            "nodata": 0}) #None data ################## None / 0
                    with rasterio.open(outpath_label, "w", compress='lzw', **out_meta1) as dest:
                        dest.write((lab*255).astype(np.uint8))
                    #dest.write(lab)
                n=n+1
                    
                        


        
   