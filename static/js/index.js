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
    
    // Створюємо новий масив
    const newArray = document.createElement('div');
    newArray.className = 'panel-array';
    newArray.dataset.arrayId = newArrayId;
    
    // Створюємо заголовок масиву
    const arrayHeader = document.createElement('div');
    arrayHeader.className = 'array-header';
    
    const arrayTitle = document.createElement('h4');
    arrayTitle.textContent = `Масив #${newArrayId}`;
    arrayHeader.appendChild(arrayTitle);
    
    // Додаємо поле для назви масиву
    const arrayNameInput = document.createElement('input');
    arrayNameInput.type = 'text';
    arrayNameInput.className = 'array-name-input';
    arrayNameInput.id = `array_name_${newArrayId}`;
    arrayNameInput.name = `array_name_${newArrayId}`;
    arrayNameInput.placeholder = 'Назва масиву';
    arrayNameInput.value = '';
    arrayHeader.appendChild(arrayNameInput);
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.name = 'remove-array-btn';
    removeButton.setAttribute('onclick', 'removeArray(this)');
    removeButton.innerHTML = '<i class="fas fa-times"></i>';
    arrayHeader.appendChild(removeButton);
    
    newArray.appendChild(arrayHeader);
    
    // Створюємо контент масиву
    const arrayContent = document.createElement('div');
    arrayContent.className = 'array-content';
    
    // Додаємо поля для кількості рядів
    const rowsGroup = document.createElement('div');
    rowsGroup.className = 'form-group';
    
    const rowsLabel = document.createElement('label');
    rowsLabel.setAttribute('for', `rows_${newArrayId}`);
    rowsLabel.innerHTML = '<i class="fas fa-grip-lines"></i> Кількість рядів:';
    rowsGroup.appendChild(rowsLabel);
    
    const rowsInput = document.createElement('input');
    rowsInput.type = 'number';
    rowsInput.id = `rows_${newArrayId}`;
    rowsInput.name = `rows_${newArrayId}`;
    rowsInput.value = '2';
    rowsInput.required = true;
    rowsInput.min = '1';
    rowsInput.setAttribute('onchange', 'calculateTotalPanels()');
    rowsGroup.appendChild(rowsInput);
    
    arrayContent.appendChild(rowsGroup);
    
    // Додаємо поля для кількості панелей на ряд
    const panelsGroup = document.createElement('div');
    panelsGroup.className = 'form-group';
    
    const panelsLabel = document.createElement('label');
    panelsLabel.setAttribute('for', `panels_per_row_${newArrayId}`);
    panelsLabel.innerHTML = '<i class="fas fa-grip-lines-vertical"></i> Кількість панелей на ряд:';
    panelsGroup.appendChild(panelsLabel);
    
    const panelsInput = document.createElement('input');
    panelsInput.type = 'number';
    panelsInput.id = `panels_per_row_${newArrayId}`;
    panelsInput.name = `panels_per_row_${newArrayId}`;
    panelsInput.value = '3';
    panelsInput.required = true;
    panelsInput.min = '1';
    panelsInput.setAttribute('onchange', 'calculateTotalPanels()');
    panelsGroup.appendChild(panelsInput);
    
    arrayContent.appendChild(panelsGroup);
    
    // Додаємо поле для відображення загальної кількості панелей у масиві
    const totalGroup = document.createElement('div');
    totalGroup.className = 'form-group';
    
    const totalLabel = document.createElement('label');
    totalLabel.innerHTML = '<i class="fas fa-calculator"></i> Панелей у масиві:';
    totalGroup.appendChild(totalLabel);
    
    const totalSpan = document.createElement('span');
    totalSpan.className = 'array-total';
    totalSpan.textContent = '6';
    totalGroup.appendChild(totalSpan);
    
    arrayContent.appendChild(totalGroup);
    
    // Якщо активовано наземне розміщення, додаємо поля для параметрів
    if (groundMountingEnabled) {
        // Створюємо контейнер для полів наземного розміщення
        const groundMountingWrapper = document.createElement('div');
        groundMountingWrapper.className = 'ground-mounting-wrapper';
        
        // Створюємо контейнер для полів
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
        
        // Додаємо поля
        // 1. Висота конструкції
        const heightGroup = document.createElement('div');
        heightGroup.className = 'form-group';
        
        const heightLabel = document.createElement('label');
        heightLabel.htmlFor = `mounting_height_${newArrayId}`;
        heightLabel.innerHTML = '<i class="fas fa-arrows-alt-v"></i> Висота конструкції (м):';
        heightGroup.appendChild(heightLabel);
        
        const heightInput = document.createElement('input');
        heightInput.type = 'number';
        heightInput.id = `mounting_height_${newArrayId}`;
        heightInput.name = `mounting_height_${newArrayId}`;
        heightInput.value = '1';
        heightInput.min = '0.1';
        heightInput.step = '0.1';
        heightGroup.appendChild(heightInput);
        
        fieldsContainer.appendChild(heightGroup);
        
        // 2. Кут нахилу
        const angleGroup = document.createElement('div');
        angleGroup.className = 'form-group';
        
        const angleLabel = document.createElement('label');
        angleLabel.htmlFor = `mounting_angle_${newArrayId}`;
        angleLabel.innerHTML = '<i class="fas fa-ruler-combined"></i> Кут нахилу (градусів):';
        angleGroup.appendChild(angleLabel);
        
        const angleInput = document.createElement('input');
        angleInput.type = 'number';
        angleInput.id = `mounting_angle_${newArrayId}`;
        angleInput.name = `mounting_angle_${newArrayId}`;
        angleInput.value = '30';
        angleInput.min = '0';
        angleInput.max = '90';
        angleInput.step = '1';
        angleGroup.appendChild(angleInput);
        
        fieldsContainer.appendChild(angleGroup);
        
        // 3. Відстань між стовпцями
        const distanceGroup = document.createElement('div');
        distanceGroup.className = 'form-group';
        
        const distanceLabel = document.createElement('label');
        distanceLabel.htmlFor = `column_distance_${newArrayId}`;
        distanceLabel.innerHTML = '<i class="fas fa-arrows-alt-h"></i> Відстань між стовпцями (м):';
        distanceGroup.appendChild(distanceLabel);
        
        const distanceInput = document.createElement('input');
        distanceInput.type = 'number';
        distanceInput.id = `column_distance_${newArrayId}`;
        distanceInput.name = `column_distance_${newArrayId}`;
        distanceInput.value = '2';
        distanceInput.min = '0.5';
        distanceInput.step = '0.1';
        distanceGroup.appendChild(distanceInput);
        
        fieldsContainer.appendChild(distanceGroup);
        
        // 4. Матеріал каркасу
        const materialGroup = document.createElement('div');
        materialGroup.className = 'form-group';
        
        const materialLabel = document.createElement('label');
        materialLabel.htmlFor = `frame_material_${newArrayId}`;
        materialLabel.innerHTML = '<i class="fas fa-cubes"></i> Матеріал каркасу:';
        materialGroup.appendChild(materialLabel);
        
        const materialSelect = document.createElement('select');
        materialSelect.id = `frame_material_${newArrayId}`;
        materialSelect.name = `frame_material_${newArrayId}`;
        
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
        
        const foundationLabel = document.createElement('label');
        foundationLabel.htmlFor = `foundation_type_${newArrayId}`;
        foundationLabel.innerHTML = '<i class="fas fa-hammer"></i> Тип основи:';
        foundationGroup.appendChild(foundationLabel);
        
        const foundationSelect = document.createElement('select');
        foundationSelect.id = `foundation_type_${newArrayId}`;
        foundationSelect.name = `foundation_type_${newArrayId}`;
        
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
    
    newArray.appendChild(arrayContent);
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
