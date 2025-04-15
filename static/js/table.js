// Функція для обчислення суми в рядку
function calculateRowSum(row) {
    // Знаходимо всі інпути в рядку
    const inputs = row.querySelectorAll('input[type="number"]');
    
    // Знаходимо інпути для кількості, ціни та суми
    let quantityInput = null;
    let priceInput = null;
    let sumInput = null;
    let isProfileRow = false;
    let profileLength = 1;
    
    // Визначаємо інпути за їх атрибутами name
    inputs.forEach(input => {
        const name = input.name;
        
        // Перевіряємо, чи це інпут для кількості профілю (починається з K11_ або K71_)
        if (name.startsWith('K11_') || name.startsWith('K71_')) {
            isProfileRow = true;
            // Витягуємо довжину профілю з імені інпута (K11_3 -> 3 або K71_3 -> 3)
            const lengthMatch = name.match(/K\d+_(\d+\.?\d*)/);
            if (lengthMatch) {
                profileLength = parseFloat(lengthMatch[1]) || 1;
            }
            quantityInput = input;
        }
        // Перевіряємо, чи це інпут для кількості (3-й символ == 1)
        else if (name.length >= 3 && name.charAt(2) === '1' && !name.startsWith('Z')) {
            quantityInput = input;
        }
        
        // Перевіряємо, чи це інпут для ціни профілю (починається з K12_ або K72_)
        if (name.startsWith('K12_') || name.startsWith('K72_')) {
            priceInput = input;
        }
        // Перевіряємо, чи це інпут для ціни (3-й символ == 2)
        else if (name.length >= 3 && name.charAt(2) === '2' && !name.startsWith('Z')) {
            priceInput = input;
        }
        
        // Перевіряємо, чи це інпут для суми профілю (починається з K13_ або K73_)
        if (name.startsWith('K13_') || name.startsWith('K73_')) {
            sumInput = input;
        }
        // Перевіряємо, чи це інпут для суми (3-й символ == 3)
        else if (name.length >= 3 && name.charAt(2) === '3' && !name.startsWith('Z')) {
            sumInput = input;
        }
    });
    
    // Якщо знайдені всі потрібні інпути, обчислюємо суму
    if (quantityInput && priceInput && sumInput) {
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        
        let sum = 0;
        
        if (isProfileRow) {
            // Для профілю: кількість * ціна * метри
            sum = quantity * price * profileLength;
            console.log('Профіль, Довжина:', profileLength, 'Кількість:', quantity, 'Ціна:', price, 'Сума:', sum);
        } else if (sumInput.hasAttribute('data-length')) {
            // Для профілю120: кількість * ціна * метри (використовуємо атрибут data-length)
            const length = parseFloat(sumInput.getAttribute('data-length')) || 1;
            sum = quantity * price * length;
            console.log('Профіль120, Довжина:', length, 'Кількість:', quantity, 'Ціна:', price, 'Сума:', sum);
        } else {
            // Для інших рядків: кількість * ціна
            sum = quantity * price;
        }
        
        // Встановлюємо обчислену суму в інпут суми
        sumInput.value = sum.toFixed(2);
        
        return sum; // Повертаємо значення суми для використання в інших функціях
    }
    
    return 0; // Повертаємо 0, якщо не вдалося обчислити суму
}

// Функція для обчислення закупки в рядку
function calculatePurchase(row) {
    // Знаходимо всі інпути в рядку
    const inputs = row.querySelectorAll('input[type="number"]');
    
    // Знаходимо інпути для кількості та закупки
    let quantityInput = null;
    let purchaseInput = null;
    let isProfileRow = false;
    let profileLength = 1;
    
    // Визначаємо інпути за їх атрибутами name
    inputs.forEach(input => {
        const name = input.name;
        
        // Перевіряємо, чи це інпут для кількості профілю (починається з K11_ або K71_)
        if (name.startsWith('K11_') || name.startsWith('K71_')) {
            isProfileRow = true;
            // Витягуємо довжину профілю з імені інпута (K11_3 -> 3 або K71_3 -> 3)
            const lengthMatch = name.match(/K\d+_(\d+\.?\d*)/);
            if (lengthMatch) {
                profileLength = parseFloat(lengthMatch[1]) || 1;
            }
            quantityInput = input;
        }
        // Перевіряємо, чи це інпут для кількості (3-й символ == 1)
        else if (name.length >= 3 && name.charAt(2) === '1' && !name.startsWith('Z')) {
            quantityInput = input;
        }
        
        // Перевіряємо, чи це інпут для закупки профілю (починається з Z4_ або Z10_)
        if (name.startsWith('Z4_') || name.startsWith('Z10_')) {
            purchaseInput = input;
        }
        // Перевіряємо, чи це інпут для закупки (починається з "Z")
        else if (name.startsWith('Z')) {
            purchaseInput = input;
        }
    });
    
    // Якщо знайдені всі потрібні інпути, обчислюємо закупку
    if (quantityInput && purchaseInput) {
        const quantity = parseFloat(quantityInput.value) || 0;
        const purchasePrice = parseFloat(purchaseInput.value) || 0;
        
        let totalPurchase = 0;
        
        if (isProfileRow) {
            // Для профілів: кількість * закупка * метри
            totalPurchase = quantity * purchasePrice * profileLength;
            console.log('Профіль закупка, Довжина:', profileLength, 'Кількість:', quantity, 'Закупка:', purchasePrice, 'Загальна закупка:', totalPurchase);
        } else if (purchaseInput.hasAttribute('data-length') || quantityInput.hasAttribute('data-length')) {
            // Для профілю120: кількість * закупка * метри (використовуємо атрибут data-length)
            const length = parseFloat(purchaseInput.getAttribute('data-length') || quantityInput.getAttribute('data-length')) || 1;
            totalPurchase = quantity * purchasePrice * length;
            console.log('Профіль120 закупка, Довжина:', length, 'Кількість:', quantity, 'Закупка:', purchasePrice, 'Загальна закупка:', totalPurchase);
        } else {
            // Для інших рядків: кількість * закупка
            totalPurchase = quantity * purchasePrice;
        }
        
        return totalPurchase; // Повертаємо загальну вартість закупки
    }
    
    return 0;
}

