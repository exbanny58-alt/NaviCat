# music_page.py

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtSvg import QSvgRenderer
from notifications import get_notification_manager
from music_player import MusicPlayer
from svg_icons import SVGIcon


class TrackItemWidget(QWidget):
    """Виджет для элемента списка треков с прогресс-баром и перемоткой."""
    
    def __init__(self, track_path, track_name, play_icon, pause_icon, music_icon, parent=None):
        super().__init__(parent)
        self.track_path = track_path
        self.progress = 0.0
        self.is_playing = False
        self.duration = 0  # Длительность трека в миллисекундах
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)
        
        # Иконка ноты
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setPixmap(music_icon.pixmap(QSize(20, 20)))
        layout.addWidget(self.icon_label)
        
        # Название трека
        self.name_label = QLabel(track_name)
        self.name_label.setStyleSheet("color: #cccccc; font-size: 14px; background-color: transparent;")
        self.name_label.setWordWrap(False)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.name_label, 1)
        
        # Кнопка Play/Pause
        self.play_btn = QPushButton()
        self.play_btn.setIcon(play_icon)
        self.play_btn.setIconSize(QSize(24, 24))
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
        """)
        self.play_btn.setProperty("file_path", track_path)
        layout.addWidget(self.play_btn)
        
        # Настройка для рисования прогресса и подчёркивания
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            TrackItemWidget {
                background-color: transparent;
                border-radius: 4px;
                border-bottom: 1px solid #2a2a2a;
            }
            TrackItemWidget:hover {
                background-color: #2a2a2a;
            }
        """)
        
        # Включаем отслеживание мыши для hover эффекта
        self.setMouseTracking(True)
        self.is_hovered = False
    
    def set_progress(self, progress):
        """Устанавливает прогресс (0.0 - 1.0)"""
        self.progress = max(0.0, min(1.0, progress))
        self.update()
    
    def set_duration(self, duration):
        """Устанавливает длительность трека в миллисекундах"""
        self.duration = duration
    
    def set_playing_state(self, is_playing):
        """Устанавливает состояние воспроизведения"""
        self.is_playing = is_playing
        self.update()
    
    def paintEvent(self, event):
        """Рисуем фон с прогрессом"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем прогресс-бар только если есть прогресс
        if self.progress > 0.01:
            # Серый цвет, светлее фона
            progress_color = QColor(58, 58, 58, 200)  # #3a3a3a с альфа 200
            
            # Если курсор наведён на прогресс, показываем более яркий цвет
            if self.is_hovered and self.progress > 0.01:
                progress_color = QColor(80, 80, 80, 220)  # #505050
            
            # Рисуем прямоугольник прогресса
            rect = self.rect()
            progress_width = int(rect.width() * self.progress)
            progress_rect = rect.adjusted(0, 0, -rect.width() + progress_width, 0)
            
            painter.setBrush(QBrush(progress_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(progress_rect, 4, 4)
        
        # Вызываем родительский paintEvent для отрисовки остального
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        """Обработка клика мыши для перемотки"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Получаем позицию клика относительно виджета
            pos = event.position().x()
            width = self.width()
            
            # Вычисляем прогресс от 0.0 до 1.0
            click_progress = max(0.0, min(1.0, pos / width))
            
            # Если есть длительность, отправляем сигнал о перемотке
            if self.duration > 0:
                new_position = int(click_progress * self.duration)
                # Создаём кастомный сигнал через родителя
                if self.parent():
                    # Ищем MusicPage в родителях
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'seek_to_position'):
                            parent.seek_to_position(self.track_path, new_position)
                            break
                        parent = parent.parent()
            
            # Обновляем прогресс для визуального отклика
            self.set_progress(click_progress)
            
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Курсор вошёл в область виджета"""
        self.is_hovered = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Курсор вышел из области виджета"""
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)


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
        
        # Создаём иконки через SVGIcon
        self.music_icon = SVGIcon.svg_to_icon(
            SVGIcon.create_music_note_icon("#888888"), 
            size=20
        )
        self.play_icon = SVGIcon.svg_to_icon(
            SVGIcon.create_play_circle_icon("#888888"), 
            size=24
        )
        self.pause_icon = SVGIcon.svg_to_icon(
            SVGIcon.create_pause_circle_icon("#888888"), 
            size=24
        )
        
        # Храним кнопки и виджеты для обновления состояний
        self.play_buttons = {}
        self.track_widgets = {}
        
        # Таймер для обновления прогресса
        self.progress_timer = QTimer()
        self.progress_timer.setInterval(200)  # Обновление 5 раз в секунду
        self.progress_timer.timeout.connect(self._update_progress)
        
        self._setup_ui()
        self._load_music_path()
        
        # Подключаем сигналы плеера
        self.player.track_changed.connect(self._on_track_changed)
        self.player.state_changed.connect(self._on_player_state_changed)
        self.player.position_changed.connect(self._on_position_changed)
        self.player.duration_changed.connect(self._on_duration_changed)
        self.player.error_occurred.connect(self._on_player_error)
        self.player.track_finished.connect(self._on_track_finished)
    
    def _setup_ui(self):
        """Создаёт интерфейс страницы музыки."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)
        
        # Заголовок страницы
        title_label = QLabel("Музыка")
        title_label.setStyleSheet("color: #cccccc; font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Отступ после заголовка
        spacer = QLabel()
        spacer.setFixedHeight(10)
        main_layout.addWidget(spacer)
        
        # Список треков с красивым скроллбаром и подчёркиванием
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
        
        main_layout.addWidget(self.track_list_widget, 1)
    
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
        self.track_widgets.clear()
        
        if not self.music_path or not os.path.exists(self.music_path):
            item = QListWidgetItem("Папка с музыкой не выбрана")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(150, 150, 150))
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
                        
                        # Создаём кастомный виджет
                        item_widget = TrackItemWidget(
                            full_path,
                            rel_path,
                            self.play_icon,
                            self.pause_icon,
                            self.music_icon
                        )
                        
                        # Подключаем кнопку
                        item_widget.play_btn.clicked.connect(self._on_play_clicked)
                        
                        # Добавляем в список
                        item = QListWidgetItem()
                        item.setData(Qt.ItemDataRole.UserRole, full_path)
                        item.setSizeHint(QSize(0, 52))
                        self.track_list_widget.addItem(item)
                        self.track_list_widget.setItemWidget(item, item_widget)
                        
                        # Сохраняем ссылки
                        self.play_buttons[full_path] = item_widget.play_btn
                        self.track_widgets[full_path] = item_widget
                        track_count += 1
            
            if track_count == 0:
                item = QListWidgetItem("Нет музыкальных файлов")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor(150, 150, 150))
                self.track_list_widget.addItem(item)
                
        except Exception as e:
            item = QListWidgetItem(f"Ошибка: {str(e)}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor(180, 80, 80))
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
                self.progress_timer.stop()
            else:
                # Если на паузе - возобновляем
                self.player.play()
                btn.setIcon(self.pause_icon)
                self.progress_timer.start()
        else:
            # Иначе начинаем воспроизведение нового трека
            self.player.play_track_by_path(file_path)
            self.progress_timer.start()
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
    
    def _update_progress(self):
        """Обновляет прогресс для текущего трека"""
        current_path = self.player.get_current_track_path()
        if not current_path or current_path not in self.track_widgets:
            return
        
        duration = self.player.get_duration()
        position = self.player.get_position()
        
        if duration > 0:
            progress = position / duration
            widget = self.track_widgets[current_path]
            widget.set_progress(progress)
    
    def _on_position_changed(self, position):
        """Обработчик изменения позиции"""
        if self.progress_timer.isActive():
            self._update_progress()
    
    def _on_duration_changed(self, duration):
        """Обработчик изменения длительности"""
        current_path = self.player.get_current_track_path()
        if current_path and current_path in self.track_widgets:
            self.track_widgets[current_path].set_duration(duration)
        self._update_progress()
    
    def _on_track_changed(self, path):
        """Обработчик смены трека."""
        # Сбрасываем прогресс и длительность у всех треков
        for widget in self.track_widgets.values():
            widget.set_progress(0.0)
            widget.set_playing_state(False)
            widget.set_duration(0)
        
        # Устанавливаем состояние для текущего трека
        if path in self.track_widgets:
            widget = self.track_widgets[path]
            widget.set_playing_state(True)
            widget.set_progress(0.0)
            widget.set_duration(self.player.get_duration())
        
        self._update_all_buttons()
        self.progress_timer.start()
        
        self.notifications.show_info(
            "Сейчас играет",
            os.path.basename(path),
            3000
        )
    
    def _on_player_state_changed(self, state):
        """Обработчик изменения состояния плеера."""
        current_path = self.player.get_current_track_path()
        
        if state == "playing":
            self._update_all_buttons()
            if current_path in self.track_widgets:
                self.track_widgets[current_path].set_playing_state(True)
            self.progress_timer.start()
            
        elif state == "paused":
            self._update_all_buttons()
            self.progress_timer.stop()
            
        elif state == "stopped":
            # Сбрасываем все кнопки
            for btn in self.play_buttons.values():
                btn.setIcon(self.play_icon)
            for widget in self.track_widgets.values():
                widget.set_progress(0.0)
                widget.set_playing_state(False)
                widget.set_duration(0)
            self.progress_timer.stop()
    
    def _on_player_error(self, error_message):
        """Обработчик ошибок плеера."""
        self.notifications.show_error("Ошибка воспроизведения", error_message, 5000)
    
    def _on_track_finished(self):
        """Обработчик окончания трека - автоматически переключает на следующий"""
        playlist = self.player.get_playlist()
        if playlist and len(playlist) > 0:
            self.player.next_track()
            self._update_all_buttons()
    
    def seek_to_position(self, track_path, position_ms):
        """Перематывает трек на указанную позицию"""
        # Проверяем, что это текущий трек
        if self.player.get_current_track_path() == track_path:
            self.player.set_position(position_ms)
            # Обновляем прогресс сразу
            duration = self.player.get_duration()
            if duration > 0:
                progress = position_ms / duration
                if track_path in self.track_widgets:
                    self.track_widgets[track_path].set_progress(progress)