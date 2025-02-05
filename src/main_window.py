from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QTextEdit,
                             QVBoxLayout, QComboBox, QSystemTrayIcon,
                             QHBoxLayout, QLabel, QStatusBar)
from PyQt5.QtCore import Qt


class TranslatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        # 语言选择
        self.languages = ["中文","English","日本語"]
        self.s_lang_combo = QComboBox()
        self.t_lang_combo = QComboBox()
        self.s_lang_combo.addItems(["自动检测语言"] + self.languages)
        self.t_lang_combo.addItems(self.languages)

        # 文本区域
        self.source = QTextEdit()
        self.target = QTextEdit()
        self.target.setReadOnly(True)

        # 布局系统
        main_layout = QVBoxLayout()

        # 水平布局：语言选择
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("原文语言："))  # 添加标签更清晰
        lang_layout.addWidget(self.s_lang_combo)
        lang_layout.addWidget(QLabel("      ---→"))  # 添加箭头符号
        lang_layout.addWidget(QLabel("目标语言："))
        lang_layout.addWidget(self.t_lang_combo)

        # 水平布局：文本区域
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.source, stretch=3)  # 比例控制
        text_layout.addWidget(self.target, stretch=3)

        # 垂直整合布局
        main_layout.addLayout(lang_layout)  # 正确使用addLayout
        main_layout.addLayout(text_layout)

        # 添加底部状态栏（可选）
        status_bar = QStatusBar()
        status_bar.showMessage("就绪")
        main_layout.addWidget(status_bar)

        self.setLayout(main_layout)

        # 窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setMinimumSize(400, 300)

    def init_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon("icon.png"))
        self.tray.show()


if __name__ == "__main__":
    app = QApplication([])
    window = TranslatorUI()
    window.show()
    app.exec_()