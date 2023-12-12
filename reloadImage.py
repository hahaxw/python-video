import os

from PIL import Image


#获取路径

#获取指定下的所有文件名称
def get_image_files(folder_path):
    image_files = []

    # 列出文件夹中的所有文件
    files = os.listdir(folder_path)

    for file in files:
        # 拼接文件的完整路径
        file_path = os.path.join(folder_path, file)

        # 检查文件是否为图像文件
        try:
            img = Image.open(file_path)
            # 如果没有抛出异常，则文件是图像文件
            image_files.append(file)
        except (OSError, IOError):
            # 文件不是图像文件，忽略
            pass

    return image_files

# 指定文件夹路径
# folder_path = "D:\\video\\python\\processFile\\image"
#
# # 获取图像文件名列表
# image_files = get_image_files(folder_path)
#
# # 打印图像文件名列表
# print(image_files)
