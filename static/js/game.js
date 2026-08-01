// ============================================
// УПРАВЛЕНИЕ ИГРОЙ - СПИСОК КЛИЕНТСКИХ МОДОВ
// ============================================

let clientModsList = [];
let gameLinks = {};
let isGamePageVisible = true;
let gameRefreshInterval = null;

// ============================================
// ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ ИГРЫ
// ============================================
async function initGamePage() {
    console.log('🎮 Инициализация страницы игры');
    await loadGameLinks();
    await loadClientMods();
    await loadNickname();  // ← ДОБАВЛЯЕМ
    startGameAutoRefresh();
    
    // Обработчик кнопки подключения всех модов
    const connectAllBtn = document.getElementById('connectAllGameModsBtn');
    if (connectAllBtn) {
        const newBtn = connectAllBtn.cloneNode(true);
        connectAllBtn.parentNode.replaceChild(newBtn, connectAllBtn);
        newBtn.addEventListener('click', connectAllServerMods);
    }
    
    // Обработчик кнопки смены ника ← НОВЫЙ
    const nicknameBtn = document.getElementById('changeNicknameBtn');
    if (nicknameBtn) {
        const newBtn = nicknameBtn.cloneNode(true);
        nicknameBtn.parentNode.replaceChild(newBtn, nicknameBtn);
        newBtn.addEventListener('click', showNicknameModal);
    }
}

// ============================================
// АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ
// ============================================
function startGameAutoRefresh() {
    if (gameRefreshInterval) {
        clearInterval(gameRefreshInterval);
        gameRefreshInterval = null;
    }
    
    gameRefreshInterval = setInterval(async () => {
        if (isGamePageVisible) {
            await refreshGameData();
        }
    }, 10000);
    
    console.log('🔄 Автообновление игры запущено (каждые 10 сек)');
}

function stopGameAutoRefresh() {
    if (gameRefreshInterval) {
        clearInterval(gameRefreshInterval);
        gameRefreshInterval = null;
        console.log('🔄 Автообновление игры остановлено');
    }
}

document.addEventListener('visibilitychange', () => {
    isGamePageVisible = !document.hidden;
});

async function refreshGameData() {
    try {
        await loadGameLinks();
        await loadClientMods();
    } catch (e) {
        console.warn('⚠️ Ошибка автообновления игры:', e);
    }
}

// ============================================
// ЗАГРУЗКА ПОДКЛЮЧЕННЫХ МОДОВ ИГРЫ
// ============================================
async function loadGameLinks() {
    try {
        const response = await fetch('/api/game/links');
        const data = await response.json();
        if (data.success) {
            gameLinks = data.links || {};
            console.log(`🔗 Загружено ${Object.keys(gameLinks).length} подключенных модов игры`);
            return true;
        }
        return false;
    } catch (e) {
        console.warn('⚠️ Не удалось загрузить список подключений игры:', e);
        return false;
    }
}

// ============================================
// ЗАГРУЗКА КЛИЕНТСКИХ МОДОВ ИЗ КОНФИГА
// ============================================
async function loadClientMods() {
    const container = document.getElementById('gameModsContainer');
    if (!container) {
        console.warn('Контейнер gameModsContainer не найден');
        return;
    }

    try {
        await loadGameLinks();
        
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
        
        const clientMods = [];
        for (const [modId, attrs] of Object.entries(modsConfig)) {
            // Показываем ВСЕ моды, у которых client = true
            // ИЛИ которые уже подключены к игре (gameLinks)
            if (attrs.client === true || gameLinks[modId] === true) {
                const modInfo = modsList.find(m => m.id === modId);
                const isConnected = gameLinks[modId] === true;
                
                if (modInfo) {
                    clientMods.push({
                        id: modId,
                        name: modInfo.name || modId,
                        folder: modInfo.folder || modId,
                        path: modInfo.path || '',
                        version: modInfo.version || 'Неизвестно',
                        type: modInfo.type || 'unknown',
                        is_connected: isConnected,
                        is_client: attrs.client === true
                    });
                } else {
                    clientMods.push({
                        id: modId,
                        name: modId,
                        folder: modId,
                        path: '',
                        version: 'Неизвестно',
                        type: 'unknown',
                        is_connected: isConnected,
                        is_client: attrs.client === true
                    });
                }
            }
        }

        clientModsList = clientMods;
        console.log(`📋 Загружено ${clientModsList.length} клиентских модов`);
        renderClientMods(clientModsList);

    } catch (e) {
        console.error('❌ Ошибка загрузки клиентских модов:', e);
        container.innerHTML = `
            <div class="empty-mods">
                <p>❌ Ошибка: ${e.message}</p>
            </div>
        `;
    }
}

