// ============================================
// УПРАВЛЕНИЕ СЕРВЕРОМ И ИГРОЙ (РЕАЛЬНЫЕ ВЫЗОВЫ)
// ============================================

// Состояние кнопок
let isServerActionInProgress = false;
let isGameActionInProgress = false;

// ============================================
// УПРАВЛЕНИЕ СЕРВЕРОМ
// ============================================

async function controlServer(action, event) {
    // Предотвращаем переход по ссылке
    if (event) {
        event.preventDefault();
    }
    
    // Проверяем, не заблокирована ли кнопка
    const btn = document.querySelector(`.control-btn.control-${action === 'start' ? 'start' : action === 'restart' ? 'restart' : 'stop'}`);
    if (btn && btn.disabled) {
        return; // Кнопка заблокирована — ничего не делаем
    }
    
    if (isServerActionInProgress) {
        if (typeof notifications !== 'undefined') {
            notifications.warning('Подождите, выполняется предыдущая операция...');
        }
        return;
    }
    
    const actionNames = {
        'start': 'Запуск сервера',
        'restart': 'Перезапуск сервера',
        'stop': 'Остановка сервера'
    };
    
    const actionIcons = {
        'start': '▶️',
        'restart': '🔄',
        'stop': '⏹️'
    };
    
    console.log(`${actionIcons[action]} ${actionNames[action]}`);
    
    // Находим кнопку
    if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
        btn.style.opacity = '0.6';
    }
    
    isServerActionInProgress = true;
    
    try {
        const endpoint = `/api/server/${action}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (typeof notifications !== 'undefined') {
                notifications.success(data.message || `${actionNames[action]} выполнен`);
            }
        } else {
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || `Ошибка ${actionNames[action]}`);
            }
        }
        
        // Обновляем статус сервера
        await updateServerStatus();
        
    } catch (e) {
        console.error('❌ Ошибка:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
    
    // Восстанавливаем кнопку
    if (btn) {
        btn.classList.remove('loading');
        // Не снимаем disabled — оно будет снято при обновлении статуса
    }
    
    isServerActionInProgress = false;
}

// ============================================
// ПОЛУЧЕНИЕ СТАТУСА СЕРВЕРА
// ============================================

async function updateServerStatus() {
    try {
        const response = await fetch('/api/server/status');
        const data = await response.json();
        
        if (data.success && data.status) {
            const status = data.status;
            
            // Обновляем индикацию в меню
            const startBtn = document.querySelector('.control-btn.control-start');
            const stopBtn = document.querySelector('.control-btn.control-stop');
            const restartBtn = document.querySelector('.control-btn.control-restart');
            
            if (status.running) {
                // Сервер запущен — БЛОКИРУЕМ кнопки запуска и перезапуска
                if (startBtn) {
                    startBtn.disabled = true;
                    startBtn.style.opacity = '0.5';
                    startBtn.title = 'Сервер уже запущен';
                }
                if (stopBtn) {
                    stopBtn.disabled = false;
                    stopBtn.style.opacity = '1';
                    stopBtn.title = 'Остановить сервер';
                }
                if (restartBtn) {
                    restartBtn.disabled = false;
                    restartBtn.style.opacity = '1';
                    restartBtn.title = 'Перезапустить сервер';
                }
                
                // Добавляем индикатор статуса в меню
                updateStatusIndicator(true, status);
                
            } else {
                // Сервер остановлен — БЛОКИРУЕМ кнопку остановки
                if (startBtn) {
                    startBtn.disabled = false;
                    startBtn.style.opacity = '1';
                    startBtn.title = 'Запустить сервер';
                }
                if (stopBtn) {
                    stopBtn.disabled = true;
                    stopBtn.style.opacity = '0.5';
                    stopBtn.title = 'Сервер не запущен';
                }
                if (restartBtn) {
                    restartBtn.disabled = true;
                    restartBtn.style.opacity = '0.5';
                    restartBtn.title = 'Сервер не запущен';
                }
                
                updateStatusIndicator(false, null);
            }
        }
    } catch (e) {
        console.warn('⚠️ Ошибка получения статуса сервера:', e);
    }
}

// ============================================
// ИНДИКАТОР СТАТУСА В МЕНЮ
// ============================================

function updateStatusIndicator(running, status) {
    // Удаляем старый индикатор
    const oldIndicator = document.querySelector('.server-status-indicator');
    if (oldIndicator) {
        oldIndicator.remove();
    }
    
    const menuBottom = document.querySelector('.menu-bottom');
    if (!menuBottom) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'server-status-indicator';
    indicator.style.cssText = `
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        margin: 4px 12px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 500;
        background: ${running ? 'rgba(74, 222, 128, 0.08)' : 'rgba(255, 255, 255, 0.03)'};
        border: 1px solid ${running ? 'rgba(74, 222, 128, 0.15)' : 'rgba(255, 255, 255, 0.05)'};
        color: ${running ? '#4ade80' : 'rgba(255, 255, 255, 0.3)'};
    `;
    
    const dot = document.createElement('span');
    dot.style.cssText = `
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: ${running ? '#4ade80' : 'rgba(255, 255, 255, 0.15)'};
        ${running ? 'box-shadow: 0 0 10px rgba(74, 222, 128, 0.3);' : ''}
        ${running ? 'animation: pulse-dot 1.5s ease-in-out infinite;' : ''}
    `;
    
    const text = document.createElement('span');
    text.textContent = running ? 
        `🟢 Сервер запущен (PID: ${status?.pid || '?'})` : 
        '⚪ Сервер остановлен';
    
    indicator.appendChild(dot);
    indicator.appendChild(text);
    
    // Вставляем перед блоком настроек
    const settingsBlock = menuBottom.querySelector('.menu-block-settings');
    if (settingsBlock) {
        menuBottom.insertBefore(indicator, settingsBlock);
    } else {
        menuBottom.appendChild(indicator);
    }
}

// ============================================
// УПРАВЛЕНИЕ ИГРОЙ (РЕАЛЬНЫЕ ВЫЗОВЫ)
// ============================================

async function controlGame(action, event) {
    // Предотвращаем переход по ссылке
    if (event) {
        event.preventDefault();
    }
    
    // Проверяем, не заблокирована ли кнопка
    const btn = document.querySelector(`.control-btn.control-game-${action === 'start' ? 'start' : 'stop'}`);
    if (btn && btn.disabled) {
        return; // Кнопка заблокирована — ничего не делаем
    }
    
    if (isGameActionInProgress) {
        if (typeof notifications !== 'undefined') {
            notifications.warning('Подождите, выполняется предыдущая операция...');
        }
        return;
    }
    
    const actionNames = {
        'start': 'Запуск игры',
        'stop': 'Остановка игры'
    };
    
    const actionIcons = {
        'start': '🎮',
        'stop': '⏹️'
    };
    
    console.log(`${actionIcons[action]} ${actionNames[action]}`);
    
    // Находим кнопку
    if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
        btn.style.opacity = '0.6';
    }
    
    isGameActionInProgress = true;
    
    try {
        const endpoint = `/api/game/${action}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (typeof notifications !== 'undefined') {
                notifications.success(data.message || `${actionNames[action]} выполнен`);
            }
        } else {
            if (typeof notifications !== 'undefined') {
                notifications.error(data.message || `Ошибка ${actionNames[action]}`);
            }
        }
        
        // Обновляем статус игры
        await updateGameStatus();
        
    } catch (e) {
        console.error('❌ Ошибка:', e);
        if (typeof notifications !== 'undefined') {
            notifications.error('Ошибка: ' + e.message);
        }
    }
    
    // Восстанавливаем кнопку
    if (btn) {
        btn.classList.remove('loading');
        // Не снимаем disabled — оно будет снято при обновлении статуса
    }
    
    isGameActionInProgress = false;
}

