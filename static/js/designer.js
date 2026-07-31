// ===== Visual Designer =====
class VisualDesigner {
    constructor() {
        this.canvas = document.getElementById('designCanvas');
        this.elements = [];
        this.selectedElement = null;
        this.counter = 0;
        this.init();
    }

    init() {
        // Удаляем плейсхолдер при добавлении элементов
        this.canvas.addEventListener('dragover', this.handleDragOver.bind(this));
        this.canvas.addEventListener('drop', this.handleDrop.bind(this));

        // Настройка drag для компонентов
        document.querySelectorAll('.component-item').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('type', item.dataset.type);
                e.dataTransfer.effectAllowed = 'copy';
            });
        });

        // Клик для выделения на холсте
        this.canvas.addEventListener('click', (e) => {
            const element = e.target.closest('.canvas-element');
            if (element) {
                this.selectElement(element);
            } else {
                this.deselectElement();
            }
        });

        // Удаление по клавише Delete
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Delete' && this.selectedElement) {
                this.deleteElement(this.selectedElement);
            }
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    }

    handleDrop(e) {
        e.preventDefault();
        const type = e.dataTransfer.getData('type');
        if (type) {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            this.createElement(type, x, y);
        }
    }

    createElement(type, x, y) {
        this.counter++;
        const id = `element-${this.counter}`;
        const element = document.createElement('div');
        element.className = 'canvas-element';
        element.id = id;
        element.style.position = 'absolute';
        element.style.left = Math.max(10, x) + 'px';
        element.style.top = Math.max(10, y) + 'px';
        element.draggable = true;

        // Удаляем плейсхолдер
        const placeholder = this.canvas.querySelector('.canvas-placeholder');
        if (placeholder) placeholder.remove();

        // Создаем контент в зависимости от типа
        const content = this.createElementContent(type);
        element.appendChild(content);

        // Кнопка удаления
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '×';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteElement(element);
        });
        element.appendChild(deleteBtn);

        // Drag для перемещения
        element.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('elementId', element.id);
            element.style.opacity = '0.5';
        });

        element.addEventListener('dragend', (e) => {
            element.style.opacity = '1';
        });

        this.canvas.appendChild(element);
        this.elements.push(element);
        this.selectElement(element);
        this.updateProperties();

        return element;
    }

    createElementContent(type) {
        const content = document.createElement('div');
        content.className = 'element-content';

        switch(type) {
            case 'button':
                const button = document.createElement('button');
                button.textContent = 'Кнопка';
                button.style.cssText = `
                    padding: 8px 16px;
                    background: #3498db;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-family: inherit;
                    font-size: 14px;
                `;
                content.appendChild(button);
                break;

            case 'label':
                const label = document.createElement('span');
                label.textContent = 'Метка';
                label.style.cssText = `
                    color: var(--text-color);
                    font-size: 14px;
                    font-family: inherit;
                `;
                content.appendChild(label);
                break;

            case 'input':
                const input = document.createElement('input');
                input.type = 'text';
                input.placeholder = 'Введите текст...';
                input.style.cssText = `
                    padding: 8px 12px;
                    background: rgba(255,255,255,0.1);
                    border: 1px solid var(--glass-border);
                    border-radius: 6px;
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 14px;
                    width: 200px;
                `;
                content.appendChild(input);
                break;

            case 'panel':
                const panel = document.createElement('div');
                panel.style.cssText = `
                    padding: 20px;
                    background: rgba(255,255,255,0.05);
                    border: 1px solid var(--glass-border);
                    border-radius: 8px;
                    min-width: 150px;
                    min-height: 80px;
                `;
                const panelLabel = document.createElement('p');
                panelLabel.textContent = 'Панель';
                panelLabel.style.cssText = `
                    margin: 0;
                    opacity: 0.5;
                    font-size: 12px;
                `;
                panel.appendChild(panelLabel);
                content.appendChild(panel);
                break;

            case 'image':
                const img = document.createElement('div');
                img.style.cssText = `
                    width: 100px;
                    height: 100px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 12px;
                    opacity: 0.7;
                `;
                img.textContent = '🖼️ Изображение';
                content.appendChild(img);
                break;

            case 'checkbox':
                const checkbox = document.createElement('div');
                checkbox.style.cssText = `
                    display: flex;
                    align-items: center;
                    gap: 8px;
                `;
                const cb = document.createElement('input');
                cb.type = 'checkbox';
                cb.style.cssText = `
                    width: 18px;
                    height: 18px;
                    cursor: pointer;
                `;
                const cbLabel = document.createElement('label');
                cbLabel.textContent = 'Чекбокс';
                cbLabel.style.cssText = `
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 14px;
                    cursor: pointer;
                `;
                checkbox.appendChild(cb);
                checkbox.appendChild(cbLabel);
                content.appendChild(checkbox);
                break;

            case 'radio':
                const radio = document.createElement('div');
                radio.style.cssText = `
                    display: flex;
                    align-items: center;
                    gap: 8px;
                `;
                const rd = document.createElement('input');
                rd.type = 'radio';
                rd.name = 'radio-group';
                rd.style.cssText = `
                    width: 18px;
                    height: 18px;
                    cursor: pointer;
                `;
                const rdLabel = document.createElement('label');
                rdLabel.textContent = 'Радио';
                rdLabel.style.cssText = `
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 14px;
                    cursor: pointer;
                `;
                radio.appendChild(rd);
                radio.appendChild(rdLabel);
                content.appendChild(radio);
                break;

            case 'textarea':
                const textarea = document.createElement('textarea');
                textarea.placeholder = 'Введите текст...';
                textarea.style.cssText = `
                    padding: 8px 12px;
                    background: rgba(255,255,255,0.1);
                    border: 1px solid var(--glass-border);
                    border-radius: 6px;
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 14px;
                    width: 200px;
                    height: 80px;
                    resize: vertical;
                `;
                content.appendChild(textarea);
                break;

            default:
                content.textContent = 'Элемент';
        }

        return content;
    }

    selectElement(element) {
        this.deselectElement();
        this.selectedElement = element;
        element.classList.add('selected');
        this.updateProperties();
    }

    deselectElement() {
        if (this.selectedElement) {
            this.selectedElement.classList.remove('selected');
            this.selectedElement = null;
            this.updateProperties();
        }
    }

    deleteElement(element) {
        if (element) {
            element.remove();
            const index = this.elements.indexOf(element);
            if (index > -1) {
                this.elements.splice(index, 1);
            }
            if (this.selectedElement === element) {
                this.selectedElement = null;
            }
            this.updateProperties();

            // Если элементов нет, показываем плейсхолдер
            if (this.elements.length === 0) {
                this.showPlaceholder();
            }
        }
    }

    showPlaceholder() {
        const placeholder = document.createElement('div');
        placeholder.className = 'canvas-placeholder';
        placeholder.innerHTML = `
            <i class="fas fa-arrow-down"></i>
            <p>Перетащите компоненты сюда</p>
        `;
        this.canvas.appendChild(placeholder);
    }

    updateProperties() {
        const propertiesContent = document.getElementById('propertiesContent');
        if (!this.selectedElement) {
            propertiesContent.innerHTML = `<p class="no-selection">Выберите элемент на холсте</p>`;
            return;
        }

        const element = this.selectedElement;
        const style = element.style;
        const left = parseFloat(style.left) || 0;
        const top = parseFloat(style.top) || 0;
        const width = parseFloat(style.width) || (element.offsetWidth || 150);
        const height = parseFloat(style.height) || (element.offsetHeight || 50);

        propertiesContent.innerHTML = `
            <div class="property-group">
                <label>ID</label>
                <input type="text" value="${element.id}" disabled>
            </div>
            <div class="property-group">
                <label>Позиция X</label>
                <input type="number" value="${Math.round(left)}" onchange="window.designer.updateElementProperty('left', this.value)">
            </div>
            <div class="property-group">
                <label>Позиция Y</label>
                <input type="number" value="${Math.round(top)}" onchange="window.designer.updateElementProperty('top', this.value)">
            </div>
            <div class="property-group">
                <label>Ширина</label>
                <input type="number" value="${Math.round(width)}" onchange="window.designer.updateElementProperty('width', this.value + 'px')">
            </div>
            <div class="property-group">
                <label>Высота</label>
                <input type="number" value="${Math.round(height)}" onchange="window.designer.updateElementProperty('height', this.value + 'px')">
            </div>
            <div class="property-group">
                <label>Цвет фона</label>
                <input type="color" value="${style.backgroundColor || '#ffffff'}" onchange="window.designer.updateElementProperty('backgroundColor', this.value)">
            </div>
            <div class="property-group">
                <label>Цвет текста</label>
                <input type="color" value="${style.color || '#000000'}" onchange="window.designer.updateElementProperty('color', this.value)">
            </div>
            <div class="property-group">
                <label>Прозрачность</label>
                <input type="range" min="0" max="1" step="0.05" value="${style.opacity || 1}" onchange="window.designer.updateElementProperty('opacity', this.value)">
            </div>
        `;
    }

    updateElementProperty(property, value) {
        if (this.selectedElement) {
            this.selectedElement.style[property] = value;
        }
    }

    exportHTML() {
        if (this.elements.length === 0) {
            alert('Нет элементов для экспорта!');
            return;
        }

        let html = `<!-- Экспортировано из визуального конструктора -->\n<div style="position:relative;min-height:400px;padding:20px;background:#1a1a2e;">\n`;
        
        this.elements.forEach(el => {
            const style = el.style;
            const left = parseFloat(style.left) || 0;
            const top = parseFloat(style.top) || 0;
            const width = style.width || 'auto';
            const height = style.height || 'auto';
            const bg = style.backgroundColor || 'transparent';
            const color = style.color || '#ffffff';
            
            html += `    <div style="position:absolute;left:${left}px;top:${top}px;width:${width};height:${height};background:${bg};color:${color};padding:10px;border-radius:6px;">\n`;
            html += `        <!-- ${el.id} -->\n`;
            html += `        ${el.querySelector('.element-content')?.innerHTML || ''}\n`;
            html += `    </div>\n`;
        });

        html += `</div>`;

        // Копируем в буфер обмена или скачиваем
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'design-export.html';
        a.click();
        URL.revokeObjectURL(url);
    }

    clearCanvas() {
        if (confirm('Очистить холст? Все элементы будут удалены.')) {
            this.elements.forEach(el => el.remove());
            this.elements = [];
            this.selectedElement = null;
            this.showPlaceholder();
            this.updateProperties();
        }
    }
}

// ===== Инициализация =====
let designer;

document.addEventListener('DOMContentLoaded', function() {
    // Ждем загрузки вкладки редактора
    const observer = new MutationObserver(() => {
        const panel = document.getElementById('panel-editors');
        if (panel && panel.classList.contains('active') && !designer) {
            designer = new VisualDesigner();
            window.designer = designer;
        }
    });

    observer.observe(document.getElementById('panel-editors'), {
        attributes: true,
        attributeFilter: ['class']
    });

    // Если редактор уже активен
    const panel = document.getElementById('panel-editors');
    if (panel && panel.classList.contains('active')) {
        designer = new VisualDesigner();
        window.designer = designer;
    }
});

// ===== Глобальные функции для кнопок =====
function exportHTML() {
    if (window.designer) {
        window.designer.exportHTML();
    }
}

function clearCanvas() {
    if (window.designer) {
        window.designer.clearCanvas();
    }
}