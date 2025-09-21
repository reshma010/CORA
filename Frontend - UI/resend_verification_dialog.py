# Oleg Korobeyko
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from api_client import api_client

class ResendVerificationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        title_label.setStyleSheet("color: #0c554a; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Enter email address to receive a new verification email.")
        desc_label.setFont(QFont("Trebuchet MS", 11))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #0f1614; margin-bottom: 10px;")
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
        
        # Call API to resend verification
        success, message, data = api_client.resend_verification_email(email)
        
        if success:
            QMessageBox.information(self, "Success", 
                                  f"Verification email sent successfully to {email}.\n\n"
                                  "Please check email inbox and spam folder.")
            self.accept()  # Close dialog
        else:
            QMessageBox.warning(self, "Error", f"Failed to send verification email:\n{message}")
    
    def load_styles(self):
        return """
        QDialog {
            background-color: #f3f7f6;
        }
        QLineEdit {
            border: 2px solid #b2a48f;
            border-radius: 20px;
            padding: 10px 15px;
            font-size: 14px;
            background-color: #f3f7f6;
            color: #0f1614;
        }
        QLineEdit:focus {
            border: 2px solid #0c554a;
        }
        QPushButton {
            background-color: #0c554a;
            color: #f3f7f6;
            font-size: 14px;
            font-weight: 500;
            padding: 10px 20px;
            border-radius: 20px;
            border: none;
        }
        QPushButton:hover {
            background-color: #edbc2c;
            color: #0f1614;
        }
        QPushButton#cancel_button {
            background-color: #b2a48f;
        }
        QPushButton#cancel_button:hover {
            background-color: #999;
        }
        """