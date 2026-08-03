# notifications.py

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
    
    # Счётчик для отслеживания позиции
    _instance_counter = 0
    
    def __init__(self, title, message, duration=4000, icon_type="information", offset=0):
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
        self.offset = offset  # Смещение от нижнего края
        
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
        """Позиционирует окно с учётом смещения."""
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.width() - 20,
            screen.height() - self.height() - 50 - self.offset,
            self.width(),
            self.height()
        )
    
    def set_offset(self, offset):
        """Обновляет смещение уведомления."""
        self.offset = offset
        self._position_window()
    
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
        self.notification_height = 80  # Приблизительная высота уведомления
        self.spacing = 10  # Расстояние между уведомлениями
    
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
    
    def _update_positions(self):
        """Обновляет позиции всех уведомлений."""
        self._cleanup_notifications()
        
        # Сортируем уведомления по времени добавления (новые сверху)
        visible = []
        for notif in self.notifications:
            try:
                if not sip.isdeleted(notif) and notif.isVisible():
                    visible.append(notif)
            except (RuntimeError, AttributeError):
                continue
        
        # Обновляем позиции для каждого уведомления
        # Новые уведомления будут сверху (меньший offset)
        for i, notif in enumerate(visible):
            try:
                if not sip.isdeleted(notif):
                    # Вычисляем смещение: каждое следующее уведомление ниже
                    # Используем реальную высоту уведомления + отступ
                    height = notif.height() if notif.height() > 0 else self.notification_height
                    offset = i * (height + self.spacing)
                    notif.set_offset(offset)
            except (RuntimeError, AttributeError):
                continue
    
    def show_notification(self, title, message, duration=4000, icon_type="information"):
        self._cleanup_notifications()
        
        # Если достигнут лимит - удаляем самое старое
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications[0]
            try:
                if not sip.isdeleted(oldest) and oldest.isVisible():
                    oldest.close()
            except (RuntimeError, AttributeError):
                pass
            self.notifications.pop(0)
        
        # Создаём новое уведомление
        notif = NotificationPopup(title, message, duration, icon_type, offset=0)
        notif.show()
        
        # Добавляем в начало списка (новые сверху)
        self.notifications.insert(0, notif)
        
        # Обновляем позиции всех уведомлений
        self._update_positions()
        
        # Подключаем сигнал закрытия
        notif.destroyed.connect(self._on_notification_closed)
    
    def _on_notification_closed(self):
        """Обработчик закрытия уведомления с защитой от удалённых объектов."""
        try:
            self._cleanup_notifications()
            self._update_positions()
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