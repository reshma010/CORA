# Oleg Korobeyko
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from api_client import api_client
from theme_manager import ThemeManager

class ResendVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        self.setWindowTitle("Resend Email Verification")
        self.setFixedSize(400, 250)
        self.setModal(True)
        
        # Apply the same styling as other pages
        self.setStyleSheet(self.load_styles())
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Resend Email Verification")
        title_label.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.theme_manager.get_color('primary')}; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Enter email address to receive a new verification email.")
        desc_label.setFont(QFont("Trebuchet MS", 11))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {self.theme_manager.get_color('text')}; margin-bottom: 10px;")
        layout.addWidget(desc_label)
        
        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email (@wayne.edu)")
        self.email_input.setFixedHeight(40)
        layout.addWidget(self.email_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setFixedWidth(120)
        self.cancel_button.clicked.connect(self.reject)
        
        self.resend_button = QPushButton("Resend Email")
        self.resend_button.setFixedHeight(40)
        self.resend_button.setFixedWidth(120)
        self.resend_button.clicked.connect(self.resend_verification)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.resend_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def resend_verification(self):
        email = self.email_input.text().strip()
        
        # Validation
        if not email:
            QMessageBox.warning(self, "Error", "Please enter email address.")
            return
        
        if not email.endswith("@wayne.edu"):
            QMessageBox.warning(self, "Error", "Only @wayne.edu email addresses are allowed.")
            return
        
        # Disable button and show loading state
        self.resend_button.setEnabled(False)
        self.resend_button.setText("Sending...")
        
        # Call API to resend verification
        success, message, data = api_client.resend_verification_email(email)
        
        # Re-enable button
        self.resend_button.setEnabled(True)
        self.resend_button.setText("Resend Email")
        
        if success:
            QMessageBox.information(self, "Success", 
                                  f"Verification email sent successfully to {email}!\n\n"
                                  "Please check your email inbox and spam folder.")
            self.accept()  # Close dialog
        else:
            # Check if it's an email service timeout issue
            if "email service" in message.lower() or "timeout" in message.lower():
                QMessageBox.critical(self, "Email Service Issue", 
                                   f"⚠️ {message}\n\n"
                                   "💡 What you can do:\n"
                                   "• Wait a few minutes and try again\n"
                                   "• Contact support if the issue persists\n"
                                   "• You can still use the system without email verification")
            else:
                QMessageBox.warning(self, "Error", f"Failed to send verification email:\n\n{message}")
    
    def load_styles(self):
        return f"""
        QDialog {{
            background-color: {self.theme_manager.get_color('background')};
        }}
        QLineEdit {{
            border: 2px solid {self.theme_manager.get_color('accent')};
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 14px;
            background-color: {self.theme_manager.get_color('background')};
            color: {self.theme_manager.get_color('text')};
            font-family: Trebuchet MS;
        }}
        QLineEdit:focus {{
            border: 2px solid {self.theme_manager.get_color('primary')};
        }}
        QPushButton {{
            background-color: {self.theme_manager.get_color('primary')};
            color: {self.theme_manager.get_color('text')};
            font-size: 14px;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
            font-family: Trebuchet MS;
        }}
        QPushButton:hover {{
            background-color: {self.theme_manager.get_color('secondary')};
            color: {self.theme_manager.get_color('text')};
        }}
        QPushButton#cancel_button {{
            background-color: {self.theme_manager.get_color('accent')};
        }}
        QPushButton#cancel_button:hover {{
            background-color: {self.theme_manager.get_color('accent_dark', '#999')};
        }}
        """