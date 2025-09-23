# Reshma Shaik
# Main application file for CORA using PyQt5
import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from login import LoginPage
from signup import SignUpPage
from dashboard import Dashboard
from activity_page import ActivityPage

# -----------------------------
# Main application entry point
# -----------------------------

# Create the application object
app = QApplication(sys.argv)

# QStackedWidget allows stacking multiple pages
main_window = QStackedWidget()
main_window.setWindowTitle("CORA")
main_window.setGeometry(100, 100, 1200, 800)
main_window.setMinimumSize(800, 600)  # Set minimum size for usability

# -----------------------------
# Create and register pages
# -----------------------------

login_page = LoginPage(main_window)       # Index 0  -  Login Page
signup_page = SignUpPage(main_window)     # Index 1  -  Sign-Up Page
dashboard_page = Dashboard()              # Index 2  -  Dashboard Page
activity_page = ActivityPage()            # Index 3  -  Activity Logs Page

# Add all pages to the stacked widget
main_window.addWidget(login_page)
main_window.addWidget(signup_page)
main_window.addWidget(dashboard_page)
main_window.addWidget(activity_page)

# -----------------------------
# Start application
# -----------------------------

main_window.setCurrentIndex(0)  # Start on login page
main_window.show()

sys.exit(app.exec_())
