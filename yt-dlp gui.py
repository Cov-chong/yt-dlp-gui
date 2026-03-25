import sys,subprocess,threading,locale
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, QObject

class Worker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    log = pyqtSignal(str)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        self.setWindowTitle("yt-dlp video download")
        self.resize(1000, 600)
        self.setStyleSheet("""
            QLineEdit, QTextEdit {
                font-family: "Microsoft YaHei";
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                background-color: #fafafa;
            }

            QLineEdit:focus, QTextEdit:focus {
                font-family: "Microsoft YaHei";
                border: 2px solid #0078d7;
                background-color: #ffffff;
            }

            QPushButton {
                font-family: "Microsoft YaHei";
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                background-color: #f5f5f5;
            }

            QPushButton:hover {
                border: 2px solid #0078d7;
                background-color: #f0f8ff;
            }

            QPushButton:pressed {
                background-color: #e6f2ff;
            }
        """)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("URL")
        self.line_edit.setFixedHeight(35)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Cookies")

        self.text_log = QTextEdit()
        self.text_log.setPlaceholderText("Log")
        self.text_log.setReadOnly(True)

        self.btn_1 = QPushButton("Download")
        self.btn_1.clicked.connect(
            lambda :threading.Thread(target=self.download).start())
        self.btn_2 = QPushButton("Download using Cookies")
        self.btn_2.clicked.connect(
            lambda :threading.Thread(target=self.download_cookies).start())
        self.btn_1.setEnabled(False)
        self.btn_2.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_1)
        button_layout.addWidget(self.btn_2)

        layout = QVBoxLayout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.text_log)
        layout.addLayout(button_layout)

        self.worker.started.connect(lambda: (
            self.btn_1.setEnabled(False),
            self.btn_2.setEnabled(False)
        ))

        self.worker.finished.connect(lambda: (
            self.btn_1.setEnabled(True),
            self.btn_2.setEnabled(True)
        ))

        self.worker.log.connect(self.append_log)

        self.setLayout(layout)
        threading.Thread(target=self.update).start()        

    def append_log(self, text):
        self.text_log.append(text)
        self.text_log.moveCursor(self.text_log.textCursor().MoveOperation.End)

    def update(self):
        self.text_log.append("Just paste the URL and click \"Download\". If you encounter any login issues, please download using the cookies method.")
        self.text_log.append("Only audio and video files will be downloaded. If you need other formats, please use the command.")
        self.text_log.append("\nUpdating...")
        try:
            proc = subprocess.Popen(
                ["yt-dlp.exe", "-U"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            self.worker.log.emit("yt-dlp.exe not found.")
            return

        for line in proc.stdout:
            self.worker.log.emit(line.rstrip())
        self.worker.finished.emit()

    def download(self):
        self.worker.started.emit()
        self.worker.log.emit("\nDownloading...")
        url = self.line_edit.text()
        try:
            proc = subprocess.Popen(
                ["yt-dlp.exe", "-f", "bv*+ba/best", "-S",
                 "res:1080", "-o", "%(playlist_index)s-%(title)s.%(ext)s", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            self.worker.log.emit("yt-dlp.exe not found.")
            return

        for line in proc.stdout:
            self.worker.log.emit(line.rstrip())
        self.worker.finished.emit()

    def save_cookies(self):
        text = self.text_edit.toPlainText()

        with open("cookies.txt", "w", encoding="utf-8") as f:
            f.write(text)

    def download_cookies(self):
        self.worker.started.emit()
        self.worker.log.emit("\nDownloading...")
        url = self.line_edit.text()
        self.save_cookies()
        try:
            proc = subprocess.Popen(
                ["yt-dlp.exe", "--cookies", "cookies.txt", "-f", "bv*+ba/best", "-S",
                 "res:1080", "-o", "%(playlist_index)s-%(title)s.%(ext)s", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding=locale.getpreferredencoding(False),
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            self.worker.log.emit("yt-dlp.exe not found.")
            return

        for line in proc.stdout:
            self.worker.log.emit(line.rstrip())
        self.worker.finished.emit()

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
