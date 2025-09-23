# Oleg Korobeyko
"""
Icon Utilities for CORA Application
Centralized management of Font Awesome Duotone icons
"""

try:
    import qtawesome as qta
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False

class IconManager:
    """Centralized icon management with Font Awesome Duotone icons"""
    
    # Font Awesome 5 Solid icon mappings
    ICONS = {
        # Authentication & Security
        'eye': 'fa5s.eye',
        'eye_slash': 'fa5s.eye-slash',
        'lock': 'fa5s.lock',
        'unlock': 'fa5s.unlock-alt',
        'key': 'fa5s.key',
        'shield': 'fa5s.shield-alt',
        'user': 'fa5s.user',
        'user_circle': 'fa5s.user-circle',
        'sign_out': 'fa5s.sign-out-alt',
        
        # Navigation & UI
        'dashboard': 'fa5s.tachometer-alt',
        'home': 'fa5s.home',
        'settings': 'fa5s.cog',
        'menu': 'fa5s.bars',
        'chevron_right': 'fa5s.chevron-right',
        'chevron_left': 'fa5s.chevron-left',
        'times': 'fa5s.times',
        'check': 'fa5s.check',
        
        # Application Features
        'camera': 'fa5s.video',
        'file': 'fa5s.file-alt',
        'robot': 'fa5s.robot',
        'chart': 'fa5s.chart-line',
        'bell': 'fa5s.bell',
        'refresh': 'fa5s.sync-alt',
        'clock': 'fa5s.clock',
        'palette': 'fa5s.palette',
        
        # System & Status
        'server': 'fa5s.server',
        'database': 'fa5s.database',
        'cpu': 'fa5s.microchip',
        'memory': 'fa5s.memory',
        'warning': 'fa5s.exclamation-triangle',
        'error': 'fa5s.times-circle',
        'success': 'fa5s.check-circle',
        'info': 'fa5s.info-circle',
        
        # Documents & Data
        'folder': 'fa5s.folder',
        'download': 'fa5s.download',
        'upload': 'fa5s.upload',
        'save': 'fa5s.save',
        'print': 'fa5s.print',
        'search': 'fa5s.search',
    }
    

    FALLBACKS = {
        'eye': 'Show',
        'eye_slash': 'Hide',
        'lock': 'Lock',
        'unlock': 'Unlock',
        'key': 'Key',
        'shield': 'Security',
        'user': 'User',
        'user_circle': 'Account',
        'sign_out': 'Logout',
        
        'dashboard': 'Dashboard',
        'home': 'Home',
        'settings': 'Settings',
        'menu': 'Menu',
        'chevron_right': '>',
        'chevron_left': '<',
        'times': 'X',
        'check': 'OK',
        
        'camera': 'Camera',
        'file': 'File',
        'chart': 'Chart',
        'bell': 'Alerts',
        'refresh': 'Refresh',
        'clock': 'Time',
        'palette': 'Theme',
        
        'server': 'Server',
        'database': 'Database',
        'cpu': 'CPU',
        'memory': 'Memory',
        'warning': 'Warning',
        'error': 'Error',
        'success': 'Success',
        'info': 'Info',
        
        'folder': 'Folder',
        'download': 'Download',
        'upload': 'Upload',
        'save': 'Save',
        'print': 'Print',
        'search': 'Search',
    }
    
    @classmethod
    def get_icon(cls, icon_name, size=16, color=None):
        """
        Get a Font Awesome duotone icon or fallback to Unicode
        
        Args:
            icon_name (str): Icon identifier from ICONS dict
            size (int): Icon size in pixels
            color (str): Icon color (hex or color name)
            
        Returns:
            QIcon or None: Qt icon object or None if not available
        """
        if not ICONS_AVAILABLE:
            return None
            
        if icon_name not in cls.ICONS:
            return None
            
        try:
            icon_code = cls.ICONS[icon_name]
            if color:
                return qta.icon(icon_code, color=color)
            else:
                return qta.icon(icon_code)
        except Exception:
            return None
    
    @classmethod
    def get_fallback(cls, icon_name):
        """
        Get text fallback for an icon (no emojis)
        
        Args:
            icon_name (str): Icon identifier
            
        Returns:
            str: Text description or empty string
        """
        return cls.FALLBACKS.get(icon_name, '')
    
    @classmethod
    def set_button_icon(cls, button, icon_name, text=None, size=16, color=None):
        """
        Set icon on a button with fallback to text only (no emojis)
        
        Args:
            button: QPushButton object
            icon_name (str): Icon identifier
            text (str): Button text (optional)
            size (int): Icon size
            color (str): Icon color
        """
        icon = cls.get_icon(icon_name, size, color)
        if icon:
            button.setIcon(icon)
            if text:
                button.setText(text)
        else:
            # Fallback to text only (no emojis)
            if text:
                button.setText(text)
            else:
                fallback = cls.get_fallback(icon_name)
                button.setText(fallback)
    
    @classmethod
    def set_label_icon(cls, label, icon_name, text, color=None, size=16):
        """
        Set icon on a label with fallback to text only (no emojis)
        
        Args:
            label: QLabel object
            icon_name (str): Icon identifier  
            text (str): Label text
            color (str): Icon color
            size (int): Icon size
        """

        label.setText(text)