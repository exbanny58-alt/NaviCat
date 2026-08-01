// ============================================
// НАСТРОЙКИ С ИСПОЛЬЗОВАНИЕМ НОВОЙ СИСТЕМЫ УВЕДОМЛЕНИЙ
// ============================================

// Загрузка сохранённых путей из сервера
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        const fields = ['server_exe', 'game_exe', 'workshop', 'custom_mods'];
        const inputIds = ['server-exe-path', 'game-exe-path', 'workshop-path', 'custom-mods-path'];
        
        fields.forEach((field, i) => {
            const input = document.getElementById(inputIds[i]);
            // Проверяем существование элемента
            if (input) {
                if (data[field] && data[field].trim()) {
                    input.value = data[field];
                } else {
                    input.value = '';
                }
            }
        });
    } catch (e) {
        console.error('Ошибка загрузки настроек:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка загрузки настроек');
        }
    }
}

// Сохранение одного поля на сервер
async function saveField(field, inputId, statusId) {
    const input = document.getElementById(inputId);
    if (!input) {
        console.error('Элемент не найден:', inputId);
        return;
    }
    
    const value = input.value.trim();
    if (!value) {
        const statusEl = document.getElementById(statusId);
        if (statusEl) {
            statusEl.textContent = 'Укажите путь';
            statusEl.style.color = '#f87171';
        }
        if (typeof notifications !== 'undefined') {
            notifications.warning('Укажите путь перед сохранением');
        }
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 2000);
        return;
    }
    
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        settings[field] = value;
        
        const saveResponse = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const result = await saveResponse.json();
        
        const statusEl = document.getElementById(statusId);
        if (result.success) {
            if (statusEl) {
                statusEl.textContent = '✓ Сохранено';
                statusEl.style.color = '#4ade80';
            }
            if (typeof notifications !== 'undefined') {
                notifications.success('Настройки сохранены успешно');
            }
        } else {
            if (statusEl) {
                statusEl.textContent = '❌ Ошибка';
                statusEl.style.color = '#f87171';
            }
            if (typeof notifications !== 'undefined') {
                notifications.error('Ошибка сохранения настроек');
            }
        }
        
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 2000);
    } catch (e) {
        const statusEl = document.getElementById(statusId);
        if (statusEl) {
            statusEl.textContent = '❌ Ошибка';
            statusEl.style.color = '#f87171';
        }
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка сохранения: ' + e.message);
        }
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 2000);
    }
}

// Сброс одного поля
async function resetField(field, inputId, statusId) {
    try {
        const response = await fetch(`/api/settings/reset/${field}`, {
            method: 'POST',
        });
        
        const result = await response.json();
        const statusEl = document.getElementById(statusId);
        const input = document.getElementById(inputId);
        
        if (result.success) {
            if (input) input.value = '';
            if (statusEl) {
                statusEl.textContent = '✓ Сброшено';
                statusEl.style.color = '#4ade80';
            }
            if (typeof notifications !== 'undefined') {
                notifications.success('Поле сброшено');
            }
        } else {
            if (statusEl) {
                statusEl.textContent = '❌ Ошибка';
                statusEl.style.color = '#f87171';
            }
            if (typeof notifications !== 'undefined') {
                notifications.error('Ошибка сброса');
            }
        }
        
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 2000);
    } catch (e) {
        const statusEl = document.getElementById(statusId);
        if (statusEl) {
            statusEl.textContent = '❌ Ошибка';
            statusEl.style.color = '#f87171';
        }
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 2000);
    }
}

// Открытие проводника через сервер
async function browseFile(inputId, type = 'file') {
    const btn = document.querySelector(`[data-target="${inputId}"]`);
    const field = btn?.dataset.field;
    if (!field) {
        console.error('Не найден field для inputId:', inputId);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: не найден параметр');
        }
        return;
    }
    
    // Показываем, что процесс начался
    const statusId = `status-${field}`;
    const statusEl = document.getElementById(statusId);
    if (statusEl) {
        statusEl.textContent = '⏳ Открывается диалог...';
        statusEl.style.color = '#60a5fa';
    }
    if (typeof notifications !== 'undefined') {
        notifications.info('Открывается диалог выбора...');
    }
    
    try {
        const endpoint = type === 'folder' ? '/api/browse/folder' : '/api/browse/file';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                field: field,
                inputId: inputId
            })
        });
        
        const result = await response.json();
        
        if (result.success && result.path) {
            const input = document.getElementById(inputId);
            if (input) {
                input.value = result.path;
            }
            
            // Автоматически сохраняем после выбора
            await saveField(field, inputId, statusId);
            
            if (typeof notifications !== 'undefined') {
                notifications.success('Путь выбран и сохранён');
            }
        } else if (!result.success) {
            if (statusEl) {
                statusEl.textContent = '❌ ' + (result.message || 'Ошибка выбора');
                statusEl.style.color = '#f87171';
            }
            if (typeof notifications !== 'undefined') {
                notifications.error(result.message || 'Ошибка выбора');
            }
            setTimeout(() => {
                if (statusEl) {
                    statusEl.textContent = '';
                }
            }, 3000);
        }
    } catch (e) {
        console.error('Ошибка открытия проводника:', e);
        if (statusEl) {
            statusEl.textContent = '❌ Ошибка: ' + e.message;
            statusEl.style.color = '#f87171';
        }
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
        setTimeout(() => {
            if (statusEl) {
                statusEl.textContent = '';
            }
        }, 3000);
    }
}

// Открыть выбранную папку в проводнике
async function openInExplorer(inputId) {
    const input = document.getElementById(inputId);
    if (!input) {
        if (typeof notifications !== 'undefined') {
            notifications.warning('Элемент не найден');
        }
        return;
    }
    
    const path = input.value.trim();
    
    if (!path) {
        if (typeof notifications !== 'undefined') {
            notifications.warning('Сначала выберите путь');
        }
        return;
    }
    
    try {
        const response = await fetch('/api/open/explorer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: path })
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (typeof notifications !== 'undefined') {
                notifications.success(result.message);
            }
        } else {
            if (typeof notifications !== 'undefined') {
                notifications.error(result.message);
            }
        }
    } catch (e) {
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
}

// Функция для прикрепления обработчиков (вызывается из script.js)
function attachSettingsHandlers() {
    document.querySelectorAll('.save-single-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const field = this.dataset.field;
            const target = this.dataset.target;
            const statusId = `status-${field}`;
            saveField(field, target, statusId);
        });
    });
    
    document.querySelectorAll('.reset-single-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const field = this.dataset.field;
            const target = this.dataset.target;
            const statusId = `status-${field}`;
            resetField(field, target, statusId);
        });
    });
    
    document.querySelectorAll('.browse-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.target;
            const type = this.dataset.type || 'file';
            browseFile(target, type);
        });
    });
    
    document.querySelectorAll('.open-explorer-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.target;
            openInExplorer(target);
        });
    });
}

// Экспортируем для использования в script.js
window.loadSettings = loadSettings;
window.attachSettingsHandlers = attachSettingsHandlers;
window.saveField = saveField;
window.resetField = resetField;
window.browseFile = browseFile;
window.openInExplorer = openInExplorer;