import mouse
import keyboard


class keyboardWatcher:

    def __init__(self, ScanGUI):
        self.ScanGUI = ScanGUI
        self.ScanButtonPosi = None  # 初始化时没有记录扫描按键坐标

        keyboard.on_press(self.on_press)  # 注册键盘事件

    def on_press(self, event):
        if event.name == "space":  # 空格键
            self.ScanButtonPosi = mouse.get_position()  # 记录鼠标位置
            self.ScanGUI.result_text.append("已记录扫描按键坐标")  # 输出日志
        elif event.name == "left":  # 左方向键
            self.ScanGUI.scan_page(self.ScanGUI.STATE_SCANNING_ADV_PAGE)
        elif event.name == "right":  # 右方向键
            self.ScanGUI.scan_page(self.ScanGUI.STATE_SCANNING_SUB_PAGE)

    def clickScanButton(self):
        if self.ScanButtonPosi is None:  # 如果没有记录扫描按键坐标
            self.ScanGUI.result_text.append("未设置扫描按键坐标")
            return False
        else:
            current_posi = mouse.get_position()  # 记录当前鼠标位置
            mouse.move(*self.ScanButtonPosi)  # 移动鼠标到扫描按键位置
            mouse.click()  # 模拟点击扫描按键
            mouse.move(*current_posi)  # 将鼠标移回原位
            return True