import sys
from PyQt6.QtWidgets import QApplication, QToolTip
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from main_window import MatteBlackWindow
from notifications import get_notification_manager


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: transparent; }")
    QToolTip.setFont(QFont("Segoe UI", 9))
    
    # Создаём окно
    window = MatteBlackWindow()
    window.setWindowTitle("DayZ Manager")
    window.show()
    
    # Инициализируем уведомления
    notifications = get_notification_manager()
    
    # Показываем приветствие с небольшой задержкой
    QTimer.singleShot(500, lambda: notifications.show_success(
        "Приложение запущено",
        "DayZ Manager готов к работе",
        3000
    ))
    
    # Сохраняем геометрию при закрытии приложения
    app.aboutToQuit.connect(window.save_window_geometry)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()