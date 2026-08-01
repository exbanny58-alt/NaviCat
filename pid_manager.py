# pid_manager.py
import os
import json
import psutil

PID_DIR = os.path.join(os.path.dirname(__file__), 'pids')

def ensure_pid_dir():
    """Создаёт папку для PID файлов если её нет"""
    if not os.path.exists(PID_DIR):
        os.makedirs(PID_DIR, exist_ok=True)

def save_pid(pid_type, pid):
    """Сохраняет PID в файл"""
    ensure_pid_dir()
    pid_file = os.path.join(PID_DIR, f'{pid_type}.pid')
    try:
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения PID {pid_type}: {e}')
        return False

def load_pid(pid_type):
    """Загружает PID из файла"""
    pid_file = os.path.join(PID_DIR, f'{pid_type}.pid')
    if not os.path.exists(pid_file):
        return None
    try:
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    except Exception as e:
        print(f'⚠️ Ошибка загрузки PID {pid_type}: {e}')
        return None

def clear_pid(pid_type):
    """Удаляет PID файл"""
    pid_file = os.path.join(PID_DIR, f'{pid_type}.pid')
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
        return True
    except Exception as e:
        print(f'⚠️ Ошибка удаления PID {pid_type}: {e}')
        return False

def is_process_running(pid):
    """Проверяет, запущен ли процесс с данным PID"""
    if pid is None:
        return False
    try:
        return psutil.pid_exists(pid)
    except:
        return False

def get_process_info(pid):
    """Получает информацию о процессе"""
    if pid is None:
        return None
    try:
        p = psutil.Process(pid)
        return {
            'pid': pid,
            'name': p.name(),
            'status': p.status(),
            'memory_mb': p.memory_info().rss / 1024 / 1024,
            'cpu_percent': p.cpu_percent(interval=0.1)
        }
    except psutil.NoSuchProcess:
        return None
    except Exception as e:
        print(f'⚠️ Ошибка получения информации о процессе {pid}: {e}')
        return None

def restore_process(process_obj, pid_type):
    """Восстанавливает процесс из PID файла"""
    pid = load_pid(pid_type)
    if pid is None:
        return False
    
    if not is_process_running(pid):
        print(f'⚠️ Процесс {pid_type} (PID: {pid}) не найден, очищаем PID')
        clear_pid(pid_type)
        return False
    
    # Присваиваем PID процессу
    try:
        process_obj._pid = pid
        process_obj._using_pid = True
        process_obj.process = None
        print(f'✅ Восстановлен {pid_type} с PID: {pid}')
        return True
    except Exception as e:
        print(f'❌ Ошибка восстановления {pid_type}: {e}')
        return False