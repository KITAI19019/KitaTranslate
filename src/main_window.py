from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QLocale
from PyQt5.QtWidgets import (QApplication, QWidget, QTextEdit,
                             QVBoxLayout, QComboBox, QSystemTrayIcon,
                             QHBoxLayout, QLabel, QStatusBar)

from text_capture import TextCapture
from translate import Translator
import time

class TranslationSignals(QObject):
    text_captured = pyqtSignal(str)  # 文本捕获信号
    translation_start = pyqtSignal()  # 翻译开始信号
    translation_done = pyqtSignal(str)  # 翻译完成信号

class TranslationWorker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(str)

    def __init__(self, text, translator):
        super().__init__()
        self.text = text
        self.translator = translator
        self.is_interrupted = False  # 新增标志位

    def run(self):
        try:
            for _ in range(10):  # 模拟翻译过程
                if self.is_interrupted:
                    return  # 直接终止
                time.sleep(0.1)  # 模拟处理延迟

            if not self.is_interrupted:
                trans_text = self.translator.translate(self.text)
                self.result.emit(trans_text)
        except Exception as e:
            self.result.emit(f"翻译错误：{str(e)}")
        finally:
            self.finished.emit()

class TranslatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = TranslationSignals()
        self.translator = Translator(from_lang='en', to_lang='zh')
        self.capture = TextCapture(self.handle_captured_text)  # 文本捕获实例
        self.init_ui()
        self.init_tray()
        self.connect_signals()
        self.capture.start_capture()  # 启动捕获
        self.trans_queue = []
        self.trans_thread = None


    def closeEvent(self, event):
        self.capture.stop_capture()
        if hasattr(self, 'trans_thread') and self.trans_thread.isRunning():
            self.trans_thread.quit()
            self.trans_thread.wait()
        event.accept()

    def init_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("icon.png"))
        self.tray.show()

    def show_translating_status(self):
        """显示翻译状态"""
        self.status_bar.showMessage("翻译中...")

    def connect_signals(self):
        self.signals.text_captured.connect(self.update_source)
        self.signals.translation_start.connect(self.show_translating_status)
        self.signals.translation_done.connect(self.update_target)

    def handle_captured_text(self, text: str):
        # 去重处理，防止相同文本重复翻译
        if self.trans_queue and self.trans_queue[-1] == text:
            return
        self.trans_queue.append(text)
        self.signals.text_captured.emit(text)  # 触发更新输入框
        self.process_queue()  # 确保翻译任务启动

    def process_queue(self):
        """处理任务队列"""
        print(f"当前队列: {self.trans_queue}")  # 调试输出
        if self.trans_thread is None or not self.trans_thread.isRunning():
            if self.trans_queue:
                text = self.trans_queue.pop(0)
                print(f"开始翻译: {text}")  # 调试输出
                self.start_translation(text)
            else:
                print("队列为空，等待新任务")
        else:
            print("当前仍有翻译任务进行中，等待结束")  # 调试信息


    def on_thread_finished(self):
        """翻译线程结束时调用：清理线程引用并继续处理队列"""
        print("翻译线程结束，尝试处理下一个队列任务")  # 添加调试信息
        thread = self.trans_thread
        self.trans_thread = None  # 先重置引用

        if thread:
            thread.deleteLater()  # 确保线程被销毁

        self.process_queue()  # 确保队列继续

    def update_source(self, text: str):
        """更新原文输入框"""
        self.source.setText(text)

    def update_target(self, result: str):
        """更新译文显示"""
        print(f"翻译完成: {result}")  # 调试信息
        self.target.setText(result)
        self.status_bar.showMessage("翻译完成")

    def start_translation(self, text: str):
        """启动/中断翻译线程"""
        print(f"尝试启动翻译: {text}")  # 调试信息

        # 终止之前的线程，确保清理
        if self.trans_thread is not None:
            if self.trans_thread.isRunning():
                print("中断之前的翻译任务")  # 调试信息
                self.trans_worker.is_interrupted = True
                self.trans_thread.quit()
                self.trans_thread.wait()

            print("彻底清理旧线程")  # 调试信息
            self.trans_thread.deleteLater()
            self.trans_thread = None

        self.signals.translation_start.emit()  # 更新状态栏

        self.trans_thread = QThread()
        self.trans_worker = TranslationWorker(text, self.translator)
        self.trans_worker.moveToThread(self.trans_thread)

        # 连接信号
        self.trans_worker.result.connect(self.signals.translation_done)
        self.trans_worker.finished.connect(self.trans_thread.quit)
        self.trans_worker.finished.connect(self.on_thread_finished)  # 线程结束后继续队列
        self.trans_thread.started.connect(self.trans_worker.run)
        self.trans_thread.finished.connect(self.trans_thread.deleteLater)

        print("翻译线程已启动")  # 调试信息
        self.trans_thread.start()



    def init_ui(self):
        # 语言选择
        self.languages = ["中文","English","日本語"]
        self.s_lang_combo = QComboBox()
        self.t_lang_combo = QComboBox()
        self.s_lang_combo.addItems(self.languages)
        self.t_lang_combo.addItems(self.languages)

        self.s_lang_combo.currentIndexChanged.connect(self.chosed_language)
        self.t_lang_combo.currentIndexChanged.connect(self.chosed_language)
        # 文本区域
        self.source = QTextEdit()
        self.target = QTextEdit()
        self.target.setReadOnly(True)
        #状态栏
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("就绪")



        # 布局系统
        main_layout = QVBoxLayout()
        # 水平布局：语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("原文语言："))  # 添加标签更清晰
        lang_layout.addWidget(self.s_lang_combo)
        lang_layout.addWidget(QLabel("      ---→"))
        lang_layout.addWidget(QLabel("目标语言："))
        lang_layout.addWidget(self.t_lang_combo)
        # 水平布局：文本区域
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.source, stretch=3)  # 比例控制
        text_layout.addWidget(self.target, stretch=3)
        # 垂直整合布局
        main_layout.addLayout(lang_layout)  # 正确使用addLayout
        main_layout.addLayout(text_layout)
        # 添加底部状态栏
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        # 窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumSize(400, 300)

    def chosed_language(self):
        langs = {"中文": "zh", "English": "en", "日本語": "ja"}
        s_lang = self.s_lang_combo.currentText()
        t_lang = self.t_lang_combo.currentText()
        self.translator = Translator(from_lang=langs[s_lang], to_lang=langs[t_lang])
        print(f"输入语言：{s_lang}\n输出语言：{t_lang}")


if __name__ == "__main__":
    app = QApplication([])
    window = TranslatorUI()
    window.show()
    app.exec_()