// ============================================
// ОТРИСОВКА СПИСКА КЛИЕНТСКИХ МОДОВ
// ============================================
function renderClientMods(mods) {
    const container = document.getElementById('gameModsContainer');
    if (!container) return;

    const searchInput = document.getElementById('gameModsSearchInput');
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
                <p>📭 Клиентских модов не найдено</p>
                ${searchValue ? '<p class="empty-hint">Попробуйте изменить поиск</p>' : ''}
                <p class="empty-hint">Нажмите "Подключить все моды сервера" чтобы автоматически добавить их</p>
            </div>
        `;
        return;
    }

    let html = '';
    filtered.forEach(mod => {
        const escapedPath = mod.path.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        const isConnected = mod.is_connected || false;
        
        html += `
            <div class="game-mod-item" data-mod-id="${mod.id}">
                <div class="game-mod-info">
                    <div class="game-mod-name">
                        ${mod.name}
                        ${mod.type === 'workshop' ? '🛠️' : mod.type === 'custom' ? '📁' : '❓'}
                        ${isConnected ? '<span class="mod-connected-badge">🔗 Подключен</span>' : ''}
                        ${!mod.is_client && isConnected ? '<span class="mod-warning-badge">⚠️ Не отмечен как клиентский</span>' : ''}
                    </div>
                    <div class="game-mod-details">
                        <span class="game-mod-folder">${mod.folder}</span>
                        <span class="game-mod-version">v${mod.version}</span>
                        <span class="game-mod-type ${mod.type}">${mod.type === 'workshop' ? 'Workshop' : mod.type === 'custom' ? 'Кастомный' : 'Неизвестно'}</span>
                    </div>
                </div>
                <div class="game-mod-actions">
                    <button class="btn btn-connect-mod ${isConnected ? 'connected' : ''}" 
                            onclick="toggleGameModConnection('${mod.id}')" 
                            title="${isConnected ? 'Отключить мод от игры' : 'Подключить мод к игре'}">
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
// ПОДКЛЮЧИТЬ ВСЕ МОДЫ СЕРВЕРА
// ============================================
async function connectAllServerMods() {
    console.log('🎮 Подключение всех модов сервера...');
    
    const btn = document.getElementById('connectAllGameModsBtn');
    if (btn) {
        btn.disabled = true;
        btn.classList.add('loading');
        btn.textContent = '⏳ Подключение...';
    }

    try {
        const settingsResponse = await fetch('/api/settings');
        const settings = await settingsResponse.json();
        
        if (!settings.game_exe || !settings.game_exe.trim()) {
            if (typeof notifications !== 'undefined') {
                notifications.warning('Сначала укажите путь к игре в настройках');
            }
            restoreButton(btn);
            return;
        }

        const gameDir = getGameDirectory(settings.game_exe);
        if (!gameDir) {
            if (typeof notifications !== 'undefined') {
                notifications.error('Не удалось определить папку игры');
            }
            restoreButton(btn);
            return;
        }

        // Получаем конфиг модов
        const modsConfigResponse = await fetch('/api/mods/config');
        const modsConfigData = await modsConfigResponse.json();
        
        if (!modsConfigData.success) {
            if (typeof notifications !== 'undefined') {
                notifications.error('Ошибка загрузки конфига модов');
            }
            restoreButton(btn);
            return;
        }

        // Получаем список серверных модов
        const serverModsConfig = modsConfigData.config;
        const serverModIds = Object.keys(serverModsConfig).filter(
            modId => serverModsConfig[modId].server_mod === true
        );

        if (serverModIds.length === 0) {
            if (typeof notifications !== 'undefined') {
                notifications.warning('Нет модов с пометкой "СерверМод"');
            }
            restoreButton(btn);
            return;
        }

        // Получаем кеш модов
        const cacheResponse = await fetch('/api/mods/cache');
        const cacheData = await cacheResponse.json();
        const modsList = cacheData.success ? cacheData.mods : [];

        // Обновляем gameLinks
        await loadGameLinks();

        let connectedCount = 0;
        let skippedCount = 0;
        let errorCount = 0;
        let markedAsClient = 0;
        let total = serverModIds.length;

        if (typeof notifications !== 'undefined') {
            notifications.info(`Обработка ${total} модов...`);
        }

        for (const modId of serverModIds) {
            // Проверяем, отмечен ли мод как клиентский
            const modConfig = modsConfigData.config[modId];
            if (!modConfig || modConfig.client !== true) {
                // Отмечаем мод как клиентский
                try {
                    const markResponse = await fetch(`/api/mods/config/${modId}/client`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ value: true })
                    });
                    const markData = await markResponse.json();
                    if (markData.success) {
                        markedAsClient++;
                        console.log(`✅ Мод ${modId} отмечен как клиентский`);
                    }
                } catch (e) {
                    console.warn(`⚠️ Не удалось отметить мод ${modId} как клиентский:`, e);
                }
            }

            // Проверяем, уже подключен ли мод
            if (gameLinks[modId] === true) {
                skippedCount++;
                continue;
            }

            const modInfo = modsList.find(m => m.id === modId);
            if (!modInfo || !modInfo.path || !modInfo.folder) {
                errorCount++;
                console.warn(`⚠️ Не найдена информация о моде: ${modId}`);
                continue;
            }

            try {
                const response = await fetch(`/api/game/mods/${modId}/connect`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        mod_path: modInfo.path,
                        mod_name: modInfo.name || modId,
                        mod_folder: modInfo.folder,
                        game_dir: gameDir
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    gameLinks[modId] = true;
                    connectedCount++;
                    console.log(`✅ Подключен: ${modInfo.name}`);
                } else {
                    errorCount++;
                    console.error(`❌ Ошибка подключения ${modInfo.name}: ${data.message}`);
                }
            } catch (e) {
                errorCount++;
                console.error(`❌ Ошибка подключения ${modId}: ${e.message}`);
            }
        }

        // Принудительно перезагружаем список
        console.log('🔄 Принудительное обновление списка...');
        await loadGameLinks();
        await loadClientMods();

        let message = `✅ Подключено: ${connectedCount}`;
        if (skippedCount > 0) message += `, уже подключены: ${skippedCount}`;
        if (markedAsClient > 0) message += `, отмечено как клиентские: ${markedAsClient}`;
        if (errorCount > 0) message += `, ошибок: ${errorCount}`;
        
        if (typeof notifications !== 'undefined') {
            if (errorCount === 0 && connectedCount > 0) {
                notifications.success(message);
            } else if (connectedCount === 0 && skippedCount > 0 && errorCount === 0) {
                notifications.info(`Все моды уже подключены (${skippedCount})`);
            } else if (errorCount > 0) {
                notifications.warning(message);
            } else {
                notifications.info('Нет модов для подключения');
            }
        }

    } catch (e) {
        console.error('❌ Ошибка:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }

    restoreButton(btn);
}

function restoreButton(btn) {
    if (btn) {
        btn.disabled = false;
        btn.classList.remove('loading');
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5v14"/>
                <path d="M5 12h14"/>
            </svg>
            Подключить все моды сервера
        `;
    }
}

// ============================================
// ПОЛУЧИТЬ ПАПКУ ИГРЫ ИЗ ПУТИ К EXE
// ============================================
function getGameDirectory(exePath) {
    if (!exePath) return null;
    const normalized = exePath.replace(/\\/g, '/');
    const lastSlash = normalized.lastIndexOf('/');
    if (lastSlash === -1) return null;
    return normalized.substring(0, lastSlash);
}

// ============================================
// ПОИСК КЛИЕНТСКИХ МОДОВ
// ============================================
function setupGameModsSearch() {
    const searchInput = document.getElementById('gameModsSearchInput');
    if (searchInput) {
        const newInput = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newInput, searchInput);
        
        newInput.addEventListener('input', () => {
            renderClientMods(clientModsList);
        });
    }
}

// ============================================
// ОБНОВЛЕНИЕ СПИСКА (кнопка)
// ============================================
async function refreshGameMods() {
    const btn = document.getElementById('refreshGameModsBtn');
    if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
    }
    
    console.log('🔄 Принудительное обновление списка...');
    await loadGameLinks();
    await loadClientMods();
    
    if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
    
    if (typeof notifications !== 'undefined') {
        notifications.success('Список клиентских модов обновлён');
    }
}

// ============================================
// ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ МОДА К ИГРЕ
// ============================================
async function toggleGameModConnection(modId) {
    console.log(`🎮 Переключение подключения мода к игре: ${modId}`);
    
    const mod = clientModsList.find(m => m.id === modId);
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
        
        if (!settings.game_exe || !settings.game_exe.trim()) {
            if (typeof notifications !== 'undefined') {
                notifications.warning('Сначала укажите путь к игре в настройках');
            }
            return;
        }

        const gameDir = getGameDirectory(settings.game_exe);
        if (!gameDir) {
            if (typeof notifications !== 'undefined') {
                notifications.error('Не удалось определить папку игры');
            }
            return;
        }

        const isConnected = gameLinks[modId] === true;
        
        const btn = document.querySelector(`.game-mod-item[data-mod-id="${modId}"] .btn-connect-mod`);
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ ...';
        }

        if (isConnected) {
            const response = await fetch(`/api/game/mods/${modId}/disconnect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const data = await response.json();
            
            if (data.success) {
                delete gameLinks[modId];
                mod.is_connected = false;
                if (typeof notifications !== 'undefined') {
                    notifications.success(`Мод "${mod.name}" отключён от игры`);
                }
            } else {
                if (typeof notifications !== 'undefined') {
                    notifications.error(data.message || 'Ошибка');
                }
            }
        } else {
            const response = await fetch(`/api/game/mods/${modId}/connect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mod_path: mod.path,
                    mod_name: mod.name,
                    mod_folder: mod.folder,
                    game_dir: gameDir
                })
            });
            const data = await response.json();
            
            if (data.success) {
                gameLinks[modId] = true;
                mod.is_connected = true;
                if (typeof notifications !== 'undefined') {
                    notifications.success(`Мод "${mod.name}" подключён к игре`);
                }
            } else {
                if (typeof notifications !== 'undefined') {
                    notifications.error(data.message || 'Ошибка');
                }
            }
        }
        
        renderClientMods(clientModsList);
        
    } catch (e) {
        console.error('❌ Ошибка:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
        renderClientMods(clientModsList);
    }
}

// ============================================
// СМЕНА НИКА В ИГРЕ
// ============================================

// Загрузить текущий ник из настроек
async function loadNickname() {
    try {
        const response = await fetch('/api/game/nickname');
        const data = await response.json();
        console.log('🔍 Загружен ник:', data);  // ← ОТЛАДКА
        if (data.success) {
            const display = document.getElementById('currentNicknameDisplay');
            if (display) {
                display.textContent = data.nickname || 'player';
            }
            return data.nickname || 'player';
        }
        return 'player';
    } catch (e) {
        console.warn('⚠️ Не удалось загрузить ник:', e);
        return 'player';
    }
}

// Показать модальное окно для смены ника
function showNicknameModal() {
    // Удаляем старое окно если есть
    const oldModal = document.getElementById('nicknameModal');
    if (oldModal) {
        oldModal.remove();
    }

    // Загружаем текущий ник
    fetch('/api/game/nickname')
        .then(r => r.json())
        .then(data => {
            const currentNick = data.success ? data.nickname : 'player';
            createNicknameModal(currentNick);
        })
        .catch(() => {
            createNicknameModal('player');
        });
}

// Создать модальное окно
function createNicknameModal(currentNick) {
    const modal = document.createElement('div');
    modal.id = 'nicknameModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content modal-nickname">
            <div class="modal-header">
                <h3>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                    Смена ника
                </h3>
                <button class="modal-close" onclick="closeNicknameModal()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <div class="modal-body">
                <p class="modal-hint">Введите ник, который будет использоваться при запуске игры</p>
                <div class="modal-input-group">
                    <label for="nicknameInput">Ваш ник:</label>
                    <input type="text" id="nicknameInput" class="modal-input" 
                           value="${currentNick}" 
                           placeholder="Введите ник..." 
                           maxlength="32"
                           autofocus>
                    <span class="modal-char-count">${currentNick.length}/32</span>
                </div>
                <div class="modal-errors" id="nicknameErrors" style="display:none;"></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeNicknameModal()">Отмена</button>
                <button class="btn btn-primary" id="saveNicknameBtn" onclick="saveNickname()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                        <polyline points="17 21 17 13 7 13 7 21"/>
                        <polyline points="7 3 7 8 15 8"/>
                    </svg>
                    Сохранить
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Анимация появления
    requestAnimationFrame(() => {
        modal.classList.add('show');
        const input = document.getElementById('nicknameInput');
        if (input) {
            input.focus();
            input.select();
            // Счётчик символов
            input.addEventListener('input', function() {
                const count = document.querySelector('.modal-char-count');
                if (count) {
                    count.textContent = `${this.value.length}/32`;
                }
                // Скрываем ошибки при вводе
                const errors = document.getElementById('nicknameErrors');
                if (errors) {
                    errors.style.display = 'none';
                }
            });
        }
    });

    // Закрытие по клику на фон
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            closeNicknameModal();
        }
    });

    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeNicknameModal();
        }
    });
}

// Закрыть модальное окно
function closeNicknameModal() {
    const modal = document.getElementById('nicknameModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Сохранить ник
async function saveNickname() {
    const input = document.getElementById('nicknameInput');
    const errors = document.getElementById('nicknameErrors');
    const saveBtn = document.getElementById('saveNicknameBtn');
    
    if (!input) return;
    
    const nickname = input.value.trim();
    
    // Валидация
    if (!nickname) {
        if (errors) {
            errors.style.display = 'block';
            errors.innerHTML = '❌ Ник не может быть пустым';
            errors.style.color = '#f87171';
        }
        return;
    }
    
    if (nickname.length > 32) {
        if (errors) {
            errors.style.display = 'block';
            errors.innerHTML = '❌ Ник не может быть длиннее 32 символов';
            errors.style.color = '#f87171';
        }
        return;
    }
    
    // Блокируем кнопку
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = '⏳ Сохранение...';
    }
    
    try {
        const response = await fetch('/api/game/nickname', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nickname: nickname })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Обновляем отображение ника
            const display = document.getElementById('currentNicknameDisplay');
            if (display) {
                display.textContent = nickname;
            }
            
            if (typeof notifications !== 'undefined') {
                notifications.success(`Ник сохранён: ${nickname}`);
            }
            
            closeNicknameModal();
        } else {
            if (errors) {
                errors.style.display = 'block';
                errors.innerHTML = `❌ ${data.message || 'Ошибка сохранения'}`;
                errors.style.color = '#f87171';
            }
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || 'Ошибка сохранения');
            }
        }
    } catch (e) {
        if (errors) {
            errors.style.display = 'block';
            errors.innerHTML = `❌ Ошибка: ${e.message}`;
            errors.style.color = '#f87171';
        }
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
    
    // Разблокируем кнопку
    if (saveBtn) {
        saveBtn.disabled = false;
        saveBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
            </svg>
            Сохранить
        `;
    }
}

// ============================================
// ОСТАНОВКА АВТООБНОВЛЕНИЯ
// ============================================
function destroyGamePage() {
    stopGameAutoRefresh();
    console.log('🎮 Страница игры уничтожена');
}

// ============================================
// ЭКСПОРТ ФУНКЦИЙ
// ============================================
window.initGamePage = initGamePage;
window.loadClientMods = loadClientMods;
window.renderClientMods = renderClientMods;
window.setupGameModsSearch = setupGameModsSearch;
window.toggleGameModConnection = toggleGameModConnection;
window.refreshGameMods = refreshGameMods;
window.loadGameLinks = loadGameLinks;
window.destroyGamePage = destroyGamePage;
window.startGameAutoRefresh = startGameAutoRefresh;
window.stopGameAutoRefresh = stopGameAutoRefresh;
window.connectAllServerMods = connectAllServerMods;
window.loadNickname = loadNickname;
window.showNicknameModal = showNicknameModal;
window.createNicknameModal = createNicknameModal;
window.closeNicknameModal = closeNicknameModal;
window.saveNickname = saveNickname;

console.log('🎮 game.js загружен');