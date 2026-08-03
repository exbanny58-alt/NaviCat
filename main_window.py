# main_window.py

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QStackedWidget, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QCursor
from svg_icons import SVGIcon
from title_bar import CustomTitleBar
from pages import SettingsPage, MusicPage, MainPage, ModsPage, ClientPage


class ResizeHandle(QWidget):
    """Виджет для растягивания окна за края."""
    
    def __init__(self, parent, direction):
        super().__init__(parent)
        self.parent_window = parent
        self.direction = direction
        self.setMouseTracking(True)
        
        cursors = {
            'left': Qt.CursorShape.SizeHorCursor,
            'right': Qt.CursorShape.SizeHorCursor,
            'bottom': Qt.CursorShape.SizeVerCursor,
            'bottom_left': Qt.CursorShape.SizeFDiagCursor,
            'bottom_right': Qt.CursorShape.SizeFDiagCursor,
        }
        self.setCursor(cursors.get(direction, Qt.CursorShape.ArrowCursor))
        self.handle_size = 10
        self._update_geometry()
    
    def _update_geometry(self):
        window = self.parent_window
        w = window.width()
        h = window.height()
        s = self.handle_size
        
        geometries = {
            'right': QRect(w - s, 0, s, h),
            'bottom': QRect(0, h - s, w, s),
            'bottom_right': QRect(w - s, h - s, s, s),
        }
        
        if self.direction in geometries:
            self.setGeometry(geometries[self.direction])
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
            self.window_start_geometry = self.parent_window.geometry()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_start_pos'):
                delta = event.globalPosition().toPoint() - self.drag_start_pos
                geometry = self.window_start_geometry
                x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
                
                min_width = 600
                min_height = 400
                
                if self.direction == 'right':
                    new_w = max(min_width, w + delta.x())
                    self.parent_window.setGeometry(x, y, new_w, h)
                    
                elif self.direction == 'bottom':
                    new_h = max(min_height, h + delta.y())
                    self.parent_window.setGeometry(x, y, w, new_h)
                    
                elif self.direction == 'bottom_right':
                    new_w = max(min_width, w + delta.x())
                    new_h = max(min_height, h + delta.y())
                    self.parent_window.setGeometry(x, y, new_w, new_h)
                
                self.parent_window.update_resize_handles()
                event.accept()
    
    def resizeEvent(self, event):
        self._update_geometry()
        super().resizeEvent(event)


class MatteBlackWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(600, 400)
        
        self.load_window_geometry()

        self.menu_expanded = False
        self.menu_width_expanded = 160
        self.menu_width_collapsed = 64
        self.current_menu_index = -1

        self.icon_functions = [
            SVGIcon.create_server_icon,
            SVGIcon.create_client_icon,
            SVGIcon.create_mods_icon,
            SVGIcon.create_editors_icon,
            SVGIcon.create_settings_icon,
            SVGIcon.create_music_icon,
        ]

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

        self.content_container = QWidget()
        content_container_layout = QVBoxLayout()
        content_container_layout.setContentsMargins(0, 0, 0, 0)
        content_container_layout.setSpacing(0)
        
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

        settings_btn = QPushButton("Настройки")
        settings_btn.setObjectName("menu_settings")
        settings_btn.setCheckable(True)
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

        # --- ГЛАВНАЯ СТРАНИЦА ---
        main_page = MainPage()
        self.content_stack.addWidget(main_page)
        self.main_page_index = 0

        self.menu_page_indices = {}
        
        # Инициализируем ссылки на страницы
        self.mods_page = None
        self.client_page = None

        # Страницы для пунктов меню
        menu_page_names = ["Сервер", "Клиент", "Моды", "Редакторы"]
        for i, name in enumerate(menu_page_names):
            if name == "Моды":
                mods_page = ModsPage()
                self.content_stack.addWidget(mods_page)
                self.menu_page_indices[i] = self.content_stack.count() - 1
                self.mods_page = mods_page
            elif name == "Клиент":
                client_page = ClientPage()
                self.content_stack.addWidget(client_page)
                self.menu_page_indices[i] = self.content_stack.count() - 1
                self.client_page = client_page
            else:
                page = self._create_default_page(name)
                self.content_stack.addWidget(page)
                self.menu_page_indices[i] = self.content_stack.count() - 1

        # Страница настроек
        settings_page = SettingsPage()
        self.content_stack.addWidget(settings_page)
        self.menu_page_indices[4] = self.content_stack.count() - 1

        # Страница музыки
        music_page = MusicPage()
        self.content_stack.addWidget(music_page)
        self.menu_page_indices[5] = self.content_stack.count() - 1

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.content_stack)
        content_panel.setLayout(content_layout)

        self.main_hbox.addWidget(self.menu_panel)
        self.main_hbox.addWidget(self.separator_vertical)
        self.main_hbox.addWidget(content_panel)

        content_container_layout.addLayout(self.main_hbox)
        self.content_container.setLayout(content_container_layout)
        main_layout.addWidget(self.content_container)
        
        # ---- Хэндлы для растягивания ----
        self.resize_handles = []
        for direction in ['right', 'bottom', 'bottom_right']:
            handle = ResizeHandle(self, direction)
            self.resize_handles.append(handle)
        
        self.setLayout(main_layout)

        # Подключаем сигнал обновления Client-страницы при изменении Client-статуса
        # Только если страницы существуют
        if hasattr(self, 'mods_page') and self.mods_page is not None and \
           hasattr(self, 'client_page') and self.client_page is not None:
            self.mods_page.client_status_changed.connect(self.client_page.load_client_mods)

        # Начальное состояние
        self.apply_menu_state()
        self.open_main_page()
        self.update_resize_handles()
    
    def _on_preload_finished(self):
        """Обработчик завершения предзагрузки всех страниц."""
        pass

    def update_resize_handles(self):
        for handle in self.resize_handles:
            handle._update_geometry()
            handle.raise_()

    # ---------- Методы для сохранения/загрузки геометрии ----------
    
    def save_window_geometry(self):
        try:
            config_dir = "config"
            config_file = os.path.join(config_dir, "settings.json")
            
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            settings = {}
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                except:
                    pass
            
            settings["window_x"] = self.x()
            settings["window_y"] = self.y()
            settings["window_width"] = self.width()
            settings["window_height"] = self.height()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Ошибка сохранения геометрии окна: {e}")

    def load_window_geometry(self):
        try:
            config_dir = "config"
            config_file = os.path.join(config_dir, "settings.json")
            
            if not os.path.exists(config_file):
                return
            
            with open(config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            x = settings.get("window_x")
            y = settings.get("window_y")
            width = settings.get("window_width")
            height = settings.get("window_height")
            
            if all(v is not None for v in [x, y, width, height]):
                screen = QApplication.primaryScreen().geometry()
                width = max(600, min(width, screen.width()))
                height = max(400, min(height, screen.height()))
                x = max(0, min(x, screen.width() - width))
                y = max(0, min(y, screen.height() - height))
                self.setGeometry(x, y, width, height)
                
        except Exception as e:
            print(f"Ошибка загрузки геометрии окна: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_resize_handles()
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer()
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self.save_window_geometry)
        self._resize_timer.stop()
        self._resize_timer.start(300)

    def moveEvent(self, event):
        super().moveEvent(event)
        if not hasattr(self, '_move_timer'):
            self._move_timer = QTimer()
            self._move_timer.setSingleShot(True)
            self._move_timer.timeout.connect(self.save_window_geometry)
        self._move_timer.stop()
        self._move_timer.start(300)

    # ---------- Остальные методы ----------

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

    def open_main_page(self):
        self.current_menu_index = -1
        self.content_stack.setCurrentIndex(self.main_page_index)
        self._reset_menu_icons()

    def show_page(self, index):
        self.content_stack.setCurrentIndex(index)

    def on_menu_clicked(self, index):
        if self.current_menu_index == index:
            self.open_main_page()
            return

        self.current_menu_index = index
        page_index = self.menu_page_indices.get(index)
        if page_index is not None:
            self.show_page(page_index)
            self._update_menu_icons(index)

    def _update_menu_icons(self, active_index):
        for i, btn in enumerate(self.menu_buttons):
            if i == active_index:
                color = "#ffffff"
                btn.setChecked(True)
            else:
                color = "#aaaaaa"
                btn.setChecked(False)
            svg = self.icon_functions[i](color)
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)

    def _reset_menu_icons(self):
        for i, btn in enumerate(self.menu_buttons):
            svg = self.icon_functions[i]("#aaaaaa")
            icon = SVGIcon.svg_to_icon(svg, size=24)
            btn.setIcon(icon)
            btn.setChecked(False)

    def on_music_clicked(self):
        self.on_menu_clicked(5)

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