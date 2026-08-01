import os
import json
import subprocess
import platform
import shutil
import tempfile
from datetime import datetime

# Файл для хранения конфига подключённых модов
SERVER_LINKS_FILE = os.path.join(os.path.dirname(__file__), 'server_links.json')

def load_server_links():
    """Загружает список подключённых модов"""
    if os.path.exists(SERVER_LINKS_FILE):
        try:
            with open(SERVER_LINKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_server_links(links):
    """Сохраняет список подключённых модов"""
    try:
        with open(SERVER_LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения server_links: {e}')
        return False

def is_symlink(path):
    """Проверяет, является ли путь символической ссылкой"""
    return os.path.islink(path)

def force_delete_path(path):
    """
    Удаляет путь любой ценой
    """
    if not os.path.exists(path) and not os.path.islink(path):
        return True
    
    try:
        # Если это ссылка - удаляем через os.unlink
        if os.path.islink(path):
            os.unlink(path)
            print(f'🗑️ Удалена ссылка (unlink): {path}')
            return True
        
        # Если это папка
        if os.path.isdir(path):
            # Пробуем через shutil
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f'🗑️ Удалена папка (rmtree): {path}')
                return True
            except:
                pass
            
            # Через cmd rmdir
            try:
                cmd = ['cmd', '/c', 'rmdir', '/s', '/q', path]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    print(f'🗑️ Удалена папка (rmdir): {path}')
                    return True
            except:
                pass
        
        # Если это файл
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f'🗑️ Удалён файл: {path}')
                return True
            except:
                # Через cmd del
                try:
                    cmd = ['cmd', '/c', 'del', '/f', '/q', path]
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        print(f'🗑️ Удалён файл (del): {path}')
                        return True
                except:
                    pass
        
        # Последняя попытка - через cmd с принудительным удалением
        try:
            if os.path.isdir(path):
                cmd = ['cmd', '/c', 'rmdir', '/s', '/q', path]
            else:
                cmd = ['cmd', '/c', 'del', '/f', '/q', path]
            subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if not os.path.exists(path) and not os.path.islink(path):
                print(f'🗑️ Удалено (force): {path}')
                return True
        except:
            pass
        
        print(f'⚠️ Не удалось удалить: {path}')
        return False
        
    except Exception as e:
        print(f'❌ Ошибка удаления {path}: {e}')
        return False

def create_symlink_windows(source_path, link_path):
    """
    Создаёт символическую ссылку на Windows через os.symlink
    (требует права администратора или включённый режим разработчика)
    """
    try:
        # Удаляем всё что есть по пути
        if os.path.exists(link_path) or os.path.islink(link_path):
            print(f'🗑️ Удаляем существующий путь: {link_path}')
            force_delete_path(link_path)
        
        # Создаём символическую ссылку через os.symlink
        # На Windows нужно указать target_is_directory=True для папок
        os.symlink(source_path, link_path, target_is_directory=True)
        print(f'✅ Создана симлинк: {link_path} -> {source_path}')
        return True, 'Символическая ссылка создана'
            
    except Exception as e:
        print(f'❌ Ошибка создания симлинка: {e}')
        # Если os.symlink не работает, пробуем через mklink
        return create_symlink_mklink(source_path, link_path)

def create_symlink_mklink(source_path, link_path):
    """
    Создаёт ссылку через mklink (Windows)
    """
    try:
        # Удаляем всё что есть по пути
        if os.path.exists(link_path) or os.path.islink(link_path):
            print(f'🗑️ Удаляем существующий путь: {link_path}')
            force_delete_path(link_path)
        
        # Пробуем /D (симлинк для папок) - требует прав
        cmd = ['cmd', '/c', 'mklink', '/D', link_path, source_path]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            # Пробуем /J (junction) - не требует прав
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
    """
    Создаёт символическую ссылку
    """
    system = platform.system()
    
    if system == 'Windows':
        # Сначала пробуем os.symlink
        success, message = create_symlink_windows(source_path, link_path)
        if success:
            return success, message
        
        # Если не вышло - пробуем mklink
        print('⚠️ os.symlink не сработал, пробуем mklink...')
        return create_symlink_mklink(source_path, link_path)
    else:
        # Linux/Mac
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

