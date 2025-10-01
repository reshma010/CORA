# Oleg Korobeyko
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from icon_utils import IconManager
from api_client import api_client
from theme_manager import ThemeManager

class EmailConfirmationDialog(QDialog):
    # Signal emitted when email is verified
    emailVerified = pyqtSignal(str, str)  # email, user_name
    
    def __init__(self, user_name, user_email, parent=None):
        super().__init__(parent)
        self.user_name = user_name
        self.user_email = user_email
        self.theme_manager = ThemeManager()
        self.setWindowTitle("Email Verification")
        self.setFixedSize(500, 450)
        self.setModal(True)
        
        # Verification polling
        self.verification_timer = QTimer()
        self.verification_timer.timeout.connect(self.check_verification_status)
        self.poll_interval = 5000  # 5 seconds
        self.is_verified = False
        
        # Apply CORA styling
        self.setStyleSheet(self.load_styles())
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Logo 
        logo_label = QLabel()
        logo_label.setStyleSheet("background-color: transparent;")
        pixmap = QPixmap("assets/Cora.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("CORA")
            logo_label.setFont(QFont("Trebuchet MS", 24, QFont.Bold))
            logo_label.setStyleSheet(f"color: {self.theme_manager.get_color('primary')}; background-color: transparent;")
        logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)
        
        # Success message
        success_label = QLabel("Account Created Successfully!")
        success_label.setFont(QFont("Trebuchet MS", 20, QFont.Bold))
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet(f"color: {self.theme_manager.get_color('primary')}; margin-bottom: 10px;")
        main_layout.addWidget(success_label)
        
        # Welcome message
        welcome_label = QLabel(f"Welcome to CORA, {self.user_name}!")
        welcome_label.setFont(QFont("Trebuchet MS", 14))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; margin-bottom: 15px;")
        main_layout.addWidget(welcome_label)
        
        # Email verification info card
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme_manager.get_color('secondary')};
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0px;
            }}
        """)
        
        card_layout = QVBoxLayout(info_card)
        card_layout.setSpacing(10)
        
        # Email icon and title
        email_title = QLabel("Email Verification Required")
        email_title.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
        email_title.setAlignment(Qt.AlignCenter)
        email_title.setStyleSheet(f"color: {self.theme_manager.get_color('text')};")
        card_layout.addWidget(email_title)
        
        # Email address
        email_address_label = QLabel(f"Verification email sent to:")
        email_address_label.setFont(QFont("Trebuchet MS", 12))
        email_address_label.setAlignment(Qt.AlignCenter)
        email_address_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')};")
        card_layout.addWidget(email_address_label)
        
        email_label = QLabel(self.user_email)
        email_label.setFont(QFont("Trebuchet MS", 14, QFont.Bold))
        email_label.setAlignment(Qt.AlignCenter)
        email_label.setStyleSheet(f"color: {self.theme_manager.get_color('primary')};")
        card_layout.addWidget(email_label)
        
        # Instructions
        instructions = QLabel("Please check email and click the verification link to complete account setup.")
        instructions.setFont(QFont("Trebuchet MS", 11))
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; margin-top: 5px;")
        card_layout.addWidget(instructions)
        
        main_layout.addWidget(info_card)
        
        # Status label for verification polling
        self.status_label = QLabel("Waiting for email verification...")
        self.status_label.setFont(QFont("Trebuchet MS", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; margin: 10px 0px;")
        main_layout.addWidget(self.status_label)
        
        # Note about staying on this page
        note_label = QLabel("This window automatically closes and logs in once email is verified.")
        note_label.setFont(QFont("Trebuchet MS", 10))
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {self.theme_manager.get_color('accent')}; margin-top: 5px;")
        main_layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Resend email button
        self.resend_button = QPushButton("Resend Email")
        self.resend_button.setFixedHeight(45)
        self.resend_button.setFixedWidth(140)
        self.resend_button.clicked.connect(self.resend_verification)
        
        # Skip verification button
        self.skip_button = QPushButton("Skip for Now")
        self.skip_button.setFixedHeight(45)
        self.skip_button.setFixedWidth(160)
        self.skip_button.clicked.connect(self.skip_verification)
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #b2a48f;
                color: #f3f7f6;
                font-size: 14px;
                font-weight: 500;
                padding: 12px 20px;
                border-radius: 22px;
                border: none;
            }
            QPushButton:hover {
                background-color: #999;
            }
        """)
        
        button_layout.addWidget(self.resend_button)
        button_layout.addWidget(self.skip_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Start verification polling
        self.start_verification_polling()
    
    def start_verification_polling(self):
        """Start polling for email verification status"""
        self.verification_timer.start(self.poll_interval)
        
    def stop_verification_polling(self):
        """Stop polling for email verification status"""
        if self.verification_timer.isActive():
            self.verification_timer.stop()
    
    def check_verification_status(self):
        """Check if the email has been verified"""
        print(f"Checking verification status for: {self.user_email}")
        success, message, data = api_client.check_verification_status(self.user_email)
        print(f"Verification check result: success={success}, data={data}")
        
        if success and data.get('isEmailVerified', False):
            print("Email verified! Stopping polling and showing success.")
            self.is_verified = True
            self.stop_verification_polling()
            self.on_email_verified()
        else:
            # Update status to show still checking
            if success:
                self.status_label.setText("Waiting for email verification...")
            else:
                self.status_label.setText(f"Checking... ({message})")
    
    def on_email_verified(self):
        """Handle successful email verification"""
        self.status_label.setText("Email verified successfully! Logging in...")
        self.status_label.setStyleSheet("color: #0c554a; font-weight: bold; margin: 10px 0px;")
        
        # Disable buttons
        self.resend_button.setEnabled(False)
        self.skip_button.setEnabled(False)
        
        # Emit signal and close dialog after a short delay
        QTimer.singleShot(2000, self.complete_verification)
    
    def complete_verification(self):
        """Complete the verification process"""
        self.emailVerified.emit(self.user_email, self.user_name)
        self.accept()
    
    def skip_verification(self):
        """Skip verification for now"""
        self.stop_verification_polling()
        self.accept()
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.stop_verification_polling()
        super().closeEvent(event)
    
    def resend_verification(self):
        """Resend verification email"""
        success, message, data = api_client.resend_verification_email(self.user_email)
        
        if success:
            self.resend_button.setText("Email Sent!")
            self.resend_button.setStyleSheet("""
                QPushButton {
                    background-color: #0c554a;
                    color: #f3f7f6;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 12px 20px;
                    border-radius: 22px;
                    border: none;
                }
            """)
            self.resend_button.setEnabled(False)
        else:
            self.resend_button.setText("Retry")
            self.resend_button.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: #f3f7f6;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 12px 20px;
                    border-radius: 22px;
                    border: none;
                }
            """)
    
    def load_styles(self):
        return f"""
        QDialog {{
            background-color: {self.theme_manager.get_color('background')};
        }}
        QPushButton {{
            background-color: {self.theme_manager.get_color('accent')};
            color: {self.theme_manager.get_color('text')};
            font-size: 14px;
            font-weight: 500;
            padding: 12px 20px;
            border-radius: 22px;
            border: none;
            font-family: Trebuchet MS;
        }}
        QPushButton:hover {{
            background-color: {self.theme_manager.get_color('accent_dark', '#999')};
        }}
        QPushButton:disabled {{
            background-color: {self.theme_manager.get_color('disabled', '#ccc')};
            color: {self.theme_manager.get_color('disabled_text', '#666')};
        }}
        """