import os
import json

# Путь к файлу с настройками
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')
MODS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'mods_config.json')

def load_settings():
    """Загружает настройки из JSON файла"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """Сохраняет настройки в JSON файл"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения: {e}')
        return False

# ============================================
# РАБОТА С КОНФИГОМ МОДОВ
# ============================================

def load_mods_config():
    """Загружает конфиг модов"""
    if os.path.exists(MODS_CONFIG_FILE):
        try:
            with open(MODS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_mods_config(config):
    """Сохраняет конфиг модов"""
    try:
        with open(MODS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f'❌ Ошибка сохранения конфига модов: {e}')
        return False

def get_mod_state(mod_id, attr):
    """Получить состояние конкретного атрибута мода"""
    config = load_mods_config()
    if mod_id in config:
        return config[mod_id].get(attr, False)
    return False

def set_mod_state(mod_id, attr, value):
    """Установить состояние конкретного атрибута мода"""
    config = load_mods_config()
    if mod_id not in config:
        config[mod_id] = {}
    config[mod_id][attr] = value
    return save_mods_config(config)

def get_mod_full_state(mod_id):
    """Получить полное состояние мода"""
    config = load_mods_config()
    if mod_id in config:
        return config[mod_id]
    return {
        'server': False,
        'server_mod': False,
        'client': False
    }

def init_mods_config(mods):
    """Инициализирует конфиг для новых модов (если их нет)"""
    config = load_mods_config()
    changed = False
    
    for mod in mods:
        mod_id = mod['id']
        if mod_id not in config:
            config[mod_id] = {
                'server': False,
                'server_mod': False,
                'client': False  # По умолчанию клиентский мод включён
            }
            changed = True
    
    if changed:
        save_mods_config(config)
    
    return config