def _copy_keys_from_mod(mod_name, mod_source_path, server_keys_dir):
    """Копирует все .bikey файлы из папки мода в папку Keys сервера."""
    copied_count = 0
    
    for root, dirs, files in os.walk(mod_source_path):
        for dir_name in dirs:
            if dir_name.lower() in ['keys', 'key']:
                key_dir = os.path.join(root, dir_name)
                if not os.path.exists(key_dir):
                    continue
                for filename in os.listdir(key_dir):
                    if filename.endswith('.bikey'):
                        src_path = os.path.join(key_dir, filename)
                        dst_path = os.path.join(server_keys_dir, filename)
                        try:
                            shutil.copy2(src_path, dst_path)
                            print(f'  Ключ скопирован: {filename} (из {mod_name})')
                            copied_count += 1
                        except Exception as e:
                            print(f'  Ошибка копирования ключа {filename} из {mod_name}: {e}')
    
    if copied_count == 0:
        print(f'  Предупреждение: ключи не найдены в моде {mod_name}')
    else:
        print(f'  Мод {mod_name}: скопировано ключей — {copied_count}')
    
    return copied_count

def _remove_keys_from_mod(mod_name, mod_source_path, server_keys_dir):
    """Удаляет ключи конкретного мода из папки Keys сервера."""
    if not os.path.exists(server_keys_dir):
        return
    
    mod_key_names = set()
    for root, dirs, files in os.walk(mod_source_path):
        for d in dirs:
            if d.lower() in ['keys', 'key']:
                key_dir = os.path.join(root, d)
                if os.path.exists(key_dir):
                    for f in os.listdir(key_dir):
                        if f.endswith('.bikey'):
                            mod_key_names.add(f)
    
    for key_name in mod_key_names:
        if key_name.lower() == 'dayz.bikey':
            continue
        key_path = os.path.join(server_keys_dir, key_name)
        if os.path.exists(key_path):
            try:
                os.remove(key_path)
                print(f'🗑️ Ключ удалён: {key_name}')
            except Exception as e:
                print(f'⚠️ Ошибка удаления ключа {key_name}: {e}')

def rebuild_all_keys(server_dir, connected_mods_list):
    """
    Полностью пересобирает папку Keys для всех подключённых модов
    """
    server_keys_dir = os.path.join(server_dir, 'Keys')
    os.makedirs(server_keys_dir, exist_ok=True)
    
    # Сохраняем официальный ключ
    official_key_path = os.path.join(server_keys_dir, 'dayz.bikey')
    official_key_backup = None
    
    if os.path.exists(official_key_path):
        try:
            official_key_backup = os.path.join(tempfile.gettempdir(), 'dayz_bikey_backup')
            shutil.copy2(official_key_path, official_key_backup)
            print('📦 Официальный ключ dayz.bikey сохранён')
        except Exception as e:
            print(f'⚠️ Ошибка сохранения dayz.bikey: {e}')
    
    # Удаляем все ключи
    if os.path.exists(server_keys_dir):
        for filename in os.listdir(server_keys_dir):
            if filename.endswith('.bikey'):
                filepath = os.path.join(server_keys_dir, filename)
                try:
                    os.remove(filepath)
                    print(f'🗑️ Ключ удалён: {filename}')
                except Exception as e:
                    print(f'⚠️ Ошибка удаления ключа {filename}: {e}')
    
    # Копируем ключи из подключённых модов
    for mod_name, mod_path in connected_mods_list:
        _copy_keys_from_mod(mod_name, mod_path, server_keys_dir)
    
    # Восстанавливаем официальный ключ
    if official_key_backup and os.path.exists(official_key_backup):
        try:
            shutil.copy2(official_key_backup, official_key_path)
            print('✅ Официальный ключ dayz.bikey восстановлен')
        except Exception as e:
            print(f'⚠️ Ошибка восстановления dayz.bikey: {e}')
        try:
            os.remove(official_key_backup)
        except:
            pass
    
    print(f'✅ Папка Keys пересобрана. Подключено модов: {len(connected_mods_list)}')

