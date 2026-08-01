import os
import json
import subprocess
import platform
import shutil
from datetime import datetime

# Файл для хранения конфига подключённых модов игры
GAME_LINKS_FILE = os.path.join(os.path.dirname(__file__), 'game_links.json')

def load_game_links():
    """Загружает список подключённых модов игры"""
    if os.path.exists(GAME_LINKS_FILE):
        try:
            with open(GAME_LINKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_game_links(links):
    """Сохраняет список подключённых модов игры"""
    try:
        with open(GAME_LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения game_links: {e}')
        return False

def force_delete_path(path):
    """Удаляет путь любой ценой"""
    if not os.path.exists(path) and not os.path.islink(path):
        return True
    
    try:
        if os.path.islink(path):
            os.unlink(path)
            print(f'🗑️ Удалена ссылка: {path}')
            return True
        
        if os.path.isdir(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f'🗑️ Удалена папка: {path}')
                return True
            except:
                pass
            
            try:
                cmd = ['cmd', '/c', 'rmdir', '/s', '/q', path]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    print(f'🗑️ Удалена папка (rmdir): {path}')
                    return True
            except:
                pass
        
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f'🗑️ Удалён файл: {path}')
                return True
            except:
                try:
                    cmd = ['cmd', '/c', 'del', '/f', '/q', path]
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        print(f'🗑️ Удалён файл (del): {path}')
                        return True
                except:
                    pass
        
        print(f'⚠️ Не удалось удалить: {path}')
        return False
        
    except Exception as e:
        print(f'❌ Ошибка удаления {path}: {e}')
        return False

def create_symlink_windows(source_path, link_path):
    """Создаёт символическую ссылку на Windows через os.symlink"""
    try:
        if os.path.exists(link_path) or os.path.islink(link_path):
            print(f'🗑️ Удаляем существующий путь: {link_path}')
            force_delete_path(link_path)
        
        os.symlink(source_path, link_path, target_is_directory=True)
        print(f'✅ Создана симлинк: {link_path} -> {source_path}')
        return True, 'Символическая ссылка создана'
            
    except Exception as e:
        print(f'❌ Ошибка создания симлинка: {e}')
        return create_symlink_mklink(source_path, link_path)

def create_symlink_mklink(source_path, link_path):
    """Создаёт ссылку через mklink (Windows)"""
    try:
        if os.path.exists(link_path) or os.path.islink(link_path):
            print(f'🗑️ Удаляем существующий путь: {link_path}')
            force_delete_path(link_path)
        
        cmd = ['cmd', '/c', 'mklink', '/D', link_path, source_path]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            cmd = ['cmd', '/c', 'mklink', '/J', link_path, source_path]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode != 0:
                return False, f'Ошибка: {result.stderr or result.stdout}'
        
        print(f'✅ Создана ссылка: {link_path} -> {source_path}')
        return True, 'Ссылка создана'
            
    except Exception as e:
        print(f'❌ Ошибка создания ссылки: {e}')
        return False, str(e)

def create_symlink(source_path, link_path):
    """Создаёт символическую ссылку"""
    system = platform.system()
    
    if system == 'Windows':
        success, message = create_symlink_windows(source_path, link_path)
        if success:
            return success, message
        print('⚠️ os.symlink не сработал, пробуем mklink...')
        return create_symlink_mklink(source_path, link_path)
    else:
        try:
            if os.path.exists(link_path) or os.path.islink(link_path):
                force_delete_path(link_path)
            os.symlink(source_path, link_path)
            print(f'✅ Создана ссылка: {link_path} -> {source_path}')
            return True, 'Ссылка создана'
        except Exception as e:
            return False, str(e)

def get_mod_link_name(mod_folder):
    """Генерирует имя для ссылки (с префиксом @)"""
    clean_name = mod_folder.lstrip('@')
    return f'@{clean_name}'

def connect_game_mod(mod_id, mod_path, mod_name, mod_folder, game_dir):
    """
    Подключает мод к игре - создаёт ссылку
    """
    if not game_dir:
        return {'success': False, 'message': 'Папка игры не указана'}
    
    if not mod_path or not os.path.exists(mod_path):
        return {'success': False, 'message': f'Папка мода не найдена: {mod_path}'}
    
    if not os.path.exists(game_dir):
        return {'success': False, 'message': f'Папка игры не найдена: {game_dir}'}
    
    # Генерируем имя для ссылки
    link_name = get_mod_link_name(mod_folder)
    link_path = os.path.join(game_dir, link_name)
    
    # Создаём ссылку
    success, message = create_symlink(mod_path, link_path)
    if not success:
        return {'success': False, 'message': message}
    
    # Сохраняем в конфиг
    links = load_game_links()
    links[mod_id] = {
        'mod_id': mod_id,
        'mod_name': mod_name,
        'mod_folder': mod_folder,
        'mod_path': mod_path,
        'link_name': link_name,
        'link_path': link_path,
        'game_dir': game_dir,
        'created_at': datetime.now().isoformat(),
        'enabled': True
    }
    save_game_links(links)
    
    return {
        'success': True,
        'message': f'Мод "{mod_name}" подключён к игре',
        'link_path': link_path
    }

def disconnect_game_mod(mod_id):
    """
    Отключает мод от игры - удаляет ссылку/папку и конфиг
    """
    links = load_game_links()
    
    if mod_id not in links:
        return {'success': False, 'message': 'Мод не подключён'}
    
    link_info = links[mod_id]
    link_path = link_info.get('link_path')
    
    # Удаляем ссылку/папку
    if link_path:
        print(f'🗑️ Удаляем: {link_path}')
        force_delete_path(link_path)
    
    # Удаляем из конфига
    del links[mod_id]
    save_game_links(links)
    
    return {
        'success': True,
        'message': f'Мод отключён от игры'
    }

def get_connected_game_mods():
    """Возвращает список подключённых модов игры"""
    links = load_game_links()
    return links