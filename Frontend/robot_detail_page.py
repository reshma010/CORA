# Oleg Korobeyko
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta
import json
from api_client import api_client
import sys

class StreamWidget(QWidget):
    """
    Enhanced widget to display a single RTSP stream with status and statistics
    Shows placeholder for now, can be extended with actual video display
    """
    
    def __init__(self, rtsp_uri, stream_number, detection_data=None, parent=None):
        super().__init__(parent)
        self.rtsp_uri = rtsp_uri
        self.stream_number = stream_number
        self.detection_data = detection_data or []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the stream widget UI"""
        self.setFixedSize(320, 240)
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header with stream info
        header_layout = QHBoxLayout()
        
        # Stream title
        title_label = QLabel(f"Camera {self.stream_number}")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        status_label = QLabel("ACTIVE")
        status_label.setStyleSheet("color: #27ae60; font-size: 10px; font-weight: bold;")
        status_label.setToolTip("Stream Active")
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # Video area
        video_area = QLabel()
        video_area.setMinimumHeight(120)
        video_area.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 1px solid #555;
                border-radius: 4px;
                color: #bbb;
            }
        """)
        video_area.setText("Video Feed\n(Available)")
        video_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(video_area)
        
        # Stream statistics
        stats_layout = QHBoxLayout()
        
        # Recent detections count
        recent_count = len([d for d in self.detection_data if self.is_recent_detection(d)])
        detections_label = QLabel(f"Detections: {recent_count}")
        detections_label.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        stats_layout.addWidget(detections_label)
        
        stats_layout.addStretch()
        
        # Stream resolution
        resolution_label = QLabel("1080p")
        resolution_label.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        stats_layout.addWidget(resolution_label)
        
        layout.addLayout(stats_layout)
        
        # URI display (truncated)
        uri_display = self.rtsp_uri
        if len(uri_display) > 35:
            uri_display = uri_display[:32] + "..."
            
        uri_label = QLabel(uri_display)
        uri_label.setStyleSheet("font-size: 9px; color: #7f8c8d; font-family: monospace;")
        uri_label.setWordWrap(True)
        layout.addWidget(uri_label)
        
    def is_recent_detection(self, detection):
        """Check if detection is from the last hour"""
        try:
            from datetime import datetime, timedelta
            detection_time = datetime.fromisoformat(detection.get('timestamp', '').replace('Z', '+00:00'))
            return detection_time > datetime.now().replace(tzinfo=detection_time.tzinfo) - timedelta(hours=1)
        except:
            return False


