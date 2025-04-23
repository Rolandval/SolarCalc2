// Створюємо об'єкт панелей в JavaScript
const panelsData = JSON.parse(document.getElementById('panels-data').textContent);
const invertersData = JSON.parse(document.getElementById('inverters-data').textContent);
const batteriesData = JSON.parse(document.getElementById('batteries-data').textContent);

function updateModelOptions() {
    const brandSelect = document.getElementById('panel_brand');
    const modelSelect = document.getElementById('panel_model');
    const selectedBrand = brandSelect.value;
    const customModelContainer = document.getElementById('custom-model-container');
    
    // Очищаємо попередні опції
    modelSelect.innerHTML = '<option value="" disabled selected>Виберіть модель</option>';
    
    if (!selectedBrand) return;
    
    // Якщо вибрано "Інший", показуємо поле для ручного введення моделі
    if (selectedBrand === 'other') {
        customModelContainer.style.display = 'block';
        modelSelect.disabled = true; // Деактивуємо стандартний select
        modelSelect.required = false; // Знімаємо обов'язковість
        document.getElementById('custom_panel_model').required = true; // Робимо поле ручного введення обов'язковим
        
        // Викликаємо updatePanelDimensions, щоб оновити стан полів
        updatePanelDimensions();
    } else {
        customModelContainer.style.display = 'none';
        modelSelect.disabled = false; // Активуємо стандартний select
        modelSelect.required = true; // Повертаємо обов'язковість
        document.getElementById('custom_panel_model').required = false; // Знімаємо обов'язковість з поля ручного введення
        
        // Додаємо нові опції моделей для обраного бренду
        const models = panelsData[selectedBrand];
        if (models && models.length > 0) {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.model;
                option.dataset.length = model.length;
                option.dataset.width = model.width;
                option.dataset.height = model.height;
                option.dataset.panelType = model.panel_type;
                modelSelect.appendChild(option);
            });
        }
    }
}

// Додаємо обробник події для поля ручного введення моделі
document.getElementById('custom_panel_model').addEventListener('input', function() {
    // Якщо поле не порожнє, робимо його валідним
    this.setCustomValidity('');
});

function updateInverterOptions() {
    const brandSelect = document.getElementById('inverter_brand');
    const modelSelect = document.getElementById('inverter_model');
    const selectedBrand = brandSelect.value;
    const customInverterContainer = document.getElementById('custom-inverter-container');
    
    // Очищаємо попередні опції
    modelSelect.innerHTML = '<option value="" disabled selected>Виберіть модель</option>';
    
    if (!selectedBrand) return;
    
    // Якщо вибрано "Інший", показуємо поле для ручного введення моделі
    if (selectedBrand === 'other') {
        customInverterContainer.style.display = 'block';
        modelSelect.disabled = true; // Деактивуємо стандартний select
        document.getElementById('custom_inverter_model').required = true; // Робимо поле ручного введення обов'язковим
        
        // Деактивуємо кнопку завантаження datasheet
        document.getElementById('inverter-datasheet-btn').disabled = true;
        
        // Очищаємо поля для ручного введення
        document.getElementById('inverter_power').value = '';
        document.getElementById('inverter_power').readOnly = false;
        document.getElementById('inverter_phases').value = '1';
        document.getElementById('strings_count').value = '';
        document.getElementById('strings_count').removeAttribute('max');
    } else {
        customInverterContainer.style.display = 'none';
        modelSelect.disabled = false; // Активуємо стандартний select
        document.getElementById('custom_inverter_model').required = false; // Знімаємо обов'язковість з поля ручного введення
        
        // Додаємо нові опції моделей для обраного бренду
        const models = invertersData[selectedBrand];
        if (models && models.length > 0) {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.model;
                option.dataset.power = model.power;
                option.dataset.phases_count = model.phases_count;
                option.dataset.voltage_type = model.voltage_type;
                option.dataset.strings_count = model.strings_count;
                modelSelect.appendChild(option);
            });
        }
    }
}

