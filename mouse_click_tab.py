# by jolley
import json
import os
import threading
import time
import winsound

from pynput.mouse import Button, Controller
from pynput.mouse import Listener as MouseListener
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QPushButton, QSizePolicy,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)


class MouseClickTab(QWidget):
    def __init__(self):
        super().__init__()
        # 状态变量
        self.is_running = False
        self.is_listening_mouse = False
        self.mouse_pos_listener = None
        self.thread_list = []
        self.mouse_ctrl = Controller()
        # 初始化UI
        self.init_ui()
        # 加载配置
        self.load_config()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5,5,5,5)
        left_layout.setSpacing(8)

        # 坐标输入区域
        input_layout = QHBoxLayout()
        self.pos_input = QLineEdit()
        self.pos_input.setPlaceholderText("无需手动输入，点击选点后按鼠标左键即可")
        self.add_pos_btn = QPushButton("选择坐标点")
        self.del_pos_btn = QPushButton("删除坐标点")
        self.add_pos_btn.clicked.connect(self.start_listen_mouse_pos)
        self.del_pos_btn.clicked.connect(self.delete_mouse_row)
        input_layout.addWidget(self.pos_input)
        input_layout.addWidget(self.add_pos_btn)
        input_layout.addWidget(self.del_pos_btn)
        left_layout.addLayout(input_layout)

        # 鼠标坐标表格
        self.mouse_table = QTableWidget()
        self.mouse_table.setColumnCount(5)
        self.mouse_table.setHorizontalHeaderLabels(["状态", "序号", "X坐标", "Y坐标", "延迟(ms)"])
        self.mouse_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mouse_table.setSelectionMode(QTableWidget.SingleSelection)
        self.mouse_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mouse_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mouse_table.verticalHeader().setDefaultSectionSize(36)
        self.mouse_table.verticalHeader().setVisible(False)
        left_layout.addWidget(self.mouse_table)

        # 右侧配置区域
        right_layout = QVBoxLayout()
        right_layout.setSpacing(18)
        right_layout.setContentsMargins(10,10,10,10)

        # 选点快捷键
        select_hotkey_layout = QHBoxLayout()
        select_hotkey_layout.addWidget(QLabel("选点快捷键："))
        self.select_hotkey_combo = QComboBox()
        for i in range(1, 13):
            self.select_hotkey_combo.addItem(f"F{i}")
        self.select_hotkey_combo.setCurrentText("F9")
        select_hotkey_layout.addWidget(self.select_hotkey_combo)
        right_layout.addLayout(select_hotkey_layout)

        # 启停快捷键
        mouse_hotkey_layout = QHBoxLayout()
        mouse_hotkey_layout.addWidget(QLabel("启停快捷键："))
        self.mouse_hotkey_combo = QComboBox()
        for i in range(1, 13):
            self.mouse_hotkey_combo.addItem(f"F{i}")
        self.mouse_hotkey_combo.setCurrentText("F11")
        mouse_hotkey_layout.addWidget(self.mouse_hotkey_combo)
        right_layout.addLayout(mouse_hotkey_layout)

        # 连点模式
        mouse_mode_layout = QHBoxLayout()
        mouse_mode_layout.addWidget(QLabel("连点模式："))
        self.mouse_mode_combo = QComboBox()
        self.mouse_mode_combo.addItems(["开关模式", "单次模式"])
        mouse_mode_layout.addWidget(self.mouse_mode_combo)
        right_layout.addLayout(mouse_mode_layout)

        # 提示音
        mouse_sound_layout = QHBoxLayout()
        self.mouse_sound_check = QCheckBox("开启提示音")
        self.mouse_sound_check.setChecked(True)
        mouse_sound_layout.addWidget(self.mouse_sound_check)
        right_layout.addLayout(mouse_sound_layout)

        # 启动/停止按钮
        mouse_btn_layout = QHBoxLayout()
        self.mouse_start_btn = QPushButton("启动连点")
        self.mouse_stop_btn = QPushButton("停止连点")
        self.mouse_stop_btn.setEnabled(False)
        self.mouse_start_btn.clicked.connect(self.start_mouse_click)
        self.mouse_stop_btn.clicked.connect(self.stop_mouse_click)
        mouse_btn_layout.addWidget(self.mouse_start_btn)
        mouse_btn_layout.addWidget(self.mouse_stop_btn)
        right_layout.addLayout(mouse_btn_layout)

        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)

    # ========== 鼠标坐标监听 ==========
    def start_listen_mouse_pos(self):
        if not self.is_listening_mouse:
            self.is_listening_mouse = True
            self.add_pos_btn.setEnabled(False)
            self.add_pos_btn.setText("请点击鼠标左键选点...")
            self.mouse_pos_listener = MouseListener(on_click=self.on_mouse_click)
            self.mouse_pos_listener.start()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed and button == Button.left:
            try:
                self.add_mouse_row((x, y))
                self.stop_listen_mouse_pos()
            except:
                self.stop_listen_mouse_pos()

    def stop_listen_mouse_pos(self):
        if self.is_listening_mouse and self.mouse_pos_listener:
            self.is_listening_mouse = False
            self.add_pos_btn.setEnabled(True)
            self.add_pos_btn.setText("选择坐标点")
            self.mouse_pos_listener.stop()

    # ========== 鼠标表格操作 ==========
    def add_mouse_row(self, pos):
        row = self.mouse_table.rowCount()
        self.mouse_table.insertRow(row)
        # 状态复选框
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_box.setStyleSheet("margin-left:auto;margin-right:auto;")
        self.mouse_table.setCellWidget(row, 0, check_box)
        # 序号
        self.mouse_table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
        # X/Y坐标
        self.mouse_table.setItem(row, 2, QTableWidgetItem(str(pos[0])))
        self.mouse_table.setItem(row, 3, QTableWidgetItem(str(pos[1])))
        # 延迟
        self.mouse_table.setItem(row, 4, QTableWidgetItem("10"))

    def delete_mouse_row(self):
        selected_row = self.mouse_table.currentRow()
        if selected_row != -1:
            self.mouse_table.removeRow(selected_row)
            # 重新更新序号
            for row in range(self.mouse_table.rowCount()):
                self.mouse_table.setItem(row, 1, QTableWidgetItem(str(row + 1)))

    # ========== 鼠标连点核心逻辑 ==========
    def start_mouse_click(self):
        if not self.is_running:
            self.is_running = True
            self.mouse_start_btn.setEnabled(False)
            self.mouse_stop_btn.setEnabled(True)
            if self.mouse_sound_check.isChecked():
                self.play_start_sound()
            # 获取选中的坐标
            selected_pos = self.get_selected_mouse_pos()
            if selected_pos:
                t = threading.Thread(target=self.auto_mouse_click_sequence, args=(selected_pos,), daemon=True)
                t.start()
                self.thread_list.append(t)

    def stop_mouse_click(self):
        if self.is_running:
            self.is_running = False
            self.mouse_start_btn.setEnabled(True)
            self.mouse_stop_btn.setEnabled(False)
            if self.mouse_sound_check.isChecked():
                self.play_stop_sound()
            # 停止所有线程
            for t in self.thread_list:
                if t.is_alive() and t != threading.current_thread():
                    t.join(0.1)
            self.thread_list.clear()

    def auto_mouse_click_sequence(self, selected_pos):
        current_mode = self.mouse_mode_combo.currentText()
        if current_mode == "单次模式":
            # 单次模式：执行一次
            for x, y, delay_s in selected_pos:
                if not self.is_running:
                    break
                self.simulate_mouse_click(x, y, delay_s)
            self.stop_mouse_click()
        else:
            # 开关模式：循环执行
            while self.is_running:
                for x, y, delay_s in selected_pos:
                    if not self.is_running:
                        break
                    self.simulate_mouse_click(x, y, delay_s)

    # ========== 辅助方法 ==========
    def simulate_mouse_click(self, x, y, delay=0.01):
        """模拟鼠标点击指定坐标"""
        self.mouse_ctrl.position = (int(x), int(y))
        self.mouse_ctrl.press(Button.left)
        self.mouse_ctrl.release(Button.left)
        time.sleep(delay)

    def get_selected_mouse_pos(self):
        """获取选中的鼠标坐标列表"""
        selected_pos = []
        row_count = self.mouse_table.rowCount()
        for row in range(row_count):
            check_box = self.mouse_table.cellWidget(row, 0)
            if check_box.isChecked():
                x = self.mouse_table.item(row, 2).text()
                y = self.mouse_table.item(row, 3).text()
                delay_text = self.mouse_table.item(row, 4).text()
                delay_s = int(delay_text) / 1000
                selected_pos.append((int(x), int(y), delay_s))
        return selected_pos

    def play_start_sound(self):
        """播放启动提示音"""
        winsound.Beep(1500, 200)

    def play_stop_sound(self):
        """播放停止提示音"""
        winsound.Beep(800, 200)

    # ========== 配置保存/加载 ==========
    def save_config(self):
        """保存鼠标连点配置到config.json"""
        table_data = []
        row_count = self.mouse_table.rowCount()
        for row in range(row_count):
            check_box = self.mouse_table.cellWidget(row, 0)
            table_data.append({
                "checked": check_box.isChecked(),
                "index": self.mouse_table.item(row, 1).text(),
                "x": self.mouse_table.item(row, 2).text(),
                "y": self.mouse_table.item(row, 3).text(),
                "delay": self.mouse_table.item(row, 4).text()
            })
        config_data = {
            "mouse_click": {
                "table_data": table_data,
                "select_hotkey": self.select_hotkey_combo.currentText(),
                "mouse_hotkey": self.mouse_hotkey_combo.currentText(),
                "mode": self.mouse_mode_combo.currentText(),
                "sound": self.mouse_sound_check.isChecked()
            }
        }
        # 合并配置（避免覆盖其他Tab的配置）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                all_config = json.load(f)
            all_config.update(config_data)
        else:
            all_config = config_data
        # 保存
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(all_config, f, ensure_ascii=False, indent=4)

    def load_config(self):
        """从config.json加载鼠标连点配置"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        if not os.path.exists(config_path):
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                all_config = json.load(f)
            mouse_config = all_config.get("mouse_click", {})
            if not mouse_config:
                return

            # 恢复表格
            self.mouse_table.setRowCount(0)
            for item in mouse_config.get("table_data", []):
                row = self.mouse_table.rowCount()
                self.mouse_table.insertRow(row)
                check_box = QCheckBox()
                check_box.setChecked(item["checked"])
                check_box.setStyleSheet("margin-left:auto;margin-right:auto;")
                self.mouse_table.setCellWidget(row, 0, check_box)
                self.mouse_table.setItem(row, 1, QTableWidgetItem(item["index"]))
                self.mouse_table.setItem(row, 2, QTableWidgetItem(item["x"]))
                self.mouse_table.setItem(row, 3, QTableWidgetItem(item["y"]))
                self.mouse_table.setItem(row, 4, QTableWidgetItem(item["delay"]))

            # 恢复其他配置
            self.select_hotkey_combo.setCurrentText(mouse_config.get("select_hotkey", "F9"))
            self.mouse_hotkey_combo.setCurrentText(mouse_config.get("mouse_hotkey", "F11"))
            self.mouse_mode_combo.setCurrentText(mouse_config.get("mode", "开关模式"))
            self.mouse_sound_check.setChecked(mouse_config.get("sound", True))
        except Exception as e:
            print(f"加载鼠标配置失败：{e}")