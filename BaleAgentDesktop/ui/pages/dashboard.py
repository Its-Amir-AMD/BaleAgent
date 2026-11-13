from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QListWidget
from ..components import GlassPanel


def build_dashboard(self):
    page, layout = self._page("داشبورد", "وضعیت کلی حساب و ابزارهای پرکاربرد")

    hero = GlassPanel(radius=24, variant="material", interactive=True)
    hero_layout = QHBoxLayout(hero); hero_layout.setContentsMargins(24, 20, 24, 20); hero_layout.setSpacing(18)
    hero_text = QVBoxLayout(); hero_text.setSpacing(6)
    eyebrow = QLabel("BALE AGENT  /  WORKSPACE")
    eyebrow.setObjectName("Muted"); eyebrow.setStyleSheet("font-size:8pt; letter-spacing:1.1px;")
    hero_text.addWidget(eyebrow)
    welcome = QLabel("همه‌چیز برای مدیریت گفتگوها آماده است")
    welcome.setObjectName("PageTitle"); welcome.setWordWrap(True)
    hero_text.addWidget(welcome)
    hero_sub = QLabel("گفتگوها، پاسخ‌های هوشمند و ابزارهای روزمره را از یک فضای منسجم مدیریت کن.")
    hero_sub.setObjectName("Muted"); hero_sub.setWordWrap(True)
    hero_text.addWidget(hero_sub)
    hero_layout.addLayout(hero_text, 1)
    hero_actions = QVBoxLayout(); hero_actions.setSpacing(8)
    open_chats = QPushButton("رفتن به گفتگوها"); open_chats.setObjectName("Primary")
    open_chats.clicked.connect(lambda: self.show_page("chats"))
    open_ai = QPushButton("تنظیم هوش مصنوعی")
    open_ai.clicked.connect(lambda: self.show_page("settings"))
    hero_actions.addWidget(open_chats); hero_actions.addWidget(open_ai)
    hero_layout.addLayout(hero_actions)
    layout.addWidget(hero)

    stats_grid = QGridLayout(); stats_grid.setSpacing(12)
    stat_specs = [
        ("وضعیت حساب", "—", "نشست بله", "stat_session"),
        ("حافظه محلی", "0", "یادداشت ذخیره‌شده", "stat_facts"),
        ("قوانین پاسخ", "0", "قانون تعریف‌شده", "stat_rules"),
        ("هوش مصنوعی", "—", "وضعیت پیکربندی", "stat_ai"),
        ("پیام‌های زمان‌بندی", "0", "در انتظار ارسال", "stat_scheduled"),
    ]
    for i, (title, value, detail, attr) in enumerate(stat_specs):
        card, number = self._stat(title, value, detail)
        setattr(self, attr, number)
        stats_grid.addWidget(card, 0, i)
    layout.addLayout(stats_grid)

    lower = QHBoxLayout(); lower.setSpacing(12)
    activity_panel, ap = self._panel("فعالیت اخیر")
    self.activity = QListWidget()
    self.activity.setObjectName("ActivityList")
    self.activity.setMinimumHeight(170)
    self.activity.addItem("برنامه آماده است.")
    ap.addWidget(self.activity, 1)
    lower.addWidget(activity_panel, 3)

    privacy_panel, pp = self._panel("کنترل و حریم خصوصی")
    privacy_text = QLabel(
        "ارسال پیام، پاسخ، واکنش و فوروارد نیازمند اقدام صریح است.\n\n"
        "تاریخچه گفتگو فقط با اجازه مشخص برای سرویس هوش مصنوعی ارسال می‌شود.\n\n"
        "کلید API و نشست بله را مانند اطلاعات محرمانه نگهداری کن."
    )
    privacy_text.setObjectName("Muted"); privacy_text.setWordWrap(True)
    pp.addWidget(privacy_text, 1)
    lower.addWidget(privacy_panel, 2)
    layout.addLayout(lower, 1)
    return page