// Функція для оновлення деталей інвертора
function updateInverterDetails() {
    const modelSelect = document.getElementById('inverter_model');
    const selectedOption = modelSelect.options[modelSelect.selectedIndex];
    const datasheetBtn = document.getElementById('inverter-datasheet-btn');
    const voltageSelect = document.getElementById('inverter_voltage');
    const stringsCountInput = document.getElementById('strings_count');
    
    if (selectedOption && selectedOption.value) {
        // Оновлюємо деталі інвертора
        document.getElementById('inverter_power').value = selectedOption.dataset.power;
        document.getElementById('inverter_power').readOnly = true;
        document.getElementById('inverter_phases').value = selectedOption.dataset.phases_count;
        
        // Оновлюємо напругу
        if (selectedOption.dataset.voltage_type) {
            voltageSelect.value = selectedOption.dataset.voltage_type;
            voltageSelect.disabled = true;
        } else {
            voltageSelect.disabled = false;
        }
        
        // Оновлюємо кількість стрінгів
        if (selectedOption.dataset.strings_count && selectedOption.dataset.strings_count !== "null") {
            stringsCountInput.value = selectedOption.dataset.strings_count;
            stringsCountInput.max = selectedOption.dataset.strings_count;
        } else {
            stringsCountInput.value = '';
            stringsCountInput.removeAttribute('max');
        }
        
        // Активуємо кнопку завантаження datasheet
        datasheetBtn.disabled = false;
        
        // Зберігаємо ID інвертора як атрибут кнопки для використання в downloadInverterDatasheet()
        datasheetBtn.setAttribute('data-inverter-id', selectedOption.value);
    } else {
        // Деактивуємо кнопку, якщо модель не вибрана
        datasheetBtn.disabled = true;
        document.getElementById('inverter_power').readOnly = false;
        voltageSelect.disabled = false;
        stringsCountInput.value = '';
        stringsCountInput.removeAttribute('max');
    }
}

// Функція для оновлення опцій батарей
function updateBatteryOptions() {
    const brandSelect = document.getElementById('battery_brand');
    const modelSelect = document.getElementById('battery_model');
    const selectedBrand = brandSelect.value;
    const customBatteryContainer = document.getElementById('custom-battery-container');
    
    // Очищаємо попередні опції
    modelSelect.innerHTML = '<option value="" disabled selected>Виберіть модель</option>';
    
    if (!selectedBrand) return;
    
    // Якщо вибрано "Інший", показуємо поле для ручного введення моделі
    if (selectedBrand === 'other') {
        customBatteryContainer.style.display = 'block';
        modelSelect.disabled = true; // Деактивуємо стандартний select
        document.getElementById('custom_battery_model').required = true; // Робимо поле ручного введення обов'язковим
        
        // Деактивуємо кнопку завантаження datasheet
        document.getElementById('battery-datasheet-btn').disabled = true;
        
        // Очищаємо поля для ручного введення
        document.getElementById('battery_capacity').value = '';
        document.getElementById('battery_capacity').readOnly = false;
    } else {
        customBatteryContainer.style.display = 'none';
        modelSelect.disabled = false; // Активуємо стандартний select
        document.getElementById('custom_battery_model').required = false; // Знімаємо обов'язковість з поля ручного введення
        
        // Додаємо нові опції моделей для обраного бренду
        const models = batteriesData[selectedBrand];
        if (models && models.length > 0) {
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.model;
                option.dataset.capacity = model.capacity;
                option.dataset.is_head = model.is_head;
                option.dataset.is_stand = model.is_stand;
                option.dataset.voltage_type = model.voltage_type;
                modelSelect.appendChild(option);
            });
        }
    }
}

// Функція для оновлення деталей батареї
function updateBatteryDetails() {
    const modelSelect = document.getElementById('battery_model');
    const selectedOption = modelSelect.options[modelSelect.selectedIndex];
    const datasheetBtn = document.getElementById('battery-datasheet-btn');
    const voltageSelect = document.getElementById('battery_voltage');
    
    if (selectedOption && selectedOption.value) {
        // Оновлюємо деталі батареї
        document.getElementById('battery_capacity').value = selectedOption.dataset.capacity;
        document.getElementById('battery_capacity').readOnly = true;
        
        // Встановлюємо значення чекбоксів
        document.getElementById('battery_is_head').checked = selectedOption.dataset.is_head === 'true';
        document.getElementById('battery_is_stand_8').checked = selectedOption.dataset.is_stand === 'true';
        document.getElementById('battery_is_stand_12').checked = selectedOption.dataset.is_stand === 'true';
        
        // Оновлюємо напругу
        if (selectedOption.dataset.voltage_type) {
            voltageSelect.value = selectedOption.dataset.voltage_type;
            voltageSelect.disabled = true;
        } else {
            voltageSelect.disabled = false;
        }
        
        // Активуємо кнопку завантаження datasheet незалежно від стану чекбоксів
        datasheetBtn.disabled = false;
        
        // Зберігаємо ID батареї як атрибут кнопки для використання в downloadBatteryDatasheet()
        datasheetBtn.setAttribute('data-battery-id', selectedOption.value);
    } else {
        // Деактивуємо кнопку, якщо модель не вибрана
        datasheetBtn.disabled = true;
        document.getElementById('battery_capacity').readOnly = false;
        voltageSelect.disabled = false;
        
        // Скидаємо значення чекбоксів
        document.getElementById('battery_is_head').checked = false;
        document.getElementById('battery_is_stand_8').checked = false;
        document.getElementById('battery_is_stand_12').checked = false;
    }
}

// Додаємо обробники подій для полів ручного введення
document.getElementById('custom_panel_model').addEventListener('input', function() {
    // Якщо поле не порожнє, робимо його валідним
    this.setCustomValidity('');
});

