// Переключение вкладок
document.addEventListener('DOMContentLoaded', function() {
    const menuItems = document.querySelectorAll('.menu-item[data-tab]');
    const panels = {
        server: document.getElementById('panel-server'),
        client: document.getElementById('panel-client'),
        mods: document.getElementById('panel-mods'),
        editors: document.getElementById('panel-editors'),
        settings: document.getElementById('panel-settings')
    };

    function switchTab(tabId) {
        // Скрыть все панели
        Object.values(panels).forEach(panel => {
            if (panel) panel.classList.remove('active');
        });

        // Убрать активный класс у всех пунктов меню
        menuItems.forEach(item => {
            item.classList.remove('active');
        });

        // Показать выбранную панель
        if (panels[tabId]) {
            panels[tabId].classList.add('active');
        }

        // Активировать соответствующий пункт меню
        menuItems.forEach(item => {
            if (item.dataset.tab === tabId) {
                item.classList.add('active');
            }
        });
    }

    // Обработчики кликов
    menuItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.dataset.tab;
            if (tabId) {
                switchTab(tabId);
            }
        });
    });

    // По умолчанию активна вкладка "Сервер"
    switchTab('server');
});