// Функція для обчислення загальної суми та закупки
function calculateTotal() {
    let totalSum = 0;
    let totalPurchase = 0;
    
    // Створюємо об'єкт для зберігання сум по кожній таблиці
    let tableSums = {
        'equipment': 0,
        'mounting': 0,
        'electricity': 0,
        'work': 0
    };
    
    // Отримуємо курс долара з поля вводу
    let usdRate = parseFloat(document.getElementById('usd-rate-input').value.replace(',', '.'));
    
    // Якщо не вдалося отримати з поля вводу, використовуємо значення за замовчуванням
    if (isNaN(usdRate) || usdRate <= 0) {
        usdRate = parseFloat(document.getElementById('hidden-usd-rate').value.replace(',', '.')) || 42.5;
        // Встановлюємо коректне значення в поле вводу
        document.getElementById('usd-rate-input').value = usdRate.toFixed(2);
    }
    
    // Оновлюємо приховане поле з курсом долара для PDF-звіту
    document.getElementById('hidden-usd-rate').value = usdRate.toFixed(2);
    
    // Виводимо у консоль для перевірки
    console.log('Курс долара (число):', usdRate);
    
    // Проходимо по всіх таблицях
    const tables = ['equipment-table', 'mounting-table', 'electricity-table', 'work-table'];
    const tableIds = ['equipment', 'mounting', 'electricity', 'work'];
    
    tables.forEach((tableId, index) => {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        // Проходимо по всіх рядках таблиці
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            // Обчислюємо суму для рядка і додаємо до загальної суми
            const rowSum = calculateRowSum(row);
            totalSum += rowSum;
            
            // Додаємо суму рядка до суми відповідної таблиці
            tableSums[tableIds[index]] += rowSum;
            
            // Обчислюємо закупку для рядка і додаємо до загальної закупки
            const rowPurchase = calculatePurchase(row);
            totalPurchase += rowPurchase;
        });
        
        // Оновлюємо відображення суми для поточної таблиці
        document.getElementById(tableIds[index] + '-sum').textContent = tableSums[tableIds[index]].toFixed(2);
    });
    
    // Обчислюємо прибуток
    const profit = totalSum - totalPurchase;
    
    // Розраховуємо суму в доларах (лише загальна сума без закупки)
    const totalUsdValue = totalSum / usdRate;
    
    // Виводимо у консоль для перевірки
    console.log('Загальна сума (грн):', totalSum);
    console.log('Загальна закупка (грн):', totalPurchase);
    console.log('Прибуток (грн):', profit);
    console.log('Сума в доларах (без закупки):', totalUsdValue);
    
    // Виводимо у консоль суми по кожній таблиці
    console.log('Суми по таблицях:', tableSums);
    
    // Оновлюємо відображення загальних сум
    document.getElementById('total-purchase').textContent = totalPurchase.toFixed(2);
    document.getElementById('total-sum').textContent = totalSum.toFixed(2);
    
    // Оновлюємо відображення прибутку з перевіркою на від'ємне значення
    const profitElement = document.getElementById('profit');
    profitElement.textContent = profit.toFixed(2);
    
    // Змінюємо колір прибутку залежно від значення
    if (profit < 0) {
        profitElement.style.color = 'red'; // Червоний колір для від'ємного прибутку
    } else {
        profitElement.style.color = 'var(--secondary-color)'; // Зелений колір для додатного прибутку
    }
    
    document.getElementById('total-usd').textContent = totalUsdValue.toFixed(2);
    document.getElementById('hidden-total-usd').value = totalUsdValue.toFixed(2);
    
    // Виводимо у консоль значення прихованого інпута
    console.log('Значення прихованого інпута з сумою в доларах:', document.getElementById('hidden-total-usd').value);
    
    // Розраховуємо суму з відсотком, якщо чекбокс активний
    calculatePercentage();
}

