// ============================================
// УПРАВЛЕНИЕ СЕРВЕРОМ - СПИСОК СЕРВЕРНЫХ МОДОВ
// ============================================

let serverModsList = [];
let serverLinks = {};
let isPageVisible = true;

// ============================================
// ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ СЕРВЕРА
// ============================================
async function initServerPage() {
    console.log('🖥️ Инициализация страницы сервера');
    
    // Загружаем подключения и моды
    await loadServerLinks();
    await loadServerMods();
    
    // Запускаем автообновление
    startAutoRefresh();
}

// ============================================
// АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ
// ============================================
let refreshInterval = null;

function startAutoRefresh() {
    // Останавливаем старый интервал если был
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
    
    // Запускаем обновление каждые 10 секунд (только если страница видима)
    refreshInterval = setInterval(async () => {
        if (isPageVisible) {
            await refreshServerData();
        }
    }, 10000);
    
    console.log('🔄 Автообновление запущено (каждые 10 сек)');
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        console.log('🔄 Автообновление остановлено');
    }
}

// Отслеживаем видимость страницы
document.addEventListener('visibilitychange', () => {
    isPageVisible = !document.hidden;
});

// ============================================
// ОБНОВЛЕНИЕ ДАННЫХ (без перерисовки всей страницы)
// ============================================
async function refreshServerData() {
    try {
        // Загружаем свежие подключения
        await loadServerLinks();
        
        // Обновляем статус подключения у каждого мода
        let updated = false;
        serverModsList.forEach(mod => {
            const newState = serverLinks[mod.id] === true;
            if (mod.is_connected !== newState) {
                mod.is_connected = newState;
                updated = true;
            }
        });
        
        // Если были изменения - перерисовываем
        if (updated) {
            console.log('🔄 Обнаружены изменения, обновляем список');
            renderServerMods(serverModsList);
        }
    } catch (e) {
        console.warn('⚠️ Ошибка автообновления:', e);
    }
}

// ============================================
// ЗАГРУЗКА ПОДКЛЮЧЕННЫХ МОДОВ
// ============================================
async function loadServerLinks() {
    try {
        const response = await fetch('/api/server/links');
        const data = await response.json();
        if (data.success) {
            serverLinks = data.links || {};
            console.log(`🔗 Загружено ${Object.keys(serverLinks).length} подключенных модов`);
            return true;
        }
        return false;
    } catch (e) {
        console.warn('⚠️ Не удалось загрузить список подключений:', e);
        return false;
    }
}

// ============================================
// ЗАГРУЗКА СЕРВЕРНЫХ МОДОВ ИЗ КОНФИГА
// ============================================
async function loadServerMods() {
    const container = document.getElementById('serverModsContainer');
    if (!container) {
        console.warn('Контейнер serverModsContainer не найден');
        return;
    }

    try {
        // Сначала загружаем КЕШ модов
        let modsList = [];
        let modsConfig = {};
        
        try {
            const cacheResponse = await fetch('/api/mods/cache');
            const cacheData = await cacheResponse.json();
            if (cacheData.success && cacheData.mods) {
                modsList = cacheData.mods;
            }
        } catch (e) {
            console.warn('⚠️ Не удалось загрузить кеш модов:', e);
        }

        // Загружаем конфиг модов
        const response = await fetch('/api/mods/config');
        const data = await response.json();
        
        if (!data.success) {
            container.innerHTML = `
                <div class="empty-mods">
                    <p>❌ Ошибка загрузки конфига</p>
                </div>
            `;
            return;
        }

        modsConfig = data.config;
        
        const serverMods = [];
        for (const [modId, attrs] of Object.entries(modsConfig)) {
            if (attrs.server_mod === true) {
                const modInfo = modsList.find(m => m.id === modId);
                
                if (modInfo) {
                    serverMods.push({
                        id: modId,
                        name: modInfo.name || modId,
                        folder: modInfo.folder || modId,
                        path: modInfo.path || '',
                        version: modInfo.version || 'Неизвестно',
                        type: modInfo.type || 'unknown',
                        is_connected: serverLinks[modId] === true
                    });
                } else {
                    serverMods.push({
                        id: modId,
                        name: modId,
                        folder: modId,
                        path: '',
                        version: 'Неизвестно',
                        type: 'unknown',
                        is_connected: serverLinks[modId] === true
                    });
                }
            }
        }

        serverModsList = serverMods;
        renderServerMods(serverMods);

    } catch (e) {
        console.error('❌ Ошибка загрузки серверных модов:', e);
        container.innerHTML = `
            <div class="empty-mods">
                <p>❌ Ошибка: ${e.message}</p>
            </div>
        `;
    }
}

