# by jolley
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QMainWindow, QPushButton,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QTabWidget, QVBoxLayout, QWidget)


class KeyToolView(QMainWindow):
    # 定义业务信号
    signal_add_key = pyqtSignal(str)
    signal_start_listen_key = pyqtSignal()
    signal_stop_listen_key = pyqtSignal()
    signal_delete_key = pyqtSignal()
    signal_start_auto_press = pyqtSignal()
    signal_stop_auto_press = pyqtSignal()
    signal_tab_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle("云栖 按键工具")
        self.resize(836, 448)
        # 全局样式表
        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox {font-size: 14px; padding: 4px;}
            QTableWidget {font-size: 13px; border: 1px solid #ccc;}
            QTableWidget::item {padding: 8px;}
            QHeaderView::section {font-size: 14px; padding: 8px; background-color: #4CAF50; color: white; font-weight: bold; border: 1px solid #ffffff; border-radius: 3px;}
        """)

        # 主选项卡
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # 按键连发Tab页
        self.auto_tab = QWidget()
        self.tab_widget.addTab(self.auto_tab, "按键连发")
        self.build_auto_tab_ui()

        # 鼠标连点Tab页
        self.macro_tab = QWidget()
        self.tab_widget.addTab(self.macro_tab, "鼠标连点")
        self.build_macro_tab_ui()

    # 构建按键连发UI
    def build_auto_tab_ui(self):
        main_layout = QHBoxLayout(self.auto_tab)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5,5,5,5)
        left_layout.setSpacing(8)

        input_layout = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("无需手动输入，点击添加按键后按任意键即可")
        self.add_btn = QPushButton("添加按键")
        self.del_btn = QPushButton("删除按键")
        self.add_btn.clicked.connect(self.signal_start_listen_key.emit)
        self.del_btn.clicked.connect(self.signal_delete_key.emit)
        input_layout.addWidget(self.key_input)
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.del_btn)
        left_layout.addLayout(input_layout)

        self.key_table = QTableWidget()
        self.key_table.setColumnCount(4)
        self.key_table.setHorizontalHeaderLabels(["状态", "按键", "模式", "延迟"])
        self.key_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.key_table.setSelectionMode(QTableWidget.SingleSelection)
        self.key_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.key_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.key_table.verticalHeader().setDefaultSectionSize(36)
        self.key_table.verticalHeader().setVisible(False)
        left_layout.addWidget(self.key_table)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        right_layout.setContentsMargins(10,10,10,10)

        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(QLabel("启停快捷键："))
        self.hotkey_combo = QComboBox()
        for i in range(1, 13): self.hotkey_combo.addItem(f"F{i}")
        self.hotkey_combo.setCurrentText("F10")
        hotkey_layout.addWidget(self.hotkey_combo)
        right_layout.addLayout(hotkey_layout)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("按键间隔(毫秒)："))
        self.interval_input = QLineEdit("10")
        interval_layout.addWidget(self.interval_input)
        right_layout.addLayout(interval_layout)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("按键模式："))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["开关模式", "单次模式"])
        mode_layout.addWidget(self.mode_combo)
        right_layout.addLayout(mode_layout)

        checkbox_layout = QHBoxLayout()
        self.sound_check = QCheckBox("开启提示音")
        self.sound_check.setChecked(True)
        checkbox_layout.addWidget(self.sound_check)
        right_layout.addLayout(checkbox_layout)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("启动")
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.signal_start_auto_press.emit)
        self.stop_btn.clicked.connect(self.signal_stop_auto_press.emit)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        right_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)

    # 构建鼠标连点UI
    def build_macro_tab_ui(self):
        layout = QVBoxLayout(self.macro_tab)
        layout.addWidget(QLabel("鼠标连点功能开发中..."), alignment=Qt.AlignCenter)

    # Tab切换触发信号
    def on_tab_changed(self, index):
        self.signal_tab_changed.emit(index)

    # UI操作对外提供方法
    @pyqtSlot(str)
    def add_key_row(self, key_text):
        row = self.key_table.rowCount()
        self.key_table.insertRow(row)
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_box.setStyleSheet("margin-left:auto;margin-right:auto;")
        # ========== 修复这里：cellWidget → setCellWidget ==========
        self.key_table.setCellWidget(row, 0, check_box)
        self.key_table.setItem(row, 1, QTableWidgetItem(key_text))
        self.key_table.setItem(row, 2, QTableWidgetItem("开关"))
        self.key_table.setItem(row, 3, QTableWidgetItem("10"))

    def delete_key_row(self):
        selected_row = self.key_table.currentRow()
        if selected_row != -1: self.key_table.removeRow(selected_row)

    def set_listen_state(self, is_listening):
        self.add_btn.setEnabled(not is_listening)
        self.add_btn.setText("请按任意键..." if is_listening else "添加按键")
        self.setWindowTitle("云栖 按键工具 - 监听按键中..." if is_listening else "云栖 按键工具")

    def set_running_state(self, is_running):
        self.start_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)
        self.setWindowTitle("云栖 按键工具 - 运行中 ✅" if is_running else "云栖 按键工具 - 已停止 ❌")

    def get_selected_keys(self):
        selected_keys = []
        row_count = self.key_table.rowCount()
        for row in range(row_count):
            check_box = self.key_table.cellWidget(row, 0)
            if check_box.isChecked():
                key_text = self.key_table.item(row, 1).text()
                delay_text = self.key_table.item(row, 3).text()
                delay_s = int(delay_text) / 1000
                selected_keys.append((key_text, delay_s))
        return selected_keys