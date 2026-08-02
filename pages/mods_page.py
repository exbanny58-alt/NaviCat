# mods_page.py

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QFrame, QMenu
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QIcon, QAction
from svg_icons import SVGIcon
from notifications import get_notification_manager


class ModScanner(QThread):
    """Поток для сканирования модов."""
    
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, workshop_path, custom_path):
        super().__init__()
        self.workshop_path = workshop_path
        self.custom_path = custom_path
    
    def run(self):
        try:
            mods = []
            
            if self.workshop_path and os.path.exists(self.workshop_path):
                workshop_mods = self._scan_workshop(self.workshop_path)
                mods.extend(workshop_mods)
            
            if self.custom_path and os.path.exists(self.custom_path):
                custom_mods = self._scan_custom(self.custom_path)
                mods.extend(custom_mods)
            
            mods.sort(key=lambda x: x['name'].lower())
            self.finished.emit(mods)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _scan_workshop(self, path):
        mods = []
        
        try:
            content_path = os.path.join(path, "content", "221100")
            
            if not os.path.exists(content_path):
                content_path = path
            
            for item in os.listdir(content_path):
                item_path = os.path.join(content_path, item)
                if os.path.isdir(item_path):
                    meta_path = os.path.join(item_path, "meta.cpp")
                    
                    if os.path.exists(meta_path):
                        mod_info = self._read_meta_cpp(meta_path)
                        if mod_info:
                            mods.append({
                                'name': mod_info.get('name', item),
                                'path': item_path,
                                'type': 'Workshop',
                                'id': item,
                                'author': mod_info.get('author', ''),
                                'version': mod_info.get('version', '')
                            })
                        else:
                            mods.append({
                                'name': f"Mod {item}",
                                'path': item_path,
                                'type': 'Workshop',
                                'id': item,
                                'author': '',
                                'version': ''
                            })
                    else:
                        mod_info = self._read_any_meta(item_path)
                        if mod_info:
                            mods.append({
                                'name': mod_info.get('name', item),
                                'path': item_path,
                                'type': 'Workshop',
                                'id': item,
                                'author': mod_info.get('author', ''),
                                'version': mod_info.get('version', '')
                            })
                            
        except Exception as e:
            print(f"Ошибка сканирования Workshop: {e}")
        
        return mods
    
    def _scan_custom(self, path):
        mods = []
        
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    mod_info = self._read_any_meta(item_path)
                    if mod_info:
                        mods.append({
                            'name': mod_info.get('name', item),
                            'path': item_path,
                            'type': 'Кастомный',
                            'id': item,
                            'author': mod_info.get('author', ''),
                            'version': mod_info.get('version', '')
                        })
                    else:
                        mods.append({
                            'name': item,
                            'path': item_path,
                            'type': 'Кастомный',
                            'id': item,
                            'author': '',
                            'version': ''
                        })
        except Exception as e:
            print(f"Ошибка сканирования кастомных модов: {e}")
        
        return mods
    
    def _read_meta_cpp(self, meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            info = {}
            import re
            
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if name_match:
                info['name'] = name_match.group(1)
            
            author_match = re.search(r'author\s*=\s*"([^"]+)"', content)
            if author_match:
                info['author'] = author_match.group(1)
            
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                info['version'] = version_match.group(1)
            
            return info if info else None
            
        except Exception as e:
            print(f"Ошибка чтения {meta_path}: {e}")
            return None
    
    def _read_any_meta(self, mod_path):
        meta_files = [
            os.path.join(mod_path, 'meta.cpp'),
            os.path.join(mod_path, 'meta.xml'),
            os.path.join(mod_path, 'mod.cpp'),
            os.path.join(mod_path, 'mod.xml'),
            os.path.join(mod_path, 'config.cpp'),
        ]
        
        for meta_file in meta_files:
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    info = {}
                    import re
                    
                    name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
                    if name_match:
                        info['name'] = name_match.group(1)
                    
                    author_match = re.search(r'author\s*=\s*"([^"]+)"', content)
                    if author_match:
                        info['author'] = author_match.group(1)
                    
                    version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                    if version_match:
                        info['version'] = version_match.group(1)
                    
                    return info if info else None
                    
                except Exception as e:
                    print(f"Ошибка чтения {meta_file}: {e}")
                    continue
        
        return None


class ModItemWidget(QWidget):
    """Виджет для отображения одного мода с тремя кнопками-иконками справа."""
    
    # Сигналы для кнопок
    server_toggled = pyqtSignal(dict, bool)
    cloud_toggled = pyqtSignal(dict, bool)
    gamepad_toggled = pyqtSignal(dict, bool)
    
    def __init__(self, mod_data, parent=None):
        super().__init__(parent)
        self.mod_data = mod_data
        
        # Состояния кнопок
        self.server_enabled = False
        self.cloud_enabled = False
        self.gamepad_enabled = False
        
        # Цвета для каждой кнопки (включённое состояние)
        self.server_color = "#ff6644"  # Яркий оранжево-красный
        self.cloud_color = "#44ddff"   # Голубой
        self.gamepad_color = "#44ff88" # Зелёный
        
        # Создаём иконки
        self.server_icon_off = SVGIcon.svg_to_icon(
            SVGIcon.create_server_icon_2("#888888"), 
            size=18
        )
        self.server_icon_on = SVGIcon.svg_to_icon(
            SVGIcon.create_server_icon_2(self.server_color), 
            size=18
        )
        self.cloud_icon_off = SVGIcon.svg_to_icon(
            SVGIcon.create_cloud_server_icon("#888888"), 
            size=18
        )
        self.cloud_icon_on = SVGIcon.svg_to_icon(
            SVGIcon.create_cloud_server_icon(self.cloud_color), 
            size=18
        )
        self.gamepad_icon_off = SVGIcon.svg_to_icon(
            SVGIcon.create_gamepad_icon("#888888"), 
            size=18
        )
        self.gamepad_icon_on = SVGIcon.svg_to_icon(
            SVGIcon.create_gamepad_icon(self.gamepad_color), 
            size=18
        )
        
        self._setup_ui()
        
        # Настройка hover эффекта для виджета
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            ModItemWidget {
                background-color: transparent;
                border-radius: 4px;
            }
            ModItemWidget:hover {
                background-color: #2a2a2a;
            }
        """)
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        # Название мода (слева)
        name_label = QLabel(self.mod_data['name'])
        name_label.setStyleSheet("color: #cccccc; font-size: 14px; font-weight: 500; background-color: transparent;")
        name_label.setWordWrap(False)
        layout.addWidget(name_label, 1)
        
        # Информация (автор, версия, ID)
        info_parts = []
        if self.mod_data.get('author'):
            info_parts.append(self.mod_data['author'])
        if self.mod_data.get('version'):
            info_parts.append(f"v{self.mod_data['version']}")
        if self.mod_data.get('id') and self.mod_data['type'] == 'Workshop':
            info_parts.append(f"ID: {self.mod_data['id']}")
        
        if info_parts:
            info_label = QLabel(" | ".join(info_parts))
            info_label.setStyleSheet("color: #666666; font-size: 12px; background-color: transparent;")
            info_label.setWordWrap(False)
            layout.addWidget(info_label)
        
        # Тип мода
        type_label = QLabel(self.mod_data['type'])
        type_color = "#88aacc" if self.mod_data['type'] == 'Workshop' else "#88ccaa"
        type_label.setStyleSheet(f"""
            color: {type_color}; 
            font-size: 11px; 
            background-color: #2a2a2a;
            padding: 2px 10px;
            border-radius: 10px;
        """)
        layout.addWidget(type_label)
        
        # Разделитель перед иконками
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #333333; max-width: 1px;")
        sep.setFixedWidth(1)
        sep.setFixedHeight(30)
        layout.addWidget(sep)
        
        # Кнопка 1 - Сервер (яркий оранжево-красный)
        self.server_btn = QPushButton()
        self.server_btn.setFixedSize(28, 28)
        self.server_btn.setIcon(self.server_icon_off)
        self.server_btn.setIconSize(QSize(18, 18))
        self.server_btn.setToolTip("Серверный мод")
        self.server_btn.setCheckable(True)
        self.server_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QPushButton:checked {
                background-color: transparent;
                border: none;
            }
        """)
        self.server_btn.clicked.connect(self._on_server_toggled)
        layout.addWidget(self.server_btn)
        
        # Кнопка 2 - Облако (голубая)
        self.cloud_btn = QPushButton()
        self.cloud_btn.setFixedSize(28, 28)
        self.cloud_btn.setIcon(self.cloud_icon_off)
        self.cloud_btn.setIconSize(QSize(18, 18))
        self.cloud_btn.setToolTip("Облачный мод")
        self.cloud_btn.setCheckable(True)
        self.cloud_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QPushButton:checked {
                background-color: transparent;
                border: none;
            }
        """)
        self.cloud_btn.clicked.connect(self._on_cloud_toggled)
        layout.addWidget(self.cloud_btn)
        
        # Кнопка 3 - Геймпад (зелёная)
        self.gamepad_btn = QPushButton()
        self.gamepad_btn.setFixedSize(28, 28)
        self.gamepad_btn.setIcon(self.gamepad_icon_off)
        self.gamepad_btn.setIconSize(QSize(18, 18))
        self.gamepad_btn.setToolTip("Клиентский мод")
        self.gamepad_btn.setCheckable(True)
        self.gamepad_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QPushButton:checked {
                background-color: transparent;
                border: none;
            }
        """)
        self.gamepad_btn.clicked.connect(self._on_gamepad_toggled)
        layout.addWidget(self.gamepad_btn)
        
        # Устанавливаем минимальную высоту
        self.setMinimumHeight(40)
    
    def _on_server_toggled(self, checked):
        self.server_enabled = checked
        if checked:
            self.server_btn.setIcon(self.server_icon_on)
        else:
            self.server_btn.setIcon(self.server_icon_off)
        self.server_toggled.emit(self.mod_data, checked)
    
    def _on_cloud_toggled(self, checked):
        self.cloud_enabled = checked
        if checked:
            self.cloud_btn.setIcon(self.cloud_icon_on)
        else:
            self.cloud_btn.setIcon(self.cloud_icon_off)
        self.cloud_toggled.emit(self.mod_data, checked)
    
    def _on_gamepad_toggled(self, checked):
        self.gamepad_enabled = checked
        if checked:
            self.gamepad_btn.setIcon(self.gamepad_icon_on)
        else:
            self.gamepad_btn.setIcon(self.gamepad_icon_off)
        self.gamepad_toggled.emit(self.mod_data, checked)
    
    def set_server_state(self, enabled):
        """Устанавливает состояние кнопки сервера."""
        self.server_btn.setChecked(enabled)
        self._on_server_toggled(enabled)
    
    def set_cloud_state(self, enabled):
        """Устанавливает состояние кнопки облака."""
        self.cloud_btn.setChecked(enabled)
        self._on_cloud_toggled(enabled)
    
    def set_gamepad_state(self, enabled):
        """Устанавливает состояние кнопки геймпада."""
        self.gamepad_btn.setChecked(enabled)
        self._on_gamepad_toggled(enabled)
    
    def get_states(self):
        """Возвращает все состояния кнопок."""
        return {
            'server': self.server_enabled,
            'cloud': self.cloud_enabled,
            'gamepad': self.gamepad_enabled
        }