// ============================================
// ОТРИСОВКА СПИСКА СЕРВЕРНЫХ МОДОВ
// ============================================
function renderServerMods(mods) {
    const container = document.getElementById('serverModsContainer');
    if (!container) return;

    const searchInput = document.getElementById('serverModsSearchInput');
    const searchValue = searchInput?.value?.toLowerCase() || '';

    let filtered = mods;
    if (searchValue) {
        filtered = mods.filter(m => 
            m.name.toLowerCase().includes(searchValue) || 
            m.folder.toLowerCase().includes(searchValue)
        );
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-mods">
                <p>📭 Серверных модов не найдено</p>
                ${mods.length === 0 ? '<p class="empty-hint">Отметьте моды как "СерверМод" в разделе "Управление модами"</p>' : ''}
                ${searchValue ? '<p class="empty-hint">Попробуйте изменить поиск</p>' : ''}
            </div>
        `;
        return;
    }

    let html = '';
    filtered.forEach(mod => {
        const escapedPath = mod.path.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        const isConnected = mod.is_connected || false;
        
        html += `
            <div class="server-mod-item" data-mod-id="${mod.id}">
                <div class="server-mod-info">
                    <div class="server-mod-name">
                        ${mod.name}
                        ${mod.type === 'workshop' ? '🛠️' : mod.type === 'custom' ? '📁' : '❓'}
                        ${isConnected ? '<span class="mod-connected-badge">🔗 Подключен</span>' : ''}
                    </div>
                    <div class="server-mod-details">
                        <span class="server-mod-folder">${mod.folder}</span>
                        <span class="server-mod-version">v${mod.version}</span>
                        <span class="server-mod-type ${mod.type}">${mod.type === 'workshop' ? 'Workshop' : mod.type === 'custom' ? 'Кастомный' : 'Неизвестно'}</span>
                    </div>
                </div>
                <div class="server-mod-actions">
                    <button class="btn btn-connect-mod ${isConnected ? 'connected' : ''}" 
                            onclick="toggleModConnection('${mod.id}')" 
                            title="${isConnected ? 'Отключить мод от сервера' : 'Подключить мод к серверу'}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            ${isConnected ? 
                                '<path d="M18 6L6 18"/><path d="M6 6l12 12"/>' :
                                '<path d="M12 5v14"/><path d="M5 12h14"/>'
                            }
                        </svg>
                        ${isConnected ? 'Отключить' : 'Подключить'}
                    </button>
                    
                    <button class="btn-mod-folder" onclick="openModFolder('${escapedPath}')" title="Открыть папку мода" ${!mod.path ? 'disabled style="opacity:0.3;cursor:not-allowed;"' : ''}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22,19a2,2,0,0,1-2,2H4a2,2,0,0,1-2-2V5A2,2,0,0,1,4,3H9l2,3h9a2,2,0,0,1,2,2Z"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// ============================================
// ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ МОДА К СЕРВЕРУ
// ============================================
async function toggleModConnection(modId) {
    console.log(`🔌 Переключение подключения мода: ${modId}`);
    
    const mod = serverModsList.find(m => m.id === modId);
    if (!mod) {
        if (typeof notifications !== 'undefined') {
            notifications.error('Мод не найден');
        }
        return;
    }

    if (!mod.path) {
        if (typeof notifications !== 'undefined') {
            notifications.error('Путь к моду не найден');
        }
        return;
    }

    try {
        const settingsResponse = await fetch('/api/settings');
        const settings = await settingsResponse.json();
        
        if (!settings.server_exe || !settings.server_exe.trim()) {
            if (typeof notifications !== 'undefined') {
                notifications.warning('Сначала укажите путь к серверу в настройках');
            }
            return;
        }

        const serverDir = getServerDirectory(settings.server_exe);
        if (!serverDir) {
            if (typeof notifications !== 'undefined') {
                notifications.error('Не удалось определить папку сервера');
            }
            return;
        }

        const isConnected = serverLinks[modId] === true;
        
        // Отключаем кнопку
        const btn = document.querySelector(`.server-mod-item[data-mod-id="${modId}"] .btn-connect-mod`);
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ ...';
        }

        if (isConnected) {
            // Отключаем
            const response = await fetch(`/api/server/mods/${modId}/disconnect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const data = await response.json();
            
            if (data.success) {
                delete serverLinks[modId];
                mod.is_connected = false;
                if (typeof notifications !== 'undefined') {
                    notifications.success(`Мод "${mod.name}" отключён`);
                }
            } else {
                if (typeof notifications !== 'undefined') {
                    notifications.error(data.message || 'Ошибка');
                }
            }
        } else {
            // Подключаем
            const response = await fetch(`/api/server/mods/${modId}/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mod_path: mod.path,
                    mod_name: mod.name,
                    mod_folder: mod.folder,
                    server_dir: serverDir
                })
            });
            const data = await response.json();
            
            if (data.success) {
                serverLinks[modId] = true;
                mod.is_connected = true;
                if (typeof notifications !== 'undefined') {
                    notifications.success(`Мод "${mod.name}" подключён`);
                }
            } else {
                if (typeof notifications !== 'undefined') {
                    notifications.error(data.message || 'Ошибка');
                }
            }
        }
        
        // Обновляем список
        renderServerMods(serverModsList);
        
    } catch (e) {
        console.error('❌ Ошибка:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
        renderServerMods(serverModsList);
    }
}
// ============================================
// ПОЛУЧИТЬ ПАПКУ СЕРВЕРА ИЗ ПУТИ К EXE
// ============================================
function getServerDirectory(exePath) {
    if (!exePath) return null;
    const normalized = exePath.replace(/\\/g, '/');
    const lastSlash = normalized.lastIndexOf('/');
    if (lastSlash === -1) return null;
    return normalized.substring(0, lastSlash);
}

