#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bale Agent Desktop — rebuilt UI entry point."""
from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import RebuiltMainWindow

APP_NAME = "Bale Agent Desktop"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Bale Agent")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    window = RebuiltMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
