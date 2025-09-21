# Reshma Shaik
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget, QMessageBox, QComboBox, QDialog, QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import Activity Logs page
from activity_page import ActivityPage

# Import robot components
from robot_widgets import RobotGridWidget
from robot_detail_page import RobotDetailPage

# Import icon utilities for duotone Font Awesome icons
from icon_utils import IconManager

# Import API client and resend verification dialog
from api_client import api_client
from resend_verification_dialog import ResendVerificationDialog


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
        
        self.btn_logs = QPushButton("Logs & Reports")
        IconManager.set_button_icon(self.btn_logs, 'file', "Logs & Reports", size=18)
        
        self.btn_camera = QPushButton("Live Camera")
        IconManager.set_button_icon(self.btn_camera, 'camera', "Live Camera", size=18)
        
        self.sidebar_buttons = [self.btn_dashboard, self.btn_robots, self.btn_logs, self.btn_camera]

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
        dash_layout = QVBoxLayout(dashboard_page)
        dash_layout.setSpacing(20)

        # Top summary cards
        summary_cards = QFrame()
        summary_layout = QHBoxLayout(summary_cards)
        summary_layout.setSpacing(15)

        # Define card data with duotone icon names
        card_data = [
            ("Model Status", "Loading...", "server", "#0c554a"),
            ("CPU/GPU Usage", "0%", "cpu", "#edbc2c"),
            ("Errors", "0", "warning", "#b2a48f")
        ]
        
        for title, value, icon_name, color in card_data:
            card = QFrame()
            card.setObjectName("Card")
            card.setFixedSize(180, 120)
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)

            # Use duotone icon with fallback
            lbl_icon = QLabel()
            IconManager.set_label_icon(lbl_icon, icon_name, "")
            lbl_icon.setFont(QFont("Trebuchet MS", 24))
            lbl_icon.setAlignment(Qt.AlignCenter)

            lbl_value = QLabel(value)
            lbl_value.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
            lbl_value.setAlignment(Qt.AlignCenter)

            lbl_title = QLabel(title)
            lbl_title.setFont(QFont("Trebuchet MS", 10))
            lbl_title.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(lbl_icon)
            card_layout.addWidget(lbl_value)
            card_layout.addWidget(lbl_title)
            card.setStyleSheet(f"background-color: {color}; color: #f3f7f6; border-radius: 15px;")
            summary_layout.addWidget(card)

        dash_layout.addWidget(summary_cards)
        dash_layout.addStretch()
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

        # ------------------ Logs Page (ActivityPage integrated) ------------------
        logs_page = ActivityPage()  
        self.pages.addWidget(logs_page)

        # ------------------ Camera Page ------------------
        camera_page = QWidget()
        camera_layout = QVBoxLayout(camera_page)
        camera_label = QLabel()
        IconManager.set_label_icon(camera_label, 'camera', "Live Camera Feed Page")
        camera_label.setFont(QFont("Trebuchet MS", 14))
        camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(camera_label)
        camera_layout.addStretch()
        self.pages.addWidget(camera_page)

        # ------------------ Settings Page ------------------
        self.settings_page = self.create_settings_page()
        self.pages.addWidget(self.settings_page)

        content_layout.addWidget(self.pages)

        # ----------------- Connect Buttons -----------------
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, "Dashboard Overview"))
        self.btn_robots.clicked.connect(lambda: self.switch_page(1, "Robot Units"))
        self.btn_logs.clicked.connect(lambda: self.switch_page(3, "Logs & Reports"))
        self.btn_camera.clicked.connect(lambda: self.switch_page(4, "Live Camera"))
        self.btn_settings.clicked.connect(lambda: self.switch_page(5, "Settings"))

        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

        # Apply stylesheet
        self.setStyleSheet(self.load_styles())

        # Set default selected button
        self.select_button(self.btn_dashboard)

    # ----------------- Page Switching -----------------
    def switch_page(self, index, title):
        self.pages.setCurrentIndex(index)
        self.title_label.setText(title)
        if index < len(self.sidebar_buttons):
            self.select_button(self.sidebar_buttons[index])
        else:
            self.select_button(self.btn_settings)
            
        # Special handling for robots page
        if index == 1 and title == "Robot Units":
            self.robot_grid.load_robots()

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

    # ----------------- Settings Page -----------------
    def create_settings_page(self):
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_layout.setContentsMargins(40, 40, 40, 40)
        settings_layout.setSpacing(30)

        # Account Section
        account_section = QFrame()
        account_section.setStyleSheet("background-color: #f3f7f6; border-radius: 15px; border: 1px solid #b2a48f;")
        account_layout = QVBoxLayout(account_section)
        account_layout.setContentsMargins(30, 25, 30, 25)
        account_layout.setSpacing(20)
        
        account_title = QLabel("Account Settings")
        account_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        account_title.setStyleSheet("color: #0c554a;")
        account_layout.addWidget(account_title)
        
        # Logout button with icon
        self.logout_btn = QPushButton("Logout")
        IconManager.set_button_icon(self.logout_btn, 'sign_out', "Logout", size=16)
        self.logout_btn.setFixedWidth(150)
        self.logout_btn.setFixedHeight(40)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.logout_btn.clicked.connect(self.logout_user)
        account_layout.addWidget(self.logout_btn, 0, Qt.AlignLeft)
        
        settings_layout.addWidget(account_section)

        # Application Settings Section
        app_section = QFrame()
        app_section.setStyleSheet("background-color: #f3f7f6; border-radius: 15px; border: 1px solid #b2a48f;")
        app_layout = QVBoxLayout(app_section)
        app_layout.setContentsMargins(30, 25, 30, 25)
        app_layout.setSpacing(15)
        
        app_title = QLabel("Application Settings")
        app_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        app_title.setStyleSheet("color: #0c554a;")
        app_layout.addWidget(app_title)
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(15)
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Trebuchet MS", 12))
        theme_label.setStyleSheet("color: #0f1614;")
        
        self.theme_btn = QPushButton("Light Mode")
        self.theme_btn.setFixedWidth(100)
        self.theme_btn.setFixedHeight(35)
        self.theme_btn.setCheckable(True)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QPushButton:checked {
                background-color: #b2a48f;
                color: #0f1614;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_btn)
        app_layout.addLayout(theme_layout)
        
        # Notifications settings
        notifications_layout = QHBoxLayout()
        notifications_layout.setSpacing(15)
        notifications_label = QLabel("Notifications:")
        notifications_label.setFont(QFont("Trebuchet MS", 12))
        notifications_label.setStyleSheet("color: #0f1614;")
        
        self.notifications_btn = QPushButton("Enabled")
        self.notifications_btn.setFixedWidth(100)
        self.notifications_btn.setFixedHeight(35)
        self.notifications_btn.setCheckable(True)
        self.notifications_btn.setChecked(True)
        self.notifications_btn.setStyleSheet("""
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QPushButton:checked {
                background-color: #b2a48f;
                color: #0f1614;
            }
        """)
        self.notifications_btn.clicked.connect(self.toggle_notifications)
        
        notifications_layout.addWidget(notifications_label)
        notifications_layout.addStretch()
        notifications_layout.addWidget(self.notifications_btn)
        app_layout.addLayout(notifications_layout)
        
        # Auto-refresh settings
        refresh_layout = QHBoxLayout()
        refresh_layout.setSpacing(15)
        refresh_label = QLabel("Auto-refresh:")
        refresh_label.setFont(QFont("Trebuchet MS", 12))
        refresh_label.setStyleSheet("color: #0f1614;")
        
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(["10 seconds", "30 seconds", "1 minute", "5 minutes", "Disabled"])
        self.refresh_combo.setCurrentText("30 seconds")
        self.refresh_combo.setFixedWidth(100)
        self.refresh_combo.setFixedHeight(35)
        self.refresh_combo.setStyleSheet("""
            QComboBox {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 500;
                padding-left: 10px;
                border: none;
            }
            QComboBox:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.refresh_combo.currentTextChanged.connect(self.change_refresh_rate)
        
        refresh_layout.addWidget(refresh_label)
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_combo)
        app_layout.addLayout(refresh_layout)
        
        settings_layout.addWidget(app_section)

        # Security Settings Section
        security_section = QFrame()
        security_section.setStyleSheet("background-color: #f3f7f6; border-radius: 15px; border: 1px solid #b2a48f;")
        security_layout = QVBoxLayout(security_section)
        security_layout.setContentsMargins(30, 25, 30, 25)
        security_layout.setSpacing(20)
        
        security_title = QLabel("Security Settings")
        security_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        security_title.setStyleSheet("color: #0c554a;")
        security_layout.addWidget(security_title)
        
        # Change password button
        self.change_pwd_btn = QPushButton("Change Password")
        IconManager.set_button_icon(self.change_pwd_btn, 'key', "Change Password", size=16)
        self.change_pwd_btn.setFixedWidth(150)
        self.change_pwd_btn.setFixedHeight(40)
        self.change_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
        """)
        self.change_pwd_btn.clicked.connect(self.change_password)
        security_layout.addWidget(self.change_pwd_btn, 0, Qt.AlignLeft)
        
        # Session timeout
        session_layout = QHBoxLayout()
        session_layout.setSpacing(15)
        session_label = QLabel("Session Timeout:")
        session_label.setFont(QFont("Trebuchet MS", 12))
        session_label.setStyleSheet("color: #0f1614;")
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["30 minutes", "1 hour", "2 hours", "4 hours", "8 hours", "Never"])
        self.session_combo.setCurrentText("2 hours")
        self.session_combo.setFixedWidth(100)
        self.session_combo.setFixedHeight(35)
        self.session_combo.setStyleSheet("""
            QComboBox {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 500;
                padding-left: 10px;
                border: none;
            }
            QComboBox:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.session_combo.currentTextChanged.connect(self.change_session_timeout)
        
        session_layout.addWidget(session_label)
        session_layout.addStretch()
        session_layout.addWidget(self.session_combo)
        security_layout.addLayout(session_layout)
        
        settings_layout.addWidget(security_section)
        
        # About Section
        about_section = QFrame()
        about_section.setStyleSheet("background-color: #f3f7f6; border-radius: 15px; border: 1px solid #b2a48f;")
        about_layout = QVBoxLayout(about_section)
        about_layout.setContentsMargins(30, 25, 30, 25)
        about_layout.setSpacing(15)
        
        about_title = QLabel("About CORA")
        about_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        about_title.setStyleSheet("color: #0c554a;")
        about_layout.addWidget(about_title)
        
        # Version info
        version_label = QLabel("Version: 1.0.0")
        version_label.setFont(QFont("Trebuchet MS", 12))
        version_label.setStyleSheet("color: #0f1614;")
        about_layout.addWidget(version_label)
        
        # Organization info
        org_label = QLabel("Organization: Wayne State University")
        org_label.setFont(QFont("Trebuchet MS", 12))
        org_label.setStyleSheet("color: #0f1614;")
        about_layout.addWidget(org_label)
        
        # Backend API connection status
        api_status_label = QLabel("Backend API: Connected")
        api_status_label.setFont(QFont("Trebuchet MS", 12))
        api_status_label.setStyleSheet("color: #0c554a; font-weight: 500;")
        about_layout.addWidget(api_status_label)

        # Email verification status
        self.email_status_label = QLabel("Email: Checking...")
        self.email_status_label.setFont(QFont("Trebuchet MS", 12))
        self.email_status_label.setStyleSheet("color: #b2a48f; font-weight: 500;")
        about_layout.addWidget(self.email_status_label)

        # Resend verification button (initially hidden) - more subtle
        self.resend_email_button = QPushButton("Resend verification email")
        self.resend_email_button.setFixedWidth(180)
        self.resend_email_button.setFixedHeight(30)
        self.resend_email_button.clicked.connect(self.show_resend_verification_dialog)
        self.resend_email_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #edbc2c;
                font-size: 11px;
                font-weight: normal;
                padding: 5px 10px;
                border: 1px solid #edbc2c;
                border-radius: 15px;
                text-decoration: underline;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
                text-decoration: none;
            }
        """)
        self.resend_email_button.hide()  # Hide initially
        about_layout.addWidget(self.resend_email_button)

        # Check email verification status when dashboard loads
        self.check_email_verification_status()
        
        # Last updated info
        import datetime
        last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_label = QLabel(f"Last Updated: {last_updated}")
        updated_label.setFont(QFont("Trebuchet MS", 10))
        updated_label.setStyleSheet("color: #b2a48f;")
        about_layout.addWidget(updated_label)
        
        # System info button
        self.system_info_btn = QPushButton("System Information")
        IconManager.set_button_icon(self.system_info_btn, 'info', "System Information", size=16)
        self.system_info_btn.setFixedWidth(150)
        self.system_info_btn.setFixedHeight(35)
        self.system_info_btn.setStyleSheet("""
            QPushButton {
                background-color: #b2a48f;
                color: #0f1614;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 500;
                border: none;
            }
            QPushButton:hover {
                background-color: #0c554a;
                color: #f3f7f6;
            }
        """)
        self.system_info_btn.clicked.connect(self.show_system_info)
        about_layout.addWidget(self.system_info_btn, 0, Qt.AlignLeft)
        
        settings_layout.addWidget(about_section)
        
        settings_layout.addStretch()
        return settings_page

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.theme_btn.isChecked():
            self.theme_btn.setText("Dark Mode")
            # Dark theme switching implementation
            QMessageBox.information(self, "Theme", "Dark mode enabled!")
        else:
            self.theme_btn.setText("Light Mode")
            QMessageBox.information(self, "Theme", "Light mode enabled!")
    
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
        return """
        QFrame#Sidebar { background-color: #0c554a; }
        QPushButton {
            background-color: #0c554a;
            color: #f3f7f6;
            border-radius: 20px;
            padding: 12px 20px;
            font-weight: 500;
            max-width: 180px;
        }
        QPushButton:hover { background-color: #edbc2c; color: #0f1614; }
        QPushButton:checked { background-color: #b2a48f; color: #0f1614; }
        QFrame#Card { color: #0f1614; }
        QFrame#Content, QFrame#TopBar { background-color: #f3f7f6; }
        QLabel { color: #0f1614; }
        """

    def create_status_card(self, title, value, icon, color):
        card = QFrame()
        card.setStyleSheet(f"background-color: {color}; color: #f3f7f6; border-radius: 10px; padding: 10px;")
        layout = QVBoxLayout(card)

        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; color: white;")
        value_label.setObjectName(title)  # store name for updates

        layout.addWidget(title_label)
        layout.addWidget(value_label)

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
                    self.email_status_label.setStyleSheet("color: #0c554a; font-weight: 500;")
                    self.resend_email_button.hide()
                else:
                    self.email_status_label.setText("Email: Not Verified")
                    self.email_status_label.setStyleSheet("color: #edbc2c; font-weight: 500;")
                    self.resend_email_button.show()
            else:
                self.email_status_label.setText("Email: Status Unknown")
                self.email_status_label.setStyleSheet("color: #b2a48f; font-weight: 500;")
        except Exception as e:
            print(f"Error checking email verification: {e}")
            self.email_status_label.setText("Email: Status Unknown")
            self.email_status_label.setStyleSheet("color: #b2a48f; font-weight: 500;")

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
        self.setFixedSize(500, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f7f6;
            }
            QLabel {
                color: #0f1614;
                font-size: 13px;
                margin: 3px 0;
                background-color: transparent;
            }
            QLineEdit {
                border: 2px solid #b2a48f;
                border-radius: 12px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #f3f7f6;
                color: #0f1614;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border: 2px solid #0c554a;
            }
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 500;
                margin: 8px 5px;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(35, 25, 35, 25)
        
        # Title
        title = QLabel("Change Password")
        title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        title.setStyleSheet("color: #0c554a; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Current password
        current_label = QLabel("Current Password:")
        layout.addWidget(current_label)
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setPlaceholderText("Enter current password")
        layout.addWidget(self.current_password)
        
        # New password
        new_label = QLabel("New Password:")
        layout.addWidget(new_label)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter new password")
        self.new_password.textChanged.connect(self.update_password_validation)
        layout.addWidget(self.new_password)
        
        # Confirm new password
        confirm_label = QLabel("Confirm New Password:")
        layout.addWidget(confirm_label)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm new password")
        self.confirm_password.textChanged.connect(self.update_password_validation)
        layout.addWidget(self.confirm_password)
        
        # Password requirements with color coding
        requirements_label = QLabel("Password Requirements:")
        requirements_label.setFont(QFont("Trebuchet MS", 12, QFont.Bold))
        requirements_label.setStyleSheet("color: #0c554a; margin-top: 10px;")
        layout.addWidget(requirements_label)
        
        self.req_length = QLabel("• 10-20 characters long")
        self.req_length.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.req_length)
        
        self.req_special = QLabel("• At least one special character")
        self.req_special.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.req_special)
        
        self.req_capital = QLabel("• At least one capital letter")
        self.req_capital.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.req_capital)
        
        self.req_number = QLabel("• At least one number")
        self.req_number.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        layout.addWidget(self.req_number)
        
        self.req_match = QLabel("• Passwords must match")
        self.req_match.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
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
            self.req_length.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_length.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        
        # Check special character requirement
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.req_special.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_special.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        
        # Check capital letter requirement
        if re.search(r'[A-Z]', password):
            self.req_capital.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_capital.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        
        # Check number requirement
        if re.search(r'[0-9]', password):
            self.req_number.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_number.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        
        # Check password match requirement
        if password and confirm_password and password == confirm_password:
            self.req_match.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_match.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
    
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