// ============================================
// ПОИСК СЕРВЕРНЫХ МОДОВ
// ============================================
function setupServerModsSearch() {
    const searchInput = document.getElementById('serverModsSearchInput');
    if (searchInput) {
        const newInput = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newInput, searchInput);
        
        newInput.addEventListener('input', () => {
            renderServerMods(serverModsList);
        });
    }
}

// ============================================
// ОБНОВЛЕНИЕ СПИСКА (кнопка)
// ============================================
async function refreshServerMods() {
    const btn = document.getElementById('refreshServerModsBtn');
    if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
    }
    
    // Загружаем актуальные подключения и моды
    await loadServerLinks();
    await loadServerMods();
    
    if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
    
    if (typeof notifications !== 'undefined') {
        notifications.success('Список серверных модов обновлён');
    }
}

// ============================================
// ОСТАНОВКА АВТООБНОВЛЕНИЯ ПРИ УХОДЕ СО СТРАНИЦЫ
// ============================================
// Вызывается из script.js при переключении страниц
function destroyServerPage() {
    stopAutoRefresh();
    console.log('🖥️ Страница сервера уничтожена');
}

// ============================================
// ЭКСПОРТ ФУНКЦИЙ
// ============================================
window.initServerPage = initServerPage;
window.loadServerMods = loadServerMods;
window.renderServerMods = renderServerMods;
window.refreshServerMods = refreshServerMods;
window.setupServerModsSearch = setupServerModsSearch;
window.toggleModConnection = toggleModConnection;
window.loadServerLinks = loadServerLinks;
window.destroyServerPage = destroyServerPage;
window.startAutoRefresh = startAutoRefresh;
window.stopAutoRefresh = stopAutoRefresh;

console.log('🖥️ server.js загружен');