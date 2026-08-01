import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtSvg import QSvgRenderer
from notifications import get_notification_manager
from music_player import MusicPlayer


class MusicPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        self.notifications = get_notification_manager()
        
        # Путь к конфиг-файлу
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.music_path = ""
        
        # Создаём плеер
        self.player = MusicPlayer()
        
        # Создаём иконки
        self.music_icon = self._create_icon_from_svg(self._get_music_note_svg())
        self.play_icon = self._create_icon_from_svg(self._get_play_svg())
        self.pause_icon = self._create_icon_from_svg(self._get_pause_svg())
        
        # Храним кнопки для обновления состояний
        self.play_buttons = {}
        
        self._setup_ui()
        self._load_music_path()
        
        # Подключаем сигналы плеера
        self.player.track_changed.connect(self._on_track_changed)
        self.player.state_changed.connect(self._on_player_state_changed)
        self.player.error_occurred.connect(self._on_player_error)
    
    def _get_music_note_svg(self):
        """Возвращает SVG иконки ноты."""
        return '''<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14" id="Music-Note-Circle--Streamline-Flex-Remix" height="14" width="14">
            <path fill="#888888" fill-rule="evenodd" d="M2.72444 2.72444C1.78946 3.65942 1.25 5.07504 1.25 7c0 1.92496 0.53946 3.3406 1.47444 4.2756C3.65942 12.2105 5.07504 12.75 7 12.75c1.92496 0 3.3406 -0.5395 4.2756 -1.4744C12.2105 10.3406 12.75 8.92496 12.75 7s-0.5395 -3.34058 -1.4744 -4.27556C10.3406 1.78946 8.92496 1.25 7 1.25s-3.34058 0.53946 -4.27556 1.47444Zm-0.88388 -0.88388C3.07308 0.60804 4.84496 0 7 0s3.9269 0.60804 5.1594 1.84056C13.392 3.07308 14 4.84496 14 7s-0.608 3.9269 -1.8406 5.1594C10.9269 13.392 9.15504 14 7 14c-2.15504 0 -3.92692 -0.608 -5.15944 -1.8406C0.60804 10.9269 0 9.15504 0 7c0 -2.15504 0.60804 -3.92692 1.84056 -5.15944Zm5.08762 1.38308h0.00118l0.00319 0.00002 0.01158 0.00005 0.03827 0.0002c0.02928 0.00018 0.067 0.00045 0.0935 0.00085 1.84606 0.02737 3.4528 1.58464 3.4528 3.45732 0 0.34518 -0.2798 0.625 -0.62496 0.625 -0.34518 0 -0.625 -0.27982 -0.625 -0.625 0 -0.99855 -0.76025 -1.89633 -1.72796 -2.14174v4.19634c0 0.00755 -0.00013 0.01506 -0.0004 0.02254 -0.00415 0.55919 -0.16651 1.08208 -0.55059 1.46618 -0.38913 0.3891 -0.92074 0.5507 -1.48823 0.5507 -0.56749 0 -1.0991 -0.1616 -1.48823 -0.5507 -0.38913 -0.38916 -0.55067 -0.92076 -0.55067 -1.48825 0 -0.5675 0.16154 -1.0991 0.55067 -1.48823 0.38913 -0.38914 0.92074 -0.55068 1.48823 -0.55068 0.27561 0 0.54275 0.0381 0.78922 0.12187V3.84863c0 -0.16617 0.06618 -0.32551 0.18391 -0.44279 0.11773 -0.11727 0.27732 -0.18284 0.44349 -0.1822Z" clip-rule="evenodd" stroke-width="1"></path>
        </svg>'''
    
    def _get_play_svg(self):
        """Возвращает SVG иконки Play."""
        return '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" id="Play-Circle--Streamline-Solar-Ar" height="24" width="24">
            <path stroke="#888888" d="M2 12a10 10 0 1 0 20 0 10 10 0 1 0 -20 0" stroke-width="1.5"></path>
            <path d="M15.4137 10.941c0.7817 0.4616 0.7817 1.6564 0 2.118l-4.7202 2.7868C9.93371 16.2944 9 15.7105 9 14.7868l0 -5.57364c0 -0.92369 0.93371 -1.50755 1.6935 -1.05897l4.7202 2.78681Z" stroke="#888888" stroke-width="1.5"></path>
        </svg>'''
    
    def _get_pause_svg(self):
        """Возвращает SVG иконки Pause."""
        return '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" id="Pause-Circle--Streamline-Solar-Ar" height="24" width="24">
            <path stroke="#888888" d="M2 12a10 10 0 1 0 20 0 10 10 0 1 0 -20 0" stroke-width="1.5"></path>
            <path d="M8 9.5c0 -0.46594 0 -0.69891 0.07612 -0.88268 0.10149 -0.24503 0.29617 -0.43971 0.5412 -0.5412C8.80109 8 9.03406 8 9.5 8s0.6989 0 0.8827 0.07612c0.245 0.10149 0.4397 0.29617 0.5412 0.5412C11 8.80109 11 9.03406 11 9.5v5c0 0.4659 0 0.6989 -0.0761 0.8827 -0.1015 0.245 -0.2962 0.4397 -0.5412 0.5412C10.1989 16 9.96594 16 9.5 16s-0.69891 0 -0.88268 -0.0761c-0.24503 -0.1015 -0.43971 -0.2962 -0.5412 -0.5412C8 15.1989 8 14.9659 8 14.5v-5Z" stroke="#888888" stroke-width="1.5"></path>
            <path d="M13 9.5c0 -0.46594 0 -0.69891 0.0761 -0.88268 0.1015 -0.24503 0.2962 -0.43971 0.5412 -0.5412C13.8011 8 14.0341 8 14.5 8c0.4659 0 0.6989 0 0.8827 0.07612 0.245 0.10149 0.4397 0.29617 0.5412 0.5412C16 8.80109 16 9.03406 16 9.5v5c0 0.4659 0 0.6989 -0.0761 0.8827 -0.1015 0.245 -0.2962 0.4397 -0.5412 0.5412C15.1989 16 14.9659 16 14.5 16c-0.4659 0 -0.6989 0 -0.8827 -0.0761 -0.245 -0.1015 -0.4397 -0.2962 -0.5412 -0.5412C13 15.1989 13 14.9659 13 14.5v-5Z" stroke="#888888" stroke-width="1.5"></path>
        </svg>'''
    
    def _create_icon_from_svg(self, svg_string, size=24):
        """Создаёт QIcon из SVG строки."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        renderer = QSvgRenderer(QByteArray(svg_string.encode()))
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
        
    def _setup_ui(self):
        """Создаёт интерфейс страницы музыки."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)
        
        # Список треков с красивым скроллбаром
        self.track_list_widget = QListWidget()
        self.track_list_widget.setStyleSheet("""
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
                margin: 2px 0;
            }
            
            QListWidget::item:hover {
                background-color: #2a2a2a;
            }
            
            QListWidget::item:selected {
                background-color: #3a6ea5;
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
        
        # Устанавливаем фиксированную высоту элементов
        self.track_list_widget.setUniformItemSizes(True)
        
        main_layout.addWidget(self.track_list_widget)
        
    def _load_music_path(self):
        """Загружает путь к музыке из конфига."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.music_path = settings.get("Путь до папки с музыкой", "")
                    if self.music_path:
                        self.load_tracks()
            except Exception as e:
                self.notifications.show_error("Ошибка загрузки", str(e), 5000)
    
    def load_tracks(self):
        """Загружает список треков из папки с музыкой."""
        self.track_list_widget.clear()
        self.play_buttons.clear()
        
        if not self.music_path or not os.path.exists(self.music_path):
            item = QListWidgetItem("Папка с музыкой не выбрана")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(Qt.GlobalColor.gray)
            self.track_list_widget.addItem(item)
            return
        
        self._scan_tracks()
    
    def _scan_tracks(self):
        """Сканирует папку на наличие музыкальных файлов."""
        try:
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
            track_count = 0
            
            for root, dirs, files in os.walk(self.music_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in audio_extensions:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.music_path)
                        
                        # Создаём виджет для элемента списка
                        item_widget = QWidget()
                        item_widget.setStyleSheet("background-color: transparent;")
                        
                        item_layout = QHBoxLayout(item_widget)
                        item_layout.setContentsMargins(10, 8, 10, 8)
                        item_layout.setSpacing(12)
                        
                        # Иконка ноты
                        icon_label = QLabel()
                        icon_label.setPixmap(self.music_icon.pixmap(QSize(20, 20)))
                        icon_label.setFixedSize(20, 20)
                        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        item_layout.addWidget(icon_label)
                        
                        # Название трека
                        name_label = QLabel(rel_path)
                        name_label.setStyleSheet("color: #cccccc; font-size: 14px;")
                        name_label.setWordWrap(False)
                        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                        item_layout.addWidget(name_label, 1)
                        
                        # Кнопка Play/Pause
                        play_btn = QPushButton()
                        play_btn.setIcon(self.play_icon)
                        play_btn.setIconSize(QSize(24, 24))
                        play_btn.setFixedSize(32, 32)
                        play_btn.setStyleSheet("""
                            QPushButton {
                                background-color: transparent;
                                border: none;
                                border-radius: 16px;
                                padding: 4px;
                            }
                            QPushButton:hover {
                                background-color: #2a2a2a;
                            }
                            QPushButton:pressed {
                                background-color: #3a3a3a;
                            }
                        """)
                        play_btn.setProperty("file_path", full_path)
                        play_btn.clicked.connect(self._on_play_clicked)
                        item_layout.addWidget(play_btn)
                        
                        # Добавляем в список
                        item = QListWidgetItem()
                        item.setData(Qt.ItemDataRole.UserRole, full_path)
                        item.setSizeHint(QSize(0, 50))  # Фиксированная высота
                        self.track_list_widget.addItem(item)
                        self.track_list_widget.setItemWidget(item, item_widget)
                        
                        # Сохраняем ссылку на кнопку
                        self.play_buttons[full_path] = play_btn
                        track_count += 1
            
            if track_count == 0:
                item = QListWidgetItem("Нет музыкальных файлов")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(Qt.GlobalColor.gray)
                self.track_list_widget.addItem(item)
                
        except Exception as e:
            item = QListWidgetItem(f"Ошибка: {str(e)}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(Qt.GlobalColor.red)
            self.track_list_widget.addItem(item)
    
    def _on_play_clicked(self):
        """Обработчик нажатия на кнопку Play/Pause."""
        btn = self.sender()
        file_path = btn.property("file_path")
        
        if not file_path:
            return
        
        # Если этот трек уже загружен в плеере
        if self.player.get_current_track_path() == file_path:
            if self.player.is_playing:
                # Если играет - ставим на паузу
                self.player.pause()
                btn.setIcon(self.play_icon)
            else:
                # Если на паузе - возобновляем
                self.player.play()
                btn.setIcon(self.pause_icon)
        else:
            # Иначе начинаем воспроизведение нового трека
            self.player.play_track_by_path(file_path)
            # Обновляем все кнопки
            self._update_all_buttons()
    
    def _update_all_buttons(self):
        """Обновляет состояние всех кнопок Play/Pause."""
        current_track = self.player.get_current_track_path()
        
        for path, btn in self.play_buttons.items():
            if path == current_track:
                if self.player.is_playing:
                    btn.setIcon(self.pause_icon)
                else:
                    btn.setIcon(self.play_icon)
            else:
                btn.setIcon(self.play_icon)
    
    def _on_track_changed(self, path):
        """Обработчик смены трека."""
        self._update_all_buttons()
        self.notifications.show_info(
            "Сейчас играет",
            os.path.basename(path),
            3000
        )
    
    def _on_player_state_changed(self, state):
        """Обработчик изменения состояния плеера."""
        if state == "playing":
            self._update_all_buttons()
        elif state == "paused":
            # Обновляем все кнопки
            self._update_all_buttons()
        elif state == "stopped":
            # Сбрасываем все кнопки
            for btn in self.play_buttons.values():
                btn.setIcon(self.play_icon)
    
    def _on_player_error(self, error_message):
        """Обработчик ошибок плеера."""
        self.notifications.show_error("Ошибка воспроизведения", error_message, 5000)