// ============================================
// ПОЛУЧЕНИЕ СТАТУСА ИГРЫ
// ============================================

async function updateGameStatus() {
    try {
        const response = await fetch('/api/game/status');
        const data = await response.json();
        
        if (data.success && data.status) {
            const status = data.status;
            
            const startBtn = document.querySelector('.control-btn.control-game-start');
            const stopBtn = document.querySelector('.control-btn.control-game-stop');
            
            if (status.running) {
                // Игра запущена — БЛОКИРУЕМ кнопку запуска
                if (startBtn) {
                    startBtn.disabled = true;
                    startBtn.style.opacity = '0.5';
                    startBtn.title = 'Игра уже запущена';
                }
                if (stopBtn) {
                    stopBtn.disabled = false;
                    stopBtn.style.opacity = '1';
                    stopBtn.title = 'Остановить игру';
                }
            } else {
                // Игра остановлена — БЛОКИРУЕМ кнопку остановки
                if (startBtn) {
                    startBtn.disabled = false;
                    startBtn.style.opacity = '1';
                    startBtn.title = 'Запустить игру';
                }
                if (stopBtn) {
                    stopBtn.disabled = true;
                    stopBtn.style.opacity = '0.5';
                    stopBtn.title = 'Игра не запущена';
                }
            }
        }
    } catch (e) {
        console.warn('⚠️ Ошибка получения статуса игры:', e);
    }
}

// ============================================
// ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Добавляем стили для пульсации индикатора
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse-dot {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.5;
                transform: scale(1.3);
            }
        }
        
        .control-btn.loading {
            position: relative;
        }
        
        .control-btn.loading .nav-text::after {
            content: '...';
            animation: dots 1.2s steps(3, end) infinite;
        }
        
        @keyframes dots {
            0% { content: ''; }
            33% { content: '.'; }
            66% { content: '..'; }
            100% { content: '...'; }
        }
        
        /* Стиль для заблокированных кнопок */
        .control-btn:disabled {
            cursor: not-allowed !important;
            pointer-events: none !important;
        }
        
        .control-btn:disabled .nav-text {
            opacity: 0.6;
        }
    `;
    document.head.appendChild(style);
    
    // Проверяем статус сервера при загрузке
    setTimeout(() => {
        updateServerStatus();
        updateGameStatus();
    }, 1000);
    
    // Обновляем статус каждые 10 секунд
    setInterval(() => {
        updateServerStatus();
        updateGameStatus();
    }, 10000);
});

// ============================================
// ЭКСПОРТ ФУНКЦИЙ
// ============================================

window.controlServer = controlServer;
window.controlGame = controlGame;
window.updateServerStatus = updateServerStatus;
window.updateGameStatus = updateGameStatus;

console.log('🎮 controls.js загружен (с реальным API)');