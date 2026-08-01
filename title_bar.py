from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QSize
from svg_icons import SVGIcon


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.drag_pos = None
        self.setFixedHeight(44)
        self.setStyleSheet("background-color: #1a1a1a;")

        # Кнопка-стрелка для меню
        self.toggle_btn = QPushButton()
        # Используем новую иконку для открытия меню (по умолчанию меню открыто)
        self.toggle_btn.setIcon(SVGIcon.svg_to_icon(SVGIcon.create_menu_close_icon(), size=20))
        self.toggle_btn.setIconSize(QSize(20, 20))
        self.toggle_btn.setToolTip("Свернуть меню")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.toggle_btn.clicked.connect(self.parent.toggle_menu)

        # Кнопка музыки
        self.music_btn = QPushButton()
        self.music_btn.setIcon(SVGIcon.svg_to_icon(SVGIcon.create_music_icon("#aaaaaa"), size=20))
        self.music_btn.setIconSize(QSize(20, 20))
        self.music_btn.setToolTip("Музыка")
        self.music_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.music_btn.clicked.connect(self.parent.on_music_clicked)

        # Кнопки управления
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
        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.music_btn)
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

    def update_toggle_icon(self, expanded):
        if expanded:
            # Меню развёрнуто - показываем иконку закрытия (стрелка влево)
            icon = SVGIcon.svg_to_icon(SVGIcon.create_menu_close_icon(), size=20)
            self.toggle_btn.setToolTip("Свернуть меню")
        else:
            # Меню свёрнуто - показываем иконку открытия (стрелка вправо)
            icon = SVGIcon.svg_to_icon(SVGIcon.create_menu_open_icon(), size=20)
            self.toggle_btn.setToolTip("Развернуть меню")
        self.toggle_btn.setIcon(icon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent.move(self.parent.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()