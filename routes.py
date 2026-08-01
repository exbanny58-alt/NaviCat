# routes.py
from flask import render_template, send_from_directory, request, jsonify
import os
import subprocess
import platform
import threading
import re
import json
import hashlib
import queue
import traceback
import uuid
from datetime import datetime
from settings_manager import load_settings, save_settings
from file_dialogs import select_file_dialog, select_folder_dialog

def register_routes(app):
    """Регистрирует все маршруты в приложении"""

    # Путь к файлу кеша модов
    MODS_CACHE_FILE = os.path.join(os.path.dirname(__file__), 'mods_cache.json')

    def get_mods_cache():
        """Загружает кеш модов из файла"""
        if os.path.exists(MODS_CACHE_FILE):
            try:
                with open(MODS_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        return None

    def save_mods_cache(mods_data):
        """Сохраняет кеш модов в файл"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'mods': mods_data,
                'hash': hashlib.md5(json.dumps(mods_data, sort_keys=True).encode()).hexdigest()
            }
            with open(MODS_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f'❌ Ошибка сохранения кеша модов: {e}')
            return False

    # ============================================
    # ГЛАВНАЯ СТРАНИЦА
    # ============================================
    @app.route('/')
    def index():
        return render_template('index.html')

    # ============================================
    # СТАТИЧЕСКИЕ ФАЙЛЫ
    # ============================================
    @app.route('/static/webfonts/<path:filename>')
    def serve_webfonts(filename):
        return send_from_directory('static/webfonts', filename)

    @app.route('/static/images/<path:filename>')
    def serve_images(filename):
        return send_from_directory('static/images', filename)

    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory('static/css', filename)

    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory('static/js', filename)

    # ============================================
    # СТРАНИЦА НАСТРОЕК
    # ============================================
    @app.route('/settings-content')
    def settings_content():
        return render_template('settings_content.html')

    # ============================================
    # API ДЛЯ НАСТРОЕК
    # ============================================
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        settings = load_settings()
        return jsonify(settings)

    @app.route('/api/settings', methods=['POST'])
    def save_settings_api():
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'success': False, 'message': 'Нет данных'}), 400
            
            if save_settings(data):
                return jsonify({'success': True, 'message': 'Настройки сохранены'})
            return jsonify({'success': False, 'message': 'Ошибка сохранения'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/settings/reset/<field>', methods=['POST'])
    def reset_setting(field):
        try:
            settings = load_settings()
            settings[field] = ""
            save_settings(settings)
            return jsonify({'success': True, 'message': f'Поле {field} сброшено'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============================================
    # API ДЛЯ ОТКРЫТИЯ ПРОВОДНИКА
    # ============================================
    @app.route('/api/browse/file', methods=['POST'])
    def browse_file():
        try:
            data = request.get_json()
            field = data.get('field')
            input_id = data.get('inputId')
            
            result = [None]
            
            def thread_func():
                result[0] = select_file_dialog()
            
            thread = threading.Thread(target=thread_func)
            thread.start()
            thread.join(timeout=60)
            
            file_path = result[0]
            
            if file_path and file_path.strip():
                return jsonify({
                    'success': True,
                    'path': file_path,
                    'field': field,
                    'inputId': input_id,
                    'message': 'Файл выбран'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Файл не выбран'
                })
        
        except Exception as e:
            print(f'❌ Ошибка: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/browse/folder', methods=['POST'])
    def browse_folder():
        try:
            data = request.get_json()
            field = data.get('field')
            input_id = data.get('inputId')
            
            result = [None]
            
            def thread_func():
                result[0] = select_folder_dialog()
            
            thread = threading.Thread(target=thread_func)
            thread.start()
            thread.join(timeout=60)
            
            folder_path = result[0]
            
            if folder_path and folder_path.strip():
                return jsonify({
                    'success': True,
                    'path': folder_path,
                    'field': field,
                    'inputId': input_id,
                    'message': 'Папка выбрана'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Папка не выбрана'
                })
        
        except Exception as e:
            print(f'❌ Ошибка: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    # ============================================
    # API ДЛЯ ОТКРЫТИЯ ПАПКИ В ПРОВОДНИКЕ
    # ============================================
    @app.route('/api/open/explorer', methods=['POST'])
    def open_explorer():
        try:
            data = request.get_json()
            path = data.get('path', '').strip()
            
            if not path:
                return jsonify({
                    'success': False,
                    'message': 'Путь не указан'
                })
            
            if not os.path.exists(path):
                return jsonify({
                    'success': False,
                    'message': f'Путь не существует: {path}'
                })
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(path)
            elif system == 'Darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
            
            return jsonify({
                'success': True,
                'message': f'Открыто: {path}'
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    # ============================================
    # ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ МОДОВ
    # ============================================
    def read_mod_meta(mod_path):
        meta_path = os.path.join(mod_path, 'meta.cpp')
        if not os.path.exists(meta_path):
            return None
        
        try:
            with open(meta_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if name_match:
                return name_match.group(1).strip()
            
            name_match = re.search(r'name\s*=\s*\{([^}]+)\}', content)
            if name_match:
                return name_match.group(1).strip()
            
            return None
        except Exception as e:
            print(f'⚠️ Ошибка чтения meta.cpp в {mod_path}: {e}')
            return None

    def get_mod_version(mod_path):
        meta_path = os.path.join(mod_path, 'meta.cpp')
        if not os.path.exists(meta_path):
            return None
        
        try:
            with open(meta_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                return version_match.group(1).strip()
            
            version_match = re.search(r'version\s*=\s*\{([^}]+)\}', content)
            if version_match:
                return version_match.group(1).strip()
            
            return None
        except:
            return None

    def scan_mods(workshop_path, custom_mods_path):
        mods = []
        mod_ids = set()
        
        if workshop_path and os.path.exists(workshop_path):
            try:
                for item in os.listdir(workshop_path):
                    item_path = os.path.join(workshop_path, item)
                    if os.path.isdir(item_path):
                        has_meta = os.path.exists(os.path.join(item_path, 'meta.cpp'))
                        has_config = os.path.exists(os.path.join(item_path, 'config.cpp'))
                        
                        if has_meta or has_config:
                            mod_name = read_mod_meta(item_path)
                            mod_version = get_mod_version(item_path)
                            
                            if not mod_name:
                                mod_name = item
                            
                            mod_id = f"workshop_{item}"
                            if mod_id not in mod_ids:
                                mod_ids.add(mod_id)
                                mods.append({
                                    'id': mod_id,
                                    'name': mod_name,
                                    'folder': item,
                                    'path': item_path,
                                    'type': 'workshop',
                                    'version': mod_version or 'Неизвестно',
                                    'enabled': True,
                                    'has_meta': has_meta
                                })
            except Exception as e:
                print(f'⚠️ Ошибка сканирования Workshop: {e}')
        
        if custom_mods_path and os.path.exists(custom_mods_path):
            try:
                for item in os.listdir(custom_mods_path):
                    item_path = os.path.join(custom_mods_path, item)
                    if os.path.isdir(item_path):
                        has_meta = os.path.exists(os.path.join(item_path, 'meta.cpp'))
                        has_config = os.path.exists(os.path.join(item_path, 'config.cpp'))
                        
                        if has_meta or has_config:
                            mod_name = read_mod_meta(item_path)
                            mod_version = get_mod_version(item_path)
                            
                            if not mod_name:
                                mod_name = item
                            
                            mod_id = f"custom_{item}"
                            if mod_id not in mod_ids:
                                mod_ids.add(mod_id)
                                mods.append({
                                    'id': mod_id,
                                    'name': mod_name,
                                    'folder': item,
                                    'path': item_path,
                                    'type': 'custom',
                                    'version': mod_version or 'Неизвестно',
                                    'enabled': True,
                                    'has_meta': has_meta
                                })
            except Exception as e:
                print(f'⚠️ Ошибка сканирования кастомных модов: {e}')
        
        mods.sort(key=lambda x: x['name'].lower())
        return mods

    # ============================================
    # API ДЛЯ РАБОТЫ С МОДАМИ
    # ============================================
    
    @app.route('/api/mods/cache', methods=['GET'])
    def get_mods_from_cache():
        try:
            cache = get_mods_cache()
            if cache and cache.get('mods'):
                from settings_manager import load_mods_config
                config = load_mods_config()
                
                mods = cache.get('mods')
                for mod in mods:
                    if mod['id'] in config:
                        mod['server'] = config[mod['id']].get('server', False)
                        mod['server_mod'] = config[mod['id']].get('server_mod', False)
                        mod['client'] = config[mod['id']].get('client', True)
                
                return jsonify({
                    'success': True,
                    'from_cache': True,
                    'timestamp': cache.get('timestamp'),
                    'mods': mods,
                    'stats': {
                        'total': len(mods),
                        'workshop': len([m for m in mods if m.get('type') == 'workshop']),
                        'custom': len([m for m in mods if m.get('type') == 'custom']),
                        'enabled': len([m for m in mods if m.get('enabled', True)])
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Кеш не найден'
                }), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/scan', methods=['GET'])
    def scan_mods_api():
        try:
            settings = load_settings()
            workshop = settings.get('workshop', '')
            custom_mods = settings.get('custom_mods', '')
            
            if not workshop and not custom_mods:
                return jsonify({
                    'success': False,
                    'message': 'Не указаны папки с модами в настройках'
                }), 400
            
            mods = scan_mods(workshop, custom_mods)
            
            from settings_manager import load_mods_config
            config = load_mods_config()
            for mod in mods:
                if mod['id'] in config:
                    mod['server'] = config[mod['id']].get('server', False)
                    mod['server_mod'] = config[mod['id']].get('server_mod', False)
                    mod['client'] = config[mod['id']].get('client', True)
            
            return jsonify({
                'success': True,
                'mods': mods,
                'stats': {
                    'total': len(mods),
                    'workshop': len([m for m in mods if m['type'] == 'workshop']),
                    'custom': len([m for m in mods if m['type'] == 'custom']),
                    'enabled': len([m for m in mods if m.get('enabled', True)])
                }
            })
        
        except Exception as e:
            print(f'❌ Ошибка сканирования модов: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/mods/scan-and-cache', methods=['POST'])
    def scan_and_cache_mods():
        try:
            settings = load_settings()
            workshop = settings.get('workshop', '')
            custom_mods = settings.get('custom_mods', '')
            
            if not workshop and not custom_mods:
                return jsonify({
                    'success': False,
                    'message': 'Не указаны папки с модами в настройках'
                }), 400
            
            mods = scan_mods(workshop, custom_mods)
            
            from settings_manager import init_mods_config
            
            config = init_mods_config(mods)
            
            for mod in mods:
                if mod['id'] in config:
                    mod['server'] = config[mod['id']].get('server', False)
                    mod['server_mod'] = config[mod['id']].get('server_mod', False)
                    mod['client'] = config[mod['id']].get('client', True)
            
            save_mods_cache(mods)
            
            return jsonify({
                'success': True,
                'message': f'Кеш обновлён, найдено {len(mods)} модов',
                'mods': mods,
                'stats': {
                    'total': len(mods),
                    'workshop': len([m for m in mods if m.get('type') == 'workshop']),
                    'custom': len([m for m in mods if m.get('type') == 'custom']),
                    'enabled': len([m for m in mods if m.get('enabled', True)])
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============================================
    # API ДЛЯ КОНФИГА МОДОВ
    # ============================================
    
    @app.route('/api/mods/config', methods=['GET'])
    def get_mods_config():
        try:
            from settings_manager import load_mods_config
            config = load_mods_config()
            return jsonify({
                'success': True,
                'config': config
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/config/<mod_id>', methods=['GET'])
    def get_mod_config(mod_id):
        try:
            from settings_manager import get_mod_full_state
            state = get_mod_full_state(mod_id)
            return jsonify({
                'success': True,
                'mod_id': mod_id,
                'state': state
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/config/<mod_id>/<attr>', methods=['POST'])
    def set_mod_config(mod_id, attr):
        try:
            data = request.get_json()
            value = data.get('value', False)
            
            if attr not in ['server', 'server_mod', 'client']:
                return jsonify({'success': False, 'message': 'Неверный атрибут'}), 400
            
            from settings_manager import set_mod_state
            result = set_mod_state(mod_id, attr, value)
            
            if result:
                return jsonify({
                    'success': True,
                    'mod_id': mod_id,
                    'attr': attr,
                    'value': value,
                    'message': f'{attr} = {value}'
                })
            else:
                return jsonify({'success': False, 'message': 'Ошибка сохранения'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/config/init', methods=['POST'])
    def init_mods_config_api():
        try:
            settings = load_settings()
            workshop = settings.get('workshop', '')
            custom_mods = settings.get('custom_mods', '')
            
            mods = scan_mods(workshop, custom_mods)
            
            from settings_manager import init_mods_config
            config = init_mods_config(mods)
            
            return jsonify({
                'success': True,
                'message': f'Инициализировано {len(config)} модов',
                'config': config
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/toggle', methods=['POST'])
    def toggle_mod():
        try:
            data = request.get_json()
            mod_id = data.get('mod_id')
            enabled = data.get('enabled')
            
            if not mod_id:
                return jsonify({'success': False, 'message': 'Не указан ID мода'}), 400
            
            from settings_manager import set_mod_state
            set_mod_state(mod_id, 'server_mod', enabled)
            
            return jsonify({
                'success': True,
                'message': f'Мод {"включён" if enabled else "выключен"}'
            })
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/mods/state', methods=['GET'])
    def get_mods_state():
        try:
            from settings_manager import load_mods_config
            config = load_mods_config()
            state = {}
            for mod_id, attrs in config.items():
                state[mod_id] = attrs.get('server_mod', False)
            return jsonify({'success': True, 'state': state})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    # ============================================
    # API ДЛЯ УПРАВЛЕНИЯ ССЫЛКАМИ МОДОВ СЕРВЕРА
    # ============================================
    
    @app.route('/api/server/links', methods=['GET'])
    def get_server_links():
        try:
            from server_links import load_server_links
            links = load_server_links()
            connected = {mod_id: True for mod_id in links.keys()}
            return jsonify({
                'success': True,
                'links': connected,
                'details': links
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/server/links/check', methods=['GET'])
    def check_server_links():
        try:
            from server_links import check_links_integrity, repair_links
            import threading
            
            def check_and_repair():
                try:
                    check_links_integrity()
                except Exception as e:
                    print(f'❌ Ошибка проверки ссылок: {e}')
            
            thread = threading.Thread(target=check_and_repair)
            thread.start()
            
            from server_links import load_server_links
            links = load_server_links()
            
            return jsonify({
                'success': True,
                'links': {mod_id: True for mod_id in links.keys()},
                'details': links,
                'message': 'Проверка выполнена'
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/server/mods/<mod_id>/connect', methods=['POST'])
    def connect_mod(mod_id):
        try:
            data = request.get_json()
            mod_path = data.get('mod_path')
            mod_name = data.get('mod_name')
            mod_folder = data.get('mod_folder')
            server_dir = data.get('server_dir')
            
            if not mod_path:
                return jsonify({'success': False, 'message': 'Путь к моду не указан'}), 400
            if not server_dir:
                return jsonify({'success': False, 'message': 'Путь к серверу не указан'}), 400
            
            from server_links import connect_mod_to_server
            result = connect_mod_to_server(mod_id, mod_path, mod_name, mod_folder, server_dir)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/server/mods/<mod_id>/disconnect', methods=['POST'])
    def disconnect_mod(mod_id):
        try:
            from server_links import disconnect_mod_from_server
            result = disconnect_mod_from_server(mod_id)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/server/mods/check', methods=['GET'])
    def check_mod_links():
        try:
            from server_links import check_links_integrity
            broken = check_links_integrity()
            return jsonify({
                'success': True,
                'broken': broken,
                'count': len(broken)
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    @app.route('/api/server/keys/rebuild', methods=['POST'])
    def rebuild_keys():
        try:
            settings = load_settings()
            server_exe = settings.get('server_exe', '')
            
            if not server_exe:
                return jsonify({'success': False, 'message': 'Путь к серверу не указан'}), 400
            
            server_dir = os.path.dirname(server_exe)
            if not os.path.exists(server_dir):
                return jsonify({'success': False, 'message': f'Папка сервера не найдена: {server_dir}'}), 400
            
            from server_links import get_connected_mods_list, rebuild_all_keys
            connected = get_connected_mods_list(settings)
            rebuild_all_keys(server_dir, connected)
            
            return jsonify({
                'success': True,
                'message': f'Ключи пересобраны, подключено модов: {len(connected)}'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    # ============================================
    # API ДЛЯ УПРАВЛЕНИЯ ССЫЛКАМИ МОДОВ ИГРЫ
    # ============================================

    @app.route('/api/game/links', methods=['GET'])
    def get_game_links():
        try:
            from game_links import load_game_links
            links = load_game_links()
            connected = {mod_id: True for mod_id in links.keys()}
            return jsonify({
                'success': True,
                'links': connected,
                'details': links
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/game/mods/<mod_id>/connect', methods=['POST'])
    def connect_game_mod(mod_id):
        try:
            data = request.get_json()
            mod_path = data.get('mod_path')
            mod_name = data.get('mod_name')
            mod_folder = data.get('mod_folder')
            game_dir = data.get('game_dir')
            
            if not mod_path:
                return jsonify({'success': False, 'message': 'Путь к моду не указан'}), 400
            if not game_dir:
                return jsonify({'success': False, 'message': 'Путь к игре не указан'}), 400
            
            from game_links import connect_game_mod
            result = connect_game_mod(mod_id, mod_path, mod_name, mod_folder, game_dir)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/game/mods/<mod_id>/disconnect', methods=['POST'])
    def disconnect_game_mod(mod_id):
        try:
            from game_links import disconnect_game_mod
            result = disconnect_game_mod(mod_id)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    @app.route('/api/mods/config/<mod_id>/client', methods=['POST'])
    def set_mod_client(mod_id):
        try:
            data = request.get_json()
            value = data.get('value', True)
            
            from settings_manager import set_mod_state
            result = set_mod_state(mod_id, 'client', value)
            
            if result:
                return jsonify({
                    'success': True,
                    'mod_id': mod_id,
                    'client': value,
                    'message': f'Мод отмечен как {"клиентский" if value else "не клиентский"}'
                })
            else:
                return jsonify({'success': False, 'message': 'Ошибка сохранения'}), 500
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        
    # ============================================
    # API ДЛЯ УПРАВЛЕНИЯ СЕРВЕРОМ
    # ============================================
    @app.route('/api/server/start', methods=['POST'])
    def start_server_api():
        try:
            from app import get_server
            from settings_manager import load_settings
            from server_links import load_server_links
            
            server = get_server()
            
            settings = load_settings()
            if not settings.get('server_exe') or not settings.get('server_exe').strip():
                return jsonify({
                    'success': False,
                    'message': 'Путь к серверу не указан в настройках'
                }), 400
            
            server_links = load_server_links()
            
            mods_for_server = {}
            for mod_id, link_info in server_links.items():
                if link_info.get('enabled', False):
                    mods_for_server[mod_id] = {'connected': True}
            
            success, message = server.start(mods_for_server if mods_for_server else None)
            
            return jsonify({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            print(f'❌ Ошибка запуска сервера: {e}')
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    @app.route('/api/server/stop', methods=['POST'])
    def stop_server_api():
        try:
            from app import get_server
            server = get_server()
            
            success, message = server.stop()
            
            return jsonify({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            print(f'❌ Ошибка остановки сервера: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/server/restart', methods=['POST'])
    def restart_server_api():
        try:
            from app import get_server
            from settings_manager import load_settings, load_mods_config
            
            server = get_server()
            
            settings = load_settings()
            if not settings.get('server_exe') or not settings.get('server_exe').strip():
                return jsonify({
                    'success': False,
                    'message': 'Путь к серверу не указан в настройках'
                }), 400
            
            if server.is_running():
                success, message = server.stop()
                if not success:
                    return jsonify({
                        'success': False,
                        'message': f'Ошибка остановки: {message}'
                    }), 500
            
            mods_config = load_mods_config()
            
            mods_for_server = {}
            for mod_id, attrs in mods_config.items():
                if attrs.get('server_mod', False) or attrs.get('server', False):
                    from server_links import load_server_links
                    links = load_server_links()
                    if mod_id in links:
                        mods_for_server[mod_id] = {
                            'server': attrs.get('server', False),
                            'server_mod': attrs.get('server_mod', False),
                            'connected': True
                        }
                    else:
                        mods_for_server[mod_id] = {
                            'server': attrs.get('server', False),
                            'server_mod': attrs.get('server_mod', False),
                            'connected': False
                        }
            
            success, message = server.start(mods_for_server if mods_for_server else None)
            
            return jsonify({
                'success': success,
                'message': f'Перезапуск: {message}'
            })
            
        except Exception as e:
            print(f'❌ Ошибка перезапуска сервера: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/server/status', methods=['GET'])
    def server_status_api():
        try:
            from app import get_server
            server = get_server()
            
            status = server.status()
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            print(f'❌ Ошибка получения статуса: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/server/logs', methods=['GET'])
    def server_logs_api():
        try:
            from app import get_server
            server = get_server()
            
            logs = server.get_logs()
            
            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs)
            })
            
        except Exception as e:
            print(f'❌ Ошибка получения логов: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    # ============================================
    # API ДЛЯ УПРАВЛЕНИЯ ИГРОЙ
    # ============================================
    @app.route('/api/game/start', methods=['POST'])
    def start_game_api():
        try:
            from app import get_game
            from settings_manager import load_settings
            from game_links import load_game_links
            import json
            
            game = get_game()
            
            settings = load_settings()
            if not settings.get('game_exe') or not settings.get('game_exe').strip():
                return jsonify({
                    'success': False,
                    'message': 'Путь к игре не указан в настройках'
                }), 400
            
            # Загружаем подключённые моды
            game_links = load_game_links()
            
            # Формируем конфиг для запуска
            mods_for_game = {}
            for mod_id, link_info in game_links.items():
                if link_info.get('enabled', False):
                    mods_for_game[mod_id] = {
                        'link_name': link_info.get('link_name', ''),
                        'enabled': True
                    }
            
            # Параметры подключения
            connect_ip = '127.0.0.1'
            connect_port = '2302'
            player_name = 'player'
            
            # Получаем ник из настроек
            player_name = settings.get('game_nickname', 'player')
            if not player_name or not player_name.strip():
                player_name = 'player'
            
            # Если есть JSON тело - можно переопределить
            if request.data and request.data.strip():
                try:
                    data = request.get_json(silent=True)
                    if data:
                        connect_ip = data.get('connect_ip', '127.0.0.1')
                        connect_port = data.get('connect_port', '2302')
                        if data.get('player_name'):
                            player_name = data.get('player_name')
                except:
                    pass
            
            print(f"🎮 Запуск игры с ником: '{player_name}'")
            
            success, message = game.start(
                mods_for_game if mods_for_game else None,
                connect_ip=connect_ip,
                connect_port=connect_port,
                player_name=player_name
            )
            
            return jsonify({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            print(f'❌ Ошибка запуска игры: {e}')
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    @app.route('/api/game/stop', methods=['POST'])
    def stop_game_api():
        try:
            from app import get_game
            game = get_game()
            
            success, message = game.stop()
            
            return jsonify({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            print(f'❌ Ошибка остановки игры: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/game/status', methods=['GET'])
    def game_status_api():
        try:
            from app import get_game
            game = get_game()
            
            status = game.status()
            
            return jsonify({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            print(f'❌ Ошибка получения статуса игры: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/game/logs', methods=['GET'])
    def game_logs_api():
        try:
            from app import get_game
            game = get_game()
            
            logs = game.get_logs()
            
            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs)
            })
            
        except Exception as e:
            print(f'❌ Ошибка получения логов игры: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    # ============================================
    # API ДЛЯ РАБОТЫ С НИКОМ В ИГРЕ
    # ============================================

    @app.route('/api/game/nickname', methods=['GET'])
    def get_nickname_api():
        try:
            from settings_manager import load_settings
            settings = load_settings()
            nickname = settings.get('game_nickname', 'player')
            return jsonify({
                'success': True,
                'nickname': nickname
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/api/game/nickname', methods=['POST'])
    def set_nickname_api():
        try:
            from settings_manager import load_settings, save_settings
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'Нет данных'
                }), 400
            
            nickname = data.get('nickname', '').strip()
            
            if not nickname:
                return jsonify({
                    'success': False,
                    'message': 'Ник не может быть пустым'
                }), 400
            
            # Ограничиваем длину ника (DayZ ограничение)
            if len(nickname) > 32:
                return jsonify({
                    'success': False,
                    'message': 'Ник не может быть длиннее 32 символов'
                }), 400
            
            settings = load_settings()
            settings['game_nickname'] = nickname
            save_settings(settings)
            
            return jsonify({
                'success': True,
                'message': f'Ник сохранён: {nickname}',
                'nickname': nickname
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    # ============================================
    # API ДЛЯ RPT ЛОГОВ
    # ============================================

    @app.route('/api/server/rpt-logs', methods=['GET'])
    def get_rpt_logs_api():
        """Возвращает RPT логи сервера."""
        try:
            from app import get_server
            server = get_server()
            
            logs = server.get_rpt_logs()
            
            return jsonify({
                'success': True,
                'logs': logs,
                'count': len(logs)
            })
        except Exception as e:
            print(f'❌ Ошибка получения RPT логов: {e}')
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    # ============================================
    # API ДЛЯ СТАТУСА RPT МОНИТОРА
    # ============================================

    @app.route('/api/server/rpt-status', methods=['GET'])
    def get_rpt_status_api():
        """Возвращает статус RPT монитора."""
        try:
            from app import get_server
            server = get_server()
            
            # Проверяем, активен ли RPT монитор
            is_monitoring = False
            if hasattr(server, 'rpt_monitor') and server.rpt_monitor:
                is_monitoring = server.rpt_monitor.is_running()
            
            return jsonify({
                'success': True,
                'monitoring': is_monitoring,
                'profiles_dir': getattr(server, 'profiles_dir', '')
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
        
    # ============================================
    # API ДЛЯ РАБОТЫ С ИГРОКАМИ (только счётчик)
    # ============================================

    @app.route('/api/players/current', methods=['GET'])
    def get_current_players():
        """Возвращает количество игроков онлайн."""
        try:
            from app import get_server
            server = get_server()
            
            if hasattr(server, 'rpt_monitor') and server.rpt_monitor:
                online_count = server.rpt_monitor.get_online_count()
                return jsonify({
                    'success': True,
                    'players': [],  # Пустой список
                    'online_count': online_count
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'RPT монитор не активен'
                }), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
