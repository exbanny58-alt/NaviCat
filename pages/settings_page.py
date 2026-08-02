import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QFileDialog, QFrame,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from notifications import get_notification_manager
from dialog import CustomDialog


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: transparent;")
        self.notifications = get_notification_manager()
        
        # Путь к конфиг-файлу
        self.config_dir = "config"
        self.config_file = os.path.join(self.config_dir, "settings.json")
        
        # Создаём папку config, если её нет
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # Основной layout - выравнивание по левому краю
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Создаём контейнер с фиксированной шириной
        container = QFrame()
        container.setFixedWidth(700)
        container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Заголовок
        title = QLabel("Настройки")
        title.setStyleSheet("color: #cccccc; font-size: 24px; font-weight: bold;")
        container_layout.addWidget(title)

        # Подсказка
        hint = QLabel("Заполните необходимые пути (можно не все)")
        hint.setStyleSheet("color: #888888; font-size: 12px;")
        container_layout.addWidget(hint)

        # Разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #333333; max-height: 1px;")
        container_layout.addWidget(sep)

        # Форма для путей
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.paths = {}  # словарь {метка: QLineEdit}

        # Описание полей: (метка, режим выбора)
        items = [
            ("Путь до сервера", "directory"),
            ("Путь до exe файла игры", "file"),
            ("Путь до папки Workshop", "directory"),
            ("Путь до папки своих модов", "directory"),
            ("Путь до папки с музыкой", "directory"),
        ]

        for label_text, mode in items:
            # Каждая строка в отдельном фрейме для лучшего контроля
            row_frame = QFrame()
            row_frame.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: none;
                }
            """)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(12)
            
            # Метка с фиксированной шириной - выравнивание по левому краю
            label = QLabel(label_text)
            label.setFixedWidth(200)
            label.setStyleSheet("""
                color: #aaaaaa; 
                font-size: 14px;
                background-color: transparent;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            row_layout.addWidget(label)

            # Поле ввода - растягивается, но ограничено максимальной шириной
            line_edit = QLineEdit()
            line_edit.setFixedHeight(36)
            line_edit.setPlaceholderText("Введите путь или выберите через 'Обзор'")
            line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #cccccc;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #888888;
                    background-color: #333333;
                }
                QLineEdit::placeholder {
                    color: #666666;
                }
            """)
            line_edit.setSizePolicy(
                QSizePolicy.Policy.Expanding, 
                QSizePolicy.Policy.Fixed
            )
            row_layout.addWidget(line_edit, 1)

            # Кнопка "Обзор" с фиксированной шириной
            browse_btn = QPushButton("Обзор")
            browse_btn.setFixedSize(100, 36)
            browse_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #cccccc;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 13px;
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
            browse_btn.clicked.connect(
                lambda checked, le=line_edit, m=mode: self.browse(le, m)
            )
            row_layout.addWidget(browse_btn)

            container_layout.addWidget(row_frame)
            self.paths[label_text] = line_edit

        container_layout.addLayout(form_layout)

        # Разделитель перед кнопками
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #333333; max-height: 1px;")
        container_layout.addWidget(sep2)

        # Кнопки (Сохранить и Очистить) в одной строке
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Выравнивание по левому краю

        # Кнопка сохранить (теперь первая)
        save_btn = QPushButton("Сохранить")
        save_btn.setFixedSize(160, 42)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
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
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        # Кнопка очистить (теперь вторая)
        clear_btn = QPushButton("Очистить всё")
        clear_btn.setFixedSize(160, 42)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #cccccc;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
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
        clear_btn.clicked.connect(self.clear_settings)
        buttons_layout.addWidget(clear_btn)

        container_layout.addLayout(buttons_layout)
        
        # Добавляем контейнер в основной layout с отступом сверху
        main_layout.addWidget(container)

        # Загружаем сохранённые настройки при инициализации
        self.load_settings()

    def browse(self, line_edit, mode):
        """Открывает диалог выбора папки или файла."""
        try:
            if mode == "directory":
                dir_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
                if dir_path:
                    # Нормализуем путь (заменяем обратные слеши на прямые)
                    dir_path = dir_path.replace('\\', '/')
                    line_edit.setText(dir_path)
                    self.notifications.show_success(
                        "Папка выбрана", 
                        os.path.basename(dir_path), 
                        2000
                    )
            elif mode == "file":
                file_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Выберите файл",
                    filter="Executable files (*.exe);;All files (*.*)"
                )
                if file_path:
                    file_path = file_path.replace('\\', '/')
                    line_edit.setText(file_path)
                    self.notifications.show_success(
                        "Файл выбран", 
                        os.path.basename(file_path), 
                        2000
                    )
        except Exception as e:
            self.notifications.show_error("Ошибка", str(e), 5000)

    def load_settings(self):
        """Загружает настройки из JSON-файла и заполняет поля."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            for label, le in self.paths.items():
                if label in settings:
                    le.setText(settings[label])
                else:
                    le.setText("")
        except Exception as e:
            self.notifications.show_error("Ошибка загрузки", str(e), 5000)

    def save_settings(self):
        """Сохраняет настройки в JSON-файл (можно не все поля)."""
        settings = {}
        filled_count = 0
        
        for label, le in self.paths.items():
            text = le.text().strip()
            # Нормализуем путь
            if text:
                text = text.replace('\\', '/')
                filled_count += 1
            settings[label] = text
        
        try:
            # Сохраняем в JSON
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            # Показываем уведомление
            if filled_count == 0:
                self.notifications.show_info(
                    "Настройки сохранены",
                    "Ни один путь не был указан",
                    3000
                )
            else:
                self.notifications.show_success(
                    "Настройки сохранены",
                    f"Сохранено {filled_count} из {len(settings)} путей",
                    3000
                )
        except Exception as e:
            self.notifications.show_error("Ошибка сохранения", str(e), 5000)

    def clear_settings(self):
        """Очищает все поля и удаляет файл конфига с подтверждением."""
        confirmed = CustomDialog.question(
            self,
            "Очистка настроек",
            "Вы действительно хотите очистить все пути и удалить конфигурацию?\n\n"
            "Это действие нельзя отменить.",
            default=False
        )
        
        if not confirmed:
            return
        
        try:
            # Очищаем все поля ввода
            for le in self.paths.values():
                le.clear()
            
            # Удаляем файл конфига, если он существует
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                self.notifications.show_success(
                    "Настройки очищены",
                    "Файл конфигурации удалён",
                    3000
                )
            else:
                self.notifications.show_info(
                    "Настройки очищены",
                    "Все поля очищены (конфиг уже отсутствовал)",
                    3000
                )
        except Exception as e:
            self.notifications.show_error("Ошибка очистки", str(e), 5000)