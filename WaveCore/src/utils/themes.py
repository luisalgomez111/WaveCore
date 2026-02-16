# Centralized Theme Tokens for WaveCore

THEMES = {
    "dark": {
        "bg_main": "#121212",
        "bg_secondary": "#1a1a1a",
        "bg_toolbar": "#1f1f1f",
        "bg_button": "#333333",
        "bg_button_hover": "#444444",
        "text_main": "#e0e0e0",
        "text_secondary": "#888888",
        "text_hover": "#cccccc",
        "accent": "#D75239",
        "border": "#2a2a2a",
        "border_focus": "#333333",
        "selection": "#D75239",
        "shadow": "rgba(0,0,0,0.5)"
    },
    "light": {
        "bg_main": "#F5F5F7",
        "bg_secondary": "#FFFFFF",
        "bg_toolbar": "#EBEBEB",
        "bg_button": "#D1D1D1",
        "bg_button_hover": "#BFBFBF",
        "text_main": "#1D1D1F",
        "text_secondary": "#636366",
        "text_hover": "#000000",
        "accent": "#D75239",
        "border": "#D2D2D7",
        "border_focus": "#C7C7CC",
        "selection": "#D75239",
        "shadow": "rgba(0,0,0,0.1)"
    }
}

class ThemeManager:
    def __init__(self, initial_theme="dark"):
        self.current_theme = initial_theme
        
    def set_theme(self, theme_name):
        if theme_name in THEMES:
            self.current_theme = theme_name
            
    def get(self, key):
        return THEMES[self.current_theme].get(key, "#FF00FF") # Fallback to magenta if key missing
