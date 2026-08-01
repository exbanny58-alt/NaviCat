// ============================================
// УПРАВЛЕНИЕ МОДАМИ (с тремя кнопками вместо тумблеров)
// ============================================

let modsList = [];
let modsConfig = {};
let isModsReady = false;
let isCacheLoaded = false;

// Делаем доступными глобально
window.modsList = modsList;
window.isModsReady = isModsReady;
window._modsStats = null;

// ============================================
// ЗАГРУЗКА КОНФИГА МОДОВ
// ============================================
async function loadModsConfig() {
    try {
        const response = await fetch('/api/mods/config');
        const data = await response.json();
        if (data.success) {
            modsConfig = data.config;
            console.log('✅ Конфиг модов загружен');
            return true;
        }
    } catch (e) {
        console.error('❌ Ошибка загрузки конфига модов:', e);
    }
    return false;
}

// ============================================
// ЗАГРУЗКА МОДОВ ИЗ КЕША
// ============================================
async function loadModsFromCache() {
    try {
        console.log('⚡ Загрузка модов из кеша...');
        const response = await fetch('/api/mods/cache');
        const data = await response.json();
        
        if (data.success && data.mods) {
            modsList = data.mods;
            window.modsList = modsList;
            
            // Применяем конфиг к каждому моду
            modsList.forEach(mod => {
                if (modsConfig[mod.id]) {
                    mod.server = modsConfig[mod.id].server || false;
                    mod.server_mod = modsConfig[mod.id].server_mod || false;
                    mod.client = modsConfig[mod.id].client || false;
                } else {
                    // Если конфига нет — создаём с false
                    modsConfig[mod.id] = {
                        server: false,
                        server_mod: false,
                        client: false
                    };
                    mod.server = false;
                    mod.server_mod = false;
                    mod.client = false;
                }
            });
            
            isModsReady = true;
            isCacheLoaded = true;
            window.isModsReady = isModsReady;
            window._modsStats = data.stats;
            
            console.log(`✅ Загружено ${data.stats.total} модов из кеша`);
            return true;
        } else {
            console.warn('⚠️ Кеш не найден, нужно сканирование');
            return false;
        }
    } catch (e) {
        console.error('❌ Ошибка загрузки кеша:', e);
        return false;
    }
}

