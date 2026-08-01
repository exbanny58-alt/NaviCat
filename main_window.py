from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from svg_icons import SVGIcon
from title_bar import CustomTitleBar
from pages import SettingsPage


class MatteBlackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1000, 650)

        self.menu_expanded = False
        self.menu_width_expanded = 160
        self.menu_width_collapsed = 64

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        separator_top = QFrame()
        separator_top.setFrameShape(QFrame.Shape.HLine)
        separator_top.setFrameShadow(QFrame.Shadow.Sunken)
        separator_top.setStyleSheet("background-color: #333333; max-height: 1px;")
        main_layout.addWidget(separator_top)

        self.main_hbox = QHBoxLayout()
        self.main_hbox.setContentsMargins(0, 0, 0, 0)
        self.main_hbox.setSpacing(0)

        # ---- Левая панель (меню) ----
        self.menu_panel = QWidget()
        self.menu_panel.setFixedWidth(self.menu_width_expanded)
        self.menu_panel.setStyleSheet("background-color: #1a1a1a;")
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 20, 10, 20)
        menu_layout.setSpacing(8)

        self.menu_buttons = []
        menu_items = [
            ("Сервер", SVGIcon.create_server_icon),
            ("Клиент", SVGIcon.create_client_icon),
            ("Моды", SVGIcon.create_mods_icon),
            ("Редакторы", SVGIcon.create_editors_icon),
        ]

        for i, (name, icon_func) in enumerate(menu_items):
            btn = QPushButton(name)
            btn.setObjectName(f"menu_{i}")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            svg = icon_func("#aaaaaa")
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(name)
            btn.setStyleSheet(self._menu_button_style())
            btn.clicked.connect(lambda checked, idx=i: self.on_menu_clicked(idx))
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        menu_layout.addStretch()

        # Настройки
        settings_btn = QPushButton("Настройки")
        settings_btn.setObjectName("menu_settings")
        settings_btn.setCheckable(True)
        settings_btn.setAutoExclusive(True)
        svg_settings = SVGIcon.create_settings_icon("#aaaaaa")
        icon_settings = SVGIcon.svg_to_icon(svg_settings, size=24)
        settings_btn.setIcon(icon_settings)
        settings_btn.setIconSize(QSize(24, 24))
        settings_btn.setToolTip("Настройки")
        settings_btn.setStyleSheet(self._menu_button_style())
        settings_btn.clicked.connect(lambda checked: self.on_menu_clicked(4))
        menu_layout.addWidget(settings_btn)
        self.menu_buttons.append(settings_btn)

        self.menu_panel.setLayout(menu_layout)

        # ---- Вертикальный разделитель ----
        self.separator_vertical = QFrame()
        self.separator_vertical.setFrameShape(QFrame.Shape.VLine)
        self.separator_vertical.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator_vertical.setStyleSheet("background-color: #333333; max-width: 1px;")

        # ---- Правая панель (контент) ----
        content_panel = QWidget()
        content_panel.setStyleSheet("background-color: #1a1a1a;")
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")

        # Страницы для пунктов меню (0–3)
        for name, _ in menu_items:
            page = self._create_default_page(name)
            self.content_stack.addWidget(page)

        # Страница настроек (индекс 4)
        settings_page = SettingsPage()
        self.content_stack.addWidget(settings_page)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_stack)
        content_panel.setLayout(content_layout)

        # Собираем горизонтальную часть
        self.main_hbox.addWidget(self.menu_panel)
        self.main_hbox.addWidget(self.separator_vertical)
        self.main_hbox.addWidget(content_panel)

        main_layout.addLayout(self.main_hbox)
        self.setLayout(main_layout)

        # Начальное состояние (свёрнутое меню)
        self.apply_menu_state()

        # Выбираем первый пункт
        self.menu_buttons[0].setChecked(True)
        self.on_menu_clicked(0)

    # --- Вспомогательные методы ---

    def _menu_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: #aaaaaa;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
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
        """

    def _create_default_page(self, name):
        """Создаёт стандартную страницу-заглушку для пунктов меню."""
        page = QWidget()
        page.setStyleSheet("background-color: transparent;")
        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(30, 30, 30, 30)
        label = QLabel(
            f"<h1 style='color: #cccccc;'>{name}</h1>"
            f"<p style='color: #666666;'>Контент для страницы «{name}»</p>"
            f"<p style='color: #555555;'>Здесь может быть ваша информация.</p>"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setWordWrap(True)
        page_layout.addWidget(label)
        page_layout.addStretch()
        page.setLayout(page_layout)
        return page

    def apply_menu_state(self):
        width = self.menu_width_expanded if self.menu_expanded else self.menu_width_collapsed
        self.menu_panel.setFixedWidth(width)
        self.title_bar.update_toggle_icon(self.menu_expanded)

        for btn in self.menu_buttons:
            if self.menu_expanded:
                btn.setText(btn.toolTip())
                btn.setStyleSheet(self._menu_button_style())
            else:
                btn.setText("")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #aaaaaa;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 0px;
                        font-size: 0px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        text-align: center;
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
                btn.setIconSize(QSize(24, 24))

    def toggle_menu(self):
        self.menu_expanded = not self.menu_expanded
        self.apply_menu_state()

    def on_menu_clicked(self, index):
        self.content_stack.setCurrentIndex(index)
        icon_functions = [
            SVGIcon.create_server_icon,
            SVGIcon.create_client_icon,
            SVGIcon.create_mods_icon,
            SVGIcon.create_editors_icon,
            SVGIcon.create_settings_icon,
        ]
        for i, btn in enumerate(self.menu_buttons):
            color = "#ffffff" if i == index else "#aaaaaa"
            svg = icon_functions[i](color)
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shadow_color = QColor(0, 0, 0, 80)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(10, 10, self.width() - 20, self.height() - 20)
        painter.setBrush(QBrush(QColor(26, 26, 26)))
        painter.setPen(QPen(QColor(50, 50, 50), 1))
        painter.drawRect(0, 0, self.width(), self.height())
        super().paintEvent(event)