class ModsPage(QWidget):
    """Страница управления модами."""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1a1a1a;")
        self.notifications = get_notification_manager()
        
        self.workshop_path = ""
        self.custom_path = ""
        self.mods = []
        self.mod_widgets = {}  # Словарь для хранения виджетов
        
        self._load_paths()
        self._setup_ui()
        QTimer.singleShot(100, self.refresh_mods)
    
    def _load_paths(self):
        config_dir = "config"
        config_file = os.path.join(config_dir, "settings.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.workshop_path = settings.get("Путь до папки Workshop", "")
                    self.custom_path = settings.get("Путь до папки своих модов", "")
                    
                    if self.workshop_path:
                        self.workshop_path = self.workshop_path.replace('\\', '/')
                    if self.custom_path:
                        self.custom_path = self.custom_path.replace('\\', '/')
                        
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")
    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # ---- Кнопки управления ----
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #666666;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
                border-color: #333333;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_mods)
        toolbar_layout.addWidget(self.refresh_btn)
        
        workshop_btn = QPushButton("Открыть Workshop")
        workshop_btn.setFixedHeight(40)
        workshop_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #666666;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        workshop_btn.clicked.connect(self._open_workshop)
        toolbar_layout.addWidget(workshop_btn)
        
        custom_btn = QPushButton("Открыть кастомные")
        custom_btn.setFixedHeight(40)
        custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #666666;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        custom_btn.clicked.connect(self._open_custom)
        toolbar_layout.addWidget(custom_btn)
        
        # Кнопка сброса всех состояний
        reset_btn = QPushButton("Сбросить всё")
        reset_btn.setFixedHeight(40)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #666666;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        reset_btn.clicked.connect(self._reset_all_states)
        toolbar_layout.addWidget(reset_btn)
        
        # Растягиваем чтобы поиск уехал вправо
        toolbar_layout.addStretch()
        
        # Поле поиска справа
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        self.search_input.setMinimumWidth(250)
        self.search_input.setMaximumWidth(350)
        self.search_input.setPlaceholderText("Поиск по имени...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #666666;
                background-color: #333333;
            }
            QLineEdit::placeholder {
                color: #666666;
            }
        """)
        self.search_input.textChanged.connect(self._search_mods)
        toolbar_layout.addWidget(self.search_input)
        
        main_layout.addLayout(toolbar_layout)
        
        # ---- Список модов с красивым скроллбаром ----
        self.mods_list = QListWidget()
        self.mods_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
                color: #cccccc;
                font-size: 14px;
                padding: 5px;
                outline: none;
            }
            
            QListWidget::item {
                padding: 0px;
                border-radius: 4px;
                margin: 1px 0;
                border-bottom: 1px solid #2a2a2a;
                background-color: transparent;
            }
            
            QListWidget::item:last {
                border-bottom: none;
            }
            
            QListWidget::item:hover {
                background-color: #2a2a2a;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: transparent;
                color: #cccccc;
            }
            
            QListWidget::item:selected:hover {
                background-color: #2a2a2a;
                border-radius: 4px;
            }
            
            /* Кастомный скроллбар */
            QScrollBar:vertical {
                background-color: #1a1a1a;
                border: none;
                border-radius: 4px;
                width: 8px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #444444;
                border-radius: 4px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #888888;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar:horizontal {
                background-color: #1a1a1a;
                border: none;
                border-radius: 4px;
                height: 8px;
                margin: 2px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #444444;
                border-radius: 4px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #666666;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: #888888;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.mods_list.setUniformItemSizes(True)
        self.mods_list.setMinimumHeight(400)
        main_layout.addWidget(self.mods_list)
    
    def refresh_mods(self):
        self._load_paths()
        self.mod_widgets.clear()
        
        if not self.workshop_path and not self.custom_path:
            self.mods_list.clear()
            item = QListWidgetItem("Пути к папкам модов не заданы в настройках")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(150, 150, 150))
            self.mods_list.addItem(item)
            return
        
        paths_exist = False
        if self.workshop_path and os.path.exists(self.workshop_path):
            paths_exist = True
        if self.custom_path and os.path.exists(self.custom_path):
            paths_exist = True
        
        if not paths_exist:
            self.mods_list.clear()
            item = QListWidgetItem("Указанные папки не существуют")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(180, 80, 80))
            self.mods_list.addItem(item)
            return
        
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Загрузка...")
        
        self.scanner = ModScanner(self.workshop_path, self.custom_path)
        self.scanner.finished.connect(self._on_mods_loaded)
        self.scanner.error.connect(self._on_scan_error)
        self.scanner.start()
    
    def _on_mods_loaded(self, mods):
        self.mods = mods
        self._display_mods(mods)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Обновить")
        
        if mods:
            self.notifications.show_success(
                "Моды загружены",
                f"Найдено {len(mods)} модов",
                3000
            )
        else:
            self.notifications.show_warning(
                "Моды не найдены",
                "Не найдено ни одного мода",
                3000
            )
    
    def _on_scan_error(self, error):
        self.mods_list.clear()
        item = QListWidgetItem(f"Ошибка: {error}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QColor(180, 80, 80))
        self.mods_list.addItem(item)
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Обновить")
        self.notifications.show_error("Ошибка сканирования", error, 5000)
    
    def _display_mods(self, mods):
        self.mods_list.clear()
        self.mod_widgets.clear()
        
        if not mods:
            item = QListWidgetItem("Моды не найдены")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(150, 150, 150))
            self.mods_list.addItem(item)
            return
        
        for mod in mods:
            # Создаём кастомный виджет для мода
            item_widget = ModItemWidget(mod)
            
            # Подключаем сигналы кнопок
            item_widget.server_toggled.connect(self._on_server_toggled)
            item_widget.cloud_toggled.connect(self._on_cloud_toggled)
            item_widget.gamepad_toggled.connect(self._on_gamepad_toggled)
            
            # Сохраняем виджет по имени мода
            self.mod_widgets[mod['name']] = item_widget
            
            # Добавляем в список
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, mod)
            item.setSizeHint(QSize(0, 42))
            self.mods_list.addItem(item)
            self.mods_list.setItemWidget(item, item_widget)
    
    def _on_server_toggled(self, mod_data, enabled):
        """Обработчик переключения кнопки сервера."""
        status = "включён" if enabled else "выключен"
        self.notifications.show_info(
            f"Серверный мод {status}",
            f"{mod_data['name']} - {status}",
            2000
        )
        print(f"[Сервер] {mod_data['name']} -> {status}")
    
    def _on_cloud_toggled(self, mod_data, enabled):
        """Обработчик переключения кнопки облака."""
        status = "включён" if enabled else "выключен"
        self.notifications.show_info(
            f"Облачный мод {status}",
            f"{mod_data['name']} - {status}",
            2000
        )
        print(f"[Облако] {mod_data['name']} -> {status}")
    
    def _on_gamepad_toggled(self, mod_data, enabled):
        """Обработчик переключения кнопки геймпада."""
        status = "включён" if enabled else "выключен"
        self.notifications.show_info(
            f"Клиентский мод {status}",
            f"{mod_data['name']} - {status}",
            2000
        )
        print(f"[Клиент] {mod_data['name']} -> {status}")
    
    def _reset_all_states(self):
        """Сбрасывает все состояния кнопок."""
        for widget in self.mod_widgets.values():
            widget.set_server_state(False)
            widget.set_cloud_state(False)
            widget.set_gamepad_state(False)
        
        self.notifications.show_info(
            "Все состояния сброшены",
            "Все кнопки выключены",
            2000
        )
    
    def _search_mods(self):
        search_text = self.search_input.text().strip().lower()
        
        if not search_text:
            self._display_mods(self.mods)
            return
        
        filtered = []
        for mod in self.mods:
            if search_text in mod['name'].lower():
                filtered.append(mod)
        
        self._display_mods(filtered)
    
    def _open_workshop(self):
        if self.workshop_path and os.path.exists(self.workshop_path):
            os.startfile(self.workshop_path)
        else:
            self.notifications.show_warning(
                "Папка не найдена",
                "Путь к Workshop не задан или папка не существует",
                3000
            )
    
    def _open_custom(self):
        if self.custom_path and os.path.exists(self.custom_path):
            os.startfile(self.custom_path)
        else:
            self.notifications.show_warning(
                "Папка не найдена",
                "Путь к кастомным модам не задан или папка не существует",
                3000
            )