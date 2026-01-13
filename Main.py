# by jolley
import sys
import threading

from pynput.keyboard import Key, KeyCode, Listener
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QTabWidget, QVBoxLayout, QWidget)

from about_tab import AboutTab
# 导入各个Tab模块
from auto_key_tab import AutoKeyTab
from mouse_click_tab import MouseClickTab
from profit_calc_tab import ProfitCalcTab  # 新增：导入利润计算Tab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.start_global_hotkey_listener()

    def init_ui(self):
        # 窗口基础设置
        self.setWindowTitle("云栖工具箱")
        self.resize(900, 700)
        self.setStyleSheet("""
            QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox {font-size: 14px; padding: 4px;}
            QTableWidget {font-size: 13px; border: 1px solid #ccc;}
            QTableWidget::item {padding: 8px;}
            QHeaderView::section {font-size: 14px; padding: 8px; color: #333333; font-weight: bold; border: 1px solid #e0e0e0; border-radius: 3px;}
        """)

        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 主选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 初始化各个Tab并添加到主选项卡
        self.auto_key_tab = AutoKeyTab()
        self.mouse_click_tab = MouseClickTab()
        self.profit_calc_tab = ProfitCalcTab()  # 新增：初始化利润计算Tab
        self.about_tab = AboutTab()

        self.tab_widget.addTab(self.auto_key_tab, "按键连发")
        self.tab_widget.addTab(self.mouse_click_tab, "鼠标连点")
        self.tab_widget.addTab(self.profit_calc_tab, "配方利润计算")  # 新增：添加利润计算Tab
        self.tab_widget.addTab(self.about_tab, "关于我")

        # 版权标签
        copyright_label = QLabel("jolley by 双梦-叶弈弈")
        copyright_label.setStyleSheet("font-size: 12px; color: #666;")
        copyright_layout = QHBoxLayout()
        copyright_layout.addStretch()
        copyright_layout.addWidget(copyright_label)
        copyright_layout.setContentsMargins(10, 0, 10, 5)
        main_layout.addLayout(copyright_layout)

        # Tab切换时停止当前Tab的运行状态
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        """切换Tab时停止当前运行的功能"""
        if self.auto_key_tab.is_running:
            self.auto_key_tab.stop_auto_press()
        if self.mouse_click_tab.is_running:
            self.mouse_click_tab.stop_mouse_click()

    def start_global_hotkey_listener(self):
        """全局快捷键监听（对应当前激活的Tab）"""
        def on_hotkey_press(key):
            try:
                # 格式化按键名称
                if isinstance(key, KeyCode) and key.char:
                    pressed_key = key.char.upper()
                elif isinstance(key, Key):
                    pressed_key = str(key).replace("Key.", "").capitalize()
                    # 特殊键映射（和各个Tab内保持一致）
                    key_map = {
                        "Space": "空格", "Enter": "回车", "Backspace": "退格",
                        "Esc": "ESC", "Shift": "Shift", "Ctrl": "Ctrl", "Alt": "Alt",
                        "Up": "↑", "Down": "↓", "Left": "←", "Right": "→",
                        "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5",
                        "F6": "F6", "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10",
                        "F11": "F11", "F12": "F12"
                    }
                    pressed_key = key_map.get(pressed_key, pressed_key)

                current_tab_index = self.tab_widget.currentIndex()
                # 按键连发Tab快捷键
                if current_tab_index == 0:
                    selected_hotkey = self.auto_key_tab.hotkey_combo.currentText()
                    if pressed_key == selected_hotkey:
                        if self.auto_key_tab.is_running:
                            self.auto_key_tab.stop_auto_press()
                        else:
                            self.auto_key_tab.start_auto_press()
                # 鼠标连点Tab快捷键
                elif current_tab_index == 1:
                    # 选点快捷键
                    select_hotkey = self.mouse_click_tab.select_hotkey_combo.currentText()
                    if pressed_key == select_hotkey and not self.mouse_click_tab.is_listening_mouse:
                        self.mouse_click_tab.start_listen_mouse_pos()
                    # 启停快捷键
                    mouse_hotkey = self.mouse_click_tab.mouse_hotkey_combo.currentText()
                    if pressed_key == mouse_hotkey:
                        if self.mouse_click_tab.is_running:
                            self.mouse_click_tab.stop_mouse_click()
                        else:
                            self.mouse_click_tab.start_mouse_click()
                # 利润计算Tab无快捷键，无需处理
            except Exception as e:
                pass

        # 启动全局快捷键监听线程
        self.hotkey_listener = Listener(on_press=on_hotkey_press)
        self.hotkey_listener.start()

    def closeEvent(self, event):
        """程序关闭时停止所有监听和线程"""
        # 停止按键连发
        if self.auto_key_tab.is_running:
            self.auto_key_tab.stop_auto_press()
        if self.auto_key_tab.is_listening:
            self.auto_key_tab.stop_listen_key()
        # 停止鼠标连点
        if self.mouse_click_tab.is_running:
            self.mouse_click_tab.stop_mouse_click()
        if self.mouse_click_tab.is_listening_mouse:
            self.mouse_click_tab.stop_listen_mouse_pos()
        # 停止全局快捷键监听
        self.hotkey_listener.stop()
        # 保存配置
        self.auto_key_tab.save_config()
        self.mouse_click_tab.save_config()
        self.profit_calc_tab.save_config()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())