// Функція для розрахунку суми з відсотком
function calculatePercentage() {
    const checkbox = document.getElementById('add-percentage-checkbox');
    const percentageInputs = document.getElementById('percentage-inputs');
    const percentageValue = document.getElementById('percentage-value');
    const totalWithPercentage = document.getElementById('total-with-percentage');
    const profitWithPercentage = document.getElementById('profit-with-percentage');
    const totalUsdWithPercentage = document.getElementById('total-usd-with-percentage');
    
    // Перевіряємо, чи всі елементи існують
    if (!checkbox || !percentageInputs || !percentageValue || !totalWithPercentage) {
        return;
    }
    
    // Показуємо/приховуємо поля для відсотка в залежності від стану чекбоксу
    percentageInputs.style.display = checkbox.checked ? 'block' : 'none';
    
    // Якщо чекбокс активний, розраховуємо суму з відсотком
    if (checkbox.checked) {
        const totalSum = parseFloat(document.getElementById('total-sum').textContent) || 0;
        const totalPurchase = parseFloat(document.getElementById('total-purchase').textContent) || 0;
        const percentage = parseFloat(percentageValue.value) || 0;
        const usdRate = parseFloat(document.getElementById('usd-rate-input').value) || 42.5;
        
        // Розраховуємо суму з відсотком
        const sumWithPercentage = totalSum * (1 + percentage / 100);
        
        // Розраховуємо заробіток з відсотком (сума з відсотком - закупка)
        const profitWithPercentageValue = sumWithPercentage - totalPurchase;
        
        // Розраховуємо суму в доларах з відсотком
        const usdWithPercentage = sumWithPercentage / usdRate;
        
        // Оновлюємо відображення суми з відсотком
        totalWithPercentage.textContent = sumWithPercentage.toFixed(2);
        
        // Оновлюємо відображення заробітку з відсотком
        if (profitWithPercentage) {
            profitWithPercentage.textContent = profitWithPercentageValue.toFixed(2);
            
            // Змінюємо колір заробітку залежно від значення
            if (profitWithPercentageValue < 0) {
                profitWithPercentage.style.color = 'red'; // Червоний колір для від'ємного заробітку
            } else {
                profitWithPercentage.style.color = 'var(--secondary-color)'; // Зелений колір для додатного заробітку
            }
        }
        
        // Оновлюємо відображення суми в доларах з відсотком
        if (totalUsdWithPercentage) {
            totalUsdWithPercentage.textContent = usdWithPercentage.toFixed(2);
        }
    }
}

// Функція для збільшення кількості кріплень
function increaseMountingQuantity() {
    const mountingTable = document.getElementById('mounting-table');
    if (!mountingTable) return;
    
    // Отримуємо коефіцієнт збільшення
    const factor = parseFloat(document.getElementById('mounting-quantity-factor').value) || 1.2;
    
    // Проходимо по всіх рядках таблиці кріплень
    const rows = mountingTable.querySelectorAll('tbody tr');
    rows.forEach(row => {
        // Знаходимо інпут для кількості (3-й символ == 1)
        const inputs = row.querySelectorAll('input[type="number"]');
        let quantityInput = null;
        
        inputs.forEach(input => {
            const name = input.name;
            // Перевіряємо, чи це інпут для кількості профілю (починається з K11_ або K71_)
            if (name.startsWith('K11_') || name.startsWith('K71_')) {
                quantityInput = input;
            }
            // Перевіряємо, чи це інпут для кількості (3-й символ == 1)
            else if (name.length >= 3 && name.charAt(2) === '1' && !name.startsWith('Z')) {
                quantityInput = input;
            }
        });
        
        // Якщо знайдено інпут для кількості, збільшуємо його значення
        if (quantityInput) {
            const currentValue = parseFloat(quantityInput.value) || 0;
            const newValue = Math.ceil(currentValue * factor); // Округляємо вгору до цілого числа
            quantityInput.value = newValue;
            
            // Викликаємо функцію обчислення суми для оновлення значень
            calculateRowSum(row);
        }
    });
    
    // Перераховуємо загальну суму
    calculateTotal();
    
    // Показуємо повідомлення про успішне застосування
    alert(`Кількість кріплень збільшена в ${factor} рази`);
}

