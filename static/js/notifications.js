// ============================================
// СИСТЕМА УВЕДОМЛЕНИЙ С SVG ИКОНКАМИ
// ============================================

class NotificationSystem {
    constructor() {
        this.container = null;
        this.maxNotifications = 5;
        this.defaultDuration = 4000;
        this.init();
    }

    // Инициализация контейнера
    init() {
        this.container = document.createElement('div');
        this.container.id = 'notificationContainer';
        this.container.className = 'notification-container';
        document.body.appendChild(this.container);
    }

    // Получить SVG иконку по типу
    getIcon(type) {
        const icons = {
            success: `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
            `,
            error: `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
            `,
            warning: `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 9v4"/>
                    <path d="M12 17h.01"/>
                    <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/>
                </svg>
            `,
            info: `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="16" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
            `
        };

        return icons[type] || icons.info;
    }

    // Показать уведомление
    show(message, type = 'info', duration = null) {
        const actualDuration = duration || this.defaultDuration;

        // Удаляем старые уведомления если превышен лимит
        const notifications = this.container.querySelectorAll('.notification-item');
        if (notifications.length >= this.maxNotifications) {
            notifications[0].remove();
        }

        // Создаем уведомление
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);

        // Анимация появления
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Запускаем таймер авто-закрытия
        this.startAutoClose(notification, actualDuration);

        return notification;
    }

    // Создать DOM элемент уведомления
    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification-item notification-${type}`;

        const iconSvg = this.getIcon(type);

        notification.innerHTML = `
            <span class="notification-icon">${iconSvg}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" aria-label="Закрыть">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
            <div class="notification-progress"></div>
        `;

        // Обработчик закрытия
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.close(notification);
        });

        return notification;
    }

    // Закрыть уведомление
    close(notification) {
        if (!notification || notification._closing) return;
        notification._closing = true;

        const progress = notification.querySelector('.notification-progress');
        if (progress) {
            progress.style.animationPlayState = 'paused';
        }

        notification.classList.remove('show');
        notification.classList.add('hiding');

        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }

    // Авто-закрытие с прогресс-баром
    startAutoClose(notification, duration) {
        const progress = notification.querySelector('.notification-progress');
        if (progress) {
            progress.style.animationDuration = `${duration}ms`;
            progress.style.animationPlayState = 'running';
        }

        const timeout = setTimeout(() => {
            this.close(notification);
        }, duration);

        notification.addEventListener('mouseenter', () => {
            clearTimeout(timeout);
            if (progress) {
                progress.style.animationPlayState = 'paused';
            }
        });

        notification.addEventListener('mouseleave', () => {
            const newTimeout = setTimeout(() => {
                this.close(notification);
            }, duration);
            notification._timeout = newTimeout;
            
            if (progress) {
                progress.style.animationPlayState = 'running';
            }
        });
    }

    // Удобные методы для разных типов
    success(message, duration = null) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = null) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = null) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = null) {
        return this.show(message, 'info', duration);
    }

    // Очистить все уведомления
    clearAll() {
        const notifications = this.container.querySelectorAll('.notification-item');
        notifications.forEach(notification => {
            this.close(notification);
        });
    }
}

// Создаем глобальный экземпляр
const notifications = new NotificationSystem();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = notifications;
}