document.getElementById('custom_inverter_model').addEventListener('input', function() {
    // Якщо поле не порожнє, робимо його валідним
    this.setCustomValidity('');
});

document.getElementById('custom_battery_model').addEventListener('input', function() {
    // Якщо поле не порожнє, робимо його валідним
    this.setCustomValidity('');
});

function updatePanelDimensions() {
    const modelSelect = document.getElementById('panel_model');
    const selectedOption = modelSelect.options[modelSelect.selectedIndex];
    const datasheetBtn = document.getElementById('datasheet-btn');
    const brandSelect = document.getElementById('panel_brand');
    
    // Перевіряємо, чи вибрано "Інший" бренд
    if (brandSelect.value === 'other') {
        // Якщо вибрано "Інший", то кнопка завантаження datasheet завжди недоступна
        datasheetBtn.disabled = true;
        
        // Поля для розмірів панелі стають доступними для редагування
        document.getElementById('panel_length').readOnly = false;
        document.getElementById('panel_width').readOnly = false;
        document.getElementById('panel_height').readOnly = false;
        
        return; // Виходимо з функції, щоб не виконувати код нижче
    }
    
    if (selectedOption && selectedOption.value) {
        // Оновлюємо розміри панелі
        document.getElementById('panel_length').value = selectedOption.dataset.length || '';
        document.getElementById('panel_width').value = selectedOption.dataset.width || '';
        document.getElementById('panel_height').value = selectedOption.dataset.height || '';
        
        // Оновлюємо тип панелі
        if (selectedOption.dataset.panelType) {
            document.getElementById('panel_type').value = selectedOption.dataset.panelType;
        }
        
        // Активуємо кнопку завантаження datasheet
        datasheetBtn.disabled = false;
        
        // Зберігаємо ID панелі як атрибут кнопки для використання в downloadDatasheet()
        datasheetBtn.setAttribute('data-panel-id', selectedOption.value);
        
        // Встановлюємо поля для розмірів панелі в режим тільки для читання
        document.getElementById('panel_length').readOnly = true;
        document.getElementById('panel_width').readOnly = true;
        document.getElementById('panel_height').readOnly = true;
    } else {
        // Деактивуємо кнопку, якщо модель не вибрана
        datasheetBtn.disabled = true;
        
        // Поля для розмірів панелі стають доступними для редагування
        document.getElementById('panel_length').readOnly = false;
        document.getElementById('panel_width').readOnly = false;
        document.getElementById('panel_height').readOnly = false;
    }
}

function calculateTotalPanels() {
    let totalPanels = 0;
    const arrays = document.querySelectorAll('.panel-array');
    
    arrays.forEach(array => {
        const arrayId = array.dataset.arrayId;
        const rows = parseInt(document.getElementById(`rows_${arrayId}`).value) || 0;
        const panelsPerRow = parseInt(document.getElementById(`panels_per_row_${arrayId}`).value) || 0;
        const arrayTotal = rows * panelsPerRow;
        
        // Оновлюємо відображення кількості панелей у масиві
        array.querySelector('.array-total').textContent = arrayTotal;
        
        totalPanels += arrayTotal;
    });
    
    document.getElementById('total_panels').value = totalPanels;
}

