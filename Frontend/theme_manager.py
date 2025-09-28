# Theme Manager for CORA Application
# Manages light and dark theme color schemes

class ThemeManager:
    def __init__(self):
        self.current_theme = "light"  # default to light theme
        
        # Light theme colors - ONLY these 5 colors allowed
        self.light_theme = {
            'text': '#0e1513',
            'background': '#f3f7f6', 
            'primary': '#0c554a',
            'secondary': '#edbc2c',
            'accent': '#b3a58f'
        }
        
        # Dark theme colors - ONLY these 5 colors allowed
        self.dark_theme = {
            'text': '#eaf1ef',
            'background': '#080c0b',
            'primary': '#aaf3e8', 
            'secondary': '#d3a312',
            'accent': '#70634c'
        }
    
    def get_color(self, color_name, fallback=None):
        """Get a color value for the current theme - only returns the 5 approved theme colors"""
        theme = self.light_theme if self.current_theme == "light" else self.dark_theme
        
        # Map any non-standard color requests to our 5 approved colors
        color_mapping = {
            # All variations map to the base 5 colors
            'text_light': 'text',
            'text_lighter': 'text', 
            'text_dark': 'text',
            'background_light': 'background',
            'background_lighter': 'background',
            'background_dark': 'background',
            'background_darker': 'background',
            'primary_light': 'primary',
            'primary_lighter': 'primary',
            'primary_dark': 'primary',
            'secondary_light': 'secondary',
            'secondary_dark': 'secondary',
            'accent_light': 'accent',
            'accent_dark': 'accent',
            'accent_darker': 'accent',
            # Status colors map to theme colors
            'success': 'primary',
            'error': 'secondary', 
            'warning': 'secondary',
            'info': 'primary',
            'disabled': 'accent',
            'disabled_text': 'accent',
            'border': 'accent',
            'surface': 'background'
        }
        
        # Map the color name if needed
        mapped_color = color_mapping.get(color_name, color_name)
        
        # Return the mapped color or fallback to primary color
        return theme.get(mapped_color, theme.get('primary', '#0c554a'))
    
    def set_theme(self, theme_name):
        """Switch between 'light' and 'dark' themes"""
        if theme_name in ['light', 'dark']:
            self.current_theme = theme_name
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
    
    def get_stylesheet(self, component_type="default"):
        """Generate stylesheet strings for different UI components"""
        
        if component_type == "main_window":
            return f"""
                QMainWindow {{
                    background-color: {self.get_color('background')};
                    color: {self.get_color('text')};
                    font-family: 'Trebuchet MS', sans-serif;
                }}
            """
        
        elif component_type == "sidebar":
            return f"""
                QFrame#Sidebar {{
                    background-color: {self.get_color('primary')};
                }}
                QPushButton {{
                    background-color: {self.get_color('primary')};
                    color: {self.get_color('background')};
                    border-radius: 20px;
                    padding: 12px 20px;
                    font-weight: 500;
                    font-family: 'Trebuchet MS';
                }}
                QPushButton:hover {{
                    background-color: {self.get_color('secondary')};
                    color: {self.get_color('text')};
                }}
                QPushButton:pressed {{
                    background-color: {self.get_color('accent')};
                    color: {self.get_color('text')};
                }}
            """
        
        elif component_type == "card":
            return f"""
                QFrame#Card {{
                    background-color: {self.get_color('background_light') if self.current_theme == 'dark' else self.get_color('background')};
                    border: 1px solid {self.get_color('accent_light')};
                    border-radius: 16px;
                    padding: 20px;
                }}
                QFrame#Card:hover {{
                    border-color: {self.get_color('primary_light')};
                }}
            """
        
        elif component_type == "input":
            return f"""
                QLineEdit {{
                    background-color: {self.get_color('background_light') if self.current_theme == 'dark' else self.get_color('background')};
                    color: {self.get_color('text')};
                    border: 2px solid {self.get_color('accent_light')};
                    border-radius: 20px;
                    padding: 10px 15px;
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border-color: {self.get_color('primary')};
                }}
            """
        
        elif component_type == "button":
            return f"""
                QPushButton {{
                    background-color: {self.get_color('primary')};
                    color: {self.get_color('background')};
                    border: none;
                    border-radius: 20px;
                    padding: 12px 24px;
                    font-size: 15px;
                    font-weight: 500;
                    font-family: 'Trebuchet MS';
                }}
                QPushButton:hover {{
                    background-color: {self.get_color('secondary')};
                    color: {self.get_color('text')};
                }}
                QPushButton:pressed {{
                    background-color: {self.get_color('accent')};
                    color: {self.get_color('text')};
                }}
            """
        
        else:
            return f"""
                QWidget {{
                    background-color: {self.get_color('background')};
                    color: {self.get_color('text')};
                    font-family: 'Trebuchet MS';
                }}
                QLabel {{
                    color: {self.get_color('text')};
                    font-family: 'Trebuchet MS';
                }}
            """

# Global theme manager instance
theme_manager = ThemeManager()