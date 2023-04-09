from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
import os
import re
import cv2
import numpy as np


class picProc:
    def __init__(self, ScanGUI):
        self.ScanGUI = ScanGUI
        self.width = 800
        self.height = 800
        self.display_height = 800
        self.display_width = 800
        self.radio = 1
        self.points = []
        self.img_path = ""


    def picEdit(self, img_path):
        # 显示图片
        self.img_path = img_path
        self.display_image = cv2.imread(self.img_path)

        # 计算缩放比例
        h, w, _ = self.display_image.shape
        self.radio = min(self.width / w, self.height / h)
        self.display_height, self.display_width = int(h * self.radio), int(w * self.radio)
        # 缩放图像
        self.display_image = cv2.resize(self.display_image, (self.display_width, self.display_height))
        pixmap = QPixmap.fromImage(QImage(self.display_image.data, self.display_width, self.display_height, QImage.Format_RGB888))
        self.ScanGUI.image_label.setPixmap(pixmap)
        self.ScanGUI.image_label.setAlignment(Qt.AlignTop)

        # 点击四个点
        self.ScanGUI.result_text.append("请在图片上点击四个点，以选择裁剪区域。")
        self.ScanGUI.image_label.mousePressEvent = self.get_points

    def get_points(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.points.append([x, y])
        self.ScanGUI.result_text.append("已选择第%d个点：(%d,%d)" % (len(self.points), x, y))

        p1 = (x, y)
        cv2.circle(self.display_image, p1, 1, (0, 255, 0), 2)
        if len(self.points) > 1:
            print(tuple(self.points[len(self.points) - 2]))
            cv2.line(self.display_image, p1, tuple(self.points[len(self.points) - 2]), (0, 255, 0),2)

        if len(self.points) == 4:
            cv2.line(self.display_image, tuple(self.points[len(self.points) - 1]), tuple(self.points[0]), (0, 255, 0), 2)


        pixmap = QPixmap.fromImage(QImage(self.display_image.data, self.display_width, self.display_height, QImage.Format_RGB888))
        self.ScanGUI.image_label.setPixmap(pixmap)

        if len(self.points) == 4:
            self.ScanGUI.image_label.mousePressEvent = None
            self.crop_and_save()

    def order_points(self, pts):
        # 初始化坐标点
        rect = np.zeros((4, 2), dtype='float32')

        # 获取左上角和右下角坐标点
        s = pts.sum(axis=1)  # 每行像素值进行相加；若axis=0，每列像素值相加
        rect[0] = pts[np.argmin(s)]  # top_left,返回s首个最小值索引，eg.[1,0,2,0],返回值为1
        rect[2] = pts[np.argmax(s)]  # bottom_left,返回s首个最大值索引，eg.[1,0,2,0],返回值为2

        # 分别计算左上角和右下角的离散差值
        diff = np.diff(pts, axis=1)  # 第i+1列减第i列
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def four_point_transform(self, pts):
        print(pts)
        # 获取坐标点，并将它们分离开来
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # 计算新图片的宽度值，选取水平差值的最大值
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # 计算新图片的高度值，选取垂直差值的最大值
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # 构建新图片的4个坐标点,左上角为原点
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # 获取透视变换矩阵并应用它
        M = cv2.getPerspectiveTransform(rect, dst)
        # 进行透视变换

        return M, (maxWidth, maxHeight)

    def crop_and_save(self):
        # 将points转换为左上、右上、右下、左下排列的列表
        points = self.points.copy()

        # 按照比例还原为原图像坐标
        img = cv2.imread(self.img_path)

        points = [[int(x / self.radio), int(y / self.radio)] for (x, y) in points]
        points = np.array(points, dtype=np.float32)
        # 定义变换矩阵
        M, WH = self.four_point_transform(points)

        # 进行透视变换
        cropped_img = cv2.warpPerspective(img, M, WH)
        # 保存为原图片
        cv2.imwrite(self.img_path, cropped_img)
        #cv2.imwrite("img.png", cropped_img)

        self.ScanGUI.result_text.append("裁剪后的图片已保存为%s" % self.img_path)
        self.points = []

        ed_img_path = self.img_path
        ed_display_image = cv2.imread(ed_img_path)

        #计算缩放比例
        h, w, _ = ed_display_image.shape
        ed_radio = min(self.width / w, self.height / h)
        ed_display_height, ed_display_width = int(h * ed_radio), int(w * ed_radio)

        #缩放图像
        ed_display_image = cv2.resize(ed_display_image, (ed_display_width, ed_display_height))
        pixmap = QPixmap.fromImage(
            QImage(ed_display_image.data, ed_display_width, ed_display_height, QImage.Format_RGB888))
        self.ScanGUI.image_label.setPixmap(pixmap)
        self.ScanGUI.image_label.setAlignment(Qt.AlignTop)

    def cleanIMG(self):
        self.points = []
        self.ScanGUI.image_label.clear()


