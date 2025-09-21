# Reshma Shaik
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QDialog, QDialogButtonBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from icon_utils import IconManager
from api_client import api_client

class LoginPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget  # reference to QStackedWidget for navigation
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
        layout.addSpacerItem(QSpacerItem(25, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

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
        self.password_input.setEchoMode(QLineEdit.Password)  # hide text input
        self.password_input.setFixedHeight(40)
        self.password_input.setFixedWidth(300)  # make it less wide to accommodate the button
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

        layout.addLayout(pw_layout)

        # ---------------- Login Button ----------------
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(250)  # Consistent width
        self.login_button.clicked.connect(self.login_user)  # connect to login logic
        layout.addWidget(self.login_button, 0, Qt.AlignCenter)

        # ---------------- Forgot Password Link ----------------
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.setFixedWidth(200)
        self.forgot_password_button.setObjectName("forgotPasswordButton")  
        self.forgot_password_button.clicked.connect(self.show_forgot_password_dialog)
        layout.addWidget(self.forgot_password_button, 0, Qt.AlignCenter)

        # Small spacer between forgot password and signup
        layout.addSpacerItem(QSpacerItem(25, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ---------------- Sign Up Button ----------------
        self.signup_button = QPushButton("Create New Account")
        self.signup_button.setFixedWidth(250)  # Consistent width
        self.signup_button.clicked.connect(self.go_to_signup)  # navigate to signup page
        layout.addWidget(self.signup_button, 0, Qt.AlignCenter)

        # Spacer (keeps layout balanced vertically)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Apply layout to this page
        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.toggle_pw_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            IconManager.set_button_icon(self.toggle_pw_btn, 'eye_slash', size=16)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            IconManager.set_button_icon(self.toggle_pw_btn, 'eye', size=16)



    # ---------------- Login Logic ----------------
    def login_user(self):
        print(" LOGIN: Button clicked, starting login process...")
        
        # Collect user input
        email = self.email_input.text().strip()
        password = self.password_input.text()
        print(f" LOGIN: Collected credentials - Email: {email[:10]}...")

        # Validation: fields cannot be empty
        if not email or not password:
            print(" LOGIN: Validation failed - empty fields")
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return

        print(" LOGIN: About to call API client...")
        try:
            # Call backend API for login
            success, message, data = api_client.login(email, password)
            print(f" LOGIN: API call completed - Success: {success}, Message: {message}")
            
            if success:
                print(" LOGIN: Login successful, clearing fields...")
                # Clear the input fields on successful login
                self.email_input.clear()
                self.password_input.clear()
                
                print(f" LOGIN: User data received: {data}")
                
                # Show success message (optional)
                # QMessageBox.information(self, "Success", f"Welcome {data.get('user', {}).get('name', 'User')}!")
                
                print(" LOGIN: About to navigate to dashboard...")
                # Navigate to dashboard page
                self.stacked_widget.setCurrentIndex(2)
                print(" LOGIN: Navigation completed successfully!")
            else:
                print(f" LOGIN: Login failed - {message}")
                QMessageBox.warning(self, "Login Error", message)
        except Exception as e:
            print(f" LOGIN: Exception occurred: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Login failed with error: {str(e)}")

    # ---------------- Forgot Password Dialog ----------------
    def show_forgot_password_dialog(self):
        """Show dialog for forgot password functionality"""
        print(" FORGOT PASSWORD: Opening dialog...")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setFixedSize(480, 320)  # Increased height from 280 to 320
        dialog.setModal(True)
        
        # Enhanced styling to match the application's design system
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f3f7f6;
                border-radius: 16px;
                border: 2px solid #b2a48f;
            }
            QLabel {
                color: #0f1614;
                font-family: 'Trebuchet MS', sans-serif;
                font-size: 14px;
                line-height: 1.4;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0c554a;
                margin: 0px 0px 8px 0px;
            }
            QLabel#instructionLabel {
                font-size: 13px;
                color: #0f1614;
                margin: 0px 0px 10px 0px;
            }
            QLineEdit {
                border: 2px solid #b2a48f;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Trebuchet MS', sans-serif;
                background-color: #f3f7f6;
                color: #0f1614;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #0c554a;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #0c554a;
            }
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                font-size: 14px;
                font-family: 'Trebuchet MS', sans-serif;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 15px;
                border: none;
                min-width: 120px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QPushButton:pressed {
                background-color: #d4a627;
                transform: translateY(1px);
            }
            QPushButton#cancelButton {
                background-color: transparent;
                color: #0f1614;
                border: 2px solid #b2a48f;
            }
            QPushButton#cancelButton:hover {
                background-color: #b2a48f;
                color: #f3f7f6;
                border: 2px solid #b2a48f;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)  # Reduced spacing from 20 to 15
        layout.setContentsMargins(40, 30, 40, 30)  # Reduced top/bottom margins from 35 to 30
        
        # Title with consistent styling
        title_label = QLabel("Reset Password")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Reduced from 10 to 8
        
        # Instructions with better formatting
        instructions = QLabel("Enter email address and a link will be sent to reset password.")
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Trebuchet MS", 13))
        layout.addWidget(instructions)
        
        # Add some vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Email input with consistent styling
        email_input = QLineEdit()
        email_input.setPlaceholderText("Enter @wayne.edu email address")
        email_input.setFont(QFont("Trebuchet MS", 14))
        layout.addWidget(email_input)
        
        # Add some vertical spacing before buttons
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Custom button layout for better control
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFont(QFont("Trebuchet MS", 14, QFont.Normal))
        
        # Send button
        send_button = QPushButton(" Send Reset Link")
        send_button.setFont(QFont("Trebuchet MS", 14, QFont.DemiBold))
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(send_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        def send_reset_email():
            email = email_input.text().strip()
            if not email:
                # Enhanced error styling
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Input Required")
                msg.setText("Please enter email address.")
                msg.setIcon(QMessageBox.Warning)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f3f7f6;
                        font-family: 'Trebuchet MS', sans-serif;
                    }
                    QMessageBox QPushButton {
                        background-color: #0c554a;
                        color: #f3f7f6;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-weight: 600;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #edbc2c;
                        color: #0f1614;
                    }
                """)
                msg.exec_()
                return
            
            if not email.endswith("@wayne.edu"):
                # Enhanced error styling
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Invalid Email")
                msg.setText("Please enter a valid @wayne.edu email address.")
                msg.setIcon(QMessageBox.Warning)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f3f7f6;
                        font-family: 'Trebuchet MS', sans-serif;
                    }
                    QMessageBox QPushButton {
                        background-color: #0c554a;
                        color: #f3f7f6;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-weight: 600;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #edbc2c;
                        color: #0f1614;
                    }
                """)
                msg.exec_()
                return
            
            print(f" FORGOT PASSWORD: Sending reset email to {email}")
            
            # Call API to send reset email
            success, message, _ = api_client.send_password_reset(email)
            
            if success:
                # Enhanced success styling
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Email Sent")
                msg.setText(f"Password reset instructions have been sent to {email}.\n\nPlease check email and follow the link to reset password.")
                msg.setIcon(QMessageBox.Information)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f3f7f6;
                        font-family: 'Trebuchet MS', sans-serif;
                    }
                    QMessageBox QPushButton {
                        background-color: #0c554a;
                        color: #f3f7f6;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-weight: 600;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #edbc2c;
                        color: #0f1614;
                    }
                """)
                msg.exec_()
                dialog.accept()
            else:
                # Enhanced error styling
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Error")
                msg.setText(message)
                msg.setIcon(QMessageBox.Critical)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #f3f7f6;
                        font-family: 'Trebuchet MS', sans-serif;
                    }
                    QMessageBox QPushButton {
                        background-color: #0c554a;
                        color: #f3f7f6;
                        padding: 8px 16px;
                        border-radius: 8px;
                        font-weight: 600;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #edbc2c;
                        color: #0f1614;
                    }
                """)
                msg.exec_()
        
        # Connect button signals
        send_button.clicked.connect(send_reset_email)
        cancel_button.clicked.connect(dialog.reject)
        
        # Set focus to email input for better UX
        email_input.setFocus()
        
        # Allow Enter key to submit
        email_input.returnPressed.connect(send_reset_email)
        
        dialog.exec_()

    def show_password_reset_dialog(self, reset_token=None):
        """Show dialog for entering new password with validation"""
        print(" PASSWORD RESET: Opening password reset dialog...")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setFixedSize(520, 650)
        dialog.setModal(True)
        
        # Enhanced styling to match the application's design system
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f3f7f6;
                border-radius: 16px;
                border: 2px solid #b2a48f;
            }
            QLabel {
                color: #0f1614;
                font-family: 'Trebuchet MS', sans-serif;
                font-size: 14px;
                line-height: 1.4;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0c554a;
                margin: 0px 0px 8px 0px;
            }
            QLabel#instructionLabel {
                font-size: 13px;
                color: #0f1614;
                margin: 0px 0px 10px 0px;
            }
            QLabel#reqLabel {
                font-size: 12px;
                color: #edbc2c;
                background-color: transparent;
                padding: 2px 0px;
            }
            QLineEdit {
                border: 2px solid #b2a48f;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: 'Trebuchet MS', sans-serif;
                background-color: #f3f7f6;
                color: #0f1614;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #0c554a;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #0c554a;
            }
            QPushButton {
                background-color: #0c554a;
                color: #f3f7f6;
                font-size: 14px;
                font-family: 'Trebuchet MS', sans-serif;
                font-weight: 600;
                padding: 12px 24px;
                border-radius: 15px;
                border: none;
                min-width: 120px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #edbc2c;
                color: #0f1614;
            }
            QPushButton:pressed {
                background-color: #d4a627;
                transform: translateY(1px);
            }
            QPushButton:disabled {
                background-color: #b2a48f;
                color: #f3f7f6;
            }
            QPushButton#cancelButton {
                background-color: transparent;
                color: #0f1614;
                border: 2px solid #b2a48f;
            }
            QPushButton#cancelButton:hover {
                background-color: #b2a48f;
                color: #f3f7f6;
                border: 2px solid #b2a48f;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 35, 40, 35)
        
        # Title with consistent styling
        title_label = QLabel("Create New Password")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Instructions with better formatting
        instructions = QLabel("Please enter new password. Make sure it meets all the requirements below.")
        instructions.setObjectName("instructionLabel")
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setFont(QFont("Trebuchet MS", 13))
        layout.addWidget(instructions)
        
        # Add some vertical spacing
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # New Password input
        new_password_label = QLabel("New Password:")
        new_password_label.setFont(QFont("Trebuchet MS", 14, QFont.DemiBold))
        layout.addWidget(new_password_label)
        
        # Password input with show/hide button
        password_layout = QHBoxLayout()
        new_password_input = QLineEdit()
        new_password_input.setPlaceholderText("Enter new password")
        new_password_input.setEchoMode(QLineEdit.Password)
        new_password_input.setFont(QFont("Trebuchet MS", 14))
        password_layout.addWidget(new_password_input)
        
        # Show/hide password button
        toggle_btn = QPushButton("")
        toggle_btn.setFixedSize(45, 45)
        toggle_btn.setToolTip("Show/Hide Password")
        password_layout.addWidget(toggle_btn)
        layout.addLayout(password_layout)
        
        # Confirm Password input
        confirm_password_label = QLabel("Confirm New Password:")
        confirm_password_label.setFont(QFont("Trebuchet MS", 14, QFont.DemiBold))
        layout.addWidget(confirm_password_label)
        
        confirm_password_input = QLineEdit()
        confirm_password_input.setPlaceholderText("Confirm new password")
        confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setFont(QFont("Trebuchet MS", 14))
        layout.addWidget(confirm_password_input)
        
        # Add spacing before requirements
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Password requirements section
        req_label = QLabel("Password Requirements:")
        req_label.setFont(QFont("Trebuchet MS", 14, QFont.DemiBold))
        req_label.setStyleSheet("color: #0c554a;")
        layout.addWidget(req_label)
        
        # Requirements list
        req_length = QLabel("• Must be 10-20 characters long")
        req_length.setObjectName("reqLabel")
        layout.addWidget(req_length)
        
        req_special = QLabel("• Must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        req_special.setObjectName("reqLabel")
        layout.addWidget(req_special)
        
        req_capital = QLabel("• Must contain at least one uppercase letter")
        req_capital.setObjectName("reqLabel")
        layout.addWidget(req_capital)
        
        req_lowercase = QLabel("• Must contain at least one lowercase letter")
        req_lowercase.setObjectName("reqLabel")
        layout.addWidget(req_lowercase)
        
        req_number = QLabel("• Must contain at least one number")
        req_number.setObjectName("reqLabel")
        layout.addWidget(req_number)
        
        req_match = QLabel("• Passwords must match")
        req_match.setObjectName("reqLabel")
        layout.addWidget(req_match)
        
        # Add spacing before buttons
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Custom button layout for better control
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFont(QFont("Trebuchet MS", 14, QFont.Normal))
        
        # Reset button (initially disabled)
        reset_button = QPushButton(" Reset Password")
        reset_button.setFont(QFont("Trebuchet MS", 14, QFont.DemiBold))
        reset_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Password validation function
        def update_password_validation():
            """Update password requirement colors and button state based on current input"""
            import re
            
            password = new_password_input.text()
            confirm_password = confirm_password_input.text()
            all_valid = True
            
            # Check length requirement (10-20 characters)
            if len(password) >= 10 and len(password) <= 20:
                req_length.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_length.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
            
            # Check special character requirement
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                req_special.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_special.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
            
            # Check capital letter requirement
            if re.search(r'[A-Z]', password):
                req_capital.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_capital.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
                
            # Check lowercase letter requirement
            if re.search(r'[a-z]', password):
                req_lowercase.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_lowercase.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
            
            # Check number requirement
            if re.search(r'[0-9]', password):
                req_number.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_number.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
            
            # Check password match requirement
            if password and confirm_password and password == confirm_password:
                req_match.setStyleSheet("color: #0c554a; font-size: 12px; background-color: transparent;")
            else:
                req_match.setStyleSheet("color: #edbc2c; font-size: 12px; background-color: transparent;")
                all_valid = False
            
            # Enable/disable reset button based on validation
            reset_button.setEnabled(all_valid and len(password) > 0)
        
        # Password visibility toggle
        def toggle_password_visibility():
            if new_password_input.echoMode() == QLineEdit.Password:
                new_password_input.setEchoMode(QLineEdit.Normal)
                confirm_password_input.setEchoMode(QLineEdit.Normal)
                toggle_btn.setText("")
            else:
                new_password_input.setEchoMode(QLineEdit.Password)
                confirm_password_input.setEchoMode(QLineEdit.Password)
                toggle_btn.setText("")
        
        # Reset password function
        def reset_password():
            password = new_password_input.text()
            confirm_password = confirm_password_input.text()
            
            # Double-check validation before proceeding
            import re
            
            if not password:
                return
                
            if len(password) < 10 or len(password) > 20:
                return
                
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return
                
            if not re.search(r'[A-Z]', password):
                return
                
            if not re.search(r'[a-z]', password):
                return
                
            if not re.search(r'[0-9]', password):
                return
                
            if password != confirm_password:
                return
            
            print(f" PASSWORD RESET: Resetting password with token: {reset_token}")
            
            # Call API to reset the password
            success, message, _ = api_client.reset_password_with_token(reset_token, password)
            
            if success:
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Password Reset Successful")
                msg.setText("Password has been successfully reset.\n\nLogin with the new password.")
                msg.setIcon(QMessageBox.Information)
            else:
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Password Reset Failed")
                msg.setText(f"Failed to reset password:\n\n{message}")
                msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f3f7f6;
                    font-family: 'Trebuchet MS', sans-serif;
                }
                QMessageBox QPushButton {
                    background-color: #0c554a;
                    color: #f3f7f6;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #edbc2c;
                    color: #0f1614;
                }
            """)
            msg.exec_()
            
            # Only close dialog on success
            if success:
                dialog.accept()
        
        # Connect signals
        new_password_input.textChanged.connect(update_password_validation)
        confirm_password_input.textChanged.connect(update_password_validation)
        toggle_btn.clicked.connect(toggle_password_visibility)
        reset_button.clicked.connect(reset_password)
        cancel_button.clicked.connect(dialog.reject)
        
        # Set focus to password input
        new_password_input.setFocus()
        
        # Initialize validation
        update_password_validation()
        
        dialog.exec_()

    # ---------------- Navigation to Sign Up ----------------
    def go_to_signup(self):
        self.stacked_widget.setCurrentIndex(1)  # switch to signup page (index 1)

    # ---------------- Stylesheet ----------------
    def load_styles(self):
        # Defines styling for all widgets on the login page
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
        QPushButton#forgotPasswordButton {
            background-color: transparent;
            color: #0c554a;
            text-decoration: underline;
            border: none;
            padding: 5px;
            font-size: 13px;
        }
        QPushButton#forgotPasswordButton:hover {
            color: #edbc2c;
            background-color: transparent;
        }
        QLabel {
            color: #0f1614;
        }
        """
