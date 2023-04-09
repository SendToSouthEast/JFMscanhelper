import os
import threading
import time
from shutil import move


class IMGFileControl:
    def __init__(self, ScanGUI, picProc):
        self.ScanGUI = ScanGUI
        self.picProc = picProc
        self.thread = threading.Thread(target=self._check_folder)
        self.thread.start()

    def _check_folder(self):
        while True:
            if self.ScanGUI.scanState == self.ScanGUI.STATE_SCANNING_SUB_PAGE \
                    or self.ScanGUI.scanState == self.ScanGUI.STATE_SCANNING_ADV_PAGE:

                files = os.listdir(self.ScanGUI.in_imgpath)
                if len(files) >= 2:
                    self.ScanGUI.result_text.append("存在多个不符合要求的文件，请手动处理。")
                elif len(files) == 1:
                    time.sleep(1)
                    self.ScanGUI.result_text.append("识别到扫描文件，本页扫描结束")
                    file_path = os.path.join(self.ScanGUI.in_imgpath, files[0])
                    new_name = self.ScanGUI.scanFinishUIProcessing()
                    new_path = self.ScanGUI.out_imgpath
                    new_file_path = os.path.join(new_path, new_name)
                    move(file_path, new_file_path)
                    self.picProc.picEdit(new_file_path)



    def delete_all_files(self):
        files = os.listdir(self.ScanGUI.in_imgpath)
        for file in files:
            os.remove(os.path.join(self.ScanGUI.in_imgpath, file))
