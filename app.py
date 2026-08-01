from flask import Flask
from routes import register_routes
import logging
import sys
from server_manager import DayZServer
from game_manager import DayZGame
import os
from pid_manager import load_pid, is_process_running, clear_pid  # Добавляем

app = Flask(__name__)

# Глобальные экземпляры
server_instance = None
game_instance = None

def get_server():
    """Возвращает экземпляр сервера, создавая его при необходимости"""
    global server_instance
    if server_instance is None:
        from settings_manager import load_settings
        settings = load_settings()
        server_exe = settings.get('server_exe', '')
        if server_exe and server_exe.strip():
            server_dir = os.path.dirname(server_exe)
            server_instance = DayZServer(server_dir)
        else:
            server_instance = DayZServer('')
    return server_instance

def get_game():
    """Возвращает экземпляр игры, создавая его при необходимости"""
    global game_instance
    if game_instance is None:
        from settings_manager import load_settings
        settings = load_settings()
        game_exe = settings.get('game_exe', '')
        if game_exe and game_exe.strip():
            game_dir = os.path.dirname(game_exe)
            game_instance = DayZGame(game_dir)
        else:
            game_instance = DayZGame('')
    return game_instance

# Регистрируем все маршруты из routes.py
register_routes(app)

if __name__ == '__main__':
    # Проверяем наличие старых PID файлов при старте
    # Если процесс не запущен - очищаем
    for pid_type in ['server', 'game']:
        pid = load_pid(pid_type)
        if pid and not is_process_running(pid):
            clear_pid(pid_type)
            print(f'🧹 Очищен неактивный PID {pid_type}: {pid}')
    
    if '--gui' in sys.argv:
        # Запуск в GUI режиме
        from flaskwebgui import FlaskUI
        
        flaskwebgui_logger = logging.getLogger('flaskwebgui')
        flaskwebgui_logger.setLevel(logging.ERROR)
        
        # Инициализируем сервер до запуска GUI
        get_server()
        
        FlaskUI(
            app=app,
            server="flask",
            width=1300,
            height=850,
            fullscreen=False
        ).run()
    else:
        # Запуск в браузере (по умолчанию)
        get_server()
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True
        )