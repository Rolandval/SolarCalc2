from fpdf import FPDF
import os
import sys
import shutil
from datetime import date
import base64

# Отримуємо абсолютний шлях до директорії проекту
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Функція для нормалізації шляхів (заміна зворотних слешів на прямі)
def normalize_path(path):
    if path is None:
        return None
    return path.replace('\\', '/')

# Функція для пошуку файлу в різних можливих директоріях
def find_file(filename, possible_dirs):
    for directory in possible_dirs:
        path = os.path.join(directory, filename)
        normalized_path = normalize_path(path)
        if os.path.exists(normalized_path):
            return normalized_path
    return None

# Можливі директорії, де можуть знаходитися шрифти
possible_font_dirs = [
    os.path.join(BASE_DIR, "static", "fonts"),
    os.path.join(BASE_DIR, "static/fonts"),
    "/opt/render/project/src/static/fonts",
    os.path.join(os.path.dirname(BASE_DIR), "static", "fonts"),
    os.path.join(os.path.dirname(BASE_DIR), "static/fonts"),
    os.path.join(BASE_DIR, "fonts"),
    "/opt/render/project/src/fonts",
]

# Створюємо власний клас PDF, який розширює FPDF і відстежує, чи додавався контент на поточну сторінку
class CustomPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_has_content = False
    
    def add_page(self, *args, **kwargs):
        # Перед додаванням нової сторінки перевіряємо, чи поточна сторінка має контент
        if self.page_no() > 0 and not self.page_has_content:
            # Якщо поточна сторінка пуста, не додаємо нову
            return
        
        # Додаємо нову сторінку і скидаємо прапорець контенту
        super().add_page(*args, **kwargs)
        self.page_has_content = False
    
    # Перевизначаємо методи, які додають контент на сторінку
    def cell(self, *args, **kwargs):
        super().cell(*args, **kwargs)
        self.page_has_content = True
    
    def multi_cell(self, *args, **kwargs):
        super().multi_cell(*args, **kwargs)
        self.page_has_content = True
    
    def text(self, *args, **kwargs):
        super().text(*args, **kwargs)
        self.page_has_content = True
    
    def image(self, *args, **kwargs):
        super().image(*args, **kwargs)
        self.page_has_content = True
    
    # Метод для перевірки, чи остання сторінка має контент
    def check_last_page(self):
        if self.page_no() > 0 and not self.page_has_content:
            # Якщо остання сторінка пуста, видаляємо її
            self._pages.pop(self.page_no() - 1)
            self.page = self.page_no() - 1

