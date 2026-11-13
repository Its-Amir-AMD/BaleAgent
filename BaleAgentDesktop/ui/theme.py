"""Scoped widget styling for the Spatial Liquid Glass visual system."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication
from .design_tokens import LIGHT, DARK


def stylesheet(dark: bool) -> str:
    p = DARK if dark else LIGHT
    text, muted, line = p["text"], p["muted"], p["line"]
    primary, primary_hover = p["primary"], p["primary_hover"]
    surface_soft = p["surface_soft"]

    if dark:
        field_bg = "rgba(14, 21, 37, 218)"
        popup_bg = "#202943"
        button_bg = "rgba(190, 202, 255, 20)"
        button_border = "rgba(219, 229, 255, 66)"
        hover_bg = "rgba(190, 204, 255, 48)"
        selected_bg = "rgba(190, 204, 255, 62)"
        menu_bg = "#1B243C"
        scrollbar = "rgba(197, 207, 239, 92)"
        list_bg = "rgba(13, 20, 35, 214)"
    else:
        field_bg = "rgba(255, 255, 255, 224)"
        popup_bg = "#F8F9FD"
        button_bg = "rgba(255, 255, 255, 126)"
        button_border = "rgba(255, 255, 255, 226)"
        hover_bg = "rgba(255, 255, 255, 192)"
        selected_bg = "rgba(196, 198, 244, 118)"
        menu_bg = "#F8F9FD"
        scrollbar = "rgba(112, 121, 151, 90)"
        list_bg = "rgba(255, 255, 255, 225)"

    return f"""
    * {{ font-family: 'Segoe UI', 'Vazirmatn', 'Tahoma'; font-size: 10pt; }}
    QWidget {{ color: {text}; background: transparent; outline: none; }}
    QMainWindow {{ background: {p['canvas']}; }}
    QDialog, QMessageBox {{ background: {p['surface']}; color: {text}; }}

    QLabel#Brand {{ font-size: 20pt; font-weight: 800; color: {text}; letter-spacing: 1px; }}
    QLabel#PageTitle {{ font-size: 21pt; font-weight: 760; color: {text}; }}
    QLabel#SectionTitle {{ font-size: 11pt; font-weight: 720; color: {text}; }}
    QLabel#Muted {{ color: {muted}; }}
    QLabel#Pill {{ background: {button_bg}; border: 1px solid {button_border}; color: {primary}; border-radius: 14px; padding: 6px 11px; font-weight: 650; }}
    QFrame#MessageIn, QFrame#MessageOut {{ background: transparent; border: 0; }}

    QPushButton {{
        background: {button_bg}; color: {text}; border: 1px solid {button_border};
        border-radius: 13px; padding: 9px 15px; font-weight: 620;
    }}
    QPushButton:hover {{ background: {hover_bg}; border-color: {primary}; }}
    QPushButton:pressed {{ background: {selected_bg}; padding-top: 10px; padding-bottom: 8px; }}
    QPushButton:disabled {{ color: {p['subtle']}; background: {surface_soft}; border-color: {line}; }}
    QPushButton#Primary {{ background: {primary}; border: 1px solid {primary}; color: {'#22243A' if dark else '#FFFFFF'}; font-weight: 760; }}
    QPushButton#Primary:hover {{ background: {primary_hover}; border-color: {primary_hover}; }}
    QPushButton#Secondary {{ background: {p['mint_soft']}; color: {p['mint']}; border: 1px solid {line}; }}
    QPushButton#Danger {{ background: {p['danger_soft']}; color: {p['danger']}; border: 1px solid {line}; }}
    QPushButton#Ghost {{ background: transparent; border-color: transparent; }}
    QPushButton#IconButton {{ padding: 0; border-radius: 14px; min-width: 40px; min-height: 40px; max-width: 40px; max-height: 40px; }}
    QPushButton#DockButton {{ background: transparent; border: 1px solid transparent; border-radius: 15px; padding: 4px; }}
    QPushButton#DockButton:hover {{ background: {hover_bg}; border-color: {line}; }}
    QPushButton#DockButton[active="true"] {{ background: {selected_bg}; border: 1px solid {button_border}; }}

    QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QComboBox, QSpinBox, QDateTimeEdit {{
        background: {field_bg}; color: {text}; border: 1px solid {button_border};
        border-radius: 13px; padding: 10px 12px; selection-background-color: {primary};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus {{
        border: 1px solid {primary}; background: {popup_bg};
    }}
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{ color: {p['subtle']}; }}
    QComboBox::drop-down {{ border: 0; width: 26px; }}
    QComboBox QAbstractItemView {{ background: {popup_bg}; color: {text}; border: 1px solid {line}; selection-background-color: {selected_bg}; padding: 5px; }}

    QListWidget {{ background: {list_bg}; color: {text}; border: 1px solid {button_border}; border-radius: 17px; padding: 7px; outline: none; }}
    QListWidget::item {{ padding: 12px 10px; border-radius: 11px; margin: 2px; }}
    QListWidget::item:hover {{ background: {hover_bg}; }}
    QListWidget::item:selected {{ background: {selected_bg}; border: 1px solid {line}; color: {text}; }}
    QGroupBox {{ background: {list_bg}; border: 1px solid {button_border}; border-radius: 17px; margin-top: 12px; padding: 14px; font-weight: 650; }}
    QGroupBox::title {{ subcontrol-origin: margin; right: 14px; padding: 0 6px; color: {muted}; }}

    QScrollArea, QAbstractScrollArea, QScrollArea::viewport, QAbstractScrollArea::viewport {{ background: transparent; border: 0; }}
    QSplitter {{ background: transparent; }}
    QSplitter::handle {{ background: {line}; width: 5px; height: 5px; border-radius: 2px; }}
    QScrollBar:vertical {{ background: transparent; width: 9px; margin: 4px 2px; }}
    QScrollBar::handle:vertical {{ background: {scrollbar}; border-radius: 4px; min-height: 28px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 9px; margin: 2px 4px; }}
    QScrollBar::handle:horizontal {{ background: {scrollbar}; border-radius: 4px; min-width: 28px; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    QCheckBox {{ spacing: 8px; color: {text}; }}
    QCheckBox::indicator {{ width: 17px; height: 17px; border-radius: 5px; border: 1px solid {line}; background: {field_bg}; }}
    QCheckBox::indicator:checked {{ background: {primary}; border-color: {primary}; }}
    QTabWidget::pane {{ background: {surface_soft}; border: 1px solid {line}; border-radius: 15px; top: -1px; }}
    QTabBar::tab {{ background: {button_bg}; color: {muted}; padding: 9px 16px; border: 1px solid {line}; border-top-left-radius: 11px; border-top-right-radius: 11px; margin-left: 3px; }}
    QTabBar::tab:selected {{ background: {selected_bg}; color: {text}; border-color: {primary}; }}
    QMenu {{ background: {menu_bg}; color: {text}; border: 1px solid {button_border}; border-radius: 14px; padding: 6px; }}
    QMenu::item {{ padding: 8px 22px; border-radius: 8px; }}
    QMenu::item:selected {{ background: {selected_bg}; }}
    QToolTip {{ background: {menu_bg}; color: {text}; border: 1px solid {button_border}; padding: 6px 8px; border-radius: 8px; }}
    QStatusBar {{ background: transparent; color: {muted}; border-top: 1px solid {line}; }}
    """


class ThemeManager:
    def __init__(self, app: QApplication):
        self.app = app

    def apply(self, dark: bool):
        self.app.setStyle("Fusion")
        self.app.setStyleSheet(stylesheet(dark))
