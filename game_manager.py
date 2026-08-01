# game_manager.py
import psutil
import subprocess
import os
import threading
import time
import queue
import sys
from pid_manager import save_pid, load_pid, clear_pid, is_process_running

class DayZGame:
    def __init__(self, game_path, executable="DayZ_x64.exe"):
        self.game_path = game_path
        self.executable = executable
        self.process = None
        self._using_pid = False
        self._pid = None
        self.log_queue = queue.Queue()
        self.reader_thread = None
        self.should_read = False
        
        # Восстанавливаем PID
        self._restore_pid()

    def _restore_pid(self):
        """Восстанавливает PID игры из файла"""
        pid = load_pid('game')
        if pid and is_process_running(pid):
            print(f'🔄 Восстановлен PID игры: {pid}')
            self._pid = pid
            self._using_pid = True
            self.process = None
            return True
        
        if pid:
            print(f'⚠️ PID игры {pid} не активен, очищаем')
            clear_pid('game')
        return False

    def is_running(self):
        """Проверяет, жив ли процесс игры"""
        if self._using_pid and self._pid:
            return is_process_running(self._pid)
        if self.process is None:
            return False
        return self.process.poll() is None

    def start(self, mods_config=None, connect_ip="127.0.0.1", connect_port="2302", player_name="player"):
        """Запускает игру с указанными модами"""
        if self.is_running():
            return False, "Игра уже запущена."

        if not self.game_path or not os.path.exists(self.game_path):
            return False, f"Папка игры не найдена: {self.game_path}"

        executable_path = os.path.join(self.game_path, self.executable)
        if not os.path.exists(executable_path):
            return False, f"Исполняемый файл не найден: {executable_path}"

        print(f"🎮 Используется ник: '{player_name}'")

        # Базовые аргументы
        command = [
            executable_path,
            f"-connect={connect_ip}",
            f"-port={connect_port}",
            f"-name={player_name}"
        ]        
        # ============ ФОРМИРУЕМ АРГУМЕНТЫ МОДОВ ============
        mod_string = None
        
        if mods_config:
            mod_list = []
            
            print("\n" + "="*80)
            print("🎮 ФОРМИРОВАНИЕ -mod= для игры")
            print("="*80)
            
            for mod_id, mod_info in mods_config.items():
                if not mod_info.get("enabled", False):
                    print(f"  ⚠️ {mod_id}: отключён")
                    continue
                
                link_name = mod_info.get("link_name", "")
                
                if link_name:
                    mod_list.append(link_name)
                    print(f"  ✅ {mod_id}: добавлен как {link_name}")
                else:
                    print(f"  ⚠️ {mod_id}: НЕ найден link_name")
            
            if mod_list:
                mod_string = ';'.join(mod_list)
                print(f"\n📋 Итоговый -mod: {mod_string}")
            else:
                print("\n⚠️ НЕТ МОДОВ для добавления")
            
            print("="*80 + "\n")
        
        if mod_string:
            command.insert(1, f"-mod={mod_string}")
        
        # ============ ВЫВОДИМ КОМАНДУ ============
        print("\n" + "="*80)
        print("🚀 ФИНАЛЬНАЯ КОМАНДА ЗАПУСКА ИГРЫ:")
        print("="*80)
        print(' '.join(command))
        print("="*80 + "\n")
        
        try:
            creationflags = 0
            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NEW_CONSOLE
            
            self.process = subprocess.Popen(
                command,
                cwd=self.game_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                creationflags=creationflags
            )
            
            # Сохраняем PID
            if self.process.pid:
                save_pid('game', self.process.pid)
                self._pid = self.process.pid
                self._using_pid = False
            
            self.should_read = True
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()
            
            time.sleep(2)
            
            if self.is_running():
                return True, f"Игра запущена (PID: {self.process.pid})"
            else:
                clear_pid('game')
                return False, "Игра не запустилась, проверьте логи"
                
        except Exception as e:
            self.process = None
            clear_pid('game')
            return False, f"Ошибка запуска: {str(e)}"

    def stop(self):
        """Останавливает игру и все дочерние процессы"""
        if not self.is_running():
            return False, "Игра не запущена."
        
        self.should_read = False
        
        try:
            if self._using_pid and self._pid:
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
            
            clear_pid('game')
            self._pid = None
            self._using_pid = False
            self.process = None
            
            return True, "Игра остановлена."
        except Exception as e:
            return False, f"Ошибка остановки: {str(e)}"

    def status(self):
        """Возвращает статус игры"""
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
        """Читает вывод игры в отдельном потоке и кладет строки в очередь"""
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
        """Извлекает все накопленные логи из очереди"""
        logs = []
        while True:
            try:
                line = self.log_queue.get_nowait()
                if line is None:
                    logs.append("--- Игра остановлена ---")
                    break
                logs.append(line)
            except queue.Empty:
                break
        return logs