def connect_mod_to_server(mod_id, mod_path, mod_name, mod_folder, server_dir):
    """
    Подключает мод к серверу - создаёт ссылку и копирует ключи
    """
    if not server_dir:
        return {'success': False, 'message': 'Папка сервера не указана'}
    
    if not mod_path or not os.path.exists(mod_path):
        return {'success': False, 'message': f'Папка мода не найдена: {mod_path}'}
    
    if not os.path.exists(server_dir):
        return {'success': False, 'message': f'Папка сервера не найдена: {server_dir}'}
    
    # Генерируем имя для ссылки
    link_name = get_mod_link_name(mod_folder)
    link_path = os.path.join(server_dir, link_name)
    
    # Создаём ссылку
    success, message = create_symlink(mod_path, link_path)
    if not success:
        return {'success': False, 'message': message}
    
    # Сохраняем в конфиг
    links = load_server_links()
    links[mod_id] = {
        'mod_id': mod_id,
        'mod_name': mod_name,
        'mod_folder': mod_folder,
        'mod_path': mod_path,
        'link_name': link_name,
        'link_path': link_path,
        'server_dir': server_dir,
        'created_at': datetime.now().isoformat(),
        'enabled': True
    }
    save_server_links(links)
    
    # Пересобираем ключи для всех подключённых модов
    connected = [(info['mod_folder'], info['mod_path']) for info in links.values()]
    rebuild_all_keys(server_dir, connected)
    
    return {
        'success': True,
        'message': f'Мод "{mod_name}" подключён к серверу',
        'link_path': link_path
    }

def disconnect_mod_from_server(mod_id):
    """
    Отключает мод от сервера - удаляет ссылку/папку и конфиг, пересобирает ключи
    """
    links = load_server_links()
    
    if mod_id not in links:
        return {'success': False, 'message': 'Мод не подключён'}
    
    link_info = links[mod_id]
    link_path = link_info.get('link_path')
    mod_path = link_info.get('mod_path')
    server_dir = link_info.get('server_dir')
    mod_folder = link_info.get('mod_folder')
    
    # Удаляем ключи этого мода
    if server_dir and mod_path:
        server_keys_dir = os.path.join(server_dir, 'Keys')
        _remove_keys_from_mod(mod_folder, mod_path, server_keys_dir)
    
    # Удаляем ссылку/папку
    if link_path:
        print(f'🗑️ Удаляем: {link_path}')
        force_delete_path(link_path)
    
    # Удаляем из конфига
    del links[mod_id]
    save_server_links(links)
    
    # Пересобираем ключи для оставшихся модов
    if server_dir:
        connected = [(info['mod_folder'], info['mod_path']) for info in links.values()]
        rebuild_all_keys(server_dir, connected)
    
    return {
        'success': True,
        'message': f'Мод отключён от сервера'
    }

def get_connected_mods():
    """Возвращает список подключённых модов"""
    links = load_server_links()
    return links

def get_connected_mods_list(settings):
    """
    Возвращает список подключённых модов с путями для пересборки ключей
    """
    links = load_server_links()
    workshop = settings.get('workshop', '')
    custom_mods = settings.get('custom_mods', '')
    
    connected = []
    for mod_id, info in links.items():
        mod_folder = info.get('mod_folder')
        if not mod_folder:
            continue
        
        # Ищем папку мода
        mod_path = None
        for base_path in [workshop, custom_mods]:
            if base_path:
                candidate = os.path.join(base_path, mod_folder)
                if os.path.exists(candidate) and os.path.isdir(candidate):
                    mod_path = candidate
                    break
        
        if mod_path:
            connected.append((mod_folder, mod_path))
        else:
            print(f'⚠️ Папка мода не найдена: {mod_folder}')
    
    return connected