class DetectionItemWidget(QWidget):
    """
    Widget to display a single detection item
    Can be expanded to show detailed information
    """
    
    def __init__(self, detection_data, parent=None):
        super().__init__(parent)
        self.detection_data = detection_data
        self.expanded = False
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """Setup the detection item UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(12, 8, 12, 8)
        
        # Header (always visible)
        self.create_header()
        
        # Details (expandable)
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setContentsMargins(0, 8, 0, 0)
        self.create_details()
        
        self.details_widget.hide()
        self.main_layout.addWidget(self.details_widget)
        
    def create_header(self):
        """Create the header section (always visible)"""
        header_layout = QHBoxLayout()
        
        # Expand/collapse icon
        self.expand_icon = QLabel("▶")
        self.expand_icon.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        self.expand_icon.setFixedSize(20, 20)
        self.expand_icon.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.expand_icon)
        
        # Action type without emoji
        action_text = self.detection_data.get('action_type', 'Unknown').replace('_', ' ').title()
        
        self.action_label = QLabel(action_text)
        self.action_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        header_layout.addWidget(self.action_label)
        
        header_layout.addStretch()
        
        # Confidence
        confidence = self.detection_data.get('confidence', 0) * 100
        confidence_color = self.get_confidence_color(confidence)
        
        self.confidence_label = QLabel(f"{confidence:.1f}%")
        self.confidence_label.setStyleSheet(f"font-weight: bold; color: {confidence_color}; background-color: {confidence_color}20; padding: 4px 8px; border-radius: 4px;")
        header_layout.addWidget(self.confidence_label)
        
        # Timestamp
        timestamp_str = self.format_timestamp(self.detection_data.get('timestamp', ''))
        self.timestamp_label = QLabel(timestamp_str)
        self.timestamp_label.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-left: 12px;")
        header_layout.addWidget(self.timestamp_label)
        
        self.main_layout.addLayout(header_layout)
        
    def create_details(self):
        """Create the details section (expandable)"""
        # Person and frame info
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Person ID:"), 0, 0)
        person_id_label = QLabel(str(self.detection_data.get('person_id', 'N/A')))
        person_id_label.setStyleSheet("font-weight: bold; color: #3498db;")
        info_layout.addWidget(person_id_label, 0, 1)
        
        info_layout.addWidget(QLabel("Frame #:"), 0, 2)
        frame_label = QLabel(str(self.detection_data.get('frame_number', 'N/A')))
        frame_label.setStyleSheet("font-family: monospace;")
        info_layout.addWidget(frame_label, 0, 3)
        
        # Enhanced tracking info
        tracking_info = self.detection_data.get('tracking_info', {})
        is_tracked = tracking_info.get('is_tracked', False)
        tracking_age = tracking_info.get('tracking_age', 0)
        
        info_layout.addWidget(QLabel("Tracking:"), 1, 0)
        tracking_widget = self.create_tracking_status_widget(is_tracked, tracking_age)
        info_layout.addWidget(tracking_widget, 1, 1)
        
        # Enhanced bounding box info with visualization
        bbox = self.detection_data.get('normalized_bbox', {})
        info_layout.addWidget(QLabel("Position:"), 1, 2)
        bbox_widget = self.create_bbox_widget(bbox)
        info_layout.addWidget(bbox_widget, 1, 3)
        
        self.details_layout.addLayout(info_layout)
        
        # Add bounding box confidence if available
        bbox_conf = bbox.get('confidence', 0) if bbox else 0
        if bbox_conf > 0:
            conf_layout = QHBoxLayout()
            conf_layout.addWidget(QLabel("Detection Quality:"))
            bbox_conf_bar = self.create_confidence_bar(bbox_conf, "Detection")
            conf_layout.addWidget(bbox_conf_bar)
            conf_layout.addStretch()
            self.details_layout.addLayout(conf_layout)
        
        # Enhanced pose scores
        pose_scores = self.detection_data.get('pose_scores', {})
        if pose_scores:
            # Add a separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setStyleSheet("color: #bdc3c7; margin: 8px 0px;")
            self.details_layout.addWidget(separator)
            
            # Header with total pose confidence
            pose_header_layout = QHBoxLayout()
            pose_header_layout.addWidget(QLabel("Pose Analysis:"))
            
            # Calculate dominant pose
            max_score = max(pose_scores.values()) if pose_scores.values() else 0
            dominant_action = max(pose_scores, key=pose_scores.get) if pose_scores else "unknown"
            
            if max_score > 0.1:
                dominant_label = QLabel(f"Primary: {dominant_action.replace('_', ' ').title()}")
                dominant_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 11px;")
                pose_header_layout.addWidget(dominant_label)
                
            pose_header_layout.addStretch()
            self.details_layout.addLayout(pose_header_layout)
            
            # Scores in a more compact layout
            scores_layout = QGridLayout()
            scores_widget = QWidget()
            scores_widget.setLayout(scores_layout)
            
            row = 0
            col = 0
            
            # Sort poses by score (highest first)
            sorted_poses = sorted(pose_scores.items(), key=lambda x: x[1], reverse=True)
            
            for action, score in sorted_poses:
                if score > 0.005:  # Show even smaller scores for completeness
                    # Create a mini widget for each pose
                    pose_widget = QWidget()
                    pose_layout = QHBoxLayout(pose_widget)
                    pose_layout.setContentsMargins(4, 2, 4, 2)
                    
                    # Action name without emoji
                    action_label = QLabel(action.replace('_', ' ').title())
                    action_label.setStyleSheet("font-size: 10px; min-width: 70px;")
                    pose_layout.addWidget(action_label)
                    
                    # Mini score bar
                    mini_score_bar = self.create_mini_score_bar(score)
                    pose_layout.addWidget(mini_score_bar)
                    
                    scores_layout.addWidget(pose_widget, row, col)
                    
                    col += 1
                    if col >= 2:  # 2 columns
                        col = 0
                        row += 1
                        
            self.details_layout.addWidget(scores_widget)
        
        # Enhanced thumbnail display
        thumbnail_data = self.detection_data.get('thumbnail')
        if thumbnail_data:
            self.create_thumbnail_display(thumbnail_data)
        else:
            # Show message for missing thumbnail
            thumbnail_placeholder = QLabel("No thumbnail available")
            thumbnail_placeholder.setStyleSheet("color: #95a5a6; font-style: italic; font-size: 10px;")
            self.details_layout.addWidget(thumbnail_placeholder)
    
    def create_thumbnail_display(self, thumbnail_data):
        """Create thumbnail display widget"""
        thumbnail_layout = QHBoxLayout()
        
        # Thumbnail label
        thumb_label = QLabel("Detection Image:")
        thumb_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        thumbnail_layout.addWidget(thumb_label)
        
        try:
            # Try to decode and display the thumbnail
            import base64
            from io import BytesIO
            
            # Decode base64 image
            image_data = base64.b64decode(thumbnail_data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            
            if not pixmap.isNull():
                # Scale the image to a reasonable thumbnail size
                scaled_pixmap = pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label = QLabel()
                image_label.setPixmap(scaled_pixmap)
                image_label.setStyleSheet("""
                    border: 1px solid #bdc3c7;
                    border-radius: 3px;
                    background-color: white;
                    padding: 2px;
                """)
                thumbnail_layout.addWidget(image_label)
            else:
                # Invalid image data
                error_label = QLabel("Invalid image data")
                error_label.setStyleSheet("color: #e74c3c; font-style: italic; font-size: 10px;")
                thumbnail_layout.addWidget(error_label)
                
        except Exception as e:
            # Error decoding image
            error_label = QLabel(f"Error loading image: {str(e)[:20]}...")
            error_label.setStyleSheet("color: #e74c3c; font-style: italic; font-size: 10px;")
            thumbnail_layout.addWidget(error_label)
        
        thumbnail_layout.addStretch()
        self.details_layout.addLayout(thumbnail_layout)
    
    def create_score_bar(self, score):
        """Create a visual score bar"""
        widget = QWidget()
        widget.setFixedSize(100, 16)
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(score * 100))
        progress.setTextVisible(True)
        progress.setFormat(f"{score:.2f}")
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        
        return widget
    
    def create_confidence_bar(self, confidence, label_text="Confidence"):
        """Create a visual confidence bar with color coding"""
        widget = QWidget()
        widget.setFixedSize(120, 20)
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        confidence_percent = int(confidence * 100)
        progress.setValue(confidence_percent)
        progress.setTextVisible(True)
        progress.setFormat(f"{confidence:.2f}")
        
        # Color code based on confidence level
        if confidence >= 0.8:
            color = "#27ae60"  # Green
        elif confidence >= 0.6:
            color = "#f39c12"  # Orange
        else:
            color = "#e74c3c"  # Red
            
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
                font-size: 10px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        
        return widget
    
    def create_tracking_status_widget(self, is_tracked, tracking_age):
        """Create a widget showing tracking status"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if is_tracked:
            status_label = QLabel("Active")
            status_label.setStyleSheet("""
                background-color: #27ae60;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            """)
            layout.addWidget(status_label)
            
            age_label = QLabel(f"{tracking_age}f")
            age_label.setStyleSheet("font-size: 10px; color: #7f8c8d; margin-left: 4px;")
            layout.addWidget(age_label)
        else:
            status_label = QLabel("Not Tracked")
            status_label.setStyleSheet("""
                background-color: #95a5a6;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            """)
            layout.addWidget(status_label)
        
        layout.addStretch()
        return widget
    
    def create_bbox_widget(self, bbox):
        """Create a widget showing bounding box information with mini visualization"""
        widget = QWidget()
        widget.setFixedSize(100, 60)
        
        if not bbox:
            label = QLabel("No position data")
            label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px;")
            layout = QVBoxLayout(widget)
            layout.addWidget(label)
            return widget
        
        # Mini bounding box visualization
        viz_widget = QWidget()
        viz_widget.setFixedSize(80, 40)
        viz_widget.setStyleSheet("""
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 3px;
        """)
        
        # Paint the bounding box on the mini visualization
        def paint_bbox(event):
            painter = QPainter(viz_widget)
            painter.setPen(QPen(QColor("#e74c3c"), 2))
            
            # Calculate position in mini widget
            x = int(bbox.get('x', 0) * 70) + 5
            y = int(bbox.get('y', 0) * 30) + 5
            w = int(bbox.get('width', 0) * 70)
            h = int(bbox.get('height', 0) * 30)
            
            painter.drawRect(x, y, w, h)
            painter.end()
        
        viz_widget.paintEvent = paint_bbox
        
        # Text info
        text_label = QLabel(f"({bbox.get('x', 0):.2f}, {bbox.get('y', 0):.2f})")
        text_label.setStyleSheet("font-size: 9px; color: #2c3e50;")
        text_label.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(viz_widget)
        layout.addWidget(text_label)
        
        return widget
    
    def create_mini_score_bar(self, score):
        """Create a smaller score bar for pose scores"""
        widget = QWidget()
        widget.setFixedSize(60, 12)
        
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(score * 100))
        progress.setTextVisible(True)
        progress.setFormat(f"{score:.2f}")
        
        # Color coding for pose confidence
        if score >= 0.5:
            color = "#27ae60"
        elif score >= 0.2:
            color = "#f39c12"
        else:
            color = "#95a5a6"
            
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 2px;
                text-align: center;
                font-size: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 1px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(progress)
        
        return widget
    

    
    def get_confidence_color(self, confidence):
        """Get color based on confidence level"""
        if confidence >= 80:
            return "#27ae60"  # Green
        elif confidence >= 60:
            return "#f39c12"  # Orange
        else:
            return "#e74c3c"  # Red
    
    def format_timestamp(self, timestamp_str):
        """Format timestamp for display"""
        if not timestamp_str:
            return "Unknown time"
            
        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.strftime("%H:%M:%S")
        except:
            return "Unknown time"
    
    def setup_style(self):
        """Setup widget styling"""
        self.setStyleSheet("""
            DetectionItemWidget {
                background-color: white;
                border: 1px solid #e1e8ed;
                border-radius: 6px;
                margin: 2px;
            }
            DetectionItemWidget:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)
        
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Handle mouse press to toggle expansion"""
        if event.button() == Qt.LeftButton:
            self.toggle_expansion()
        super().mousePressEvent(event)
        
    def toggle_expansion(self):
        """Toggle the expanded state"""
        self.expanded = not self.expanded
        
        if self.expanded:
            self.details_widget.show()
            self.expand_icon.setText("▼")
        else:
            self.details_widget.hide()
            self.expand_icon.setText("▶")


class RobotDetailPage(QWidget):
    """
    Detailed page for a specific robot unit
    Shows streams and detection data
    """
    
    back_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_id = None
        self.unit_name = None
        self.unit_data = {}
        self.detection_widgets = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the detail page UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header with back button and title
        header_layout = QHBoxLayout()
        
        self.back_button = QPushButton("<- Back to Dashboard")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.back_button.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_button)
        
        header_layout.addStretch()
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet("""
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
        """)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Streams section
        streams_label = QLabel("Camera Streams")
        streams_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 16px;")
        main_layout.addWidget(streams_label)
        
        self.streams_layout = QHBoxLayout()
        self.streams_layout.setSpacing(12)
        main_layout.addLayout(self.streams_layout)
        
        # Detection Statistics Panel
        self.stats_panel = self.create_statistics_panel()
        main_layout.addWidget(self.stats_panel)
        
        # Detections section
        detections_header_layout = QHBoxLayout()
        
        detections_label = QLabel("Recent Detections")
        detections_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 16px;")
        detections_header_layout.addWidget(detections_label)
        
        detections_header_layout.addStretch()
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Actions",
            "Sitting Down", 
            "Getting Up",
            "Sitting",
            "Standing", 
            "Walking",
            "Jumping"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_detections)
        detections_header_layout.addWidget(QLabel("Filter:"))
        detections_header_layout.addWidget(self.filter_combo)
        
        main_layout.addLayout(detections_header_layout)
        
        # Detections list
        self.detections_scroll = QScrollArea()
        self.detections_scroll.setWidgetResizable(True)
        self.detections_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.detections_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.detections_widget = QWidget()
        self.detections_layout = QVBoxLayout(self.detections_widget)
        self.detections_layout.setSpacing(4)
        self.detections_layout.setContentsMargins(8, 8, 8, 8)
        
        self.detections_scroll.setWidget(self.detections_widget)
        main_layout.addWidget(self.detections_scroll)
        
        # Loading indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 40px;")
        main_layout.addWidget(self.loading_label)
        
    def create_statistics_panel(self):
        """Create a statistics panel for detection data"""
        stats_widget = QWidget()
        stats_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                margin: 8px 0px;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(16, 12, 16, 12)
        
        # Header
        header_label = QLabel("Detection Analytics")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 8px;")
        stats_layout.addWidget(header_label)
        
        # Create layout for stats - populated when data loads
        self.stats_content_layout = QHBoxLayout()
        stats_layout.addLayout(self.stats_content_layout)
        
        # Initially hidden
        stats_widget.hide()
        
        return stats_widget
    
    def update_statistics_panel(self, detections):
        """Update the statistics panel with detection data"""
        # Clear existing content
        while self.stats_content_layout.count():
            child = self.stats_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not detections:
            self.stats_panel.hide()
            return
        
        # Calculate statistics
        action_counts = {}
        confidence_sum = 0
        tracking_count = 0
        total_detections = len(detections)
        
        confidence_levels = {"high": 0, "medium": 0, "low": 0}
        
        for detection in detections:
            # Count actions
            action = detection.get('action_type', 'unknown')
            action_counts[action] = action_counts.get(action, 0) + 1
            
            # Sum confidence
            conf = detection.get('confidence', 0)
            confidence_sum += conf
            
            # Confidence levels
            if conf >= 0.8:
                confidence_levels["high"] += 1
            elif conf >= 0.5:
                confidence_levels["medium"] += 1
            else:
                confidence_levels["low"] += 1
            
            # Tracking stats
            tracking_info = detection.get('tracking_info', {})
            if tracking_info.get('is_tracked', False):
                tracking_count += 1
        
        avg_confidence = confidence_sum / total_detections if total_detections > 0 else 0
        tracking_rate = (tracking_count / total_detections * 100) if total_detections > 0 else 0
        
        # Create stats widgets
        
        # Total detections
        total_widget = self.create_stat_widget("Total Detections", str(total_detections), "#3498db")
        self.stats_content_layout.addWidget(total_widget)
        
        # Average confidence
        conf_widget = self.create_stat_widget("Avg Confidence", f"{avg_confidence:.1%}", "#27ae60")
        self.stats_content_layout.addWidget(conf_widget)
        
        # Tracking rate
        track_widget = self.create_stat_widget("Tracking Rate", f"{tracking_rate:.1f}%", "#9b59b6")
        self.stats_content_layout.addWidget(track_widget)
        
        # Most common action
        if action_counts:
            most_common = max(action_counts, key=action_counts.get)
            most_common_count = action_counts[most_common]
            action_widget = self.create_stat_widget("Top Action", 
                                                  f"{most_common.replace('_', ' ').title()}\n({most_common_count})", 
                                                  "#f39c12")
            self.stats_content_layout.addWidget(action_widget)
        
        # Confidence distribution chart
        conf_chart_widget = self.create_confidence_chart(confidence_levels, total_detections)
        self.stats_content_layout.addWidget(conf_chart_widget)
        
        self.stats_panel.show()
    
    def create_stat_widget(self, title, value, color):
        """Create a single statistic widget"""
        widget = QWidget()
        widget.setFixedSize(120, 80)
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 6px;
                margin: 4px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 10px; color: #7f8c8d; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        return widget
    
    def create_confidence_chart(self, confidence_levels, total):
        """Create a mini confidence distribution chart"""
        widget = QWidget()
        widget.setFixedSize(140, 80)
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #34495e;
                border-radius: 6px;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        
        # Title
        title_label = QLabel("Confidence Levels")
        title_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #2c3e50; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Bars
        bars_layout = QHBoxLayout()
        
        colors = {"high": "#27ae60", "medium": "#f39c12", "low": "#e74c3c"}
        labels = {"high": "High\n80%+", "medium": "Med\n50%+", "low": "Low\n<50%"}
        
        for level in ["high", "medium", "low"]:
            bar_widget = QWidget()
            bar_layout = QVBoxLayout(bar_widget)
            bar_layout.setContentsMargins(2, 2, 2, 2)
            
            # Calculate height
            count = confidence_levels.get(level, 0)
            percentage = (count / total * 100) if total > 0 else 0
            height = max(int(percentage / 100 * 30), 2)  # Min height of 2px
            
            # Bar
            bar = QLabel()
            bar.setFixedSize(20, height)
            bar.setStyleSheet(f"background-color: {colors[level]}; border-radius: 2px;")
            
            # Add spacer to push bar to bottom
            bar_layout.addStretch()
            bar_layout.addWidget(bar, alignment=Qt.AlignCenter)
            
            # Label
            label = QLabel(labels[level])
            label.setStyleSheet("font-size: 8px; color: #7f8c8d;")
            label.setAlignment(Qt.AlignCenter)
            bar_layout.addWidget(label)
            
            bars_layout.addWidget(bar_widget)
        
        layout.addLayout(bars_layout)
        
        return widget
        
    def load_robot_data(self, unit_id, unit_name):
        """Load data for a specific robot unit"""
        self.unit_id = unit_id
        self.unit_name = unit_name
        
        self.title_label.setText(f"Robot: {unit_name}")
        self.loading_label.show()
        
        # Load data in a separate thread to avoid blocking UI
        self.load_thread = QThread()
        self.load_worker = RobotDataLoader(unit_id)
        self.load_worker.moveToThread(self.load_thread)
        
        self.load_thread.started.connect(self.load_worker.load_data)
        self.load_worker.data_loaded.connect(self.on_data_loaded)
        self.load_worker.error_occurred.connect(self.on_load_error)
        self.load_worker.finished.connect(self.load_thread.quit)
        self.load_worker.finished.connect(self.load_worker.deleteLater)
        self.load_thread.finished.connect(self.load_thread.deleteLater)
        
        self.load_thread.start()
        
    def on_data_loaded(self, unit_data, detections_data):
        """Handle loaded robot data"""
        self.unit_data = unit_data
        self.loading_label.hide()
        
        # Extract all detections from API response
        # The API returns detections directly in the 'detections' field, not wrapped in packages
        all_detections = detections_data.get('detections', [])
        
        print(f"DEBUG: Received {len(all_detections)} detections from API")
        print(f"DEBUG: Detection data keys: {list(detections_data.keys())}")
        if all_detections:
            print(f"DEBUG: Sample detection keys: {list(all_detections[0].keys())}")
            print(f"DEBUG: Sample detection: {all_detections[0]}")
        
        # Setup streams with detection data
        self.setup_streams(detections_data.get('rtsp_uris', []), all_detections)
        
        # Setup detections
        self.setup_detections(all_detections)
        
    def on_load_error(self, error_message):
        """Handle loading error"""
        self.loading_label.setText(f"Error loading data: {error_message}")
        
    def setup_streams(self, rtsp_uris, detection_data=None):
        """Setup stream widgets with detection correlation"""
        # Clear existing streams
        while self.streams_layout.count():
            child = self.streams_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not rtsp_uris:
            no_streams_label = QLabel("No camera streams configured")
            no_streams_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
            no_streams_label.setAlignment(Qt.AlignCenter)
            self.streams_layout.addWidget(no_streams_label)
            return
        
        # Distribute detections across streams (since camera IDs are not available in detection data)
        # Production systems include camera/stream IDs in detections
        all_detections = detection_data or []
        detections_per_stream = len(all_detections) // len(rtsp_uris) if rtsp_uris else 0
        
        # Add up to 4 streams
        for i, rtsp_uri in enumerate(rtsp_uris[:4]):
            # Assign some detections to this stream (simplified approach)
            start_idx = i * detections_per_stream
            end_idx = start_idx + detections_per_stream if i < len(rtsp_uris) - 1 else len(all_detections)
            stream_detections = all_detections[start_idx:end_idx] if all_detections else []
            
            stream_widget = StreamWidget(rtsp_uri, i + 1, stream_detections)
            self.streams_layout.addWidget(stream_widget)
        
        # Add stretch if less than 4 streams
        if len(rtsp_uris) < 4:
            self.streams_layout.addStretch()
            
    def setup_detections(self, detections):
        """Setup detection widgets"""
        # Clear existing detections
        self.clear_detections()
        
        # Update statistics panel
        self.update_statistics_panel(detections)
        
        if not detections:
            no_detections_label = QLabel("No detections found")
            no_detections_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 20px;")
            no_detections_label.setAlignment(Qt.AlignCenter)
            self.detections_layout.addWidget(no_detections_label)
            return
        
        # Sort detections by timestamp (most recent first)
        detections.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Add detection widgets
        for detection in detections:
            detection_widget = DetectionItemWidget(detection)
            self.detections_layout.addWidget(detection_widget)
            self.detection_widgets.append(detection_widget)
        
        # Add stretch at the end
        self.detections_layout.addStretch()
        
    def clear_detections(self):
        """Clear all detection widgets"""
        for widget in self.detection_widgets:
            widget.deleteLater()
        self.detection_widgets.clear()
        
        while self.detections_layout.count():
            child = self.detections_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def filter_detections(self, filter_text):
        """Filter detections by action type"""
        if filter_text == "All Actions":
            # Show all detections  
            for widget in self.detection_widgets:
                widget.show()
        else:
            # Filter by action type
            filter_action = filter_text.lower().replace(' ', '_')
            
            for widget in self.detection_widgets:
                detection_action = widget.detection_data.get('action_type', '')
                if filter_action in detection_action:
                    widget.show()
                else:
                    widget.hide()
                    
    def refresh_data(self):
        """Refresh the robot data"""
        if self.unit_id and self.unit_name:
            self.load_robot_data(self.unit_id, self.unit_name)


class RobotDataLoader(QObject):
    """
    Worker class to load robot data in a separate thread
    """
    
    data_loaded = pyqtSignal(dict, dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, unit_id):
        super().__init__()
        self.unit_id = unit_id
        
    def load_data(self):
        """Load robot data from API"""
        try:
            # Get unit detections
            success, message, detections_data = api_client.get_unit_detections(self.unit_id, hours=24, limit=50)
            
            print(f"DEBUG: API call result - Success: {success}, Message: {message}")
            print(f"DEBUG: Detections data keys: {list(detections_data.keys()) if detections_data else 'None'}")
            
            if not success:
                self.error_occurred.emit(message)
                self.finished.emit()
                return
                
            # Extract unit data directly from API response
            # The API response includes unit info at the top level
            unit_data = {
                'unit_name': detections_data.get('unit_name', 'Unknown Unit'),
                'rtsp_uris': detections_data.get('rtsp_uris', [])
            }
            
            print(f"DEBUG: Unit data extracted: {unit_data}")
            
            self.data_loaded.emit(unit_data, detections_data)
            
        except Exception as e:
            print(f"DEBUG: Exception in load_data: {e}")
            self.error_occurred.emit(str(e))
            
        finally:
            self.finished.emit()