// ============================================
// ФОНОВОЕ СКАНИРОВАНИЕ
// ============================================
async function backgroundScanAndCache() {
    try {
        console.log('🔄 Фоновое сканирование модов...');
        const response = await fetch('/api/mods/scan-and-cache', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ Кеш обновлён: ${data.stats.total} модов`);
            
            if (data.mods) {
                modsList = data.mods;
                window.modsList = modsList;
                window._modsStats = data.stats;
                
                const container = document.getElementById('modsListContainer');
                if (container) {
                    renderMods(modsList);
                    updateStats(data.stats);
                    if (typeof notifications !== 'undefined') {
                        notifications.info('Список модов обновлён');
                    }
                }
            }
        } else {
            console.warn('⚠️ Ошибка фонового сканирования:', data.message);
        }
    } catch (e) {
        console.error('❌ Ошибка фонового сканирования:', e);
    }
}

// ============================================
// СКАНИРОВАНИЕ МОДОВ
// ============================================
async function scanMods(showLoading = true) {
    const container = document.getElementById('modsListContainer');
    
    if (!container) {
        console.error('Контейнер modsListContainer не найден');
        return;
    }

    if (showLoading) {
        container.innerHTML = `
            <div class="loading-mods">
                <span class="spinner"></span>
                Сканирование модов...
            </div>
        `;
    }

    try {
        const response = await fetch('/api/mods/scan-and-cache', {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            modsList = data.mods;
            window.modsList = modsList;
            
            // Применяем конфиг к каждому моду
            modsList.forEach(mod => {
                if (modsConfig[mod.id]) {
                    mod.server = modsConfig[mod.id].server || false;
                    mod.server_mod = modsConfig[mod.id].server_mod || false;
                    mod.client = modsConfig[mod.id].client || false;
                } else {
                    modsConfig[mod.id] = {
                        server: false,
                        server_mod: false,
                        client: false
                    };
                    mod.server = false;
                    mod.server_mod = false;
                    mod.client = false;
                }
            });

            renderMods(modsList);
            updateStats(data.stats);
            isModsReady = true;
            window.isModsReady = isModsReady;
            window._modsStats = data.stats;
            
            if (typeof notifications !== 'undefined') {
                notifications.success(`Найдено ${data.stats.total} модов`);
            }
        } else {
            container.innerHTML = `
                <div class="empty-mods">
                    <p>❌ ${data.message || 'Ошибка сканирования'}</p>
                    <p class="empty-hint">Проверьте пути в настройках</p>
                </div>
            `;
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || 'Ошибка сканирования модов');
            }
        }
    } catch (e) {
        container.innerHTML = `
            <div class="empty-mods">
                <p>❌ Ошибка: ${e.message}</p>
            </div>
        `;
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка сканирования: ' + e.message);
        }
    }
}

// ============================================
// ОТРИСОВКА СПИСКА МОДОВ (с кнопками)
// ============================================
function renderMods(mods) {
    const container = document.getElementById('modsListContainer');
    
    if (!container) {
        console.error('Контейнер modsListContainer не найден');
        return;
    }
    
    const searchInput = document.getElementById('modsSearchInput');
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
                <p>📭 Модов не найдено</p>
                ${searchValue ? '<p class="empty-hint">Попробуйте изменить поиск</p>' : ''}
            </div>
        `;
        return;
    }

    let html = '';
    filtered.forEach(mod => {
        const escapedPath = mod.path.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        
        // Определяем классы для кнопок
        const serverActive = mod.server ? 'active' : '';
        const serverModActive = mod.server_mod ? 'active' : '';
        const clientActive = mod.client ? 'active' : '';
        
        html += `
            <div class="mod-item" data-mod-id="${mod.id}">
                <div class="mod-info">
                    <div class="mod-name">
                        ${mod.name}
                        ${mod.type === 'workshop' ? '🛠️' : '📁'}
                    </div>
                    <div class="mod-details">
                        <span class="mod-folder">${mod.folder}</span>
                        <span class="mod-version">v${mod.version}</span>
                        <span class="mod-type ${mod.type}">${mod.type === 'workshop' ? 'Workshop' : 'Кастомный'}</span>
                        ${!mod.has_meta ? '<span class="mod-warning">⚠️ Нет meta.cpp</span>' : ''}
                    </div>
                </div>
                <div class="mod-actions">
                    <button class="mod-btn mod-btn-server ${serverActive}" 
                            onclick="toggleModAttr('${mod.id}', 'server', !this.classList.contains('active'))"
                            title="Серверный мод">
                        <span class="btn-label">Серверный</span>
                        <span class="btn-status">${mod.server ? 'Вкл' : 'Выкл'}</span>
                    </button>
                    
                    <button class="mod-btn mod-btn-server-mod ${serverModActive}" 
                            onclick="toggleModAttr('${mod.id}', 'server_mod', !this.classList.contains('active'))"
                            title="Мод для сервера">
                        <span class="btn-label">СерверМод</span>
                        <span class="btn-status">${mod.server_mod ? 'Вкл' : 'Выкл'}</span>
                    </button>
                    
                    <button class="mod-btn mod-btn-client ${clientActive}" 
                            onclick="toggleModAttr('${mod.id}', 'client', !this.classList.contains('active'))"
                            title="Клиентский мод">
                        <span class="btn-label">КлиентМод</span>
                        <span class="btn-status">${mod.client ? 'Вкл' : 'Выкл'}</span>
                    </button>
                    
                    <button class="btn-mod-folder" onclick="openModFolder('${escapedPath}')" title="Открыть папку мода">
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
// ОБНОВЛЕНИЕ СТАТИСТИКИ
// ============================================
function updateStats(stats) {
    const totalEl = document.getElementById('totalModsCount');
    const workshopEl = document.getElementById('workshopModsCount');
    const customEl = document.getElementById('customModsCount');
    
    if (totalEl) totalEl.textContent = stats.total || 0;
    if (workshopEl) workshopEl.textContent = stats.workshop || 0;
    if (customEl) customEl.textContent = stats.custom || 0;
}

// ============================================
// ПЕРЕКЛЮЧЕНИЕ АТРИБУТА МОДА (с кнопками)
// ============================================
async function toggleModAttr(modId, attr, value) {
    console.log(`🔄 toggleModAttr: ${modId}, ${attr} = ${value}`);
    
    try {
        const response = await fetch(`/api/mods/config/${modId}/${attr}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value: value })
        });

        const data = await response.json();
        
        if (data.success) {
            if (!modsConfig[modId]) {
                modsConfig[modId] = {};
            }
            modsConfig[modId][attr] = value;
            
            const mod = modsList.find(m => m.id === modId);
            if (mod) {
                mod[attr] = value;
            }
            
            // Обновляем только эту кнопку, а не весь список
            updateModButton(modId, attr, value);
            
            const labels = {
                'server': '🟡 Сервер',
                'server_mod': '🔵 Мод сервера',
                'client': '🟢 Клиент'
            };
            
            const status = value ? 'включён ✅' : 'выключен ❌';
            
            if (typeof notifications !== 'undefined') {
                notifications.success(`${labels[attr] || attr}: ${status}`);
            }
        } else {
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || 'Ошибка');
            }
        }
    } catch (e) {
        console.error('❌ Ошибка переключения:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
}

// ============================================
// ОБНОВЛЕНИЕ СОСТОЯНИЯ КНОПКИ (без перерисовки всего списка)
// ============================================
function updateModButton(modId, attr, value) {
    const modItem = document.querySelector(`.mod-item[data-mod-id="${modId}"]`);
    if (!modItem) return;
    
    let btnClass;
    let label;
    
    switch(attr) {
        case 'server':
            btnClass = 'mod-btn-server';
            label = 'S';
            break;
        case 'server_mod':
            btnClass = 'mod-btn-server-mod';
            label = 'M';
            break;
        case 'client':
            btnClass = 'mod-btn-client';
            label = 'C';
            break;
        default:
            return;
    }
    
    const btn = modItem.querySelector(`.${btnClass}`);
    if (!btn) return;
    
    if (value) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
    
    const statusSpan = btn.querySelector('.btn-status');
    if (statusSpan) {
        statusSpan.textContent = value ? 'Вкл' : 'Выкл';
    }
}

// ============================================
// ОТКРЫТЬ ПАПКУ С МОДОМ
// ============================================
async function openModFolder(path) {
    console.log('📂 openModFolder вызвана с путём:', path);
    
    if (!path) {
        if (typeof notifications !== 'undefined') {
            notifications.error('Путь к моду не указан');
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
        const data = await response.json();
        
        if (data.success) {
            if (typeof notifications !== 'undefined') {
                notifications.success('Папка открыта');
            }
        } else {
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || 'Ошибка открытия папки');
            }
        }
    } catch (e) {
        console.error('❌ Ошибка открытия папки:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
}

// ============================================
// ПОИСК МОДОВ
// ============================================
function setupModsSearch() {
    const searchInput = document.getElementById('modsSearchInput');
    if (searchInput) {
        const newInput = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newInput, searchInput);
        
        newInput.addEventListener('input', () => {
            renderMods(modsList);
        });
    }
}

// ============================================
// ПРИКРЕПЛЯЕМ ОБРАБОТЧИКИ КНОПОК
// ============================================
function attachModsButtonHandlers() {
    const refreshBtn = document.getElementById('refreshModsBtn');
    if (refreshBtn) {
        const newRefreshBtn = refreshBtn.cloneNode(true);
        refreshBtn.parentNode.replaceChild(newRefreshBtn, refreshBtn);
        newRefreshBtn.addEventListener('click', () => scanMods(true));
    }
    
    const workshopBtn = document.getElementById('openWorkshopBtn');
    if (workshopBtn) {
        const newWorkshopBtn = workshopBtn.cloneNode(true);
        workshopBtn.parentNode.replaceChild(newWorkshopBtn, workshopBtn);
        newWorkshopBtn.addEventListener('click', () => {
            fetch('/api/settings')
                .then(r => r.json())
                .then(data => {
                    if (data.workshop) {
                        fetch('/api/open/explorer', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ path: data.workshop })
                        });
                    } else if (typeof notifications !== 'undefined') {
                        notifications.warning('Путь к Workshop не указан в настройках');
                    }
                });
        });
    }
    
    const customBtn = document.getElementById('openCustomModsBtn');
    if (customBtn) {
        const newCustomBtn = customBtn.cloneNode(true);
        customBtn.parentNode.replaceChild(newCustomBtn, customBtn);
        newCustomBtn.addEventListener('click', () => {
            fetch('/api/settings')
                .then(r => r.json())
                .then(data => {
                    if (data.custom_mods) {
                        fetch('/api/open/explorer', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ path: data.custom_mods })
                        });
                    } else if (typeof notifications !== 'undefined') {
                        notifications.warning('Путь к кастомным модам не указан в настройках');
                    }
                });
        });
    }
}

