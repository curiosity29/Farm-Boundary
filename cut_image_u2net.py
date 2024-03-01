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



def mk_dir(path_image, name1, name2):
    if not os.path.exists(path_image+name1):
        os.mkdir(path_image+name1)
    if not os.path.exists(path_image+name2):
        os.mkdir(path_image+name2)
    return path_image+name1, path_image+name2

def cut_img(path_image):
    # image counter
    n = 0
    for image in glob.glob(path_img):
        name_ = os.path.basename(image)
        name1 = name_.split()
        name2 = name1[0].split(".")[0]
        image_name = name2.replace('_mask', '')
        with rasterio.open(image) as ras:
            with rasterio.open(image.replace('_mask', '')) as inds:
                tile_width, tile_height = IMAGE_SIZE, IMAGE_SIZE
                stride = STRIDE
                
                for window, transform in get_tiles(inds, tile_width, tile_height, stride):
                    if np.random.random_sample()>0.2:
                        outpath_label = os.path.join(train_label, f'{name2}_{n}'+".tif")
                        outpath_image = os.path.join(train_image, f'{image_name}_{n}'+".tif")
                    else:
                        outpath_label = os.path.join(val_label, f'{name2}_{n}'+".tif")
                        outpath_image = os.path.join(val_image, f'{image_name}_{n}'+".tif")
                    img = inds.read(window=window)
                    lab = ras.read(window=window)

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
                                "nodata": 0}) 
                        with rasterio.open(outpath_label, "w", compress='lzw', **out_meta1) as dest:
                            dest.write((lab*255).astype(np.uint8))
                    n=n+1

if __name__ == '__main__':

    path_img = r'/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/anh_ro/*_mask.tif'
    out_path = r'/home/skymap/big_data/Giang_workspace/Task_110123_Farm_boundary_Edge_Detect/data/train_data/test_cut_img/'
    IMAGE_SIZE = 512
    STRIDE = 128

    if not os.path.exists(out_path):
        os.mkdir(out_path)
        path_train, path_val = mk_dir(out_path, 'train/', 'val/')
        train_image, train_label = mk_dir(path_train, 'image/', 'label/')
        val_image, val_label = mk_dir(path_val, 'image/', 'label/')

    cut_img(path_img)