# Reshma Shaik
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget, QMessageBox, QComboBox, QDialog, QLineEdit, QDialogButtonBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import robot components
from robot_widgets import RobotGridWidget
from robot_detail_page import RobotDetailPage

# Import icon utilities for duotone Font Awesome icons
from icon_utils import IconManager

# Import API client and resend verification dialog
from api_client import api_client
from resend_verification_dialog import ResendVerificationDialog
from theme_manager import theme_manager


class Dashboard(QWidget):
    def __init__(self):
        print("DASHBOARD: Initializing Dashboard class...")
        super().__init__()
        print("DASHBOARD: Super init completed")

        # ----------------- Main Layout -----------------
        print("DASHBOARD: Creating main layout...")
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        print("DASHBOARD: Main layout created")

        # ================== Sidebar ==================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 40, 0, 0)
        sidebar_layout.setSpacing(20)

        # Sidebar buttons with duotone icons
        self.btn_dashboard = QPushButton("Dashboard")
        IconManager.set_button_icon(self.btn_dashboard, 'dashboard', "Dashboard", size=18)
        
        self.btn_robots = QPushButton("Robot Units")
        IconManager.set_button_icon(self.btn_robots, 'robot', "Robot Units", size=18)
        
        self.sidebar_buttons = [self.btn_dashboard, self.btn_robots]

        for btn in self.sidebar_buttons:
            btn.setFixedHeight(50)
            btn.setFont(QFont("Trebuchet MS", 11))
            btn.setCheckable(True)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        
        # Settings button at the bottom with duotone icon
        self.btn_settings = QPushButton("Settings")
        IconManager.set_button_icon(self.btn_settings, 'settings', "Settings", size=18)
        self.btn_settings.setFixedHeight(50)
        self.btn_settings.setFont(QFont("Trebuchet MS", 11))
        self.btn_settings.setCheckable(True)
        sidebar_layout.addWidget(self.btn_settings)

        # ================== Content ==================
        content = QFrame()
        content.setObjectName("Content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Top bar
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        self.title_label = QLabel("Dashboard Overview")
        self.title_label.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()
        content_layout.addWidget(top_bar)

        # ----------------- Pages -----------------
        self.pages = QStackedWidget()

        # ------------------ Dashboard Page ------------------
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)
        dashboard_layout.setSpacing(30)
        dashboard_layout.setContentsMargins(40, 30, 40, 30)
        
        # Welcome header
        welcome_header = QFrame()
        welcome_header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme_manager.get_color('primary')}, stop:1 {theme_manager.get_color('secondary')});
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        welcome_layout = QVBoxLayout(welcome_header)
        
        # Welcome message - will be updated with user's first name
        self.welcome_label = QLabel("Welcome to CORA")
        self.welcome_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin: 0px;
        """)
        welcome_layout.addWidget(self.welcome_label)
        
        subtitle_label = QLabel("Campus Observation & Response Agent")
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 16px;
            margin-top: 5px;
        """)
        welcome_layout.addWidget(subtitle_label)
        
        dashboard_layout.addWidget(welcome_header)
        
        # Quick stats cards
        stats_container = QHBoxLayout()
        stats_container.setSpacing(20)
        
        # Active Units Card
        self.active_units_card = self.create_dashboard_card_with_icon("robot", "0", "Active Units", theme_manager.get_color('primary'))
        stats_container.addWidget(self.active_units_card)
        
        # Total Detections Card
        self.total_detections_card = self.create_dashboard_card_with_icon("eye", "0", "Total Detections", theme_manager.get_color('secondary'))
        stats_container.addWidget(self.total_detections_card)
        
        # Active Streams Card
        self.active_streams_card = self.create_dashboard_card_with_icon("video", "0", "Active Streams", theme_manager.get_color('accent'))
        stats_container.addWidget(self.active_streams_card)
        
        dashboard_layout.addLayout(stats_container)
        
        # Quick Actions
        actions_label = QLabel("Quick Actions")
        actions_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {theme_manager.get_color('text')}; margin-top: 20px; font-family: 'Trebuchet MS';")
        dashboard_layout.addWidget(actions_label)
        
        actions_container = QHBoxLayout()
        actions_container.setSpacing(15)
        
        view_units_btn = QPushButton("View All Units")
        view_units_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Trebuchet MS';
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('secondary')};
            }}
        """)
        view_units_btn.clicked.connect(lambda: self.switch_page(1, "Robot Units"))
        actions_container.addWidget(view_units_btn)
        
        actions_container.addStretch()
        dashboard_layout.addLayout(actions_container)
        
        dashboard_layout.addStretch()
        self.pages.addWidget(dashboard_page)

        # ------------------ Robots Page ------------------
        self.robots_page = QWidget()
        robots_layout = QVBoxLayout(self.robots_page)
        robots_layout.setSpacing(16)
        robots_layout.setContentsMargins(0, 0, 0, 0)
        
        # Robot grid widget
        self.robot_grid = RobotGridWidget()
        self.robot_grid.robot_selected.connect(self.on_robot_clicked)
        robots_layout.addWidget(self.robot_grid)
        
        self.pages.addWidget(self.robots_page)

        # ------------------ Robot Detail Page ------------------
        self.robot_detail_page = RobotDetailPage()
        self.robot_detail_page.back_requested.connect(self.on_robot_detail_back)
        self.pages.addWidget(self.robot_detail_page)

        # ------------------ Settings Page ------------------
        self.settings_page = self.create_settings_page()
        self.pages.addWidget(self.settings_page)

        content_layout.addWidget(self.pages)

        # ----------------- Connect Buttons -----------------
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, "Dashboard Overview"))
        self.btn_robots.clicked.connect(lambda: self.switch_page(1, "Robot Units"))
        self.btn_settings.clicked.connect(lambda: self.switch_page(3, "Settings"))

        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

        # Apply stylesheet
        self.setStyleSheet(self.load_styles())

        # Set default selected button
        self.select_button(self.btn_dashboard)
        
        # Load user data for welcome message
        self.load_user_data()
        
        # Load dashboard statistics
        self.load_dashboard_stats()

    def load_dashboard_stats(self):
        """Load real data for dashboard widgets"""
        try:
            # Load active units data
            success, message, active_data = api_client.get_active_units(24)
            if success and active_data:
                active_count = active_data.get('units_count', 0)
                self.update_widget_value(self.active_units_card, str(active_count))
                
                # For active streams, count the total RTSP URIs from active units
                active_units = active_data.get('units', [])
                total_streams = 0
                for unit in active_units:
                    rtsp_uris = unit.get('rtsp_uris', [])
                    if isinstance(rtsp_uris, list):
                        total_streams += len(rtsp_uris)
                self.update_widget_value(self.active_streams_card, str(total_streams))
            else:
                print(f"Failed to load active units: {message}")
                
            # Load robots data to get total detections
            success, message, robots_data = api_client.get_robots()
            if success and robots_data:
                robots_list = robots_data.get('robots', [])
                total_detections = 0
                for robot in robots_list:
                    total_detections += robot.get('total_detections', 0)
                self.update_widget_value(self.total_detections_card, str(total_detections))
            else:
                print(f"Failed to load robots data: {message}")
                
        except Exception as e:
            print(f"Error loading dashboard stats: {e}")
            # Keep default values if there's an error

    def update_widget_value(self, widget, new_value):
        """Update the value displayed in a dashboard widget"""
        try:
            # Find the value label within the widget (it's the second QLabel)
            for i in range(widget.layout().count()):
                item = widget.layout().itemAt(i)
                if item:
                    child_widget = item.widget()
                    if isinstance(child_widget, QLabel):
                        # Check if this looks like a value label (large font, centered)
                        stylesheet = child_widget.styleSheet()
                        if "font-size: 24px" in stylesheet and "font-weight: bold" in stylesheet:
                            child_widget.setText(new_value)
                            return
                    elif hasattr(item, 'layout') and item.layout():
                        # Handle nested layouts (like the icon layout)
                        continue
        except Exception as e:
            print(f"Error updating widget value: {e}")

    def load_user_data(self):
        """Load user data to personalize the dashboard"""
        try:
            success, message, user_data = api_client.get_user_profile()
            
            if success and user_data:
                # Backend returns user data with a 'user' object containing firstName and lastName fields
                user_info = user_data.get('user', {}) if 'user' in user_data else user_data
                
                # Use firstName field directly
                first_name = user_info.get('firstName')
                if first_name:
                    self.set_user_welcome(first_name)
                    
        except Exception as e:
            print(f"Error loading user data: {e}")
            # Keep default welcome message if there's an error

    # ----------------- Page Switching -----------------
    def switch_page(self, index, title):
        self.pages.setCurrentIndex(index)
        self.title_label.setText(title)
        if index < len(self.sidebar_buttons):
            self.select_button(self.sidebar_buttons[index])
        else:
            self.select_button(self.btn_settings)
            
        # Special handling for different pages
        if index == 0 and title == "Dashboard Overview":
            # Refresh dashboard stats when returning to dashboard
            self.load_dashboard_stats()
        elif index == 1 and title == "Robot Units":
            self.robot_grid.load_robots()

    def reset_to_dashboard(self):
        """Reset to the main dashboard welcome page"""
        self.switch_page(0, "Dashboard Overview")
        # Refresh user data for personalized welcome
        self.load_user_data()
        # Refresh dashboard stats
        self.load_dashboard_stats()

    # Highlight the selected sidebar button
    def select_button(self, button):
        for btn in self.sidebar_buttons:
            btn.setChecked(False)
        self.btn_settings.setChecked(False)
        button.setChecked(True)

    # ----------------- Robot Navigation -----------------
    def on_robot_clicked(self, unit_id, unit_name):
        """Handle robot widget click to show detail page"""
        print(f"Opening robot detail page for {unit_name} (ID: {unit_id})")
        self.robot_detail_page.load_robot_data(unit_id, unit_name)
        self.pages.setCurrentIndex(2)  # Robot detail page index
        self.title_label.setText(f"Robot: {unit_name}")
        
        # Deselect all sidebar buttons since on a detail page
        for btn in self.sidebar_buttons:
            btn.setChecked(False)
        self.btn_settings.setChecked(False)
        
    def on_robot_detail_back(self):
        """Handle back button from robot detail page"""
        print("Returning to robot units page")
        self.switch_page(1, "Robot Units")
        # Refresh robot grid data
        self.robot_grid.refresh_robots()

    def set_user_welcome(self, first_name):
        """Update the welcome message with the user's first name"""
        if first_name:
            self.welcome_label.setText(f"Welcome to CORA, {first_name}")
        else:
            self.welcome_label.setText("Welcome to CORA")

    # ----------------- Settings Page -----------------
    def create_settings_page(self):
        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {theme_manager.get_color('background')};
            }}
            QScrollBar:vertical {{
                background-color: {theme_manager.get_color('background')};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme_manager.get_color('highlight')};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme_manager.get_color('primary')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        
        # Create the actual settings content widget
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(40, 30, 40, 30)
        settings_layout.setSpacing(25)

        # Account Section
        account_section = QFrame()
        account_section.setStyleSheet(f"background-color: {theme_manager.get_color('background_light') if theme_manager.current_theme == 'dark' else theme_manager.get_color('background')}; border-radius: 15px; border: 1px solid {theme_manager.get_color('accent_light')};")
        account_layout = QVBoxLayout(account_section)
        account_layout.setContentsMargins(30, 25, 30, 25)
        account_layout.setSpacing(18)
        
        account_title = QLabel("Account Settings")
        account_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        account_title.setStyleSheet(f"color: {theme_manager.get_color('primary')}; margin-bottom: 8px; border: none; outline: none;")
        account_layout.addWidget(account_title)
        
        # Logout button with icon
        self.logout_btn = QPushButton("Logout")
        IconManager.set_button_icon(self.logout_btn, 'sign_out', "Logout", size=16)
        self.logout_btn.setFixedWidth(140)
        self.logout_btn.setFixedHeight(38)
        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('secondary')};
                color: {theme_manager.get_color('background')};
                border-radius: 19px;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 18px;
                border: none;
                font-family: 'Trebuchet MS';
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
            }}
        """)
        self.logout_btn.clicked.connect(self.logout_user)
        account_layout.addWidget(self.logout_btn, 0, Qt.AlignLeft)
        
        settings_layout.addWidget(account_section)

        # Application Settings Section
        app_section = QFrame()
        app_section.setStyleSheet(f"background-color: {theme_manager.get_color('background')}; border-radius: 15px; border: 1px solid {theme_manager.get_color('highlight')};")
        app_layout = QVBoxLayout(app_section)
        app_layout.setContentsMargins(30, 25, 30, 25)
        app_layout.setSpacing(22)
        
        app_title = QLabel("Application Settings")
        app_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        app_title.setStyleSheet(f"color: {theme_manager.get_color('text')}; margin-bottom: 8px; border: none; outline: none;")
        app_layout.addWidget(app_title)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(15)
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Trebuchet MS", 13))
        theme_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; border: none; outline: none;")
        theme_label.setFixedHeight(36)  # Match button height
        
        self.theme_btn = QPushButton("Light Mode")
        self.theme_btn.setFixedWidth(110)
        self.theme_btn.setFixedHeight(36)
        self.theme_btn.setCheckable(True)
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                border: none;
                font-family: 'Trebuchet MS';
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
            QPushButton:checked {{
                background-color: {theme_manager.get_color('highlight')};
                color: {theme_manager.get_color('text')};
            }}
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label, 0, Qt.AlignVCenter)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn, 0, Qt.AlignVCenter)
        app_layout.addLayout(theme_layout)
        
        # Notifications settings
        notifications_layout = QHBoxLayout()
        notifications_layout.setSpacing(15)
        notifications_label = QLabel("Notifications:")
        notifications_label.setFont(QFont("Trebuchet MS", 13))
        notifications_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; border: none; outline: none;")
        notifications_label.setFixedHeight(36)  # Match button height
        
        self.notifications_btn = QPushButton("Enabled")
        self.notifications_btn.setFixedWidth(110)
        self.notifications_btn.setFixedHeight(36)
        self.notifications_btn.setCheckable(True)
        self.notifications_btn.setChecked(True)
        self.notifications_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                border: none;
                font-family: 'Trebuchet MS';
                padding: 8px 14px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
            QPushButton:checked {{
                background-color: {theme_manager.get_color('highlight')};
                color: {theme_manager.get_color('text')};
            }}
        """)
        self.notifications_btn.clicked.connect(self.toggle_notifications)
        
        notifications_layout.addWidget(notifications_label, 0, Qt.AlignVCenter)
        notifications_layout.addStretch()
        notifications_layout.addWidget(self.notifications_btn, 0, Qt.AlignVCenter)
        app_layout.addLayout(notifications_layout)
        
        # Auto-refresh settings
        refresh_layout = QHBoxLayout()
        refresh_layout.setSpacing(15)
        refresh_label = QLabel("Auto-refresh:")
        refresh_label.setFont(QFont("Trebuchet MS", 13))
        refresh_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; border: none; outline: none;")
        refresh_label.setFixedHeight(36)  # Match combo height
        
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(["10 seconds", "30 seconds", "1 minute", "5 minutes", "Disabled"])
        self.refresh_combo.setCurrentText("30 seconds")
        self.refresh_combo.setFixedWidth(130)
        self.refresh_combo.setFixedHeight(36)
        self.refresh_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 14px;
                border: none;
                font-family: 'Trebuchet MS';
            }}
            QComboBox:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme_manager.get_color('background')};
                color: #333333;
                border: 1px solid {theme_manager.get_color('highlight')};
                border-radius: 8px;
                selection-background-color: {theme_manager.get_color('primary')};
                selection-color: {theme_manager.get_color('background')};
                font-family: 'Trebuchet MS';
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                color: #333333;
                background-color: transparent;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('background')};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
            }}
        """)
        self.refresh_combo.currentTextChanged.connect(self.change_refresh_rate)
        
        refresh_layout.addWidget(refresh_label, 0, Qt.AlignVCenter)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_combo, 0, Qt.AlignVCenter)
        app_layout.addLayout(refresh_layout)
        
        settings_layout.addWidget(app_section)

        # Security Settings Section
        security_section = QFrame()
        security_section.setStyleSheet(f"background-color: {theme_manager.get_color('background')}; border-radius: 15px; border: 1px solid {theme_manager.get_color('highlight')};")
        security_layout = QVBoxLayout(security_section)
        security_layout.setContentsMargins(30, 25, 30, 25)
        security_layout.setSpacing(18)
        
        security_title = QLabel("Security Settings")
        security_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        security_title.setStyleSheet(f"color: {theme_manager.get_color('text')}; margin-bottom: 8px; border: none; outline: none;")
        security_layout.addWidget(security_title)
        
        # Change password button
        self.change_pwd_btn = QPushButton("Change Password")
        IconManager.set_button_icon(self.change_pwd_btn, 'key', "Change Password", size=16)
        self.change_pwd_btn.setFixedWidth(160)
        self.change_pwd_btn.setFixedHeight(38)
        self.change_pwd_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 19px;
                font-size: 14px;
                font-weight: 500;
                padding: 10px 18px;
                border: none;
                font-family: 'Trebuchet MS';
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
        """)
        self.change_pwd_btn.clicked.connect(self.change_password)
        security_layout.addWidget(self.change_pwd_btn, 0, Qt.AlignLeft)
        
        # Session timeout
        session_layout = QHBoxLayout()
        session_layout.setSpacing(15)
        session_label = QLabel("Session Timeout:")
        session_label.setFont(QFont("Trebuchet MS", 13))
        session_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; border: none; outline: none;")
        session_label.setFixedHeight(36)  # Match combo height
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["30 minutes", "1 hour", "2 hours", "4 hours", "8 hours", "Never"])
        self.session_combo.setCurrentText("2 hours")
        self.session_combo.setFixedWidth(130)
        self.session_combo.setFixedHeight(36)
        self.session_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                padding: 8px 14px;
                border: none;
                font-family: 'Trebuchet MS';
            }}
            QComboBox:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme_manager.get_color('background')};
                color: #333333;
                border: 1px solid {theme_manager.get_color('highlight')};
                border-radius: 8px;
                selection-background-color: {theme_manager.get_color('primary')};
                selection-color: {theme_manager.get_color('background')};
                font-family: 'Trebuchet MS';
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                color: #333333;
                background-color: transparent;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('background')};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
            }}
        """)
        self.session_combo.currentTextChanged.connect(self.change_session_timeout)
        
        session_layout.addWidget(session_label, 0, Qt.AlignVCenter)
        session_layout.addStretch()
        session_layout.addWidget(self.session_combo, 0, Qt.AlignVCenter)
        security_layout.addLayout(session_layout)
        
        settings_layout.addWidget(security_section)
        
        # About Section
        about_section = QFrame()
        about_section.setStyleSheet(f"background-color: {theme_manager.get_color('background')}; border-radius: 15px; border: 1px solid {theme_manager.get_color('highlight')};")
        about_layout = QVBoxLayout(about_section)
        about_layout.setContentsMargins(30, 25, 30, 25)
        about_layout.setSpacing(15)
        
        about_title = QLabel("About CORA")
        about_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        about_title.setStyleSheet(f"color: {theme_manager.get_color('text')}; margin-bottom: 8px; border: none; outline: none;")
        about_layout.addWidget(about_title)
        
        # Version info
        version_label = QLabel("Version: 1.0.0")
        version_label.setFont(QFont("Trebuchet MS", 12))
        version_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; padding: 3px 0px; border: none; outline: none;")
        about_layout.addWidget(version_label)
        
        # Organization info
        org_label = QLabel("Organization: Wayne State University")
        org_label.setFont(QFont("Trebuchet MS", 12))
        org_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; padding: 3px 0px; border: none; outline: none;")
        about_layout.addWidget(org_label)
        
        # Backend API connection status
        api_status_label = QLabel("Backend API: Connected")
        api_status_label.setFont(QFont("Trebuchet MS", 12))
        api_status_label.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-weight: 500; padding: 3px 0px; border: none; outline: none;")
        about_layout.addWidget(api_status_label)

        # Email verification status
        self.email_status_label = QLabel("Email: Checking...")
        self.email_status_label.setFont(QFont("Trebuchet MS", 12))
        self.email_status_label.setStyleSheet(f"color: {theme_manager.get_color('highlight')}; font-weight: 500; padding: 3px 0px; border: none; outline: none;")
        about_layout.addWidget(self.email_status_label)

        # Resend verification button (initially hidden) - more subtle
        self.resend_email_button = QPushButton("Resend verification email")
        self.resend_email_button.setFixedWidth(200)
        self.resend_email_button.setFixedHeight(35)
        self.resend_email_button.clicked.connect(self.show_resend_verification_dialog)
        self.resend_email_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme_manager.get_color('accent')};
                font-size: 12px;
                font-weight: normal;
                padding: 8px 15px;
                border: 1px solid {theme_manager.get_color('accent')};
                border-radius: 17px;
                text-decoration: underline;
                font-family: 'Trebuchet MS';
                margin-top: 5px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
                text-decoration: none;
            }}
        """)
        self.resend_email_button.hide()  # Hide initially
        about_layout.addWidget(self.resend_email_button)

        # Check email verification status when dashboard loads
        self.check_email_verification_status()
        
        # Last updated info
        import datetime
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_label = QLabel(f"Last Updated: {last_updated}")
        updated_label.setFont(QFont("Trebuchet MS", 11))
        updated_label.setStyleSheet(f"color: {theme_manager.get_color('highlight')}; padding: 5px 0px; border: none; outline: none;")
        about_layout.addWidget(updated_label)
        
        # System info button
        self.system_info_btn = QPushButton("System Information")
        IconManager.set_button_icon(self.system_info_btn, 'info', "System Information", size=16)
        self.system_info_btn.setFixedWidth(160)
        self.system_info_btn.setFixedHeight(36)
        self.system_info_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme_manager.get_color('highlight')};
                color: {theme_manager.get_color('text')};
                border-radius: 18px;
                font-size: 13px;
                font-weight: 500;
                border: none;
                font-family: 'Trebuchet MS';
                padding: 8px 14px;
                margin-top: 8px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
            }}
        """)
        self.system_info_btn.clicked.connect(self.show_system_info)
        about_layout.addWidget(self.system_info_btn, 0, Qt.AlignLeft)
        
        settings_layout.addWidget(about_section)
        
        settings_layout.addStretch()
        
        # Set the settings page as the scroll area's widget
        scroll_area.setWidget(settings_page)
        return scroll_area

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        theme_manager.toggle_theme()
        
        if theme_manager.current_theme == "dark":
            self.theme_btn.setText("Dark Mode")
            self.theme_btn.setChecked(True)
            QMessageBox.information(self, "Theme", "Dark mode enabled!")
        else:
            self.theme_btn.setText("Light Mode") 
            self.theme_btn.setChecked(False)
            QMessageBox.information(self, "Theme", "Light mode enabled!")
        
        # Refresh all styling
        self.setStyleSheet(self.load_styles())
        # Update child components that might need theme updates
        self.refresh_theme()
        
    def refresh_theme(self):
        """Refresh theme for all components"""
        try:
            # Update robot grid if it exists
            if hasattr(self, 'robot_grid') and self.robot_grid:
                self.robot_grid.update()
            
            # Update robot detail page if it exists  
            if hasattr(self, 'robot_detail_page') and self.robot_detail_page:
                self.robot_detail_page.update()
                
            # Force update of the entire widget
            self.update()
        except Exception as e:
            print(f"Error refreshing theme: {e}")
    
    def toggle_notifications(self):
        """Toggle notification settings"""
        if self.notifications_btn.isChecked():
            self.notifications_btn.setText("Disabled")
            QMessageBox.information(self, "Notifications", "Notifications have been disabled.")
        else:
            self.notifications_btn.setText("Enabled")
            self.notifications_btn.setChecked(True)
            QMessageBox.information(self, "Notifications", "Notifications have been enabled.")
    
    def change_refresh_rate(self, rate):
        """Handle auto-refresh rate change"""
        QMessageBox.information(self, "Auto-refresh", f"Auto-refresh rate changed to: {rate}")
        
        
    def change_session_timeout(self, timeout):
        """Handle session timeout change"""
        QMessageBox.information(self, "Session Timeout", f"Session timeout changed to: {timeout}")
        
        
    def show_system_info(self):
        """Show system information dialog"""
        import platform
        import sys
        
        system_info = f"""
