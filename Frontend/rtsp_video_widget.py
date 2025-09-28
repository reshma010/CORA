#!/usr/bin/env python3
"""
Working RTSP Video Widget using VLC for PyQt5
This replaces the placeholder StreamWidget with actual video playback.
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import vlc
import sys
import platform
from theme_manager import ThemeManager

class RTSPVideoWidget(QFrame):
    """
    A video widget that can play RTSP streams using VLC
    """
    
    def __init__(self, rtsp_uri, stream_number, parent=None):
        super().__init__(parent)
        self.rtsp_uri = rtsp_uri
        self.stream_number = stream_number
        self.instance = None
        self.player = None
        self.theme_manager = ThemeManager()
        
        self.setup_ui()
        self.setup_vlc()
        
    def setup_ui(self):
        """Setup the video widget UI"""
        self.setFixedSize(320, 240)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border: 2px solid {self.theme_manager.get_color('primary')};
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header overlay
        self.header_widget = QWidget()
        primary_color = self.theme_manager.get_color('primary')
        # Convert hex to rgba with transparency
        r, g, b = int(primary_color[1:3], 16), int(primary_color[3:5], 16), int(primary_color[5:7], 16)
        self.header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba({r}, {g}, {b}, 180);
                border-radius: 4px;
            }}
        """)
        self.header_widget.setFixedHeight(30)
        
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # Stream title
        title_label = QLabel(f"Camera {self.stream_number}")
        title_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; font-size: 12px; font-weight: bold; font-family: Trebuchet MS;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("CONNECTING")
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('secondary')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
        header_layout.addWidget(self.status_label)
        
        # Video area
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #000000;")
        
        # Control buttons (overlay)
        self.controls_widget = QWidget()
        # Use accent color with transparency
        accent_color = self.theme_manager.get_color('accent')
        r, g, b = int(accent_color[1:3], 16), int(accent_color[3:5], 16), int(accent_color[5:7], 16)
        self.controls_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba({r}, {g}, {b}, 150);
                border-radius: 4px;
            }}
        """)
        self.controls_widget.setFixedHeight(30)
        
        controls_layout = QHBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(8, 4, 8, 4)
        
        self.play_button = QPushButton("⏸️")
        self.play_button.setFixedSize(25, 22)
        text_color = self.theme_manager.get_color('text')
        r, g, b = int(text_color[1:3], 16), int(text_color[3:5], 16), int(text_color[5:7], 16)
        self.play_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color('text')};
                border: none;
                font-size: 12px;
                font-family: Trebuchet MS;
            }}
            QPushButton:hover {{
                background-color: rgba({r}, {g}, {b}, 50);
            }}
        """)
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        self.reconnect_button = QPushButton("🔄")
        self.reconnect_button.setFixedSize(25, 22)
        text_color = self.theme_manager.get_color('text')
        r, g, b = int(text_color[1:3], 16), int(text_color[3:5], 16), int(text_color[5:7], 16)
        self.reconnect_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.theme_manager.get_color('text')};
                border: none;
                font-size: 12px;
                font-family: Trebuchet MS;
            }}
            QPushButton:hover {{
                background-color: rgba({r}, {g}, {b}, 50);
            }}
        """)
        self.reconnect_button.clicked.connect(self.reconnect_stream)
        controls_layout.addWidget(self.reconnect_button)
        
        controls_layout.addStretch()
        
        # URI display
        uri_display = self.rtsp_uri
        if len(uri_display) > 25:
            uri_display = uri_display[:22] + "..."
        uri_label = QLabel(uri_display)
        uri_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; font-size: 9px; font-family: monospace;")
        controls_layout.addWidget(uri_label)
        
        # Stack layout for overlays
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked layout for overlays
        stack_widget = QWidget()
        stack_layout = QVBoxLayout(stack_widget)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        
        stack_layout.addWidget(self.header_widget)
        stack_layout.addWidget(self.video_frame, 1)  # Video takes most space
        stack_layout.addWidget(self.controls_widget)
        
        main_layout.addWidget(stack_widget)
        
    def setup_vlc(self):
        """Setup VLC player"""
        try:
            # Create VLC instance with corrected arguments
            vlc_args = [
                '--intf', 'dummy',
                '--no-xlib',
                '--network-caching=300',
                '--rtsp-timeout=10',
                '--rtsp-tcp'  # Fixed: removed =1
            ]
            
            self.instance = vlc.Instance(vlc_args)
            if not self.instance:
                raise Exception("Failed to create VLC instance")
                
            self.player = self.instance.media_player_new()
            if not self.player:
                raise Exception("Failed to create VLC media player")
            
            # Set up media with better options
            media = self.instance.media_new(self.rtsp_uri)
            media.add_option('network-caching=300')
            media.add_option('rtsp-tcp')
            media.add_option('rtsp-timeout=10')
            media.add_option('file-caching=300')
            self.player.set_media(media)
            
            # Set video output to our widget
            if platform.system() == "Darwin":  # macOS
                self.player.set_nsobject(int(self.video_frame.winId()))
            elif platform.system() == "Windows":
                self.player.set_hwnd(int(self.video_frame.winId()))
            else:  # Linux
                self.player.set_xwindow(int(self.video_frame.winId()))
            
            # Set up event manager
            events = self.player.event_manager()
            events.event_attach(vlc.EventType.MediaPlayerBuffering, self.on_buffering)
            events.event_attach(vlc.EventType.MediaPlayerPlaying, self.on_playing)
            events.event_attach(vlc.EventType.MediaPlayerEncounteredError, self.on_error)
            events.event_attach(vlc.EventType.MediaPlayerStopped, self.on_stopped)
            
            # Start playback
            self.start_playback()
            
        except Exception as e:
            print(f"VLC setup error: {e}")
            self.status_label.setText("VLC ERROR")
            self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('error', '#e74c3c')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
    
    def start_playback(self):
        """Start video playback"""
        if self.player:
            self.player.play()
            self.status_label.setText("CONNECTING")
            self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('secondary')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
    
    def toggle_playback(self):
        """Toggle play/pause"""
        if not self.player:
            return
            
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setText("▶️")
        else:
            self.player.play()
            self.play_button.setText("⏸️")
    
    def reconnect_stream(self):
        """Reconnect to stream"""
        if self.player:
            self.player.stop()
            QTimer.singleShot(1000, self.start_playback)  # Wait 1 second before reconnecting
    
    def on_buffering(self, event):
        """Handle buffering event"""
        self.status_label.setText("BUFFERING")
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('secondary')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
    
    def on_playing(self, event):
        """Handle playing event"""
        self.status_label.setText("LIVE")
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('success', '#27ae60')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
        self.play_button.setText("⏸️")
    
    def on_error(self, event):
        """Handle error event"""
        self.status_label.setText("ERROR")
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('error', '#e74c3c')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
    
    def on_stopped(self, event):
        """Handle stopped event"""
        self.status_label.setText("STOPPED")
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; font-size: 10px; font-weight: bold; font-family: Trebuchet MS;")
        self.play_button.setText("▶️")
    
    def closeEvent(self, event):
        """Clean up when widget is closed"""
        if self.player:
            self.player.stop()
            self.player.release()
        if self.instance:
            self.instance.release()
        super().closeEvent(event)


# Test application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test with your RTSP stream
    rtsp_url = "rtsp://192.168.1.248:8554/ds-test"
    
    widget = RTSPVideoWidget(rtsp_url, 1)
    widget.show()
    
    sys.exit(app.exec_())