function addNewArray() {
    const container = document.getElementById('panel-arrays-container');
    const arrays = container.querySelectorAll('.panel-array');
    const newArrayId = arrays.length + 1;
    
    // Перевіряємо, чи активовано чекбокс наземного розміщення
    const groundMountingEnabled = document.getElementById('ground_mounting') && 
                                 document.getElementById('ground_mounting').checked;
    
    // Створюємо HTML для нового масиву
    const newArrayHTML = `
        <div class="panel-array" data-array-id="${newArrayId}">
            <div class="array-header">
                <h4>Масив #${newArrayId}</h4>
                <input type="text" class="array-name-input" id="array_name_${newArrayId}" name="array_name_${newArrayId}" placeholder="Назва масиву" value="">
                <button type="button" class="remove-array-btn" onclick="removeArray(this)">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="array-content">
                <div class="form-group">
                    <label for="rows_${newArrayId}"><i class="fas fa-grip-lines"></i> Кількість рядів:</label>
                    <input type="number" id="rows_${newArrayId}" name="rows_${newArrayId}" value="3" required min="1" onchange="calculateTotalPanels()">
                </div>
                <div class="form-group">
                    <label for="panels_per_row_${newArrayId}"><i class="fas fa-grip-lines-vertical"></i> К-сть панелей на ряд:</label>
                    <input type="number" id="panels_per_row_${newArrayId}" name="panels_per_row_${newArrayId}" value="4" required min="1" onchange="calculateTotalPanels()">
                </div>
                <div class="form-group">
                    <label><i class="fas fa-calculator"></i> Панелей у масиві:</label>
                    <span class="array-total" id="array_total_${newArrayId}">12</span>
                </div>
                <div class="form-group">
                    <label for="array_orientation_${newArrayId}"><i class="fas fa-arrows-alt"></i> Орієнтація панелей:</label>
                    <div class="orientation-container">
                        <select id="array_orientation_${newArrayId}" name="array_orientation_${newArrayId}" required onchange="updateOrientationIcon()">
                            <option value="альбомна">Альбомна</option>
                            <option value="портретна">Книжкова</option>
                        </select>
                        <div class="orientation-icon" id="orientation-icon-${newArrayId}" title="Схематичне зображення орієнтації панелі">
                            <div class="panel-icon_${newArrayId}">
                                <div class="panel-icon-inner_${newArrayId}"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Додаємо новий масив до контейнера
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = newArrayHTML.trim();
    const newArrayElement = tempDiv.firstChild;
    container.appendChild(newArrayElement);
    
    // Якщо активовано наземне розміщення, додаємо поля для параметрів
    if (groundMountingEnabled) {
        addGroundMountingFields(newArrayId);
    }
    
    // Оновлюємо загальну кількість панелей
    calculateTotalPanels();
    
    // Додаємо стилі для нових класів panel-icon та panel-icon-inner
    addOrientationIconStyles(newArrayId);
    
    // Ініціалізуємо іконку орієнтації
    setTimeout(() => {
        updateOrientationIcon();
    }, 100);
}

// Функція для додавання стилів для іконки орієнтації
function addOrientationIconStyles(arrayId) {
    // Перевіряємо, чи існує вже стиль для цього arrayId
    const styleId = `orientation-icon-styles-${arrayId}`;
    if (document.getElementById(styleId)) {
        return;
    }
    
    // Створюємо новий елемент style
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
        .panel-icon_${arrayId} {
            width: 40px;
            height: 30px;
            border: 2px solid var(--primary-color);
            border-radius: 2px;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: rgba(96, 165, 250, 0.1);
            position: relative;
            transition: transform 0.3s ease, width 0.3s ease, height 0.3s ease;
        }
        
        .panel-icon-inner_${arrayId} {
            width: 30px;
            height: 20px;
            background-color: rgba(96, 165, 250, 0.3);
            border: 1px solid var(--primary-color);
            transition: width 0.3s ease, height 0.3s ease;
        }
        
        .orientation-icon.landscape .panel-icon_${arrayId} {
            width: 40px;
            height: 30px;
        }
        
        .orientation-icon.landscape .panel-icon-inner_${arrayId} {
            width: 30px;
            height: 20px;
        }
        
        .orientation-icon.portrait .panel-icon_${arrayId} {
            width: 30px;
            height: 40px;
        }
        
        .orientation-icon.portrait .panel-icon-inner_${arrayId} {
            width: 20px;
            height: 30px;
        }
    `;
    
    // Додаємо стиль до head
    document.head.appendChild(style);
}

function removeArray(button) {
    const array = button.closest('.panel-array');
    const container = document.getElementById('panel-arrays-container');
    const arrays = container.querySelectorAll('.panel-array');
    
    // Не дозволяємо видалити останній масив
    if (arrays.length <= 1) {
        return;
    }
    
    // Видаляємо масив
    array.remove();
    
    // Перенумеровуємо масиви
    const remainingArrays = container.querySelectorAll('.panel-array');
    remainingArrays.forEach((array, index) => {
        const arrayId = index + 1;
        array.dataset.arrayId = arrayId;
        
        // Оновлюємо заголовок
        const header = array.querySelector('h4');
        if (header) {
            header.textContent = `Масив #${arrayId}`;
        }
        
        // Оновлюємо ID та назви полів
        const rowsInput = array.querySelector('input[id^="rows_"]');
        const panelsInput = array.querySelector('input[id^="panels_per_row_"]');
        
        if (rowsInput) {
            rowsInput.id = `rows_${arrayId}`;
            rowsInput.name = `rows_${arrayId}`;
        }
        
        if (panelsInput) {
            panelsInput.id = `panels_per_row_${arrayId}`;
            panelsInput.name = `panels_per_row_${arrayId}`;
        }
        
        // Приховуємо кнопку видалення для першого масиву, якщо він єдиний
        if (remainingArrays.length === 1 && index === 0) {
            const removeBtn = array.querySelector('.remove-array-btn');
            if (removeBtn) {
                removeBtn.style.display = 'none';
            }
        }
    });
    
    calculateTotalPanels();
}

// Підготовка даних форми перед відправкою
function prepareFormData() {
    // Збираємо дані про масиви панелей для передачі на сервер
    const panelArraysData = [];
    const arrays = document.querySelectorAll('.panel-array');
    
    arrays.forEach(array => {
        const arrayId = array.dataset.arrayId;
        const rows = parseInt(document.getElementById(`rows_${arrayId}`).value) || 0;
        const panelsPerRow = parseInt(document.getElementById(`panels_per_row_${arrayId}`).value) || 0;
        
        panelArraysData.push({
            id: arrayId,
            rows: rows,
            panels_per_row: panelsPerRow,
            total: rows * panelsPerRow
        });
    });
    
    // Додаємо дані про масиви панелей до прихованого поля
    const panelArraysInput = document.createElement('input');
    panelArraysInput.type = 'hidden';
    panelArraysInput.name = 'panel_arrays';
    panelArraysInput.value = JSON.stringify(panelArraysData);
    document.getElementById('calculator-form').appendChild(panelArraysInput);
    
    return true;
}

