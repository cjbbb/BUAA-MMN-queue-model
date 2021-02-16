import sys

from PyQt5.QtWidgets import QApplication

from UiClass import UI

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = UI()
    w.show()

    sys.exit(app.exec_())
