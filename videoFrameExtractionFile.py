import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from flask import Flask, render_template, request

import imageHash
import reloadImage
import videoFrameExtraction
import cv2

executor = ThreadPoolExecutor(max_workers=16)

executor_sub = ThreadPoolExecutor(max_workers=64)

app = Flask(__name__)

# 端口号
APP_PORT = 5000
app.config['APP_PORT'] = APP_PORT

# 原视频保存路径
PRIMARY_FILE_UPLOAD_FOLDER = '\\video\\python_{}\\primaryFile\\video\\'.format(APP_PORT)
app.config['PRIMARY_FILE_UPLOAD_FOLDER'] = PRIMARY_FILE_UPLOAD_FOLDER
# 原视频图片保存路径
PRIMARY_FILE_UPLOAD_FOLDER_IMAGE = '\\video\\python_{}\\primaryFile\\image\\'.format(APP_PORT)
app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE'] = PRIMARY_FILE_UPLOAD_FOLDER_IMAGE

# 剪辑后的视频保存路径
PROCESS_FILE_UPLOAD_FOLDER = '\\video\\python_{}\\processFile\\video\\'.format(APP_PORT)
app.config['PROCESS_FILE_UPLOAD_FOLDER'] = PROCESS_FILE_UPLOAD_FOLDER
# 剪辑后视频图片保存路径
PROCESS_FILE_UPLOAD_FOLDER_IMAGE = '\\video\\python_{}\\processFile\\image\\'.format(APP_PORT)
app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE'] = PROCESS_FILE_UPLOAD_FOLDER_IMAGE

# 设置允许上传的文件类型
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#返回首页
@app.route('/')
def index():
    return render_template('index.html')


#文件处理方法
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            start_time = time.time()
            delete_folder(app.config['PRIMARY_FILE_UPLOAD_FOLDER'])
            delete_folder(app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE'])
            delete_folder(app.config['PROCESS_FILE_UPLOAD_FOLDER'])
            delete_folder(app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE'])
            create_folder_if_not_exists(app.config['PRIMARY_FILE_UPLOAD_FOLDER'])
            create_folder_if_not_exists(app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE'])
            create_folder_if_not_exists(app.config['PROCESS_FILE_UPLOAD_FOLDER'])
            create_folder_if_not_exists(app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE'])

            # 检查文件是否存在于请求中
            if 'primaryMultipartFile' not in request.files:
                return render_template('index.html', message='原视频无文件')
            # 检查文件是否存在于请求中
            if 'processMultipartFile' not in request.files:
                return render_template('index.html', message='剪辑后的视频无文件')

            # 原视频文件
            primary_file = request.files['primaryMultipartFile']
            upload_primary_file(primary_file)
            video_path = app.config['PRIMARY_FILE_UPLOAD_FOLDER'] + primary_file.filename
            primary_output_folder = app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE']
            videoFrameExtraction.extract_frames(video_path, primary_output_folder)

            # 剪辑后的视频文件
            process_file = request.files['processMultipartFile']
            upload_process_file(process_file)
            video_path = app.config['PROCESS_FILE_UPLOAD_FOLDER'] + process_file.filename
            process_output_folder = app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE']
            videoFrameExtraction.extract_frames(video_path, process_output_folder)

            # 进行imageHash值对比
            primary_image_files = reloadImage.get_image_files(primary_output_folder)
            process_image_files = reloadImage.get_image_files(process_output_folder)

            #原视频图片
            futures_primary = []
            for primary_image_file in primary_image_files:
                primary_file_name = primary_output_folder + primary_image_file
                future = executor.submit(worker_imread, primary_file_name)
                futures_primary.append(future)

            # 剪辑后视频图片
            futures_process = []
            for process_image_file in process_image_files:
                process_file_name = process_output_folder + process_image_file
                future = executor_sub.submit(worker_process_imread, process_file_name)
                futures_process.append(future)

            # 原视频图片对象
            futures_primary_images = []
            for future in futures_primary:
                futures_primary_images.append(future.result())

            # 剪辑后视频图片对象
            process_img_array = []
            for future in futures_process:
                process_img_array.append(future.result())

            futures_arrays = []
            for process_img in process_img_array:
                futures = executor.submit(worker_image_max_score, futures_primary_images, process_img)
                futures_arrays.append(futures)

            # i = 1
            results = []
            for futures_array in futures_arrays:
                score = futures_array.result()
                results.append(score)

            result_max = max(results)
            result_min = min(results)
            result_avg = round(np.mean(results), 2)
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print(f"对比结果平均值：{result_avg} 最大值：{result_max} 最小值：{result_min} 耗时：{elapsed_time}秒")
            message_result = "<p style='font-size:50px;'>原视频名称：{} 剪辑后的视频名称：{} 上传文件处理成功！</p><p style='font-size:50px;'>对比结果平均值：{} 最大值：{} 最小值：{} 耗时：{}秒</p>".format(
                primary_file.filename,
                process_file.filename,
                result_avg,
                result_max,
                result_min,
                elapsed_time)
            return render_template('success.html', message=message_result)
        except Exception as e:
            print(f"视频对比出现异常：{e}")
            return render_template('success.html', message="视频对比出现异常...")
    return render_template('index.html')


# 上传原视频文件
def upload_primary_file(file):
    # 如果用户没有选择文件，提交空表单
    if file.filename == '':
        return render_template('index.html', message='原视频未选择文件')

    # 如果文件存在并且是允许的文件类型，保存文件
    if file and allowed_file(file.filename):
        # 保存上传的文件
        file_path = os.path.join(app.config['PRIMARY_FILE_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)


# 上传剪辑后的视频文件
def upload_process_file(file):
    # 如果用户没有选择文件，提交空表单
    if file.filename == '':
        return render_template('index.html', message='剪辑后的视频未选择文件')

    # 如果文件存在并且是允许的文件类型，保存文件
    if file and allowed_file(file.filename):
        # 保存上传的文件
        file_path = os.path.join(app.config['PROCESS_FILE_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)


# 多线程获取最大分数值
def worker_image_max_score(futures_primary_images, process_img):
    future_array = []
    for futures_primary_image in futures_primary_images:
        future = executor_sub.submit(worker_image_score, futures_primary_image, process_img.img)
        future_array.append(future)

    score_array = []
    for future in future_array:
        score = future.result()
        score_array.append(round(score, 2))
    max_score = max(score_array)
    print(f"获取最大分数 {process_img.file_path_name} {max_score} 结束")
    return max_score


def worker_image_score(primary_file_name_image, process_file_name_image):
    score = imageHash.comparison_hash_imread(primary_file_name_image, process_file_name_image)
    return score

#读取剪辑后视频图片img
def worker_process_imread(file_path_name):
    img = cv2.imread(file_path_name)
    process_img = Process_img(img, file_path_name)
    return process_img

#读取原视频图片img
def worker_imread(file_path_name):
    img = cv2.imread(file_path_name)
    return img

# 删除文件夹下的文件
def delete_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' and its contents deleted successfully.")
    except OSError as e:
        print(f"Error deleting folder '{folder_path}': {e}")


# 如果不存在该文件夹则创建
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            print(f"Error creating folder '{folder_path}': {e}")
    else:
        print(f"Folder '{folder_path}' already exists.")

#剪辑后的视频图片对象包含路径和img
class Process_img:
    img = None
    file_path_name = None

    # 构造方法，用于初始化对象的属性
    def __init__(self, img, file_path_name):
        self.img = img
        self.file_path_name = file_path_name

if __name__ == '__main__':
    app.run(debug=True, port=APP_PORT)
