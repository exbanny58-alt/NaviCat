from PyQt6 import sip
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush
from svg_icons import SVGIcon


class NotificationPopup(QWidget):
    """Всплывающее уведомление в правом нижнем углу."""
    
    def __init__(self, title, message, duration=4000, icon_type="information"):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        self.duration = duration
        self.icon_type = icon_type
        self._is_deleted = False
        
        self._setup_ui(title, message)
        self._setup_timer()
        self._setup_animation()
        
        self._position_window()
    
    def _setup_ui(self, title, message):
        container = QFrame(self)
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 8px;
            }
        """)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(15, 10, 15, 12)
        main_layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        svg_icon = self._get_svg_icon()
        if svg_icon:
            pixmap = SVGIcon.svg_to_icon(svg_icon, size=24).pixmap(QSize(24, 24))
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText(self._get_emoji_icon())
            icon_label.setStyleSheet("font-size: 16px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold;")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { color: #ffffff; background-color: #444444; }
            QPushButton:pressed { background-color: #666666; }
        """)
        close_btn.clicked.connect(self.close_animated)
        header_layout.addWidget(close_btn)
        main_layout.addLayout(header_layout)
        
        message_label = QLabel(message)
        message_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(350)
        main_layout.addWidget(message_label)
        
        container.adjustSize()
        self.setFixedSize(container.size())
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)
    
    def _get_svg_icon(self):
        icons = {
            "success": SVGIcon.create_success_icon(),
            "error": SVGIcon.create_error_icon(),
            "warning": SVGIcon.create_warning_icon(),
            "information": SVGIcon.create_info_icon()
        }
        return icons.get(self.icon_type)
    
    def _get_emoji_icon(self):
        emojis = {"success": "✅", "error": "❌", "warning": "⚠️", "information": "ℹ️"}
        return emojis.get(self.icon_type, "ℹ️")
    
    def _setup_timer(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_animated)
        self.timer.start(self.duration)
    
    def _setup_animation(self):
        self.setWindowOpacity(0)
        self.show_animation = QPropertyAnimation(self, b"windowOpacity")
        self.show_animation.setDuration(300)
        self.show_animation.setStartValue(0)
        self.show_animation.setEndValue(1)
        self.show_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.hide_animation = QPropertyAnimation(self, b"windowOpacity")
        self.hide_animation.setDuration(300)
        self.hide_animation.setStartValue(1)
        self.hide_animation.setEndValue(0)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.hide_animation.finished.connect(self._safe_close)
    
    def _safe_close(self):
        """Безопасное закрытие окна, игнорируя уже удалённые объекты."""
        if not self._is_deleted:
            self.close()
    
    def _position_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 50,
            self.width(),
            self.height()
        )
    
    def showEvent(self, event):
        super().showEvent(event)
        self.show_animation.start()
    
    def close_animated(self):
        if not self._is_deleted:
            self.timer.stop()
            self.hide_animation.start()
    
    def mousePressEvent(self, event):
        if not self._is_deleted:
            self.close_animated()
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shadow = QColor(0, 0, 0, 60)
        painter.setBrush(QBrush(shadow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(5, 5, self.width() - 10, self.height() - 10, 10, 10)
        super().paintEvent(event)
    
    def closeEvent(self, event):
        self._is_deleted = True
        super().closeEvent(event)


class NotificationManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.notifications = []
        self.max_notifications = 5
    
    def _cleanup_notifications(self):
        """Удаляет закрытые уведомления с защитой от удалённых объектов."""
        cleaned = []
        for n in self.notifications:
            try:
                # Проверяем, существует ли объект и не удалён ли он
                if not sip.isdeleted(n) and n.isVisible():
                    cleaned.append(n)
            except (RuntimeError, AttributeError):
                # Если объект уже удалён, просто пропускаем
                pass
        self.notifications = cleaned
    
    def _position_notifications(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 20
        y = screen.height() - 50
        visible = []
        for notif in reversed(self.notifications):
            try:
                if not sip.isdeleted(notif) and notif.isVisible():
                    visible.append(notif)
            except (RuntimeError, AttributeError):
                continue
        for i, notif in enumerate(visible):
            try:
                if not sip.isdeleted(notif):
                    notif.move(
                        x - notif.width(),
                        y - notif.height() - (i * (notif.height() + 10))
                    )
            except (RuntimeError, AttributeError):
                continue
    
    def show_notification(self, title, message, duration=4000, icon_type="information"):
        self._cleanup_notifications()
        
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications[0]
            try:
                if not sip.isdeleted(oldest) and oldest.isVisible():
                    oldest.close()
            except (RuntimeError, AttributeError):
                pass
            self.notifications.pop(0)
        
        notif = NotificationPopup(title, message, duration, icon_type)
        notif.show()
        self.notifications.append(notif)
        self._position_notifications()
        notif.destroyed.connect(self._on_notification_closed)
    
    def _on_notification_closed(self):
        """Обработчик закрытия уведомления с защитой от удалённых объектов."""
        try:
            self._cleanup_notifications()
            self._position_notifications()
        except (RuntimeError, AttributeError):
            # Если объекты уже удалены, игнорируем
            pass
    
    def show_success(self, title, message, duration=4000):
        self.show_notification(title, message, duration, "success")
    
    def show_error(self, title, message, duration=5000):
        self.show_notification(title, message, duration, "error")
    
    def show_warning(self, title, message, duration=4000):
        self.show_notification(title, message, duration, "warning")
    
    def show_info(self, title, message, duration=4000):
        self.show_notification(title, message, duration, "information")


_notification_manager = None


def get_notification_manager():
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager