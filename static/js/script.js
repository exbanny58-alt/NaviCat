// ============================================
// ГЛАВНЫЙ СКРИПТ - НАВИГАЦИЯ И УПРАВЛЕНИЕ КОНТЕНТОМ
// ============================================

// Контент для разных разделов
const pages = {
    server: `
        <div class="server-content-wrapper">
            <div class="server-header">
                <h1>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                        <line x1="8" y1="21" x2="16" y2="21"/>
                        <line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                    Управление сервером
                </h1>
                <p class="server-subtitle">Список модов, отмеченных как "СерверМод"</p>
            </div>

            <!-- ❌ УДАЛЯЕМ ВЕСЬ БЛОК server-stats -->
            <!--
            <div class="server-stats" id="serverStats">
                <div class="stat-card">
                    <span class="stat-number" id="serverModsCount">0</span>
                    <span class="stat-label">Серверных модов</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number" id="serverWorkshopCount">0</span>
                    <span class="stat-label">Из Workshop</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number" id="serverCustomCount">0</span>
                    <span class="stat-label">Кастомных</span>
                </div>
            </div>
            -->

            <!-- Панель управления -->
            <div class="server-toolbar">
                <button class="btn btn-primary" id="refreshServerModsBtn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23,4 23,10 17,10"/>
                        <path d="M21,12a9,9,0,0,0-5.5-8.2,9,9,0,0,0-11,3.7"/>
                        <polyline points="1,20 1,14 7,14"/>
                        <path d="M3,12a9,9,0,0,0,5.5,8.2,9,9,0,0,0,11-3.7"/>
                    </svg>
                    Обновить список
                </button>
                <div class="server-filter">
                    <input type="text" id="serverModsSearchInput" placeholder="🔍 Поиск модов..." class="server-search">
                </div>
            </div>

            <!-- Список серверных модов -->
            <div class="server-mods-list-container" id="serverModsContainer">
                <div class="loading-mods">
                    <span class="spinner"></span>
                    Загрузка серверных модов...
                </div>
            </div>
        </div>
    `,
// В pages.game - добавляем кнопку
    game: `
        <div class="game-content-wrapper">
            <div class="game-header">
                <h1>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="5,3 19,12 5,21"/>
                    </svg>
                    Управление игрой
                </h1>
                <p class="game-subtitle">Список модов, отмеченных как "КлиентМод"</p>
            </div>

            <!-- Панель управления -->
            <div class="game-toolbar">
                <button class="btn btn-primary" id="refreshGameModsBtn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23,4 23,10 17,10"/>
                        <path d="M21,12a9,9,0,0,0-5.5-8.2,9,9,0,0,0-11,3.7"/>
                        <polyline points="1,20 1,14 7,14"/>
                        <path d="M3,12a9,9,0,0,0,5.5,8.2,9,9,0,0,0,11-3.7"/>
                    </svg>
                    Обновить список
                </button>
                
                <!-- НОВАЯ КНОПКА СМЕНЫ НИКА -->
                <button class="btn btn-nickname" id="changeNicknameBtn" title="Изменить ник в игре">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                    </svg>
                    Ник: <span id="currentNicknameDisplay">player</span>
                </button>
                
                <!-- Кнопка подключения всех модов -->
                <button class="btn btn-game-connect-all" id="connectAllGameModsBtn" title="Подключить все моды, которые используются на сервере">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 5v14"/>
                        <path d="M5 12h14"/>
                    </svg>
                    Подключить все моды сервера
                </button>
                
                <div class="game-filter">
                    <input type="text" id="gameModsSearchInput" placeholder="🔍 Поиск модов..." class="game-search">
                </div>
            </div>

            <!-- Список клиентских модов -->
            <div class="game-mods-list-container" id="gameModsContainer">
                <div class="loading-mods">
                    <span class="spinner"></span>
                    Загрузка клиентских модов...
                </div>
            </div>
        </div>
    `,
    mods: `
        <div id="modsPageContent" style="height: 100%;">
            <div class="mods-content-wrapper" style="height: 100%; overflow-y: auto; padding-right: 8px; padding-bottom: 20px; box-sizing: border-box;">
                <div class="mods-header">
                    <h1>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22,19a2,2,0,0,1-2,2H4a2,2,0,0,1-2-2V5A2,2,0,0,1,4,3H9l2,3h9a2,2,0,0,1,2,2Z"/>
                        </svg>
                        Управление модами
                    </h1>
                </div>

                <!-- Статистика -->
                <div class="mods-stats" id="modsStats">
                    <div class="stat-card">
                        <span class="stat-number" id="totalModsCount">0</span>
                        <span class="stat-label">Всего модов</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number" id="workshopModsCount">0</span>
                        <span class="stat-label">Из Workshop</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-number" id="customModsCount">0</span>
                        <span class="stat-label">Кастомных</span>
                    </div>
                </div>

                <!-- Панель управления -->
                <div class="mods-toolbar">
                    <button class="btn btn-primary" id="refreshModsBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="23,4 23,10 17,10"/>
                            <path d="M21,12a9,9,0,0,0-5.5-8.2,9,9,0,0,0-11,3.7"/>
                            <polyline points="1,20 1,14 7,14"/>
                            <path d="M3,12a9,9,0,0,0,5.5,8.2,9,9,0,0,0,11-3.7"/>
                        </svg>
                        Обновить список
                    </button>
                    <button class="btn btn-secondary" id="openWorkshopBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22,19a2,2,0,0,1-2,2H4a2,2,0,0,1-2-2V5A2,2,0,0,1,4,3H9l2,3h9a2,2,0,0,1,2,2Z"/>
                        </svg>
                        Открыть Workshop
                    </button>
                    <button class="btn btn-secondary" id="openCustomModsBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22,19a2,2,0,0,1-2,2H4a2,2,0,0,1-2-2V5A2,2,0,0,1,4,3H9l2,3h9a2,2,0,0,1,2,2Z"/>
                        </svg>
                        Открыть кастомные
                    </button>
                    <div class="mods-filter">
                        <input type="text" id="modsSearchInput" placeholder="🔍 Поиск модов..." class="mods-search">
                    </div>
                </div>

                <!-- Список модов -->
                <div class="mods-list-container" id="modsListContainer">
                    <div class="loading-mods">
                        <span class="spinner"></span>
                        Загрузка модов...
                    </div>
                </div>
            </div>
        </div>
    `
};

// Текущий активный раздел
let currentPage = null;

// Флаг, был ли первый клик
let isFirstClick = true;

// Массив пунктов меню в порядке сверху вниз
const menuOrder = ['server', 'game', 'mods', 'settings'];

// Получить HTML стартовой страницы
function getStartPageHTML() {
    return `
        <div id="startPage" class="start-page">
            <div class="start-content">
                <div class="start-logo">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        <polyline points="9 12 11 14 15 10"/>
                    </svg>
                </div>
                <h1>DayZ Менеджер</h1>
                <p>Выберите раздел в меню слева</p>
                <div class="start-hint">
                    <span class="hint-dot"></span>
                    <span class="hint-dot"></span>
                    <span class="hint-dot"></span>
                </div>
            </div>
        </div>
    `;
}

// Определить направление анимации
function getAnimationDirection(targetPage) {
    if (!currentPage) {
        return 'in';
    }
    
    const currentIndex = menuOrder.indexOf(currentPage);
    const targetIndex = menuOrder.indexOf(targetPage);
    
    if (currentIndex === -1 || targetIndex === -1) {
        return 'in';
    }
    
    if (targetIndex < currentIndex) {
        return 'down';
    } else if (targetIndex > currentIndex) {
        return 'up';
    } else {
        return 'in';
    }
}

// Универсальная функция смены контента с анимацией
function switchContent(newHtml, page, direction, isFirst) {
    const contentArea = document.getElementById('contentArea');
    
    if (isFirst) {
        contentArea.classList.add('slide-up');
        
        setTimeout(() => {
            contentArea.innerHTML = newHtml;
            contentArea.classList.remove('slide-up');
            contentArea.classList.add('slide-in-down');
            
            setTimeout(() => {
                contentArea.classList.remove('slide-in-down');
                initPageAfterLoad(page);
            }, 350);
        }, 300);
        return;
    }
    
    if (direction === 'in') {
        contentArea.innerHTML = newHtml;
        contentArea.classList.add('slide-in-up');
        setTimeout(() => {
            contentArea.classList.remove('slide-in-up');
            initPageAfterLoad(page);
        }, 350);
        return;
    }
    
    contentArea.classList.add(direction === 'up' ? 'slide-up' : 'slide-down');
    
    setTimeout(() => {
        contentArea.innerHTML = newHtml;
        contentArea.classList.remove('slide-up', 'slide-down');
        contentArea.classList.add(direction === 'up' ? 'slide-in-down' : 'slide-in-up');
        
        setTimeout(() => {
            contentArea.classList.remove('slide-in-down', 'slide-in-up');
            initPageAfterLoad(page);
        }, 350);
        
    }, 300);
}

// Инициализация страницы после загрузки
function initPageAfterLoad(page) {
    // ============================================
    // СТРАНИЦА МОДОВ
    // ============================================
    if (page === 'mods') {
        let attempts = 0;
        const maxAttempts = 10;
        
        function tryInitMods() {
            attempts++;
            const container = document.getElementById('modsListContainer');
            
            if (container) {
                if (typeof initModsPage === 'function') {
                    initModsPage();
                }
                return;
            }
            
            if (attempts < maxAttempts) {
                setTimeout(tryInitMods, 200);
            } else {
                console.warn('Не удалось найти modsListContainer после ' + maxAttempts + ' попыток');
            }
        }
        
        setTimeout(tryInitMods, 100);
    }
    
    // ============================================
    // СТРАНИЦА СЕРВЕРА
    // ============================================
    if (page === 'server') {
        let attempts = 0;
        const maxAttempts = 10;
        
        function tryInitServer() {
            attempts++;
            const container = document.getElementById('serverModsContainer');
            
            if (container) {
                // Инициализируем страницу сервера
                if (typeof initServerPage === 'function') {
                    initServerPage();
                }
                
                // Настраиваем поиск
                if (typeof setupServerModsSearch === 'function') {
                    setupServerModsSearch();
                }
                
                // Обработчик кнопки обновления
                const refreshBtn = document.getElementById('refreshServerModsBtn');
                if (refreshBtn) {
                    // Удаляем старые обработчики, чтобы не дублировать
                    const newRefreshBtn = refreshBtn.cloneNode(true);
                    refreshBtn.parentNode.replaceChild(newRefreshBtn, refreshBtn);
                    
                    newRefreshBtn.addEventListener('click', () => {
                        if (typeof refreshServerMods === 'function') {
                            refreshServerMods();
                        }
                    });
                }
                return;
            }
            
            if (attempts < maxAttempts) {
                setTimeout(tryInitServer, 200);
            } else {
                console.warn('Не удалось найти serverModsContainer после ' + maxAttempts + ' попыток');
            }
        }
        
        setTimeout(tryInitServer, 100);
    }

    // ============================================
    // СТРАНИЦА КЛИЕНТА
    // ============================================   
    // В функции initPageAfterLoad - для страницы game:
    if (page === 'game') {
        let attempts = 0;
        const maxAttempts = 10;
        
        function tryInitGame() {
            attempts++;
            const container = document.getElementById('gameModsContainer');
            
            if (container) {
                if (typeof initGamePage === 'function') {
                    initGamePage();
                }
                
                if (typeof setupGameModsSearch === 'function') {
                    setupGameModsSearch();
                }
                
                const refreshBtn = document.getElementById('refreshGameModsBtn');
                if (refreshBtn) {
                    const newRefreshBtn = refreshBtn.cloneNode(true);
                    refreshBtn.parentNode.replaceChild(newRefreshBtn, refreshBtn);
                    
                    newRefreshBtn.addEventListener('click', () => {
                        if (typeof refreshGameMods === 'function') {
                            refreshGameMods();
                        }
                    });
                }
                return;
            }
            
            if (attempts < maxAttempts) {
                setTimeout(tryInitGame, 200);
            } else {
                console.warn('Не удалось найти gameModsContainer после ' + maxAttempts + ' попыток');
            }
        }
        
        setTimeout(tryInitGame, 100);
    }


    // ============================================
    // СТРАНИЦА STEAMCMD
    // ============================================   
    if (page === 'steamcmd') {
        let attempts = 0;
        const maxAttempts = 10;
        
        function tryInitSteamCMD() {
            attempts++;
            const container = document.getElementById('installServerBtn');
            
            if (container) {
                if (typeof initSteamCMD === 'function') {
                    initSteamCMD();
                }
                return;
            }
            
            if (attempts < maxAttempts) {
                setTimeout(tryInitSteamCMD, 200);
            } else {
                console.warn('Не удалось инициализировать SteamCMD');
            }
        }
        
        setTimeout(tryInitSteamCMD, 100);
    }
}

// Показать стартовую страницу
function showStartPage(direction = 'in') {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    document.querySelectorAll('.nav-item a').forEach(link => {
        const icon = link.querySelector('.nav-icon');
        const text = link.querySelector('.nav-text');
        if (icon) icon.style.color = '';
        if (text) text.style.color = '';
    });
    
    const html = getStartPageHTML();
    switchContent(html, 'start', direction, false);
    currentPage = null;
}

// Показать контент
function showContent(page, event) {
    const clickedItem = event.target.closest('.nav-item');
    if (!clickedItem) return;
    
    if (clickedItem.classList.contains('active')) {
        const direction = currentPage ? getAnimationDirection('start') : 'in';
        showStartPage(direction);
        return;
    }
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    clickedItem.classList.add('active');
    const direction = getAnimationDirection(page);
    const html = pages[page] || '<h1>Страница не найдена</h1>';
    
    switchContent(html, page, direction, isFirstClick);
    
    if (isFirstClick) {
        isFirstClick = false;
    }
    
    currentPage = page;
    
    document.querySelectorAll('.nav-item a').forEach(link => {
        const icon = link.querySelector('.nav-icon');
        const text = link.querySelector('.nav-text');
        if (icon) icon.style.color = '';
        if (text) text.style.color = '';
    });
}

// Показать настройки
function showSettings(event) {
    const clickedItem = event.target.closest('.nav-item');
    if (!clickedItem) return;
    
    if (clickedItem.classList.contains('active')) {
        const direction = currentPage ? getAnimationDirection('start') : 'in';
        showStartPage(direction);
        return;
    }
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    clickedItem.classList.add('active');
    const direction = getAnimationDirection('settings');
    const contentArea = document.getElementById('contentArea');
    
    if (isFirstClick) {
        contentArea.classList.add('slide-up');
        
        setTimeout(() => {
            fetch('/settings-content')
                .then(response => response.text())
                .then(html => {
                    contentArea.innerHTML = html;
                    if (typeof loadSettings === 'function') {
                        loadSettings();
                    }
                    if (typeof attachSettingsHandlers === 'function') {
                        attachSettingsHandlers();
                    }
                    contentArea.classList.remove('slide-up');
                    contentArea.classList.add('slide-in-down');
                    setTimeout(() => {
                        contentArea.classList.remove('slide-in-down');
                    }, 350);
                })
                .catch(() => {
                    contentArea.innerHTML = `
                        <div class="settings-content-wrapper">
                            <div class="settings-header">
                                <h1>⚙️ Настройки</h1>
                                <p class="settings-subtitle">Укажите пути к файлам и папкам DayZ</p>
                            </div>
                            <div class="settings-body">
                                <p style="color: rgba(255,255,255,0.5); text-align: center; padding: 40px;">
                                    Загрузка настроек...
                                </p>
                            </div>
                        </div>
                    `;
                    contentArea.classList.remove('slide-up');
                    contentArea.classList.add('slide-in-down');
                    setTimeout(() => {
                        contentArea.classList.remove('slide-in-down');
                    }, 350);
                });
        }, 300);
        
        isFirstClick = false;
        currentPage = 'settings';
        return;
    }
    
    if (direction === 'in') {
        fetch('/settings-content')
            .then(response => response.text())
            .then(html => {
                contentArea.innerHTML = html;
                if (typeof loadSettings === 'function') {
                    loadSettings();
                }
                if (typeof attachSettingsHandlers === 'function') {
                    attachSettingsHandlers();
                }
                contentArea.classList.add('slide-in-up');
                setTimeout(() => {
                    contentArea.classList.remove('slide-in-up');
                }, 350);
            })
            .catch(() => {
                contentArea.innerHTML = `
                    <div class="settings-content-wrapper">
                        <div class="settings-header">
                            <h1>⚙️ Настройки</h1>
                            <p class="settings-subtitle">Укажите пути к файлам и папкам DayZ</p>
                        </div>
                        <div class="settings-body">
                            <p style="color: rgba(255,255,255,0.5); text-align: center; padding: 40px;">
                                Загрузка настроек...
                            </p>
                        </div>
                    </div>
                `;
                contentArea.classList.add('slide-in-up');
                setTimeout(() => {
                    contentArea.classList.remove('slide-in-up');
                }, 350);
            });
        
        currentPage = 'settings';
        return;
    }
    
    contentArea.classList.add(direction === 'up' ? 'slide-up' : 'slide-down');
    
    setTimeout(() => {
        fetch('/settings-content')
            .then(response => response.text())
            .then(html => {
                contentArea.innerHTML = html;
                if (typeof loadSettings === 'function') {
                    loadSettings();
                }
                if (typeof attachSettingsHandlers === 'function') {
                    attachSettingsHandlers();
                }
                
                contentArea.classList.remove('slide-up', 'slide-down');
                contentArea.classList.add(direction === 'up' ? 'slide-in-down' : 'slide-in-up');
                
                setTimeout(() => {
                    contentArea.classList.remove('slide-in-down', 'slide-in-up');
                }, 350);
            })
            .catch(() => {
                contentArea.innerHTML = `
                    <div class="settings-content-wrapper">
                        <div class="settings-header">
                            <h1>⚙️ Настройки</h1>
                            <p class="settings-subtitle">Укажите пути к файлам и папкам DayZ</p>
                        </div>
                        <div class="settings-body">
                            <p style="color: rgba(255,255,255,0.5); text-align: center; padding: 40px;">
                                Загрузка настроек...
                            </p>
                        </div>
                    </div>
                `;
                contentArea.classList.remove('slide-up', 'slide-down');
                contentArea.classList.add(direction === 'up' ? 'slide-in-down' : 'slide-in-up');
                setTimeout(() => {
                    contentArea.classList.remove('slide-in-down', 'slide-in-up');
                }, 350);
            });
            
    }, 300);
    
    currentPage = 'settings';
    
    document.querySelectorAll('.nav-item a').forEach(link => {
        const icon = link.querySelector('.nav-icon');
        const text = link.querySelector('.nav-text');
        if (icon) icon.style.color = '';
        if (text) text.style.color = '';
    });
}

// ============================================
// РАЗНОЦВЕТНЫЕ ИКОНКИ ПРИ НАВЕДЕНИИ
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const navItems = document.querySelectorAll('.nav-item a');
    
    const colors = [
        '#FF6B6B', '#FF4757', '#FF8A5C', '#FF6348', '#FF9F43',
        '#FECA57', '#FFD93D', '#00B894', '#00CEC9', '#55EFC4',
        '#0984E3', '#45B7D1', '#74B9FF', '#6C5CE7', '#A29BFE',
        '#7BED9F', '#70A1FF', '#FFAF40', '#FF4D4D', '#D980FA'
    ];
    
    let lastColor = null;
    let lastColor2 = null;
    
    function getRandomColor() {
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    function getUniqueRandomColor() {
        let newColor;
        let attempts = 0;
        do {
            newColor = getRandomColor();
            attempts++;
            if (attempts > 50) break;
        } while (newColor === lastColor || newColor === lastColor2);
        
        lastColor2 = lastColor;
        lastColor = newColor;
        return newColor;
    }
    
    navItems.forEach(item => {
        const icon = item.querySelector('.nav-icon');
        const text = item.querySelector('.nav-text');
        
        item.addEventListener('mouseenter', function() {
            const color = getUniqueRandomColor();
            if (icon) {
                icon.style.color = color;
                icon.style.transition = 'color 0.3s ease, transform 0.3s ease';
            }
            if (text) {
                text.style.color = color;
                text.style.transition = 'color 0.3s ease';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            if (icon) {
                icon.style.color = '';
            }
            if (text) {
                text.style.color = '';
            }
        });
    });
});

// ============================================
// ПРЕДВАРИТЕЛЬНАЯ ЗАГРУЗКА МОДОВ ПРИ СТАРТЕ
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    if (typeof loadModsState === 'function') {
        loadModsState().then(() => {
            // Пытаемся загрузить кеш (мгновенно)
            if (typeof loadModsFromCache === 'function') {
                console.log('⚡ Загрузка кеша модов...');
                loadModsFromCache().then((loaded) => {
                    if (loaded) {
                        console.log('✅ Кеш модов загружен');
                        // В фоне проверяем обновления через 3 секунды
                        setTimeout(() => {
                            if (typeof backgroundScanAndCache === 'function') {
                                console.log('🔄 Фоновая проверка обновлений...');
                                backgroundScanAndCache();
                            }
                        }, 3000);
                    } else {
                        // Кеша нет — запускаем сканирование в фоне
                        console.log('🚀 Кеша нет, запуск фонового сканирования...');
                        if (typeof scanMods === 'function') {
                            scanMods(false);
                        }
                    }
                });
            }
        });
    }
});

// ============================================
// ИНИЦИАЛИЗАЦИЯ КОНСОЛИ ПРИ СТАРТЕ
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем консоль после загрузки страницы
    setTimeout(() => {
        if (typeof initConsole === 'function') {
            initConsole();
        }
    }, 500);
});