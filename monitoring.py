import sys
import sqlite3
import psutil
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QHBoxLayout,
    QFrame,
)



class MonitoringApp(QWidget):
    def __init__(self):
        super().__init__()

        # Database setup
        self.conn = sqlite3.connect("monitoring.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring (
                timestamp TEXT,
                cpu_load REAL,
                ram_free INTEGER,
                ram_total INTEGER,
                disk_free INTEGER,
                disk_total INTEGER
            )
        """)
        self.conn.commit()

        # UI setup
        self.init_ui()
        
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_monitoring_data)
        self.recording = False
        self.start_time = None

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Header
        header_label = QLabel("Системный мониторинг")
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("color: #2E86C1; text-align: center;")
        self.layout.addWidget(header_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(separator)

        # Labels for system info
        self.cpu_label = QLabel("ЦП: ...")
        self.cpu_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.cpu_label)

        self.ram_label = QLabel("ОЗУ: ...")
        self.ram_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.ram_label)

        self.disk_label = QLabel("ПЗУ: ...")
        self.disk_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.disk_label)

        # Interval selection
        self.interval_label = QLabel("Интервал обновления (сек):")
        self.interval_label.setFont(QFont("Arial", 11))
        self.layout.addWidget(self.interval_label)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setStyleSheet("background-color: #E8F8F5; font-size: 12px;")
        self.layout.addWidget(self.interval_spinbox)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Начать запись")
        self.start_button.setStyleSheet("background-color: #2ECC71; color: white; font-size: 12px; padding: 5px;")
        self.start_button.clicked.connect(self.start_recording)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Остановить")
        self.stop_button.setStyleSheet("background-color: #E74C3C; color: white; font-size: 12px; padding: 5px;")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.hide()
        button_layout.addWidget(self.stop_button)

        self.layout.addLayout(button_layout)

        # Timer label
        self.timer_label = QLabel("Время записи: 0 сек")
        self.timer_label.setFont(QFont("Arial", 12))
        self.timer_label.setStyleSheet("color: #2980B9;")
        self.timer_label.hide()
        self.layout.addWidget(self.timer_label)

        self.setLayout(self.layout)
        self.setWindowTitle("Мониторинг системы")
        self.setStyleSheet("background-color: #FDFEFE; padding: 10px;")
        self.setFixedSize(600, 400)

    def update_monitoring_data(self):
        # Fetch system data
        cpu_load = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Update labels
        self.cpu_label.setText(f"ЦП: {cpu_load}%")
        self.ram_label.setText(f"ОЗУ: {ram.available // (1024 ** 2)} MB / {ram.total // (1024 ** 2)} MB")
        self.disk_label.setText(f"ПЗУ: {disk.free // (1024 ** 3)} GB / {disk.total // (1024 ** 3)} GB")

        # Record data if recording
        if self.recording:
            self.cursor.execute("INSERT INTO monitoring VALUES (?, ?, ?, ?, ?, ?)", (
                time.strftime("%Y-%m-%d %H:%M:%S"),
                cpu_load,
                ram.available // (1024 ** 2),
                ram.total // (1024 ** 2),
                disk.free // (1024 ** 3),
                disk.total // (1024 ** 3)
            ))
            self.conn.commit()

            # Update timer
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.setText(f"Время записи: {elapsed_time} сек")

    def start_recording(self):
        self.recording = True
        self.start_time = time.time()
        self.timer_label.show()
        self.stop_button.show()
        self.start_button.hide()
        self.timer.start(self.interval_spinbox.value() * 1000)

    def stop_recording(self):
        self.recording = False
        self.timer_label.hide()
        self.stop_button.hide()
        self.start_button.show()
        self.timer.stop()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MonitoringApp()
    window.show()
    sys.exit(app.exec_())