// ============================================
// ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ МОДОВ
// ============================================
async function initModsPage() {
    const container = document.getElementById('modsListContainer');
    if (!container) {
        console.warn('Страница модов не загружена, пропускаем инициализацию');
        return;
    }

    // Сначала загружаем конфиг
    await loadModsConfig();

    const cacheLoaded = await loadModsFromCache();
    
    if (cacheLoaded && modsList.length > 0) {
        console.log('⚡ Мгновенная загрузка из кеша');
        renderMods(modsList);
        if (window._modsStats) {
            updateStats(window._modsStats);
        }
        setupModsSearch();
        attachModsButtonHandlers();
        return;
    }

    container.innerHTML = `
        <div class="loading-mods">
            <span class="spinner"></span>
            Первое сканирование модов...
        </div>
    `;
    
    await scanMods(true);
    setupModsSearch();
    attachModsButtonHandlers();
}

// ============================================
// ЭКСПОРТ ФУНКЦИЙ В ГЛОБАЛЬНУЮ ОБЛАСТЬ
// ============================================
window.initModsPage = initModsPage;
window.toggleModAttr = toggleModAttr;
window.updateModButton = updateModButton;
window.openModFolder = openModFolder;
window.scanMods = scanMods;
window.loadModsConfig = loadModsConfig;
window.loadModsFromCache = loadModsFromCache;
window.backgroundScanAndCache = backgroundScanAndCache;
window.renderMods = renderMods;
window.updateStats = updateStats;
window.attachModsButtonHandlers = attachModsButtonHandlers;
window.setupModsSearch = setupModsSearch;

console.log('📦 mods.js загружен, функции экспортированы');
console.log('  - initModsPage:', typeof window.initModsPage);
console.log('  - toggleModAttr:', typeof window.toggleModAttr);
console.log('  - updateModButton:', typeof window.updateModButton);
console.log('  - openModFolder:', typeof window.openModFolder);