# Ініціалізуємо PDF з підтримкою UTF-8
def generate(
        O: bool = True, K: bool = True, E: bool = True, R: bool = True,
        O11: int = 0, O12: float = 0.0,
        O21: int = 0, O22: float = 0.0,
        O31: int = 0, O32: float = 0.0,
        K1112: list = [],
        K21: int = 0, K22: float = 0.0,
        K31: int = 0, K32: float = 0.0,
        K41: int = 0, K42: float = 0.0,
        K51: int = 0, K52: float = 0.0,
        K61: int = 0, K62: float = 0.0,
        K71: list = [],
        K81: int = 0, K82: float = 0.0,
        K91: int = 0, K92: float = 0.0,
        K111: int = 0, K121: float = 0.0,
        K912: int = 0, K922: float = 0.0,
        K913: int = 0, K923: float = 0.0,
        E11: int = 0, E12: float = 0.0,
        E21: int = 0, E22: float = 0.0,
        R11: int = 0, R12: float = 0.0,
        R21: int = 0, R22: float = 0.0,
        R31: int = 0, R32: float = 0.0,
        scheme_image: str = '',
        panel_height: int = 30,
        dynamic_equipment: list = [],
        dynamic_mounting: list = [],  # Додаємо динамічні рядки кріплень
        dynamic_electrical: list = [],
        dynamic_other: list = [],
        dynamic_work: list = [],
        usd_rate: float = 0.0,  # Додаємо курс долара
        total_usd: float = 0.0,  # Додаємо суму в доларах
        screw_material: str = 'оцинковані',
        profile_material: str = 'алюміній',
        current_date: str = '',  # Додаємо поточну дату
        show_usd: bool = True,  # Додаємо параметр для відображення суми в доларах
        panel_model_name: str = '',  # Додаємо назву моделі панелі
        panel_length: int = 0,  # Додаємо довжину панелі
        panel_width: int = 0,  # Додаємо ширину панелі
        panel_arrangement: str = '',  # Додаємо розташування панелі
        panel_type: str = '',  # Додаємо тип панелі
        panel_arrays: list = [],  # Додаємо дані про масиви панелей
        total_panels: int = 0,  # Додаємо загальну кількість панелей
        total_rows: int = 0,  # Додаємо загальну кількість рядів
        avg_panels_per_row: float = 0,  # Додаємо середню кількість панелей в ряді
        panel_schemes: list = [],  # Додаємо список схем для кожного масиву
        carcase_material: str = '',  # Додаємо матеріал каркасу
        foundation_type_1: str = '',  # Додаємо тип основи
        carcase_profiles: list = []  # Додаємо профілі каркасу
        ):
    # Створюємо тимчасову директорію для шрифтів
    temp_font_dir = os.path.join(BASE_DIR, "temp_fonts")
    os.makedirs(temp_font_dir, exist_ok=True)
    
    # Шукаємо шрифти
    font_path = find_file("DejaVuSans.ttf", possible_font_dirs)
    bold_font_path = find_file("DejaVuSans-Bold.ttf", possible_font_dirs)
    
    # Виводимо діагностичну інформацію
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"Font path: {font_path}")
    print(f"Bold font path: {bold_font_path}")
    
    # Копіюємо шрифти у тимчасову директорію, якщо вони знайдені
    if font_path:
        shutil.copy(font_path, os.path.join(temp_font_dir, "DejaVuSans.ttf"))
    if bold_font_path:
        shutil.copy(bold_font_path, os.path.join(temp_font_dir, "DejaVuSans-Bold.ttf"))
    
    # Ініціалізуємо PDF
    pdf = CustomPDF()
    pdf.add_font('DejaVu', '', os.path.join(temp_font_dir, "DejaVuSans.ttf"), uni=True)
    pdf.add_font('DejaVu', 'B', os.path.join(temp_font_dir, "DejaVuSans-Bold.ttf"), uni=True)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    total_sum = 0

    # Додаємо шрифти, якщо вони доступні
    if font_path and bold_font_path:
        try:
            pdf.set_font('DejaVu', size=12)
        except Exception as e:
            print(f"Помилка при додаванні шрифту: {e}")
            print("Використовуємо стандартний шрифт")
            pdf.set_font('Arial', size=12)
    else:
        print(f"Шрифти не знайдено або не скопійовано. Використовуємо стандартний шрифт")
        pdf.set_font('Arial', size=12)

    # Функція для створення таблиці
    def create_table(title, items, total: float = 0):
        nonlocal total_sum
        # Заголовок таблиці
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, title, ln=True, align='L')
        pdf.set_font('DejaVu', size=12)
        total_sum += total
        
        # Заголовки колонок
        headers = ['Найменування', 'К-сть', 'Од', 'Ціна', 'Сума']
        col_widths = [106, 15, 20, 27, 27]
        
        # Встановлюємо жирний шрифт для заголовків
        pdf.set_font('DejaVu', 'B', 12)
        
        # Виводимо заголовки
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()
        
        # Встановлюємо звичайний шрифт для даних
        pdf.set_font('DejaVu', size=12)
        
        # Виводимо дані
        for item in items:
            pdf.cell(col_widths[0], 10, item[0], 1, 0, 'L')
            pdf.cell(col_widths[1], 10, str(item[1]), 1, 0, 'C')
            pdf.cell(col_widths[2], 10, item[2], 1, 0, 'C')
            pdf.cell(col_widths[3], 10, str(item[3]), 1, 0, 'R')
            pdf.cell(col_widths[4], 10, str(item[4]), 1, 0, 'R')
            pdf.ln()
        
        # Додаємо рядок для суми
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(sum(col_widths[:-2]), 10, '     Cума:', 1, 0, 'R')
        pdf.cell(col_widths[-2], 10, '', 1, 0, 'R')
        pdf.cell(col_widths[-1], 10, f'{total}', 1, 0, 'R')
        pdf.ln()
        
        # Додаємо відступ між таблицями
        pdf.ln(5)

    # Дані для таблиць
    equipment = [
        ['Інвертор', f'{O11}', 'шт.', f'{O12}', f'{O11 * O12}'],
        ['Акумулятор', f'{O21}', 'шт.', f'{O22}', f'{O21 * O22}'],
        ['Сонячна панель', f'{O31}', 'шт.', f'{O32}', f'{O31 * O32}']
    ]
    
    # Додаємо динамічно створені рядки обладнання
    for item in dynamic_equipment:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт')
        # Додаємо крапку після одиниці виміру, якщо її ще немає
        if not unit.endswith('.'):
            unit += '.'
        price = item.get('price', 0)
        total = quantity * price
        equipment.append([name, f'{quantity}', unit, f'{price}', f'{total}'])

    # Створюємо базову структуру для mounting
    mounting = []
    
    # Додаємо профілі з K1112
    for profile in K1112:
        length = profile.get('length', 0)
        count = profile.get('count', 0)
        price = profile.get('price', 0)
        # Обчислюємо суму як кількість * ціна * метри
        total = count * price * length
        mounting.append([f'Профіль {length}м ({profile_material})', f'{count}', 'шт.', f'{price}/м', f'{total}'])
    
    # Додаємо інші елементи
    mounting.extend([
        [f'Бокові Г-образні зажими ({panel_height} мм)', f'{K21}', 'компл.', f'{K22}', f'{K21 * K22}'],
        [f'Міжпанельні V-образні зажими ({panel_height} мм)', f'{K31}', 'компл.', f'{K32}', f'{K31 * K32}'],
        [f'Гвинт шуруп М10*200 комплект ({screw_material})', f'{K41}', 'компл.', f'{K42}', f'{K41 * K42}'],
        ['Комплект з\'єднувача профілів (ЗОВНІШНІЙ)', f'{K51}', 'компл.', f'{K52}', f'{K51 * K52}'],
        ['Комплект з\'єднувача профілів (ВНУТРІШНІЙ)', f'{K61}', 'компл.', f'{K62}', f'{K61 * K62}'],
        ['Конектори МС4', f'{K91}', 'пара.', f'{K92}', f'{K91 * K92}'],
        ['Кабель', f'{K111}', 'м.', f'{K121}', f'{K111 * K121}']
    ])
    
    # Додаємо профілі каркасу та тип основи, якщо вказано матеріал каркасу
    if carcase_material:
        # Виведемо діагностичну інформацію
        print("PDF: carcase_material:", carcase_material)
        print("PDF: foundation_type_1:", foundation_type_1)
        print("PDF: carcase_profiles:", carcase_profiles)
        
        # Додаємо профілі каркасу з K71 (carcase_profiles)
        if isinstance(K71, list) and len(K71) > 0:
            for profile in K71:
                length = profile.get('length', 0)
                count = profile.get('count', 0)
                price = profile.get('price', 0)
                # Обчислюємо суму як кількість * ціна * метри (відповідно до MEMORY[2d85b207-b263-492c-a6ea-5dbfb4924d50])
                total = count * price * length
                mounting.append([f'Профіль120 {length}м ({carcase_material})', f'{count}', 'шт.', f'{price}/м', f'{total}'])
        
        # Додаємо тип основи
        if foundation_type_1 and K81 > 0:
            mounting.append([f'Основа ({foundation_type_1})', f'{K81}', 'шт.', f'{K82}', f'{K81 * K82}'])
    
    # Додаємо стійки тільки якщо їх кількість більше 0
    if K912 > 0:
        mounting.append(['Стійка 8', f'{K912}', 'шт.', f'{K922}', f'{K912 * K922}'])
    
    if K913 > 0:
        mounting.append(['Стійка 12', f'{K913}', 'шт.', f'{K923}', f'{K913 * K923}'])
    
    # Додаємо динамічно створені рядки кріплення
    for item in dynamic_mounting:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт')
        # Додаємо крапку після одиниці виміру, якщо її ще немає
        if not unit.endswith('.'):
            unit += '.'
        price = item.get('price', 0)
        total = quantity * price
        mounting.append([name, f'{quantity}', unit, f'{price}', f'{total}'])

    electrical = [
        ['Коробки з автоматами', f'{E11}', 'компл.', f'{E12}', f'{E11 * E12}'],
        ['Блискавкозахист', f'{E21}', 'компл.', f'{E22}', f'{E21 * E22}']
    ]
    
    # Додаємо динамічно створені рядки електрики
    for item in dynamic_electrical:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт')
        # Додаємо крапку після одиниці виміру, якщо її ще немає
        if not unit.endswith('.'):
            unit += '.'
        price = item.get('price', 0)
        total = quantity * price
        electrical.append([name, f'{quantity}', unit, f'{price}', f'{total}'])

    work = [
        ['Доставка', f'{R11}', 'км', f'{R12}', f'{R11 * R12}'],
        ['Роботи електрика', f'{R21}', 'послуга', f'{R22}', f'{R21 * R22}'],
        ['Монтаж', f'{R31}', 'послуга', f'{R32}', f'{R31 * R32}'],
    ]
    
    # Додаємо динамічно створені рядки роботи
    for item in dynamic_work:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт')
        # Додаємо крапку після одиниці виміру, якщо її ще немає і це не "послуга"
        if not unit.endswith('.') and unit != 'послуга':
            unit += '.'
        price = item.get('price', 0)
        total = quantity * price
        work.append([name, f'{quantity}', unit, f'{price}', f'{total}'])

    # Створюємо таблиці
    create_table('ОБЛАДНАННЯ', equipment, total=sum(float(item[4]) for item in equipment)) if O else None
    create_table('КРІПЛЕННЯ', mounting, total=sum(float(item[4]) for item in mounting)) if K else None
    create_table('ЕЛЕКТРИКА', electrical, total=sum(float(item[4]) for item in electrical)) if E else None
    create_table('РОБОТА', work, total=sum(float(item[4]) for item in work)) if R else None

    # Додаємо загальну суму
    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 10, f'Загальна сума: {total_sum}', ln=True, align='R')
    
    # Додаємо інформацію про курс долара та суму в доларах, якщо вони передані і показ суми в доларах включений
    if usd_rate > 0 and show_usd:
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f'Курс долара: {usd_rate} грн', ln=True, align='R')
        pdf.cell(0, 10, f'Сума в доларах: {total_usd} $', ln=True, align='R')
    
    # Додаємо інформацію про поточну дату
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 10, f'Дата: {current_date or date.today().strftime("%d.%m.%Y")}', ln=True, align='R')
    
    # Додаємо схеми розміщення панелей
    if panel_schemes and len(panel_schemes) > 0:
        # Якщо є окремі схеми для кожного масиву, відображаємо їх на окремих сторінках
        for i, scheme in enumerate(panel_schemes):
            # Перевіряємо, чи є base64 зображення
            if 'image_base64' in scheme and scheme['image_base64']:
                # Додаємо нову сторінку для кожної схеми (крім першої, якщо сторінка ще порожня)
                if i > 0 or pdf.get_y() > 50:
                    pdf.add_page()
                
                try:
                    # Декодуємо base64 в бінарні дані
                    image_data = base64.b64decode(scheme['image_base64'])
                    
                    # Створюємо тимчасовий файл
                    temp_image_path = os.path.join(BASE_DIR, f"temp_scheme_{i}.png")
                    
                    # Зберігаємо в тимчасовий файл
                    with open(temp_image_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Визначаємо розмір схеми (максимальна ширина сторінки з урахуванням полів)
                    img_width = 190  # Максимальна ширина сторінки A4 з урахуванням полів
                    
                    # Додаємо зображення схеми з центруванням на всю ширину сторінки
                    pdf.image(normalize_path(temp_image_path), x=10, w=img_width)
                    
                    # Видаляємо тимчасовий файл після використання
                    try:
                        os.remove(temp_image_path)
                    except:
                        pass
                except Exception as e:
                    print(f"Помилка при обробці зображення схеми: {e}")
    
    # Додаємо загальну схему, якщо вона передана і немає окремих схем
    elif scheme_image and os.path.exists(normalize_path(scheme_image)):
        pdf.ln(10)  # Додатковий відступ перед схемою
        pdf.set_font('DejaVu', 'B', 14)
        pdf.cell(0, 10, 'Схема розміщення панелей:', ln=True, align='L')
        
        # Визначаємо розмір схеми (максимальна ширина сторінки з урахуванням полів)
        img_width = 190  # Максимальна ширина сторінки A4 з урахуванням полів
        # Додаємо зображення схеми з центруванням на всю ширину сторінки
        pdf.image(normalize_path(scheme_image), x=10, w=img_width)
    
    # Перевіряємо, чи остання сторінка має контент
    pdf.check_last_page()
    
    # Шлях для збереження PDF
    output_path = normalize_path(os.path.join(BASE_DIR, "report.pdf"))

    # Зберігаємо PDF
    pdf.output(output_path)

    # Повертаємо шлях до збереженого PDF
    return output_path 
