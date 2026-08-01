import os
import json
from PyQt6.QtCore import QObject, QUrl, QTimer, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from notifications import get_notification_manager


class MusicPlayer(QObject):
    """Музыкальный проигрыватель без визуального интерфейса."""
    
    # Сигналы для взаимодействия с UI
    track_changed = pyqtSignal(str)  # Сигнал при смене трека (путь к файлу)
    position_changed = pyqtSignal(int)  # Сигнал при изменении позиции (в мс)
    duration_changed = pyqtSignal(int)  # Сигнал при изменении длительности (в мс)
    state_changed = pyqtSignal(str)  # Сигнал при изменении состояния (playing/paused/stopped)
    error_occurred = pyqtSignal(str)  # Сигнал при ошибке
    track_finished = pyqtSignal()  # Сигнал при окончании трека
    
    def __init__(self):
        super().__init__()
        
        # Конфиг
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "settings.json")
        
        # Плеер и аудио-выход
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Состояние
        self.current_track = None
        self.current_track_index = -1
        self.playlist = []
        self.is_playing = False
        self.volume = 70  # от 0 до 100
        self.saved_position = 0  # Сохраняем позицию для паузы
        self.is_paused_manually = False  # Флаг ручной паузы
        
        # Таймер для обновления позиции
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)  # Обновление каждую секунду
        self.update_timer.timeout.connect(self._update_position)
        
        # Подключение сигналов
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_error)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        
        # Установка громкости
        self.set_volume(self.volume)
        
        # Загрузка плейлиста
        self._load_music_path()
    
    def _load_music_path(self):
        """Загружает путь к музыке из конфига."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    music_path = settings.get("Путь до папки с музыкой", "")
                    if music_path:
                        self.scan_tracks(music_path)
            except Exception as e:
                self.error_occurred.emit(f"Ошибка загрузки конфига: {str(e)}")
    
    def scan_tracks(self, music_path):
        """Сканирует папку и создаёт плейлист."""
        if not music_path or not os.path.exists(music_path):
            self.error_occurred.emit("Папка с музыкой не существует")
            return
        
        try:
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
            self.playlist.clear()
            
            for root, dirs, files in os.walk(music_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in audio_extensions:
                        full_path = os.path.join(root, file)
                        self.playlist.append(full_path)
            
            if not self.playlist:
                self.error_occurred.emit("В папке не найдено музыкальных файлов")
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка сканирования: {str(e)}")
    
    def play_track(self, index):
        """Воспроизводит трек по индексу в плейлисте."""
        if 0 <= index < len(self.playlist):
            self.current_track_index = index
            self.current_track = self.playlist[index]
            self.saved_position = 0  # Сбрасываем сохранённую позицию при смене трека
            self.is_paused_manually = False
            
            url = QUrl.fromLocalFile(self.current_track)
            self.player.setSource(url)
            self.player.play()
            self.is_playing = True
            
            self.track_changed.emit(self.current_track)
        else:
            self.error_occurred.emit("Трек не найден в плейлисте")
    
    def play_track_by_path(self, path):
        """Воспроизводит трек по пути к файлу."""
        if path in self.playlist:
            index = self.playlist.index(path)
            self.play_track(index)
        else:
            self.error_occurred.emit("Трек не найден в плейлисте")
    
    def play(self):
        """Воспроизводит текущий трек с сохранённой позиции."""
        if self.current_track:
            self.is_paused_manually = False
            # Если есть сохранённая позиция, восстанавливаем её
            if self.saved_position > 0:
                self.player.setPosition(self.saved_position)
            self.player.play()
            self.is_playing = True
    
    def pause(self):
        """Приостанавливает воспроизведение и сохраняет позицию."""
        if self.player.isPlaying():
            # Сохраняем текущую позицию перед паузой
            self.saved_position = self.player.position()
            self.is_paused_manually = True
            self.player.pause()
            self.is_playing = False
    
    def stop(self):
        """Останавливает воспроизведение."""
        self.is_paused_manually = False
        self.player.stop()
        self.is_playing = False
        self.saved_position = 0
        self.update_timer.stop()
        self.position_changed.emit(0)
    
    def next_track(self):
        """Переключает на следующий трек."""
        if not self.playlist:
            return
        
        next_index = (self.current_track_index + 1) % len(self.playlist)
        self.play_track(next_index)
    
    def previous_track(self):
        """Переключает на предыдущий трек."""
        if not self.playlist:
            return
        
        prev_index = (self.current_track_index - 1) % len(self.playlist)
        self.play_track(prev_index)
    
    def set_volume(self, volume):
        """Устанавливает громкость (0-100)."""
        self.volume = max(0, min(100, volume))
        self.audio_output.setVolume(self.volume / 100.0)
    
    def get_volume(self):
        """Возвращает текущую громкость."""
        return self.volume
    
    def set_position(self, position_ms):
        """Устанавливает позицию воспроизведения (в мс)."""
        if self.player.isSeekable():
            self.player.setPosition(position_ms)
            # Обновляем сохранённую позицию
            if not self.is_playing:
                self.saved_position = position_ms
    
    def get_position(self):
        """Возвращает текущую позицию (в мс)."""
        return self.player.position()
    
    def get_duration(self):
        """Возвращает длительность текущего трека (в мс)."""
        return self.player.duration()
    
    def get_current_track_name(self):
        """Возвращает имя текущего трека."""
        if self.current_track:
            return os.path.basename(self.current_track)
        return ""
    
    def get_current_track_path(self):
        """Возвращает путь к текущему треку."""
        return self.current_track
    
    def get_playlist(self):
        """Возвращает весь плейлист."""
        return self.playlist.copy()
    
    def get_playlist_names(self):
        """Возвращает имена всех треков в плейлисте."""
        return [os.path.basename(path) for path in self.playlist]
    
    def get_track_index(self):
        """Возвращает индекс текущего трека."""
        return self.current_track_index
    
    def clear_playlist(self):
        """Очищает плейлист и останавливает воспроизведение."""
        self.stop()
        self.playlist.clear()
        self.current_track = None
        self.current_track_index = -1
    
    def is_playing(self):
        """Возвращает True если воспроизведение активно."""
        return self.is_playing
    
    def is_paused(self):
        """Возвращает True если воспроизведение приостановлено."""
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState
    
    def is_stopped(self):
        """Возвращает True если воспроизведение остановлено."""
        return self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState
    
    def _update_position(self):
        """Обновляет позицию воспроизведения."""
        if self.is_playing:
            self.position_changed.emit(self.player.position())
    
    def _on_position_changed(self, position):
        """Обработчик изменения позиции."""
        if not self.update_timer.isActive() and self.is_playing:
            self.update_timer.start()
        self.position_changed.emit(position)
    
    def _on_duration_changed(self, duration):
        """Обработчик изменения длительности."""
        self.duration_changed.emit(duration)
    
    def _on_media_status_changed(self, status):
        """Обработчик изменения статуса медиа."""
        # Если медиа загружено и есть сохранённая позиция
        if status == QMediaPlayer.MediaStatus.LoadedMedia and self.saved_position > 0:
            # Устанавливаем позицию после загрузки
            self.player.setPosition(self.saved_position)
        
        # Если трек закончился
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.track_finished.emit()
            # Автоматически переключаем на следующий
            self.next_track()
    
    def _on_state_changed(self, state):
        """Обработчик изменения состояния воспроизведения."""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.is_playing = True
            self.update_timer.start()
            self.state_changed.emit("playing")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.is_playing = False
            # Сохраняем позицию при паузе, если это не ручная пауза
            if not self.is_paused_manually:
                self.saved_position = self.player.position()
            self.state_changed.emit("paused")
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.is_playing = False
            self.update_timer.stop()
            if not self.is_paused_manually:
                self.saved_position = 0
            self.state_changed.emit("stopped")
    
    def _on_error(self, error):
        """Обработчик ошибок плеера."""
        error_messages = {
            QMediaPlayer.Error.NoError: "Нет ошибки",
            QMediaPlayer.Error.ResourceError: "Ошибка ресурса",
            QMediaPlayer.Error.FormatError: "Ошибка формата",
            QMediaPlayer.Error.NetworkError: "Ошибка сети",
            QMediaPlayer.Error.AccessDeniedError: "Доступ запрещён",
            QMediaPlayer.Error.ServiceMissingError: "Отсутствует сервис"
        }
        message = error_messages.get(error, f"Неизвестная ошибка: {error}")
        self.error_occurred.emit(message)