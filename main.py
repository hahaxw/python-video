# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import concurrent
import os
import videoFrameExtraction
import reloadImage
import imageHash
from concurrent.futures import ThreadPoolExecutor

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助


def workerImageMaxScore(futuresArray):
    print(f"获取最大分数 {futuresArray} 开始")
    # 获取结果
    subResults = [future.result() for future in concurrent.futures.as_completed(futuresArray)]
    max_score = max(subResults)
    print(f"获取最大分数 {max_score} 结束")
    return max_score