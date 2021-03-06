
# -*-coding:UTF-8 -*-
'''
* merge_images_by_label.py
* @author wzm
* created 2021/03/04 01:16:19
* @function: 按照标签将所有图片合并成一张大图
'''


import os
import numpy as np

from osgeo import gdal
from gdalconst import *


def get_all_images_labels(train_file_txt_path, predict_file_txt_path):
    """
    @function: 返回所有需要合并图片的图片名和标签
    @params:
    train_file_txt_path: 训练文件及其标签
    predict_file_txt_path: 预测文件及其预测标签
    @return:
    images_names_list: 图片文件名列表
    images_labels_list: 图片标签列表
    """
    images_names_list, images_labels_list = [], []
    with open(train_file_txt_path, 'r') as fr_train:
        fr_train_lines = fr_train.readlines()
        for fr_train_line in fr_train_lines:
            name_tmp, label_tmp = fr_train_line.split()
            images_names_list.append(name_tmp)
            images_labels_list.append(label_tmp)
    with open(predict_file_txt_path, 'r') as fr_predict:
        fr_predict_lines = fr_predict.readlines()
        for fr_predict_line in fr_predict_lines:
            name_tmp, label_tmp = fr_predict_line.split()
            images_names_list.append(name_tmp)
            images_labels_list.append(label_tmp)
    return images_names_list, images_labels_list

def get_begin_point_if(prefix, images_names_list):
    """
    @function: 获取整个大图的起始点，即左上方(x_min, y_max)
    水平方向是x，往右增大，竖直方向是y，往下变小
    @params:
    prefix: 存放图片的文件夹名
    images_names_list: 图片名称列表
    @return:
    (x_min, y_max)
    """
    x_min, y_max = float('inf'), float('-inf')
    x_max, y_min = float('-inf'), float('inf')
    filename_begin, filename_end = '', ''
    for i, image_name in enumerate(images_names_list):
        image_path = os.path.join(prefix, image_name)
        image_dataset = gdal.Open(image_path, GA_ReadOnly)
        image_geotransform = image_dataset.GetGeoTransform()
        if i == 1:
            x_min, x_max = image_geotransform[0], image_geotransform[0]
            y_max, y_min = image_geotransform[3], image_geotransform[3]
            filename_begin, filename_end = image_name, image_name
            continue
        if x_min > image_geotransform[0]:
            x_min = image_geotransform[0]
            filename_begin = image_name
        if x_max < image_geotransform[0]:
            x_max = image_geotransform[0]
            filename_end = image_name
        # y_max = max(y_max, image_geotransform[3])
        if y_max < image_geotransform[3]:
            y_max = image_geotransform[3]
            filename_end = image_name
        if y_min > image_geotransform[3]:
            y_min = image_geotransform[3]
            filename_end = image_name
    return (x_min, y_max), filename_begin, (x_max, y_min), filename_end

def get_begin_point_fun(prefix, images_names_list):
    """
    @function: 获取整个大图的起始点，即左上方(x_min, y_max)
    水平方向是x，往右增大，竖直方向是y，往下变小
    @params:
    prefix: 存放图片的文件夹名
    images_names_list: 图片名称列表
    @return:
    (x_min, y_max)
    """
    x_min, y_max = float('inf'), float('-inf')
    x_max, y_min = float('-inf'), float('inf')
    filename = ''
    for i, image_name in enumerate(images_names_list):
        image_path = os.path.join(prefix, image_name)
        image_dataset = gdal.Open(image_path, GA_ReadOnly)
        image_geotransform = image_dataset.GetGeoTransform()
        # per_x, per_y = image_geotransform[1], image_geotransform[5]
        x_min = min(x_min, image_geotransform[0])
        x_max = max(x_max, image_geotransform[0])
        y_max = max(y_max, image_geotransform[3])
        y_min = min(y_min, image_geotransform[3])
    return (x_min, y_max), (x_max, y_min)


def test_get_begin_point(prefix, images_names_list):
    """
    @function: 测试两个获取整个相关信息的函数运行对不对，实验证明是对的，后面就之间得到相应图片了，运行太卡了
    
    需要注意的是得到的最大值最小值并不一定是某一张图片的起始坐标，因为原图极有可能是不规则的
    """
    point_begin, filename_begin, point_end, filename_end = get_begin_point_if(prefix, images_names_list)
    print("起始点坐标：", point_begin, end="    ")
    print("文件名：", filename_begin)
    print("终止点坐标：", point_end, end="    ")
    print("文件名：", filename_end)
    # 起始点坐标： (14566667.913461864, 5401942.654253401)    文件名： 10740_img.tiff
    # 终止点坐标： (14647307.913461864, 5323862.654253401)    文件名： 11893_img.tiff
    point_begin, point_end = get_begin_point_fun(prefix, images_names_list)
    print("起始点坐标：", point_begin)
    print("终止点坐标：", point_end)
    # 起始点坐标： (14566667.913461864, 5401942.654253401)
    # 终止点坐标： (14647307.913461864, 5323862.654253401)


