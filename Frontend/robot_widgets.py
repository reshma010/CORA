# Oleg Korobeyko
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
import sys
from api_client import api_client
from theme_manager import ThemeManager

class RobotWidget(QWidget):
    """
    Individual robot unit widget for the dashboard
    Shows robot name, ID, status, and recent activity
    """
    
    robot_clicked = pyqtSignal(str, str)  # unit_id, unit_name
    
    def __init__(self, unit_data, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Main unit ID display - CORA format
        unit_id_display = self.format_unit_id(self.unit_id)
        self.unit_id_label = QLabel(unit_id_display)
        self.unit_id_label.setAlignment(Qt.AlignCenter)
        self.unit_id_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'Trebuchet MS';
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
        """)
        layout.addWidget(self.unit_id_label)
        
        # Detection count with icon
        detection_layout = QHBoxLayout()
        detection_layout.setAlignment(Qt.AlignCenter)
        
        detection_icon = QLabel("")
        detection_icon.setStyleSheet("font-size: 16px; background-color: transparent;")
        detection_layout.addWidget(detection_icon)
        
        self.detection_count_label = QLabel(f"{self.total_detections}")
        self.detection_count_label.setStyleSheet(f"""
            QLabel {{
                font-family: 'Trebuchet MS';
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: transparent;
                margin-left: 5px;
            }}
        """)
        detection_layout.addWidget(self.detection_count_label)
        
        detection_text = QLabel("Detections")
        detection_text.setStyleSheet(f"""
            QLabel {{
                font-family: 'Trebuchet MS';
                font-size: 12px;
                color: rgba(255, 255, 255, 0.8);
                background-color: transparent;
                margin-left: 8px;
            }}
        """)
        detection_layout.addWidget(detection_text)
        
        layout.addLayout(detection_layout)
        
        # Status indicator (subtle)
        self.status_indicator = QLabel()
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.update_status_indicator()
        layout.addWidget(self.status_indicator)
        
        # Add stretch to push everything to center
        layout.addStretch()
        
    def format_unit_id(self, unit_id):
        """Format unit ID to CORA-XXXX format"""
        if not unit_id or unit_id == 'unknown':
            return "CORA-?????"
        
        # If it's already in CORA format, return as is
        if unit_id.upper().startswith('CORA-'):
            return unit_id.upper()
        
        # If it's a short ID, format as CORA-XXXX
        if len(unit_id) <= 4:
            return f"CORA-{unit_id.upper().zfill(4)}"
        
        # For longer IDs, take last 4 characters
        return f"CORA-{unit_id[-4:].upper()}"
        
    def create_stat_widget(self, icon, value, label):
        """Create a small statistics widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(3)
        layout.setContentsMargins(6, 6, 6, 6)
        
        # Icon and value
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(icon))
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {self.theme_manager.get_color('text')}; font-family: Trebuchet MS;")
        top_layout.addWidget(value_label)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"font-size: 11px; color: {self.theme_manager.get_color('accent')}; font-family: Trebuchet MS;")
        layout.addWidget(label_widget)
        
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 4px;
            }}
        """)
        
        return widget
    
    def update_status_indicator(self):
        """Update the status indicator based on last seen time"""
        if not self.last_seen:
            self.status_indicator.setText("●")
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                }}
            """)
            return
        
        try:
            # Parse the timestamp
            if isinstance(self.last_seen, str):
                # Try different formats
                try:
                    last_seen_dt = datetime.fromisoformat(self.last_seen.replace('Z', '+00:00'))
                except:
                    try:
                        last_seen_dt = datetime.strptime(self.last_seen, '%Y-%m-%dT%H:%M:%S.%fZ')
                    except:
                        last_seen_dt = datetime.strptime(self.last_seen, '%Y-%m-%dT%H:%M:%SZ')
            else:
                last_seen_dt = self.last_seen
            
            # Calculate time difference
            now = datetime.utcnow()
            time_diff = now - last_seen_dt.replace(tzinfo=None)
            
            # Determine status
            if time_diff < timedelta(minutes=5):
                # Online
                self.status_indicator.setText("● Online")
                self.status_indicator.setStyleSheet(f"""
                    QLabel {{
                        color: #4ade80;
                        font-size: 10px;
                        font-weight: bold;
                        font-family: Trebuchet MS;
                    }}
                """)
            elif time_diff < timedelta(hours=1):
                # Recently active
                self.status_indicator.setText("● Recent")
                self.status_indicator.setStyleSheet(f"""
                    QLabel {{
                        color: #fbbf24;
                        font-size: 10px;
                        font-weight: bold;
                        font-family: Trebuchet MS;
                    }}
                """)
            else:
                # Offline
                self.status_indicator.setText("● Offline")
                self.status_indicator.setStyleSheet(f"""
                    QLabel {{
                        color: rgba(255, 255, 255, 0.6);
                        font-size: 10px;
                        font-weight: bold;
                        font-family: Trebuchet MS;
                    }}
                """)
                
        except Exception as e:
            print(f"Error parsing last_seen: {e}")
            self.status_indicator.setText("● Unknown")
            self.status_indicator.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 10px;
                    font-weight: bold;
                    font-family: Trebuchet MS;
                }}
            """)
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
        print(f"DEBUG: Setting robot widget style with green color #0c554a")
        
        # Use minimal stylesheet - let paintEvent handle the appearance
        self.setStyleSheet("""
            RobotWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Set object name for more specific targeting
        self.setObjectName("robot_widget")
        
        # Also set background using palette (alternative method)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#0c554a"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Make the widget clickable
        self.setCursor(Qt.PointingHandCursor)
        
        # Set fixed size for consistent layout - larger for better text display
        self.setFixedSize(280, 180)
        
        print(f"DEBUG: Widget stylesheet applied: {self.styleSheet()[:100]}...")
        print(f"DEBUG: Widget palette background: {palette.color(self.backgroundRole()).name()}")
        
        # Ensure all child widgets have transparent backgrounds
        self.setStyleSheet("""
            RobotWidget {
                background-color: transparent;
                border: none;
            }
            RobotWidget QLabel {
                background-color: transparent;
            }
            RobotWidget QWidget {
                background-color: transparent;
            }
        """)
        

    
    def paintEvent(self, event):
        """Custom paint event to ensure green background with rounded corners"""
        from PyQt5.QtGui import QPainter, QBrush, QPen, QPainterPath
        from PyQt5.QtCore import QRectF
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Clear the background first
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))  # transparent
        
        # Create a rounded rectangle path with proper margins - convert to QRectF
        rect = QRectF(self.rect().adjusted(1, 1, -1, -1))  # Convert QRect to QRectF
        path = QPainterPath()
        path.addRoundedRect(rect, 16.0, 16.0)  # Use float values
        
        # Set clipping to the rounded path
        painter.setClipPath(path)
        
        # Fill the clipped area with green color
        painter.fillRect(self.rect(), QColor("#0c554a"))
        
        # Remove clipping and draw the border
        painter.setClipping(False)
        painter.setPen(QPen(QColor(255, 255, 255, 51), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # No fill, just border
        painter.drawRoundedRect(rect, 16.0, 16.0)  # Use float values
        
    def on_view_clicked(self):
        """Handle view details button click"""
        formatted_id = self.format_unit_id(self.unit_id)
        self.robot_clicked.emit(self.unit_id, formatted_id)
        
    def mousePressEvent(self, event):
        """Handle mouse press on the widget"""
        if event.button() == Qt.LeftButton:
            formatted_id = self.format_unit_id(self.unit_id)
            self.robot_clicked.emit(self.unit_id, formatted_id)
        super().mousePressEvent(event)


class RobotGridWidget(QScrollArea):
    """
    Grid widget that displays multiple robot units
    """
    
    robot_selected = pyqtSignal(str, str)  # unit_id, unit_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.robots_data = []
        self.robot_widgets = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the scroll area and grid layout"""
        # Create scroll widget
        scroll_widget = QWidget()
        self.setWidget(scroll_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create grid layout
        self.grid_layout = QGridLayout(scroll_widget)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        
        # Add stretch to fill empty space
        self.grid_layout.setRowStretch(0, 1)
        self.grid_layout.setColumnStretch(0, 1)
        
        # Style the scroll area
        self.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.theme_manager.get_color('background')};
                border-radius: 8px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.theme_manager.get_color('surface')};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.theme_manager.get_color('primary')};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {self.theme_manager.get_color('primary_hover')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
    def update_robots(self, robots_data):
        """Update the grid with new robot data"""
        self.robots_data = robots_data
        self.clear_grid()
        
        if not robots_data:
            self.show_no_robots_message()
            return
            
        # Calculate grid dimensions
        columns = max(1, self.width() // 320)  # Adjust based on widget width (280px + margins)
        
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
        icon_label.setStyleSheet(f"font-size: 48px; color: {self.theme_manager.get_color('accent')};")
        layout.addWidget(icon_label)
        
        text_label = QLabel("No Robot Units Found")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"font-size: 18px; color: {self.theme_manager.get_color('text')}; font-weight: bold; font-family: Trebuchet MS;")
        layout.addWidget(text_label)
        
        subtext_label = QLabel("Robot units appear here when they send detection data")
        subtext_label.setAlignment(Qt.AlignCenter)
        subtext_label.setStyleSheet(f"font-size: 12px; color: {self.theme_manager.get_color('accent')}; font-family: Trebuchet MS;")
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