// Функція для додавання нових рядків
function addNewRow(tableId, prefix, zIndex) {
    const table = document.getElementById(tableId + '-table');
    const tbody = table.querySelector('tbody');
    const rowCount = tbody.querySelectorAll('tr').length + 1;
    
    // Створюємо новий рядок
    const newRow = document.createElement('tr');
    
    // Формуємо правильні індекси для полів
    let nameIndex, quantityIndex, priceIndex, sumIndex;
    
    if (rowCount < 10) {
        // Для рядків 1-9 використовуємо старий формат: К10, К11, К12, К13
        nameIndex = rowCount + '0';
        quantityIndex = rowCount + '1';
        priceIndex = rowCount + '2';
        sumIndex = rowCount + '3';
    } else {
        // Для рядків 10+ використовуємо новий формат: К11n, К12n, К13n
        // де n - номер рядка (для рядка 10: n=0, для рядка 11: n=1, і т.д.)
        const n = rowCount - 10; // Отримуємо зміщення від 10 (0, 1, 2, ...)
        quantityIndex = '11' + n; // prefix + 11 + n для кількості
        priceIndex = '12' + n;    // prefix + 12 + n для ціни
        sumIndex = '13' + n;      // prefix + 13 + n для суми
        nameIndex = '10' + n;     // prefix + 10 + n для назви
    }
    
    // Додаємо комірку для назви
    const nameCell = document.createElement('td');
    const nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.name = prefix + nameIndex; // Додаємо поле для назви
    nameInput.placeholder = 'Назва';
    nameInput.style.fontFamily = "'Montserrat', sans-serif";
    nameInput.style.fontSize = '0.95rem';
    nameCell.appendChild(nameInput);
    
    // Додаємо комірку для кількості
    const quantityCell = document.createElement('td');
    const quantityInput = document.createElement('input');
    quantityInput.type = 'number';
    quantityInput.name = prefix + quantityIndex;
    quantityInput.value = '0';
    quantityInput.addEventListener('input', calculateTotal);
    quantityCell.appendChild(quantityInput);
    
    // Додаємо комірку для одиниці виміру
    const unitCell = document.createElement('td');
    const unitSelect = document.createElement('select');
    unitSelect.name = prefix + rowCount + 'unit';
    unitSelect.style.fontFamily = "'Montserrat', sans-serif";
    unitSelect.style.fontSize = '1rem';
    
    const units = ['шт', 'м', 'компл', 'послуга'];
    units.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit;
        option.textContent = unit;
        unitSelect.appendChild(option);
    });
    
    unitCell.appendChild(unitSelect);
    
    // Додаємо комірку для закупки
    const purchaseCell = document.createElement('td');
    const purchaseInput = document.createElement('input');
    purchaseInput.type = 'number';
    purchaseInput.name = 'Z' + zIndex;
    purchaseInput.value = '0';
    purchaseInput.addEventListener('input', calculateTotal);
    purchaseCell.appendChild(purchaseInput);
    
    // Додаємо комірку для ціни
    const priceCell = document.createElement('td');
    const priceInput = document.createElement('input');
    priceInput.type = 'number';
    priceInput.name = prefix + priceIndex;
    priceInput.value = '0';
    priceInput.addEventListener('input', calculateTotal);
    priceCell.appendChild(priceInput);
    
    // Додаємо комірку для суми
    const sumCell = document.createElement('td');
    const sumInput = document.createElement('input');
    sumInput.type = 'number';
    sumInput.name = prefix + sumIndex;
    sumInput.value = '0';
    sumInput.readOnly = true;
    
    // Створюємо контейнер для суми та кнопки видалення
    const rowActions = document.createElement('div');
    rowActions.className = 'row-actions';
    
    // Додаємо поле суми
    rowActions.appendChild(sumInput);
    
    // Створюємо кнопку видалення
    const deleteBtn = document.createElement('button');
    deleteBtn.type = 'button';
    deleteBtn.className = 'delete-row-btn';
    deleteBtn.innerHTML = '<i class="fas fa-minus"></i>';
    deleteBtn.title = 'Видалити рядок';
    
    // Додаємо обробник події для кнопки видалення
    deleteBtn.addEventListener('click', function() {
        // Видаляємо рядок з таблиці
        newRow.remove();
        // Перераховуємо загальну суму
        calculateTotal();
    });
    
    // Додаємо кнопку видалення до контейнера
    rowActions.appendChild(deleteBtn);
    
    // Додаємо контейнер до комірки суми
    sumCell.appendChild(rowActions);
    
    // Додаємо всі комірки до рядка
    newRow.appendChild(nameCell);
    newRow.appendChild(quantityCell);
    newRow.appendChild(unitCell);
    newRow.appendChild(purchaseCell);
    newRow.appendChild(priceCell);
    newRow.appendChild(sumCell);
    
    // Додаємо рядок до таблиці
    tbody.appendChild(newRow);
    
    // Оновлюємо значення data-z-start для кнопки
    const button = document.querySelector(`button[data-table="${tableId}"]`);
    button.dataset.zStart = parseInt(zIndex) + 1;
    
    // Перераховуємо загальну суму
    calculateTotal();
}

