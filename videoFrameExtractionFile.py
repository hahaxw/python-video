import os
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from flask import Flask, render_template, request

import imageHash
import reloadImage
import videoFrameExtraction

executor = ThreadPoolExecutor(max_workers=16)

executor_sub = ThreadPoolExecutor(max_workers=64)

app = Flask(__name__)

#原视频保存路径
PRIMARY_FILE_UPLOAD_FOLDER = '\\video\\python\\primaryFile\\video\\'
app.config['PRIMARY_FILE_UPLOAD_FOLDER'] = PRIMARY_FILE_UPLOAD_FOLDER
#原视频图片保存路径
PRIMARY_FILE_UPLOAD_FOLDER_IMAGE = '\\video\\python\\primaryFile\\image\\'
app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE'] = PRIMARY_FILE_UPLOAD_FOLDER_IMAGE

#剪辑后的视频保存路径
PROCESS_FILE_UPLOAD_FOLDER = '\\video\\python\\processFile\\video\\'
app.config['PROCESS_FILE_UPLOAD_FOLDER'] = PROCESS_FILE_UPLOAD_FOLDER
#剪辑后视频图片保存路径
PROCESS_FILE_UPLOAD_FOLDER_IMAGE = '\\video\\python\\processFile\\image\\'
app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE'] = PROCESS_FILE_UPLOAD_FOLDER_IMAGE

# 设置允许上传的文件类型
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        start_time = time.time()
        # 检查文件是否存在于请求中
        if 'primaryMultipartFile' not in request.files:
            return render_template('index.html', message='原视频无文件')
        # 检查文件是否存在于请求中
        if 'processMultipartFile' not in request.files:
            return render_template('index.html', message='剪辑后的视频无文件')

        #原视频文件
        file = request.files['primaryMultipartFile']
        upload_primary_file(file)
        video_path = app.config['PRIMARY_FILE_UPLOAD_FOLDER'] + file.filename
        primary_output_folder = app.config['PRIMARY_FILE_UPLOAD_FOLDER_IMAGE']
        videoFrameExtraction.extract_frames(video_path, primary_output_folder)

        #剪辑后的视频文件
        file = request.files['processMultipartFile']
        upload_process_file(file)
        video_path = app.config['PROCESS_FILE_UPLOAD_FOLDER'] + file.filename
        process_output_folder = app.config['PROCESS_FILE_UPLOAD_FOLDER_IMAGE']
        videoFrameExtraction.extract_frames(video_path, process_output_folder)

        #进行imageHash值对比
        primary_image_files = reloadImage.get_image_files(primary_output_folder)
        process_image_files = reloadImage.get_image_files(process_output_folder)

        futures_arrays = []
        for process_image_file in process_image_files:
            processFileName = process_output_folder + process_image_file
            futures = executor.submit(worker_image_max_score, primary_output_folder, primary_image_files, processFileName)
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
        print(f"对比结果平均值：{result_avg} 最大值：{result_max} 最小值：{result_min} 耗时：{elapsed_time}")
        message_result = "对比结果平均值：{} 最大值：{} 最小值：{} 耗时：{}".format(result_avg, result_max, result_min, elapsed_time)
        return render_template('success.html', message = message_result)
    return render_template('index.html')

#上传原视频文件
def upload_primary_file(file):
    # 如果用户没有选择文件，提交空表单
    if file.filename == '':
        return render_template('index.html', message='原视频未选择文件')

    # 如果文件存在并且是允许的文件类型，保存文件
    if file and allowed_file(file.filename):
        # 保存上传的文件
        file_path = os.path.join(app.config['PRIMARY_FILE_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # return render_template('index.html', message='原视频文件上传成功')

#上传剪辑后的视频文件
def upload_process_file(file):
    # 如果用户没有选择文件，提交空表单
    if file.filename == '':
        return render_template('index.html', message='剪辑后的视频未选择文件')

    # 如果文件存在并且是允许的文件类型，保存文件
    if file and allowed_file(file.filename):
        # 保存上传的文件
        file_path = os.path.join(app.config['PROCESS_FILE_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # return render_template('index.html', message='剪辑后的视频文件上传成功')

#多线程获取最大分数值
def worker_image_max_score(primary_output_folder, primary_image_files, process_file_name):
    # print(f"获取最大分数 {processFileName} 开始")

    future_array = []
    for primary_image_file in primary_image_files:
        primary_file_name = primary_output_folder + primary_image_file
        future = executor_sub.submit(worker_image_score, primary_file_name, process_file_name)
        future_array.append(future)
        # score = imageHash.comparisonHashImage(primaryFileName, processFileName)

    score_array = []
    for future in future_array:
        score = future.result()
        score_array.append(round(score, 2))
    max_score = max(score_array)
    print(f"获取最大分数 {process_file_name} {max_score} 结束")
    return max_score

def worker_image_score(primary_file_name, process_file_name):
    score = imageHash.comparison_hash_image(primary_file_name, process_file_name)
    return score

if __name__ == '__main__':
    app.run(debug=True)
