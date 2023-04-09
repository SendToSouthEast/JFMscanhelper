from PyQt5 import QtWidgets, QtCore
import sys
import json
from pathlib import Path

import picProc
import keyboardWatcher
import IMGFileControl

class ScanGUI(QtWidgets.QWidget):
    def __init__(self, keyboardWatcher, IMGFileControl, picProc):
        super().__init__()

        self.STATE_WAITING_FOR_USER_ACTION = 0
        self.STATE_SCANNING_SUB_PAGE = 1  # 初级页面
        self.STATE_SCANNING_ADV_PAGE = 2  # 高级页面


        self.keyboardWatcher = keyboardWatcher
        self.IMGFileControl = IMGFileControl
        self.picProc = picProc


        self.setWindowTitle("扫描仪控制程序")
        self.book_no = QtWidgets.QSpinBox(self)
        self.adv_page = QtWidgets.QSpinBox(self)
        self.sub_page = QtWidgets.QSpinBox(self)
        self.out_imgpath = ""
        self.in_imgpath = ""

        self.scan_adv_button = QtWidgets.QPushButton("扫描高级页面", self)
        self.scan_sub_button = QtWidgets.QPushButton("扫描次级页面", self)
        self.scan_clean_button = QtWidgets.QPushButton("清空", self)
        self.scan_save_button = QtWidgets.QPushButton("保存扫描位置", self)
        self.result_text = QtWidgets.QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setFixedSize(800, 800)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #e0e0e0")
        self.out_imgpath_edit = QtWidgets.QLineEdit(self)
        self.out_browse_button = QtWidgets.QPushButton("浏览", self)
        self.in_imgpath_edit = QtWidgets.QLineEdit(self)
        self.in_browse_button = QtWidgets.QPushButton("浏览", self)
        self.scanState = self.STATE_WAITING_FOR_USER_ACTION

        # Check if JSON file exists, then load data
        json_file = Path("scan_positions.json")
        if json_file.exists():
            with json_file.open("r") as f:
                data = json.load(f)
                self.adv_page.setValue(data["adv_page"])
                self.sub_page.setValue(data["sub_page"])
                self.book_no.setValue(data["book_no"])
                self.out_imgpath = data["out_imgpath"]
                self.out_imgpath_edit.setText(self.out_imgpath)
                self.in_imgpath = data["in_imgpath"]
                self.in_imgpath_edit.setText(self.in_imgpath)


        grid = QtWidgets.QGridLayout(self)
        grid.addWidget(QtWidgets.QLabel("本数编号："), 0, 0)
        grid.addWidget(self.book_no, 0, 1)
        grid.addWidget(QtWidgets.QLabel("高级页码："), 1, 0)
        grid.addWidget(self.adv_page, 1, 1)
        grid.addWidget(QtWidgets.QLabel("次级页码："), 2, 0)
        grid.addWidget(self.sub_page, 2, 1)
        grid.addWidget(QtWidgets.QLabel("扫描输出路径："), 3, 0)
        grid.addWidget(self.out_imgpath_edit, 3, 1)
        grid.addWidget(self.out_browse_button, 3, 2)
        grid.addWidget(QtWidgets.QLabel("扫描输入路径："), 4, 0)
        grid.addWidget(self.in_imgpath_edit, 4, 1)
        grid.addWidget(self.in_browse_button, 4, 2)
        grid.addWidget(self.scan_adv_button, 5, 0)
        grid.addWidget(self.scan_sub_button, 5, 1)
        grid.addWidget(self.scan_clean_button, 6, 0)
        grid.addWidget(self.scan_save_button, 6, 1)
        grid.addWidget(self.result_text, 7, 0, 1, 3)
        grid.addWidget(self.image_label, 0, 3, 8, 1)

        # Connect signals and slots
        self.in_browse_button.clicked.connect(self.in_browse_path)
        self.out_browse_button.clicked.connect(self.out_browse_path)
        self.scan_save_button.clicked.connect(lambda: self.save_scan_position(True))
        self.scan_clean_button.clicked.connect(self.scan_clean)

        self.scan_adv_button.clicked.connect(lambda: self.scan_page(self.STATE_SCANNING_ADV_PAGE))
        self.scan_sub_button.clicked.connect(lambda: self.scan_page(self.STATE_SCANNING_SUB_PAGE))

    def scanInit(self):
        self.IMGFileControl.delete_all_files()
        self.result_text.append("欢迎使用JFM辅助扫描程序")
        self.result_text.append("请先在扫描仪窗口的“开始扫描”按键的位置按下空格，程序会监听到位置，以半自动扫描")

    def check_inputs(self):
        if not all(isinstance(x, int) and x >= 0 for x in
                   [self.book_no.value(), self.adv_page.value(), self.sub_page.value()]):
            self.result_text.append("页码请输入大于等于0的整数")
            return False
        if not all(isinstance(x, str) and x.strip() for x in [self.out_imgpath, self.in_imgpath]):
            self.result_text.append("请选择路径")
            return False
        return True

    def scan_page(self, scan_state):
        if self.check_inputs():
            if self.keyboardWatcher.clickScanButton():
                ori_book_no = self.book_no.value()
                ori_adv_page = self.adv_page.value()
                ori_sub_page = self.sub_page.value()

                if scan_state == self.STATE_SCANNING_ADV_PAGE:
                    self.adv_page.setValue(ori_adv_page + 1)
                    self.sub_page.setValue(1)
                elif scan_state == self.STATE_SCANNING_SUB_PAGE:
                    self.sub_page.setValue(ori_sub_page + 1)

                ori_book_no = self.book_no.value()
                ori_adv_page = self.adv_page.value()
                ori_sub_page = self.sub_page.value()

                if scan_state == self.STATE_SCANNING_ADV_PAGE:
                    self.result_text.append(
                        "扫描高级页面：本数编号 {}，高级页码 {}，次级页码 {}"
                            .format(ori_book_no, ori_adv_page, ori_sub_page))
                elif scan_state == self.STATE_SCANNING_SUB_PAGE:
                    self.result_text.append(
                        "扫描次级页面：本数编号 {}，高级页码 {}，次级页码 {}"
                            .format(ori_book_no, ori_adv_page, ori_sub_page))
                self.scanState = scan_state
                self.save_scan_position(False)
                self.enableScanButton(False)

    def out_browse_path(self):
        img_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择扫描输出路径")
        if img_path:
            self.out_imgpath_edit.setText(img_path)
            self.out_imgpath = img_path
    def in_browse_path(self):
        img_path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择扫描输入路径")
        if img_path:
            self.in_imgpath_edit.setText(img_path)
            self.in_imgpath = img_path


    def scan_clean(self):
        self.IMGFileControl.delete_all_files()
        self.picProc.cleanIMG()
        self.scanState = self.STATE_WAITING_FOR_USER_ACTION
        self.enableScanButton(True)



    def enableScanButton(self,state):
        self.scan_adv_button.setEnabled(state)
        self.scan_sub_button.setEnabled(state)
        self.out_imgpath_edit.setEnabled(state)
        self.out_browse_button.setEnabled(state)
        self.in_imgpath_edit.setEnabled(state)
        self.in_browse_button.setEnabled(state)


    def scanFinishUIProcessing(self):
        ori_book_no = self.book_no.value()
        ori_adv_page = self.adv_page.value()
        ori_sub_page = self.sub_page.value()



        target_filename = "{}_{}_{}.jpg".format(ori_book_no, ori_adv_page, ori_sub_page)
        self.scanState = self.STATE_WAITING_FOR_USER_ACTION
        self.enableScanButton(True)

        return target_filename


    def save_scan_position(self,iflog):
        # Save scan positions to JSON file
        data = {
            "adv_page": self.adv_page.value(),
            "sub_page": self.sub_page.value(),
            "book_no": self.book_no.value(),
            "out_imgpath": self.out_imgpath,
            "in_imgpath":self.in_imgpath
        }
        with open("scan_positions.json", "w") as f:
            json.dump(data, f)

        if iflog:
            self.result_text.append("扫描位置已被保存至scan_positions.json")






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ScanGUI = ScanGUI(None,None,None)

    picProc = picProc.picProc(ScanGUI)
    keyboardWatcher = keyboardWatcher.keyboardWatcher(ScanGUI)
    IMGFileControl = IMGFileControl.IMGFileControl(ScanGUI,picProc)

    ScanGUI.keyboardWatcher = keyboardWatcher
    ScanGUI.IMGFileControl = IMGFileControl
    ScanGUI.picProc = picProc

    ScanGUI.scanInit()
    ScanGUI.show()
    #picProc.picEdit("E:/Projects/33diaryscan/pythonScan/test/1_0_1.jpg")
    app.exec_()