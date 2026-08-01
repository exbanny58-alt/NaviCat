# server_manager.py
import psutil
import subprocess
import os
import threading
import time
import queue
import sys
from rpt_monitor import RPTMonitor
from pid_manager import save_pid, load_pid, clear_pid, is_process_running

class DayZServer:
    def __init__(self, server_path, executable="DayZServer_x64.exe", config="serverDZ.cfg"):
        self.server_path = server_path
        self.executable = executable
        self.config = config
        self.process = None
        self._using_pid = False
        self._pid = None
        self.log_queue = queue.Queue()
        self.reader_thread = None
        self.should_read = False
        
        # RPT монитор
        self.rpt_monitor = None
        self.rpt_monitor_thread = None
        self.should_monitor_rpt = False
        self.rpt_log_queue = queue.Queue()
        
        # Путь к папке profiles
        self.profiles_dir = os.path.join(server_path, "profiles") if server_path else ""
        
        # Пытаемся восстановить PID
        self._restore_pid()
        
        # Запускаем RPT монитор
        self._init_rpt_monitor()

    def _restore_pid(self):
        """Восстанавливает PID сервера из файла"""
        pid = load_pid('server')
        if pid and is_process_running(pid):
            print(f'🔄 Восстановлен PID сервера: {pid}')
            self._pid = pid
            self._using_pid = True
            self.process = None  # Не используем Popen
            return True
        
        if pid:
            print(f'⚠️ PID сервера {pid} не активен, очищаем')
            clear_pid('server')
        return False

    def _init_rpt_monitor(self):
        """Инициализирует и запускает RPT монитор."""
        if not self.profiles_dir or not os.path.exists(self.profiles_dir):
            print(f"⚠️ Папка profiles не найдена: {self.profiles_dir}")
            # Пробуем найти profiles относительно server_path
            if self.server_path:
                alt_profiles = os.path.join(self.server_path, "profiles")
                if os.path.exists(alt_profiles):
                    self.profiles_dir = alt_profiles
                    print(f"✅ Найдена папка profiles: {self.profiles_dir}")
                else:
                    # Создаём папку profiles если её нет
                    try:
                        os.makedirs(alt_profiles, exist_ok=True)
                        self.profiles_dir = alt_profiles
                        print(f"✅ Создана папка profiles: {self.profiles_dir}")
                    except:
                        print(f"❌ Не удалось создать папку profiles")
                        return
        
        # Создаём и запускаем RPT монитор
        try:
            self.rpt_monitor = RPTMonitor(self.profiles_dir)
            self.should_monitor_rpt = True
            self.rpt_monitor_thread = threading.Thread(target=self._rpt_monitor_loop, daemon=True)
            self.rpt_monitor_thread.start()
            print(f"📟 RPT монитор запущен, папка: {self.profiles_dir}")
        except Exception as e:
            print(f"❌ Ошибка запуска RPT монитора: {e}")

    def _rpt_monitor_loop(self):
        """Запускает RPT монитор в отдельном потоке и передаёт логи."""
        if not self.rpt_monitor:
            return
        
        # Запускаем монитор
        self.rpt_monitor.start()
        
        # Передаём логи из монитора в очередь
        while self.should_monitor_rpt and self.rpt_monitor:
            try:
                logs = self.rpt_monitor.get_logs()
                for log in logs:
                    self.rpt_log_queue.put(log)
                time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Ошибка в RPT мониторе: {e}")
                time.sleep(1)
        
        if self.rpt_monitor:
            self.rpt_monitor.stop()

    def is_running(self):
        """Проверяет, жив ли процесс сервера."""
        if self._using_pid and self._pid:
            return is_process_running(self._pid)
        if self.process is None:
            return False
        return self.process.poll() is None

    def start(self, mods_config=None):
        """Запускает сервер, если он еще не запущен."""
        # Проверяем, не запущен ли уже
        if self.is_running():
            return False, "Сервер уже запущен."

        if not self.server_path or not os.path.exists(self.server_path):
            return False, f"Папка сервера не найдена: {self.server_path}"

        executable_path = os.path.join(self.server_path, self.executable)
        if not os.path.exists(executable_path):
            return False, f"Исполняемый файл не найден: {executable_path}"

        command = [
            executable_path,
            f"-config={self.config}",
            "-profiles=profiles",
            "-port=2302",
            "-freezecheck",
            "-noFilePatching",
            "-doLogs",
            "-adminLog",
            "-netLog",
            "-pid=dayz.pid"
        ]
        
        # ============ ФОРМИРУЕМ АРГУМЕНТЫ МОДОВ ============
        if mods_config:
            mod_list = []
            
            print("\n" + "="*80)
            print("📋 ФОРМИРОВАНИЕ -mod=")
            print("="*80)
            
            for mod_name, types in mods_config.items():
                if not types.get("connected", False):
                    print(f"  ⚠️ {mod_name}: НЕ добавлен")
                    continue
                
                from server_links import load_server_links
                server_links = load_server_links()
                
                link_info = server_links.get(mod_name, {})
                mod_folder = link_info.get('mod_folder', '')
                
                if mod_folder:
                    mod_list.append('@' + mod_folder)
                    print(f"  ✅ {mod_name}: добавлен как @{mod_folder}")
                else:
                    print(f"  ⚠️ {mod_name}: НЕ найден mod_folder в server_links")
            
            if mod_list:
                mod_string = ';'.join(mod_list)
                command.insert(1, f"-mod={mod_string}")
                print(f"\n📋 Итоговый -mod: {mod_string}")
            else:
                print("\n⚠️ НЕТ МОДОВ для добавления")
            
            print("="*80 + "\n")
        
        # ============ ВЫВОДИМ КОМАНДУ ============
        print("\n" + "="*80)
        print("🚀 ФИНАЛЬНАЯ КОМАНДА ЗАПУСКА:")
        print("="*80)
        print(' '.join(command))
        print("="*80 + "\n")
        
        try:
            creationflags = 0
            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NEW_CONSOLE
            
            self.process = subprocess.Popen(
                command,
                cwd=self.server_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creationflags
            )
            
            # Сохраняем PID в файл
            if self.process.pid:
                save_pid('server', self.process.pid)
                self._pid = self.process.pid
                self._using_pid = False  # Используем Popen
            
            self.should_read = True
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()
            
            time.sleep(2)
            
            if self.is_running():
                return True, f"Сервер запущен (PID: {self.process.pid})"
            else:
                clear_pid('server')
                return False, "Сервер не запустился, проверьте логи"
                
        except Exception as e:
            self.process = None
            clear_pid('server')
            return False, f"Ошибка запуска: {str(e)}"

    def stop(self):
        """Останавливает сервер и все дочерние процессы."""
        if not self.is_running():
            return False, "Сервер не запущен."
        
        self.should_read = False
        
        try:
            if self._using_pid and self._pid:
                # Останавливаем по PID
                try:
                    p = psutil.Process(self._pid)
                    children = p.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            pass
                    p.terminate()
                    gone, alive = psutil.wait_procs(children + [p], timeout=5)
                    for proc in alive:
                        try:
                            proc.kill()
                        except:
                            pass
                except psutil.NoSuchProcess:
                    pass
            else:
                # Останавливаем через Popen
                try:
                    parent = psutil.Process(self.process.pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except:
                            pass
                    gone, alive = psutil.wait_procs(children + [parent], timeout=5)
                    for proc in alive:
                        try:
                            proc.kill()
                        except:
                            pass
                except psutil.NoSuchProcess:
                    pass
            
            # Очищаем PID файл
            clear_pid('server')
            self._pid = None
            self._using_pid = False
            self.process = None
            
            return True, "Сервер остановлен."
        except Exception as e:
            return False, f"Ошибка остановки: {str(e)}"

    def status(self):
        """Возвращает статус сервера."""
        if self.is_running():
            try:
                pid = self._pid if self._using_pid else self.process.pid
                p = psutil.Process(pid)
                mem_mb = p.memory_info().rss / 1024 / 1024
                cpu = p.cpu_percent(interval=0.1)
                return {
                    "running": True,
                    "pid": pid,
                    "memory_mb": f"{mem_mb:.1f}",
                    "cpu_percent": f"{cpu:.1f}"
                }
            except:
                return {"running": True, "pid": pid}
        return {"running": False}

    def _read_output(self):
        """Читает вывод сервера в отдельном потоке и кладет строки в очередь."""
        while self.should_read and self.process and self.process.stdout:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                self.log_queue.put(line.strip())
            except:
                break
        self.log_queue.put(None)

    def get_logs(self):
        """Извлекает все накопленные логи из очереди."""
        logs = []
        while True:
            try:
                line = self.log_queue.get_nowait()
                if line is None:
                    logs.append("--- Сервер остановлен ---")
                    break
                logs.append(line)
            except queue.Empty:
                break
        return logs

    def get_rpt_logs(self):
        """Извлекает все накопленные RPT логи из очереди."""
        logs = []
        while True:
            try:
                item = self.rpt_log_queue.get_nowait()
                logs.append(item)
            except queue.Empty:
                break
        return logs
    
    def is_rpt_active(self):
        """Проверяет, активен ли RPT монитор."""
        return (self.rpt_monitor is not None and 
                self.rpt_monitor.is_running() and 
                self.should_monitor_rpt)