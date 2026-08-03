# dialog.py

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush
from svg_icons import SVGIcon


class CustomDialog(QDialog):
    """Универсальное кастомное диалоговое окно с возможностью перетаскивания за заголовок."""
    
    def __init__(self, title="", text="", icon_type="question", 
                 buttons=("OK",), default_button=0, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ПЕРЕОПРЕДЕЛЯЕМ СТИЛИ для этого диалога (игнорируем глобальные)
        self.setStyleSheet("""
            QDialog {
                background: transparent;
                border: none;
            }
            QDialog QFrame#container {
                background-color: #2a2a2a;
                border: none;
                border-radius: 10px;
            }
            QDialog QLabel {
                color: #cccccc;
                background-color: transparent;
            }
        """)
        
        self.title_text = title
        self.message_text = text
        self.icon_type = icon_type
        self.button_texts = buttons
        self.default_button_index = default_button
        self.result_index = -1
        
        # Для перетаскивания
        self.drag_pos = None
        self.drag_active = False
        
        self._setup_ui()
        self._adjust_size()
        self._center_on_parent()
    
    def _setup_ui(self):
        container = QFrame(self)
        container.setObjectName("container")
        # Убираем стили из кода, они теперь в self.setStyleSheet
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Заголовок (область для перетаскивания)
        header_layout = QHBoxLayout()
        title_label = QLabel(self.title_text)
        title_label.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold; background-color: transparent;")
        header_layout.addWidget(title_label, 1)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #444444;
            }
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        main_layout.addLayout(header_layout)
        
        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #444444; max-height: 1px; border: none;")
        main_layout.addWidget(sep)
        
        # Содержимое: иконка + текст
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = self._get_icon_pixmap()
        if pixmap:
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            icon_label.hide()
        content_layout.addWidget(icon_label)
        
        self.message_label = QLabel(self.message_text)
        self.message_label.setStyleSheet("color: #cccccc; font-size: 14px; background-color: transparent;")
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.message_label, 1)
        main_layout.addLayout(content_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        for i, btn_text in enumerate(self.button_texts):
            btn = QPushButton(btn_text)
            btn.setFixedHeight(32)
            btn.setMinimumWidth(80)
            if i == self.default_button_index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a6ea5;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #4a7eb5; }
                    QPushButton:pressed { background-color: #2a5e95; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3a3a3a;
                        color: #cccccc;
                        border: 1px solid #555555;
                        border-radius: 4px;
                        padding: 6px 16px;
                    }
                    QPushButton:hover { background-color: #4a4a4a; }
                    QPushButton:pressed { background-color: #2a2a2a; }
                """)
            btn.clicked.connect(lambda checked, idx=i: self._on_button_clicked(idx))
            buttons_layout.addWidget(btn)
        main_layout.addLayout(buttons_layout)
        
        container.setLayout(main_layout)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)
    
    def _adjust_size(self):
        """Адаптивный размер в зависимости от длины текста."""
        text_len = len(self.message_text)
        if text_len > 80:
            width = 650
        elif text_len > 50:
            width = 600
        else:
            width = 480
        
        self.setFixedWidth(width)
        self.setMinimumHeight(150)
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())
    
    def _get_icon_pixmap(self):
        icon_map = {
            "question": SVGIcon.create_info_icon("#66e1ff"),
            "information": SVGIcon.create_info_icon("#66e1ff"),
            "warning": SVGIcon.create_warning_icon("#ffef5e"),
            "error": SVGIcon.create_error_icon("#ff808c"),
            "success": SVGIcon.create_success_icon("#78eb7b")
        }
        svg = icon_map.get(self.icon_type)
        if svg:
            return SVGIcon.svg_to_icon(svg, size=48).pixmap(QSize(48, 48))
        return None
    
    def _center_on_parent(self):
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.x() + (parent_geo.width() - self.width()) // 2,
                parent_geo.y() + (parent_geo.height() - self.height()) // 2
            )
        else:
            screen = QApplication.primaryScreen().geometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2
            )
    
    def _on_button_clicked(self, index):
        self.result_index = index
        self.accept()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Тень
        shadow = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(8, 8, self.width() - 16, self.height() - 16, 12, 12)
        
        # Рисуем сам диалог без обводки
        painter.setBrush(QBrush(QColor(42, 42, 42)))
        painter.setPen(Qt.PenStyle.NoPen)  # Убираем обводку полностью
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        super().paintEvent(event)
    
    # ---------- Перетаскивание окна за заголовок ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 50:
                self.drag_pos = event.globalPosition().toPoint()
                self.drag_active = True
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_active:
            if self.drag_pos is not None:
                delta = event.globalPosition().toPoint() - self.drag_pos
                self.move(self.pos() + delta)
                self.drag_pos = event.globalPosition().toPoint()
                event.accept()
                return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_active = False
            self.drag_pos = None
        super().mouseReleaseEvent(event)
    # ------------------------------------------------
    
    # Статические методы
    @staticmethod
    def question(parent, title, text, default=True):
        buttons = ("Да", "Нет")
        default_idx = 0 if default else 1
        dialog = CustomDialog(title, text, "question", buttons, default_idx, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted and dialog.result_index == 0
    
    @staticmethod
    def information(parent, title, text):
        CustomDialog(title, text, "information", ("OK",), 0, parent).exec()
    
    @staticmethod
    def warning(parent, title, text):
        CustomDialog(title, text, "warning", ("OK",), 0, parent).exec()
    
    @staticmethod
    def error(parent, title, text):
        CustomDialog(title, text, "error", ("OK",), 0, parent).exec()
    
    @staticmethod
    def success(parent, title, text):
        CustomDialog(title, text, "success", ("OK",), 0, parent).exec()