// Функція для додавання кнопки видалення до існуючого рядка
function addDeleteButtonToRow(row) {
    const sumCell = row.querySelector('td:last-child');
    const sumInput = sumCell.querySelector('input[type="number"]');
    
    // Якщо кнопка видалення вже є, не додаємо нову
    if (sumCell.querySelector('.delete-row-btn')) {
        return;
    }
    
    // Якщо sumInput вже в контейнері row-actions, не створюємо новий
    if (sumCell.querySelector('.row-actions')) {
        const rowActions = sumCell.querySelector('.row-actions');
        
        // Створюємо кнопку видалення
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-row-btn';
        deleteBtn.innerHTML = '<i class="fas fa-minus"></i>';
        deleteBtn.title = 'Видалити рядок';
        
        // Додаємо обробник події для кнопки видалення
        deleteBtn.addEventListener('click', function() {
            // Видаляємо рядок з таблиці
            row.remove();
            // Перераховуємо загальну суму
            calculateTotal();
        });
        
        // Додаємо кнопку видалення до контейнера
        rowActions.appendChild(deleteBtn);
    } else {
        // Видаляємо sumInput з комірки
        sumCell.removeChild(sumInput);
        
        // Створюємо контейнер для суми та кнопки видалення
        const rowActions = document.createElement('div');
        rowActions.className = 'row-actions';
        
        // Додаємо поле суми
        rowActions.appendChild(sumInput);
        
        // Створюємо кнопку видалення
        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-row-btn';
        deleteBtn.innerHTML = '<i class="fas fa-minus"></i>';
        deleteBtn.title = 'Видалити рядок';
        
        // Додаємо обробник події для кнопки видалення
        deleteBtn.addEventListener('click', function() {
            // Видаляємо рядок з таблиці
            row.remove();
            // Перераховуємо загальну суму
            calculateTotal();
        });
        
        // Додаємо кнопку видалення до контейнера
        rowActions.appendChild(deleteBtn);
        
        // Додаємо контейнер до комірки суми
        sumCell.appendChild(rowActions);
    }
}

// Функція для перемикання відображення параметрів
function toggleParameters() {
    const parametersContent = document.getElementById('parameters-content');
    const toggleBtn = document.getElementById('toggle-parameters');
    
    if (parametersContent.style.display === 'none') {
        parametersContent.style.display = 'block';
        toggleBtn.querySelector('i').classList.remove('fa-chevron-down');
        toggleBtn.querySelector('i').classList.add('fa-chevron-up');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i> Сховати параметри';
    } else {
        parametersContent.style.display = 'none';
        toggleBtn.querySelector('i').classList.remove('fa-chevron-up');
        toggleBtn.querySelector('i').classList.add('fa-chevron-down');
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Показати параметри';
    }
}

// Функція для перемикання відображення таблиць
function toggleTableSection(sectionId) {
    const section = document.getElementById(sectionId + '-section');
    const checkbox = document.getElementById('show-' + sectionId);
    
    if (checkbox.checked) {
        section.style.display = 'block';
    } else {
        section.style.display = 'none';
    }
}