function downloadDatasheet() {
    const datasheetBtn = document.getElementById('datasheet-btn');
    const panelId = datasheetBtn.getAttribute('data-panel-id');
    
    if (panelId) {
        // Відкриваємо нове вікно з URL для завантаження datasheet
        window.open(`/panels/datasheet/${panelId}/`, '_blank');
    }
}

function downloadInverterDatasheet() {
    const datasheetBtn = document.getElementById('inverter-datasheet-btn');
    const inverterId = datasheetBtn.getAttribute('data-inverter-id');
    
    if (inverterId) {
        // Відкриваємо нове вікно з URL для завантаження datasheet
        window.open(`/inverters/datasheet/${inverterId}/`, '_blank');
    }
}

function downloadBatteryDatasheet() {
    const datasheetBtn = document.getElementById('battery-datasheet-btn');
    const batteryId = datasheetBtn.getAttribute('data-battery-id');
    
    if (batteryId) {
        // Відкриваємо нове вікно з URL для завантаження datasheet
        window.open(`/batteries/datasheet/${batteryId}/`, '_blank');
    }
}

// Функція для оновлення іконки орієнтації
function updateOrientationIcon() {
    // Знаходимо всі селектори орієнтації на сторінці
    let orientationSelects = document.querySelectorAll('select[id^="array_orientation_"], select#orientation');
    
    // Обробляємо кожен знайдений селектор
    orientationSelects.forEach(orientationSelect => {
        let orientationIcon;
        let arrayId = '';
        
        // Визначаємо ID іконки в залежності від ID селектора
        if (orientationSelect.id === 'orientation') {
            // Для основного селектора орієнтації
            orientationIcon = document.getElementById('orientation-icon');
        } else {
            // Для селекторів масивів, отримуємо ID масиву з ID селектора
            arrayId = orientationSelect.id.replace('array_orientation_', '');
            orientationIcon = document.getElementById(`orientation-icon-${arrayId}`);
            
            // Якщо не знайдено іконку з ID orientation-icon-{arrayId}, спробуємо знайти основну іконку
            if (!orientationIcon && arrayId === '1') {
                orientationIcon = document.getElementById('orientation-icon');
            }
        }
        
        // Перевіряємо чи знайдена іконка
        if (orientationIcon) {
            // Встановлюємо клас в залежності від обраної орієнтації
            if (orientationSelect.value === 'альбомна') {
                orientationIcon.className = 'orientation-icon landscape';
                orientationIcon.style.width = '30px';
                orientationIcon.style.height = '20px';
                
                // Оновлюємо стилі для внутрішніх елементів
                let panelIcon;
                let panelIconInner;
                
                if (arrayId) {
                    // Для масивів використовуємо класи з суфіксом _arrayId
                    panelIcon = orientationIcon.querySelector(`.panel-icon_${arrayId}`);
                    panelIconInner = orientationIcon.querySelector(`.panel-icon-inner_${arrayId}`);
                    
                    // Якщо не знайдено, спробуємо знайти без суфікса
                    if (!panelIcon) {
                        panelIcon = orientationIcon.querySelector('.panel-icon');
                    }
                    if (!panelIconInner) {
                        panelIconInner = orientationIcon.querySelector('.panel-icon-inner');
                    }
                } else {
                    // Для основного селектора використовуємо класи без суфікса
                    panelIcon = orientationIcon.querySelector('.panel-icon');
                    panelIconInner = orientationIcon.querySelector('.panel-icon-inner');
                }
                
                if (panelIcon) {
                    panelIcon.style.width = '40px';
                    panelIcon.style.height = '30px';
                }
                
                if (panelIconInner) {
                    panelIconInner.style.width = '30px';
                    panelIconInner.style.height = '20px';
                }
            } else {
                orientationIcon.className = 'orientation-icon portrait';
                orientationIcon.style.width = '20px';
                orientationIcon.style.height = '30px';
                
                // Оновлюємо стилі для внутрішніх елементів
                let panelIcon;
                let panelIconInner;
                
                if (arrayId) {
                    // Для масивів використовуємо класи з суфіксом _arrayId
                    panelIcon = orientationIcon.querySelector(`.panel-icon_${arrayId}`);
                    panelIconInner = orientationIcon.querySelector(`.panel-icon-inner_${arrayId}`);
                    
                    // Якщо не знайдено, спробуємо знайти без суфікса
                    if (!panelIcon) {
                        panelIcon = orientationIcon.querySelector('.panel-icon');
                    }
                    if (!panelIconInner) {
                        panelIconInner = orientationIcon.querySelector('.panel-icon-inner');
                    }
                } else {
                    // Для основного селектора використовуємо класи без суфікса
                    panelIcon = orientationIcon.querySelector('.panel-icon');
                    panelIconInner = orientationIcon.querySelector('.panel-icon-inner');
                }
                
                if (panelIcon) {
                    panelIcon.style.width = '30px';
                    panelIcon.style.height = '40px';
                }
                
                if (panelIconInner) {
                    panelIconInner.style.width = '20px';
                    panelIconInner.style.height = '30px';
                }
            }
        }
    });
}

