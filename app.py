import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QPoint, QByteArray, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer


class SVGIcon:
    """Класс для создания SVG иконок"""

    # Иконки для меню
    @staticmethod
    def create_home_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_settings_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_help_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_info_icon(color="#aaaaaa"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="{color}"/>
        </svg>'''

    # Иконки заголовка
    @staticmethod
    def create_close_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_minimize_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 13H5v-2h14v2z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_maximize_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def create_restore_icon(color="#ffffff"):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
            <path d="M19 9h-4V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h4v4c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-8c0-1.1-.9-2-2-2zm-8 8H5V5h8v4h-4c-1.1 0-2 .9-2 2v4h4v2zm4-4v4h-4v-4h4zm4 4h-2v-4h-4V9h6v8z" fill="{color}"/>
        </svg>'''

    @staticmethod
    def svg_to_icon(svg_string, size=24):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(QByteArray(svg_string.encode()))
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.drag_pos = None
        self.setFixedHeight(44)
        self.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 10px 10px 0 0;
        """)
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()
        self.setup_buttons()
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 14, 0)
        layout.setSpacing(8)
        layout.addStretch()
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

    def setup_buttons(self):
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
                max-width: 28px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """
        close_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                min-width: 28px;
                min-height: 28px;
                max-width: 28px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #e81123;
                border-radius: 4px;
            }
        """
        close_svg = SVGIcon.create_close_icon("#ffffff")
        minimize_svg = SVGIcon.create_minimize_icon("#ffffff")
        maximize_svg = SVGIcon.create_maximize_icon("#ffffff")
        restore_svg = SVGIcon.create_restore_icon("#ffffff")
        self.close_icon = SVGIcon.svg_to_icon(close_svg)
        self.minimize_icon = SVGIcon.svg_to_icon(minimize_svg)
        self.maximize_icon = SVGIcon.svg_to_icon(maximize_svg)
        self.restore_icon = SVGIcon.svg_to_icon(restore_svg)
        self.close_btn.setIcon(self.close_icon)
        self.minimize_btn.setIcon(self.minimize_icon)
        self.maximize_btn.setIcon(self.maximize_icon)
        self.minimize_btn.setStyleSheet(btn_style)
        self.maximize_btn.setStyleSheet(btn_style)
        self.close_btn.setStyleSheet(close_style)
        icon_size = 16
        self.close_btn.setIconSize(QSize(icon_size, icon_size))
        self.minimize_btn.setIconSize(QSize(icon_size, icon_size))
        self.maximize_btn.setIconSize(QSize(icon_size, icon_size))

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_btn.setIcon(self.maximize_icon)
        else:
            self.parent.showMaximized()
            self.maximize_btn.setIcon(self.restore_icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent.move(self.parent.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()


class MatteBlackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1000, 650)

        # Главный вертикальный макет (шапка + основная часть)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Шапка
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # Разделитель под шапкой (горизонтальная линия)
        separator_top = QFrame()
        separator_top.setFrameShape(QFrame.Shape.HLine)
        separator_top.setFrameShadow(QFrame.Shadow.Sunken)
        separator_top.setStyleSheet("background-color: #333333; max-height: 1px;")
        main_layout.addWidget(separator_top)

        # Основная горизонтальная часть (меню + контент)
        main_hbox = QHBoxLayout()
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)

        # ---- Левая панель (меню) ----
        menu_panel = QWidget()
        menu_panel.setFixedWidth(220)
        menu_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 0 0 0 10px;")
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 20, 10, 20)
        menu_layout.setSpacing(8)

        # Пункты меню с SVG иконками
        self.menu_buttons = []
        menu_items = [
            ("Главная", SVGIcon.create_home_icon),
            ("Настройки", SVGIcon.create_settings_icon),
            ("Помощь", SVGIcon.create_help_icon),
            ("О программе", SVGIcon.create_info_icon)
        ]

        for i, (name, icon_func) in enumerate(menu_items):
            btn = QPushButton(name)
            btn.setObjectName(f"menu_{i}")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            # Создаём иконку (цвет #aaaaaa, при выделении станет белым)
            svg = icon_func("#aaaaaa")
            icon = SVGIcon.svg_to_icon(svg, size=20)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 16px;
                    font-size: 15px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QPushButton:checked {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border-left: 3px solid #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.on_menu_clicked(idx))
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        menu_layout.addStretch()
        menu_panel.setLayout(menu_layout)

        # ---- Вертикальный разделитель между меню и контентом ----
        separator_vertical = QFrame()
        separator_vertical.setFrameShape(QFrame.Shape.VLine)
        separator_vertical.setFrameShadow(QFrame.Shadow.Sunken)
        separator_vertical.setStyleSheet("background-color: #333333; max-width: 1px;")

        # ---- Правая панель (контент) ----
        content_panel = QWidget()
        content_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 0 0 10px 0;")
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")

        # Создаём 4 страницы
        self.pages = []
        for i, (name, _) in enumerate(menu_items):
            page = QWidget()
            page_layout = QVBoxLayout()
            page_layout.setContentsMargins(30, 30, 30, 30)
            label = QLabel(f"<h1 style='color: #cccccc;'>{name}</h1>"
                           f"<p style='color: #666666;'>Контент для страницы «{name}»</p>"
                           f"<p style='color: #555555;'>Здесь может быть ваша информация.</p>")
            label.setAlignment(Qt.AlignmentFlag.AlignTop)
            label.setWordWrap(True)
            page_layout.addWidget(label)
            page_layout.addStretch()
            page.setLayout(page_layout)
            self.content_stack.addWidget(page)
            self.pages.append(page)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_stack)
        content_panel.setLayout(content_layout)

        # Собираем горизонтальную часть: меню + разделитель + контент
        main_hbox.addWidget(menu_panel)
        main_hbox.addWidget(separator_vertical)
        main_hbox.addWidget(content_panel)

        main_layout.addLayout(main_hbox)
        self.setLayout(main_layout)

        # По умолчанию выбираем первый пункт
        self.menu_buttons[0].setChecked(True)
        self.on_menu_clicked(0)

    def on_menu_clicked(self, index):
        self.content_stack.setCurrentIndex(index)
        # Обновляем цвета иконок: для активного делаем белыми, остальные серые
        menu_icon_functions = [
            SVGIcon.create_home_icon,
            SVGIcon.create_settings_icon,
            SVGIcon.create_help_icon,
            SVGIcon.create_info_icon
        ]
        for i, btn in enumerate(self.menu_buttons):
            color = "#ffffff" if i == index else "#aaaaaa"
            svg = menu_icon_functions[i](color)
            icon = SVGIcon.svg_to_icon(svg, size=20)
            btn.setIcon(icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Тень
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(10, 10, self.width() - 20, self.height() - 20, 10, 10)
        # Основная рамка
        painter.setBrush(QBrush(QColor(26, 26, 26)))
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: transparent; }")
    window = MatteBlackWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()