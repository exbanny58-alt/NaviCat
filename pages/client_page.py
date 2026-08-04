# client_page.py

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter
from svg_icons import SVGIcon
from notifications import get_notification_manager
from dialog import CustomDialog
from symlink_manager import SymlinkManager


class ClientItemWidget(QWidget):
    """Виджет для отображения одного клиентского мода с кнопкой Подключить."""
    
    def __init__(self, mod_data, parent=None):
        super().__init__(parent)
        self.mod_data = mod_data
        self.is_connected = False
        
        # Создаём иконки геймпада с правильным размером и прозрачностью
        self.gamepad_icon_on = self._create_icon(
            SVGIcon.create_gamepad_icon("#44ff88"),
            20
        )
        self.gamepad_icon_off = self._create_icon(
            SVGIcon.create_gamepad_icon("#888888"),
            20
        )
        
        self._setup_ui()
        
        # Настройка hover эффекта
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            ClientItemWidget {
                background-color: transparent;
                border-radius: 4px;
                border-bottom: 1px solid #2a2a2a;
            }
            ClientItemWidget:hover {
                background-color: #2a2a2a;
            }
        """)
    
    def _create_icon(self, svg_string, size):
        """Создаёт QPixmap из SVG с прозрачным фоном."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(svg_string.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        
        # Иконка геймпада (слева)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setPixmap(self.gamepad_icon_off.scaled(
            24, 24, Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(self.icon_label)
        
        # Название мода
        name_label = QLabel(self.mod_data['name'])
        name_label.setStyleSheet("color: #cccccc; font-size: 14px; font-weight: 500; background-color: transparent;")
        name_label.setWordWrap(False)
        layout.addWidget(name_label, 1)
        
        # Информация (автор, версия)
        info_parts = []
        if self.mod_data.get('author'):
            info_parts.append(self.mod_data['author'])
        if self.mod_data.get('version'):
            info_parts.append(f"v{self.mod_data['version']}")
        if self.mod_data.get('id') and self.mod_data.get('type') == 'Workshop':
            info_parts.append(f"ID: {self.mod_data['id']}")
        
        if info_parts:
            info_label = QLabel(" | ".join(info_parts))
            info_label.setStyleSheet("color: #666666; font-size: 12px; background-color: transparent;")
            info_label.setWordWrap(False)
            layout.addWidget(info_label)
        
        # Тип мода
        type_label = QLabel(self.mod_data.get('type', 'Мод'))
        type_label.setStyleSheet("""
            color: #88ccaa;
            font-size: 11px;
            background-color: #2a2a2a;
            padding: 2px 10px;
            border-radius: 10px;
        """)
        layout.addWidget(type_label)
        
        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: #333333; max-width: 1px;")
        sep.setFixedWidth(1)
        sep.setFixedHeight(30)
        layout.addWidget(sep)
        
        # Кнопка Подключить/Отключить (белая)
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.setFixedSize(120, 30)
        self.connect_btn.setCheckable(True)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #777777;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QPushButton:checked {
                background-color: #3a6a3a;
                color: #88ff88;
                border-color: #44aa44;
            }
            QPushButton:checked:hover {
                background-color: #4a7a4a;
                border-color: #66cc66;
            }
            QPushButton:checked:pressed {
                background-color: #2a5a2a;
            }
        """)
        self.connect_btn.clicked.connect(self._on_connect_toggled)
        layout.addWidget(self.connect_btn)
        
        self.setMinimumHeight(40)
    
    def _on_connect_toggled(self, checked):
        self.is_connected = checked
        if checked:
            self.connect_btn.setText("Отключить")
            self.icon_label.setPixmap(self.gamepad_icon_on.scaled(
                24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.connect_btn.setText("Подключить")
            self.icon_label.setPixmap(self.gamepad_icon_off.scaled(
                24, 24, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
    
    def set_connected_state(self, connected):
        """Устанавливает состояние подключения."""
        self.connect_btn.setChecked(connected)
        self._on_connect_toggled(connected)
    
    def get_connection_state(self):
        """Возвращает состояние подключения."""
        return self.is_connected


class ClientPage(QWidget):
    """Страница клиента - отображает моды с Client-статусом."""
    
    # Сигнал для обновления страницы модов
    mods_status_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1a1a1a;")
        self.notifications = get_notification_manager()
        
        # Пути к конфигам
        self.config_dir = "config"
        self.mods_status_file = os.path.join(self.config_dir, "mods_status.json")
        self.client_connections_file = os.path.join(self.config_dir, "client_connections.json")
        self.server_connections_file = os.path.join(self.config_dir, "server_connections.json")
        
        # Создаём папку config, если её нет
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Данные
        self.client_mods = []
        self.mod_widgets = {}  # {mod_name: widget}
        self.connections = {}  # {mod_name: True/False или {connected: True, symlink_path: "..."}}
        self.last_status_hash = ""  # Хеш для отслеживания изменений
        
        # Пути из настроек
        self.workshop_path = ""
        self.custom_path = ""
        
        # Менеджер симлинков
        self.symlink_manager = SymlinkManager()
        
        self._load_paths()
        self._load_connections()
        self._setup_ui()
        
        # Таймер для автоматического обновления
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.setInterval(2000)  # 2 секунды
        self.auto_refresh_timer.timeout.connect(self._check_and_refresh)
        self.auto_refresh_timer.start()
        
        # Загружаем моды
        QTimer.singleShot(200, self.load_client_mods)
    
    def _load_paths(self):
        """Загружает пути из настроек."""
        config_file = os.path.join(self.config_dir, "settings.json")
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.workshop_path = settings.get("Путь до папки Workshop", "").replace('\\', '/')
                    self.custom_path = settings.get("Путь до папки своих модов", "").replace('\\', '/')
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")
    
    def _load_connections(self):
        """Загружает сохранённые подключения."""
        if os.path.exists(self.client_connections_file):
            try:
                with open(self.client_connections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data and isinstance(data, dict):
                        first_value = next(iter(data.values())) if data else None
                        if isinstance(first_value, dict):
                            self.connections = {mod_name: info.get("connected", False) 
                                              for mod_name, info in data.items()}
                        else:
                            self.connections = data
                    else:
                        self.connections = {}
            except Exception as e:
                print(f"Ошибка загрузки подключений: {e}")
                self.connections = {}
        else:
            self.connections = {}
    
    def _save_connections(self):
        """Сохраняет ВСЕ состояния подключений в файл с путями к симлинкам."""
        try:
            connections = {}
            for mod_name, widget in self.mod_widgets.items():
                client_path = self._get_client_path()
                if client_path:
                    symlink_exists = self.symlink_manager.check_symlink_exists(mod_name, client_path)
                    if widget.get_connection_state() or symlink_exists:
                        symlink_path = None
                        if client_path:
                            symlink_name = f"@{mod_name}"
                            symlink_path = os.path.join(client_path, symlink_name)
                            if not os.path.exists(symlink_path):
                                symlink_path = None
                        
                        connections[mod_name] = {
                            "connected": widget.get_connection_state(),
                            "symlink_path": symlink_path,
                            "mod_type": "Client"
                        }
            
            with open(self.client_connections_file, 'w', encoding='utf-8') as f:
                json.dump(connections, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Ошибка сохранения подключений: {e}")
    
    def _load_server_connections(self):
        """Загружает серверные подключения из файла."""
        if os.path.exists(self.server_connections_file):
            try:
                with open(self.server_connections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data and isinstance(data, dict):
                        first_value = next(iter(data.values())) if data else None
                        if isinstance(first_value, dict):
                            return {mod_name: info.get("connected", False) 
                                   for mod_name, info in data.items()}
                        else:
                            return data
                    return {}
            except Exception as e:
                print(f"Ошибка загрузки серверных подключений: {e}")
                return {}
        return {}
    
    def _mark_mods_as_client(self, mod_names):
        """Отмечает моды как Client в mods_status.json."""
        try:
            if os.path.exists(self.mods_status_file):
                with open(self.mods_status_file, 'r', encoding='utf-8') as f:
                    mods_status = json.load(f)
            else:
                mods_status = {}
            
            added_count = 0
            for mod_name in mod_names:
                if mod_name not in mods_status:
                    mods_status[mod_name] = {}
                
                if not mods_status[mod_name].get('Client', False):
                    mods_status[mod_name]['Client'] = True
                    added_count += 1
            
            if added_count > 0:
                with open(self.mods_status_file, 'w', encoding='utf-8') as f:
                    json.dump(mods_status, f, ensure_ascii=False, indent=4)
                self.mods_status_changed.emit()
                print(f"Отмечено {added_count} модов как Client")
            
            return added_count
            
        except Exception as e:
            print(f"Ошибка отметки модов как Client: {e}")
            return 0
    
    def _get_status_file_hash(self):
        """Возвращает хеш содержимого файла статусов."""
        if not os.path.exists(self.mods_status_file):
            return ""
        try:
            with open(self.mods_status_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return str(hash(content))
        except Exception:
            return ""
    
    def _check_and_refresh(self):
        """Проверяет изменения и обновляет список при необходимости."""
        current_hash = self._get_status_file_hash()
        if current_hash != self.last_status_hash:
            self.last_status_hash = current_hash
            self.load_client_mods()
    
    def _setup_ui(self):
        """Создаёт интерфейс страницы клиента."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Заголовок с кнопками
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        title_label = QLabel("Клиентские моды")
        title_label.setStyleSheet("color: #cccccc; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Кнопка "Подключить все/Отключить все"
        self.toggle_all_btn = QPushButton("Подключить все")
        self.toggle_all_btn.setFixedSize(160, 36)
        self.toggle_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #777777;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        self.toggle_all_btn.clicked.connect(self._toggle_all_connections)
        header_layout.addWidget(self.toggle_all_btn)
        
        # Кнопка "Очистить CFG"
        self.clear_cfg_btn = QPushButton("🗑️ Очистить CFG")
        self.clear_cfg_btn.setFixedSize(160, 36)
        self.clear_cfg_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a2a2a;
                color: #ff8888;
                border-color: #aa4444;
            }
            QPushButton:pressed {
                background-color: #4a1a1a;
            }
        """)
        self.clear_cfg_btn.clicked.connect(self._clear_client_cfg)
        header_layout.addWidget(self.clear_cfg_btn)
        
        # Кнопка "Подключить моды сервера"
        self.connect_server_btn = QPushButton()
        self.connect_server_btn.setIcon(SVGIcon.svg_to_icon(
            SVGIcon.create_gamepad_icon("#aaaaaa"),
            size=20
        ))
        self.connect_server_btn.setIconSize(QSize(20, 20))
        self.connect_server_btn.setText(" Подключить моды сервера")
        self.connect_server_btn.setFixedSize(260, 36)
        self.connect_server_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #777777;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        self.connect_server_btn.clicked.connect(self._on_connect_server_clicked)
        header_layout.addWidget(self.connect_server_btn)
        
        # Кнопка обновления с иконкой
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(SVGIcon.svg_to_icon(
            SVGIcon.create_refresh_icon("#aaaaaa"),
            size=20
        ))
        self.refresh_btn.setIconSize(QSize(20, 20))
        self.refresh_btn.setToolTip("Обновить список")
        self.refresh_btn.setFixedSize(40, 36)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border-color: #666666;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_client_mods)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Список модов
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
                margin: 0px;
                background-color: transparent;
                border-bottom: 1px solid #2a2a2a;
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
        
        main_layout.addWidget(self.mods_list, 1)
    
    def _get_client_path(self):
        """Возвращает путь к клиенту (игре) из настроек."""
        try:
            config_file = os.path.join(self.config_dir, "settings.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    exe_path = settings.get("Путь до exe файла игры", "").replace('\\', '/')
                    if exe_path:
                        return os.path.dirname(exe_path)
            return ""
        except Exception as e:
            print(f"Ошибка получения пути к клиенту: {e}")
            return ""
    
    def _toggle_all_connections(self):
        """Переключает состояние всех модов (подключить все/отключить все)."""
        if not self.mod_widgets:
            self.notifications.show_warning(
                "Нет модов",
                "Список модов пуст",
                2000
            )
            return
        
        # Проверяем, все ли моды уже подключены
        all_connected = True
        for widget in self.mod_widgets.values():
            if not widget.get_connection_state():
                all_connected = False
                break
        
        new_state = not all_connected
        client_path = self._get_client_path()
        
        if not client_path:
            self.notifications.show_error(
                "Путь не найден",
                "Не задан путь к exe файлу игры в настройках",
                5000
            )
            return
        
        # Обновляем состояние виджетов и создаём/удаляем симлинки
        success_count = 0
        for widget in self.mod_widgets.values():
            mod_data = widget.mod_data
            # Обновляем виджет
            widget.set_connected_state(new_state)
            # Создаём/удаляем симлинк
            if new_state:
                success, _ = self.symlink_manager.create_symlink(
                    mod_data, 
                    client_path, 
                    "Client"
                )
                if success:
                    success_count += 1
            else:
                self.symlink_manager.remove_symlink(mod_data['name'], client_path)
        
        # Сохраняем состояния
        self._save_connections()
        
        # Обновляем кнопку "Подключить все"
        self._update_toggle_all_button()
        
        if new_state:
            self.notifications.show_success(
                "Все моды подключены",
                f"Подключено {success_count} модов",
                3000
            )
        else:
            self.notifications.show_info(
                "Все моды отключены",
                f"Отключено {len(self.mod_widgets)} модов",
                3000
            )
    
    def _clear_client_cfg(self):
        """Очищает конфиг клиентских подключений и удаляет симлинки."""
        confirmed = CustomDialog.question(
            self,
            "Очистка CFG клиента",
            "Вы действительно хотите очистить все клиентские подключения?\n\n"
            "Будут удалены все симлинки из папки игры.\n"
            "Это действие нельзя отменить.",
            default=False
        )
        
        if not confirmed:
            return
        
        try:
            client_path = self._get_client_path()
            
            removed_count = 0
            for mod_name in list(self.connections.keys()):
                if self.symlink_manager.remove_symlink(mod_name, client_path):
                    removed_count += 1
            
            if os.path.exists(self.client_connections_file):
                os.remove(self.client_connections_file)
                self.connections = {}
                
                for widget in self.mod_widgets.values():
                    widget.set_connected_state(False)
                
                self._update_toggle_all_button()
                self.load_client_mods()
                
                self.notifications.show_success(
                    "CFG клиента очищен",
                    f"Удалено {removed_count} симлинков",
                    3000
                )
            else:
                self.notifications.show_info(
                    "CFG уже пуст",
                    "Файл конфигурации не существует",
                    3000
                )
        except Exception as e:
            self.notifications.show_error(
                "Ошибка очистки",
                str(e),
                5000
            )
    
    def _on_connect_server_clicked(self):
        """Подключает моды, которые отмечены на странице сервера (только Server, не ServerSide)."""
        server_connections = self._load_server_connections()
        
        if not server_connections:
            self.notifications.show_warning(
                "Нет серверных модов",
                "На странице сервера нет подключённых модов",
                3000
            )
            return
        
        server_mod_names = list(server_connections.keys())
        
        serverside_mods = []
        if os.path.exists(self.mods_status_file):
            try:
                with open(self.mods_status_file, 'r', encoding='utf-8') as f:
                    mods_status = json.load(f)
                
                for mod_name in server_mod_names:
                    if mod_name in mods_status and mods_status[mod_name].get('ServerSide', False):
                        serverside_mods.append(mod_name)
            except Exception as e:
                print(f"Ошибка проверки ServerSide модов: {e}")
        
        filtered_mod_names = [mod for mod in server_mod_names if mod not in serverside_mods]
        
        if not filtered_mod_names:
            self.notifications.show_warning(
                "Только ServerSide моды",
                "Все серверные моды являются ServerSide и не могут быть подключены на клиенте",
                3000
            )
            return
        
        if serverside_mods:
            self.notifications.show_warning(
                "ServerSide моды исключены",
                f"{len(serverside_mods)} модов являются ServerSide и не будут подключены:\n"
                f"{', '.join(serverside_mods[:3])}"
                f"{'...' if len(serverside_mods) > 3 else ''}",
                5000
            )
        
        confirmed = CustomDialog.question(
            self,
            "Подключение модов сервера",
            f"Будет подключено {len(filtered_mod_names)} модов.\n\n"
            f"{'ServerSide моды исключены (' + str(len(serverside_mods)) + ' шт.)' if serverside_mods else ''}\n"
            "Моды будут отмечены как Client и подключены на клиенте.\n"
            "Продолжить?",
            default=True
        )
        
        if not confirmed:
            return
        
        marked_count = self._mark_mods_as_client(filtered_mod_names)
        
        if marked_count > 0:
            self.notifications.show_success(
                "Моды отмечены как Client",
                f"Отмечено {marked_count} новых модов",
                3000
            )
            self.last_status_hash = ""
            QTimer.singleShot(100, self._connect_server_mods)
        else:
            self._connect_server_mods()
    
    def _connect_server_mods(self):
        """Подключает серверные моды (внутренний метод)."""
        self.load_client_mods()
        server_connections = self._load_server_connections()
        
        if not server_connections:
            return
        
        client_path = self._get_client_path()
        
        if not client_path:
            self.notifications.show_error(
                "Путь не найден",
                "Не задан путь к exe файлу игры в настройках",
                5000
            )
            return
        
        connected_count = 0
        not_found_count = 0
        already_connected = 0
        not_found_mods = []
        
        for mod_name in server_connections.keys():
            if mod_name in self.mod_widgets:
                widget = self.mod_widgets[mod_name]
                if not widget.get_connection_state():
                    # Обновляем виджет
                    widget.set_connected_state(True)
                    # Создаём симлинк
                    mod_data = widget.mod_data
                    success, _ = self.symlink_manager.create_symlink(
                        mod_data, 
                        client_path, 
                        "Client"
                    )
                    if success:
                        connected_count += 1
                    else:
                        widget.set_connected_state(False)
                else:
                    already_connected += 1
            else:
                not_found_count += 1
                not_found_mods.append(mod_name)
        
        self._save_connections()
        self._update_toggle_all_button()
        
        if connected_count > 0:
            self.notifications.show_success(
                "Моды сервера подключены",
                f"Подключено {connected_count} модов",
                3000
            )
        
        if already_connected > 0:
            self.notifications.show_info(
                "Уже подключено",
                f"{already_connected} модов уже были подключены",
                3000
            )
        
        if not_found_count > 0:
            self.notifications.show_warning(
                "Моды не найдены",
                f"{not_found_count} модов не найдены на клиенте:\n"
                f"{', '.join(not_found_mods[:5])}"
                f"{'...' if len(not_found_mods) > 5 else ''}",
                5000
            )
        
        if connected_count == 0 and already_connected == 0 and not_found_count == 0:
            self.notifications.show_info(
                "Нет изменений",
                "Все серверные моды уже подключены",
                3000
            )
    
    def load_client_mods(self):
        """Загружает моды с Client-статусом."""
        self._load_connections()
        
        self.mods_list.clear()
        self.mod_widgets.clear()
        self.client_mods = []
        
        if not self.workshop_path and not self.custom_path:
            self._show_empty_state("Пути к папкам модов не заданы в настройках")
            return
        
        paths_exist = False
        if self.workshop_path and os.path.exists(self.workshop_path):
            paths_exist = True
        if self.custom_path and os.path.exists(self.custom_path):
            paths_exist = True
        
        if not paths_exist:
            self._show_empty_state("Указанные папки не существуют")
            return
        
        if not os.path.exists(self.mods_status_file):
            self._show_empty_state("Нет отмеченных Client-модов\n\nОтметьте моды как Client на странице 'Моды'")
            return
        
        try:
            with open(self.mods_status_file, 'r', encoding='utf-8') as f:
                mods_status = json.load(f)
            
            client_mod_names = []
            for mod_name, statuses in mods_status.items():
                if statuses.get('Client', False):
                    client_mod_names.append(mod_name)
            
            if not client_mod_names:
                self._show_empty_state("Нет отмеченных Client-модов\n\nОтметьте моды как Client на странице 'Моды'")
                return
            
            self._load_mod_data(client_mod_names)
            
        except Exception as e:
            self._show_empty_state(f"Ошибка загрузки: {str(e)}")
            self.notifications.show_error("Ошибка", str(e), 5000)
    
    def _load_mod_data(self, client_mod_names):
        """Загружает полные данные о модах из папок."""
        all_mods = []
        
        if self.workshop_path and os.path.exists(self.workshop_path):
            workshop_mods = self._scan_workshop(self.workshop_path)
            all_mods.extend(workshop_mods)
        
        if self.custom_path and os.path.exists(self.custom_path):
            custom_mods = self._scan_custom(self.custom_path)
            all_mods.extend(custom_mods)
        
        self.client_mods = [mod for mod in all_mods if mod['name'] in client_mod_names]
        self.client_mods.sort(key=lambda x: x['name'].lower())
        
        self._display_mods()
        self._update_toggle_all_button()
        
        if self.client_mods:
            self.notifications.show_success(
                "Моды загружены",
                f"Найдено {len(self.client_mods)} Client-модов",
                3000
            )
    
    def _update_toggle_all_button(self):
        """Обновляет текст кнопки 'Подключить все/Отключить все'."""
        if not self.mod_widgets:
            self.toggle_all_btn.setText("Подключить все")
            return
        
        all_connected = True
        for widget in self.mod_widgets.values():
            if not widget.get_connection_state():
                all_connected = False
                break
        
        if all_connected:
            self.toggle_all_btn.setText("Отключить все")
        else:
            self.toggle_all_btn.setText("Подключить все")
    
    def _scan_workshop(self, path):
        """Сканирует папку Workshop."""
        mods = []
        try:
            content_path = os.path.join(path, "content", "221100")
            if not os.path.exists(content_path):
                content_path = path
            
            for item in os.listdir(content_path):
                item_path = os.path.join(content_path, item)
                if os.path.isdir(item_path):
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
        """Сканирует папку кастомных модов."""
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
        except Exception as e:
            print(f"Ошибка сканирования кастомных модов: {e}")
        return mods
    
    def _read_any_meta(self, mod_path):
        """Читает мета-файлы мода."""
        import re
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
                except Exception:
                    continue
        return None
    
    def _display_mods(self):
        """Отображает моды в списке."""
        self.mods_list.clear()
        self.mod_widgets.clear()
        
        if not self.client_mods:
            self._show_empty_state("Нет Client-модов для отображения")
            return
        
        for mod in self.client_mods:
            item_widget = ClientItemWidget(mod)
            
            if mod['name'] in self.connections:
                is_connected = self.connections[mod['name']]
                item_widget.set_connected_state(is_connected)
            else:
                item_widget.set_connected_state(False)
            
            item_widget.connect_btn.clicked.connect(
                lambda checked, m=mod: self._on_connection_toggled(m, checked)
            )
            
            self.mod_widgets[mod['name']] = item_widget
            
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, mod)
            item.setSizeHint(QSize(0, 42))
            self.mods_list.addItem(item)
            self.mods_list.setItemWidget(item, item_widget)
        
        self._update_toggle_all_button()
    
    def _on_connection_toggled(self, mod_data, checked):
        """Обработчик переключения подключения."""
        client_path = self._get_client_path()
        
        if not client_path:
            self.notifications.show_error(
                "Путь не найден",
                "Не задан путь к exe файлу игры в настройках",
                5000
            )
            widget = self.mod_widgets.get(mod_data['name'])
            if widget:
                widget.set_connected_state(False)
            return
        
        if checked:
            success, symlink_path = self.symlink_manager.create_symlink(
                mod_data, 
                client_path, 
                "Client"
            )
            if success:
                self._save_connections()
                self._update_toggle_all_button()
                self.notifications.show_success(
                    f"Мод подключён: {mod_data['name']}",
                    f"Симлинк создан: {os.path.basename(symlink_path)}",
                    3000
                )
            else:
                widget = self.mod_widgets.get(mod_data['name'])
                if widget:
                    widget.set_connected_state(False)
        else:
            success = self.symlink_manager.remove_symlink(mod_data['name'], client_path)
            if success:
                self._save_connections()
                self._update_toggle_all_button()
                self.notifications.show_info(
                    f"Мод отключён: {mod_data['name']}",
                    "Симлинк удалён",
                    3000
                )
    
    def _show_empty_state(self, message):
        """Показывает сообщение о пустом списке."""
        self.mods_list.clear()
        self.mod_widgets.clear()
        self.client_mods = []
        self.toggle_all_btn.setText("Подключить все")
        
        item = QListWidgetItem(message)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QColor(150, 150, 150))
        self.mods_list.addItem(item)