def make_array(prefix, filename_begin, filename_end):
    """
    @function: 根据起始和终止坐标创建一个三维矩阵
    """
    image_begin_dataset = gdal.Open(os.path.join(prefix, filename_begin), GA_ReadOnly)
    image_end_dataset = gdal.Open(os.path.join(prefix, filename_end), GA_ReadOnly)
    image_begin_geotransform, image_end_geotransform = image_begin_dataset.GetGeoTransform(), image_end_dataset.GetGeoTransform()
    image_begin_x, image_begin_y = image_begin_geotransform[0], image_begin_geotransform[3]
    image_end_x, image_end_y = image_end_geotransform[0], image_end_geotransform[3]
    image_end_width, image_end_height = image_end_dataset.RasterXSize, image_end_dataset.RasterYSize
    per_x, per_y = image_end_geotransform[1], image_end_geotransform[5]
    image_end_x, image_end_y = image_end_x + image_end_width * per_x, image_end_y + image_end_height * per_y
    whole_width, whole_height = (image_end_x - image_begin_x) / per_x, (image_end_y - image_begin_y) / per_y
    image_begin_x, image_begin_y = 14566667.913461864, 5401942.654253401
    image_end_x, image_end_y = 14647307.913461864, 5323862.654253401
    image_end_x, image_end_y = image_end_x + image_end_width * per_x, image_end_y + image_end_height * per_y
    whole_width, whole_height = (image_end_x - image_begin_x) / per_x, (image_end_y - image_begin_y) / per_y
    # print(whole_height, whole_width)
    return whole_height, whole_width


def make_colors(whole_height, whole_width, prefix, images_names_list, images_labels_list):
    image_begin_x, image_begin_y = 14566667.913461864, 5401942.654253401
    whole_array = np.zeros((3, int(whole_height), int(whole_width)))
    whole_per_x, whole_per_y = 0.0, 0.0
    whole_proj = None
    for num, image_name in enumerate(images_names_list):
        image_dataset = gdal.Open(os.path.join(prefix, image_name), GA_ReadOnly)
        if image_dataset is None:
            print("文件读写错误！！！")
            continue
        image_geotransform = image_dataset.GetGeoTransform()
        image_width, image_height = image_dataset.RasterXSize, image_dataset.RasterYSize
        image_x, image_y = image_geotransform[0], image_geotransform[3]
        per_x, per_y = image_geotransform[1], image_geotransform[5]
        whole_per_x, whole_per_y = per_x, per_y
        whole_proj = image_dataset.GetProjection()
        num_height, num_width = (image_y - image_begin_y) / per_y, (image_x - image_begin_x) / per_x
        if images_labels_list[num] == '0':
            whole_array[:, int(num_height):int(num_height+image_height), int(num_width):int(num_width+image_width)] = 192
        elif images_labels_list[num] == '1':
            whole_array[0, int(num_height):int(num_height+image_height), int(num_width):int(num_width+image_width)] = 255
        elif images_labels_list[num] == '2':
            whole_array[2, int(num_height):int(num_height+image_height), int(num_width):int(num_width+image_width)] = 255
    
    if 'int8' in whole_array.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in whole_array.dtype.name:
        datatype = gdal.GDT_UInt16
    elif 'float64' in whole_array.dtype.name:
        datatype = gdal.GDT_Float64
    else:
        datatype = gdal.GDT_Float32
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create('whole_pic.tiff', int(whole_width), int(whole_height), 3, datatype, options = ['BigTIFF=YES'])
    geotrans = (image_begin_x, whole_per_x, 0.0, image_begin_y, 0.0, whole_per_y)
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(whole_proj)
    for i in range(3):
        dataset.GetRasterBand(i + 1).WriteArray(whole_array[i, :, :])
    dataset.BuildOverviews('average', [2,4,8,16,32,64,128])
    dataset.FlushCache()
    del dataset
    print("save image success...")
    


def read_tif(prefix, image_name):
    image_path = os.path.join(prefix, image_name)
    image_dataset = gdal.Open(image_path, GA_ReadOnly)
    if image_dataset is None:
        print("文件读写错误！！！")
        return
    image_geotransform = image_dataset.GetGeoTransform()
    image_width, image_height = image_dataset.RasterXSize, image_dataset.RasterYSize
    image_data = image_dataset.ReadAsArray(0, 0, image_width, image_height)
    print(image_geotransform)
    print(image_width, image_height)
    print(image_data.shape)


if __name__ == "__main__":
    train_file_txt_path, predict_file_txt_path = "test\\Norighttrain20.txt", "test\\predict_result_vgg.txt"
    prefix = "test"
    images_names_list, images_labels_list = get_all_images_labels(train_file_txt_path, predict_file_txt_path)
    print("图片名称列表长度：", len(images_names_list))
    print("图片标签列表长度：", len(images_labels_list))
    # test_get_begin_point(prefix, images_names_list)
    filename_begin, filename_end = "10740_img.tiff", "11893_img.tiff"
    # read_tif(prefix, '00001_img.tiff')
    whole_height, whole_width = make_array(prefix, filename_begin, filename_end)
    make_colors(whole_height, whole_width, prefix, images_names_list, images_labels_list)
    