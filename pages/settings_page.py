import os
import json
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from notifications import get_notification_manager
from dialog import CustomDialog  # новый импорт


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
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("Настройки")
        title.setStyleSheet("color: #cccccc; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Подсказка
        hint = QLabel("Заполните необходимые пути (можно не все)")
        hint.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(hint)

        # Форма для путей
        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)

        self.paths = {}  # словарь {метка: QLineEdit}

        # Описание полей: (метка, режим выбора)
        items = [
            ("Путь до сервера", "directory"),
            ("Путь до exe файла игры", "file"),
            ("Путь до папки Workshop", "directory"),
            ("Путь до папки своих модов", "directory"),
        ]

        for label_text, mode in items:
            row = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(200)
            label.setStyleSheet("color: #aaaaaa; font-size: 14px;")
            row.addWidget(label)

            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Введите путь или выберите через 'Обзор'")
            line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #cccccc;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 13px;
                }
                QLineEdit:focus {
                    border: 1px solid #888888;
                }
                QLineEdit::placeholder {
                    color: #666666;
                }
            """)
            row.addWidget(line_edit)

            browse_btn = QPushButton("Обзор")
            browse_btn.setFixedWidth(80)
            browse_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: #cccccc;
                    border: 1px solid #444444;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                }
            """)
            browse_btn.clicked.connect(
                lambda checked, le=line_edit, m=mode: self.browse(le, m)
            )
            row.addWidget(browse_btn)

            form_layout.addLayout(row)
            self.paths[label_text] = line_edit

        layout.addLayout(form_layout)

        # Кнопки (Сохранить и Очистить) в одной строке
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        # Кнопка очистить
        clear_btn = QPushButton("Очистить настройки")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a1a1a;
                color: #ff6b6b;
                border: 1px solid #5a2a2a;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a2a2a;
                color: #ff8a8a;
                border-color: #7a3a3a;
            }
            QPushButton:pressed {
                background-color: #2a0a0a;
                border-color: #4a1a1a;
            }
        """)
        clear_btn.clicked.connect(self.clear_settings)
        buttons_layout.addWidget(clear_btn)

        # Кнопка сохранить
        save_btn = QPushButton("Сохранить настройки")
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
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        # Загружаем сохранённые настройки при инициализации
        self.load_settings()

    def browse(self, line_edit, mode):
        """Открывает диалог выбора папки или файла."""
        try:
            if mode == "directory":
                dir_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
                if dir_path:
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
            if text:
                filled_count += 1
            settings[label] = text
        
        try:
            # Сохраняем в JSON
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            
            print("Настройки сохранены:")
            for k, v in settings.items():
                print(f"{k}: {v}")
            
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
        # Используем кастомный диалог вместо QMessageBox
        confirmed = CustomDialog.question(
            self,
            "Очистка настроек",
            "Вы действительно хотите очистить все пути и удалить конфигурацию?\n\n"
            "Это действие нельзя отменить.",
            default=False  # По умолчанию "Нет"
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