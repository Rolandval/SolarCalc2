document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM завантажено');
    
    const form = document.getElementById('calculator-form');
    const resultsDiv = document.getElementById('results');
    const resultsTable = document.getElementById('results-table');
    const canvas = document.getElementById('layout-canvas');
    const ctx = canvas.getContext('2d');

    // Не приховуємо блок результатів, щоб було видно кнопку PDF
    // resultsDiv.style.display = 'none';
    
    // Перевіряємо, чи є на сторінці елементи для роботи з PDF
    const pdfOptions = document.getElementById('pdf-options');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    
    if (pdfOptions && downloadPdfBtn) {
        console.log('Елементи для PDF знайдені');
        
        // Налаштовуємо обробник кнопки PDF
        downloadPdfBtn.addEventListener('click', function() {
            console.log('Клік на кнопці завантаження PDF');
            
            // Отримуємо значення параметрів
            const paramO = document.getElementById('param-o').checked;
            const paramK = document.getElementById('param-k').checked;
            const paramE = document.getElementById('param-e').checked;
            const paramR = document.getElementById('param-r').checked;
            
            const parameters = {
                O: paramO,
                K: paramK,
                E: paramE,
                R: paramR
            };
            
            console.log('Параметри PDF:', parameters);
            
            // Отримуємо дані з таблиці
            const tableData = getTableData();
            
            // Перевіряємо наявність даних
            if (!tableData || tableData.items.length === 0) {
                alert('Спочатку виконайте розрахунок, щоб отримати дані для PDF-звіту');
                return;
            }
            
            // Відправляємо дані для генерації PDF
            downloadPDF(parameters, tableData);
        });
    }
    
    // Додаємо тестову кнопку для відлагодження
    const testButton = document.createElement('button');
    testButton.textContent = 'Тестова таблиця';
    testButton.style.marginTop = '20px';
    testButton.addEventListener('click', function(e) {
        e.preventDefault();
        testDisplayTable();
    });
    form.appendChild(testButton);
    
    // Додаємо ще одну кнопку для ручного виклику відправки форми
    const manualButton = document.createElement('button');
    manualButton.textContent = 'Ручний розрахунок';
    manualButton.style.marginTop = '20px';
    manualButton.style.marginLeft = '10px';
    manualButton.addEventListener('click', function(e) {
        e.preventDefault();
        window.submitFormManually();
    });
    form.appendChild(manualButton);
    
    console.log('Елементи на сторінці:');
    console.log('Форма:', form);
    console.log('Результати:', resultsDiv);
    console.log('Таблиця:', resultsTable);
    console.log('Canvas:', canvas);
    console.log('Кнопка відправки:', form.querySelector('.calculate-button'));
    
    // Робимо функцію displayResults доступною глобально
    window.displayResults = function(results) {
        console.log('Відображаємо результати:', results);
        
        // Створюємо HTML таблиці
        let html = '<h3>Результати розрахунку</h3>';
        html += '<table class="results-table">';
        html += '<tr>';
        html += '<th>№</th>';
        html += '<th>Найменування</th>';
        html += '<th>Кількість</th>';
        html += '<th>Од.</th>';
        html += '<th>Закупка</th>';
        html += '<th>Ціна</th>';
        html += '<th>Сума</th>';
        html += '</tr>';

        // ОБЛАДНАННЯ
        html += '<tr class="category-header"><td colspan="7">ОБЛАДНАННЯ</td></tr>';
        
        html += '<tr>';
        html += '<td>1</td>';
        html += '<td>Інвертор</td>';
        html += '<td>1</td>';
        html += '<td>шт</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="1" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="1" value="0.00"></td>';
        html += '<td class="sum" data-row="1">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>2</td>';
        html += '<td>Акумулятор</td>';
        html += '<td>1</td>';
        html += '<td>шт</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="2" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="2" value="0.00"></td>';
        html += '<td class="sum" data-row="2">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>3</td>';
        html += '<td>Сонячна панель</td>';
        html += `<td>${results.total_panels || 10}</td>`;
        html += '<td>шт</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="3" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="3" value="0.00"></td>';
        html += '<td class="sum" data-row="3">0.00</td>';
        html += '</tr>';
        
        // КРІПЛЕННЯ
        html += '<tr class="category-header"><td colspan="7">КРІПЛЕННЯ</td></tr>';
        
        html += '<tr>';
        html += '<td>4</td>';
        html += '<td>Профіль</td>';
        html += `<td>${results.total_profile_length || 10}</td>`;
        html += '<td>м</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="4" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="4" value="0.00"></td>';
        html += '<td class="sum" data-row="4">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>6</td>';
        html += '<td>Бокові Г-образні зажими (комплект)</td>';
        html += `<td>${results.clamps?.end_clamps || 8}</td>`;
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="6" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="6" value="0.00"></td>';
        html += '<td class="sum" data-row="6">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>7</td>';
        html += '<td>Міжпанельні V-образні зажими (комплект)</td>';
        html += `<td>${results.clamps?.middle_clamps || 8}</td>`;
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="7" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="7" value="0.00"></td>';
        html += '<td class="sum" data-row="7">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>8</td>';
        html += '<td>Гвинт шуруп М10*200 комплект цинк</td>';
        html += `<td>${(results.clamps?.end_clamps + results.clamps?.middle_clamps) || 16}</td>`;
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="8" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="8" value="0.00"></td>';
        html += '<td class="sum" data-row="8">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>9</td>';
        html += '<td>Комплект з\'єднувача профілів (ЗОВНІШНІЙ)</td>';
        html += `<td>${results.profiles?.length * 2 || 8}</td>`;
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="9" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="9" value="0.00"></td>';
        html += '<td class="sum" data-row="9">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>10</td>';
        html += '<td>Конектори МС4</td>';
        html += '<td>4</td>';
        html += '<td>пара</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="10" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="10" value="0.00"></td>';
        html += '<td class="sum" data-row="10">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>11</td>';
        html += '<td>Кабель</td>';
        html += `<td>${results.cables || 10}</td>`;
        html += '<td>м</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="11" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="11" value="0.00"></td>';
        html += '<td class="sum" data-row="11">0.00</td>';
        html += '</tr>';
        
        // ЕЛЕКТРИКА
        html += '<tr class="category-header"><td colspan="7">ЕЛЕКТРИКА</td></tr>';
        
        html += '<tr>';
        html += '<td>12</td>';
        html += '<td>Коробки з автоматами</td>';
        html += '<td>1</td>';
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="12" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="12" value="0.00"></td>';
        html += '<td class="sum" data-row="12">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>14</td>';
        html += '<td>Блискавкозахист</td>';
        html += '<td>1</td>';
        html += '<td>компл</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="14" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="14" value="0.00"></td>';
        html += '<td class="sum" data-row="14">0.00</td>';
        html += '</tr>';
        
        // РОБОТИ
        html += '<tr class="category-header"><td colspan="7">РОБОТИ</td></tr>';
        
        html += '<tr>';
        html += '<td>15</td>';
        html += '<td>Доставка</td>';
        html += '<td>1</td>';
        html += '<td>послуга</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="15" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="15" value="0.00"></td>';
        html += '<td class="sum" data-row="15">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>16</td>';
        html += '<td>Роботи електрика</td>';
        html += '<td>1</td>';
        html += '<td>послуга</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="16" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="16" value="0.00"></td>';
        html += '<td class="sum" data-row="16">0.00</td>';
        html += '</tr>';
        
        html += '<tr>';
        html += '<td>17</td>';
        html += '<td>Монтаж</td>';
        html += '<td>1</td>';
        html += '<td>послуга</td>';
        html += '<td><input type="number" class="price-input purchase" data-row="17" value="0.00"></td>';
        html += '<td><input type="number" class="price-input price" data-row="17" value="0.00"></td>';
        html += '<td class="sum" data-row="17">0.00</td>';
        html += '</tr>';

        // Додаємо підсумки
        html += '</table>';
        html += '<div class="totals">';
        html += '<p>Сума закупки разом: <span id="total-purchase">0.00</span></p>';
        html += '<p>Сума разом: <span id="total-sum">0.00</span></p>';
        html += '<p>Заробіток (Сума мінус сума закупки): <span id="total-profit">0.00</span></p>';
        html += '</div>';

        // Встановлюємо HTML вміст
        resultsTable.innerHTML = html;
        
        // Перевірка чи відображена таблиця
        console.log('Таблиця відображена:', resultsTable.offsetParent !== null);
        console.log('HTML таблиці:', resultsTable.innerHTML.substring(0, 200) + '...');
        
        // Показуємо блок з результатами
        resultsDiv.style.display = 'block';

        // Додаємо обробники подій для інпутів
        document.querySelectorAll('.price-input').forEach(input => {
            input.addEventListener('input', updateSums);
        });
        
        // Викликаємо розрахунок сум одразу після відображення
        updateSums();

        // Показуємо блок з параметрами PDF після успішного відображення результатів
        const pdfOptions = document.getElementById('pdf-options');
        if (pdfOptions) {
            pdfOptions.style.display = 'block';
            console.log('Блок з параметрами PDF відображено');
        } else {
            console.error('Не знайдено блок з параметрами PDF!');
        }
    };

    function updateSums() {
        let totalPurchase = 0;
        let totalSum = 0;

        // Проходимо по всіх рядках таблиці, крім заголовків категорій
        document.querySelectorAll('.results-table tr:not(.category-header)').forEach(row => {
            // Перевіряємо, чи є це звичайний рядок з даними (має комірки з цінами)
            const purchaseInput = row.querySelector('.purchase');
            if (purchaseInput) {
                const quantity = parseFloat(row.querySelector('td:nth-child(3)').textContent) || 0;
                const purchase = parseFloat(purchaseInput.value) || 0;
                const price = parseFloat(row.querySelector('.price').value) || 0;
                
                const sum = quantity * price;
                row.querySelector('.sum').textContent = sum.toFixed(2);
                
                totalPurchase += quantity * purchase;
                totalSum += sum;
            }
        });

        // Оновлюємо підсумки
        const totalPurchaseEl = document.getElementById('total-purchase');
        const totalSumEl = document.getElementById('total-sum');
        const totalProfitEl = document.getElementById('total-profit');
        
        if (totalPurchaseEl && totalSumEl && totalProfitEl) {
            totalPurchaseEl.textContent = totalPurchase.toFixed(2);
            totalSumEl.textContent = totalSum.toFixed(2);
            
            // Розраховуємо та відображаємо заробіток
            const profit = totalSum - totalPurchase;
            totalProfitEl.textContent = profit.toFixed(2);
            
            console.log('Суми розраховані:', {
                totalPurchase: totalPurchase.toFixed(2),
                totalSum: totalSum.toFixed(2),
                profit: profit.toFixed(2)
            });
        } else {
            console.error('Не знайдено елементи для відображення сум');
        }
    }

    // Перевіряємо, чи існує форма
    if (form) {
        console.log('Додаємо обробник форми');
        
        // Додаємо обробник для кнопки "Розрахувати"
        const calculateButton = form.querySelector('.calculate-button');
        if (calculateButton) {
            console.log('Знайдено кнопку розрахунку');
            
            // Додаємо обробник кліку на кнопку
            calculateButton.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Кнопка розрахунку натиснута');
                submitForm();
            });
        } else {
            console.error('Кнопка розрахунку не знайдена');
        }
        
        // Додаємо обробник відправки форми
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Форма відправлена через submit');
            submitForm();
        });
    } else {
        console.error('Форма не знайдена');
    }
    
    // Функція для відправки форми
    function submitForm() {
        console.log('Відправка форми...');
        
        // Збираємо дані форми
        const formData = {
            panel_length: document.getElementById('panel-length').value,
            panel_width: document.getElementById('panel-width').value,
            rows: document.getElementById('rows').value,
            panels_per_row: document.getElementById('panels-per-row').value,
            orientation: document.querySelector('input[name="orientation"]:checked').value,
            panel_type: document.querySelector('input[name="panel-type"]:checked').value,
            profile_lengths: document.getElementById('profile-lengths').value,
            strings: document.getElementById('strings').value,
            cable_length: document.getElementById('cable-length').value
        };
        
        console.log('Дані форми:', formData);
        
        // Отримуємо CSRF-токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('CSRF-токен:', csrfToken);
        
        // Збираємо дані з таблиці
        const table = document.getElementById('results-table');
        const rows = table.getElementsByTagName('tr');
        const tableData = [];
        
        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            const rowData = [];
            for (let j = 0; j < cells.length; j++) {
                rowData.push(cells[j].innerText);
            }
            tableData.push(rowData);
        }
        
        // Записуємо дані у приховане поле
        document.getElementById('table-data').value = JSON.stringify(tableData);
        
        // Відправляємо запит на сервер
        fetch('/calculator/calculate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            console.log('Отримано відповідь від сервера:', response);
            if (!response.ok) {
                throw new Error('Помилка сервера: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Дані від сервера:', data);
            if (data.success) {
                // Відображаємо результати
                window.displayResults(data.data);
                
                // Малюємо схему розташування
                window.drawLayout(data.data);
                
                // Прокручуємо до результатів
                resultsDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                console.error('Помилка:', data.error);
                alert('Помилка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Помилка:', error);
            alert('Помилка при відправці запиту: ' + error.message);
        });
    }

    // Додаємо функцію для прямого виклику з консолі
    window.submitFormManually = function() {
        console.log('Ручний виклик відправки форми');
        
        // Збираємо дані форми
        const formData = {
            panel_length: document.getElementById('panel-length').value,
            panel_width: document.getElementById('panel-width').value,
            rows: document.getElementById('rows').value,
            panels_per_row: document.getElementById('panels-per-row').value,
            orientation: document.querySelector('input[name="orientation"]:checked').value,
            panel_type: document.querySelector('input[name="panel-type"]:checked').value,
            profile_lengths: document.getElementById('profile-lengths').value,
            strings: document.getElementById('strings').value,
            cable_length: document.getElementById('cable-length').value
        };
        
        console.log('Дані форми:', formData);
        
        // Отримуємо CSRF-токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        console.log('CSRF-токен:', csrfToken);
        
        // Відправляємо запит на сервер
        fetch('/api/calculate/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            console.log('Отримано відповідь від сервера:', response);
            if (!response.ok) {
                throw new Error('Помилка сервера: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Дані від сервера:', data);
            if (data.success) {
                // Відображаємо результати
                window.displayResults(data.data);
                
                // Малюємо схему розташування
                window.drawLayout(data.data);
                
                // Прокручуємо до результатів
                document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
            } else {
                console.error('Помилка:', data.error);
                alert('Помилка: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Помилка:', error);
            alert('Помилка при відправці запиту: ' + error.message);
        });
    };

    // Робимо функцію drawLayout доступною глобально
    window.drawLayout = function(data) {
        console.log('Малюємо схему розташування:', data);
        
        // Отримуємо розміри полотна
        const canvasWidth = canvas.width;
        const canvasHeight = canvas.height;
        
        // Очищаємо полотно
        ctx.clearRect(0, 0, canvasWidth, canvasHeight);
        
        // Встановлюємо параметри малювання
        const padding = 50;
        const maxWidth = canvasWidth - (padding * 2);
        const maxHeight = canvasHeight - (padding * 2);
        
        // Отримуємо кількість рядів та панелей у ряді
        const rows = parseInt(document.getElementById('rows').value);
        const panelsPerRow = parseInt(document.getElementById('panels-per-row').value);
        
        // Отримуємо розміри панелі
        const panelLength = parseFloat(document.getElementById('panel-length').value);
        const panelWidth = parseFloat(document.getElementById('panel-width').value);
        
        // Визначаємо орієнтацію панелей
        const orientation = document.querySelector('input[name="orientation"]:checked').value;
        
        // Визначаємо розміри панелі для малювання
        let panelDrawWidth, panelDrawHeight;
        if (orientation === 'landscape') {
            panelDrawWidth = panelLength;
            panelDrawHeight = panelWidth;
        } else {
            panelDrawWidth = panelWidth;
            panelDrawHeight = panelLength;
        }
        
        // Розраховуємо масштаб для малювання
        const rowWidth = panelDrawWidth * panelsPerRow;
        const totalHeight = panelDrawHeight * rows;
        
        const scaleX = maxWidth / rowWidth;
        const scaleY = maxHeight / totalHeight;
        const scale = Math.min(scaleX, scaleY);
        
        // Розраховуємо розміри панелі з урахуванням масштабу
        const scaledPanelWidth = panelDrawWidth * scale;
        const scaledPanelHeight = panelDrawHeight * scale;
        
        // Розраховуємо початкові координати для центрування схеми
        const startX = (canvasWidth - (scaledPanelWidth * panelsPerRow)) / 2;
        const startY = (canvasHeight - (scaledPanelHeight * rows)) / 2;
        
        // Малюємо панелі
        for (let row = 0; row < rows; row++) {
            for (let panel = 0; panel < panelsPerRow; panel++) {
                const x = startX + (panel * scaledPanelWidth);
                const y = startY + (row * scaledPanelHeight);
                
                // Малюємо рамку панелі
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, scaledPanelWidth, scaledPanelHeight);
                
                // Малюємо внутрішню частину панелі
                ctx.fillStyle = '#e0e0e0';
                ctx.fillRect(x + 2, y + 2, scaledPanelWidth - 4, scaledPanelHeight - 4);
                
                // Додаємо текст з номером панелі
                ctx.fillStyle = '#333';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(`${row * panelsPerRow + panel + 1}`, x + scaledPanelWidth / 2, y + scaledPanelHeight / 2);
            }
        }
        
        // Додаємо легенду
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`Схема розташування: ${rows} ряди × ${panelsPerRow} панелей`, padding, padding / 2);
    };
    
    // Додаємо тестову функцію для відображення таблиці без відправки форми (для тестування)
    window.testDisplayTable = function() {
        console.log('Виклик тестової функції');
        const testData = {
            total_panels: 10,
            total_profile_length: 30,
            clamps: {
                end_clamps: 8,
                middle_clamps: 12
            },
            profiles: [
                {length: 6, count: 2},
                {length: 4, count: 3},
                {length: 3, count: 2}
            ],
            cables: 15
        };
        window.displayResults(testData);
        window.drawLayout(testData);
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
        console.log('Тестова таблиця відображена');
    };

    // Функція для відправки даних та отримання PDF-звіту
    function downloadPDF(parameters, tableData) {
        console.log('Відправка даних для генерації PDF-звіту:', parameters, tableData);
        
        // Отримуємо CSRF-токен
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Показуємо індикатор завантаження
        const downloadBtn = document.getElementById('download-pdf-btn');
        const originalBtnText = downloadBtn.textContent;
        downloadBtn.textContent = 'Генерація PDF...';
        downloadBtn.disabled = true;
        downloadBtn.style.opacity = '0.7';
        
        // Визначаємо URL для генерації PDF
        const pdfUrl = '/calculator/generate-pdf/';
        
        // Отримуємо дані з таблиці у новому форматі
        const tableParams = getTableDataAsParams();
        
        // Об'єднуємо параметри
        const allParams = {
            ...parameters,
            ...tableParams
        };
        
        // Відправляємо запит на сервер
        fetch(pdfUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(allParams)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Помилка отримання PDF: ' + response.status);
            }
            return response.json();  // Змінимо на response.blob(), якщо повертається PDF
        })
        .then(data => {
            if (data.success) {
                // Створюємо URL для об'єкта blob
                const url = window.URL.createObjectURL(data.blob);
                
                // Створюємо тимчасове посилання для завантаження
                const a = document.createElement('a');
                a.href = url;
                a.download = 'звіт_калькулятор.pdf';
                document.body.appendChild(a);
                a.click();
                
                // Прибираємо посилання
                setTimeout(() => {
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                }, 0);
            } else {
                throw new Error(data.error || 'Невідома помилка при генерації PDF');
            }
        })
        .catch(error => {
            console.error('Помилка завантаження PDF:', error);
            alert('Помилка при генерації PDF: ' + error.message);
        })
        .finally(() => {
            // Відновлюємо оригінальний стан кнопки
            downloadBtn.textContent = originalBtnText;
            downloadBtn.disabled = false;
            downloadBtn.style.opacity = '1';
        });
    }

    // Функція для отримання даних з таблиці
    function getTableData() {
        const table = document.querySelector('.results-table');
        if (!table) {
            console.error('Таблиця результатів не знайдена');
            return {
                items: [],
                totals: {
                    purchase: "0",
                    sum: "0",
                    profit: "0"
                }
            };
        }
        
        const rows = table.querySelectorAll('tr');
        let data = [];
        let currentCategory = '';
        
        rows.forEach(row => {
            // Якщо це заголовок категорії
            if (row.classList.contains('category-header')) {
                currentCategory = row.textContent.trim();
                return;
            }
            
            // Пропускаємо заголовок таблиці
            if (row.querySelector('th')) return;
            
            const cells = row.querySelectorAll('td');
            if (cells.length < 6) return;
            
            const rowData = {
                category: currentCategory,
                number: cells[0].textContent.trim(),
                name: cells[1].textContent.trim(),
                quantity: cells[2].textContent.trim(),
                unit: cells[3].textContent.trim(),
                purchase: cells[4].querySelector('input') ? cells[4].querySelector('input').value : '0',
                price: cells[5].querySelector('input') ? cells[5].querySelector('input').value : '0',
                sum: cells[6].textContent.trim()
            };
            
            data.push(rowData);
        });
        
        // Додаємо загальні суми
        const totalPurchase = document.getElementById('total-purchase') ? document.getElementById('total-purchase').textContent : "0";
        const totalSum = document.getElementById('total-sum') ? document.getElementById('total-sum').textContent : "0";
        const totalProfit = document.getElementById('total-profit') ? document.getElementById('total-profit').textContent : "0";
        
        return {
            items: data,
            totals: {
                purchase: totalPurchase,
                sum: totalSum,
                profit: totalProfit
            }
        };
    }

    function getTableDataAsParams() {
        const table = document.querySelector('.results-table');
        if (!table) {
            console.error('Таблиця результатів не знайдена');
            return {};
        }

        const rows = table.querySelectorAll('tr');
        let params = {};
        let currentCategory = '';

        rows.forEach(row => {
            // Якщо це заголовок категорії
            if (row.classList.contains('category-header')) {
                currentCategory = row.textContent.trim();
                return;
            }

            // Пропускаємо заголовок таблиці
            if (row.querySelector('th')) return;

            const cells = row.querySelectorAll('td');
            if (cells.length < 6) return;

            // Отримуємо номер рядка
            const rowNumber = cells[0].textContent.trim();

            // Створюємо ключі для параметрів
            const categoryPrefix = getCategoryPrefix(currentCategory);
            const quantityKey = `${categoryPrefix}${rowNumber}1`;
            const priceKey = `${categoryPrefix}${rowNumber}2`;

            // Отримуємо значення
            const quantity = cells[2].textContent.trim();
            const price = cells[5].querySelector('input') ? cells[5].querySelector('input').value : '0';

            // Додаємо до параметрів
            params[quantityKey] = quantity;
            params[priceKey] = price;
        });

        return params;
    }

    function getCategoryPrefix(category) {
        switch (category) {
            case 'ОБЛАДНАННЯ':
                return 'O';
            case 'КРІПЛЕННЯ':
                return 'K';
            case 'ЕЛЕКТРИКА':
                return 'E';
            case 'РОБОТИ':
                return 'R';
            default:
                return '';
        }
    }
});