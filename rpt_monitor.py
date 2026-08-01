# rpt_monitor.py
import os
import time
import glob
import threading
import queue
import re
from datetime import datetime

class RPTMonitor:
    def __init__(self, profiles_dir):
        self.profiles_dir = profiles_dir
        self.log_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.current_rpt = None
        self.last_position = 0
        self.server_ready = False
        
        # ===== Для отслеживания players.db =====
        self.storage_path = None
        self.last_db_mtime = None
        self.db_monitor_thread = None
        self.db_monitor_running = False
        self.db_monitor_started = False
        self.initial_db_mtime = None
        
        # ===== Простой счётчик онлайн =====
        self.online_count = 0
        
        # Пытаемся найти папку storage_1
        self._find_storage_path()
        
    def _find_storage_path(self):
        """Ищет папку storage_1 относительно profiles_dir."""
        if not self.profiles_dir:
            return
        
        possible_paths = [
            os.path.join(os.path.dirname(self.profiles_dir), 'mpmissions', 'dayzOffline.chernarusplus', 'storage_1'),
            os.path.join(os.path.dirname(self.profiles_dir), 'mpmissions', 'dayzOffline.chernarusplus', 'storage_2'),
            os.path.join(os.path.dirname(self.profiles_dir), 'mpmissions', 'dayz.chernarusplus', 'storage_1'),
            os.path.join(os.path.dirname(self.profiles_dir), 'mpmissions', 'dayz.chernarusplus', 'storage_2'),
            os.path.join(self.profiles_dir, '..', 'mpmissions', 'dayzOffline.chernarusplus', 'storage_1'),
            os.path.join(self.profiles_dir, '..', 'mpmissions', 'dayzOffline.chernarusplus', 'storage_2'),
        ]
        
        for path in possible_paths:
            normalized = os.path.normpath(path)
            if os.path.exists(normalized) and os.path.isdir(normalized):
                self.storage_path = normalized
                print(f'📁 Найдена папка storage: {self.storage_path}')
                return
        
        base_dir = os.path.dirname(self.profiles_dir)
        for root, dirs, files in os.walk(base_dir):
            if 'storage_1' in dirs:
                candidate = os.path.join(root, 'storage_1')
                self.storage_path = candidate
                print(f'📁 Найдена папка storage (поиск): {self.storage_path}')
                return
            if 'storage_2' in dirs:
                candidate = os.path.join(root, 'storage_2')
                self.storage_path = candidate
                print(f'📁 Найдена папка storage (поиск): {self.storage_path}')
                return
        
        print('⚠️ Папка storage_1 не найдена!')
    
    def _check_db_file(self):
        """Проверяет, изменился ли файл players.db."""
        if not self.storage_path:
            return None
        
        db_path = os.path.join(self.storage_path, 'players.db')
        if not os.path.exists(db_path):
            return None
        
        try:
            mtime = os.path.getmtime(db_path)
            
            if not self.db_monitor_started:
                self.initial_db_mtime = mtime
                self.last_db_mtime = mtime
                print(f'📁 Начальное состояние players.db: {datetime.fromtimestamp(mtime).strftime("%H:%M:%S")}')
                return None
            
            if self.last_db_mtime is None:
                self.last_db_mtime = mtime
                return None
            
            if mtime != self.last_db_mtime:
                self.last_db_mtime = mtime
                return datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
                
        except Exception as e:
            print(f'⚠️ Ошибка проверки players.db: {e}')
        
        return None
    
    def _db_monitor_loop(self):
        """Отдельный поток для мониторинга players.db."""
        self.db_monitor_running = True
        print('📁 Запущен мониторинг players.db (ожидание первого сохранения...)')
        
        while self.db_monitor_running and self.running:
            if self.db_monitor_started:
                break
            time.sleep(0.5)
        
        if self.storage_path and self.db_monitor_started:
            db_path = os.path.join(self.storage_path, 'players.db')
            if os.path.exists(db_path):
                try:
                    self.last_db_mtime = os.path.getmtime(db_path)
                    print(f'📁 Мониторинг players.db активен (последнее сохранение: {datetime.fromtimestamp(self.last_db_mtime).strftime("%H:%M:%S")})')
                except:
                    pass
        
        while self.db_monitor_running and self.running and self.db_monitor_started:
            try:
                save_time = self._check_db_file()
                if save_time:
                    self.log_queue.put({
                        'type': 'save_db',
                        'message': f'💾 [ СОХРАНЕНИЕ МИРА ] {save_time} ---> players.db ОБНОВЛЁН!',
                        'raw': f'players.db updated at {save_time}',
                        'timestamp': datetime.now().isoformat(),
                        'server_ready': True
                    })
                    
                    self.log_queue.put({
                        'type': 'system',
                        'message': '═' * 25 + ' [ СЕРВЕР СОХРАНИЛ МИР ] ' + '═' * 25,
                        'raw': '',
                        'timestamp': datetime.now().isoformat(),
                        'server_ready': True
                    })
                
                time.sleep(2)
                
            except Exception as e:
                print(f'⚠️ Ошибка в db_monitor_loop: {e}')
                time.sleep(5)
        
        self.db_monitor_running = False
        print('📁 Мониторинг players.db остановлен')
    
    def start_db_monitor(self):
        """Запускает мониторинг players.db в отдельном потоке (но не активирует его)."""
        if not self.storage_path:
            print('⚠️ Невозможно запустить мониторинг players.db: storage_path не найден')
            return False
        
        if self.db_monitor_thread and self.db_monitor_thread.is_alive():
            return False
        
        self.db_monitor_started = False
        self.db_monitor_thread = threading.Thread(target=self._db_monitor_loop, daemon=True)
        self.db_monitor_thread.start()
        return True
    
    def activate_db_monitor(self):
        """Активирует мониторинг players.db (начинает отслеживать изменения)."""
        if not self.db_monitor_thread or not self.db_monitor_thread.is_alive():
            return False
        
        self.db_monitor_started = True
        print('📁 Мониторинг players.db АКТИВИРОВАН!')
        return True
    
    def stop_db_monitor(self):
        """Останавливает мониторинг players.db."""
        self.db_monitor_running = False
        if self.db_monitor_thread:
            self.db_monitor_thread.join(timeout=2)
        return True
    
    def get_latest_rpt(self):
        """Находит самый новый RPT-файл."""
        if not os.path.exists(self.profiles_dir):
            return None
        rpt_pattern = os.path.join(self.profiles_dir, "*.RPT")
        files = glob.glob(rpt_pattern)
        return max(files, key=os.path.getmtime) if files else None
    
    def _parse_log_line(self, line):
        """
        Анализирует строку лога.
        Возвращает словарь с полями: type, message, raw, timestamp
        Если строка не подходит ни под один фильтр - возвращает None
        """
        stripped = line.strip()
        
        if not stripped:
            return None
        
        msg_type = None
        message = None
        raw_time = stripped[:8] if len(stripped) > 8 else ""
        
        # ============================================
        # ОСТАЛЬНЫЕ СОБЫТИЯ
        # ============================================
        
        if "Создан выделенный сервер" in stripped:
            msg_type = 'start'
            message = f"🚀 Создан выделенный сервер"
            
        elif "SUCCESS: SteamGameServer_Init" in stripped:
            msg_type = 'steam'
            message = f"🔵 Steam авторизация успешна"
            
        elif "Роли назначены" in stripped:
            msg_type = 'info'
            message = f"📋 Роли назначены"
            
        elif "Чтение задания" in stripped:
            msg_type = 'mission'
            message = f"📁 Чтение задания..."
            
        elif "[CE][Hive] :: Loading core data" in stripped:
            msg_type = 'economy'
            message = f"⚙️ Загрузка основных данных экономики..."
            
        elif "[CE][Hive] :: Loading map data" in stripped:
            msg_type = 'economy'
            message = f"🗺️ Загрузка карты..."
            
        elif "[CE][Hive] :: Storage load took" in stripped:
            msg_type = 'economy'
            match = re.search(r'took:([\d.]+)\s+seconds', stripped)
            if match:
                load_time = match.group(1)
                message = f"💾 Загрузка хранилища: {load_time} сек"
            else:
                message = f"💾 Загрузка хранилища завершена"
            
        elif "[CE][Hive] :: Initializing" in stripped:
            msg_type = 'economy'
            message = f"⚙️ Инициализация экономики..."
            
        elif "[CE][Hive] :: Initializing spawners" in stripped:
            msg_type = 'economy'
            message = f"🔄 Инициализация спавнеров..."
            
        elif "Initializing of spawners done" in stripped:
            msg_type = 'economy'
            message = f"✅ Инициализация спавнеров завершена"
            
        elif "Player connect enabled" in stripped:
            msg_type = 'network'
            message = f"🌐 Порты открыты, ожидание игроков"
            
        elif "[IdleMode] Entering IN - save processed" in stripped:
            msg_type = 'save'
            log_time = raw_time if raw_time else "Время неизвестно"
            message = f"\n💾 [ СОХРАНЕНИЕ МИРА ] {log_time} ---> МИР УСПЕШНО ЗАПИСАН НА ДИСК! Server IDLE."
            self.server_ready = True
            self.activate_db_monitor()
            
        elif "[CE][Hive] :: Init sequence finished" in stripped:
            msg_type = 'economy'
            message = f"✅ Последовательность инициализации завершена"
            
        elif "Hostname of server" in stripped:
            msg_type = 'info'
            match = re.search(r'"([^"]+)"', stripped)
            if match:
                server_name = match.group(1)
                message = f"🏷️ Имя сервера: {server_name}"
            else:
                message = f"🏷️ Имя сервера установлено"
            
        elif "[CE][LootRespawner]" in stripped and "Initially (re)spawned" in stripped:
            msg_type = 'economy'
            match = re.search(r'Initially \(re\)spawned:(\d+)', stripped)
            if match:
                count = match.group(1)
                message = f"📦 Загружено предметов: {count}"
            else:
                message = f"📦 Загрузка предметов завершена"
            
        # ===== СЧЁТЧИК ОНЛАЙН =====
        elif "Подключился игрок" in stripped or "Player" in stripped and "is connected" in stripped:
            # Просто увеличиваем счётчик
            self.online_count += 1
            # Не выводим сообщение
            
        elif "[Disconnect]: Client" in stripped or "[Disconnect]: Player destroy" in stripped:
            # Уменьшаем счётчик
            if self.online_count > 0:
                self.online_count -= 1
            # Не выводим сообщение
            
        if msg_type is None:
            return None
        
        return {
            'type': msg_type,
            'message': message,
            'raw': stripped,
            'timestamp': datetime.now().isoformat(),
            'server_ready': self.server_ready
        }
    
    def _monitor_loop(self):
        """Основной цикл мониторинга RPT файла."""
        self.running = True
        self.current_rpt = self.get_latest_rpt()
        
        self.log_queue.put({
            'type': 'system',
            'message': '📟 Система мониторинга DayZ запущена',
            'raw': '',
            'timestamp': datetime.now().isoformat(),
            'server_ready': False
        })
        
        self.start_db_monitor()
        
        if not self.current_rpt:
            self.log_queue.put({
                'type': 'system',
                'message': '⏳ Ожидание создания лог-файла сервера...',
                'raw': '',
                'timestamp': datetime.now().isoformat(),
                'server_ready': False
            })
            while not self.current_rpt and self.running:
                time.sleep(1)
                self.current_rpt = self.get_latest_rpt()
            if not self.running:
                return
        
        self.log_queue.put({
            'type': 'system',
            'message': f'📄 Подключено к логу: {os.path.basename(self.current_rpt)}',
            'raw': '',
            'timestamp': datetime.now().isoformat(),
            'server_ready': False
        })
        self.log_queue.put({
            'type': 'system',
            'message': '─' * 50,
            'raw': '',
            'timestamp': datetime.now().isoformat(),
            'server_ready': False
        })
        
        try:
            f = open(self.current_rpt, "r", encoding="utf-8", errors="ignore")
            f.seek(0, os.SEEK_END)
        except Exception as e:
            self.log_queue.put({
                'type': 'error',
                'message': f'❌ Ошибка открытия RPT файла: {str(e)}',
                'raw': '',
                'timestamp': datetime.now().isoformat(),
                'server_ready': False
            })
            self.running = False
            return
        
        while self.running:
            try:
                latest_rpt = self.get_latest_rpt()
                if latest_rpt and latest_rpt != self.current_rpt:
                    self.log_queue.put({
                        'type': 'system',
                        'message': f'\n🔄 Обнаружен перезапуск сервера! Переключаюсь на: {os.path.basename(latest_rpt)}',
                        'raw': '',
                        'timestamp': datetime.now().isoformat(),
                        'server_ready': False
                    })
                    self.log_queue.put({
                        'type': 'system',
                        'message': '─' * 50,
                        'raw': '',
                        'timestamp': datetime.now().isoformat(),
                        'server_ready': False
                    })
                    self.current_rpt = latest_rpt
                    self.server_ready = False
                    self.last_db_mtime = None
                    self.db_monitor_started = False
                    self.online_count = 0  # Сбрасываем счётчик при перезапуске
                    f.close()
                    f = open(self.current_rpt, "r", encoding="utf-8", errors="ignore")
                    f.seek(0, os.SEEK_END)
                
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                parsed = self._parse_log_line(line)
                if parsed:
                    if parsed['type'] == 'save':
                        parsed['message'] = parsed['message'] + "\n" + "═" * 25 + " [ СЕРВЕР ГОТОВ ] " + "═" * 25
                    self.log_queue.put(parsed)
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.log_queue.put({
                    'type': 'error',
                    'message': f'❌ Ошибка чтения лога: {str(e)}',
                    'raw': '',
                    'timestamp': datetime.now().isoformat(),
                    'server_ready': False
                })
                time.sleep(1)
        
        f.close()
        self.running = False
        self.stop_db_monitor()
    
    def start(self):
        """Запускает мониторинг в отдельном потоке."""
        if self.thread and self.thread.is_alive():
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Останавливает мониторинг."""
        self.running = False
        self.stop_db_monitor()
        if self.thread:
            self.thread.join(timeout=2)
        return True
    
    def get_logs(self):
        """Возвращает все накопленные логи из очереди."""
        logs = []
        while True:
            try:
                item = self.log_queue.get_nowait()
                logs.append(item)
            except queue.Empty:
                break
        return logs
    
    def is_running(self):
        """Проверяет, запущен ли мониторинг."""
        return self.running and self.thread and self.thread.is_alive()
    
    def is_server_ready(self):
        """Возвращает статус готовности сервера."""
        return self.server_ready
    
    def get_online_count(self):
        """Возвращает количество игроков онлайн."""
        return self.online_count