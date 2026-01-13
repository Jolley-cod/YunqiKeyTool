# by jolley
import webbrowser

from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
                             QWidget)


class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(60, 40, 60, 40)
        self.setStyleSheet("background-color: #f8f9fa;")

        # 标题
        title_label = QLabel("云栖按键工具 - 关于作者")
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #333333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(15)

        # 按钮统一尺寸
        btn_width = 180
        btn_height = 40

        # 博客按钮
        self.jump_btn = QPushButton("访问我的博客")
        self.jump_btn.setFixedSize(QSize(btn_width, btn_height))
        self.jump_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #2E7D32;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1B5E20;
                transform: scale(1.05);
            }
        """)
        self.jump_btn.clicked.connect(lambda: webbrowser.open("https://www.0cv.com"))
        main_layout.addWidget(self.jump_btn, alignment=Qt.AlignCenter)

        # GitHub按钮
        self.jump_btn1 = QPushButton("访问GitHub源码")
        self.jump_btn1.setFixedSize(QSize(btn_width, btn_height))
        self.jump_btn1.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #24292e;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #000000;
                transform: scale(1.05);
            }
        """)
        self.jump_btn1.clicked.connect(lambda: webbrowser.open("https://github.com/Jolley-cod/YunqiKeyTool.git"))
        main_layout.addWidget(self.jump_btn1, alignment=Qt.AlignCenter)
        
        main_layout.addSpacing(40)

        # 版本+版权
        version_label = QLabel("版本号：v1.1")
        version_label.setStyleSheet("font-size: 13px; color: #666666;")
        version_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(version_label)
        
        copyright_label = QLabel("© 2026 jolley 版权所有")
        copyright_label.setStyleSheet("font-size: 12px; color: #999999;")
        copyright_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(copyright_label)