// Функція для відображення/приховування параметрів наземного розміщення
function toggleGroundMountingParams() {
    console.log("toggleGroundMountingParams викликано");
    const groundMountingCheckbox = document.getElementById('ground_mounting');
    const groundMountingParams = document.getElementById('ground_mounting_params');
    const profileCarcaseLengthsContainer = document.getElementById('profile_carcase_lengths_container');
    
    console.log("Чекбокс:", groundMountingCheckbox);
    console.log("Параметри:", groundMountingParams);
    console.log("Стан чекбоксу:", groundMountingCheckbox ? groundMountingCheckbox.checked : "не знайдено");
    
    if (groundMountingCheckbox) {
        if (groundMountingCheckbox.checked) {
            console.log("Показуємо параметри");
            if (groundMountingParams) {
                groundMountingParams.style.display = 'block';
            }
            if (profileCarcaseLengthsContainer) {
                profileCarcaseLengthsContainer.style.display = 'flex';
            }
        } else {
            console.log("Приховуємо параметри");
            if (groundMountingParams) {
                groundMountingParams.style.display = 'none';
            }
            if (profileCarcaseLengthsContainer) {
                profileCarcaseLengthsContainer.style.display = 'none';
            }
        }
    } else {
        console.log("Елементи не знайдено");
    }
    
    // Оновлюємо всі існуючі масиви панелей
    updateArraysGroundMountingFields();
    
    // Додатково застосовуємо стилі до всіх полів наземного розміщення
    setTimeout(function() {
        const allGroundMountingFields = document.querySelectorAll('.ground-mounting-fields');
        allGroundMountingFields.forEach(field => {
            field.style.display = 'flex';
            field.style.flexDirection = 'row';
            field.style.flexWrap = 'wrap';
            field.style.gap = '15px';
            field.style.width = '100%';
            
            // Стилізуємо всі групи полів всередині
            const formGroups = field.querySelectorAll('.form-group');
            formGroups.forEach(group => {
                group.style.flex = '1 1 150px';
                group.style.minWidth = '150px';
                group.style.marginBottom = '0';
                
                // Стилізуємо всі поля вводу всередині
                const inputs = group.querySelectorAll('input, select');
                inputs.forEach(input => {
                    input.style.width = '100%';
                });
            });
        });
        
        console.log("Застосовано додаткові стилі до всіх полів наземного розміщення");
    }, 100); // Невелика затримка для гарантії, що DOM оновлено
}

