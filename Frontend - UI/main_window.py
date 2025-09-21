# Reshma Shaik
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from icon_utils import IconManager

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        # ================== Main Layout ==================
        # Main container splits the window into Sidebar (left) + Content (right)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ================== Sidebar ==================
        # Sidebar holds navigation buttons
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)  # fixed width for sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 40, 0, 0)  # add top margin so buttons don’t stick to top
        sidebar_layout.setSpacing(20)

        # Sidebar buttons
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_logs = QPushButton("Logs & Reports")
        self.btn_camera = QPushButton("Live Camera")

        # Apply same styling and sizing to all buttons
        for btn in [self.btn_dashboard, self.btn_logs, self.btn_camera]:
            btn.setFixedHeight(50)
            btn.setFont(QFont("Trebuchet MS", 11))
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()  # push buttons to top, leave space below

        # ================== Content ==================
        # This area changes depending on which page is selected
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # ----------- Top Bar -----------
        # Shows the current section title (changes with navigation)
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar_layout = QHBoxLayout(top_bar)
        self.title_label = QLabel("Dashboard Overview")  # default title
        self.title_label.setFont(QFont("Trebuchet MS", 18, QFont.Bold))
        top_bar_layout.addWidget(self.title_label)
        top_bar_layout.addStretch()  # push title to the left

        # ----------- Summary Cards -----------
        # Cards display quick stats (like KPIs)
        summary_cards = QFrame()
        summary_layout = QHBoxLayout(summary_cards)
        summary_layout.setSpacing(15)

        # Define sample stats for dashboard
        card_data = [
            ("Properties", "721K", "home"),
            ("Clients", "1,156", "user"),
            ("Amount Invested", "$3.67K", "database"),
            ("Avg Price", "2.35K", "chart")
        ]
        
        for title, value, icon_name in card_data:
            card = QFrame()
            card.setObjectName("Card")
            card.setMinimumSize(180, 120)  # minimum size but allow growth
            card.setMaximumHeight(140)     # limit height growth
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)

            # Icon using duotone Font Awesome
            lbl_icon = QLabel()
            IconManager.set_label_icon(lbl_icon, icon_name, "")
            lbl_icon.setFont(QFont("Trebuchet MS", 24))
            lbl_icon.setAlignment(Qt.AlignCenter)

            # Value (big bold number)
            lbl_value = QLabel(value)
            lbl_value.setFont(QFont("Trebuchet MS", 16, QFont.Bold))
            lbl_value.setAlignment(Qt.AlignCenter)

            # Title (label under value)
            lbl_title = QLabel(title)
            lbl_title.setFont(QFont("Trebuchet MS", 10))
            lbl_title.setAlignment(Qt.AlignCenter)

            # Add widgets to card
            card_layout.addWidget(lbl_icon)
            card_layout.addWidget(lbl_value)
            card_layout.addWidget(lbl_title)
            summary_layout.addWidget(card)

        # ----------- Pages (Stacked Widget) -----------
        # Pages switch dynamically based on sidebar button clicks
        self.pages = QStackedWidget()

        # --- Dashboard page ---
        dashboard_page = QWidget()
        dash_layout = QVBoxLayout(dashboard_page)
        dash_label = QLabel()
        IconManager.set_label_icon(dash_label, 'dashboard', "Main Dashboard Content Here")
        dash_label.setFont(QFont("Trebuchet MS", 14))
        dash_label.setAlignment(Qt.AlignCenter)
        dash_layout.addWidget(summary_cards)  # add cards on top
        dash_layout.addWidget(dash_label)
        dash_layout.addStretch()

        # --- Logs & Reports page ---
        logs_page = QLabel()
        IconManager.set_label_icon(logs_page, 'file', "Logs & Reports Page")
        logs_page.setFont(QFont("Trebuchet MS", 14))
        logs_page.setAlignment(Qt.AlignCenter)

        # --- Camera page ---
        camera_page = QLabel()
        IconManager.set_label_icon(camera_page, 'camera', "Live Camera Feed Page")
        camera_page.setFont(QFont("Trebuchet MS", 14))
        camera_page.setAlignment(Qt.AlignCenter)

        # Add all pages into stacked widget
        self.pages.addWidget(dashboard_page)
        self.pages.addWidget(logs_page)
        self.pages.addWidget(camera_page)

        # Add top bar + pages into content area
        content_layout.addWidget(top_bar)
        content_layout.addWidget(self.pages)

        # ================== Navigation Connections ==================
        # Clicking sidebar buttons switches stacked widget index and updates title
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, "Dashboard Overview"))
        self.btn_logs.clicked.connect(lambda: self.switch_page(1, "Logs & Reports"))
        self.btn_camera.clicked.connect(lambda: self.switch_page(2, "Live Camera"))

        # Add sidebar (left) + content (right) into main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        # Apply custom styles
        self.setStyleSheet(self.load_styles())

    # Function to switch between stacked widget pages
    def switch_page(self, index, title):
        self.pages.setCurrentIndex(index)  # change page
        self.title_label.setText(title)    # update title bar

    # ================== Stylesheet ==================
    def load_styles(self):
        return """
        /* Sidebar */
        QFrame#Sidebar {
            background-color: #0c554a;
        }
        QPushButton {
            background-color: #0c554a;
            color: #f3f7f6;
            border-radius: 20px;
            padding: 12px 20px;
            font-weight: 500;
            max-width: 180px;
        }
        QPushButton:hover {
            background-color: #edbc2c;
            color: #0f1614;
        }
        QPushButton:pressed {
            background-color: #b2a48f;
            color: #0f1614;
        }

        /* Cards */
        QFrame#Card {
            background-color: #f3f7f6;
            border-radius: 20px;
            color: #0f1614;
            padding: 15px;
            border: 2px solid #b2a48f;
        }

        /* Content background */
        QFrame {
            background-color: #f3f7f6;
        }
        QLabel {
            color: #0f1614;
        }
        """
