# -*- coding: utf-8 -*-
import cv2


# Hash值对比
def cmpHash(hash1, hash2,shape=(10,10)):
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1)!=len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 相等则n计数+1，n最终为相似度
        if hash1[i] == hash2[i]:
            n = n + 1
    return n/(shape[0]*shape[1])
# 差值感知算法
def dHash(cv2,img,shape=(10,10)):
    # 缩放10*11
    img = cv2.resize(img, (shape[0]+1, shape[1]))
    # 转换灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hash_str = ''
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(shape[0]):
        for j in range(shape[1]):
            if gray[i, j] > gray[i, j + 1]:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str

def comparison_hash_image(primaryFileName, processFileName):
    img1 = cv2.imread(primaryFileName)
    img2 = cv2.imread(processFileName)

    hash1 = dHash(cv2,img1)
    hash2 = dHash(cv2,img2)
    n = cmpHash(hash1, hash2) * 100
    return n

#直接使用img对象比较，预先全部读取出来，提高性能
def comparison_hash_imread(img1, img2):
    hash1 = dHash(cv2,img1)
    hash2 = dHash(cv2,img2)
    n = cmpHash(hash1, hash2) * 100
    return n

# if __name__=="__main__":
#     n = comparison_hash_image('D:\\video\\python\\primaryFile\\image\\frame_0001.jpg', 'D:\\video\\python\\processFile\\image\\frame_0001.jpg')
#     print('均值哈希算法相似度：', n)

