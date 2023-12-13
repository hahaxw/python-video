import os

import cv2
import time
from concurrent.futures import ThreadPoolExecutor

#视频抽帧

executor_sub = ThreadPoolExecutor(max_workers=64)

def extract_frames(video_path, output_folder):

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 获取视频帧率
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 获取视频帧的宽度和高度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 计算视频总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频帧率: {fps}")
    print(f"视频分辨率: {width} x {height}")
    print(f"总帧数: {total_frames}")

    start_time = time.time()
    # 逐帧读取视频并保存为图像文件
    frame_count = 0
    frame_future_array = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        future = executor_sub.submit(worker_frame, output_folder, frame_count, frame)
        frame_future_array.append(future)

    for future in frame_future_array:
        future.result()

    # 释放视频捕获对象
    cap.release()
    end_time = time.time() - start_time
    print(f"抽取了 {frame_count} 帧，保存在 {output_folder} 中，总耗时：{end_time}秒。")


#异步抽帧
def worker_frame(output_folder, frame_count, frame):
    frame_filename = os.path.join(output_folder, f"frame_{frame_count:04d}.jpg")
    cv2.imwrite(frame_filename, frame)
    return 1

# 视频文件路径
# video_path = "D:\\video\\processFile\\video\\1_1.mp4"

# 输出文件夹路径
# output_folder = "D:\\video\\processFile\\image"

# 执行抽帧操作
# extract_frames(video_path, output_folder)
