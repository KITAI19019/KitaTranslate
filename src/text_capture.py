import keyboard
import pyperclip
import pytesseract
from PIL import ImageGrab, Image
import numpy as np
from typing import Callable
import time
from threading import Thread

class TextCapture:
    def __init__(self, callback: Callable[[str], None]):
        """
        初始化文本捕获类
        :param callback: 捕获到文本后的回调函数
        """
        self.callback = callback
        self.last_clipboard_content = ''
        self.is_monitoring = False
        self.monitor_thread = None  # 线程引用

    def start_capture(self):
        """启动文本捕获"""
        self.is_monitoring = True
        self.last_clipboard_content = pyperclip.paste()
        # 设置快捷键监听
        keyboard.add_hotkey('ctrl+shift+s', self._capture_screen)
        # 启动剪贴板监控
        self.monitor_thread = Thread(target=self._monitor_clipboard)  # 创建独立线程
        self.monitor_thread.start()  # 启动线程

    def stop_capture(self):
        """停止文本捕获"""
        self.is_monitoring = False
        keyboard.remove_hotkey('ctrl+shift+s')
        if self.monitor_thread:
            self.monitor_thread.join()  # 等待线程退出

    def _capture_screen(self):
        """屏幕文字识别"""
        try:
            # 捕获屏幕截图
            screenshot = ImageGrab.grab()
            # 转换为numpy数组进行处理
            img_np = np.array(screenshot)
            # 使用tesseract进行OCR识别
            text = pytesseract.image_to_string(img_np, lang='chi_sim+eng')
            if text.strip():
                self.callback(text.strip())
        except Exception as e:
            print(f"截图识别错误: {str(e)}")

    def _monitor_clipboard(self):
        """监控剪贴板"""
        while self.is_monitoring:
            try:
                current_content = pyperclip.paste()
                if current_content != self.last_clipboard_content:
                    self.last_clipboard_content = current_content
                    if current_content.strip():
                        self.callback(current_content.strip())
            except Exception as e:
                print(f"剪贴板监控错误: {str(e)}")
            time.sleep(0.5)  # 降低CPU使用率