System Information:

Operating System: {platform.system()} {platform.release()}
Python Version: {sys.version.split()[0]}
Architecture: {platform.machine()}
Processor: {platform.processor()}

CORA Application:
Version: 1.0.0
Backend API: Node.js + MongoDB (Connected)
UI Framework: PyQt5
Icons: Font Awesome 5 Solid
        """
        
        QMessageBox.information(self, "System Information", system_info.strip())
        
    def change_password(self):
        """Open change password dialog"""
        dialog = ChangePasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Success", "Password changed successfully!")

    def logout_user(self):
        """Handle user logout and return to login page"""
        reply = QMessageBox.question(self, "Logout", "Confirm logout?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Find the parent stacked widget and go back to login
            parent = self.parent()
            while parent and not hasattr(parent, 'setCurrentIndex'):
                parent = parent.parent()
            if parent:
                parent.setCurrentIndex(0)  # Go back to login page

    # ----------------- Stylesheet -----------------
    def load_styles(self):
        return f"""
        QFrame#Sidebar {{ background-color: {theme_manager.get_color('primary')}; }}
        QPushButton {{
            background-color: {theme_manager.get_color('primary')};
            color: {theme_manager.get_color('background')};
            border-radius: 20px;
            padding: 12px 20px;
            font-weight: 500;
            max-width: 180px;
            font-family: 'Trebuchet MS';
        }}
        QPushButton:hover {{ 
            background-color: {theme_manager.get_color('secondary')}; 
            color: {theme_manager.get_color('text')}; 
        }}
        QPushButton:checked {{ 
            background-color: {theme_manager.get_color('accent')}; 
            color: {theme_manager.get_color('text')}; 
        }}
        QFrame#Card {{ color: {theme_manager.get_color('text')}; }}
        QFrame#Content, QFrame#TopBar {{ background-color: {theme_manager.get_color('background')}; }}
        QLabel {{ 
            color: {theme_manager.get_color('text')}; 
            font-family: 'Trebuchet MS';
        }}
        QWidget {{
            background-color: {theme_manager.get_color('background')};
            color: {theme_manager.get_color('text')};
        }}
        """

    def create_status_card(self, title, value, icon, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: {color}; color: {theme_manager.get_color('background')}; border-radius: 10px; padding: 10px;")
        layout = QVBoxLayout(card)

        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {theme_manager.get_color('background')}; font-family: 'Trebuchet MS';")

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 20px; color: {theme_manager.get_color('background')}; font-family: 'Trebuchet MS';")
        value_label.setObjectName(title)  # store name for updates

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card

    def create_dashboard_card(self, icon, value, title, color):
        """Create a modern dashboard stat card with emoji icon"""
        card = QFrame()
        card.setFixedSize(200, 140)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            color: {theme_manager.get_color('background')};
            font-size: 32px;
            font-weight: bold;
            font-family: 'Trebuchet MS';
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {theme_manager.get_color('background')};
            font-size: 24px;
            font-weight: bold;
            font-family: 'Trebuchet MS';
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {theme_manager.get_color('background')};
            font-size: 12px;
            font-weight: 500;
            font-family: 'Trebuchet MS';
            opacity: 0.9;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        return card

    def create_dashboard_card_with_icon(self, icon_name, value, title, color):
        """Create a modern dashboard stat card with Font Awesome icon"""
        card = QFrame()
        card.setFixedSize(220, 160)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon using IconManager
        icon_button = QPushButton()
        icon_button.setFixedSize(48, 48)
        icon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {theme_manager.get_color('background')};
            }}
        """)
        IconManager.set_button_icon(icon_button, icon_name, title, size=32, color=theme_manager.get_color('background'))
        icon_button.setEnabled(False)  # Make it non-clickable
        
        # Center the icon
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(icon_button)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {theme_manager.get_color('background')};
            font-size: 24px;
            font-weight: bold;
            font-family: 'Trebuchet MS';
        """)
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {theme_manager.get_color('background')};
            font-size: 14px;
            font-weight: 500;
            font-family: 'Trebuchet MS';
            opacity: 0.9;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        return card

    def check_email_verification_status(self):
        """Check if the current user's email is verified"""
        try:
            success, message, data = api_client.get_user_profile()
            if success:
                user_info = data.get('user', {})
                is_verified = user_info.get('isEmailVerified', False)
                
                if is_verified:
                    self.email_status_label.setText("Email: Verified")
                    self.email_status_label.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-weight: 500; border: none; outline: none;")
                    self.resend_email_button.hide()
                else:
                    self.email_status_label.setText("Email: Not Verified")
                    self.email_status_label.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-weight: 500; border: none; outline: none;")
                    self.resend_email_button.show()
            else:
                self.email_status_label.setText("Email: Status Unknown")
                self.email_status_label.setStyleSheet(f"color: {theme_manager.get_color('highlight')}; font-weight: 500; border: none; outline: none;")
        except Exception as e:
            print(f"Error checking email verification: {e}")
            self.email_status_label.setText("Email: Status Unknown")
            self.email_status_label.setStyleSheet(f"color: {theme_manager.get_color('highlight')}; font-weight: 500; border: none; outline: none;")

    def show_resend_verification_dialog(self):
        """Show the resend verification email dialog"""
        dialog = ResendVerificationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh email status after successful resend
            self.check_email_verification_status()


