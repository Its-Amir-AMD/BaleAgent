from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QLineEdit

from legacy_app import LegacyMainWindow
from .components.icons import svg_icon
from .components import AmbientCanvas, GlassPanel, DockButton
from .theme import ThemeManager


NAV_ITEMS = [
    ("dashboard", "داشبورد"),
    ("chats", "گفتگوها"),
    ("assistant", "دستیار هوشمند"),
    ("automation", "اتوماسیون"),
    ("schedule", "زمان‌بندی"),
    ("settings", "تنظیمات"),
    ("help", "راهنما"),
]


class RebuiltMainWindow(LegacyMainWindow):
    """v2 UI shell. Existing account/network workflows remain inherited."""

    def _build_auth_page(self) -> QWidget:
        page = AmbientCanvas()
        page.setObjectName("AuthPage")
        page.setLayoutDirection(Qt.RightToLeft)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(28, 24, 28, 22)
        outer.addStretch(1)

        card = GlassPanel(radius=28, variant="liquid", interactive=True)
        card.setObjectName("AuthCard")
        card.setMaximumWidth(570)
        card.setMinimumWidth(470)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(34, 30, 34, 30)
        cl.setSpacing(15)

        brand_row = QHBoxLayout()
        mark = GlassPanel(radius=16, variant="liquid", interactive=True)
        mark.setFixedSize(54, 54)
        ml = QVBoxLayout(mark); ml.setContentsMargins(0, 0, 0, 0)
        logo = QLabel(); logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(svg_icon("chats", "#A7A9E8").pixmap(30, 30))
        ml.addWidget(logo)
        brand_row.addWidget(mark)
        brand_stack = QVBoxLayout(); brand_stack.setSpacing(1)
        brand = QLabel("BALE AGENT"); brand.setObjectName("Brand")
        brand_stack.addWidget(brand)
        version = QLabel("DESKTOP WORKSPACE  ·  REBUILT UI")
        version.setObjectName("Muted")
        version.setStyleSheet("font-size:8pt; letter-spacing:1px;")
        brand_stack.addWidget(version)
        brand_row.addLayout(brand_stack)
        brand_row.addStretch(1)
        self.auth_pill = QLabel("اتصال لازم است"); self.auth_pill.setObjectName("Pill")
        brand_row.addWidget(self.auth_pill, alignment=Qt.AlignVCenter)
        cl.addLayout(brand_row)

        title = QLabel("به فضای کاری بله خوش آمدی")
        title.setObjectName("PageTitle")
        cl.addWidget(title)
        subtitle = QLabel("برای ادامه، حساب بله را متصل کن. فضای اصلی پس از تأیید اتصال در دسترس قرار می‌گیرد.")
        subtitle.setObjectName("Muted"); subtitle.setWordWrap(True)
        cl.addWidget(subtitle)

        status = GlassPanel(radius=15, variant="raised", interactive=False)
        sl = QHBoxLayout(status); sl.setContentsMargins(14, 11, 14, 11)
        self.auth_status_dot = QLabel("●")
        self.auth_status_dot.setStyleSheet("color:#B78D50; font-size:14pt;")
        sl.addWidget(self.auth_status_dot)
        self.auth_status_label = QLabel("برای ورود، شماره موبایل را وارد کن یا نشست ذخیره‌شده را بررسی کن.")
        self.auth_status_label.setObjectName("SectionTitle"); self.auth_status_label.setWordWrap(True)
        sl.addWidget(self.auth_status_label, 1)
        cl.addWidget(status)

        phone_label = QLabel("شماره موبایل")
        phone_label.setObjectName("SectionTitle")
        cl.addWidget(phone_label)
        self.auth_phone_input = QLineEdit()
        self.auth_phone_input.setPlaceholderText("مثلاً 09xxxxxxxxx یا +98…")
        self.auth_phone_input.setLayoutDirection(Qt.LeftToRight)
        self.auth_phone_input.setMinimumHeight(48)
        self.auth_phone_input.setObjectName("auth_phone_input")
        self.auth_phone_input.returnPressed.connect(self.start_login)
        cl.addWidget(self.auth_phone_input)

        self.auth_login_button = QPushButton("ورود و اتصال به بله")
        self.auth_login_button.setObjectName("Primary")
        self.auth_login_button.setMinimumHeight(48)
        self.auth_login_button.clicked.connect(self.start_login)
        cl.addWidget(self.auth_login_button)
        self.auth_check_button = QPushButton("بررسی نشست ذخیره‌شده")
        self.auth_check_button.setMinimumHeight(42)
        self.auth_check_button.clicked.connect(lambda: self._check_saved_session(automatic=False))
        cl.addWidget(self.auth_check_button)
        self.auth_fresh_button = QPushButton("ساخت نشست تازه")
        self.auth_fresh_button.setObjectName("Secondary")
        self.auth_fresh_button.clicked.connect(self.start_fresh_session)
        cl.addWidget(self.auth_fresh_button)

        warning = QLabel("اتصال از طریق کتابخانه غیررسمی balelink انجام می‌شود و ممکن است با ریسک محدودیت حساب همراه باشد. فایل نشست را مانند گذرواژه محافظت کن.")
        warning.setWordWrap(True)
        warning.setStyleSheet("color:#A77C54; background:rgba(201,173,114,34); border:1px solid rgba(201,173,114,85); border-radius:12px; padding:10px;")
        cl.addWidget(warning)
        hint = QLabel("کد تأیید و رمز دومرحله‌ای فقط در پنجره ورود درخواست می‌شوند؛ آن‌ها را برای هیچ‌کس ارسال نکن.")
        hint.setObjectName("Muted"); hint.setWordWrap(True)
        cl.addWidget(hint)

        center = QHBoxLayout(); center.addStretch(1); center.addWidget(card); center.addStretch(1)
        outer.addLayout(center)
        outer.addStretch(1)
        footer = QLabel("BALE AGENT  /  PRIVATE DESKTOP WORKSPACE")
        footer.setObjectName("Muted"); footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size:8pt; letter-spacing:1.2px;")
        outer.addWidget(footer)
        return page

    def _build_shell(self):
        self.nav_buttons = {}
        self.root_stack = QStackedWidget()
        self.root_stack.setObjectName("RootStack")
        self.auth_page = self._build_auth_page()
        self.root_stack.addWidget(self.auth_page)

        self.app_shell = AmbientCanvas()
        self.app_shell.setObjectName("Root")
        self.app_shell.setLayoutDirection(Qt.RightToLeft)
        root_layout = QVBoxLayout(self.app_shell)
        root_layout.setContentsMargins(20, 16, 20, 14)
        root_layout.setSpacing(14)

        topbar = GlassPanel(radius=22, variant="liquid", interactive=True)
        topbar.setObjectName("Topbar")
        topbar.setFixedHeight(76)
        top = QHBoxLayout(topbar); top.setContentsMargins(20, 10, 20, 10); top.setSpacing(12)
        brand_mark = QLabel()
        brand_mark.setFixedSize(38, 38)
        brand_mark.setAlignment(Qt.AlignCenter)
        brand_mark.setPixmap(svg_icon("chats", "#9DA8E8" if not self.dark_mode else "#C6C8FF").pixmap(25, 25))
        top.addWidget(brand_mark)
        title_stack = QVBoxLayout(); title_stack.setSpacing(1)
        self.top_title = QLabel("داشبورد"); self.top_title.setObjectName("PageTitle")
        self.top_title.setStyleSheet("font-size:14pt;")
        self.top_subtitle = QLabel("وضعیت کلی حساب و ابزارهای پرکاربرد")
        self.top_subtitle.setObjectName("Muted")
        self.top_subtitle.setStyleSheet("font-size:8.5pt;")
        title_stack.addWidget(self.top_title); title_stack.addWidget(self.top_subtitle)
        top.addLayout(title_stack); top.addStretch(1)

        self.connection_badge = QLabel("● نشست تأییدشده"); self.connection_badge.setObjectName("Pill")
        top.addWidget(self.connection_badge)
        self.header_status = QLabel("نشست معتبر"); self.header_status.hide()

        self.theme_button = QPushButton()
        self.theme_button.setObjectName("IconButton")
        self.theme_button.setToolTip("تغییر پوسته روشن و تاریک")
        self.theme_button.clicked.connect(self.toggle_theme)
        top.addWidget(self.theme_button)
        refresh = QPushButton()
        refresh.setObjectName("IconButton")
        refresh.setToolTip("بررسی دوباره اتصال")
        refresh.setIcon(svg_icon("refresh", "#79BDA8")); refresh.setIconSize(QSize(19, 19))
        refresh.clicked.connect(self.refresh_status)
        top.addWidget(refresh)
        root_layout.addWidget(topbar)

        self.pages = QStackedWidget()
        self.pages.setObjectName("PageStack")
        self.page_map = {
            "dashboard": self._build_dashboard(),
            "chats": self._build_chats(),
            "assistant": self._build_assistant(),
            "automation": self._build_automation(),
            "schedule": self._build_schedule_page(),
            "settings": self._build_settings(),
            "help": self._build_help_page(),
        }
        for page in self.page_map.values():
            self.pages.addWidget(page)
        root_layout.addWidget(self.pages, 1)

        dock_row = QHBoxLayout(); dock_row.addStretch(1)
        self.dock = GlassPanel(radius=26, variant="dock", interactive=False)
        self.dock.setObjectName("Dock")
        self.dock.setFixedHeight(68)
        self.dock.setMaximumWidth(520)
        dock_layout = QHBoxLayout(self.dock)
        dock_layout.setContentsMargins(10, 7, 10, 7)
        dock_layout.setSpacing(7)
        for key, label in NAV_ITEMS:
            button = DockButton(key, label, svg_icon)
            button.setProperty("active", key == "dashboard")
            button.clicked.connect(lambda checked=False, k=key: self.show_page(k))
            self.nav_buttons[key] = button
            dock_layout.addWidget(button)
        dock_row.addWidget(self.dock); dock_row.addStretch(1)
        root_layout.addLayout(dock_row)

        # Both top-level pages must be registered in the root stack. The auth
        # page is added above; without adding app_shell here, Qt ignores the
        # later setCurrentWidget(app_shell) call and leaves the user on login.
        if self.root_stack.indexOf(self.app_shell) < 0:
            self.root_stack.addWidget(self.app_shell)

        self.setCentralWidget(self.root_stack)
        self.root_stack.setCurrentWidget(self.auth_page)
        self.statusBar().hide()
        self._install_context_help()

    def _page(self, title: str, subtitle: str = ""):
        page = QWidget()
        page.setObjectName("Page")
        page.setLayoutDirection(Qt.RightToLeft)
        page.setProperty("guide_title", title or "راهنمای صفحه")
        page.setProperty("guide_body", subtitle or "این صفحه شامل ابزارهای مرتبط با همین بخش است.")
        page.setProperty("guide_topic", self._topic_for_page_title(title))
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 4, 8, 5)
        layout.setSpacing(14)
        return page, layout

    def _panel(self, title: str = ""):
        panel = GlassPanel(radius=21, variant="material", interactive=True)
        panel.setObjectName("GlassPanel")
        if title:
            panel.setProperty("guide_title", title)
            panel.setProperty("guide_body", self._section_help(title))
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(17, 15, 17, 16)
        layout.setSpacing(11)
        if title:
            label = QLabel(title); label.setObjectName("SectionTitle")
            layout.addWidget(label)
        return panel, layout

    def _stat(self, title: str, value: str, detail: str):
        accents = ["#9DA8E8", "#79BDA8", "#D49CB3", "#C9AD72", "#8EB7DE"]
        accent = accents[self._stat_index % len(accents)]
        self._stat_index += 1
        card = GlassPanel(radius=18, variant="material", interactive=True)
        card.setObjectName("StatCard")
        layout = QVBoxLayout(card); layout.setContentsMargins(15, 13, 15, 13); layout.setSpacing(6)
        label = QLabel(title); label.setObjectName("Muted")
        number = QLabel(value); number.setStyleSheet("font-size:22pt; font-weight:760; color:%s;" % accent)
        info = QLabel(detail); info.setObjectName("Muted"); info.setStyleSheet("font-size:8.5pt;")
        layout.addWidget(label); layout.addWidget(number); layout.addWidget(info)
        return card, number

    def _build_dashboard(self):
        from .pages.dashboard import build_dashboard
        return build_dashboard(self)

    def _build_chats(self):
        from .pages.chats import build_chats
        return build_chats(self)

    def render_messages(self, rows: list[dict[str, Any]]):
        from .pages.chats import render_messages
        return render_messages(self, rows)

    def _refresh_dock_icons(self):
        if not hasattr(self, "nav_buttons"):
            return
        active = "#777FC1" if not self.dark_mode else "#D1D2FF"
        normal = "#858CA4" if not self.dark_mode else "#ADB2CB"
        for key, button in self.nav_buttons.items():
            button.set_icon_tint(active if button.property("active") else normal)
        if hasattr(self, "theme_button"):
            self.theme_button.setIcon(svg_icon("sun" if self.dark_mode else "moon", active))
        if hasattr(self, "app_shell") and isinstance(self.app_shell, AmbientCanvas):
            self.app_shell.set_dark_mode(self.dark_mode)

    def apply_theme(self):
        app = QApplication.instance()
        if app:
            if not hasattr(self, "_theme_manager"):
                self._theme_manager = ThemeManager(app)
            self._theme_manager.apply(self.dark_mode)
        for surface in self.findChildren(GlassPanel):
            surface.set_dark_mode(self.dark_mode)
        if hasattr(self, "auth_page") and isinstance(self.auth_page, AmbientCanvas):
            self.auth_page.set_dark_mode(self.dark_mode)
        if hasattr(self, "app_shell") and isinstance(self.app_shell, AmbientCanvas):
            self.app_shell.set_dark_mode(self.dark_mode)
        self._refresh_dock_icons()
        if getattr(self, "_help_current_html", "") and hasattr(self, "help_detail"):
            self._render_help_html(self._help_current_html)

    def _topic_for_page_title(self, title: str) -> str:
        if title == "داشبورد":
            return "dashboard"
        return super()._topic_for_page_title(title)

    def show_page(self, key: str):
        super().show_page(key)
        if hasattr(self, "chat_meta") and key == "chats" and not self.current_chat:
            self.chat_meta.setText("یک گفتگو را از فهرست انتخاب کن تا تاریخچه آن بارگذاری شود.")

    def on_chat_selected(self):
        super().on_chat_selected()
        if self.current_chat and hasattr(self, "chat_meta"):
            kind = self.current_chat.get("kind", "private")
            self.chat_meta.setText("شناسه گفتگو: %s  ·  نوع: %s" % (self.current_chat.get("id", "-"), kind))
