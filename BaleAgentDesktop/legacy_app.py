#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bale Agent Desktop — a PySide6 desktop interface for bale_agent.py."""
from __future__ import annotations

import asyncio
import html
import json
import os
import sys
import tempfile
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from PySide6.QtCore import Qt, QThread, Signal, QSize, QDateTime, QTimer, QPropertyAnimation, QVariantAnimation, QEasingCurve, QByteArray, QPointF, QRectF
from PySide6.QtGui import QFont, QAction, QIcon, QPixmap, QPainter, QColor, QBrush, QRadialGradient, QLinearGradient, QPen, QPainterPath
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton, QGraphicsDropShadowEffect,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QListWidget, QListWidgetItem,
    QTextEdit, QTextBrowser, QLineEdit, QPlainTextEdit, QFormLayout, QComboBox,
    QCheckBox, QMessageBox, QFileDialog, QInputDialog, QDialog,
    QDialogButtonBox, QSpinBox, QSplitter, QScrollArea, QGroupBox,
    QTabWidget, QSizePolicy, QDateTimeEdit, QMenu
)

from bale_agent import AgentConfig, BaleAgent, _chat_target, _mask_secret

APP_NAME = "Bale Agent Desktop"
APP_VERSION = "2.1.0"
ACCENT = "#78A6FF"

DARK_QSS = r"""
* { font-family: 'Segoe UI', 'Vazirmatn', sans-serif; font-size: 10pt; }
QWidget { color: #F3F2FA; background: transparent; }
QMainWindow, QWidget#AuthPage { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #171A2B, stop:0.48 #22243A, stop:1 #191D30); color: #F3F2FA; }
QWidget#Root, QWidget#Page { background: transparent; color: #F3F2FA; }
QDialog, QMessageBox { background: #24263C; color: #F3F2FA; }
QWidget#Root { border: 0; }
QWidget#RootStack, QStackedWidget, QSplitter, QSplitter::handle { background: transparent; }
QFrame#Glass, QFrame#Panel, QFrame#StatCard, QFrame#AuthCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(111,126,180,104), stop:0.22 rgba(67,77,124,126),
        stop:0.58 rgba(43,51,91,166), stop:1 rgba(113,104,154,96));
    border: 1px solid rgba(226,232,255,70);
    border-top-color: rgba(255,255,255,135);
    border-left-color: rgba(233,237,255,100);
    border-radius: 24px;
}
QFrame#Topbar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(122,136,191,116), stop:0.55 rgba(59,69,116,150), stop:1 rgba(112,104,151,104));
    border: 1px solid rgba(233,237,255,78); border-top-color: rgba(255,255,255,145);
    border-radius: 22px;
}
QFrame#Dock {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(119,132,189,202), stop:0.45 rgba(66,75,128,224), stop:1 rgba(96,86,143,210));
    border: 1px solid rgba(245,247,255,112); border-top-color: rgba(255,255,255,190);
    border-radius: 27px;
}
QFrame#AuthCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(135,148,205,122), stop:0.5 rgba(70,82,133,150), stop:1 rgba(130,108,158,105));
    border: 1px solid rgba(245,247,255,125); border-radius: 30px;
}
QLabel#Brand { font-size: 19pt; font-weight: 800; color: #FBF8FF; letter-spacing: 1px; }
QLabel#Muted { color: #B4B4CA; }
QLabel#PageTitle { font-size: 21pt; font-weight: 760; color: #FBF8FF; }
QLabel#SectionTitle { font-size: 11pt; font-weight: 720; color: #F0EDFC; }
QLabel#AuthTitle { font-size: 25pt; font-weight: 800; color: #FCFAFF; }
QLabel#AuthSubtitle { color: #C7C5D8; font-size: 10.5pt; }
QLabel#Pill { background: rgba(164,174,232,28); border: 1px solid rgba(184,192,246,55); color: #D9DDFF; border-radius: 12px; padding: 6px 11px; }
QPushButton { background: rgba(255,255,255,17); color: #F2F0FA; border: 1px solid rgba(255,255,255,38); border-radius: 13px; padding: 10px 15px; }
QPushButton:hover { background: rgba(255,255,255,27); border-color: rgba(209,211,255,89); }
QPushButton:pressed { background: rgba(255,255,255,11); }
QPushButton:disabled { color: #77788C; background: rgba(255,255,255,7); border-color: rgba(255,255,255,14); }
QPushButton#Primary { background: rgba(151,160,229,61); border: 1px solid rgba(190,195,255,120); color: #FFFFFF; font-weight: 750; }
QPushButton#Primary:hover { background: rgba(163,172,241,85); border-color: rgba(218,219,255,180); }
QPushButton#Secondary { background: rgba(128,193,174,25); border: 1px solid rgba(150,221,198,60); color: #C7F2E2; }
QPushButton#Danger { background: rgba(204,111,139,29); border-color: rgba(227,145,168,70); color: #FFD7E2; }
QPushButton#DockButton { background: transparent; border: 1px solid transparent; border-radius: 15px; padding: 5px; }
QPushButton#DockButton:hover { background: rgba(255,255,255,22); border-color: rgba(255,255,255,37); }
QPushButton#DockButton[active="true"] { background: rgba(169,177,245,34); border: 1px solid rgba(198,201,255,75); }
QLineEdit, QTextEdit, QTextBrowser, QPlainTextEdit, QComboBox, QSpinBox, QDateTimeEdit { background: rgba(15,17,30,112); color: #F1EFFA; border: 1px solid rgba(255,255,255,48); border-radius: 13px; padding: 11px 13px; selection-background-color: rgba(161,169,238,150); }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus { border-color: rgba(190,194,255,175); background: rgba(26,28,47,195); }
QComboBox QAbstractItemView { background: #292B42; color: #F3F2FA; border: 1px solid #555875; selection-background-color: #555C91; }
QListWidget { background: rgba(17,19,32,67); border: 1px solid rgba(255,255,255,30); border-radius: 18px; padding: 7px; outline: 0; }
QListWidget::item { padding: 13px 11px; border-radius: 11px; color: #E3E1F1; }
QListWidget::item:selected { background: rgba(151,160,229,48); color: white; border: 1px solid rgba(193,197,255,79); }
QListWidget::item:hover { background: rgba(255,255,255,16); }
QGroupBox { background: rgba(255,255,255,12); border: 1px solid rgba(255,255,255,30); border-radius: 18px; margin-top: 13px; padding: 14px; font-weight: 650; }
QGroupBox::title { subcontrol-origin: margin; right: 14px; padding: 0 6px; color: #C9C7DC; }
QFrame#MessageIn { background: rgba(255,255,255,17); border: 1px solid rgba(255,255,255,32); border-radius: 16px; }
QFrame#MessageOut { background: rgba(161,169,238,32); border: 1px solid rgba(186,191,255,58); border-radius: 16px; }
QScrollArea, QAbstractScrollArea { border: none; background: transparent; }
QScrollArea::viewport, QAbstractScrollArea::viewport, QWidget#ScrollContent { background: transparent; border: none; }
QScrollArea#SettingsScroll, QWidget#SettingsContent, QWidget#SettingsViewport { background: transparent; border: 0; }
QPlainTextEdit, QTextEdit { background: rgba(19,22,39,145); }
QLineEdit, QComboBox, QSpinBox, QDateTimeEdit { background: rgba(19,22,39,145); }
QSplitter::handle { background: rgba(255,255,255,27); width: 5px; height: 5px; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 3px; }
QScrollBar::handle:vertical { background: rgba(206,207,233,72); border-radius: 4px; min-height: 26px; }
QScrollBar::handle:vertical:hover { background: rgba(206,207,233,118); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 9px; margin: 3px; }
QScrollBar::handle:horizontal { background: rgba(206,207,233,72); border-radius: 4px; min-width: 26px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QCheckBox { spacing: 8px; color: #D7D5E7; }
QCheckBox::indicator { width: 17px; height: 17px; }
QTabWidget::pane { background: rgba(255,255,255,9); border: 1px solid rgba(255,255,255,31); border-radius: 15px; top: -1px; }
QTabBar::tab { background: rgba(255,255,255,11); color: #B8B6CD; padding: 10px 17px; border: 1px solid rgba(255,255,255,26); border-top-left-radius: 10px; border-top-right-radius: 10px; }
QTabBar::tab:selected { background: rgba(161,169,238,40); color: white; border-color: rgba(193,197,255,69); }
QStatusBar { background: rgba(255,255,255,8); color: #AFAFC5; border-top: 1px solid rgba(255,255,255,19); }
QMenu { background: #292B42; color: #F3F2FA; border: 1px solid rgba(255,255,255,41); padding: 6px; }
QMenu::item { padding: 8px 24px; border-radius: 7px; }
QMenu::item:selected { background: rgba(161,169,238,58); }
QToolTip { background: #292B42; color: #F4F2FF; border: 1px solid #686A91; padding: 6px; }
"""

LIGHT_QSS = r"""
* { font-family: 'Segoe UI', 'Vazirmatn', sans-serif; font-size: 10pt; }
QWidget { color: #343850; background: transparent; }
QMainWindow, QWidget#AuthPage { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F1F1F9, stop:0.5 #E9EEF7, stop:1 #F7EDF2); color: #293047; }
QWidget#Root, QWidget#Page { background: transparent; color: #293047; }
QDialog, QMessageBox { background: #F0F1F8; color: #343850; }
QWidget#Root { border: 0; }
QWidget#RootStack, QStackedWidget, QSplitter, QSplitter::handle { background: transparent; }
QFrame#Glass, QFrame#Panel, QFrame#StatCard, QFrame#AuthCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,182), stop:0.20 rgba(238,243,255,158),
        stop:0.58 rgba(220,229,250,142), stop:1 rgba(248,226,238,142));
    border: 1px solid rgba(255,255,255,245); border-top-color: #FFFFFF;
    border-left-color: rgba(255,255,255,255); border-radius: 24px;
}
QFrame#Topbar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,205), stop:0.5 rgba(225,234,251,180), stop:1 rgba(246,225,239,165));
    border: 1px solid rgba(255,255,255,255); border-top-color: #FFFFFF; border-radius: 22px;
}
QFrame#Dock {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,230), stop:0.48 rgba(226,232,250,218), stop:1 rgba(244,225,239,214));
    border: 1px solid #FFFFFF; border-top-color: #FFFFFF; border-radius: 27px;
}
QFrame#AuthCard { border-radius: 30px; }
QLabel#Brand { font-size: 19pt; font-weight: 800; color: #353653; letter-spacing: 1px; }
QLabel#Muted { color: #777D94; }
QLabel#PageTitle { font-size: 21pt; font-weight: 760; color: #30334F; }
QLabel#SectionTitle { font-size: 11pt; font-weight: 720; color: #3B3D5B; }
QLabel#AuthTitle { font-size: 25pt; font-weight: 800; color: #343653; }
QLabel#AuthSubtitle { color: #747992; font-size: 10.5pt; }
QLabel#Pill { background: rgba(147,155,226,31); border: 1px solid rgba(147,155,226,73); color: #656DAE; border-radius: 12px; padding: 6px 11px; }
QPushButton { background: rgba(255,255,255,183); color: #414660; border: 1px solid rgba(255,255,255,250); border-radius: 13px; padding: 10px 15px; }
QPushButton:hover { background: rgba(255,255,255,245); border-color: #CDD0E8; }
QPushButton:pressed { background: #E9EAF4; }
QPushButton:disabled { color: #A4A8B8; background: rgba(255,255,255,105); }
QPushButton#Primary { background: rgba(143,151,224,49); border: 1px solid rgba(142,151,222,104); color: #50598F; font-weight: 750; }
QPushButton#Primary:hover { background: rgba(143,151,224,73); border-color: #A3A9E8; }
QPushButton#Secondary { background: rgba(130,194,174,42); border: 1px solid rgba(121,183,160,95); color: #397B67; }
QPushButton#Danger { background: rgba(244,213,222,190); border-color: #E8C2CD; color: #A5556B; }
QPushButton#DockButton { background: transparent; border: 1px solid transparent; border-radius: 15px; padding: 5px; }
QPushButton#DockButton:hover { background: rgba(145,153,223,24); border-color: rgba(145,153,223,59); }
QPushButton#DockButton[active="true"] { background: rgba(145,153,223,34); border: 1px solid rgba(145,153,223,91); }
QLineEdit, QTextEdit, QTextBrowser, QPlainTextEdit, QComboBox, QSpinBox, QDateTimeEdit { background: rgba(255,255,255,205); color: #343850; border: 1px solid rgba(255,255,255,253); border-radius: 13px; padding: 11px 13px; selection-background-color: #DADDF6; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus { border-color: #A9AFE2; background: #FFFFFF; }
QComboBox QAbstractItemView { background: #FFFFFF; color: #343850; border: 1px solid #D9DCEE; selection-background-color: #E8E9FA; }
QListWidget { background: rgba(255,255,255,112); border: 1px solid rgba(255,255,255,248); border-radius: 18px; padding: 7px; outline: 0; }
QListWidget::item { padding: 13px 11px; border-radius: 11px; color: #464A65; }
QListWidget::item:selected { background: rgba(145,153,223,43); color: #464E8A; border: 1px solid rgba(145,153,223,79); }
QListWidget::item:hover { background: rgba(255,255,255,210); }
QGroupBox { background: rgba(255,255,255,134); border: 1px solid rgba(255,255,255,245); border-radius: 18px; margin-top: 13px; padding: 14px; font-weight: 650; }
QGroupBox::title { subcontrol-origin: margin; right: 14px; padding: 0 6px; color: #7A8097; }
QFrame#MessageIn { background: rgba(255,255,255,223); border: 1px solid rgba(255,255,255,255); border-radius: 16px; }
QFrame#MessageOut { background: rgba(158,166,235,43); border: 1px solid rgba(145,153,223,85); border-radius: 16px; }
QScrollArea, QAbstractScrollArea { border: none; background: transparent; }
QScrollArea::viewport, QAbstractScrollArea::viewport, QWidget#ScrollContent { background: transparent; border: none; }
QScrollArea#SettingsScroll, QWidget#SettingsContent, QWidget#SettingsViewport { background: transparent; border: 0; }
QPlainTextEdit, QTextEdit { background: rgba(255,255,255,166); }
QLineEdit, QComboBox, QSpinBox, QDateTimeEdit { background: rgba(255,255,255,178); }
QSplitter::handle { background: rgba(111,119,155,28); width: 5px; height: 5px; }
QScrollBar:vertical { background: transparent; width: 9px; margin: 3px; }
QScrollBar::handle:vertical { background: rgba(111,119,155,69); border-radius: 4px; min-height: 26px; }
QScrollBar::handle:vertical:hover { background: rgba(111,119,155,112); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 9px; margin: 3px; }
QScrollBar::handle:horizontal { background: rgba(111,119,155,69); border-radius: 4px; min-width: 26px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QCheckBox { spacing: 8px; color: #596079; }
QCheckBox::indicator { width: 17px; height: 17px; }
QTabWidget::pane { background: rgba(255,255,255,122); border: 1px solid rgba(255,255,255,242); border-radius: 15px; top: -1px; }
QTabBar::tab { background: rgba(255,255,255,153); color: #777D94; padding: 10px 17px; border: 1px solid rgba(255,255,255,237); border-top-left-radius: 10px; border-top-right-radius: 10px; }
QTabBar::tab:selected { background: rgba(145,153,223,44); color: #50598F; border-color: rgba(145,153,223,85); }
QStatusBar { background: rgba(255,255,255,112); color: #7C8298; border-top: 1px solid rgba(255,255,255,230); }
QMenu { background: #FFFFFF; color: #3F435E; border: 1px solid #D8DCEE; padding: 6px; }
QMenu::item { padding: 8px 24px; border-radius: 7px; }
QMenu::item:selected { background: #E8E9FA; }
QToolTip { background: #FFFFFF; color: #3F435E; border: 1px solid #D8DCEE; padding: 6px; }
"""


class AsyncWorker(QThread):
    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, task: Callable[[], Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.task = task

    def run(self) -> None:
        try:
            result = asyncio.run(self.task())
            self.succeeded.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class LoginWorker(QThread):
    input_required = Signal(str)
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, session: str, phone: str):
        super().__init__()
        self.session = session
        self.phone = phone
        self._event = threading.Event()
        self._value = ""

    def provide_input(self, value: str) -> None:
        self._value = value
        self._event.set()

    def _ask(self, prompt: str) -> str:
        self._event.clear()
        self.input_required.emit(prompt)
        if not self._event.wait(300):
            raise RuntimeError("مهلت دریافت کد ورود تمام شد.")
        if not self._value:
            raise RuntimeError("فرآیند ورود لغو شد.")
        return self._value

    def run(self) -> None:
        try:
            async def do_login() -> str:
                try:
                    from balelink import BaleClient
                except ImportError as exc:
                    raise RuntimeError("کتابخانه balelink نصب نیست. ابتدا requirements را نصب کنید.") from exc
                client = BaleClient(self.session)
                if client.is_logged_in:
                    return "این نشست از قبل وارد حساب شده است."
                me = await client.login(
                    self.phone,
                    code=lambda: self._ask("کد تأیید ارسال‌شده از طرف بله را وارد کنید:"),
                    password=lambda: self._ask("رمز دومرحله‌ای (در صورت درخواست):"),
                )
                # balelink persists the session during sign_in(); verify the
                # saved file exists before handing control back to the GUI.
                if not client.is_logged_in:
                    raise RuntimeError(
                        "کد ورود پذیرفته شد، اما نشست ذخیره‌شده پیدا نشد. ورود را دوباره انجام بده."
                    )
                client.store.secure(self.session)
                return "ورود موفق بود. شناسه حساب: %s" % me.id
            self.succeeded.emit(asyncio.run(do_login()))
        except Exception as exc:
            self.failed.emit(str(exc))


