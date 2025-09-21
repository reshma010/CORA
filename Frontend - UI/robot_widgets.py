# Oleg Korobeyko
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
import sys
from api_client import api_client

class RobotWidget(QWidget):
    """
    Individual robot unit widget for the dashboard
    Shows robot name, ID, status, and recent activity
    """
    
    robot_clicked = pyqtSignal(str, str)  # unit_id, unit_name
    
    def __init__(self, unit_data, parent=None):
        super().__init__(parent)
        self.unit_data = unit_data
        self.unit_id = unit_data.get('_id', 'unknown')
        self.unit_name = unit_data.get('unit_name', 'Unknown Unit')
        self.last_seen = unit_data.get('last_seen', None)
        self.packages_count = unit_data.get('packages_count', 0)
        self.total_detections = unit_data.get('total_detections', 0)
        self.rtsp_uris = unit_data.get('rtsp_uris', [])
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header with robot name
        header_layout = QHBoxLayout()
        
        # Robot icon
        icon_label = QLabel("")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        # Robot name and ID
        name_layout = QVBoxLayout()
        
        self.name_label = QLabel(self.unit_name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        self.name_label.setWordWrap(True)
        name_layout.addWidget(self.name_label)
        
        self.id_label = QLabel(f"ID: {self.unit_id}")
        self.id_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        name_layout.addWidget(self.id_label)
        
        header_layout.addLayout(name_layout)
        header_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel()
        self.update_status_indicator()
        header_layout.addWidget(self.status_indicator)
        
        layout.addLayout(header_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        # Packages count
        packages_widget = self.create_stat_widget("", str(self.packages_count), "Packages")
        stats_layout.addWidget(packages_widget)
        
        # Detections count  
        detections_widget = self.create_stat_widget("", str(self.total_detections), "Detections")
        stats_layout.addWidget(detections_widget)
        
        # Camera count
        cameras_widget = self.create_stat_widget("", str(len(self.rtsp_uris)), "Cameras")
        stats_layout.addWidget(cameras_widget)
        
        layout.addLayout(stats_layout)
        
        # Last seen
        last_seen_layout = QHBoxLayout()
        last_seen_layout.addWidget(QLabel("Last seen:"))
        
        self.last_seen_label = QLabel()
        self.update_last_seen_label()
        self.last_seen_label.setStyleSheet("color: #34495e; font-weight: bold;")
        last_seen_layout.addWidget(self.last_seen_label)
        last_seen_layout.addStretch()
        
        layout.addLayout(last_seen_layout)
        
        # View details button
        self.view_button = QPushButton("View Details")
        self.view_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.view_button.clicked.connect(self.on_view_clicked)
        layout.addWidget(self.view_button)
        
    def create_stat_widget(self, icon, value, label):
        """Create a small statistics widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Icon and value
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(icon))
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        top_layout.addWidget(value_label)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(label_widget)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        
        return widget
    
    def update_status_indicator(self):
        """Update the status indicator based on last seen time"""
        if not self.last_seen:
            self.status_indicator.setText("")
            self.status_indicator.setToolTip("Status: Unknown")
            return
            
        try:
            last_seen_dt = datetime.fromisoformat(self.last_seen.replace('Z', '+00:00'))
            now = datetime.now(last_seen_dt.tzinfo)
            time_diff = now - last_seen_dt
            
            if time_diff.total_seconds() < 300:  # 5 minutes
                self.status_indicator.setText("")
                self.status_indicator.setToolTip("Status: Online")
            elif time_diff.total_seconds() < 3600:  # 1 hour
                self.status_indicator.setText("")
                self.status_indicator.setToolTip("Status: Recently Active")
            else:
                self.status_indicator.setText("")
                self.status_indicator.setToolTip("Status: Offline")
                
        except Exception:
            self.status_indicator.setText("")
            self.status_indicator.setToolTip("Status: Unknown")
    
    def update_last_seen_label(self):
        """Update the last seen label with relative time"""
        if not self.last_seen:
            self.last_seen_label.setText("Never")
            return
            
        try:
            last_seen_dt = datetime.fromisoformat(self.last_seen.replace('Z', '+00:00'))
            now = datetime.now(last_seen_dt.tzinfo)
            time_diff = now - last_seen_dt
            
            if time_diff.total_seconds() < 60:
                self.last_seen_label.setText("Just now")
            elif time_diff.total_seconds() < 3600:
                minutes = int(time_diff.total_seconds() / 60)
                self.last_seen_label.setText(f"{minutes}m ago")
            elif time_diff.total_seconds() < 86400:
                hours = int(time_diff.total_seconds() / 3600)
                self.last_seen_label.setText(f"{hours}h ago")
            else:
                days = int(time_diff.total_seconds() / 86400)
                self.last_seen_label.setText(f"{days}d ago")
                
        except Exception:
            self.last_seen_label.setText("Unknown")
    
    def setup_style(self):
        """Setup widget styling"""
        self.setStyleSheet("""
            RobotWidget {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 12px;
            }
            RobotWidget:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)
        
        # Make the widget clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Set fixed size for consistent layout
        self.setFixedSize(280, 180)
        
    def on_view_clicked(self):
        """Handle view details button click"""
        self.robot_clicked.emit(self.unit_id, self.unit_name)
        
    def mousePressEvent(self, event):
        """Handle mouse press on the widget"""
        if event.button() == Qt.LeftButton:
            self.robot_clicked.emit(self.unit_id, self.unit_name)
        super().mousePressEvent(event)


class RobotGridWidget(QScrollArea):
    """
    Grid widget that displays multiple robot units
    """
    
    robot_selected = pyqtSignal(str, str)  # unit_id, unit_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.robots_data = []
        self.robot_widgets = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the scroll area and grid layout"""
        # Create scroll widget
        scroll_widget = QWidget()
        self.setWidget(scroll_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create grid layout
        self.grid_layout = QGridLayout(scroll_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        
        # Add stretch to fill empty space
        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setColumnStretch(0, 1)
        
        # Style the scroll area
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f6fa;
            }
            QScrollBar:vertical {
                background-color: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """)
        
    def update_robots(self, robots_data):
        """Update the grid with new robot data"""
        self.robots_data = robots_data
        self.clear_grid()
        
        if not robots_data:
            self.show_no_robots_message()
            return
            
        # Calculate grid dimensions
        columns = max(1, self.width() // 300)  # Adjust based on widget width
        
        # Add robot widgets to grid
        for i, robot_data in enumerate(robots_data):
            row = i // columns
            col = i % columns
            
            robot_widget = RobotWidget(robot_data)
            robot_widget.robot_clicked.connect(self.robot_selected.emit)
            
            self.grid_layout.addWidget(robot_widget, row, col)
            self.robot_widgets.append(robot_widget)
            
        # Remove stretch and add it after all widgets
        self.grid_layout.setRowStretch(len(robots_data) // columns + 1, 1)
        
    def clear_grid(self):
        """Clear all widgets from the grid"""
        for widget in self.robot_widgets:
            widget.deleteLater()
        self.robot_widgets.clear()
        
        # Clear layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def show_no_robots_message(self):
        """Show message when no robots are available"""
        message_widget = QWidget()
        layout = QVBoxLayout(message_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; color: #bdc3c7;")
        layout.addWidget(icon_label)
        
        text_label = QLabel("No Robot Units Found")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 18px; color: #7f8c8d; font-weight: bold;")
        layout.addWidget(text_label)
        
        subtext_label = QLabel("Robot units appear here when they send detection data")
        subtext_label.setAlignment(Qt.AlignCenter)
        subtext_label.setStyleSheet("font-size: 12px; color: #95a5a6;")
        subtext_label.setWordWrap(True)
        layout.addWidget(subtext_label)
        
        self.grid_layout.addWidget(message_widget, 0, 0, Qt.AlignCenter)
        
    def load_robots(self):
        """Load robots from API"""
        print(" Loading robot units...")
        
        try:
            # Try to get robots with full data first
            success, message, robots_data = api_client.get_robots()
            
            if success and robots_data.get('units'):
                print(f" Loaded {len(robots_data['units'])} robot units from robots endpoint")
                self.update_robots(robots_data['units'])
                return
            
            # Fallback to active units endpoint
            print(" Falling back to active units endpoint...")
            success, message, units_data = api_client.get_active_units()
            
            if success and units_data.get('units'):
                print(f" Loaded {len(units_data['units'])} robot units from detections endpoint")
                self.update_robots(units_data['units'])
            else:
                print(f" No robot units found: {message}")
                self.update_robots([])
                
        except Exception as e:
            print(f" Error loading robots: {e}")
            self.update_robots([])
            
    def refresh_robots(self):
        """Refresh robot data"""
        self.load_robots()
        
    def resizeEvent(self, event):
        """Handle resize event to adjust grid columns"""
        super().resizeEvent(event)
        if self.robots_data:
            self.update_robots(self.robots_data)