// Функція для оновлення полів наземного розміщення у всіх масивах панелей
function updateArraysGroundMountingFields() {
    const groundMountingEnabled = document.getElementById('ground_mounting') && 
                                 document.getElementById('ground_mounting').checked;
    
    console.log("updateArraysGroundMountingFields викликано, наземне розміщення: " + groundMountingEnabled);
    
    // Отримуємо всі масиви панелей
    const arrays = document.querySelectorAll('.panel-array');
    
    arrays.forEach(array => {
        const arrayId = array.dataset.arrayId;
        const arrayContent = array.querySelector('.array-content');
        
        // Видаляємо існуючі поля наземного розміщення (всі можливі класи)
        const existingFields = array.querySelectorAll('.array-ground-mounting, .ground-mounting-container, .ground-mounting-wrapper');
        existingFields.forEach(field => field.remove());
        
        // Якщо наземне розміщення активовано, додаємо нові поля
        if (groundMountingEnabled) {
            // Створюємо контейнер для полів
            const groundMountingWrapper = document.createElement('div');
            groundMountingWrapper.className = 'ground-mounting-wrapper';
            groundMountingWrapper.style.width = '100%';
            
            // Створюємо HTML для полів
            const groundMountingContainer = document.createElement('div');
            groundMountingContainer.className = 'ground-mounting-container';
            
            // Створюємо заголовок
            const title = document.createElement('div');
            title.className = 'ground-mounting-title';
            title.innerHTML = '<i class="fas fa-mountain"></i> Параметри наземного розміщення';
            groundMountingContainer.appendChild(title);
            
            // Створюємо контейнер для полів
            const fieldsContainer = document.createElement('div');
            fieldsContainer.className = 'ground-mounting-fields';
            fieldsContainer.style.display = 'flex';
            fieldsContainer.style.flexDirection = 'row';
            fieldsContainer.style.flexWrap = 'wrap';
            fieldsContainer.style.gap = '15px';
            fieldsContainer.style.width = '100%';
            
            // Додаємо поля
            // 1. Висота конструкції
            const heightGroup = document.createElement('div');
            heightGroup.className = 'form-group';
            heightGroup.style.flex = '1 1 150px';
            heightGroup.style.minWidth = '150px';
            heightGroup.style.marginBottom = '0';
            
            const heightLabel = document.createElement('label');
            heightLabel.htmlFor = `mounting_height_${arrayId}`;
            heightLabel.innerHTML = '<i class="fas fa-arrows-alt-v"></i> Висота конструкції (м):';
            heightGroup.appendChild(heightLabel);
            
            const heightInput = document.createElement('input');
            heightInput.type = 'number';
            heightInput.id = `mounting_height_${arrayId}`;
            heightInput.name = `mounting_height_${arrayId}`;
            heightInput.value = '1';
            heightInput.min = '0.1';
            heightInput.step = '0.1';
            heightInput.style.width = '100%';
            heightGroup.appendChild(heightInput);
            
            fieldsContainer.appendChild(heightGroup);
            
            // 2. Кут нахилу
            const angleGroup = document.createElement('div');
            angleGroup.className = 'form-group';
            angleGroup.style.flex = '1 1 150px';
            angleGroup.style.minWidth = '150px';
            angleGroup.style.marginBottom = '0';
            
            const angleLabel = document.createElement('label');
            angleLabel.htmlFor = `mounting_angle_${arrayId}`;
            angleLabel.innerHTML = '<i class="fas fa-ruler-combined"></i> Кут нахилу (градусів):';
            angleGroup.appendChild(angleLabel);
            
            const angleInput = document.createElement('input');
            angleInput.type = 'number';
            angleInput.id = `mounting_angle_${arrayId}`;
            angleInput.name = `mounting_angle_${arrayId}`;
            angleInput.value = '30';
            angleInput.min = '0';
            angleInput.max = '90';
            angleInput.step = '1';
            angleInput.style.width = '100%';
            angleGroup.appendChild(angleInput);
            
            fieldsContainer.appendChild(angleGroup);
            
            // 3. Відстань між стовпцями
            const distanceGroup = document.createElement('div');
            distanceGroup.className = 'form-group';
            distanceGroup.style.flex = '1 1 150px';
            distanceGroup.style.minWidth = '150px';
            distanceGroup.style.marginBottom = '0';
            
            const distanceLabel = document.createElement('label');
            distanceLabel.htmlFor = `column_distance_${arrayId}`;
            distanceLabel.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Відстань між стовпцями (м):';
            distanceGroup.appendChild(distanceLabel);
            
            const distanceInput = document.createElement('input');
            distanceInput.type = 'number';
            distanceInput.id = `column_distance_${arrayId}`;
            distanceInput.name = `column_distance_${arrayId}`;
            distanceInput.value = '2';
            distanceInput.min = '0.5';
            distanceInput.step = '0.1';
            distanceInput.style.width = '100%';
            distanceGroup.appendChild(distanceInput);
            
            fieldsContainer.appendChild(distanceGroup);
            
            // 4. Матеріал каркасу
            const materialGroup = document.createElement('div');
            materialGroup.className = 'form-group';
            materialGroup.style.flex = '1 1 150px';
            materialGroup.style.minWidth = '150px';
            materialGroup.style.marginBottom = '0';
            
            const materialLabel = document.createElement('label');
            materialLabel.htmlFor = `frame_material_${arrayId}`;
            materialLabel.innerHTML = '<i class="fas fa-cubes"></i> Матеріал каркасу:';
            materialGroup.appendChild(materialLabel);
            
            const materialSelect = document.createElement('select');
            materialSelect.id = `frame_material_${arrayId}`;
            materialSelect.name = `frame_material_${arrayId}`;
            materialSelect.style.width = '100%';
            
            const materialOption1 = document.createElement('option');
            materialOption1.value = 'оцинкований';
            materialOption1.textContent = 'Оцинкований';
            materialSelect.appendChild(materialOption1);
            
            const materialOption2 = document.createElement('option');
            materialOption2.value = 'алюміній';
            materialOption2.textContent = 'Алюміній';
            materialSelect.appendChild(materialOption2);
            
            const materialOption3 = document.createElement('option');
            materialOption3.value = 'залізо';
            materialOption3.textContent = 'Залізо';
            materialSelect.appendChild(materialOption3);
            
            materialGroup.appendChild(materialSelect);
            fieldsContainer.appendChild(materialGroup);
            
            // 5. Тип основи
            const foundationGroup = document.createElement('div');
            foundationGroup.className = 'form-group';
            foundationGroup.style.flex = '1 1 150px';
            foundationGroup.style.minWidth = '150px';
            foundationGroup.style.marginBottom = '0';
            
            const foundationLabel = document.createElement('label');
            foundationLabel.htmlFor = `foundation_type_${arrayId}`;
            foundationLabel.innerHTML = '<i class="fas fa-hammer"></i> Тип основи:';
            foundationGroup.appendChild(foundationLabel);
            
            const foundationSelect = document.createElement('select');
            foundationSelect.id = `foundation_type_${arrayId}`;
            foundationSelect.name = `foundation_type_${arrayId}`;
            foundationSelect.style.width = '100%';
            
            const foundationOption1 = document.createElement('option');
            foundationOption1.value = 'забивна палка';
            foundationOption1.textContent = 'Забивна палка';
            foundationSelect.appendChild(foundationOption1);
            
            const foundationOption2 = document.createElement('option');
            foundationOption2.value = 'геошуруп';
            foundationOption2.textContent = 'Геошуруп';
            foundationSelect.appendChild(foundationOption2);
            
            const foundationOption3 = document.createElement('option');
            foundationOption3.value = 'бетонування';
            foundationOption3.textContent = 'Бетонування';
            foundationSelect.appendChild(foundationOption3);
            
            foundationGroup.appendChild(foundationSelect);
            fieldsContainer.appendChild(foundationGroup);
            
            // Додаємо контейнер полів до контейнера наземного розміщення
            groundMountingContainer.appendChild(fieldsContainer);
            
            // Додаємо контейнер наземного розміщення до обгортки
            groundMountingWrapper.appendChild(groundMountingContainer);
            
            // Додаємо обгортку до контенту масиву
            arrayContent.appendChild(groundMountingWrapper);
        }
    });
    
    console.log("Оновлено поля наземного розміщення для всіх масивів, кількість масивів: " + arrays.length);
}

