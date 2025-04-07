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
    
    if (selectedOption && selectedOption.value) {
        // Оновлюємо деталі інвертора
        document.getElementById('inverter_power').value = selectedOption.dataset.power;
        document.getElementById('inverter_power').readOnly = true;
        document.getElementById('inverter_phases').value = selectedOption.dataset.phases_count;
        
        // Активуємо кнопку завантаження datasheet
        datasheetBtn.disabled = false;
        
        // Зберігаємо ID інвертора як атрибут кнопки для використання в downloadInverterDatasheet()
        datasheetBtn.setAttribute('data-inverter-id', selectedOption.value);
    } else {
        // Деактивуємо кнопку, якщо модель не вибрана
        datasheetBtn.disabled = true;
        document.getElementById('inverter_power').readOnly = false;
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
    
    if (selectedOption && selectedOption.value) {
        // Оновлюємо деталі батареї
        document.getElementById('battery_capacity').value = selectedOption.dataset.capacity;
        document.getElementById('battery_capacity').readOnly = true;
        
        // Встановлюємо значення чекбоксів
        document.getElementById('battery_is_head').checked = selectedOption.dataset.is_head === 'true';
        document.getElementById('battery_is_stand_8').checked = selectedOption.dataset.is_stand === 'true';
        document.getElementById('battery_is_stand_12').checked = selectedOption.dataset.is_stand === 'true';
        
        // Активуємо кнопку завантаження datasheet незалежно від стану чекбоксів
        datasheetBtn.disabled = false;
        
        // Зберігаємо ID батареї як атрибут кнопки для використання в downloadBatteryDatasheet()
        datasheetBtn.setAttribute('data-battery-id', selectedOption.value);
    } else {
        // Деактивуємо кнопку, якщо модель не вибрана
        datasheetBtn.disabled = true;
        document.getElementById('battery_capacity').readOnly = false;
        
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
        document.getElementById('panel_length').value = selectedOption.dataset.length;
        document.getElementById('panel_width').value = selectedOption.dataset.width;
        document.getElementById('panel_height').value = selectedOption.dataset.height;
        
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
    
    // Створюємо новий масив
    const newArray = document.createElement('div');
    newArray.className = 'panel-array';
    newArray.dataset.arrayId = newArrayId;
    
    newArray.innerHTML = `
        <div class="array-header">
            <h4>Масив #${newArrayId}</h4>
            <button type="button" class="remove-array-btn" onclick="removeArray(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="array-content">
            <div class="form-group">
                <label for="rows_${newArrayId}"><i class="fas fa-grip-lines"></i> Кількість рядів:</label>
                <input type="number" id="rows_${newArrayId}" name="rows_${newArrayId}" value="2" required min="1" onchange="calculateTotalPanels()">
            </div>
            <div class="form-group">
                <label for="panels_per_row_${newArrayId}"><i class="fas fa-grip-lines-vertical"></i> Кількість панелей на ряд:</label>
                <input type="number" id="panels_per_row_${newArrayId}" name="panels_per_row_${newArrayId}" value="3" required min="1" onchange="calculateTotalPanels()">
            </div>
            <div class="form-group">
                <label><i class="fas fa-calculator"></i> Панелей у масиві:</label>
                <span class="array-total">6</span>
            </div>
        </div>
    `;
    
    container.appendChild(newArray);
    
    // Показуємо кнопку видалення для першого масиву, якщо тепер є більше одного масиву
    if (arrays.length === 1) {
        const firstArrayRemoveBtn = arrays[0].querySelector('.remove-array-btn');
        if (firstArrayRemoveBtn) {
            firstArrayRemoveBtn.style.display = 'block';
        }
    }
    
    calculateTotalPanels();
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

// Функція для оновлення іконки орієнтації панелей
function updateOrientationIcon() {
    const orientationSelect = document.getElementById('orientation');
    const orientationIcon = document.getElementById('orientation-icon');
    
    // Встановлюємо клас в залежності від обраної орієнтації
    if (orientationSelect.value === 'альбомна') {
        orientationIcon.className = 'orientation-icon landscape';
    } else {
        orientationIcon.className = 'orientation-icon portrait';
    }
}

// Ініціалізуємо іконку при завантаженні сторінки
document.addEventListener('DOMContentLoaded', function() {
    updateOrientationIcon();
    
    // Додаємо обробник події для зміни орієнтації
    document.getElementById('orientation').addEventListener('change', updateOrientationIcon);
});

// Ініціалізуємо загальну кількість панелей при завантаженні сторінки
calculateTotalPanels();

// Обробник для кнопки очищення параметрів
document.getElementById('reset-form-btn').addEventListener('click', function() {
    // Отримуємо всі елементи форми
    const form = document.getElementById('calculator-form');
    
    // Скидаємо значення для всіх полів вводу
    const inputs = form.querySelectorAll('input[type="text"], input[type="number"], input[type="email"], textarea');
    inputs.forEach(input => {
        // Встановлюємо значення за замовчуванням, якщо воно є
        if (input.hasAttribute('data-default')) {
            input.value = input.getAttribute('data-default');
        } else {
            // Інакше просто очищаємо
            input.value = input.defaultValue || '';
        }
    });
    
    // Скидаємо значення для всіх випадаючих списків
    const selects = form.querySelectorAll('select');
    selects.forEach(select => {
        // Встановлюємо перший елемент як вибраний
        select.selectedIndex = 0;
        
        // Якщо це select для моделі панелі, оновлюємо його
        if (select.id === 'panel_model') {
            updateModelOptions();
        }
        if (select.id === 'inverter_model') {
            updateInverterModelOptions();
        }
        if (select.id === 'battery_model') {
            updateBatteryModelOptions();
        }
    });
    
    // Скидаємо значення для всіх чекбоксів і радіокнопок
    const checkboxes = form.querySelectorAll('input[type="checkbox"], input[type="radio"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checkbox.defaultChecked;
    });
    
    // Оновлюємо залежні поля
    updatePanelDimensions();
    
    // Приховуємо поля для ручного введення моделей
    document.getElementById('custom-model-container').style.display = 'none';
    document.getElementById('custom-inverter-model-container').style.display = 'none';
    document.getElementById('custom-battery-model-container').style.display = 'none';
    
    // Відображаємо повідомлення про успішне очищення
    alert('Параметри форми очищено!');
});
