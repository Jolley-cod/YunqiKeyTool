# by jolley
import threading
import time

from pynput import keyboard
from pynput.keyboard import Key, Listener
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QCheckBox


class KeyToolController(QObject):
    # 单次模式完成信号
    signal_single_mode_finish = pyqtSignal()

    def __init__(self, view, model):
        super().__init__()
        self.view = view
        self.model = model
        self.key_listener = None
        self.hotkey_listener = None
        self.auto_tab_config = {}
        self.bind_signals()
        self.init_default_keys()
        self.save_auto_tab_config()
        self.start_hotkey_listen()

    # 绑定所有信号
    def bind_signals(self):
        self.view.signal_add_key.connect(self.view.add_key_row)
        self.view.signal_start_listen_key.connect(self.start_listen_key)
        self.view.signal_stop_listen_key.connect(self.stop_listen_key)
        self.view.signal_delete_key.connect(self.view.delete_key_row)
        self.view.signal_start_auto_press.connect(self.start_auto_press)
        self.view.signal_stop_auto_press.connect(self.stop_auto_press)
        self.view.signal_tab_changed.connect(self.on_tab_changed)
        self.signal_single_mode_finish.connect(self.stop_auto_press)

    # 初始化默认按键行
    def init_default_keys(self):
        self.view.add_key_row("G")
        self.view.add_key_row("D")
        self.view.add_key_row("A")
        d_checkbox = self.view.key_table.cellWidget(1, 0)
        d_checkbox.setChecked(False)

    # 保存按键连发配置
    def save_auto_tab_config(self):
        table_data = []
        row_count = self.view.key_table.rowCount()
        for row in range(row_count):
            check_box = self.view.key_table.cellWidget(row, 0)
            table_data.append({
                "checked": check_box.isChecked(),
                "key": self.view.key_table.item(row, 1).text(),
                "mode": self.view.key_table.item(row, 2).text(),
                "delay": self.view.key_table.item(row, 3).text()
            })
        self.auto_tab_config = {
            "table_data": table_data,
            "interval": self.view.interval_input.text(),
            "hotkey": self.view.hotkey_combo.currentText(),
            "current_mode": self.view.mode_combo.currentText(),
            "sound_checked": self.view.sound_check.isChecked()
        }

    # 恢复按键连发配置
    def restore_auto_tab_config(self):
        if not self.auto_tab_config: return
        self.view.key_table.setRowCount(0)
        for item in self.auto_tab_config["table_data"]:
            row = self.view.key_table.rowCount()
            self.view.key_table.insertRow(row)
            check_box = QCheckBox()
            check_box.setChecked(item["checked"])
            check_box.setStyleSheet("margin-left:auto;margin-right:auto;")
            # ========== 修复这里：cellWidget → setCellWidget ==========
            self.view.key_table.setCellWidget(row, 0, check_box)
            self.view.key_table.setItem(row, 1, QTableWidgetItem(item["key"]))
            self.view.key_table.setItem(row, 2, QTableWidgetItem(item["mode"]))
            self.view.key_table.setItem(row, 3, QTableWidgetItem(item["delay"]))
        self.view.interval_input.setText(self.auto_tab_config["interval"])
        self.view.hotkey_combo.setCurrentText(self.auto_tab_config["hotkey"])
        self.view.mode_combo.setCurrentText(self.auto_tab_config["current_mode"])
        self.view.sound_check.setChecked(self.auto_tab_config["sound_checked"])

    # Tab切换核心逻辑：配置保存+状态重置
    def on_tab_changed(self, index):
        if index == 1:
            self.save_auto_tab_config()
            self.stop_auto_press()
            self.model.is_running = False
            self.view.set_running_state(False)
        else:
            self.restore_auto_tab_config()
            self.model.is_running = False
            self.view.set_running_state(False)

    # 监听添加按键
    def start_listen_key(self):
        if not self.model.is_listening:
            self.model.is_listening = True
            self.view.set_listen_state(True)
            self.key_listener = Listener(on_press=self.on_key_press)
            self.key_listener.start()

    def on_key_press(self, key):
        try:
            key_name = self.model.format_key_name(key)
            self.view.signal_add_key.emit(key_name)
            self.stop_listen_key()
        except: self.stop_listen_key()

    def stop_listen_key(self):
        if self.model.is_listening and self.key_listener:
            self.model.is_listening = False
            self.view.set_listen_state(False)
            self.key_listener.stop()

    # 启动按键连发
    def start_auto_press(self):
        if not self.model.is_running:
            self.model.is_running = True
            self.view.set_running_state(True)
            if self.view.sound_check.isChecked(): self.model.play_start_sound()
            selected_keys = self.view.get_selected_keys()
            if selected_keys:
                t = threading.Thread(target=self.auto_press_sequence, args=(selected_keys,), daemon=True)
                t.start()
                self.model.thread_list.append(t)

    # 停止按键连发 - 线程安全加固
    def stop_auto_press(self):
        if self.model.is_running:
            self.model.is_running = False
            self.view.set_running_state(False)
            if self.view.sound_check.isChecked(): self.model.play_stop_sound()
            for t in self.model.thread_list:
                if t.is_alive() and t != threading.current_thread():
                    t.join(0.1)
            self.model.thread_list.clear()

    # 按键执行核心逻辑 - GAGA交替点击
    def auto_press_sequence(self, selected_keys):
        current_mode = self.view.mode_combo.currentText()
        if current_mode == "单次模式":
            for key_text, delay_s in selected_keys:
                if not self.model.is_running: break
                self.model.simulate_key_press(key_text)
                time.sleep(delay_s)
            self.signal_single_mode_finish.emit()
        else:
            while self.model.is_running:
                for key_text, delay_s in selected_keys:
                    if not self.model.is_running: break
                    self.model.simulate_key_press(key_text)
                    time.sleep(delay_s)

    # 全局快捷键监听
    def start_hotkey_listen(self):
        self.hotkey_listener = Listener(on_press=self.on_hotkey_press)
        self.hotkey_listener.start()

    def on_hotkey_press(self, key):
        try:
            selected_hotkey = self.view.hotkey_combo.currentText()
            pressed_key_name = self.model.format_key_name(key)
            if pressed_key_name == selected_hotkey:
                self.stop_auto_press() if self.model.is_running else self.start_auto_press()
        except: pass