SVG_PATHS = {
    "dashboard": '<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="5" rx="2"/><rect x="13" y="10" width="8" height="11" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/>',
    "chats": '<path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-5.5A7.5 7.5 0 1 1 20 11.5Z"/><path d="M8 10h8M8 14h5"/>',
    "assistant": '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z"/>',
    "automation": '<path d="M12 3v3M12 18v3M3 12h3M18 12h3"/><circle cx="12" cy="12" r="5"/><path d="m9.5 12 1.7 1.7 3.4-3.4"/>',
    "schedule": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2M8 2v2M16 2v2"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1a1.7 1.7 0 0 1-2.4 2.4l-.1-.1a1.7 1.7 0 0 0-2.9 1.2v.2a1.7 1.7 0 0 1-3.4 0v-.2A1.7 1.7 0 0 0 8 17.4l-.1.1a1.7 1.7 0 1 1-2.4-2.4l.1-.1a1.7 1.7 0 0 0-1.2-2.9h-.2a1.7 1.7 0 0 1 0-3.4h.2A1.7 1.7 0 0 0 5.6 6l-.1-.1a1.7 1.7 0 1 1 2.4-2.4l.1.1a1.7 1.7 0 0 0 2.9-1.2v-.2a1.7 1.7 0 0 1 3.4 0v.2A1.7 1.7 0 0 0 17.2 4l.1-.1a1.7 1.7 0 1 1 2.4 2.4l-.1.1a1.7 1.7 0 0 0 1.2 2.9h.2a1.7 1.7 0 0 1 0 3.4h-.2a1.7 1.7 0 0 0-1.4 2.3Z"/>',
    "refresh": '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M5.6 9A7 7 0 0 1 18 6.5L20 8M4 16l2 1.5A7 7 0 0 0 18.4 15"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20.5 14A8.5 8.5 0 0 1 10 3.5 8.5 8.5 0 1 0 20.5 14Z"/>',
    "cloud": '<path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 9a4.5 4.5 0 0 0 1 9Z"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9a2.5 2.5 0 1 1 4.2 1.8c-1.1 1-1.8 1.4-1.8 3M12 17.5h.01"/>',
}


