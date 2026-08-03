# symlink_manager.py

import os
import json
import shutil
from PyQt6.QtCore import QObject, pyqtSignal


class SymlinkManager(QObject):
    """Менеджер для создания и управления симлинками модов."""
    
    # Сигналы для уведомлений
    symlink_created = pyqtSignal(str, str)  # (mod_name, target_path)
    symlink_removed = pyqtSignal(str, str)  # (mod_name, target_path)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def _get_mod_name_for_symlink(self, mod_name):
        """Формирует имя для симлинка в формате @имя_мода."""
        # Удаляем недопустимые символы для имени файла
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            mod_name = mod_name.replace(char, '_')
        # Добавляем @ в начало
        return f"@{mod_name}"
    
    def create_symlink(self, mod_data, target_dir, mod_type="Server"):
        """
        Создаёт симлинк для мода в целевой папке.
        
        Args:
            mod_data: dict с данными мода (name, path, type, id, author, version)
            target_dir: путь к папке, куда создавать симлинк (сервер или клиент)
            mod_type: "Server" или "Client"
        
        Returns:
            tuple: (success, symlink_path) - (True/False, путь к симлинку или None)
        """
        try:
            mod_name = mod_data['name']
            mod_path = mod_data['path']
            
            # Проверяем существование папки мода
            if not os.path.exists(mod_path):
                self.error_occurred.emit(f"Папка мода не существует: {mod_path}")
                return False, None
            
            # Проверяем существование целевой папки
            if not os.path.exists(target_dir):
                self.error_occurred.emit(f"Целевая папка не существует: {target_dir}")
                return False, None
            
            # Формируем имя симлинка
            symlink_name = self._get_mod_name_for_symlink(mod_name)
            symlink_path = os.path.join(target_dir, symlink_name)
            
            # Если симлинк уже существует, удаляем его
            if os.path.exists(symlink_path):
                self._remove_symlink(symlink_path)
            
            # Проверяем, не является ли мод уже симлинком в этой папке
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.islink(item_path):
                    try:
                        link_target = os.readlink(item_path)
                        if link_target == mod_path:
                            self._remove_symlink(item_path)
                            break
                    except:
                        pass
            
            # Создаём симлинк
            if os.name == 'nt':  # Windows
                try:
                    os.symlink(mod_path, symlink_path, target_is_directory=True)
                except OSError:
                    try:
                        import subprocess
                        subprocess.run(['cmd', '/c', 'mklink', '/J', symlink_path, mod_path], 
                                     capture_output=True, check=True)
                    except:
                        self.error_occurred.emit(
                            f"Не удалось создать симлинк для {mod_name}. "
                            "Запустите программу от имени администратора."
                        )
                        return False, None
            else:  # Linux/Mac
                os.symlink(mod_path, symlink_path, target_is_directory=True)
            
            self.symlink_created.emit(mod_name, symlink_path)
            return True, symlink_path
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка создания симлинка для {mod_data.get('name', 'неизвестного мода')}: {str(e)}")
            return False, None
    
    def remove_symlink(self, mod_name, target_dir):
        """
        Удаляет симлинк для мода из целевой папки.
        
        Args:
            mod_name: имя мода
            target_dir: целевая папка
        
        Returns:
            bool: True если симлинк удалён успешно, иначе False
        """
        try:
            symlink_name = self._get_mod_name_for_symlink(mod_name)
            symlink_path = os.path.join(target_dir, symlink_name)
            
            if os.path.exists(symlink_path):
                self._remove_symlink(symlink_path)
                self.symlink_removed.emit(mod_name, symlink_path)
                return True
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Ошибка удаления симлинка для {mod_name}: {str(e)}")
            return False
    
    def _remove_symlink(self, symlink_path):
        """Внутренний метод для удаления симлинка."""
        try:
            if os.path.islink(symlink_path):
                os.unlink(symlink_path)
            elif os.path.exists(symlink_path):
                if os.path.isdir(symlink_path):
                    shutil.rmtree(symlink_path)
                else:
                    os.remove(symlink_path)
            return True
        except Exception as e:
            print(f"Ошибка удаления {symlink_path}: {e}")
            return False
    
    def check_symlink_exists(self, mod_name, target_dir):
        """
        Проверяет, существует ли симлинк для мода в целевой папке.
        
        Args:
            mod_name: имя мода
            target_dir: целевая папка
        
        Returns:
            bool: True если симлинк существует
        """
        symlink_name = self._get_mod_name_for_symlink(mod_name)
        symlink_path = os.path.join(target_dir, symlink_name)
        return os.path.islink(symlink_path)