// Функція для очищення форми
function resetForm() {
    // Підтвердження від користувача
    if (!confirm("Ви впевнені, що хочете очистити всі параметри форми?")) {
        return;
    }
    
    // Очищаємо всі поля форми
    document.getElementById('calculator-form').reset();
    
    // Скидаємо селекти до початкового стану
    updateModelOptions();
    updateInverterOptions();
    updateBatteryOptions();
    
    // Оновлюємо іконку орієнтації
    updateOrientationIcon();
    
    // Оновлюємо стан параметрів наземного розміщення
    toggleGroundMountingParams();
    
    // Оновлюємо загальну кількість панелей
    calculateTotalPanels();
    
    // Відображаємо повідомлення про успішне очищення
    alert("Параметри форми очищено!");
}

// Ініціалізуємо сторінку при завантаженні
document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізуємо селекти та обробники подій
    updateModelOptions();
    updateInverterOptions();
    updateBatteryOptions();
    
    // Ініціалізуємо іконку орієнтації
    updateOrientationIcon();
    
    // Додаємо обробник для зміни орієнтації
    const orientationElement = document.getElementById('orientation');
    if (orientationElement) {
        orientationElement.addEventListener('change', updateOrientationIcon);
    }
    
    // Додаємо обробник для array_orientation_1
    const arrayOrientationElement = document.getElementById('array_orientation_1');
    if (arrayOrientationElement) {
        arrayOrientationElement.addEventListener('change', updateOrientationIcon);
    }
    
    // Додаємо обробник для чекбоксу наземного розміщення
    const groundMountingCheckbox = document.getElementById('ground_mounting');
    if (groundMountingCheckbox) {
        groundMountingCheckbox.addEventListener('change', toggleGroundMountingParams);
        console.log("Встановлено обробник подій для чекбоксу наземного розміщення");
    }
    
    // Ініціалізуємо поля наземного розміщення
    toggleGroundMountingParams();
    
    // Ініціалізуємо загальну кількість панелей
    calculateTotalPanels();
});

// Функція для оновлення іконки орієнтації масиву
function updateArrayOrientationIcon(arrayId) {
    const orientationSelect = document.getElementById(`array_orientation_${arrayId}`);
    const orientationIcon = document.getElementById(`orientation-icon-${arrayId}`);
    
    if (orientationSelect && orientationIcon) {
        // Встановлюємо клас в залежності від обраної орієнтації
        if (orientationSelect.value === 'альбомна') {
            orientationIcon.className = 'orientation-icon landscape';
            orientationIcon.style.width = '30px';
            orientationIcon.style.height = '20px';
        } else {
            orientationIcon.className = 'orientation-icon portrait';
            orientationIcon.style.width = '20px';
            orientationIcon.style.height = '30px';
        }
    }
}

function calculateArrayTotal(arrayId) {
    const rows = parseInt(document.getElementById(`rows_${arrayId}`).value) || 0;
    const panelsPerRow = parseInt(document.getElementById(`panels_per_row_${arrayId}`).value) || 0;
    return rows * panelsPerRow;
}
