from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import re
from icon_utils import IconManager
from api_client import api_client
from email_confirmation_dialog import EmailConfirmationDialog

class SignUpPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget  # Reference to QStackedWidget (to switch between pages)
        self.setStyleSheet(self.load_styles())  # apply custom stylesheet

        # ---------------- Main Layout ----------------
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)        # center all widgets
        layout.setContentsMargins(100, 50, 100, 50)  # padding around content
        layout.setSpacing(20)                      # space between widgets

        # ---------------- Logo ----------------
        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background-color: transparent;")  # Transparent background
        pixmap = QPixmap("assets/Cora.png")
        if not pixmap.isNull():
            # Scale the logo to a smaller size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(850, 425, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to text if image can't be loaded
            self.logo_label.setText("CORA")
            self.logo_label.setFont(QFont("Trebuchet MS", 50, QFont.Bold))
            self.logo_label.setStyleSheet("""
                QLabel {
                    background-color: #0c554a;
                    color: #f3f7f6;
                    border-radius: 16px;
                    padding: 20px;
                }
            """)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label, 0, Qt.AlignCenter)

        # Very small spacer for minimal spacing
        layout.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ---------------- Name Input ----------------
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        self.name_input.setFixedHeight(40)           # consistent height
        self.name_input.setFixedWidth(350)           # make it less wide
        layout.addWidget(self.name_input, 0, Qt.AlignCenter)

        # ---------------- Email Input ----------------
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (@wayne.edu)")
        self.email_input.setFixedHeight(40)           # consistent height
        self.email_input.setFixedWidth(350)           # make it less wide
        layout.addWidget(self.email_input, 0, Qt.AlignCenter)

        # ---------------- Password Input ----------------
        pw_layout = QVBoxLayout()
        pw_layout.setSpacing(2)
        pw_layout.setAlignment(Qt.AlignCenter)
        pw_row = QHBoxLayout()
        pw_row.setSpacing(0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hide characters when typing
        self.password_input.setFixedHeight(40)
        self.password_input.setFixedWidth(300)  # make it less wide to accommodate the button
        self.password_input.setMaxLength(20)  # Limit to 20 characters
        self.password_input.textChanged.connect(self.update_password_validation)
        pw_row.addWidget(self.password_input)
        
        # Show/hide password button with duotone icon
        self.toggle_pw_btn = QPushButton()
        IconManager.set_button_icon(self.toggle_pw_btn, 'eye', size=16)
        self.toggle_pw_btn.setCheckable(True)
        self.toggle_pw_btn.setFixedHeight(40)
        self.toggle_pw_btn.setFixedWidth(50)
        self.toggle_pw_btn.setStyleSheet("padding: 8px 12px; font-size: 16px; border-radius: 20px;")
        self.toggle_pw_btn.clicked.connect(self.toggle_password_visibility)
        pw_row.addWidget(self.toggle_pw_btn)
        
        pw_layout.addLayout(pw_row)
        
        # Character counter
        self.char_counter = QLabel("20 characters remaining")
        self.char_counter.setStyleSheet("color: #b2a48f; font-size: 12px; background-color: transparent;")
        pw_layout.addWidget(self.char_counter)
        
        # Password requirements with better spacing
        requirements_layout = QVBoxLayout()
        requirements_layout.setSpacing(2)  # Minimal spacing between requirements
        requirements_layout.setContentsMargins(0, 2, 0, 0)  # Minimal top margin
        
        self.req_length = QLabel("• At least 10 characters")
        self.req_length.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        requirements_layout.addWidget(self.req_length)
        
        self.req_special = QLabel("• At least one special character")
        self.req_special.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        requirements_layout.addWidget(self.req_special)
        
        self.req_capital = QLabel("• At least one capital letter")
        self.req_capital.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        requirements_layout.addWidget(self.req_capital)
        
        self.req_number = QLabel("• At least one number")
        self.req_number.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        requirements_layout.addWidget(self.req_number)
        
        # Password match requirement
        self.req_match = QLabel("• Passwords must match")
        self.req_match.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        requirements_layout.addWidget(self.req_match)
        
        pw_layout.addLayout(requirements_layout)
        
        layout.addLayout(pw_layout)

        # ---------------- Confirm Password Input ----------------
        confirm_pw_layout = QVBoxLayout()
        confirm_pw_layout.setSpacing(2)
        confirm_pw_layout.setAlignment(Qt.AlignCenter)
        confirm_pw_row = QHBoxLayout()
        confirm_pw_row.setSpacing(0)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)  # Hide characters when typing
        self.confirm_password_input.setFixedHeight(40)
        self.confirm_password_input.setFixedWidth(300)  # make it less wide to accommodate the button
        self.confirm_password_input.setMaxLength(20)  # Limit to 20 characters
        self.confirm_password_input.textChanged.connect(self.update_password_validation)
        confirm_pw_row.addWidget(self.confirm_password_input)
        
        # Show/hide confirm password button with duotone icon
        self.toggle_confirm_pw_btn = QPushButton()
        IconManager.set_button_icon(self.toggle_confirm_pw_btn, 'eye', size=16)
        self.toggle_confirm_pw_btn.setCheckable(True)
        self.toggle_confirm_pw_btn.setFixedHeight(40)
        self.toggle_confirm_pw_btn.setFixedWidth(50)
        self.toggle_confirm_pw_btn.setStyleSheet("padding: 8px 12px; font-size: 16px; border-radius: 20px;")
        self.toggle_confirm_pw_btn.clicked.connect(self.toggle_confirm_password_visibility)
        confirm_pw_row.addWidget(self.toggle_confirm_pw_btn)
        
        confirm_pw_layout.addLayout(confirm_pw_row)
        layout.addLayout(confirm_pw_layout)

        # ---------------- Sign Up Button ----------------
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setFixedWidth(250)  # Consistent width
        self.signup_button.clicked.connect(self.signup_user)
        layout.addWidget(self.signup_button, 0, Qt.AlignCenter)

        # ---------------- Back to Login Button ----------------
        self.back_button = QPushButton("Back to Login")
        self.back_button.setFixedWidth(250)  # Consistent width
        self.back_button.clicked.connect(self.go_to_login)
        layout.addWidget(self.back_button, 0, Qt.AlignCenter)

        # Spacer (keeps layout balanced vertically)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Apply layout to page
        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.toggle_pw_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            IconManager.set_button_icon(self.toggle_pw_btn, 'eye_slash', size=16)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            IconManager.set_button_icon(self.toggle_pw_btn, 'eye', size=16)

    def toggle_confirm_password_visibility(self):
        if self.toggle_confirm_pw_btn.isChecked():
            self.confirm_password_input.setEchoMode(QLineEdit.Normal)
            IconManager.set_button_icon(self.toggle_confirm_pw_btn, 'eye_slash', size=16)
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            IconManager.set_button_icon(self.toggle_confirm_pw_btn, 'eye', size=16)

    def update_password_validation(self):
        password = self.password_input.text()
        count = len(password)
        remaining = max(0, 20 - count)
        
        # Update character counter
        if remaining == 0:
            self.char_counter.setText("Maximum length reached")
            self.char_counter.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
        else:
            self.char_counter.setText(f"{remaining} characters remaining")
            self.char_counter.setStyleSheet("color: #b2a48f; font-size: 12px; background-color: transparent;")
        
        # Check length requirement (at least 10 characters)
        if count >= 10:
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
        confirm_password = self.confirm_password_input.text()
        if password and confirm_password and password == confirm_password:
            self.req_match.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
        else:
            self.req_match.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")

    def is_password_valid(self):
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        return (len(password) >= 10 and 
                len(password) <= 20 and
                re.search(r'[!@#$%^&*(),.?":{}|<>]', password) and
                re.search(r'[A-Z]', password) and
                re.search(r'[0-9]', password) and
                password == confirm_password)

    #Methods
    def signup_user(self):
        """Handles user sign-up using the backend API."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        # Validation: fields cannot be empty
        if not name or not email or not password or not confirm_password:
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return

        # Validation: name must be at least 2 characters
        if len(name) < 2:
            QMessageBox.warning(self, "Error", "Name must be at least 2 characters long.")
            return
        
        # Validation: passwords must match
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        # Validation: password must meet all requirements
        if not self.is_password_valid():
            QMessageBox.warning(self, "Error", "Password does not meet all requirements.")
            return

        # Call backend API for registration
        success, message, data = api_client.register(name, email, password)
        
        if success:
            # Show email confirmation dialog
            user_info = data.get('user', {})
            user_name = user_info.get('name', 'User')
            user_email = user_info.get('email', email)
            
            # Create and show email confirmation dialog
            self.show_email_confirmation_dialog(user_name, user_email)
            
            # Clear form fields after showing dialog
            self.name_input.clear()
            self.email_input.clear()
            self.password_input.clear()
            self.confirm_password_input.clear()
            
            # Automatically log in user (redirect to dashboard)
            self.stacked_widget.setCurrentIndex(2)  # Go directly to dashboard
        else:
            QMessageBox.warning(self, "Registration Error", message)

    def go_to_login(self):
        """Switches back to login page."""
        self.stacked_widget.setCurrentIndex(0)

    def show_email_confirmation_dialog(self, user_name, user_email):
        """Show the email confirmation dialog with CORA styling"""
        dialog = EmailConfirmationDialog(user_name, user_email, self)
        dialog.emailVerified.connect(self.handle_email_verified)
        dialog.exec_()
    
    def handle_email_verified(self, user_email, user_name):
        """Handle successful email verification by auto-logging in"""
        # Get password from the form if still available (for auto-login)
        password = self.password_input.text()
        
        if password:  # If password is still in the form
            # Attempt login
            success, message, data = api_client.login(user_email, password)
            
            if success:
                # Login successful - switch to dashboard page
                # Set auth token for requests
                token = data.get('token')
                if token:
                    api_client.set_auth_token(token)
                
                # Switch to dashboard page (index 2)
                self.stacked_widget.setCurrentIndex(2)
            else:
                # Login failed for some reason, just show success message
                QMessageBox.information(self, "Email Verified", 
                    f"Email has been verified successfully! Please log in.")
                self.go_to_login()
        else:
            # No password available, just show success and go to login
            QMessageBox.information(self, "Email Verified", 
                f"Email has been verified successfully! Please log in.")
            self.go_to_login()

    # ---------------- Stylesheet ----------------
    def load_styles(self):
        # Defines styling for all widgets on the signup page
        return """
        QWidget {
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
            font-size: 15px;
            font-weight: 500;
            padding: 12px 20px;
            border-radius: 20px;
            border: none;
        }
        QPushButton:hover {
            background-color: #edbc2c;
            color: #0f1614;
        }
        QLabel {
            color: #0f1614;
        }
        """