# ----------------- Change Password Dialog -----------------
class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setFixedSize(550, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme_manager.get_color('background')};
            }}
            QLabel {{
                color: {theme_manager.get_color('text')};
                font-size: 14px;
                margin: 8px 0;
                background-color: transparent;
                font-family: 'Trebuchet MS';
            }}
            QLineEdit {{
                border: 2px solid {theme_manager.get_color('highlight')};
                border-radius: 15px;
                padding: 12px 18px;
                font-size: 14px;
                background-color: {theme_manager.get_color('background')};
                color: {theme_manager.get_color('text')};
                margin: 8px 0;
                font-family: 'Trebuchet MS';
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme_manager.get_color('primary')};
            }}
            QPushButton {{
                background-color: {theme_manager.get_color('primary')};
                color: {theme_manager.get_color('background')};
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                margin: 10px 8px;
                font-family: 'Trebuchet MS';
                min-height: 15px;
            }}
            QPushButton:hover {{
                background-color: {theme_manager.get_color('accent')};
                color: {theme_manager.get_color('text')};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(45, 35, 45, 35)
        
        # Title
        title = QLabel("Change Password")
        title.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        title.setStyleSheet(f"color: {theme_manager.get_color('text')}; margin-bottom: 20px; padding: 10px 0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Current password
        current_label = QLabel("Current Password:")
        current_label.setFont(QFont("Trebuchet MS", 14, QFont.Weight.Medium))
        layout.addWidget(current_label)
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setPlaceholderText("Enter current password")
        layout.addWidget(self.current_password)
        
        # New password
        new_label = QLabel("New Password:")
        new_label.setFont(QFont("Trebuchet MS", 14, QFont.Weight.Medium))
        layout.addWidget(new_label)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter new password")
        self.new_password.textChanged.connect(self.update_password_validation)
        layout.addWidget(self.new_password)
        
        # Confirm new password
        confirm_label = QLabel("Confirm New Password:")
        confirm_label.setFont(QFont("Trebuchet MS", 14, QFont.Weight.Medium))
        layout.addWidget(confirm_label)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm new password")
        self.confirm_password.textChanged.connect(self.update_password_validation)
        layout.addWidget(self.confirm_password)
        
        # Password requirements with color coding
        requirements_label = QLabel("Password Requirements:")
        requirements_label.setFont(QFont("Trebuchet MS", 14, QFont.Bold))
        requirements_label.setStyleSheet(f"color: {theme_manager.get_color('text')}; margin-top: 20px; margin-bottom: 10px; padding: 5px 0;")
        layout.addWidget(requirements_label)
        
        self.req_length = QLabel("• 10-20 characters long")
        self.req_length.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        layout.addWidget(self.req_length)
        
        self.req_special = QLabel("• At least one special character")
        self.req_special.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        layout.addWidget(self.req_special)
        
        self.req_capital = QLabel("• At least one capital letter")
        self.req_capital.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        layout.addWidget(self.req_capital)
        
        self.req_number = QLabel("• At least one number")
        self.req_number.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        layout.addWidget(self.req_number)
        
        self.req_match = QLabel("• Passwords must match")
        self.req_match.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        layout.addWidget(self.req_match)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_password_validation(self):
        """Update password requirement colors based on current input"""
        import re
        
        password = self.new_password.text()
        confirm_password = self.confirm_password.text()
        
        # Check length requirement (10-20 characters)
        if len(password) >= 10 and len(password) <= 20:
            self.req_length.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        else:
            self.req_length.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        
        # Check special character requirement
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.req_special.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        else:
            self.req_special.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        
        # Check capital letter requirement
        if re.search(r'[A-Z]', password):
            self.req_capital.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        else:
            self.req_capital.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        
        # Check number requirement
        if re.search(r'[0-9]', password):
            self.req_number.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        else:
            self.req_number.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        
        # Check password match requirement
        if password and confirm_password and password == confirm_password:
            self.req_match.setStyleSheet(f"color: {theme_manager.get_color('primary')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
        else:
            self.req_match.setStyleSheet(f"color: {theme_manager.get_color('accent')}; font-size: 13px; background-color: transparent; font-family: 'Trebuchet MS'; padding: 3px 0;")
    
    def validate_and_accept(self):
        """Validate password inputs before accepting"""
        import re
        
        current = self.current_password.text()
        new = self.new_password.text()
        confirm = self.confirm_password.text()
        
        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
            
        if new != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return
            
        # Apply same validation as signup
        if len(new) < 10:
            QMessageBox.warning(self, "Error", "Password must be at least 10 characters long.")
            return
            
        if len(new) > 20:
            QMessageBox.warning(self, "Error", "Password cannot be more than 20 characters long.")
            return
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new):
            QMessageBox.warning(self, "Error", "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>).")
            return
            
        if not re.search(r'[A-Z]', new):
            QMessageBox.warning(self, "Error", "Password must contain at least one capital letter.")
            return
            
        if not re.search(r'[0-9]', new):
            QMessageBox.warning(self, "Error", "Password must contain at least one number.")
            return
            
        
        self.accept()


# ----------------- Run Test -----------------
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.resize(1000, 600)
    dashboard.show()
    sys.exit(app.exec_())