// Функція для копіювання таблиці у буфер обміну в текстовому форматі
function copyTableToClipboard() {
    console.log('Функція copyTableToClipboard викликана');
    
    // Створюємо текстовий вміст для копіювання
    let textContent = '';
    let totalSum = 0;
    
    // Перевіряємо, чи відображається секція обладнання
    if (document.getElementById('equipment-section').style.display !== 'none') {
        let equipmentRows = document.querySelectorAll('#equipment-table tbody tr');
        let equipmentRowsText = '';
        let nonZeroRows = 0;
        equipmentRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let name = '';
            let quantity = '';
            let price = '';
            let sum = '';
            if (cells[0].querySelector('input[type="text"]')) {
                name = cells[0].querySelector('input[type="text"]').value;
            } else {
                name = cells[0].textContent.trim();
            }
            if (cells[1].querySelector('input[type="number"]')) {
                quantity = cells[1].querySelector('input[type="number"]').value;
            } else {
                quantity = cells[1].textContent.trim();
            }
            if (cells[4].querySelector('input[type="number"]')) {
                price = cells[4].querySelector('input[type="number"]').value;
            } else {
                price = cells[4].textContent.trim();
            }
            if (cells[5].querySelector('input[type="number"]')) {
                sum = cells[5].querySelector('input[type="number"]').value;
            } else {
                sum = cells[5].textContent.trim();
            }
            if (name && parseFloat(quantity) > 0) {
                equipmentRowsText += `-${name}-${quantity}-${price}-${sum}\n`;
                nonZeroRows++;
            }
        });
        if (nonZeroRows > 0) {
            textContent += '**Обладнання**\n';
            textContent += '-Назва-Кількість-Ціна-Сума\n';
            textContent += equipmentRowsText;
            const equipmentSum = parseFloat(document.getElementById('equipment-sum').textContent);
            textContent += `Сума обладнання: ${equipmentSum.toFixed(2)} грн\n\n`;
            totalSum += equipmentSum;
        }
    }
    // Перевіряємо, чи відображається секція кріплення
    if (document.getElementById('mounting-section').style.display !== 'none') {
        let mountingRows = document.querySelectorAll('#mounting-table tbody tr');
        let mountingRowsText = '';
        let nonZeroRows = 0;
        mountingRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let name = '';
            let quantity = '';
            let price = '';
            let sum = '';
            if (cells[0].querySelector('input[type="text"]')) {
                name = cells[0].querySelector('input[type="text"]').value;
            } else {
                name = cells[0].textContent.trim();
            }
            if (cells[1].querySelector('input[type="number"]')) {
                quantity = cells[1].querySelector('input[type="number"]').value;
            } else {
                quantity = cells[1].textContent.trim();
            }
            if (cells[4].querySelector('input[type="number"]')) {
                price = cells[4].querySelector('input[type="number"]').value;
            } else {
                price = cells[4].textContent.trim();
            }
            if (cells[5].querySelector('input[type="number"]')) {
                sum = cells[5].querySelector('input[type="number"]').value;
            } else {
                sum = cells[5].textContent.trim();
            }
            if (name && parseFloat(quantity) > 0) {
                mountingRowsText += `-${name}-${quantity}-${price}-${sum}\n`;
                nonZeroRows++;
            }
        });
        if (nonZeroRows > 0) {
            textContent += '**Кріплення**\n';
            textContent += '-Назва-Кількість-Ціна-Сума\n';
            textContent += mountingRowsText;
            const mountingSum = parseFloat(document.getElementById('mounting-sum').textContent);
            textContent += `Сума кріплення: ${mountingSum.toFixed(2)} грн\n\n`;
            totalSum += mountingSum;
        }
    }
    // Перевіряємо, чи відображається секція електрики
    if (document.getElementById('electrical-section').style.display !== 'none') {
        let electricalRows = document.querySelectorAll('#electrical-table tbody tr');
        let electricalRowsText = '';
        let nonZeroRows = 0;
        electricalRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let name = '';
            let quantity = '';
            let price = '';
            let sum = '';
            if (cells[0].querySelector('input[type="text"]')) {
                name = cells[0].querySelector('input[type="text"]').value;
            } else {
                name = cells[0].textContent.trim();
            }
            if (cells[1].querySelector('input[type="number"]')) {
                quantity = cells[1].querySelector('input[type="number"]').value;
            } else {
                quantity = cells[1].textContent.trim();
            }
            if (cells[4].querySelector('input[type="number"]')) {
                price = cells[4].querySelector('input[type="number"]').value;
            } else {
                price = cells[4].textContent.trim();
            }
            if (cells[5].querySelector('input[type="number"]')) {
                sum = cells[5].querySelector('input[type="number"]').value;
            } else {
                sum = cells[5].textContent.trim();
            }
            if (name && parseFloat(quantity) > 0) {
                electricalRowsText += `-${name}-${quantity}-${price}-${sum}\n`;
                nonZeroRows++;
            }
        });
        if (nonZeroRows > 0) {
            textContent += '**Електрика**\n';
            textContent += '-Назва-Кількість-Ціна-Сума\n';
            textContent += electricalRowsText;
            const electricalSum = parseFloat(document.getElementById('electrical-sum').textContent);
            textContent += `Сума електрики: ${electricalSum.toFixed(2)} грн\n\n`;
            totalSum += electricalSum;
        }
    }
    // Перевіряємо, чи відображається секція роботи
    if (document.getElementById('work-section').style.display !== 'none') {
        let workRows = document.querySelectorAll('#work-table tbody tr');
        let workRowsText = '';
        let nonZeroRows = 0;
        workRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let name = '';
            let quantity = '';
            let price = '';
            let sum = '';
            if (cells[0].querySelector('input[type="text"]')) {
                name = cells[0].querySelector('input[type="text"]').value;
            } else {
                name = cells[0].textContent.trim();
            }
            if (cells[1].querySelector('input[type="number"]')) {
                quantity = cells[1].querySelector('input[type="number"]').value;
            } else {
                quantity = cells[1].textContent.trim();
            }
            if (cells[4].querySelector('input[type="number"]')) {
                price = cells[4].querySelector('input[type="number"]').value;
            } else {
                price = cells[4].textContent.trim();
            }
            if (cells[5].querySelector('input[type="number"]')) {
                sum = cells[5].querySelector('input[type="number"]').value;
            } else {
                sum = cells[5].textContent.trim();
            }
            if (name && parseFloat(quantity) > 0) {
                workRowsText += `-${name}-${quantity}-${price}-${sum}\n`;
                nonZeroRows++;
            }
        });
        if (nonZeroRows > 0) {
            textContent += '**Робота**\n';
            textContent += '-Назва-Кількість-Ціна-Сума\n';
            textContent += workRowsText;
            const workSum = parseFloat(document.getElementById('work-sum').textContent);
            textContent += `Сума роботи: ${workSum.toFixed(2)} грн\n\n`;
            totalSum += workSum;
        }
    }
    // Додаємо загальну суму
    textContent += `**Загальна сума: ${totalSum.toFixed(2)} грн**`;
    
    // Копіюємо текст у буфер обміну
    navigator.clipboard.writeText(textContent)
        .then(() => {
            // Показуємо повідомлення про успішне копіювання
            const copyBtn = document.getElementById('copy-table-btn');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Скопійовано!';
            
            // Повертаємо оригінальний текст через 2 секунди
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
            
            console.log('Таблицю скопійовано у буфер обміну');
        })
        .catch(err => {
            console.error('Помилка при копіюванні таблиці: ', err);
            alert('Помилка при копіюванні таблиці. Спробуйте ще раз.');
        });
}

