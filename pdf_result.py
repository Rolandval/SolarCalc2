from fpdf import FPDF
import os
import shutil
from datetime import date
import base64
import logging
import io
from django.conf import settings
from calculator.models import Panels, Inverters, Batteries

# Налаштовуємо логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        K71: list = [],
        K81: int = 0, K82: float = 0.0,
        K91: int = 0, K92: float = 0.0,
        K111: int = 0, K121: float = 0.0,
        K112: int = 0, K122: float = 0.0,
        K211: int = 0, K221: float = 0.0,
        K212: int = 0, K222: float = 0.0,
        K912: int = 0, K922: float = 0.0,
        K913: int = 0, K923: float = 0.0,
        E11: int = 0, E12: float = 0.0,
        E21: int = 0, E22: float = 0.0,
        R11: int = 0, R12: float = 0.0,
        R21: int = 0, R22: float = 0.0,
        R31: int = 0, R32: float = 0.0,
        panel_model_name: str = '',
        panel_length: float = 0.0,
        panel_width: float = 0.0,
        panel_height: float = 0.0,
        panel_arrangement: str = '',
        panel_type: str = '',
        total_panels: int = 0,
        total_rows: int = 0,
        avg_panels_per_row: float = 0.0,
        usd_rate: float = 0.0,
        show_usd: bool = False,
        current_date: str = '',
        scheme_image: str = '',
        panel_schemes: list = [],
        carcase_material: str = '',  # Додаємо матеріал каркасу
        foundation_type_1: str = '',  # Додаємо тип основи
        carcase_profiles: list = [],  # Додаємо профілі каркасу
        include_panel_ds: bool = False,  # Додаємо параметр для включення datasheet панелі
        include_inverter_ds: bool = False,  # Додаємо параметр для включення datasheet інвертора
        include_battery_ds: bool = False,  # Додаємо параметр для включення datasheet батареї
        panel_model_id: str = '',  # ID моделі панелі для завантаження datasheet
        inverter_model_id: str = '',  # ID моделі інвертора для завантаження datasheet
        battery_model_id: str = '',  # ID моделі батареї для завантаження datasheet
        dynamic_equipment: list = [],  # Додаємо динамічні рядки обладнання
        dynamic_mounting: list = [],  # Додаємо динамічні рядки кріплень
        dynamic_electrical: list = [],  # Додаємо динамічні рядки електрики
        dynamic_work: list = [],  # Додаємо динамічні рядки роботи
        dynamic_other: list = [],  # Додаємо динамічні рядки інших матеріалів
        total_usd: float = 0.0,  # Додаємо суму в доларах
        screw_material: str = 'оцинковані',  # Додаємо матеріал гвинтів
        profile_material: str = 'алюміній',  # Додаємо матеріал профілю
        panel_arrays: list = [],  # Додаємо дані про масиви панелей
        panel_brand: str = '',  # Додаємо бренд панелі
        panel_model: str = '',  # Додаємо модель панелі
        inverter_brand: str = '',  # Додаємо бренд інвертора
        inverter_model: str = '',  # Додаємо модель інвертора
        battery_brand: str = '',  # Додаємо бренд батареї
        battery_model: str = '',  # Додаємо модель батареї
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

    # Функція для формування назв обладнання
    def get_equipment_title(equip_type, brand, model):
        if brand and model:
            if equip_type == 'panel':
                return f"Сонячна панель {brand} {model}"
            elif equip_type == 'inverter':
                return f"Інвертор {brand} {model}"
            elif equip_type == 'battery':
                return f"Акумулятор {brand} {model}"
        else:
            if equip_type == 'panel':
                return "Сонячна панель"
            elif equip_type == 'inverter':
                return "Інвертор"
            elif equip_type == 'battery':
                return "Акумулятор"

    # Дані для таблиць
    equipment = [
        [get_equipment_title('panel', panel_brand, panel_model), f'{O11}', 'шт.', f'{O12}', f'{O11 * O12}'],
        [get_equipment_title('inverter', inverter_brand, inverter_model), f'{O21}', 'шт.', f'{O22}', f'{O21 * O22}'],
        [get_equipment_title('battery', battery_brand, battery_model), f'{O31}', 'шт.', f'{O32}', f'{O31 * O32}']
    ]
    
    # Додаємо стійки тільки якщо їх кількість більше 0
    if K912 > 0:
        equipment.append(['Стійка 8', f'{K912}', 'шт.', f'{K922}', f'{K912 * K922}'])
    
    if K913 > 0:
        equipment.append(['Стійка 12', f'{K913}', 'шт.', f'{K923}', f'{K913 * K923}'])
    
    # Додаємо динамічно створені рядки обладнання
    for item in dynamic_equipment:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт.')
        price = item.get('price', 0)
        total = quantity * price
        
        equipment.append([name, f'{quantity}', unit, f'{price}', f'{total}'])
    print(equipment)

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
        ['Конектори МС4', f'{K91}', 'пара.', f'{K92}', f'{K91 * K92}'],
        ['Кабель (червоний)', f'{K111}', 'м.', f'{K121}', f'{K111 * K121}'],
        ['Кабель (чорний)', f'{K211}', 'м.', f'{K221}', f'{K211 * K221}']
    ])
    
    # Додаємо профілі каркасу та тип основи, якщо вказано матеріал каркасу
    if carcase_material:
        # Виведемо діагностичну інформацію
        logger.info("PDF: carcase_material: %s", carcase_material)
        logger.info("PDF: foundation_type_1: %s", foundation_type_1)
        logger.info("PDF: carcase_profiles: %s", carcase_profiles)
        
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
    
    # Видаляємо стійки з розділу "КРІПЛЕННЯ", оскільки вони тепер в "ОБЛАДНАННЯ"
    # if K912 > 0:
    #     mounting.append(['Стійка 8', f'{K912}', 'шт.', f'{K922}', f'{K912 * K922}'])
    
    # if K913 > 0:
    #     mounting.append(['Стійка 12', f'{K913}', 'шт.', f'{K923}', f'{K913 * K923}'])
    
    # Додаємо динамічно створені рядки кріплення
    for item in dynamic_mounting:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт.')
        price = item.get('price', 0)
        total = quantity * price
        
        mounting.append([name, f'{quantity}', unit, f'{price}', f'{total}'])
    print(mounting)

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
    print(electrical)

    work = [
        ['Монтаж', f'{R11}', 'шт.', f'{R12}', f'{R11 * R12}'],
        ['Проектування', f'{R21}', 'шт.', f'{R22}', f'{R21 * R22}'],
        ['Доставка', f'{R31}', 'шт.', f'{R32}', f'{R31 * R32}']
    ]
    
    # Додаємо динамічно створені рядки роботи
    for item in dynamic_work:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт.')
        price = item.get('price', 0)
        total = quantity * price
        
        work.append([name, f'{quantity}', unit, f'{price}', f'{total}'])
    print(work)
        
    # Додаємо динамічно створені рядки інших матеріалів
    other = []
    for item in dynamic_other:
        name = item.get('name', '')
        quantity = item.get('quantity', 0)
        unit = item.get('unit', 'шт.')
        price = item.get('price', 0)
        total = quantity * price
        
        other.append([name, f'{quantity}', unit, f'{price}', f'{total}'])

    # Створюємо таблиці
    create_table('ОБЛАДНАННЯ', equipment, total=sum(float(item[4]) for item in equipment)) if O else None
    create_table('КРІПЛЕННЯ', mounting, total=sum(float(item[4]) for item in mounting)) if K else None
    create_table('ЕЛЕКТРИКА', electrical, total=sum(float(item[4]) for item in electrical)) if E else None
    create_table('РОБОТА', work, total=sum(float(item[4]) for item in work)) if R else None
    create_table('ІНШІ МАТЕРІАЛИ', other, total=sum(float(item[4]) for item in other)) if other else None

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
                    logger.error(f"Помилка при обробці зображення схеми: {e}")
    
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
    
    # Додаємо datasheet панелі, якщо потрібно
    if include_panel_ds and panel_model_id:
        try:
            from django.conf import settings
            from calculator.models import Panels
            
            logger.info(f"Спроба отримати панель з ID: {panel_model_id}")
            # Отримуємо панель з бази даних
            panel = Panels.objects.get(id=panel_model_id)
            logger.info(f"Панель знайдено: {panel.model}")
            
            # Перевіряємо, чи є datasheet
            if panel.datasheet:
                datasheet_path = str(panel.datasheet)
                logger.info(f"Datasheet панелі знайдено: {datasheet_path}")
                
                # Перевіряємо різні можливі шляхи до файлу
                found = False
                paths_to_check = [
                    datasheet_path,  # Оригінальний шлях
                    os.path.join(settings.MEDIA_ROOT, datasheet_path) if 'MEDIA_ROOT' in globals() else None,  # MEDIA_ROOT + шлях
                    os.path.join(BASE_DIR, 'media', 'datasheets', os.path.basename(datasheet_path)),  # BASE_DIR/media/datasheets + ім'я файлу
                    os.path.join(BASE_DIR, 'media', datasheet_path),  # BASE_DIR/media + шлях
                    os.path.join(BASE_DIR, datasheet_path),  # BASE_DIR + шлях
                ]
                
                for path in paths_to_check:
                    if path:
                        logger.info(f"Перевірка шляху: {path}")
                        if os.path.exists(path):
                            datasheet_path = path
                            found = True
                            logger.info(f"Знайдено файл datasheet за шляхом: {datasheet_path}")
                            break
                
                if found:
                    # Додаємо нову сторінку для datasheet
                    pdf.add_page()
                    
                    # Отримуємо розширення файлу
                    file_ext = os.path.splitext(datasheet_path)[1].lower()
                    logger.info(f"Розширення файлу datasheet: {file_ext}")
                    
                    # Додаємо заголовок
                    pdf.set_font('DejaVu', 'B', 14)
                    pdf.cell(0, 10, f'Технічна специфікація панелі {panel.model}', ln=True, align='C')
                    pdf.ln(5)
                    
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        # Якщо це зображення, додаємо його напряму
                        logger.info(f"Файл datasheet є зображенням: {file_ext}")
                        try:
                            pdf.image(normalize_path(datasheet_path), x=10, w=190)
                            logger.info("Зображення datasheet додано до PDF")
                        except Exception as e:
                            logger.error(f"Помилка при додаванні зображення datasheet: {e}")
                    elif file_ext == '.pdf':
                        # Якщо це PDF, копіюємо файл і додаємо посилання
                        logger.info("Файл datasheet є PDF")
                        
                        # Копіюємо файл в директорію з результатами
                        result_dir = os.path.join(BASE_DIR, 'media', 'results')
                        os.makedirs(result_dir, exist_ok=True)
                        
                        # Генеруємо унікальне ім'я файлу
                        filename = os.path.basename(datasheet_path)
                        new_path = os.path.join(result_dir, f"panel_{panel.id}_{filename}")
                        
                        try:
                            shutil.copy2(datasheet_path, new_path)
                            logger.info(f"PDF файл скопійовано у: {new_path}")
                            
                            # Додаємо посилання на файл
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Datasheet доступний за посиланням:', ln=True)
                            pdf.ln(5)
                            pdf.cell(0, 10, f'{new_path}', ln=True)
                            pdf.ln(5)
                        except Exception as e:
                            logger.error(f"Помилка при копіюванні PDF файлу: {e}")
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Помилка при копіюванні PDF файлу: {e}', ln=True)
                            pdf.ln(5)
                    else:
                        # Непідтримуваний формат
                        logger.error(f"Непідтримуваний формат файлу datasheet: {file_ext}")
                        pdf.set_font('DejaVu', '', 12)
                        pdf.cell(0, 10, f'Непідтримуваний формат файлу datasheet: {file_ext}', ln=True)
                        pdf.ln(5)
                else:
                    logger.error(f"Файл datasheet не знайдено за жодним із шляхів")
                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 10, f'Файл datasheet не знайдено', ln=True)
                    pdf.ln(5)
            else:
                logger.info("Datasheet для панелі не вказано")
        except Exception as e:
            logger.error(f"Помилка при отриманні datasheet: {e}")
    
    # Додаємо datasheet інвертора, якщо потрібно
    if include_inverter_ds and inverter_model_id:
        try:
            inverter = Inverters.objects.get(id=inverter_model_id)
            logger.info(f"Інвертор знайдено: {inverter.model}")
            
            if inverter.datasheet:
                datasheet_path = str(inverter.datasheet)
                logger.info(f"Datasheet інвертора знайдено: {datasheet_path}")
                
                # Перевіряємо різні можливі шляхи до файлу
                found = False
                paths_to_check = [
                    datasheet_path,  # Оригінальний шлях
                    os.path.join(settings.MEDIA_ROOT, datasheet_path) if 'settings' in globals() and hasattr(settings, 'MEDIA_ROOT') else None,  # MEDIA_ROOT + шлях
                    os.path.join(BASE_DIR, 'media', 'datasheets', os.path.basename(datasheet_path)),  # BASE_DIR/media/datasheets + ім'я файлу
                    os.path.join(BASE_DIR, 'media', datasheet_path),  # BASE_DIR/media + шлях
                    os.path.join(BASE_DIR, datasheet_path),  # BASE_DIR + шлях
                ]
                
                for path in paths_to_check:
                    if path:
                        logger.info(f"Перевірка шляху для інвертора: {path}")
                        if os.path.exists(path):
                            datasheet_path = path
                            found = True
                            logger.info(f"Знайдено файл datasheet інвертора за шляхом: {datasheet_path}")
                            break
                
                if found:
                    # Додаємо нову сторінку для datasheet
                    pdf.add_page()
                    
                    # Отримуємо розширення файлу
                    file_ext = os.path.splitext(datasheet_path)[1].lower()
                    logger.info(f"Розширення файлу datasheet інвертора: {file_ext}")
                    
                    # Додаємо заголовок
                    pdf.set_font('DejaVu', 'B', 14)
                    pdf.cell(0, 10, f'Технічна специфікація інвертора {inverter.model}', ln=True, align='C')
                    pdf.ln(5)
                    
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        # Якщо це зображення, додаємо його напряму
                        logger.info(f"Файл datasheet інвертора є зображенням: {file_ext}")
                        try:
                            pdf.image(normalize_path(datasheet_path), x=10, w=190)
                            logger.info("Зображення datasheet інвертора додано до PDF")
                        except Exception as e:
                            logger.error(f"Помилка при додаванні зображення datasheet інвертора: {e}")
                    elif file_ext == '.pdf':
                        # Якщо це PDF, копіюємо файл і додаємо посилання
                        logger.info("Файл datasheet інвертора є PDF")
                        
                        # Копіюємо файл в директорію з результатами
                        result_dir = os.path.join(BASE_DIR, 'media', 'results')
                        os.makedirs(result_dir, exist_ok=True)
                        
                        # Генеруємо унікальне ім'я файлу
                        filename = os.path.basename(datasheet_path)
                        new_path = os.path.join(result_dir, f"inverter_{inverter.id}_{filename}")
                        
                        try:
                            shutil.copy2(datasheet_path, new_path)
                            logger.info(f"PDF файл інвертора скопійовано у: {new_path}")
                            
                            # Додаємо посилання на файл
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Datasheet доступний за посиланням:', ln=True)
                            pdf.ln(5)
                            pdf.cell(0, 10, f'{new_path}', ln=True)
                            pdf.ln(5)
                        except Exception as e:
                            logger.error(f"Помилка при копіюванні PDF файлу інвертора: {e}")
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Помилка при копіюванні PDF файлу інвертора: {e}', ln=True)
                            pdf.ln(5)
                    else:
                        # Непідтримуваний формат
                        logger.error(f"Непідтримуваний формат файлу datasheet інвертора: {file_ext}")
                        pdf.set_font('DejaVu', '', 12)
                        pdf.cell(0, 10, f'Непідтримуваний формат файлу datasheet інвертора: {file_ext}', ln=True)
                        pdf.ln(5)
                else:
                    logger.error(f"Файл datasheet інвертора не знайдено за жодним із шляхів")
                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 10, f'Файл datasheet інвертора не знайдено', ln=True)
                    pdf.ln(5)
            else:
                logger.info("Datasheet для інвертора не вказано")
        except Exception as e:
            logger.error(f"Помилка при отриманні datasheet інвертора: {e}")
    
    # Додаємо datasheet батареї, якщо потрібно
    if include_battery_ds and battery_model_id:
        try:
            battery = Batteries.objects.get(id=battery_model_id)
            logger.info(f"Батарею знайдено: {battery.model}")
            
            if battery.datasheet:
                datasheet_path = str(battery.datasheet)
                logger.info(f"Datasheet батареї знайдено: {datasheet_path}")
                
                # Перевіряємо різні можливі шляхи до файлу
                found = False
                paths_to_check = [
                    datasheet_path,  # Оригінальний шлях
                    os.path.join(settings.MEDIA_ROOT, datasheet_path) if 'settings' in globals() and hasattr(settings, 'MEDIA_ROOT') else None,  # MEDIA_ROOT + шлях
                    os.path.join(BASE_DIR, 'media', 'datasheets', os.path.basename(datasheet_path)),  # BASE_DIR/media/datasheets + ім'я файлу
                    os.path.join(BASE_DIR, 'media', datasheet_path),  # BASE_DIR/media + шлях
                    os.path.join(BASE_DIR, datasheet_path),  # BASE_DIR + шлях
                ]
                
                for path in paths_to_check:
                    if path:
                        logger.info(f"Перевірка шляху для батареї: {path}")
                        if os.path.exists(path):
                            datasheet_path = path
                            found = True
                            logger.info(f"Знайдено файл datasheet батареї за шляхом: {datasheet_path}")
                            break
                
                if found:
                    # Додаємо нову сторінку для datasheet
                    pdf.add_page()
                    
                    # Отримуємо розширення файлу
                    file_ext = os.path.splitext(datasheet_path)[1].lower()
                    logger.info(f"Розширення файлу datasheet батареї: {file_ext}")
                    
                    # Додаємо заголовок
                    pdf.set_font('DejaVu', 'B', 14)
                    pdf.cell(0, 10, f'Технічна специфікація батареї {battery.model}', ln=True, align='C')
                    pdf.ln(5)
                    
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        # Якщо це зображення, додаємо його напряму
                        logger.info(f"Файл datasheet батареї є зображенням: {file_ext}")
                        try:
                            pdf.image(normalize_path(datasheet_path), x=10, w=190)
                            logger.info("Зображення datasheet батареї додано до PDF")
                        except Exception as e:
                            logger.error(f"Помилка при додаванні зображення datasheet батареї: {e}")
                    elif file_ext == '.pdf':
                        # Якщо це PDF, копіюємо файл і додаємо посилання
                        logger.info("Файл datasheet батареї є PDF")
                        
                        # Копіюємо файл в директорію з результатами
                        result_dir = os.path.join(BASE_DIR, 'media', 'results')
                        os.makedirs(result_dir, exist_ok=True)
                        
                        # Генеруємо унікальне ім'я файлу
                        filename = os.path.basename(datasheet_path)
                        new_path = os.path.join(result_dir, f"battery_{battery.id}_{filename}")
                        
                        try:
                            shutil.copy2(datasheet_path, new_path)
                            logger.info(f"PDF файл батареї скопійовано у: {new_path}")
                            
                            # Додаємо посилання на файл
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Datasheet доступний за посиланням:', ln=True)
                            pdf.ln(5)
                            pdf.cell(0, 10, f'{new_path}', ln=True)
                            pdf.ln(5)
                        except Exception as e:
                            logger.error(f"Помилка при копіюванні PDF файлу батареї: {e}")
                            pdf.set_font('DejaVu', '', 12)
                            pdf.cell(0, 10, f'Помилка при копіюванні PDF файлу батареї: {e}', ln=True)
                            pdf.ln(5)
                    else:
                        # Непідтримуваний формат
                        logger.error(f"Непідтримуваний формат файлу datasheet батареї: {file_ext}")
                        pdf.set_font('DejaVu', '', 12)
                        pdf.cell(0, 10, f'Непідтримуваний формат файлу datasheet батареї: {file_ext}', ln=True)
                        pdf.ln(5)
                else:
                    logger.error(f"Файл datasheet батареї не знайдено за жодним із шляхів")
                    pdf.set_font('DejaVu', '', 12)
                    pdf.cell(0, 10, f'Файл datasheet батареї не знайдено', ln=True)
                    pdf.ln(5)
            else:
                logger.info("Datasheet для батареї не вказано")
        except Exception as e:
            logger.error(f"Помилка при отриманні datasheet батареї: {e}")
    
    # Шлях для збереження PDF
    output_path = normalize_path(os.path.join(BASE_DIR, "report.pdf"))

    # Зберігаємо PDF
    pdf.output(output_path)

    # Повертаємо шлях до збереженого PDF
    return output_path 
