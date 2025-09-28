# Reshma Shaik
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QTimer
import datetime
from icon_utils import IconManager
from theme_manager import ThemeManager

class ActivityPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        
        # Set page background
        self.setStyleSheet(f"""
            ActivityPage {{
                background-color: {self.theme_manager.get_color('background')};
            }}
        """)

        #Main Layout for the Activity Page
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title Label
        title = QLabel("Activity Logs")
        title.setAlignment(Qt.AlignCenter)  # Center the text
        title.setStyleSheet(f"""
            font-size: 24px; 
            font-weight: bold; 
            color: {self.theme_manager.get_color('primary')};
            font-family: 'Trebuchet MS';
            margin: 20px 0px;
        """)  # Styling for title
        layout.addWidget(title)

        # Table Widget for Logs
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # 3 columns: Time, Activity, Status
        self.table.setHorizontalHeaderLabels(["Time", "Activity", "Status"])  # Set column headers
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.theme_manager.get_color('background')};
                border: 1px solid {self.theme_manager.get_color('accent')};
                border-radius: 10px;
                gridline-color: {self.theme_manager.get_color('accent')};
                font-family: 'Trebuchet MS';
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {self.theme_manager.get_color('text')};
            }}
            QTableWidget::item:selected {{
                background-color: {self.theme_manager.get_color('primary')};
            }}
            QHeaderView::section {{
                background-color: {self.theme_manager.get_color('background')};
                border: 1px solid {self.theme_manager.get_color('accent')};
                padding: 8px;
                font-weight: bold;
                color: {self.theme_manager.get_color('text')};
                font-family: 'Trebuchet MS';
            }}
        """)
        layout.addWidget(self.table)

        # Refresh Button with duotone icon
        self.refresh_btn = QPushButton("⟲ Refresh Logs")
        IconManager.set_button_icon(self.refresh_btn, 'refresh', "Refresh Logs", size=16)
        self.refresh_btn.setFixedWidth(200)
        self.refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme_manager.get_color('primary')};
                color: {self.theme_manager.get_color('text')};
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Trebuchet MS';
            }}
            QPushButton:hover {{
                background-color: {self.theme_manager.get_color('secondary')};
            }}
        """)
        # Connect button click to reload logs
        self.refresh_btn.clicked.connect(self.load_logs)
        layout.addWidget(self.refresh_btn, 0, Qt.AlignCenter)

        # Load Initial Logs when the Page Opens
        self.load_logs()

        # Auto Refresh Every 10 Seconds
        # Creates a timer that triggers `load_logs` automatically
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_logs)  # When timer times out, reload logs
        self.timer.start(10000)  # Interval: 10000ms = 10 seconds

    def load_logs(self):
        """
        Load activity logs into the table.
        - In a production app, this connects to a database or backend API.
        - Currently uses simulated logs for demonstration.
        """

        # Clear any old data before reloading
        self.table.setRowCount(0)

        # Simulated logs with timestamp, activity description, and status
        simulated_logs = [
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Loitering detected", "Alert Sent"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Normal activity", "No Action"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Unauthorized entry attempt", "Security Notified"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Camera offline", "Maintenance Required"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Motion detected in Zone A", "Monitoring"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Crowd gathering", "Alert Sent"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "System check completed", "OK"),
            (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Suspicious package spotted", "Alert Sent"),
        ]

        # Insert each log into the table row by row
        for row_num, log in enumerate(simulated_logs):
            self.table.insertRow(row_num)  # Add a new row
            for col_num, value in enumerate(log):
                # Create a table item for each value (time, activity, status)
                self.table.setItem(row_num, col_num, QTableWidgetItem(value))
