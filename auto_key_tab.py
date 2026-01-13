import json
import os
import threading
import time
import winsound

from pynput.keyboard import Controller, Key, KeyCode, Listener
from PyQt5.QtCore import Q_ARG, QMetaObject, QSize, Qt, pyqtSlot
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QHeaderView,
                             QLabel, QLineEdit, QPushButton, QSizePolicy,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)


class AutoKeyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.is_listening = False
        self.key_listener = None
        self.thread_list = []
        self.keyboard_ctrl = Controller()
        self.init_ui()
        self.load_config()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(5,5,5,5)
        left_layout.setSpacing(8)

        input_layout = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("无需手动输入，点击添加按键后按任意键即可")
        self.add_btn = QPushButton("添加按键")
        self.del_btn = QPushButton("删除按键")
        self.add_btn.clicked.connect(self.start_listen_key)
        self.del_btn.clicked.connect(self.delete_key_row)
        input_layout.addWidget(self.key_input)
        input_layout.addWidget(self.add_btn)
        input_layout.addWidget(self.del_btn)
        left_layout.addLayout(input_layout)

        self.key_table = QTableWidget()
        self.key_table.setColumnCount(3)
        self.key_table.setHorizontalHeaderLabels(["状态", "按键", "延迟"])
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
        for i in range(1, 13):
            self.hotkey_combo.addItem(f"F{i}")
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
        self.start_btn.clicked.connect(self.start_auto_press)
        self.stop_btn.clicked.connect(self.stop_auto_press)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        right_layout.addLayout(btn_layout)

        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)

    def start_listen_key(self):
        if not self.is_listening:
            self.is_listening = True
            self.add_btn.setEnabled(False)
            self.add_btn.setText("请按任意键...")
            self.key_listener = Listener(on_press=self.on_key_press)
            self.key_listener.start()

    def on_key_press(self, key):
        try:
            key_name = self.format_key_name(key)
            QMetaObject.invokeMethod(self, "add_key_row", Qt.QueuedConnection, Q_ARG(str, key_name))
            self.stop_listen_key()
        except Exception as e:
            self.stop_listen_key()

    def stop_listen_key(self):
        if self.is_listening and self.key_listener:
            self.is_listening = False
            self.add_btn.setEnabled(True)
            self.add_btn.setText("添加按键")
            self.key_listener.stop()

    @pyqtSlot(str)
    def add_key_row(self, key_text):
        row = self.key_table.rowCount()
        self.key_table.insertRow(row)
        
        # 状态列-居中复选框
        check_widget = QWidget()
        check_layout = QHBoxLayout(check_widget)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_box = QCheckBox()
        check_box.setChecked(True)
        check_layout.addWidget(check_box, alignment=Qt.AlignCenter)
        self.key_table.setCellWidget(row, 0, check_widget)
        
        # 按键列-居中+不可编辑
        key_item = QTableWidgetItem(key_text)
        key_item.setTextAlignment(Qt.AlignCenter)
        key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
        self.key_table.setItem(row, 1, key_item)
        
        # 延迟列-居中+可编辑（核心：新增行的延迟列居中配置）
        delay_item = QTableWidgetItem("10")
        delay_item.setTextAlignment(Qt.AlignCenter)
        self.key_table.setItem(row, 2, delay_item)
        
        self.key_table.viewport().update()

    def delete_key_row(self):
        selected_row = self.key_table.currentRow()
        if selected_row != -1:
            self.key_table.removeRow(selected_row)

    def format_key_name(self, key):
        key_name_map = {
            Key.space: "空格", Key.enter: "回车", Key.backspace: "退格",
            Key.tab: "Tab", Key.esc: "ESC", Key.shift: "Shift",
            Key.ctrl: "Ctrl", Key.alt: "Alt", Key.caps_lock: "大写锁",
            Key.up: "↑", Key.down: "↓", Key.left: "←", Key.right: "→",
            Key.page_up: "PageUp", Key.page_down: "PageDown", Key.delete: "删除",
            Key.insert: "Insert", Key.home: "Home", Key.end: "End"
        }
        if isinstance(key, KeyCode) and key.char:
            return key.char.upper()
        elif isinstance(key, Key):
            return key_name_map.get(key, str(key).replace("Key.", "").capitalize())
        return str(key).upper()

    def start_auto_press(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            if self.sound_check.isChecked(): winsound.Beep(1500, 200)
            selected_keys = self.get_selected_keys()
            if selected_keys:
                t = threading.Thread(target=self.auto_press_sequence, args=(selected_keys,), daemon=True)
                t.start()
                self.thread_list.append(t)

    def stop_auto_press(self):
        if self.is_running:
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            if self.sound_check.isChecked(): winsound.Beep(800, 200)
            self.thread_list.clear()

    def auto_press_sequence(self, selected_keys):
        # 修复：获取全局按键间隔，原代码未生效
        try:
            global_interval = int(self.interval_input.text()) / 1000
        except:
            global_interval = 0.01
            
        while self.is_running:
            for key_text, delay_s in selected_keys:
                if not self.is_running: break
                self.simulate_key_press(key_text)
                time.sleep(delay_s)
                # 追加全局按键间隔
                time.sleep(global_interval)
            if self.mode_combo.currentText() == "单次模式":
                QMetaObject.invokeMethod(self, "stop_auto_press", Qt.QueuedConnection)
                break

    def simulate_key_press(self, key_text):
        # 修复：补全所有按键映射，原代码映射不全导致按键失效
        key_map = {
            "空格": Key.space, "回车": Key.enter, "退格": Key.backspace, "ESC": Key.esc,
            "Tab": Key.tab, "Shift": Key.shift, "Ctrl": Key.ctrl, "Alt": Key.alt,
            "大写锁": Key.caps_lock, "↑": Key.up, "↓": Key.down, "←": Key.left, "→": Key.right,
            "PageUp": Key.page_up, "PageDown": Key.page_down, "删除": Key.delete,
            "Insert": Key.insert, "Home": Key.home, "End": Key.end
        }
        target = key_map.get(key_text, key_text.lower())
        self.keyboard_ctrl.press(target)
        self.keyboard_ctrl.release(target)

    def get_selected_keys(self):
        keys = []
        for r in range(self.key_table.rowCount()):
            w = self.key_table.cellWidget(r, 0)
            if w and w.findChild(QCheckBox).isChecked():
                try:
                    key_text = self.key_table.item(r, 1).text()
                    delay_ms = int(self.key_table.item(r, 2).text())
                    keys.append((key_text, delay_ms / 1000))
                except: continue
        return keys

    def save_config(self):
        table_data = []
        for r in range(self.key_table.rowCount()):
            w = self.key_table.cellWidget(r, 0)
            if w:
                table_data.append({
                    "checked": w.findChild(QCheckBox).isChecked(),
                    "key": self.key_table.item(r, 1).text(),
                    "delay": self.key_table.item(r, 2).text()
                })
        config = {
            "auto_key": {
                "table_data": table_data,
                "interval": self.interval_input.text(),
                "hotkey": self.hotkey_combo.currentText(),
                "mode": self.mode_combo.currentText(),
                "sound": self.sound_check.isChecked()
            }
        }
        path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            full_cfg = {}
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f: full_cfg = json.load(f)
            full_cfg.update(config)
            with open(path, 'w', encoding='utf-8') as f: json.dump(full_cfg, f, ensure_ascii=False, indent=4)
        except: pass

    def load_config(self):
        path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(path): return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                cfg = json.load(f).get("auto_key", {})
            self.key_table.setRowCount(0)
            for item in cfg.get("table_data", []):
                self.add_key_row(item["key"])
                row = self.key_table.rowCount() - 1
                # 恢复选中状态
                self.key_table.cellWidget(row, 0).findChild(QCheckBox).setChecked(item["checked"])
                # ==========【核心修复】==========
                # 加载配置的延迟列 手动设置【居中对齐】+ 正常编辑，解决你的核心问题
                delay_item = QTableWidgetItem(item["delay"])
                delay_item.setTextAlignment(Qt.AlignCenter)
                self.key_table.setItem(row, 2, delay_item)
                
            self.interval_input.setText(cfg.get("interval", "10"))
            self.hotkey_combo.setCurrentText(cfg.get("hotkey", "F10"))
            self.mode_combo.setCurrentText(cfg.get("mode", "开关模式"))
            self.sound_check.setChecked(cfg.get("sound", True))
        except: pass