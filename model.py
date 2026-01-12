# by jolley
import winsound

from pynput.keyboard import Controller, Key, KeyCode


class KeyToolModel:
    def __init__(self):
        # 运行状态数据
        self.is_running = False
        self.is_listening = False
        self.keyboard_ctrl = Controller()
        self.thread_list = []
        # 按键名称格式化映射表
        self.key_name_map = {
            Key.space: "空格", Key.enter: "回车", Key.backspace: "退格",
            Key.tab: "Tab", Key.esc: "ESC", Key.shift: "Shift",
            Key.ctrl: "Ctrl", Key.alt: "Alt", Key.caps_lock: "大写锁",
            Key.up: "↑", Key.down: "↓", Key.left: "←", Key.right: "→",
            Key.f1: "F1", Key.f2: "F2", Key.f3: "F3", Key.f4: "F4", Key.f5: "F5",
            Key.f6: "F6", Key.f7: "F7", Key.f8: "F8", Key.f9: "F9", Key.f10: "F10",
            Key.f11: "F11", Key.f12: "F12", Key.delete: "删除", Key.insert: "插入"
        }

    # 格式化按键名称
    def format_key_name(self, key):
        if isinstance(key, KeyCode) and key.char:
            return key.char.upper()
        elif isinstance(key, Key):
            return self.key_name_map.get(key, str(key).replace("Key.", "").capitalize())
        return str(key).upper()

    # 模拟按键按下+松开
    def simulate_key_press(self, key_text):
        key_map = {
            "空格": Key.space, "回车": Key.enter, "退格": Key.backspace, "ESC": Key.esc,
            "Shift": Key.shift, "Ctrl": Key.ctrl, "Alt": Key.alt, "↑": Key.up, "↓": Key.down,
            "←": Key.left, "→": Key.right, "F1": Key.f1, "F2": Key.f2, "F3": Key.f3, "F4": Key.f4,
            "F5": Key.f5, "F6": Key.f6, "F7": Key.f7, "F8": Key.f8, "F9": Key.f9, "F10": Key.f10,
            "F11": Key.f11, "F12": Key.f12
        }
        if key_text in key_map:
            self.keyboard_ctrl.press(key_map[key_text])
            self.keyboard_ctrl.release(key_map[key_text])
        else:
            self.keyboard_ctrl.press(key_text)
            self.keyboard_ctrl.release(key_text)

    # 提示音播放
    def play_start_sound(self):
        winsound.Beep(1500, 200)

    def play_stop_sound(self):
        winsound.Beep(800, 200)