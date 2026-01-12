# by jolley
import sys

from PyQt5.QtWidgets import QApplication

from controller import KeyToolController
from model import KeyToolModel
from view import KeyToolView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # MVC三层初始化
    view = KeyToolView()
    model = KeyToolModel()
    controller = KeyToolController(view, model)
    view.show()
    sys.exit(app.exec_())