# -*- coding: utf-8 -*-
# !/usr/bin/env python
# @Time    : 2018/11/17 16:04
# @Author  : xhh
# @Desc    : 通过直方图计算图片的相似度
# @File    : difference_image_hist.py
# @Software: PyCharm
from PIL import Image


# 将图片转化为RGB
def make_regalur_image(img, size=(64, 64)):
    gray_image = img.resize(size).convert('RGB')
    return gray_image


# 计算直方图
def hist_similar(lh, rh):
    assert len(lh) == len(rh)
    hist = sum(1 - (0 if l == r else float(abs(l - r)) / max(l, r)) for l, r in zip(lh, rh)) / len(lh)
    return hist


# 计算相似度
def calc_similar(li, ri):
    calc_sim = hist_similar(li.histogram(), ri.histogram())
    return calc_sim


if __name__ == '__main__':
    image1 = Image.open('D:\\video\\ceshi1.jpg')
    image1 = make_regalur_image(image1)
    image2 = Image.open('D:\\video\\ceshi2.jpg')
    image2 = make_regalur_image(image2)
    print("图片间的相似度为", calc_similar(image1, image2))