// Функція для очищення параметрів таблиці
function clearTableParameters() {
    console.log('Функція clearTableParameters викликана');
    
    // Отримуємо всі числові інпути в таблицях
    const numberInputs = document.querySelectorAll('table input[type="number"]');
    
    // Проходимо по всіх інпутах і встановлюємо значення 0 для всіх, крім кількості панелей
    numberInputs.forEach(input => {
        // Перевіряємо, чи це не інпут для кількості сонячних панелей
        if (input.name === 'O31') {
            // Залишаємо значення для кількості сонячних панелей незмінним
            return;
        }
        
        // Для всіх інших інпутів встановлюємо значення 0
        input.value = '0';
    });
    
    // Перераховуємо загальну суму
    calculateTotal();
    
    // Показуємо повідомлення про успішне очищення
    alert('Параметри таблиці очищено');
}

// Додаємо обробники подій для всіх інпутів
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM завантажено в table.js');
    
    // Додаємо обробники для всіх інпутів типу number
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', calculateTotal);
    });
    
    // Додаємо обробники для кнопок додавання рядків
    document.querySelectorAll('.add-row-btn').forEach(button => {
        button.addEventListener('click', function() {
            const tableId = this.getAttribute('data-table');
            const prefix = this.getAttribute('data-prefix');
            const zStart = parseInt(this.getAttribute('data-z-start'));
            addNewRow(tableId, prefix, zStart);
        });
    });
    
    // Додаємо обробник для кнопки очищення параметрів таблиці
    const clearTableBtn = document.getElementById('clear-table-btn');
    if (clearTableBtn) {
        clearTableBtn.addEventListener('click', clearTableParameters);
    }
    
    // Додаємо обробник для кнопки відправки на Telegram
    const telegramBtn = document.getElementById('send-telegram-btn');
    if (telegramBtn) {
        telegramBtn.addEventListener('click', function() {
            // Отримуємо форму
            const form = document.getElementById('pdf-form');
            
            // Створюємо об'єкт FormData з форми
            const formData = new FormData(form);
            
            // Показуємо повідомлення про відправку
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'notification';
            notificationDiv.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Відправка PDF через Telegram...</p>';
            document.body.appendChild(notificationDiv);
            
            // Відправляємо AJAX запит
            fetch('/calculator/send_pdf_to_telegram/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Видаляємо повідомлення про відправку
                document.body.removeChild(notificationDiv);
                
                // Створюємо повідомлення про результат
                const resultDiv = document.createElement('div');
                resultDiv.className = 'notification ' + (data.success ? 'success' : 'error');
                
                if (data.success) {
                    resultDiv.innerHTML = '<p><i class="fas fa-check-circle"></i> ' + (data.message || 'PDF успішно відправлено через Telegram') + '</p>';
                } else {
                    resultDiv.innerHTML = '<p><i class="fas fa-exclamation-circle"></i> ' + (data.error || 'Помилка при відправці PDF через Telegram') + '</p>';
                }
                
                // Додаємо повідомлення на сторінку
                document.body.appendChild(resultDiv);
                
                // Видаляємо повідомлення через 5 секунд
                setTimeout(() => {
                    document.body.removeChild(resultDiv);
                }, 5000);
            })
            .catch(error => {
                // Видаляємо повідомлення про відправку
                document.body.removeChild(notificationDiv);
                
                // Створюємо повідомлення про помилку
                const errorDiv = document.createElement('div');
                errorDiv.className = 'notification error';
                errorDiv.innerHTML = '<p><i class="fas fa-exclamation-circle"></i> Помилка при відправці PDF через Telegram</p>';
                
                // Додаємо повідомлення на сторінку
                document.body.appendChild(errorDiv);
                
                // Видаляємо повідомлення через 5 секунд
                setTimeout(() => {
                    document.body.removeChild(errorDiv);
                }, 5000);
                
                console.error('Помилка при відправці PDF через Telegram:', error);
            });
        });
    }
    
    // Додаємо обробник для кнопки відправки на Email
    const emailBtn = document.getElementById('send-email-btn');
    if (emailBtn) {
        emailBtn.addEventListener('click', function() {
            // Показуємо модальне вікно для email
            const modal = document.getElementById('email-modal');
            if (modal) {
                modal.style.display = 'block';
                // Автоматично фокусуємо поле email для зручності
                setTimeout(() => {
                    const input = document.getElementById('email-input');
                    if (input) input.focus();
                }, 100);
            }
        });
    }
    
    // Додаємо обробник для закриття модального вікна (хрестик і кнопка "Скасувати")
    const closeEmailModal = document.getElementById('close-email-modal');
    if (closeEmailModal) {
        closeEmailModal.addEventListener('click', function() {
            document.getElementById('email-modal').style.display = 'none';
        });
    }
    const cancelEmailBtn = document.getElementById('cancel-email-btn');
    if (cancelEmailBtn) {
        cancelEmailBtn.addEventListener('click', function() {
            document.getElementById('email-modal').style.display = 'none';
        });
    }
    
    // Додаємо обробник для кнопки підтвердження в модальному вікні
    const confirmEmailBtn = document.getElementById('confirm-email-btn');
    if (confirmEmailBtn) {
        confirmEmailBtn.addEventListener('click', function() {
            // Отримуємо введений email
            const email = document.getElementById('email-input').value;
            
            // Перевіряємо, чи введено email
            if (email) {
                // Отримуємо форму
                const form = document.getElementById('pdf-form');
                
                // Створюємо об'єкт FormData з форми
                const formData = new FormData(form);
                
                // Додаємо email до formData
                formData.append('email', email);
                
                // Показуємо повідомлення про відправку
                const notificationDiv = document.createElement('div');
                notificationDiv.className = 'notification';
                notificationDiv.textContent = 'Відправка звіту на email...';
                document.body.appendChild(notificationDiv);
                
                // Відправляємо AJAX-запит замість традиційної відправки форми
                fetch('/calculator/send_pdf_email/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    // Видаляємо повідомлення про відправку
                    document.body.removeChild(notificationDiv);
                    
                    // Закриваємо модальне вікно
                    document.getElementById('email-modal').style.display = 'none';
                    
                    // Показуємо результат
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'notification success';
                    resultDiv.textContent = data.message || 'PDF звіт успішно відправлено на email';
                    document.body.appendChild(resultDiv);
                    
                    // Видаляємо повідомлення через 5 секунд
                    setTimeout(() => {
                        document.body.removeChild(resultDiv);
                    }, 5000);
                })
                .catch(error => {
                    // Видаляємо повідомлення про відправку
                    document.body.removeChild(notificationDiv);
                    
                    // Закриваємо модальне вікно
                    document.getElementById('email-modal').style.display = 'none';
                    
                    // Показуємо повідомлення про помилку
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'notification error';
                    errorDiv.textContent = 'Помилка при відправці PDF на email';
                    document.body.appendChild(errorDiv);
                    
                    // Видаляємо повідомлення через 5 секунд
                    setTimeout(() => {
                        document.body.removeChild(errorDiv);
                    }, 5000);
                    
                    console.error('Помилка при відправці PDF на email:', error);
                });
            } else {
                alert('Будь ласка, введіть email-адресу');
            }
        });
    }
    
    // Додаємо обробник події для кнопки копіювання таблиці
    const copyBtn = document.getElementById('copy-table-btn');
    console.log('Кнопка копіювання в table.js:', copyBtn);
    
    if (copyBtn) {
        console.log('Додаємо обробник для кнопки копіювання в table.js');
        copyBtn.addEventListener('click', function() {
            console.log('Кнопка копіювання натиснута в table.js');
            copyTableToClipboard();
        });
    }
    
    // Додаємо обробники подій для чекбоксу та поля з відсотком
    const checkbox = document.getElementById('add-percentage-checkbox');
    const percentageValue = document.getElementById('percentage-value');
    
    if (checkbox) {
        checkbox.addEventListener('change', calculatePercentage);
    }
    
    if (percentageValue) {
        percentageValue.addEventListener('input', calculatePercentage);
    }
    
    // Додаємо обробники подій для чекбоксу збільшення кількості кріплень
    const mountingCheckbox = document.getElementById('add-mounting-quantity-checkbox');
    const mountingInputs = document.getElementById('mounting-quantity-inputs');
    const applyMountingFactorBtn = document.getElementById('apply-mounting-factor-btn');
    
    if (mountingCheckbox && mountingInputs) {
        mountingCheckbox.addEventListener('change', function() {
            mountingInputs.style.display = mountingCheckbox.checked ? 'block' : 'none';
        });
    }
    
    if (applyMountingFactorBtn) {
        applyMountingFactorBtn.addEventListener('click', increaseMountingQuantity);
    }
    
    // Перераховуємо загальну суму
    calculateTotal();
});
