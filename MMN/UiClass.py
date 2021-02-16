import time

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QTableWidgetItem, QProgressBar

from MM import MM
from UI import Ui_UI


class UI(QWidget):

    def __init__(self):
        super().__init__()
        # 初始化模型
        self.mmn = None
        self.timeI = 0  # eventList的作用
        # 配置好 工具生成的UI
        self.ui = Ui_UI()
        self.ui.setupUi(self)
        self.initUI()
        # 设置一个定时器，用于实现业务逻辑
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.onTimeout)
        # 设置好状态
        self.status = 0  # 0 表示停止，1表示开始
        # 配置好 点击反应
        self.ui.RunBottom.clicked.connect(self.onClickRunButton)
        self.reset()

    def initUI(self):
        self.center()

        self.show()

    def onClickRunButton(self):
        self.reset()
        if self.status == 1:  # 已经开始了
            return
        if self.status == 0:  # 没有开始
            # 清理历史记录,读取录入参数是否合格
            arrive_time = 0
            serve_time = 0
            custom_num = 0
            table_number = 0
            max_number = 0
            if self.is_float(self.ui.AvgArriveTime.text()):
                arrive_time = float(self.ui.AvgArriveTime.text())
            if self.is_float(self.ui.AvgServeTime.text()):
                serve_time = float(self.ui.AvgServeTime.text())
            if self.ui.PeopleNumbers.text().isdigit():
                custom_num = int(self.ui.PeopleNumbers.text())
            if self.ui.TableNumbers.text().isdigit():
                table_number = int(self.ui.TableNumbers.text())
            if self.ui.MaxPeople.text().isdigit():
                max_number = int(self.ui.MaxPeople.text())
            custom_num = min(max_number, custom_num)  # 取最小值
            self.mmn = MM(arrive_time, serve_time, custom_num, table_number)
            self.ui.TableStatus.setRowCount(table_number)
            self.ui.TableStatus.setColumnCount(3)
            self.ui.TableStatus.setColumnWidth(0, 70)
            self.ui.TableStatus.setColumnWidth(1, 130)
            self.ui.TableStatus.setColumnWidth(2, 70)
            self.ui.TableStatus.setHorizontalHeaderLabels(("窗口ID", "利用率", "当前状态"))
            self.reset()
            self.mmn.produce()
            self.mmn.leave()
            self.mmn.eventTime = list(set(self.mmn.eventTime))
            self.mmn.eventTime.sort()  # 从小到大排列

            for i in range(0, table_number):
                self.ui.TableStatus.setItem(i, 0, QTableWidgetItem("%d" % 1))  # 设置id
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(0)
                is_busy = "空闲"
                if self.mmn.tableList[i].is_use == 1:
                    is_busy = "占用"
                self.ui.TableStatus.setCellWidget(i, 1, bar)
                self.ui.TableStatus.setItem(i, 2, QTableWidgetItem(is_busy))

            self.status = 1  # 开始
            self.timer.start()

    # 控制窗口显示在屏幕中心的方法
    def center(self):
        # 获得窗口
        qr = self.frameGeometry()
        # 获得屏幕中心点
        cp = QDesktopWidget().availableGeometry().center()
        # 显示到屏幕中心
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def reset(self):  # 复位
        self.ui.EventList.clear()
        self.ui.TableStatus.clear()
        self.ui.WaitPeopleNum.clear()
        self.ui.AvgWaitTime.clear()

        self.update()

    def onTimeout(self):
        if self.timeI == len(self.mmn.eventTime):  # 结束了
            self.timer.stop()
        else:
            str = self.mmn.run(self.timeI)
            self.ui.NowTime.setText("%.2f" % self.mmn.now_time)
            self.ui.AvgWaitTime.setText("%.2f" % self.mmn.average_wait_time)
            self.ui.WaitPeopleNum.setText("%.2f" % self.mmn.average_people_number)

            self.ui.EventList.addItem(str)
            index = self.ui.EventList.count() - 1
            self.ui.EventList.setCurrentRow(index)
            for i in range(0, self.mmn.table_number):
                device = self.mmn.tableList[i]
                bar = self.ui.TableStatus.cellWidget(i, 1)
                bar.setValue(device.use_ratio * 100)
                self.ui.TableStatus.setCellWidget(i, 1, bar)
                is_busy = "空闲"
                if device.is_use:
                    is_busy = "正忙"
                self.ui.TableStatus.setItem(i, 2, QTableWidgetItem(is_busy))

            self.timeI = self.timeI + 1

    @staticmethod
    def is_float(s: str) -> bool:
        if s.count('.') > 1:
            return False
        parts = s.split('.')
        for part in parts:
            if not part.isdigit():
                return False
        return True