def svg_icon(name: str, color: str = "#8E98D8") -> QIcon:
    body = SVG_PATHS.get(name, SVG_PATHS["dashboard"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" '
           f'fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(72, 72)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


class AmbientRoot(QWidget):
    """Paint a soft pastel ambient backdrop under translucent glass surfaces."""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._dark = False
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

    def set_dark_mode(self, enabled: bool):
        self._dark = bool(enabled)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        bounds = self.rect()
        if self._dark:
            base = QColor("#17192A")
            blobs = [
                (0.10, 0.06, 0.78, "#A5AEFF", 74),
                (0.91, 0.48, 0.65, "#83D8C2", 52),
                (0.34, 0.98, 0.62, "#DDA8C5", 45),
                (0.72, 0.04, 0.42, "#A9CFF4", 30),
                (0.50, 0.50, 0.52, "#C7B5F0", 24),
            ]
        else:
            base = QColor("#EEF0F8")
            blobs = [
                (0.10, 0.06, 0.78, "#A9B5F2", 124),
                (0.91, 0.48, 0.65, "#91D9C4", 100),
                (0.34, 0.98, 0.62, "#E8B9CE", 88),
                (0.72, 0.04, 0.42, "#A9D4F0", 66),
                (0.50, 0.50, 0.52, "#D2C1F3", 45),
            ]
        painter.fillRect(bounds, base)
        radius_base = max(bounds.width(), bounds.height())
        for x_ratio, y_ratio, scale, color, alpha in blobs:
            gradient = QRadialGradient(
                QPointF(bounds.width() * x_ratio, bounds.height() * y_ratio),
                max(1.0, radius_base * scale),
            )
            center = QColor(color)
            center.setAlpha(alpha)
            edge = QColor(color)
            edge.setAlpha(0)
            gradient.setColorAt(0.0, center)
            gradient.setColorAt(1.0, edge)
            painter.fillRect(bounds, QBrush(gradient))
        # A faint diagonal veil creates the soft, milky depth behind the glass.
        veil = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
        if self._dark:
            veil.setColorAt(0.0, QColor(255, 255, 255, 8))
            veil.setColorAt(0.48, QColor(150, 162, 230, 5))
            veil.setColorAt(1.0, QColor(12, 15, 29, 20))
        else:
            veil.setColorAt(0.0, QColor(255, 255, 255, 27))
            veil.setColorAt(0.48, QColor(255, 255, 255, 7))
            veil.setColorAt(1.0, QColor(151, 161, 211, 18))
        painter.fillRect(bounds, QBrush(veil))
        painter.end()


class SpatialGlassFrame(QFrame):
    """A layered Liquid Glass surface with a specular rim and mouse-responsive lift.

    Qt cannot sample and blur arbitrary sibling widgets as a true compositor would.
    The soft ambient backdrop, translucent layered fill, rim lighting and animated
    elevation approximate the spatial/visionOS treatment without platform APIs.
    """
    def __init__(self, parent: Optional[QWidget] = None, radius: float = 24.0):
        super().__init__(parent)
        self._radius = float(radius)
        self._lift = 0.0
        self._shine = -0.5
        self._dark = False
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 7)
        shadow.setColor(QColor(69, 78, 125, 38))
        self.setGraphicsEffect(shadow)
        self._shadow = shadow

        self._lift_anim = QVariantAnimation(self)
        self._lift_anim.setDuration(210)
        self._lift_anim.setStartValue(0.0)
        self._lift_anim.setEndValue(1.0)
        self._lift_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._lift_anim.valueChanged.connect(self._set_lift)

        self._shine_anim = QVariantAnimation(self)
        self._shine_anim.setDuration(620)
        self._shine_anim.setStartValue(-0.35)
        self._shine_anim.setEndValue(1.35)
        self._shine_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._shine_anim.valueChanged.connect(self._set_shine)

    def set_dark_mode(self, enabled: bool):
        self._dark = bool(enabled)
        self._update_shadow()
        self.update()

    def _set_lift(self, value):
        self._lift = float(value)
        self._update_shadow()
        self.update()

    def _set_shine(self, value):
        self._shine = float(value)
        self.update()

    def _update_shadow(self):
        if self._dark:
            color = QColor(4, 7, 22, int(72 + self._lift * 36))
        else:
            color = QColor(94, 103, 157, int(35 + self._lift * 28))
        self._shadow.setColor(color)
        self._shadow.setBlurRadius(18 + self._lift * 25)
        self._shadow.setOffset(0, 6 + self._lift * 8)

    def enterEvent(self, event):
        self._lift_anim.stop()
        self._lift_anim.setStartValue(self._lift)
        self._lift_anim.setEndValue(1.0)
        self._lift_anim.start()
        self._shine_anim.stop()
        self._shine_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._lift_anim.stop()
        self._lift_anim.setStartValue(self._lift)
        self._lift_anim.setEndValue(0.0)
        self._lift_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        bounds = QRectF(self.rect()).adjusted(1.1, 1.1, -1.1, -1.1)
        path = QPainterPath()
        path.addRoundedRect(bounds, self._radius, self._radius)
        painter.setBrush(Qt.NoBrush)

        # Static pearly rim: brightest on the upper/leading edge, softer below.
        rim = QLinearGradient(bounds.topLeft(), bounds.bottomRight())
        if self._dark:
            rim.setColorAt(0.0, QColor(255, 255, 255, 150))
            rim.setColorAt(0.34, QColor(210, 222, 255, 76))
            rim.setColorAt(0.72, QColor(179, 190, 236, 35))
            rim.setColorAt(1.0, QColor(255, 255, 255, 88))
        else:
            rim.setColorAt(0.0, QColor(255, 255, 255, 245))
            rim.setColorAt(0.36, QColor(255, 255, 255, 138))
            rim.setColorAt(0.72, QColor(154, 166, 213, 72))
            rim.setColorAt(1.0, QColor(255, 255, 255, 190))
        painter.setPen(QPen(rim, 1.25 + self._lift * 0.45))
        painter.drawPath(path)

        # Moving specular streak that travels around the glass rim on hover.
        sweep = QLinearGradient(
            bounds.left() + (self._shine - 0.28) * bounds.width(), bounds.top(),
            bounds.left() + (self._shine + 0.28) * bounds.width(), bounds.bottom(),
        )
        sweep.setColorAt(0.0, QColor(255, 255, 255, 0))
        sweep.setColorAt(0.5, QColor(255, 255, 255, 165 if self._dark else 225))
        sweep.setColorAt(1.0, QColor(222, 232, 255, 0))
        painter.setPen(QPen(sweep, 1.6 + self._lift * 0.5))
        painter.drawPath(path)

        # Fine inner hairline gives the panel a thicker, refractive glass edge.
        inner = bounds.adjusted(2.2, 2.2, -2.2, -2.2)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(inner, max(4.0, self._radius - 2.0), max(4.0, self._radius - 2.0))
        inner_color = QColor(255, 255, 255, 33 if self._dark else 112)
        painter.setPen(QPen(inner_color, 0.7))
        painter.drawPath(inner_path)
        painter.end()


class DockButton(QPushButton):
    """Taskbar button with a subtle mouse-responsive SVG icon zoom."""
    def __init__(self, key: str, tooltip: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.key = key
        self.setObjectName("DockButton")
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(58, 56)
        self.setIconSize(QSize(23, 23))
        self._icon_animation = QPropertyAnimation(self, b"iconSize", self)
        self._icon_animation.setDuration(155)
        self._icon_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setMouseTracking(True)

    def _animate_icon(self, target: QSize):
        self._icon_animation.stop()
        self._icon_animation.setStartValue(self.iconSize())
        self._icon_animation.setEndValue(target)
        self._icon_animation.start()

    def enterEvent(self, event):
        self._animate_icon(QSize(30, 30))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_icon(QSize(23, 23))
        super().leaveEvent(event)


class AddRuleDialog(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("ساخت قانون پاسخ")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name = QLineEdit()
        self.keywords = QLineEdit()
        self.reply = QTextEdit()
        self.reply.setFixedHeight(110)
        self.senders = QLineEdit()
        self.senders.setPlaceholderText("اختیاری؛ شناسه‌ها با کاما جدا شوند")
        form.addRow("نام قانون", self.name)
        form.addRow("کلمات کلیدی", self.keywords)
        form.addRow("متن پاسخ", self.reply)
        form.addRow("شناسه مخاطبان", self.senders)
        layout.addLayout(form)
        hint = QLabel("کلمات کلیدی را با کاما جدا کنید. قانون فقط پاسخ پیشنهادی تولید می‌کند.")
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self):
        return self.name.text().strip(), [x.strip() for x in self.keywords.text().split(",") if x.strip()], self.reply.toPlainText().strip(), [x.strip() for x in self.senders.text().split(",") if x.strip()]


class ScheduleMessageDialog(QDialog):
    def __init__(self, chat_label: str, initial_text: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("زمان‌بندی پیام")
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        title = QLabel("ارسال زمان‌بندی‌شده")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        info = QLabel("مقصد: %s\nبرای اجرای زمان‌بندی، برنامه باید باز باشد. در زمان مقرر، پیش از ارسال از شما تأیید گرفته می‌شود." % chat_label)
        info.setObjectName("Muted")
        info.setWordWrap(True)
        layout.addWidget(info)
        self.text = QPlainTextEdit()
        self.text.setPlaceholderText("متن پیام زمان‌بندی‌شده…")
        self.text.setPlainText(initial_text)
        self.text.setMinimumHeight(130)
        layout.addWidget(self.text)
        form = QFormLayout()
        self.when = QDateTimeEdit(QDateTime.currentDateTime().addSecs(300))
        self.when.setCalendarPopup(True)
        self.when.setDisplayFormat("yyyy/MM/dd  HH:mm")
        self.when.setMinimumDateTime(QDateTime.currentDateTime().addSecs(30))
        form.addRow("زمان ارسال", self.when)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("ذخیره زمان‌بندی")
        buttons.button(QDialogButtonBox.Cancel).setText("انصراف")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.text.toPlainText().strip():
            QMessageBox.information(self, "متن پیام", "متن پیام را وارد کنید.")
            return
        if self.when.dateTime().toSecsSinceEpoch() <= QDateTime.currentDateTime().addSecs(20).toSecsSinceEpoch():
            QMessageBox.information(self, "زمان نامعتبر", "زمان ارسال باید دست‌کم ۲۰ ثانیه در آینده باشد.")
            return
        self.accept()

    def values(self):
        return self.text.toPlainText().strip(), int(self.when.dateTime().toSecsSinceEpoch())


class LegacyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.home = Path.home() / ".bale-agent"
        self.session = "agent"
        self.setWindowTitle(APP_NAME + "  ·  " + APP_VERSION)
        self.setMinimumSize(1040, 700)
        self.resize(1280, 840)
        self._stat_index = 0
        self.config = AgentConfig(self.home)
        self.app_state_path = self.home / "desktop_state.json"
        self.app_state = self._load_app_state()
        self.workers: list[QThread] = []
        self.worker_callbacks: dict[QThread, tuple[Callable[[Any], None], Optional[Callable[[str], None]]]] = {}
        self.active_login_worker: Optional[LoginWorker] = None
        self.current_chat: Optional[dict[str, Any]] = None
        self.current_messages: list[dict[str, Any]] = []
        self.message_row_widgets: list[tuple[QWidget, dict[str, Any]]] = []
        self.dialogs_cache: list[dict[str, Any]] = []
        self.ai_conversation: list[dict[str, str]] = []
        self.dark_mode = self.app_state.get("theme", "light") == "dark"
        self.nav_buttons: dict[str, DockButton] = {}
        self._authenticated = False
        self._auth_check_in_progress = False
        self._build_shell()
        self.apply_theme()
        self.refresh_local_overview()
        self.refresh_schedule_list()
        self.schedule_timer = QTimer(self)
        self.schedule_timer.setInterval(10000)
        self.schedule_timer.timeout.connect(self.check_scheduled_messages)
        # Do not start a network check during window construction.  The previous
        # automatic check disabled every auth control while the worker waited for
        # Bale, making the login page look interactive but leaving its buttons
        # unusable when the connection attempt stalled.  Keep the first screen
        # immediately actionable; saved-session validation is user-triggered.
        self._set_auth_status(
            "برای ورود، شماره موبایل را وارد کن یا نشست ذخیره‌شده را بررسی کن.",
            "waiting",
        )

    def _build_auth_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("AuthPage")
        page.setLayoutDirection(Qt.RightToLeft)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.addStretch(1)

        card = SpatialGlassFrame(radius=30)
        card.setObjectName("AuthCard")
        card.setMaximumWidth(590)
        card.setMinimumWidth(470)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(38, 34, 38, 34)
        card_layout.setSpacing(16)

        brand_row = QHBoxLayout()
        brand_mark = QLabel()
        brand_mark.setFixedSize(54, 54)
        brand_mark.setAlignment(Qt.AlignCenter)
        brand_mark.setStyleSheet("background:rgba(148,158,229,34); border:1px solid rgba(159,169,239,90); border-radius:18px;")
        brand_mark.setPixmap(svg_icon("chats", "#98A4E8").pixmap(34, 34))
        brand_row.addWidget(brand_mark)
        brand_col = QVBoxLayout()
        brand = QLabel("BALE AGENT")
        brand.setObjectName("Brand")
        brand_col.addWidget(brand)
        version = QLabel("DESKTOP COMPANION  ·  " + APP_VERSION)
        version.setObjectName("Muted")
        version.setStyleSheet("font-size:8pt; letter-spacing:1.2px;")
        brand_col.addWidget(version)
        brand_row.addLayout(brand_col)
        brand_row.addStretch(1)
        self.auth_pill = QLabel("اتصال لازم است")
        self.auth_pill.setObjectName("Pill")
        brand_row.addWidget(self.auth_pill, alignment=Qt.AlignVCenter)
        card_layout.addLayout(brand_row)

        title = QLabel("اول به بله متصل شو")
        title.setObjectName("AuthTitle")
        card_layout.addWidget(title)
        subtitle = QLabel("برای حفظ امنیت، محیط اصلی برنامه تا زمان تأیید اتصال حساب در دسترس نخواهد بود.")
        subtitle.setObjectName("AuthSubtitle")
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        self.auth_status_card = SpatialGlassFrame(radius=18)
        self.auth_status_card.setObjectName("Glass")
        status_layout = QHBoxLayout(self.auth_status_card)
        status_layout.setContentsMargins(14, 12, 14, 12)
        self.auth_status_dot = QLabel("●")
        self.auth_status_dot.setStyleSheet("color:#D9B96F; font-size:15pt;")
        status_layout.addWidget(self.auth_status_dot)
        self.auth_status_label = QLabel("در حال بررسی نشست ذخیره‌شده…")
        self.auth_status_label.setObjectName("SectionTitle")
        self.auth_status_label.setWordWrap(True)
        status_layout.addWidget(self.auth_status_label, 1)
        card_layout.addWidget(self.auth_status_card)

        phone_label = QLabel("شماره موبایل")
        phone_label.setObjectName("SectionTitle")
        card_layout.addWidget(phone_label)
        self.auth_phone_input = QLineEdit()
        self.auth_phone_input.setPlaceholderText("مثلاً 09xxxxxxxxx یا +98...")
        self.auth_phone_input.setLayoutDirection(Qt.LeftToRight)
        self.auth_phone_input.setMinimumHeight(48)
        self.auth_phone_input.returnPressed.connect(self.start_login)
        card_layout.addWidget(self.auth_phone_input)

        self.auth_login_button = QPushButton("ورود و اتصال به بله")
        self.auth_login_button.setObjectName("Primary")
        self.auth_login_button.setMinimumHeight(48)
        self.auth_login_button.clicked.connect(self.start_login)
        card_layout.addWidget(self.auth_login_button)

        self.auth_check_button = QPushButton("بررسی اتصال نشست ذخیره‌شده")
        self.auth_check_button.setMinimumHeight(44)
        self.auth_check_button.clicked.connect(lambda: self._check_saved_session(automatic=False))
        card_layout.addWidget(self.auth_check_button)

        self.auth_fresh_button = QPushButton("ورود با نشست تازه؛ برای نشست قبلیِ مشکل‌دار")
        self.auth_fresh_button.setObjectName("Secondary")
        self.auth_fresh_button.setMinimumHeight(40)
        self.auth_fresh_button.clicked.connect(self.start_fresh_session)
        card_layout.addWidget(self.auth_fresh_button)

        warning = QLabel(
            "نکته امنیتی: این پروژه از کتابخانه غیررسمی balelink استفاده می‌کند. "
            "پروتکل آن رسمی نیست و ممکن است با محدودیت حساب همراه باشد. قبل از ادامه، این ریسک را در نظر بگیر."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color:#B88D73; background:rgba(221,177,139,18); border:1px solid rgba(221,177,139,42); border-radius:14px; padding:11px;")
        card_layout.addWidget(warning)

        hint = QLabel("اطلاعات نشست فقط روی همین دستگاه ذخیره می‌شود. کد تأیید و رمز دومرحله‌ای را در اختیار دیگران قرار نده.")
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        hint.setStyleSheet("font-size:9pt;")
        card_layout.addWidget(hint)

        center = QHBoxLayout()
        center.addStretch(1)
        center.addWidget(card)
        center.addStretch(1)
        outer.addLayout(center)
        outer.addStretch(1)

        footer = QLabel("BALE AGENT  /  PRIVATE DESKTOP WORKSPACE")
        footer.setObjectName("Muted")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size:8pt; letter-spacing:1.3px;")
        outer.addWidget(footer)
        return page

    def _build_shell(self):
        self.root_stack = QStackedWidget()
        self.root_stack.setObjectName("RootStack")
        self.auth_page = self._build_auth_page()
        self.root_stack.addWidget(self.auth_page)

        app_shell = AmbientRoot()
        app_shell.setObjectName("Root")
        app_shell.setLayoutDirection(Qt.RightToLeft)
        app_layout = QVBoxLayout(app_shell)
        app_layout.setContentsMargins(15, 14, 15, 12)
        app_layout.setSpacing(12)

        topbar = SpatialGlassFrame(radius=22)
        topbar.setObjectName("Topbar")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(22, 11, 18, 11)
        top_layout.setSpacing(11)
        title_stack = QVBoxLayout()
        title_stack.setSpacing(1)
        self.top_title = QLabel("نمای کلی")
        self.top_title.setObjectName("SectionTitle")
        self.top_title.setStyleSheet("font-size:13pt; font-weight:750;")
        title_stack.addWidget(self.top_title)
        self.top_subtitle = QLabel("فضای مدیریت دستیار بله")
        self.top_subtitle.setObjectName("Muted")
        self.top_subtitle.setStyleSheet("font-size:8.5pt;")
        title_stack.addWidget(self.top_subtitle)
        top_layout.addLayout(title_stack)
        top_layout.addStretch(1)
        self.connection_badge = QLabel("● متصل")
        self.connection_badge.setObjectName("Pill")
        top_layout.addWidget(self.connection_badge)
        self.header_status = QLabel("متصل")
        self.header_status.setObjectName("Muted")
        self.header_status.hide()
        theme_btn = QPushButton()
        theme_btn.setToolTip("تغییر پوسته روشن / تاریک")
        theme_btn.setIcon(svg_icon("moon", "#8E98D8"))
        theme_btn.setIconSize(QSize(19, 19))
        theme_btn.setFixedSize(42, 42)
        theme_btn.clicked.connect(self.toggle_theme)
        self.theme_button = theme_btn
        top_layout.addWidget(theme_btn)
        refresh_btn = QPushButton()
        refresh_btn.setToolTip("به‌روزرسانی وضعیت اتصال")
        refresh_btn.setIcon(svg_icon("refresh", "#82BFAF"))
        refresh_btn.setIconSize(QSize(19, 19))
        refresh_btn.setFixedSize(42, 42)
        refresh_btn.clicked.connect(self.refresh_status)
        top_layout.addWidget(refresh_btn)
        app_layout.addWidget(topbar)

        self.pages = QStackedWidget()
        self.page_map: dict[str, QWidget] = {}
        self.page_map["dashboard"] = self._build_dashboard()
        self.page_map["chats"] = self._build_chats()
        self.page_map["assistant"] = self._build_assistant()
        self.page_map["automation"] = self._build_automation()
        self.page_map["schedule"] = self._build_schedule_page()
        self.page_map["settings"] = self._build_settings()
        self.page_map["help"] = self._build_help_page()
        for page in self.page_map.values():
            self.pages.addWidget(page)
        app_layout.addWidget(self.pages, 1)

        dock_row = QHBoxLayout()
        dock_row.addStretch(1)
        dock = SpatialGlassFrame(radius=27)
        dock.setObjectName("Dock")
        dock.setFixedHeight(72)
        dock_layout = QHBoxLayout(dock)
        dock_layout.setContentsMargins(12, 7, 12, 7)
        dock_layout.setSpacing(7)
        nav_items = [
            ("dashboard", "نمای کلی"),
            ("chats", "گفتگوها"),
            ("assistant", "دستیار هوشمند"),
            ("automation", "قوانین و حافظه"),
            ("schedule", "زمان‌بندی"),
            ("settings", "تنظیمات"),
            ("help", "راهنما"),
        ]
        for key, label in nav_items:
            button = DockButton(key, label)
            button.setProperty("active", key == "dashboard")
            button.clicked.connect(lambda checked=False, k=key: self.show_page(k))
            self.nav_buttons[key] = button
            dock_layout.addWidget(button)
        dock_row.addWidget(dock)
        dock_row.addStretch(1)
        app_layout.addLayout(dock_row)
        self.app_shell = app_shell
        self.root_stack.addWidget(app_shell)
        self.root_stack.setCurrentWidget(self.auth_page)
        self.setCentralWidget(self.root_stack)
        self.statusBar().showMessage("ابتدا به بله متصل شوید")
        self.statusBar().hide()
        self._install_context_help()

    def _refresh_dock_icons(self):
        if not hasattr(self, "nav_buttons"):
            return
        active_color = "#727DBD" if not self.dark_mode else "#C2C7FF"
        normal_color = "#858AA3" if not self.dark_mode else "#C2C1D5"
        for key, button in self.nav_buttons.items():
            button.setIcon(svg_icon(key, active_color if button.property("active") else normal_color))
        if hasattr(self, "theme_button"):
            self.theme_button.setIcon(svg_icon("sun" if self.dark_mode else "moon", active_color))

    def _page(self, title: str, subtitle: str = "") -> tuple[QWidget, QVBoxLayout]:
        # Page title and description are rendered once in the app-wide topbar.
        page = QWidget()
        page.setObjectName("Page")
        page.setLayoutDirection(Qt.RightToLeft)
        page.setProperty("guide_title", title or "راهنمای صفحه")
        page.setProperty("guide_body", subtitle or "این صفحه شامل ابزارهای مرتبط با همین بخش از برنامه است.")
        page.setProperty("guide_topic", self._topic_for_page_title(title))
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(14)
        return page, layout

    def _panel(self, title: str = "") -> tuple[QFrame, QVBoxLayout]:
        panel = SpatialGlassFrame(radius=24)
        panel.setObjectName("Panel")
        if title:
            panel.setProperty("guide_title", title)
            panel.setProperty("guide_body", self._section_help(title))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 15, 16, 15)
        layout.setSpacing(10)
        if title:
            label = QLabel(title)
            label.setObjectName("SectionTitle")
            layout.addWidget(label)
        return panel, layout

    def _stat(self, title: str, value: str, detail: str) -> tuple[QFrame, QLabel]:
        accents = ["#9DA8E8", "#83C5B0", "#D9A5BB", "#D7BD83", "#94BCE0"]
        accent = accents[self._stat_index % len(accents)]
        self._stat_index += 1
        card = SpatialGlassFrame(radius=22)
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 15, 17, 15)
        label = QLabel(title)
        label.setObjectName("Muted")
        number = QLabel(value)
        number.setStyleSheet("font-size:23pt; font-weight:760; color:%s;" % accent)
        info = QLabel(detail)
        info.setObjectName("Muted")
        layout.addWidget(label)
        layout.addWidget(number)
        layout.addWidget(info)
        return card, number

    def _build_dashboard(self) -> QWidget:
        page, layout = self._page("نمای کلی", "وضعیت حساب بله و اجزای اصلی دستیار را از یک نقطه مدیریت کنید.")
        stats = QHBoxLayout()
        stats.setSpacing(13)
        card, self.stat_session = self._stat("وضعیت حساب", "—", "نشست بله")
        stats.addWidget(card)
        card, self.stat_facts = self._stat("حافظه محلی", "0", "یادداشت ذخیره‌شده")
        stats.addWidget(card)
        card, self.stat_rules = self._stat("قوانین پاسخ", "0", "قانون تعریف‌شده")
        stats.addWidget(card)
        card, self.stat_ai = self._stat("هوش مصنوعی", "—", "وضعیت پیکربندی")
        stats.addWidget(card)
        card, self.stat_scheduled = self._stat("پیام‌های زمان‌بندی", "0", "در انتظار ارسال")
        stats.addWidget(card)
        layout.addLayout(stats)

        row = QHBoxLayout()
        panel, p = self._panel("شروع سریع")
        intro = QLabel("برای شروع، حساب بله را متصل کنید؛ سپس گفتگوها را بارگذاری و پاسخ‌ها را مدیریت کنید.")
        intro.setObjectName("Muted")
        intro.setWordWrap(True)
        p.addWidget(intro)
        actions = QHBoxLayout()
        a = QPushButton("اتصال به بله")
        a.setObjectName("Primary")
        a.clicked.connect(self.start_login)
        b = QPushButton("رفتن به گفتگوها")
        b.clicked.connect(lambda: self.show_page("chats"))
        c = QPushButton("تنظیم هوش مصنوعی")
        c.clicked.connect(lambda: self.show_page("settings"))
        d = QPushButton("زمان‌بندی پیام")
        d.clicked.connect(lambda: self.show_page("schedule"))
        actions.addWidget(a)
        actions.addWidget(b)
        actions.addWidget(c)
        actions.addWidget(d)
        p.addLayout(actions)
        row.addWidget(panel, 3)

        panel2, p2 = self._panel("حریم خصوصی و کنترل")
        safety = QLabel(
            "• پیام‌ها بدون تأیید شما ارسال نمی‌شوند.\n"
            "• تاریخچه گفتگو فقط با فعال‌کردن اجازه اشتراک‌گذاری برای سرویس AI فرستاده می‌شود.\n"
            "• کلید API در فایل تنظیمات محلی ذخیره می‌شود.\n"
            "• این نسخه پاسخ خودکارِ بی‌وقفه را فعال نمی‌کند."
        )
        safety.setObjectName("Muted")
        safety.setWordWrap(True)
        p2.addWidget(safety)
        row.addWidget(panel2, 2)
        layout.addLayout(row)

        panel3, p3 = self._panel("فعالیت اخیر")
        self.activity = QListWidget()
        self.activity.setMaximumHeight(180)
        self.activity.addItem("برنامه آماده است.")
        p3.addWidget(self.activity)
        layout.addWidget(panel3)
        layout.addStretch(1)
        return page

    def _build_chats(self) -> QWidget:
        page, layout = self._page("گفتگوها", "گفتگوهای حساب بله را بارگذاری کنید، پیام‌ها را بخوانید و با تأیید خودتان پاسخ دهید.")
        controls = QHBoxLayout()
        self.chat_search = QLineEdit()
        self.chat_search.setPlaceholderText("جستجو در گفتگوهای بارگذاری‌شده…")
        self.chat_search.textChanged.connect(self.filter_chats)
        controls.addWidget(self.chat_search, 1)
        load_btn = QPushButton("بارگذاری گفتگوها")
        load_btn.setObjectName("Primary")
        load_btn.clicked.connect(self.load_dialogs)
        controls.addWidget(load_btn)
        layout.addLayout(controls)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setLayoutDirection(Qt.LeftToRight)
        splitter.setChildrenCollapsible(False)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        self.chat_list = QListWidget()
        self.chat_list.itemSelectionChanged.connect(self.on_chat_selected)
        ll.addWidget(self.chat_list)
        self.chat_count_label = QLabel("هنوز گفتگویی بارگذاری نشده است.")
        self.chat_count_label.setObjectName("Muted")
        ll.addWidget(self.chat_count_label)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.chat_heading = QLabel("یک گفتگو را انتخاب کنید")
        self.chat_heading.setObjectName("SectionTitle")
        rl.addWidget(self.chat_heading)
        message_tools = QHBoxLayout()
        self.message_search = QLineEdit()
        self.message_search.setPlaceholderText("جستجو در پیام‌های همین گفتگو…")
        self.message_search.textChanged.connect(self.filter_messages)
        message_tools.addWidget(self.message_search, 1)
        export_btn = QPushButton("خروجی تاریخچه")
        export_btn.clicked.connect(self.export_chat_history)
        message_tools.addWidget(export_btn)
        reload_history_btn = QPushButton("تازه‌سازی")
        reload_history_btn.clicked.connect(self.load_history)
        message_tools.addWidget(reload_history_btn)
        rl.addLayout(message_tools)
        self.message_scroll = QScrollArea()
        self.message_scroll.setWidgetResizable(True)
        self.message_scroll.setFrameShape(QFrame.NoFrame)
        self.message_scroll.viewport().setAutoFillBackground(False)
        self.message_scroll.viewport().setAttribute(Qt.WA_StyledBackground, True)
        self.message_container = QWidget()
        self.message_container.setObjectName("ScrollContent")
        self.message_container.setAttribute(Qt.WA_TranslucentBackground, True)
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setContentsMargins(10, 10, 10, 10)
        self.message_layout.setSpacing(10)
        self.message_layout.addStretch(1)
        self.message_scroll.setWidget(self.message_container)
        rl.addWidget(self.message_scroll, 1)
        compose = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("پیام خود را بنویسید…")
        self.message_input.setFixedHeight(82)
        compose.addWidget(self.message_input, 1)
        send_col = QVBoxLayout()
        send_btn = QPushButton("ارسال پیام")
        send_btn.setObjectName("Primary")
        send_btn.clicked.connect(self.send_chat_message)
        file_btn = QPushButton("ارسال فایل")
        file_btn.clicked.connect(self.send_chat_file)
        ai_btn = QPushButton("پیشنهاد AI")
        ai_btn.clicked.connect(self.draft_chat_reply)
        schedule_btn = QPushButton("زمان‌بندی")
        schedule_btn.clicked.connect(self.schedule_chat_message)
        send_col.addWidget(send_btn)
        send_col.addWidget(file_btn)
        send_col.addWidget(ai_btn)
        send_col.addWidget(schedule_btn)
        compose.addLayout(send_col)
        rl.addLayout(compose)
        splitter.addWidget(right)
        splitter.setSizes([330, 800])
        layout.addWidget(splitter, 1)
        self.render_messages([])
        return page

    def _build_assistant(self) -> QWidget:
        page, layout = self._page("دستیار هوشمند", "برای گفتگو با مدل، از تنظیمات یک سرویس OpenAI-compatible معرفی کنید.")
        splitter = QSplitter(Qt.Horizontal)
        left, l = self._panel("گفتگو با دستیار")
        self.ai_prompt = QTextEdit()
        self.ai_prompt.setPlaceholderText("درخواست خود را بنویسید؛ دستیار می‌تواند در ادامه همین گفتگو زمینه قبلی را هم در نظر بگیرد…")
        self.ai_prompt.setMinimumHeight(150)
        preset_row = QHBoxLayout()
        self.ai_presets = QComboBox()
        self.ai_presets.addItem("الگوی آماده…", "")
        self.ai_presets.addItem("بازنویسی روان و حرفه‌ای", "متن زیر را روان، دقیق و حرفه‌ای بازنویسی کن و معنی اصلی را حفظ کن:")
        self.ai_presets.addItem("خلاصه‌سازی نکته‌ای", "محتوای زیر را در چند نکته کوتاه و کاربردی خلاصه کن:")
        self.ai_presets.addItem("پاسخ کوتاه و محترمانه", "یک پاسخ کوتاه، محترمانه و طبیعی برای متن زیر بنویس:")
        self.ai_presets.addItem("ایده‌پردازی", "چند ایده خلاقانه، قابل اجرا و متفاوت برای موضوع زیر پیشنهاد بده:")
        apply_preset = QPushButton("استفاده از الگو")
        apply_preset.clicked.connect(self.apply_ai_preset)
        preset_row.addWidget(self.ai_presets, 1)
        preset_row.addWidget(apply_preset)
        l.addLayout(preset_row)
        l.addWidget(self.ai_prompt)
        assistant_actions = QHBoxLayout()
        ask = QPushButton("ارسال درخواست به AI")
        ask.setObjectName("Primary")
        ask.clicked.connect(self.ask_ai)
        clear_thread = QPushButton("گفتگوی جدید")
        clear_thread.clicked.connect(self.clear_ai_thread)
        assistant_actions.addWidget(ask)
        assistant_actions.addWidget(clear_thread)
        assistant_actions.addStretch(1)
        l.addLayout(assistant_actions)
        l.addStretch(1)
        splitter.addWidget(left)
        right, r = self._panel("پاسخ دستیار")
        self.ai_output = QPlainTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setPlaceholderText("پاسخ مدل اینجا نمایش داده می‌شود…")
        r.addWidget(self.ai_output, 1)
        output_actions = QHBoxLayout()
        copy = QPushButton("کپی پاسخ")
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.ai_output.toPlainText()))
        use_in_chat = QPushButton("قرار دادن در کادر پیام")
        use_in_chat.clicked.connect(self.put_ai_output_in_chat)
        output_actions.addWidget(copy)
        output_actions.addWidget(use_in_chat)
        output_actions.addStretch(1)
        r.addLayout(output_actions)
        splitter.addWidget(right)
        splitter.setSizes([1, 1])
        layout.addWidget(splitter, 1)
        return page

    def _build_automation(self) -> QWidget:
        page, layout = self._page("قوانین و حافظه", "یادداشت‌ها، قوانین پاسخ پیشنهادی و مخاطبان مورد اعتماد در تنظیمات محلی شما ذخیره می‌شوند.")
        tabs = QTabWidget()

        facts_tab = QWidget()
        fl = QVBoxLayout(facts_tab)
        fact_row = QHBoxLayout()
        self.fact_input = QLineEdit()
        self.fact_input.setPlaceholderText("یک نکته درباره ترجیحات یا اطلاعاتی که باید به خاطر سپرده شود…")
        add_fact = QPushButton("افزودن یادداشت")
        add_fact.setObjectName("Primary")
        add_fact.clicked.connect(self.add_fact)
        fact_row.addWidget(self.fact_input, 1)
        fact_row.addWidget(add_fact)
        fl.addLayout(fact_row)
        self.fact_list = QListWidget()
        fl.addWidget(self.fact_list, 1)
        del_fact = QPushButton("حذف یادداشت انتخاب‌شده")
        del_fact.setObjectName("Danger")
        del_fact.clicked.connect(self.remove_fact)
        fl.addWidget(del_fact, alignment=Qt.AlignLeft)
        tabs.addTab(facts_tab, "حافظه")

        rules_tab = QWidget()
        rlayout = QVBoxLayout(rules_tab)
        self.rule_list = QListWidget()
        rlayout.addWidget(self.rule_list, 1)
        rule_actions = QHBoxLayout()
        add_rule = QPushButton("ساخت قانون")
        add_rule.setObjectName("Primary")
        add_rule.clicked.connect(self.add_rule)
        toggle_rule = QPushButton("فعال / غیرفعال")
        toggle_rule.clicked.connect(self.toggle_rule)
        remove_rule = QPushButton("حذف قانون")
        remove_rule.setObjectName("Danger")
        remove_rule.clicked.connect(self.remove_rule)
        rule_actions.addWidget(add_rule)
        rule_actions.addWidget(toggle_rule)
        rule_actions.addWidget(remove_rule)
        rule_actions.addStretch(1)
        rlayout.addLayout(rule_actions)
        tabs.addTab(rules_tab, "قوانین پاسخ")

        trust_tab = QWidget()
        tl = QVBoxLayout(trust_tab)
        trust_row = QHBoxLayout()
        self.trust_input = QLineEdit()
        self.trust_input.setPlaceholderText("شناسه عددی مخاطب")
        add_trust = QPushButton("افزودن به فهرست")
        add_trust.setObjectName("Primary")
        add_trust.clicked.connect(self.add_trusted)
        trust_row.addWidget(self.trust_input, 1)
        trust_row.addWidget(add_trust)
        tl.addLayout(trust_row)
        self.trust_list = QListWidget()
        tl.addWidget(self.trust_list, 1)
        remove_trust = QPushButton("حذف مخاطب انتخاب‌شده")
        remove_trust.setObjectName("Danger")
        remove_trust.clicked.connect(self.remove_trusted)
        tl.addWidget(remove_trust, alignment=Qt.AlignLeft)
        tabs.addTab(trust_tab, "مخاطبان مورد اعتماد")

        layout.addWidget(tabs, 1)
        self.refresh_local_lists()
        return page

    def _build_schedule_page(self) -> QWidget:
        page, layout = self._page("زمان‌بندی پیام‌ها", "پیام‌ها را برای زمان مشخصی آماده کنید. برنامه باید باز باشد و در زمان مقرر برای ارسال نهایی از شما تأیید می‌گیرد.")
        actions = QHBoxLayout()
        refresh = QPushButton("به‌روزرسانی فهرست")
        refresh.clicked.connect(self.refresh_schedule_list)
        retry = QPushButton("ارسال مجدد مورد ناموفق")
        retry.setObjectName("Primary")
        retry.clicked.connect(self.retry_scheduled_message)
        cancel = QPushButton("لغو زمان‌بندی انتخاب‌شده")
        cancel.setObjectName("Danger")
        cancel.clicked.connect(self.cancel_scheduled_message)
        actions.addWidget(refresh)
        actions.addWidget(retry)
        actions.addWidget(cancel)
        actions.addStretch(1)
        layout.addLayout(actions)
        panel, inner = self._panel("صف پیام‌ها")
        self.schedule_list = QListWidget()
        inner.addWidget(self.schedule_list, 1)
        self.schedule_summary = QLabel("هیچ پیام زمان‌بندی‌شده‌ای ثبت نشده است.")
        self.schedule_summary.setObjectName("Muted")
        inner.addWidget(self.schedule_summary)
        layout.addWidget(panel, 1)
        note = QLabel("وضعیت‌ها: در انتظار · در حال ارسال · ارسال‌شده · ناموفق. پیام‌های در انتظار به‌صورت محلی ذخیره می‌شوند و با بسته‌شدن برنامه در زمان مقرر اجرا نخواهند شد.")
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        return page

    def _build_settings(self) -> QWidget:
        page, layout = self._page("تنظیمات", "اطلاعات اتصال و ترجیحات محلی برنامه را مدیریت کنید.")
        scroll = QScrollArea()
        scroll.setObjectName("SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setAttribute(Qt.WA_TranslucentBackground, True)
        scroll.viewport().setObjectName("SettingsViewport")
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
        scroll.viewport().setAttribute(Qt.WA_StyledBackground, True)
        wrapper = QWidget()
        wrapper.setObjectName("SettingsContent")
        wrapper.setAttribute(Qt.WA_TranslucentBackground, True)
        wrapper.setAutoFillBackground(False)
        wrapper.setStyleSheet("background: transparent; border: none;")
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 8, 0)
        wl.setSpacing(14)

        api_panel, ap = self._panel("اتصال هوش مصنوعی")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("کلید API؛ برای حفظ مقدار فعلی خالی بگذارید")
        self.base_url_input = QLineEdit()
        self.model_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.example.com/v1")
        self.model_input.setPlaceholderText("gpt-4o-mini")
        for field in (self.api_key_input, self.base_url_input, self.model_input):
            field.setMinimumHeight(44)
            field.setLayoutDirection(Qt.LeftToRight)
        for label_text, field in (("کلید API", self.api_key_input), ("آدرس پایه API", self.base_url_input), ("نام مدل", self.model_input)):
            field_label = QLabel(label_text)
            field_label.setObjectName("Muted")
            form.addRow(field_label, field)
        ap.addLayout(form)
        api_actions = QHBoxLayout()
        save_api = QPushButton("ذخیره تنظیمات AI")
        save_api.setObjectName("Primary")
        save_api.clicked.connect(self.save_ai_settings)
        clear_api = QPushButton("پاک‌کردن کلید")
        clear_api.setObjectName("Danger")
        clear_api.clicked.connect(self.clear_api_key)
        test_api = QPushButton("آزمایش اتصال مدل")
        test_api.clicked.connect(self.test_ai)
        api_actions.addWidget(save_api)
        api_actions.addWidget(test_api)
        api_actions.addWidget(clear_api)
        api_actions.addStretch(1)
        ap.addLayout(api_actions)
        wl.addWidget(api_panel)

        style_panel, sp = self._panel("سبک نگارش پاسخ‌ها")
        self.style_input = QTextEdit()
        self.style_input.setPlaceholderText("مثال: کوتاه و صمیمی بنویس، از جمله‌های رسمی طولانی استفاده نکن…")
        self.style_input.setMinimumHeight(120)
        sp.addWidget(self.style_input)
        style_actions = QHBoxLayout()
        save_style = QPushButton("ذخیره سبک نگارش")
        save_style.setObjectName("Primary")
        save_style.clicked.connect(self.save_style)
        clear_style = QPushButton("پاک‌کردن سبک")
        clear_style.clicked.connect(self.clear_style)
        style_actions.addWidget(save_style)
        style_actions.addWidget(clear_style)
        style_actions.addStretch(1)
        sp.addLayout(style_actions)
        wl.addWidget(style_panel)

        session_panel, ss = self._panel("نشست و داده‌ها")
        self.session_label = QLabel("نشست: %s" % self.session)
        self.session_label.setObjectName("Muted")
        self.data_path_label = QLabel("مسیر داده‌ها: %s" % self.home)
        self.data_path_label.setObjectName("Muted")
        self.data_path_label.setWordWrap(True)
        ss.addWidget(self.session_label)
        ss.addWidget(self.data_path_label)
        logout_btn = QPushButton("خروج از حساب بله و حذف نشست")
        logout_btn.setObjectName("Danger")
        logout_btn.clicked.connect(self.logout)
        ss.addWidget(logout_btn, alignment=Qt.AlignLeft)
        wl.addWidget(session_panel)
        wl.addStretch(1)
        scroll.setWidget(wrapper)
        layout.addWidget(scroll, 1)
        self.load_settings_values()
        return page

    def _topic_for_page_title(self, title: str) -> str:
        return {
            "نمای کلی": "dashboard",
            "گفتگوها": "chats",
            "دستیار هوشمند": "assistant",
            "قوانین و حافظه": "automation",
            "زمان‌بندی پیام‌ها": "schedule",
            "تنظیمات": "settings",
        }.get(title, "general")

    @staticmethod
    def _section_help(title: str) -> str:
        descriptions = {
            "اتصال هوش مصنوعی": "کلید API، آدرس پایه سرویس و شناسه مدل را تنظیم کنید. سرویس باید با قالب OpenAI Chat Completions سازگار باشد. پس از ذخیره، از گزینه آزمایش اتصال برای بررسی دسترسی مدل استفاده کنید.",
            "سبک نگارش پاسخ‌ها": "ویژگی‌های لحن، طول جمله‌ها، واژگان و میزان رسمی‌بودن پاسخ را بنویسید. این توضیح در ساخت پیش‌نویس‌های هوش مصنوعی استفاده می‌شود و هر زمان قابل تغییر یا پاک‌کردن است.",
            "نشست و داده‌ها": "نام نشست جاری و محل ذخیره تنظیمات محلی را نشان می‌دهد. خروج از حساب، نشست فعال بله را حذف می‌کند؛ پیش از انجام آن مطمئن شوید که دیگر به این نشست نیاز ندارید.",
            "گفتگو با دستیار": "درخواست خود را برای مدل بنویسید. الگوهای آماده می‌توانند شروع کار را سریع‌تر کنند. هر درخواست فقط متن را به سرویس مدل می‌فرستد و دستیار به‌تنهایی به ابزارهای حساب بله دسترسی اجرایی ندارد.",
            "پاسخ دستیار": "خروجی مدل در این قسمت نمایش داده می‌شود. می‌توانید آن را کپی کنید یا در صورت نیاز به کادر پیام گفتگوی انتخاب‌شده منتقل کنید؛ انتقال به کادر پیام به معنی ارسال نیست.",
            "شروع سریع": "میانبرهایی برای رفتن به گفتگوها، تنظیم هوش مصنوعی و زمان‌بندی پیام‌ها در اختیار دارید.",
            "حریم خصوصی و کنترل": "این بخش یادآوری می‌کند کدام عملیات نیازمند تأیید هستند و چه داده‌هایی ممکن است برای سرویس خارجی AI ارسال شوند.",
            "فعالیت اخیر": "رویدادهای محلی برنامه مانند ذخیره تنظیمات یا بارگذاری گفتگوها را نشان می‌دهد. این فهرست، گزارش کامل و دائمی از سرور بله نیست.",
            "صف پیام‌ها": "پیام‌های زمان‌بندی‌شده و وضعیت آن‌ها در این فهرست دیده می‌شود. اجرای زمان‌بندی فقط وقتی برنامه باز است انجام می‌شود و قبل از ارسال نهایی تأیید می‌گیرد.",
        }
        return descriptions.get(title, "این پنل ابزارها و اطلاعات مرتبط با «%s» را در بر می‌گیرد. برای جزئیات بیشتر، راهنمای همین بخش را باز کنید." % title)

    def _help_topics(self) -> list[dict[str, str]]:
        return [
            {
                "id": "dashboard", "title": "نمای کلی و داشبورد",
                "summary": "آشنایی با وضعیت حساب، شاخص‌ها و فعالیت‌های اخیر",
                "html": """
                    <h2>نمای کلی</h2>
                    <p>داشبورد، وضعیت فعلی دستیار را در یک نگاه نشان می‌دهد.</p>
                    <h3>کارت‌های وضعیت</h3>
                    <ul><li><b>وضعیت حساب:</b> نشان می‌دهد نشست بله متصل است یا نه.</li>
                    <li><b>حافظه محلی:</b> تعداد یادداشت‌هایی که خودت ذخیره کرده‌ای.</li>
                    <li><b>قوانین پاسخ:</b> تعداد قانون‌های تعریف‌شده.</li>
                    <li><b>هوش مصنوعی:</b> وضعیت تنظیم سرویس مدل.</li>
                    <li><b>پیام‌های زمان‌بندی:</b> تعداد مواردی که هنوز در صف انتظار هستند.</li></ul>
                    <h3>شروع سریع</h3><p>دکمه‌های این قسمت میانبر ورود به گفتگوها، تنظیم AI و صفحه زمان‌بندی هستند. فعالیت اخیر نیز رویدادهای محلی برنامه را نمایش می‌دهد.</p>
                """
            },
            {
                "id": "chats", "title": "گفتگوها و پیام‌ها",
                "summary": "بارگذاری گفتگوها، خواندن تاریخچه، جست‌وجو و ارسال پیام",
                "html": """
                    <h2>گفتگوها</h2>
                    <p>برای دریافت فهرست گفتگوهای حساب، «بارگذاری گفتگوها» را بزن. جست‌وجوی بالای صفحه فقط بین گفتگوهایی انجام می‌شود که بارگذاری شده‌اند.</p>
                    <h3>تاریخچه و جست‌وجو</h3><p>پس از انتخاب یک گفتگو، دکمه تازه‌سازی تاریخچه پیام‌های اخیر را از بله دریافت می‌کند. جست‌وجوی کنار عنوان گفتگو، پیام‌های بارگذاری‌شده همان گفتگو را فیلتر می‌کند.</p>
                    <h3>ارسال و عملیات پیام</h3><p>متن را در کادر پایین بنویس و «ارسال پیام» را بزن. ارسال فایل، پیش‌نویس AI و زمان‌بندی از دکمه‌های کناری انجام می‌شوند. با راست‌کلیک روی پیام، گزینه‌های کپی متن، پاسخ، واکنش، فوروارد و راهنمای پیام را می‌بینی.</p>
                    <p><b>نکته:</b> خروجی تاریخچه فقط پیام‌هایی را شامل می‌شود که در همان نوبت بارگذاری شده‌اند.</p>
                """
            },
            {
                "id": "assistant", "title": "دستیار هوشمند",
                "summary": "گفتگو با مدل، الگوهای آماده و استفاده از پاسخ تولیدشده",
                "html": """
                    <h2>دستیار هوشمند</h2>
                    <p>در کادر درخواست، وظیفه‌ای را برای مدل توضیح بده. می‌توانی از الگوهای بازنویسی، خلاصه‌سازی، پاسخ محترمانه یا ایده‌پردازی استفاده کنی.</p>
                    <h3>زمینه گفتگو</h3><p>درخواست‌های همین صفحه در طول اجرای برنامه می‌توانند به‌عنوان زمینه مکالمه نگهداری شوند. «گفتگوی جدید» این زمینه موقت را پاک می‌کند.</p>
                    <h3>استفاده از پاسخ</h3><p>خروجی را بررسی و کپی کن یا به کادر پیام گفتگوی انتخاب‌شده منتقل کن. انتقال پاسخ به چت آن را ارسال نمی‌کند؛ ارسال باید جداگانه توسط خودت انجام شود.</p>
                """
            },
            {
                "id": "automation", "title": "حافظه، قوانین و مخاطبان",
                "summary": "یادداشت‌های شخصی، قوانین پاسخ پیشنهادی و فهرست اعتماد",
                "html": """
                    <h2>قوانین و حافظه</h2>
                    <h3>حافظه</h3><p>یادداشت‌هایی درباره ترجیحات یا اطلاعاتی که باید در پاسخ‌های AI در نظر گرفته شوند ذخیره کن. فقط اطلاعات لازم را بنویس و از ثبت داده‌های حساس خودداری کن.</p>
                    <h3>قوانین پاسخ</h3><p>برای کلیدواژه‌ها یک پاسخ پیشنهادی تعریف کن. فعال‌بودن قانون به‌معنی ارسال خودکار نیست؛ برنامه در این نسخه پاسخ را به‌صورت پیشنهاد نمایش می‌دهد.</p>
                    <h3>مخاطبان مورد اعتماد</h3><p>شناسه عددی مخاطب را برای قابلیت‌هایی که فهرست اعتماد را بررسی می‌کنند ثبت کن. قبل از افزودن، شناسه را از منبع مطمئن بررسی کن.</p>
                """
            },
            {
                "id": "schedule", "title": "زمان‌بندی پیام‌ها",
                "summary": "ثبت، لغو و تلاش دوباره برای پیام‌های زمان‌بندی‌شده",
                "html": """
                    <h2>زمان‌بندی پیام‌ها</h2>
                    <p>از صفحه گفتگو یک پیام را برای تاریخ و ساعت آینده برنامه‌ریزی کن. صف در فایل محلی برنامه ذخیره می‌شود.</p>
                    <h3>نکات مهم</h3><ul><li>برنامه باید در زمان مقرر باز باشد.</li><li>قبل از ارسال نهایی پنجره تأیید نمایش داده می‌شود.</li><li>می‌توانی پیام منتظر را لغو کنی.</li><li>برای مورد ناموفق، پس از بررسی علت، ارسال مجدد را انتخاب کن.</li></ul>
                    <p>زمان‌بندی یک سرویس ابری یا پس‌زمینه نیست و با بسته‌شدن برنامه در زمان مقرر اجرا نمی‌شود.</p>
                """
            },
            {
                "id": "settings", "title": "تنظیمات و اتصال AI",
                "summary": "کلید API، نشانی سرویس، مدل و سبک نگارش",
                "html": """
                    <h2>تنظیمات</h2>
                    <h3>کلید API</h3><p>کلید سرویس مدل را وارد کن. اگر می‌خواهی کلید ذخیره‌شده باقی بماند، این فیلد را خالی بگذار. کلید در تنظیمات محلی دستگاه نگهداری می‌شود و نباید آن را با دیگران به اشتراک بگذاری.</p>
                    <h3>آدرس پایه API</h3><p>آدرس ریشه سرویس سازگار با OpenAI را وارد کن؛ معمولاً با ‎/v1‎ تمام می‌شود. از آدرس رسمی ارائه‌دهنده خودت استفاده کن.</p>
                    <h3>نام مدل</h3><p>شناسه دقیق مدلی را بنویس که سرویس‌دهنده در اختیارت قرار داده است.</p>
                    <h3>سبک نگارش</h3><p>در کادر سبک نگارش، لحن، طول پاسخ و ترجیحات نوشتاری را توضیح بده. این متن برای ساخت پیش‌نویس‌ها استفاده می‌شود.</p>
                    <h3>نشست و داده‌ها</h3><p>این قسمت نام نشست جاری و مسیر تنظیمات محلی را نشان می‌دهد. خروج از حساب، نشست بله را حذف می‌کند.</p>
                """
            },
            {
                "id": "appearance", "title": "ظاهر، پوسته و تسک‌بار",
                "summary": "تغییر تم، ناوبری و راه‌های دسترسی سریع",
                "html": """
                    <h2>ظاهر برنامه</h2>
                    <p>از دکمه بالای پنجره بین پوسته روشن و تاریک جابه‌جا شو. انتخاب پوسته در تنظیمات محلی ذخیره می‌شود.</p>
                    <h3>تسک‌بار شناور</h3><p>آیکون‌های پایین پنجره بخش‌های اصلی را باز می‌کنند. روی هر آیکون مکث کن تا نام آن دیده شود؛ هنگام نزدیک‌شدن موس، آیکون با انیمیشن ملایم بزرگ می‌شود.</p>
                    <h3>راهنمای سریع</h3><p>روی هر فیلد، دکمه، کارت یا ناحیه از برنامه راست‌کلیک کن و «راهنمای این بخش» را انتخاب کن تا توضیح همان قسمت باز شود.</p>
                """
            },
            {
                "id": "privacy", "title": "اتصال، امنیت و حریم خصوصی",
                "summary": "نشست بله، اشتراک‌گذاری زمینه و تأیید عملیات",
                "html": """
                    <h2>امنیت و حریم خصوصی</h2>
                    <p>ورود بله با کتابخانه غیررسمی انجام می‌شود؛ استفاده از آن ممکن است با ریسک حساب همراه باشد. نشست بله و کلید API را مانند گذرواژه نگهداری کن.</p>
                    <ul><li>قبل از ارسال پیام، پاسخ، واکنش یا فوروارد، اقدام صریح لازم است.</li><li>ارسال تاریخچه گفتگو به سرویس AI باید با اجازه آگاهانه انجام شود.</li><li>مدل فقط متن تولید می‌کند و مجوز اجرای کد یا فرمان‌های سیستم را ندارد.</li><li>از کلید API و فایل نشست در نسخه پشتیبان ناامن یا مخزن عمومی استفاده نکن.</li></ul>
                """
            },
            {
                "id": "context-help", "title": "راهنمای راست‌کلیک",
                "summary": "باز کردن توضیح دقیق برای فیلد یا بخش انتخاب‌شده",
                "html": """
                    <h2>راهنمای وابسته به بخش</h2>
                    <p>روی بخش موردنظر راست‌کلیک کن. در فیلدهای متنی، گزینه‌های معمولی مانند کپی، چسباندن، بریدن و انتخاب همه حفظ می‌شوند و گزینه «راهنمای این بخش» به انتهای منو اضافه می‌شود.</p>
                    <p>در کارت‌ها و بخش‌هایی که منوی استاندارد ندارند، منوی راست‌کلیک مستقیماً گزینه راهنما را نمایش می‌دهد. انتخاب آن، صفحه راهنما را با توضیح مرتبط باز می‌کند.</p>
                """
            },
        ]

    def _build_help_page(self) -> QWidget:
        page, layout = self._page("راهنما", "راهنمای کامل بخش‌های برنامه و توضیح گزینه‌ها و فیلدها.")
        top = QHBoxLayout()
        self.help_search = QLineEdit()
        self.help_search.setPlaceholderText("جستجو در راهنما…")
        self.help_search.textChanged.connect(self.filter_help_topics)
        top.addWidget(self.help_search, 1)
        layout.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setLayoutDirection(Qt.LeftToRight)
        topic_panel, topic_layout = self._panel("موضوعات راهنما")
        self.help_topic_list = QListWidget()
        topic_layout.addWidget(self.help_topic_list, 1)
        splitter.addWidget(topic_panel)

        detail_panel, detail_layout = self._panel("راهنمای بخش انتخاب‌شده")
        self.help_detail_title = QLabel("به راهنمای Bale Agent خوش آمدی")
        self.help_detail_title.setObjectName("PageTitle")
        detail_layout.addWidget(self.help_detail_title)
        self.help_detail = QTextBrowser()
        self.help_detail.setOpenExternalLinks(False)
        self.help_detail.setFrameShape(QFrame.NoFrame)
        self.help_detail.setLayoutDirection(Qt.RightToLeft)
        self.help_detail.setMinimumHeight(320)
        detail_layout.addWidget(self.help_detail, 1)
        splitter.addWidget(detail_panel)
        splitter.setSizes([300, 780])
        layout.addWidget(splitter, 1)

        hint = QLabel("نکته: روی هر قسمت از برنامه راست‌کلیک کن و «راهنمای این بخش» را انتخاب کن تا مستقیم به توضیح همان بخش برسی.")
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._help_data = self._help_topics()
        for topic in self._help_data:
            item = QListWidgetItem(topic["title"] + "\n" + topic["summary"])
            item.setData(Qt.UserRole, topic["id"])
            self.help_topic_list.addItem(item)
        self.help_topic_list.currentItemChanged.connect(self._on_help_topic_selected)
        if self.help_topic_list.count():
            self.help_topic_list.setCurrentRow(0)
        return page

    def _on_help_topic_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem] = None):
        if not current:
            return
        topic_id = current.data(Qt.UserRole)
        topic = next((item for item in self._help_data if item["id"] == topic_id), None)
        if topic:
            self.help_detail_title.setText(topic["title"])
            self._set_help_html(topic["html"])

    def _set_help_html(self, body_html: str):
        self._help_current_html = body_html
        self._render_help_html(body_html)

    def _render_help_html(self, body_html: str):
        foreground = "#EAE8F5" if self.dark_mode else "#41445F"
        heading = "#D9DDFF" if self.dark_mode else "#59629A"
        muted = "#B8B6CE" if self.dark_mode else "#747A92"
        self.help_detail.setHtml(
            "<html><head><style>body{color:%s;font-family:'Segoe UI','Vazirmatn',sans-serif;line-height:1.8;direction:rtl;text-align:right;} "
            "h2,h3{color:%s;margin-top:12px;} p,li{color:%s;} b{color:%s;} "
            "ul{margin-right:18px;} a{color:%s;}</style></head><body>%s</body></html>" %
            (foreground, heading, foreground, heading, muted, body_html)
        )

    def filter_help_topics(self, query: str):
        needle = (query or "").strip().casefold()
        for index in range(self.help_topic_list.count()):
            item = self.help_topic_list.item(index)
            topic = next((entry for entry in self._help_data if entry["id"] == item.data(Qt.UserRole)), None)
            haystack = (topic["title"] + " " + topic["summary"] + " " + topic["html"]) if topic else item.text()
            item.setHidden(bool(needle and needle not in haystack.casefold()))
        if self.help_topic_list.currentItem() and self.help_topic_list.currentItem().isHidden():
            for index in range(self.help_topic_list.count()):
                if not self.help_topic_list.item(index).isHidden():
                    self.help_topic_list.setCurrentRow(index)
                    break

    def show_help_topic(self, topic_id: str, custom_title: str = "", custom_body: str = ""):
        self.show_page("help")
        target = next((i for i, topic in enumerate(self._help_data) if topic["id"] == topic_id), 0)
        self.help_topic_list.setCurrentRow(target)
        if custom_title or custom_body:
            title = html.escape(custom_title or "راهنمای این بخش")
            body = html.escape(custom_body or "برای جزئیات بیشتر از فهرست موضوعات راهنما استفاده کن.")
            self.help_detail_title.setText(custom_title or "راهنمای این بخش")
            self._set_help_html("<h2>%s</h2><p>%s</p>" % (title, body))

    def _install_context_help(self):
        """Add a context menu to the UI while retaining native text-edit actions."""
        specific = {
            "auth_phone_input": ("privacy", "شماره موبایل", "شماره‌ای را وارد کن که حساب بله با آن ثبت شده است. این فیلد فقط برای شروع ورود استفاده می‌شود؛ کد تأیید در پنجره جداگانه درخواست خواهد شد."),
            "chat_search": ("chats", "جستجوی گفتگوها", "فهرست گفتگوهایی را که قبلاً بارگذاری شده‌اند بر اساس نام یا اطلاعات قابل مشاهده فیلتر می‌کند. این جست‌وجو درخواست تازه‌ای به سرور نمی‌فرستد."),
            "chat_list": ("chats", "فهرست گفتگوها", "برای بازکردن تاریخچه، یک گفتگو را انتخاب کن. اگر فهرست خالی است، ابتدا دکمه بارگذاری گفتگوها را بزن."),
            "message_search": ("chats", "جستجو در پیام‌ها", "فقط پیام‌های بارگذاری‌شده در گفتگوی انتخاب‌شده را فیلتر می‌کند. برای دریافت پیام‌های تازه از دکمه تازه‌سازی استفاده کن."),
            "message_input": ("chats", "کادر نوشتن پیام", "متن پاسخ را اینجا آماده کن. پیام با دکمه ارسال پیام فرستاده می‌شود و پیش از ارسال تأیید می‌خواهد."),
            "ai_prompt": ("assistant", "درخواست از دستیار", "درخواست یا متن موردنظر را برای مدل بنویس. در صورت استفاده از تاریخچه گفتگو، پیش از اشتراک‌گذاری اطلاعات با سرویس خارجی دقت کن."),
            "ai_output": ("assistant", "پاسخ هوش مصنوعی", "پاسخ تولیدشده در این کادر فقط برای بررسی است. می‌توانی آن را کپی کنی یا به کادر پیام منتقل کنی؛ انتقال به معنی ارسال نیست."),
            "ai_presets": ("assistant", "الگوهای آماده", "یک الگوی از پیش نوشته‌شده انتخاب کن و با دکمه استفاده از الگو آن را به درخواست اضافه کن."),
            "fact_input": ("automation", "افزودن یادداشت به حافظه", "یک نکته غیرحساس درباره ترجیحات یا اطلاعات موردنیاز دستیار بنویس. یادداشت روی همین دستگاه ذخیره می‌شود."),
            "fact_list": ("automation", "فهرست حافظه", "یادداشت‌های ذخیره‌شده را نشان می‌دهد. برای حذف، یک مورد را انتخاب کن و دکمه حذف یادداشت انتخاب‌شده را بزن."),
            "rule_list": ("automation", "قوانین پاسخ", "قانون‌ها بر اساس کلیدواژه‌ها پاسخ پیشنهادی فراهم می‌کنند. در این رابط، فعال بودن قانون به‌تنهایی به معنی ارسال خودکار پیام نیست."),
            "trust_input": ("automation", "شناسه مخاطب مورد اعتماد", "شناسه عددی مخاطب را وارد کن. شناسه را پیش از ثبت بررسی کن؛ این فهرست فقط برای محدودکردن قابلیت‌هایی که به اعتماد نیاز دارند استفاده می‌شود."),
            "trust_list": ("automation", "مخاطبان مورد اعتماد", "فهرست شناسه‌هایی را نشان می‌دهد که خودت به‌عنوان مخاطب مورد اعتماد ثبت کرده‌ای."),
            "schedule_list": ("schedule", "صف پیام‌های زمان‌بندی‌شده", "پیام‌های منتظر، ارسال‌شده یا ناموفق را نشان می‌دهد. برای تغییر وضعیت، یک مورد را انتخاب و از دکمه مناسب استفاده کن."),
            "api_key_input": ("settings", "کلید API", "کلید خصوصی سرویس هوش مصنوعی را وارد کن. اگر این فیلد را خالی بگذاری، کلید فعلی حفظ می‌شود. کلید ذخیره‌شده را در اختیار دیگران قرار نده."),
            "base_url_input": ("settings", "آدرس پایه API", "نشانی پایه سرویس سازگار با OpenAI را وارد کن؛ معمولاً نشانی به ‎/v1‎ ختم می‌شود. از نشانی مستندات ارائه‌دهنده سرویس خود استفاده کن."),
            "model_input": ("settings", "نام مدل", "شناسه دقیق مدلی را وارد کن که ارائه‌دهنده API در اختیارت قرار داده است. نام مدل به بزرگی و کوچکی حروف یا قالب سرویس‌دهنده وابسته است."),
            "style_input": ("settings", "سبک نگارش پاسخ‌ها", "لحن، میزان رسمی‌بودن، طول معمول پاسخ و ترجیحات نوشتاری را با چند جمله توضیح بده. این متن هنگام تولید پیش‌نویس‌های AI استفاده می‌شود."),
            "help_search": ("context-help", "جستجو در راهنما", "عنوان و توضیحات موضوعات راهنما را فیلتر می‌کند. برای بازکردن یک موضوع، آن را از فهرست سمت چپ انتخاب کن."),
            "help_topic_list": ("context-help", "موضوعات راهنما", "یکی از موضوعات را انتخاب کن تا توضیحات کامل آن در پنل سمت دیگر نمایش داده شود."),
        }
        for attr_name, (topic, title, body) in specific.items():
            widget = getattr(self, attr_name, None)
            if widget is not None:
                widget.setProperty("guide_topic", topic)
                widget.setProperty("guide_title", title)
                widget.setProperty("guide_body", body)

        text_hints = {
            "بارگذاری گفتگوها": ("chats", "بارگذاری گفتگوها", "فهرست گفتگوهای حساب بله را دریافت می‌کند. برای دیدن تاریخچه، پس از بارگذاری یک گفتگو را انتخاب کن."),
            "ارسال پیام": ("chats", "ارسال پیام", "متن نوشته‌شده را به گفتگوی انتخاب‌شده ارسال می‌کند. پیش از ارسال، مقصد و متن را بررسی کن."),
            "ارسال فایل": ("chats", "ارسال فایل", "یک فایل محلی را برای گفتگوی انتخاب‌شده آماده ارسال می‌کند. پیش از تأیید، مقصد و فایل را بررسی کن."),
            "پیشنهاد AI": ("assistant", "پیشنهاد پاسخ با AI", "با اجازه اشتراک‌گذاری زمینه گفتگو، یک پیش‌نویس پاسخ بر اساس پیام‌های اخیر تهیه می‌کند. پاسخ پیش از ارسال قابل بازبینی است."),
            "زمان‌بندی": ("schedule", "زمان‌بندی پیام", "متن پیام را برای تاریخ و ساعت آینده در صف محلی ذخیره می‌کند. برنامه باید در زمان مقرر باز باشد و تأیید نهایی می‌گیرد."),
            "ذخیره تنظیمات AI": ("settings", "ذخیره تنظیمات AI", "آدرس پایه، نام مدل و در صورت واردکردن کلید جدید، کلید API را در تنظیمات محلی ذخیره می‌کند."),
            "آزمایش اتصال مدل": ("settings", "آزمایش اتصال مدل", "یک درخواست آزمایشی کوتاه به سرویس مدل می‌فرستد تا اتصال و اعتبار تنظیمات بررسی شود."),
            "ذخیره سبک نگارش": ("settings", "ذخیره سبک نگارش", "توضیح واردشده در بخش سبک نگارش را در تنظیمات محلی ذخیره می‌کند."),
        }

        for widget in [self.root_stack, *self.root_stack.findChildren(QWidget)]:
            if widget is None or widget.property("skip_context_help"):
                continue
            if widget.objectName() == "" and not widget.parentWidget():
                continue
            widget.setContextMenuPolicy(Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                lambda pos, target=widget: self._show_widget_context_menu(target, pos)
            )
            label = ""
            if isinstance(widget, QPushButton):
                label = widget.text().strip()
            if label in text_hints and not widget.property("guide_body"):
                topic, title, body = text_hints[label]
                widget.setProperty("guide_topic", topic)
                widget.setProperty("guide_title", title)
                widget.setProperty("guide_body", body)

    def _resolve_widget_help(self, widget: QWidget) -> tuple[str, str, str]:
        current = widget
        found_title = ""
        found_body = ""
        found_topic = ""
        while current is not None:
            title = current.property("guide_title")
            body = current.property("guide_body")
            topic = current.property("guide_topic")
            if title and not found_title:
                found_title = str(title)
            if body and not found_body:
                found_body = str(body)
            if topic and not found_topic:
                found_topic = str(topic)
            current = current.parentWidget()

        if found_title or found_body or found_topic:
            return (
                found_topic or "general",
                found_title or "راهنمای این بخش",
                found_body or "این قسمت بخشی از رابط برنامه است. برای توضیحات کامل‌تر موضوع مرتبط را در راهنما انتخاب کن.",
            )

        current_key = "general"
        if hasattr(self, "pages"):
            for key, page in self.page_map.items():
                if page is self.pages.currentWidget():
                    current_key = key
                    break
        titles = {
            "dashboard": "نمای کلی", "chats": "گفتگوها", "assistant": "دستیار هوشمند",
            "automation": "قوانین و حافظه", "schedule": "زمان‌بندی پیام‌ها", "settings": "تنظیمات",
            "help": "راهنما", "general": "راهنمای برنامه",
        }
        return current_key, titles.get(current_key, "راهنمای برنامه"), "این کنترل در بخش «%s» قرار دارد. برای راهنمای دقیق‌تر، عنوان مرتبط را از فهرست موضوعات انتخاب کن." % titles.get(current_key, "برنامه")

    def _show_widget_context_menu(self, widget: QWidget, position):
        menu = None
        creator = getattr(widget, "createStandardContextMenu", None)
        if callable(creator):
            try:
                menu = creator()
            except TypeError:
                try:
                    menu = creator(position)
                except Exception:
                    menu = None
            except Exception:
                menu = None
        if menu is None:
            menu = QMenu(widget)
        if menu.actions():
            menu.addSeparator()
        help_action = menu.addAction("راهنمای این بخش")
        help_action.setIcon(svg_icon("help", "#9DA8E8" if self.dark_mode else "#747EC0"))
        help_action.triggered.connect(lambda: self._open_widget_help(widget))
        menu.exec(widget.mapToGlobal(position))

    def _open_widget_help(self, widget: QWidget):
        topic, title, body = self._resolve_widget_help(widget)
        self.show_help_topic(topic, title, body)

    def _load_app_state(self) -> dict[str, Any]:
        self.home.mkdir(parents=True, exist_ok=True)
        if not self.app_state_path.exists():
            return {"version": 1, "theme": "light", "scheduled_messages": []}
        try:
            raw = json.loads(self.app_state_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or raw.get("version") != 1 or not isinstance(raw.get("scheduled_messages", []), list):
                raise ValueError("ساختار فایل وضعیت دسکتاپ معتبر نیست.")
            entries = raw.get("scheduled_messages", [])
            if not all(isinstance(entry, dict) for entry in entries):
                raise ValueError("ساختار صف زمان‌بندی معتبر نیست.")
            for entry in entries:
                if entry.get("status") == "prompting":
                    entry["status"] = "pending"
                elif entry.get("status") == "sending":
                    entry["status"] = "failed"
                    entry["error"] = "برنامه هنگام ارسال بسته شده بود؛ برای ارسال مجدد دوباره زمان‌بندی کنید."
            theme = raw.get("theme", "light")
            if theme not in {"dark", "light"}:
                theme = "light"
            return {"version": 1, "theme": theme, "scheduled_messages": entries}
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError("فایل وضعیت Bale Agent خراب یا نامعتبر است: %s" % exc)

    def _save_app_state(self):
        self.home.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix="desktop_state.", suffix=".tmp", dir=str(self.home))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self.app_state, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.chmod(temp_name, 0o600)
            except OSError:
                pass
            os.replace(temp_name, self.app_state_path)
            try:
                os.chmod(self.app_state_path, 0o600)
            except OSError:
                pass
        except Exception:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise

    def apply_theme(self):
        app = QApplication.instance()
        app.setStyleSheet(DARK_QSS if self.dark_mode else LIGHT_QSS)
        if hasattr(self, "app_shell") and isinstance(self.app_shell, AmbientRoot):
            self.app_shell.set_dark_mode(self.dark_mode)
        for surface in self.findChildren(SpatialGlassFrame):
            surface.set_dark_mode(self.dark_mode)
        self._refresh_dock_icons()
        if getattr(self, "_help_current_html", "") and hasattr(self, "help_detail"):
            self._render_help_html(self._help_current_html)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.app_state["theme"] = "dark" if self.dark_mode else "light"
        self._save_app_state()
        self.apply_theme()
        self.statusBar().showMessage("پوسته %s فعال شد" % ("تیره" if self.dark_mode else "روشن"), 2500)

    def show_page(self, key: str):
        if not self._authenticated:
            return
        if key not in self.page_map:
            return
        self.pages.setCurrentWidget(self.page_map[key])
        titles = {
            "dashboard": ("نمای کلی", "وضعیت و نمای کلی دستیار"),
            "chats": ("گفتگوها", "مدیریت گفتگوها و پیام‌ها"),
            "assistant": ("دستیار هوشمند", "گفتگو و تولید پیش‌نویس با هوش مصنوعی"),
            "automation": ("قوانین و حافظه", "شخصی‌سازی رفتار و یادداشت‌های محلی"),
            "schedule": ("زمان‌بندی پیام‌ها", "مدیریت صف ارسال‌های برنامه‌ریزی‌شده"),
            "settings": ("تنظیمات", "اتصال مدل، سبک نگارش و نشست بله"),
            "help": ("راهنما", "توضیح کامل بخش‌ها و گزینه‌های برنامه"),
        }
        title, subtitle = titles.get(key, ("Bale Agent", ""))
        self.top_title.setText(title)
        self.top_subtitle.setText(subtitle)
        for nav_key, button in self.nav_buttons.items():
            button.setProperty("active", nav_key == key)
            button.style().unpolish(button)
            button.style().polish(button)
        self._refresh_dock_icons()
        if key == "settings":
            self.load_settings_values()
        elif key == "automation":
            self.refresh_local_lists()
        elif key == "schedule":
            self.refresh_schedule_list()

    def log(self, text: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, "activity"):
            self.activity.insertItem(0, "%s  ·  %s" % (stamp, text))
            while self.activity.count() > 30:
                self.activity.takeItem(self.activity.count() - 1)
        self.statusBar().showMessage(text, 5000)

    def _run_async(self, coroutine_factory: Callable[[], Any], on_success: Callable[[Any], None], label: str = "در حال انجام…", on_error: Optional[Callable[[str], None]] = None):
        worker = AsyncWorker(coroutine_factory, self)
        self.workers.append(worker)
        self.worker_callbacks[worker] = (on_success, on_error)
        # Bound QObject slots ensure all UI updates happen on the GUI thread.
        worker.succeeded.connect(self._on_async_succeeded)
        worker.failed.connect(self._on_async_failed)
        worker.start()
        self.statusBar().showMessage(label)
        return worker

    def _finish_worker(self, worker: QThread):
        if worker in self.workers:
            self.workers.remove(worker)
        self.worker_callbacks.pop(worker, None)
        worker.deleteLater()

    def _on_async_succeeded(self, result: Any):
        worker = self.sender()
        callback, _ = self.worker_callbacks.get(worker, (lambda _: None, None))
        self._finish_worker(worker)
        callback(result)

    def _on_async_failed(self, error: str):
        worker = self.sender()
        _, error_callback = self.worker_callbacks.get(worker, (lambda _: None, None))
        self._finish_worker(worker)
        self.statusBar().showMessage("عملیات ناموفق بود", 5000)
        if error_callback:
            error_callback(error)
        else:
            QMessageBox.critical(self, "خطا", error)

    def _new_agent(self) -> BaleAgent:
        return BaleAgent(self.session, self.home)

    def refresh_local_overview(self):
        self.config = AgentConfig(self.home)
        if hasattr(self, "stat_facts"):
            self.stat_facts.setText(str(len(self.config.data["facts"])))
            self.stat_rules.setText(str(len(self.config.data["rules"])))
            llm = self._new_agent().llm
            self.stat_ai.setText("آماده" if llm.configured else "تنظیم نشده")
            pending = sum(1 for item in self.app_state.get("scheduled_messages", []) if item.get("status") == "pending")
            self.stat_scheduled.setText(str(pending))

    def _set_auth_status(self, message: str, state: str = "waiting"):
        if not hasattr(self, "auth_status_label"):
            return
        self.auth_status_label.setText(message)
        colors = {"waiting": "#D8B76E", "error": "#D98E9D", "ok": "#79BFA7", "busy": "#93A2E0"}
        self.auth_status_dot.setStyleSheet("color:%s; font-size:15pt;" % colors.get(state, colors["waiting"]))
        self.auth_pill.setText({"waiting": "اتصال لازم است", "error": "اتصال برقرار نشد", "ok": "متصل شد", "busy": "در حال اتصال"}.get(state, "اتصال لازم است"))
        self.auth_login_button.setEnabled(state != "busy")
        self.auth_check_button.setEnabled(state != "busy")
        self.auth_fresh_button.setEnabled(state != "busy")

    def _check_saved_session(self, automatic: bool = False, after_login: bool = False):
        if self._auth_check_in_progress:
            return
        self._auth_check_in_progress = True
        if after_login:
            status_text = "ورود تأیید شد و نشست ذخیره شد؛ در حال برقراری اتصال زنده به بله… این مرحله ممکن است کمی بیشتر از اتصال ساده زمان ببرد، چون اعتبار حساب هم از سرور بررسی می‌شود."
        else:
            status_text = "در حال بررسی نشست ذخیره‌شده و برقراری اتصال زنده به بله…"
        self._set_auth_status(status_text, "busy")

        async def task():
            from ui.auth_flow import verify_saved_session
            client = self._new_agent()._client()
            return await verify_saved_session(client)

        def done(result):
            self._auth_check_in_progress = False
            if result.get("authenticated"):
                self._unlock_app(result.get("account", ""))
            elif result.get("logged") and result.get("transport_connected"):
                self._set_auth_status(
                    "ارتباط شبکه برقرار است، اما بله دسترسی حساب را تأیید نکرد. ممکن است نشست از دستگاه‌های بله خارج شده یا منقضی شده باشد. برای ورود دوباره، «ساخت نشست تازه» را انتخاب کن.",
                    "error",
                )
            elif result.get("logged"):
                self._set_auth_status(
                    "فایل نشست روی این دستگاه وجود دارد، اما اتصال یا تأیید حساب از طرف بله انجام نشد. اینترنت را بررسی کن؛ اگر دستگاه از حساب خارج شده، یک نشست تازه بساز.",
                    "error",
                )
            elif after_login:
                self._set_auth_status(
                    "بله ورود را تأیید کرد، اما فایل نشست در این برنامه پیدا نشد. برای امنیت، دوباره ورود را انجام بده.",
                    "error",
                )
            else:
                self._set_auth_status(
                    "نشست محلی پیدا نشد. شماره موبایل را وارد کن یا یک نشست تازه بساز.",
                    "waiting",
                )

        def failed(error):
            self._auth_check_in_progress = False
            if after_login:
                message = "ورود در بله تأیید شد، اما برنامه نتوانست اتصال زنده را کامل کند: %s" % error
            else:
                message = "بررسی اتصال ناموفق بود: %s" % error
            self._set_auth_status(message, "error")
            if not automatic:
                QMessageBox.warning(self, "اتصال به بله", message)

        self._run_async(task, done, "در حال اتصال به بله…", on_error=failed)

    def _unlock_app(self, account: str = ""):
        self._authenticated = True
        # Defensive guard: if a UI refactor forgets to register the workspace,
        # add it before switching. This prevents QStackedWidget's
        # "widget not contained in stack" warning and keeps auth from appearing
        # stuck after a successful server-side verification.
        if self.root_stack.indexOf(self.app_shell) < 0:
            self.root_stack.addWidget(self.app_shell)
        self._set_auth_status("نشست بله از سمت سرور تأیید شد.", "ok")
        self.root_stack.setCurrentWidget(self.app_shell)
        self.statusBar().show()
        self.statusBar().showMessage("نشست بله از سمت سرور تأیید شد" + (" · " + account if account else ""), 4500)
        # The short-lived verifier is closed after its read-only probe. Avoid
        # claiming a persistent live connection when the UI uses per-action clients.
        self.connection_badge.setText("● نشست تأیید شد" + (" · " + account if account else ""))
        self.header_status.setText("نشست معتبر")
        self.stat_session.setText("تأییدشده")
        self.schedule_timer.start()
        self.refresh_local_overview()
        self.show_page("dashboard")
        self.log("اتصال به حساب بله تأیید شد")

    def _return_to_auth(self, message: str = "برای ادامه، دوباره به بله متصل شو."):
        self._authenticated = False
        if hasattr(self, "schedule_timer"):
            self.schedule_timer.stop()
        self.root_stack.setCurrentWidget(self.auth_page)
        self.statusBar().hide()
        self._set_auth_status(message, "waiting")

    def refresh_status(self, silent: bool = False):
        async def task():
            from ui.auth_flow import verify_saved_session
            client = self._new_agent()._client()
            return await verify_saved_session(client)

        def done(data):
            account = data.get("account", "")
            if data.get("authenticated"):
                self.connection_badge.setText("●  نشست بله تأییدشده" + (" · " + account if account else ""))
                self.header_status.setText("نشست معتبر")
                self.stat_session.setText("تأییدشده")
            elif data.get("logged") and data.get("transport_connected"):
                self.connection_badge.setText("●  اتصال شبکه برقرار؛ حساب تأیید نشد")
                self.header_status.setText("نیاز به ورود مجدد")
                self.stat_session.setText("تأیید نشد")
            elif data.get("logged"):
                self.connection_badge.setText("●  فایل نشست موجود؛ اعتبار نامشخص")
                self.header_status.setText("بررسی ناموفق")
                self.stat_session.setText("نامشخص")
            else:
                self.connection_badge.setText("●  وارد حساب نشده‌اید")
                self.header_status.setText("آفلاین")
                self.stat_session.setText("وارد نشده")
            self.refresh_local_overview()
            if not silent:
                self.log("وضعیت اتصال به‌روزرسانی شد")

        def failed(error: str):
            self.connection_badge.setText("●  وضعیت اتصال نامشخص")
            self.header_status.setText("نامشخص")
            self.stat_session.setText("نامشخص")
            if not silent:
                QMessageBox.warning(self, "وضعیت اتصال", error)

        self._run_async(task, done, "در حال بررسی وضعیت اتصال…", on_error=failed)

    def start_fresh_session(self):
        if QMessageBox.question(
            self,
            "ساخت نشست تازه",
            "یک نشست جداگانه برای ورود ساخته می‌شود. نشست قبلی حذف نخواهد شد و فایل آن روی دستگاه باقی می‌ماند. ادامه می‌دهی؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) != QMessageBox.Yes:
            return
        self.session = "agent-" + uuid.uuid4().hex[:8]
        if hasattr(self, "session_label"):
            self.session_label.setText("نشست: %s" % self.session)
        self.start_login()

    def start_login(self):
        if self._auth_check_in_progress:
            QMessageBox.information(
                self, "بررسی نشست",
                "بررسی نشست ذخیره‌شده هنوز در حال انجام است. پس از پایان آن دوباره تلاش کن.",
            )
            return
        if self.active_login_worker and self.active_login_worker.isRunning():
            QMessageBox.information(
                self, "ورود به بله",
                "فرآیند ورود قبلی هنوز فعال است. لطفاً پنجره کد تأیید را تکمیل کن.",
            )
            return
        phone = self.auth_phone_input.text().strip()
        if not phone:
            QMessageBox.information(self, "شماره موبایل", "ابتدا شماره موبایل را وارد کن.")
            self.auth_phone_input.setFocus()
            return
        warning = (
            "این اتصال از کتابخانه غیررسمی balelink و پروتکل داخلی بله استفاده می‌کند. "
            "ناشر کتابخانه درباره احتمال محدودشدن حساب هشدار داده است. "
            "فایل نشست نیز دسترسی حساب را در اختیار دارنده آن قرار می‌دهد.\n\n"
            "آیا با آگاهی از این ریسک‌ها ادامه می‌دهی؟"
        )
        if QMessageBox.warning(self, "هشدار اتصال غیررسمی", warning, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self._set_auth_status("در حال درخواست کد ورود از بله…", "busy")
        worker = LoginWorker(self.session, phone)
        self.active_login_worker = worker
        self.workers.append(worker)
        worker.input_required.connect(self._handle_login_input)
        worker.succeeded.connect(self._handle_login_success)
        worker.failed.connect(self._handle_login_failed)
        worker.start()

    def _handle_login_input(self, prompt: str):
        worker = self.active_login_worker
        if worker is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("تأیید ورود به بله")
        dialog.setMinimumWidth(390)
        layout = QVBoxLayout(dialog)
        label = QLabel(prompt)
        label.setWordWrap(True)
        layout.addWidget(label)
        field = QLineEdit()
        field.setMinimumHeight(44)
        is_password = "رمز" in prompt
        field.setEchoMode(QLineEdit.Password if is_password else QLineEdit.Normal)
        field.setPlaceholderText("رمز دومرحله‌ای" if is_password else "کد ورود")
        layout.addWidget(field)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        field.returnPressed.connect(dialog.accept)
        field.setFocus()
        value = field.text().strip() if dialog.exec() == QDialog.Accepted else ""
        worker.provide_input(value)

    def _handle_login_success(self, message: str):
        worker = self.sender()
        self._finish_worker(worker)
        self.active_login_worker = None
        # Login/OTP has succeeded.  Now verify that the saved session can open
        # a live connection; do not silently leave the user on a generic spinner.
        self._set_auth_status(
            "کد ورود پذیرفته شد؛ نشست ذخیره شده است. در حال تکمیل اتصال به بله…",
            "busy",
        )
        self._check_saved_session(automatic=False, after_login=True)

    def _handle_login_failed(self, message: str):
        worker = self.sender()
        self._finish_worker(worker)
        self.active_login_worker = None
        self._set_auth_status("ورود ناموفق بود: %s" % message, "error")
        QMessageBox.critical(self, "ورود ناموفق", message)

    def load_dialogs(self):
        async def task():
            agent = self._new_agent()
            client = await agent._connected_client()
            try:
                rows = await client.dialogs(limit=100)
                result = []
                for chat in rows:
                    kind = getattr(chat.kind, "value", str(chat.kind))
                    label = ""
                    try:
                        if chat.is_private:
                            user = await client.user_info(chat.id)
                            label = (user.name or user.username or "") if user else ""
                        elif chat.is_group:
                            group = await client.group_info(chat.id)
                            label = group.title or ""
                    except Exception:
                        pass
                    result.append({"id": int(chat.id), "kind": kind, "label": label or ("گفتگو " + str(chat.id))})
                return result
            finally:
                await client.stop()

        def done(rows):
            self.dialogs_cache = list(rows)
            self.chat_list.clear()
            for row in rows:
                item = QListWidgetItem("%s\nشناسه: %s  ·  %s" % (row["label"], row["id"], row["kind"]))
                item.setData(Qt.UserRole, row)
                self.chat_list.addItem(item)
            self.chat_count_label.setText("%d گفتگو بارگذاری شد." % len(rows))
            self.log("فهرست گفتگوها بارگذاری شد")
        self._run_async(task, done, "در حال دریافت گفتگوها…")

    def filter_chats(self, text: str):
        query = text.strip().casefold()
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            item.setHidden(query not in item.text().casefold())

    def on_chat_selected(self):
        selected = self.chat_list.selectedItems()
        if not selected:
            return
        self.current_chat = selected[0].data(Qt.UserRole)
        self.chat_heading.setText("%s  ·  %s" % (self.current_chat["label"], self.current_chat["id"]))
        self.load_history()

    def load_history(self):
        if not self.current_chat:
            return
        chat = dict(self.current_chat)
        async def task():
            agent = self._new_agent()
            client = await agent._connected_client()
            try:
                rows = await client.history(_chat_target(chat["id"], chat["kind"]), limit=60)
                result = []
                for msg in reversed(rows):
                    body = msg.text or "[%s]" % msg.kind
                    result.append({
                        "id": int(msg.id),
                        "text": body,
                        "out": bool(msg.from_me),
                        "date": msg.date.astimezone().strftime("%Y-%m-%d %H:%M"),
                        "sender": int(msg.sender_id) if msg.sender_id is not None else None,
                    })
                return result
            finally:
                await client.stop()
        self._run_async(task, self.render_messages, "در حال دریافت پیام‌ها…")

    def render_messages(self, rows: list[dict[str, Any]]):
        self.current_messages = rows
        self.message_row_widgets = []
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        if not rows:
            empty = SpatialGlassFrame(radius=22)
            empty.set_dark_mode(self.dark_mode)
            empty.setObjectName("Glass")
            empty.setMaximumWidth(520)
            empty.setMinimumWidth(280)
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(24, 24, 24, 24)
            empty_layout.setSpacing(9)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setPixmap(svg_icon("chats", "#9DA8E8" if self.dark_mode else "#818ACB").pixmap(44, 44))
            empty_layout.addWidget(icon_label)
            title = QLabel("هنوز پیامی برای نمایش وجود ندارد")
            title.setObjectName("SectionTitle")
            title.setAlignment(Qt.AlignCenter)
            detail = QLabel("یک گفتگو از فهرست سمت چپ انتخاب کن یا ابتدا گفتگوها را بارگذاری کن. سپس تاریخچه پیام‌ها در همین قسمت نمایش داده می‌شود.")
            detail.setObjectName("Muted")
            detail.setWordWrap(True)
            detail.setAlignment(Qt.AlignCenter)
            empty_layout.addWidget(title)
            empty_layout.addWidget(detail)
            self.message_layout.addStretch(1)
            self.message_layout.addWidget(empty, alignment=Qt.AlignCenter)
            self.message_layout.addStretch(1)
            self.message_row_widgets = []
            self.filter_messages(self.message_search.text())
            return
        for msg in rows:
            bubble = SpatialGlassFrame(radius=16)
            bubble.set_dark_mode(self.dark_mode)
            bubble.setObjectName("MessageOut" if msg["out"] else "MessageIn")
            bubble.setMaximumWidth(620)
            bubble.setContextMenuPolicy(Qt.CustomContextMenu)
            bubble.customContextMenuRequested.connect(
                lambda pos, m=msg, b=bubble: self.show_message_menu(m, b.mapToGlobal(pos))
            )
            bl = QVBoxLayout(bubble)
            bl.setContentsMargins(14, 10, 14, 10)
            label = QLabel(msg["text"])
            label.setWordWrap(True)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setContextMenuPolicy(Qt.CustomContextMenu)
            label.customContextMenuRequested.connect(
                lambda pos, m=msg, w=label: self.show_message_menu(m, w.mapToGlobal(pos))
            )
            stamp = QLabel(("شما" if msg["out"] else "مخاطب") + "  ·  " + msg["date"] + "  ·  #" + str(msg["id"]))
            stamp.setObjectName("Muted")
            stamp.setStyleSheet("font-size:8pt;")
            bl.addWidget(label)
            bl.addWidget(stamp)
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(3, 2, 3, 2)
            row.setDirection(QHBoxLayout.LeftToRight)
            if msg["out"]:
                row.addStretch(1)
                row.addWidget(bubble)
            else:
                row.addWidget(bubble)
                row.addStretch(1)
            self.message_layout.addWidget(row_widget)
            self.message_row_widgets.append((row_widget, msg))
        self.message_layout.addStretch(1)
        self.filter_messages(self.message_search.text())
        self.message_scroll.verticalScrollBar().setValue(self.message_scroll.verticalScrollBar().maximum())

    def send_chat_message(self):
        if not self.current_chat:
            QMessageBox.information(self, "گفتگو", "ابتدا یک گفتگو انتخاب کنید.")
            return
        text = self.message_input.toPlainText().strip()
        if not text:
            return
        chat = dict(self.current_chat)
        confirm = QMessageBox.question(self, "تأیید ارسال", "این پیام در گفتگو ارسال شود؟\n\n" + text[:600], QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        async def task():
            agent = self._new_agent()
            client = await agent._connected_client()
            try:
                sent = await client.send_text(_chat_target(chat["id"], chat["kind"]), text)
                return sent.id
            finally:
                await client.stop()
        def done(message_id):
            self.message_input.clear()
            self.log("پیام ارسال شد · شناسه %s" % message_id)
            self.load_history()
        self._run_async(task, done, "در حال ارسال پیام…")

    def send_chat_file(self):
        if not self.current_chat:
            QMessageBox.information(self, "گفتگو", "ابتدا یک گفتگو انتخاب کنید.")
            return
        path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل")
        if not path:
            return
        if Path(path).stat().st_size > 50 * 1024 * 1024:
            QMessageBox.warning(self, "محدودیت فایل", "حجم فایل نباید بیشتر از ۵۰ مگابایت باشد.")
            return
        caption, ok = QInputDialog.getText(self, "توضیح فایل", "توضیح (اختیاری):")
        if not ok:
            return
        chat = dict(self.current_chat)
        if QMessageBox.question(self, "تأیید ارسال فایل", "فایل «%s» ارسال شود؟" % Path(path).name, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        async def task():
            from balelink import FileKind
            agent = self._new_agent()
            client = await agent._connected_client()
            try:
                sent = await client.send_file(_chat_target(chat["id"], chat["kind"]), path, kind=FileKind("document"), caption=caption.strip() or None)
                return sent.id
            finally:
                await client.stop()
        self._run_async(task, lambda mid: (self.log("فایل ارسال شد · شناسه %s" % mid), self.load_history()), "در حال ارسال فایل…")

    def draft_chat_reply(self):
        if not self.current_chat:
            QMessageBox.information(self, "پاسخ هوشمند", "ابتدا یک گفتگو انتخاب کنید.")
            return
        choice = QMessageBox.question(
            self, "اشتراک‌گذاری تاریخچه",
            "برای ساخت پاسخ مرتبط، پیام‌های اخیر این گفتگو به سرویس هوش مصنوعی تنظیم‌شده ارسال می‌شوند. ادامه می‌دهید؟",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if choice != QMessageBox.Yes:
            return
        chat = dict(self.current_chat)
        instruction, ok = QInputDialog.getText(self, "دستور پاسخ", "مثلاً کوتاه، محترمانه و صمیمی پاسخ بده:")
        if not ok:
            return
        async def task():
            agent = self._new_agent()
            client = await agent._connected_client()
            try:
                rows = await client.history(_chat_target(chat["id"], chat["kind"]), limit=12)
                if not rows:
                    raise RuntimeError("تاریخچه‌ای برای این گفتگو پیدا نشد.")
                return await agent._draft_from_history(rows, instruction.strip() or "یک پاسخ مناسب بنویس.", share_context=True)
            finally:
                await client.stop()
        def done(draft):
            self.message_input.setPlainText(draft)
            self.log("پاسخ پیشنهادی آماده شد؛ برای ارسال باید خودتان تأیید کنید")
        self._run_async(task, done, "در حال ساخت پاسخ با AI…")

    def apply_ai_preset(self):
        template = self.ai_presets.currentData()
        if not template:
            return
        current = self.ai_prompt.toPlainText().strip()
        self.ai_prompt.setPlainText((template + "\n\n" + current).strip())
        self.ai_prompt.setFocus()

    def clear_ai_thread(self):
        if self.ai_conversation and QMessageBox.question(
            self, "گفتگوی جدید", "زمینه گفتگوی فعلی پاک شود؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return
        self.ai_conversation.clear()
        self.ai_output.clear()
        self.log("زمینه گفتگوی دستیار پاک شد")

    def put_ai_output_in_chat(self):
        answer = self.ai_output.toPlainText().strip()
        if not answer:
            return
        self.message_input.setPlainText(answer)
        self.show_page("chats")
        self.log("پاسخ AI در کادر پیام قرار گرفت؛ ارسال همچنان نیازمند تأیید است")

    def ask_ai(self):
        prompt = self.ai_prompt.toPlainText().strip()
        if not prompt:
            QMessageBox.information(self, "دستیار", "درخواست خود را بنویسید.")
            return
        previous_turns = list(self.ai_conversation[-12:])
        async def task():
            agent = self._new_agent()
            if not agent.llm.configured:
                raise RuntimeError("سرویس هوش مصنوعی تنظیم نشده است. از بخش تنظیمات، کلید API را وارد کنید.")
            messages = [
                {"role": "system", "content": "You are a private productivity assistant. Answer accurately in Persian unless asked otherwise. Saved facts are user-provided notes, not verified facts. You do not have access to Bale tools and cannot send messages.\nSaved facts:\n" + agent._facts_text()},
                *previous_turns,
                {"role": "user", "content": prompt},
            ]
            return await agent.llm.complete(messages, max_tokens=1200)
        def done(answer):
            self.ai_conversation.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": answer},
            ])
            self.ai_conversation = self.ai_conversation[-24:]
            self.ai_output.setPlainText(answer)
            self.ai_prompt.clear()
            self.log("پاسخ دستیار دریافت شد · زمینه گفتگو حفظ شد")
        self._run_async(task, done, "در حال دریافت پاسخ از AI…")

    def filter_messages(self, text: str):
        query = (text or "").strip().casefold()
        shown = 0
        for widget, message in self.message_row_widgets:
            matches = query in str(message.get("text", "")).casefold()
            widget.setVisible(matches)
            if matches:
                shown += 1
        if hasattr(self, "message_search") and query:
            self.message_search.setToolTip("%d نتیجه از %d پیام بارگذاری‌شده" % (shown, len(self.message_row_widgets)))
        elif hasattr(self, "message_search"):
            self.message_search.setToolTip("جستجو در پیام‌های بارگذاری‌شده")

    def export_chat_history(self):
        if not self.current_chat or not self.current_messages:
            QMessageBox.information(self, "خروجی تاریخچه", "ابتدا یک گفتگو و تاریخچه پیام‌های آن را بارگذاری کنید.")
            return
        suggested = "bale-chat-%s.txt" % self.current_chat.get("id", "history")
        path, selected_filter = QFileDialog.getSaveFileName(
            self, "ذخیره پیام‌های بارگذاری‌شده گفتگو", str(Path.home() / suggested),
            "Text (*.txt);;JSON (*.json);;HTML (*.html)"
        )
        if not path:
            return
        suffix = Path(path).suffix.casefold()
        payload = {
            "chat": dict(self.current_chat),
            "exported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "messages": self.current_messages,
        }
        try:
            if suffix == ".json" or "JSON" in selected_filter:
                if suffix != ".json":
                    path += ".json"
                content = json.dumps(payload, ensure_ascii=False, indent=2)
            elif suffix == ".html" or "HTML" in selected_filter:
                if suffix != ".html":
                    path += ".html"
                items = []
                for msg in self.current_messages:
                    side = "sent" if msg["out"] else "received"
                    who = "شما" if msg["out"] else "مخاطب"
                    items.append(
                        '<article class="%s"><div>%s</div><small>%s · #%s</small></article>' %
                        (side, html.escape(str(msg["text"])).replace("\n", "<br>"), who, html.escape(str(msg["id"])))
                    )
                content = "<!doctype html><html lang='fa' dir='rtl'><meta charset='utf-8'><title>تاریخچه بله</title><style>body{font-family:Segoe UI,Tahoma,sans-serif;background:#111827;color:#eef2f8;max-width:900px;margin:36px auto;padding:0 20px}.sent,.received{padding:14px 16px;margin:12px 0;border:1px solid #334155;border-radius:16px;max-width:78%}.sent{margin-right:auto;background:#1e3a5f}.received{margin-left:auto;background:#1f2937}small{display:block;color:#9fb0c6;margin-top:8px}</style><h1>%s</h1>%s</html>" % (
                    html.escape(str(self.current_chat.get("label", "گفتگو"))), "".join(items)
                )
            else:
                if suffix != ".txt":
                    path += ".txt"
                lines = ["تاریخچه گفتگو: %s (%s)" % (self.current_chat.get("label", "-"), self.current_chat.get("id", "-")), "خروجی: %s" % datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"), "=" * 60]
                for msg in self.current_messages:
                    lines.append("[%s] %s: %s" % (msg.get("date", ""), "شما" if msg.get("out") else "مخاطب", msg.get("text", "")))
                content = "\n\n".join(lines)
            Path(path).write_text(content, encoding="utf-8")
            self.log("خروجی تاریخچه ذخیره شد")
            QMessageBox.information(self, "خروجی تاریخچه", "فایل ذخیره شد:\n%s" % path)
        except OSError as exc:
            QMessageBox.critical(self, "خطای ذخیره", str(exc))

    def show_message_menu(self, message: dict[str, Any], global_pos):
        menu = QMenu(self)
        copy_action = menu.addAction("کپی متن پیام")
        reply_action = menu.addAction("پاسخ به همین پیام")
        react_action = menu.addAction("افزودن واکنش")
        forward_action = menu.addAction("فوروارد به گفتگو…")
        menu.addSeparator()
        help_action = menu.addAction("راهنمای این بخش")
        help_action.setIcon(svg_icon("help", "#9DA8E8" if self.dark_mode else "#747EC0"))
        chosen = menu.exec(global_pos)
        if chosen == copy_action:
            QApplication.clipboard().setText(str(message.get("text", "")))
            self.log("متن پیام کپی شد")
        elif chosen == reply_action:
            self.reply_to_message(message)
        elif chosen == react_action:
            self.react_to_message(message)
        elif chosen == forward_action:
            self.forward_message(message)
        elif chosen == help_action:
            self.show_help_topic(
                "chats", "راهنمای منوی پیام",
                "از کپی متن برای برداشتن محتوای پیام استفاده کن. «پاسخ به همین پیام» متن تازه‌ای را به همان پیام متصل می‌کند. واکنش، یک واکنش به پیام اضافه می‌کند و فوروارد پیام را به گفتگوی دیگری می‌فرستد. مقصد و محتوای عملیات را پیش از تأیید بررسی کن."
            )

    def _message_from_current_chat(self, client, chat: dict[str, Any], message_id: int):
        async def lookup():
            rows = await client.history(_chat_target(chat["id"], chat["kind"]), limit=100)
            found = next((row for row in rows if int(row.id) == int(message_id)), None)
            if found is None:
                raise RuntimeError("پیام موردنظر در ۱۰۰ پیام اخیر پیدا نشد.")
            return found
        return lookup()

    def reply_to_message(self, message: dict[str, Any]):
        if not self.current_chat:
            return
        text, ok = QInputDialog.getMultiLineText(self, "پاسخ به پیام", "متن پاسخ:")
        if not ok or not text.strip():
            return
        if QMessageBox.question(self, "تأیید پاسخ", "پاسخ به پیام شماره %s ارسال شود؟\n\n%s" % (message["id"], text[:400]), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        chat = dict(self.current_chat)
        async def task():
            client = await self._new_agent()._connected_client()
            try:
                original = await self._message_from_current_chat(client, chat, message["id"])
                sent = await original.reply(text.strip())
                return sent.id
            finally:
                await client.stop()
        self._run_async(task, lambda mid: (self.log("پاسخ ارسال شد · شناسه %s" % mid), self.load_history()), "در حال ارسال پاسخ…")

    def react_to_message(self, message: dict[str, Any]):
        if not self.current_chat:
            return
        emoji, ok = QInputDialog.getText(self, "واکنش به پیام", "ایموجی واکنش:", QLineEdit.Normal, "👍")
        if not ok or not emoji.strip():
            return
        if QMessageBox.question(self, "تأیید واکنش", "واکنش %s روی پیام %s ثبت شود؟" % (emoji.strip(), message["id"]), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        chat = dict(self.current_chat)
        async def task():
            client = await self._new_agent()._connected_client()
            try:
                original = await self._message_from_current_chat(client, chat, message["id"])
                await original.react(emoji.strip())
                return True
            finally:
                await client.stop()
        self._run_async(task, lambda _: self.log("واکنش ثبت شد"), "در حال ثبت واکنش…")

    def forward_message(self, message: dict[str, Any]):
        if not self.current_chat:
            return
        if not self.dialogs_cache:
            QMessageBox.information(self, "فوروارد", "ابتدا فهرست گفتگوها را بارگذاری کنید تا مقصد را انتخاب کنید.")
            return
        destinations = [x for x in self.dialogs_cache if int(x["id"]) != int(self.current_chat["id"])]
        if not destinations:
            QMessageBox.information(self, "فوروارد", "گفتگوی دیگری برای انتخاب وجود ندارد.")
            return
        labels = ["%s · %s" % (x["label"], x["id"]) for x in destinations]
        selected, ok = QInputDialog.getItem(self, "فوروارد پیام", "گفتگوی مقصد:", labels, 0, False)
        if not ok:
            return
        target = destinations[labels.index(selected)]
        if QMessageBox.question(self, "تأیید فوروارد", "پیام شماره %s به «%s» فوروارد شود؟" % (message["id"], target["label"]), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        source = dict(self.current_chat)
        destination = dict(target)
        async def task():
            client = await self._new_agent()._connected_client()
            try:
                original = await self._message_from_current_chat(client, source, message["id"])
                await original.forward(_chat_target(destination["id"], destination["kind"]))
                return True
            finally:
                await client.stop()
        self._run_async(task, lambda _: self.log("پیام به «%s» فوروارد شد" % destination["label"]), "در حال فوروارد پیام…")

    def schedule_chat_message(self):
        if not self.current_chat:
            QMessageBox.information(self, "زمان‌بندی", "ابتدا یک گفتگو انتخاب کنید.")
            return
        chat = dict(self.current_chat)
        dialog = ScheduleMessageDialog(chat.get("label", str(chat["id"])), self.message_input.toPlainText(), self)
        if dialog.exec() != QDialog.Accepted:
            return
        text_value, scheduled_at = dialog.values()
        entry = {
            "id": uuid.uuid4().hex[:12],
            "chat": chat,
            "text": text_value,
            "scheduled_at": scheduled_at,
            "created_at": int(datetime.now().timestamp()),
            "status": "pending",
        }
        self.app_state.setdefault("scheduled_messages", []).append(entry)
        self._save_app_state()
        self.refresh_schedule_list()
        self.message_input.clear()
        self.log("پیام برای %s زمان‌بندی شد" % datetime.fromtimestamp(scheduled_at).strftime("%Y-%m-%d %H:%M"))

    def refresh_schedule_list(self):
        if not hasattr(self, "schedule_list"):
            return
        rows = sorted(self.app_state.get("scheduled_messages", []), key=lambda x: int(x.get("scheduled_at", 0)))
        self.schedule_list.clear()
        labels = {"pending": "در انتظار", "sending": "در حال ارسال", "sent": "ارسال‌شده", "failed": "ناموفق", "cancelled": "لغوشده"}
        pending = 0
        for entry in rows:
            when = datetime.fromtimestamp(int(entry.get("scheduled_at", 0))).astimezone().strftime("%Y/%m/%d  %H:%M")
            chat = entry.get("chat", {})
            state = labels.get(entry.get("status", "pending"), entry.get("status", "نامشخص"))
            if entry.get("status") == "pending":
                pending += 1
            preview = str(entry.get("text", "")).replace("\n", " ")[:90]
            item = QListWidgetItem("%s  ·  %s\n%s\n%s" % (when, chat.get("label", chat.get("id", "گفتگو")), preview, state))
            item.setData(Qt.UserRole, entry.get("id"))
            if entry.get("status") == "failed" and entry.get("error"):
                item.setToolTip(str(entry.get("error")))
            self.schedule_list.addItem(item)
        if hasattr(self, "schedule_summary"):
            self.schedule_summary.setText("%d پیام در انتظار · %d مورد در کل" % (pending, len(rows)))
        if hasattr(self, "stat_scheduled"):
            self.stat_scheduled.setText(str(pending))

    def cancel_scheduled_message(self):
        item = self.schedule_list.currentItem()
        if not item:
            return
        entry_id = item.data(Qt.UserRole)
        entries = self.app_state.get("scheduled_messages", [])
        entry = next((x for x in entries if x.get("id") == entry_id), None)
        if not entry or entry.get("status") != "pending":
            QMessageBox.information(self, "زمان‌بندی", "فقط پیام‌های در انتظار قابل لغو هستند.")
            return
        if QMessageBox.question(self, "لغو زمان‌بندی", "این پیام از صف زمان‌بندی حذف شود؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        entries.remove(entry)
        self._save_app_state()
        self.refresh_schedule_list()
        self.log("زمان‌بندی پیام لغو شد")

    def retry_scheduled_message(self):
        item = self.schedule_list.currentItem()
        if not item:
            return
        entry_id = item.data(Qt.UserRole)
        entry = next((x for x in self.app_state.get("scheduled_messages", []) if x.get("id") == entry_id), None)
        if not entry or entry.get("status") != "failed":
            QMessageBox.information(self, "ارسال مجدد", "ابتدا یک پیام با وضعیت ناموفق انتخاب کنید.")
            return
        if QMessageBox.question(self, "ارسال مجدد", "ارسال دوباره این پیام به «%s» انجام شود؟\n\n%s" % (entry.get("chat", {}).get("label", "گفتگو"), str(entry.get("text", ""))[:500]), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self.send_scheduled_message(entry)

    def check_scheduled_messages(self):
        entries = self.app_state.get("scheduled_messages", [])
        if any(x.get("status") in {"prompting", "sending"} for x in entries):
            return
        now = int(datetime.now().timestamp())
        entry = next((x for x in entries if x.get("status") == "pending" and int(x.get("scheduled_at", 0)) <= now), None)
        if not entry:
            return
        entry["status"] = "prompting"
        self._save_app_state()
        chat = entry.get("chat", {})
        box = QMessageBox(self)
        box.setWindowTitle("زمان ارسال پیام فرا رسیده است")
        box.setIcon(QMessageBox.Information)
        box.setText("پیام زمان‌بندی‌شده آماده ارسال است.")
        box.setInformativeText("مقصد: %s\n\n%s" % (chat.get("label", chat.get("id", "-")), str(entry.get("text", ""))[:700]))
        send_button = box.addButton("ارسال اکنون", QMessageBox.AcceptRole)
        later_button = box.addButton("۵ دقیقه دیگر", QMessageBox.DestructiveRole)
        cancel_button = box.addButton("لغو پیام", QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked == send_button:
            self.send_scheduled_message(entry)
        elif clicked == later_button:
            entry["status"] = "pending"
            entry["scheduled_at"] = now + 300
            self._save_app_state()
            self.log("یادآوری پیام ۵ دقیقه به تعویق افتاد")
        elif clicked == cancel_button:
            entry["status"] = "cancelled"
            self._save_app_state()
            self.log("پیام زمان‌بندی‌شده لغو شد")
        else:
            entry["status"] = "pending"
            entry["scheduled_at"] = now + 60
            self._save_app_state()
        self.refresh_schedule_list()

    def send_scheduled_message(self, entry: dict[str, Any]):
        entry["status"] = "sending"
        self._save_app_state()
        chat = dict(entry.get("chat", {}))
        text_value = str(entry.get("text", ""))
        async def task():
            client = await self._new_agent()._connected_client()
            try:
                sent = await client.send_text(_chat_target(chat["id"], chat["kind"]), text_value)
                return sent.id
            finally:
                await client.stop()
        def done(message_id):
            entry["status"] = "sent"
            entry["sent_message_id"] = int(message_id)
            entry["sent_at"] = int(datetime.now().timestamp())
            self._save_app_state()
            self.refresh_schedule_list()
            self.log("پیام زمان‌بندی‌شده ارسال شد · شناسه %s" % message_id)
        def failed(error):
            entry["status"] = "failed"
            entry["error"] = error[:500]
            self._save_app_state()
            self.refresh_schedule_list()
            QMessageBox.warning(self, "ارسال ناموفق", "پیام زمان‌بندی‌شده ارسال نشد:\n%s" % error)
        self._run_async(task, done, "در حال ارسال پیام زمان‌بندی‌شده…", on_error=failed)

    def refresh_local_lists(self):
        self.config = AgentConfig(self.home)
        self.fact_list.clear()
        for index, fact in enumerate(self.config.data["facts"], 1):
            item = QListWidgetItem("%d. %s" % (index, fact))
            item.setData(Qt.UserRole, index)
            self.fact_list.addItem(item)
        self.rule_list.clear()
        for rule in self.config.data["rules"]:
            state = "فعال" if rule.get("enabled", True) else "غیرفعال"
            mode = " · دارای مجوز پاسخ خودکار" if rule.get("auto") else " · پیشنهادی"
            label = "[%s] %s  ·  %s%s\nکلیدواژه‌ها: %s" % (rule.get("id"), rule.get("name"), state, mode, ", ".join(rule.get("keywords", [])))
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, rule.get("id"))
            self.rule_list.addItem(item)
        self.trust_list.clear()
        for sender in self.config.data["trusted_senders"]:
            self.trust_list.addItem(str(sender))
        self.refresh_local_overview()

    def add_fact(self):
        try:
            self.config.add_fact(self.fact_input.text())
            self.fact_input.clear()
            self.refresh_local_lists()
            self.log("یادداشت ذخیره شد")
        except Exception as exc:
            QMessageBox.warning(self, "حافظه", str(exc))

    def remove_fact(self):
        item = self.fact_list.currentItem()
        if not item:
            return
        try:
            self.config.remove_fact(int(item.data(Qt.UserRole)))
            self.refresh_local_lists()
            self.log("یادداشت حذف شد")
        except Exception as exc:
            QMessageBox.warning(self, "حافظه", str(exc))

    def add_rule(self):
        dialog = AddRuleDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        name, keywords, reply, sender_strings = dialog.values()
        try:
            sender_ids = [int(x) for x in sender_strings]
            self.config.add_rule(name, keywords, reply, sender_ids, auto=False)
            self.refresh_local_lists()
            self.log("قانون پاسخ پیشنهادی ساخته شد")
        except Exception as exc:
            QMessageBox.warning(self, "قانون پاسخ", str(exc))

    def toggle_rule(self):
        item = self.rule_list.currentItem()
        if not item:
            return
        rule_id = item.data(Qt.UserRole)
        for rule in self.config.data["rules"]:
            if str(rule.get("id")) == str(rule_id):
                rule["enabled"] = not rule.get("enabled", True)
                self.config.save()
                self.refresh_local_lists()
                self.log("وضعیت قانون تغییر کرد")
                return

    def remove_rule(self):
        item = self.rule_list.currentItem()
        if not item:
            return
        rule_id = item.data(Qt.UserRole)
        try:
            self.config.remove_rule(str(rule_id))
            self.refresh_local_lists()
            self.log("قانون حذف شد")
        except Exception as exc:
            QMessageBox.warning(self, "قوانین", str(exc))

    def add_trusted(self):
        try:
            value = int(self.trust_input.text().strip())
            if value <= 0:
                raise ValueError("شناسه باید عددی مثبت باشد.")
            if value not in self.config.data["trusted_senders"]:
                self.config.data["trusted_senders"].append(value)
                self.config.save()
            self.trust_input.clear()
            self.refresh_local_lists()
        except Exception as exc:
            QMessageBox.warning(self, "مخاطبان مورد اعتماد", str(exc))

    def remove_trusted(self):
        item = self.trust_list.currentItem()
        if not item:
            return
        value = int(item.text())
        if value in self.config.data["trusted_senders"]:
            self.config.data["trusted_senders"].remove(value)
            self.config.save()
        self.refresh_local_lists()

    def load_settings_values(self):
        self.config = AgentConfig(self.home)
        if not self.base_url_input.hasFocus():
            self.base_url_input.setText(self.config.data.get("base_url") or "https://api.gapgpt.app/v1")
        if not self.model_input.hasFocus():
            self.model_input.setText(self.config.data.get("model") or "gpt-4o-mini")
        if not self.style_input.hasFocus():
            self.style_input.setPlainText(self.config.data.get("style") or "")
        self.session_label.setText("نشست: %s" % self.session)
        self.data_path_label.setText("مسیر داده‌ها: %s" % self.home)

    def save_ai_settings(self):
        try:
            base_url = self.base_url_input.text().strip()
            model = self.model_input.text().strip()
            if base_url:
                self.config.set_base_url(base_url)
            if model:
                self.config.set_model(model)
            token = self.api_key_input.text().strip()
            if token:
                self.config.set_api_key(token)
                self.api_key_input.clear()
            self.refresh_local_overview()
            self.log("تنظیمات هوش مصنوعی ذخیره شد")
            QMessageBox.information(self, "تنظیمات", "تنظیمات هوش مصنوعی ذخیره شد.")
        except Exception as exc:
            QMessageBox.critical(self, "تنظیمات", str(exc))

    def clear_api_key(self):
        if QMessageBox.question(self, "پاک‌کردن کلید", "کلید ذخیره‌شده پاک شود؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self.config.clear_api_key()
        self.refresh_local_overview()
        self.log("کلید API پاک شد")

    def test_ai(self):
        async def task():
            agent = self._new_agent()
            if not agent.llm.configured:
                raise RuntimeError("کلید API تنظیم نشده است؛ یا از یک سرویس محلی localhost استفاده کنید.")
            return await agent.llm.complete([
                {"role": "system", "content": "Reply with exactly: Bale Agent connection OK"},
                {"role": "user", "content": "Connection test"},
            ], max_tokens=30)
        self._run_async(task, lambda answer: QMessageBox.information(self, "آزمایش AI", "پاسخ مدل:\n" + answer), "در حال آزمایش سرویس AI…")

    def save_style(self):
        try:
            self.config.set_style(self.style_input.toPlainText())
            self.log("سبک نگارش ذخیره شد")
            QMessageBox.information(self, "سبک نگارش", "سبک نگارش ذخیره شد.")
        except Exception as exc:
            QMessageBox.warning(self, "سبک نگارش", str(exc))

    def clear_style(self):
        self.config.clear_style()
        self.style_input.clear()
        self.log("سبک نگارش پاک شد")

    def logout(self):
        if QMessageBox.question(self, "خروج از حساب", "از حساب بله خارج شوید و فایل نشست ذخیره‌شده حذف شود؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        async def task():
            agent = self._new_agent()
            client = agent._client()
            if not client.is_logged_in:
                return "نشستی برای خروج وجود ندارد."
            await client.logout()
            return "از حساب خارج شدید و نشست حذف شد."
        def done(message):
            QMessageBox.information(self, "خروج", message)
            self._return_to_auth("از حساب خارج شدی. برای ورود دوباره شماره موبایل را وارد کن.")
        self._run_async(task, done, "در حال خروج از حساب…")


    def closeEvent(self, event):
        active = [worker for worker in self.workers if worker.isRunning()]
        if active:
            QMessageBox.information(
                self, "عملیات در حال اجراست",
                "یک یا چند عملیات هنوز در حال اجرا هستند. پس از پایان آن‌ها دوباره برنامه را ببندید."
            )
            event.ignore()
            return
        event.accept()

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    window = LegacyMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
