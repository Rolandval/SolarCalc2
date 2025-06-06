from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import math
import os
import sys

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

# Отримуємо абсолютний шлях до директорії проекту
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

def generate_panel_scheme(panel_length, panel_width, panel_height, panel_arrays, orientation, available_profiles, save_path=None):
    """
    Генерує схему розміщення панелей з урахуванням профілів
    """
    # Стандартні розміри зображення
    width = 1600
    height = 1200
    
    # Розрахуємо загальну висоту, необхідну для всіх масивів
    total_required_height = 0
    num_arrays = len(panel_arrays)
    
    # Якщо масив один, використовуємо більший масштаб
    if num_arrays == 1:
        # Для одного масиву використовуємо більшу частину доступного простору
        height_per_array = height * 0.7  # 70% висоти для масиву
    else:
        # Для кількох масивів рівномірно розподіляємо простір
        # Залишаємо місце для заголовків та легенди
        available_height = height * 0.8  # 80% висоти для всіх масивів
        height_per_array = available_height / num_arrays
    
    # Перевіряємо, чи достатньо місця для всіх масивів
    for array in panel_arrays:
        rows = array['rows']
        panels_per_row = array['panels_per_row']
        
        # Розрахунок висоти для поточного масиву
        array_height = (panel_height * rows) + (0.02 * (rows - 1))
        
        # Додаємо відступ для заголовка та профілів
        array_total_height = array_height * 1.5 + 300
        
        # Перевіряємо, чи потрібно збільшити висоту зображення
        if array_total_height > height_per_array:
            total_required_height += array_total_height
        else:
            total_required_height += height_per_array
    
    # Додаємо місце для легенди
    total_required_height += 200
    
    # Збільшуємо висоту зображення, якщо потрібно
    if total_required_height > height:
        height = int(total_required_height)
    
    # Початкові координати для малювання
    start_y = 50
    current_y = start_y
    
    # Намагаємося завантажити шрифт
    try:
        # Шукаємо шрифт Arial в різних можливих директоріях
        font_path = find_file("arial.ttf", possible_font_dirs)
        
        # Якщо Arial не знайдено, спробуємо DejaVuSans
        if not font_path:
            font_path = find_file("DejaVuSans.ttf", possible_font_dirs)
            
        # Якщо знайдено шрифт, використовуємо його
        if font_path:
            font_small = ImageFont.truetype(font_path, 12)
            font_medium = ImageFont.truetype(font_path, 14)
            font_large = ImageFont.truetype(font_path, 16)
        else:
            # Якщо не знайдено жодного шрифту, використовуємо шрифт за замовчуванням
            font_small = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_large = ImageFont.load_default()
    except Exception as e:
        print(f"Помилка при завантаженні шрифту: {e}")
        # Якщо не вдається, використовуємо шрифт за замовчуванням
        font_small = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_large = ImageFont.load_default()
    
    # Визначаємо розміри панелі для малювання
    if orientation == 'альбомна':
        actual_panel_width = panel_length
        actual_panel_height = panel_width
    else:
        actual_panel_width = panel_width
        actual_panel_height = panel_length
    
    # Відступ для профілів (10см з кожного боку)
    profile_extension = 0.1
    # Відступ між панелями (2см)
    panel_gap = 0.02
    
    # Створюємо зображення з адаптивною висотою
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Малюємо кожен масив панелей
    for i, array in enumerate(panel_arrays):
        rows = array['rows']
        panels_per_row = array['panels_per_row']
        
        # Розраховуємо масштаб для поточного масиву
        if num_arrays == 1:
            # Для одного масиву використовуємо більший масштаб, щоб розтягнути на весь простір
            total_height = (actual_panel_height * rows) + (panel_gap * (rows - 1))
            total_row_width = (actual_panel_width * panels_per_row) + (panel_gap * (panels_per_row - 1))
            
            # Використовуємо більшу частину доступної площі
            scale_width = (width * 0.8) / total_row_width
            scale_height = (height * 0.6) / total_height
            
            # Вибираємо менший масштаб, щоб зберегти пропорції
            scale = min(scale_width, scale_height)
        else:
            # Для кількох масивів використовуємо масштаб, який відповідає виділеному простору
            total_height = (actual_panel_height * rows) + (panel_gap * (rows - 1))
            total_row_width = (actual_panel_width * panels_per_row) + (panel_gap * (panels_per_row - 1))
            
            # Розраховуємо доступну висоту для поточного масиву
            available_height = height_per_array * 0.7  # 70% від виділеної висоти для масиву
            
            # Розраховуємо масштаб для поточного масиву
            scale_width = (width * 0.8) / total_row_width
            scale_height = available_height / total_height
            
            # Вибираємо менший масштаб, щоб зберегти пропорції
            scale = min(scale_width, scale_height)
        
        # Розраховуємо профілі для поточного масиву
        profile_layout = calculate_profiles(panel_length, panel_width, panel_height, rows, panels_per_row, orientation, available_profiles)
        total_profile_length = profile_layout['total_length']
        
        # Відступи для центрування
        offset_x = (width - (total_row_width * scale)) / 2
        
        # Додаємо заголовок для масиву з більшим відступом
        draw.text((width/2, current_y - 30), f"Масив #{i+1} ({rows}x{panels_per_row})", 
                 fill=(0, 0, 0), font=font_large, anchor="mm")
        
        # Малюємо рамку навколо масиву для кращої видимості
        frame_padding = 30
        frame_x1 = offset_x - frame_padding
        frame_y1 = current_y - frame_padding
        frame_x2 = offset_x + (total_row_width * scale) + frame_padding
        frame_y2 = current_y + (total_height * scale) + frame_padding + 40
        draw.rectangle([frame_x1, frame_y1, frame_x2, frame_y2], outline=(100, 149, 237), width=2)
        
        # Малюємо панелі
        draw_panels(draw, offset_x, current_y, actual_panel_width, actual_panel_height, 
                   rows, panels_per_row, panel_gap, scale, font_small)
        
        # Додаємо розмірні лінії
        rotated_text = add_dimensions(draw, offset_x, current_y, total_row_width * scale, 
                                     total_height * scale, total_row_width, panel_height, 
                                     panels_per_row, rows, font_medium)
        
        # Додаємо інформацію про виступ профілів
        protrusion_length = (total_profile_length - total_row_width) / 2
        cut_length = profile_layout['cut_length']
        add_protrusion_info(draw, offset_x, current_y, actual_panel_width * scale, 
                           total_row_width * scale, protrusion_length * scale, cut_length * scale, font_small)
        
        # Малюємо профілі з більшим відступом
        profile_y = current_y + (total_height * scale) + 60
        draw_real_profiles(draw, offset_x, profile_y, total_row_width, panel_height, 
                          profile_layout['profiles'], scale, font_medium)
        
        # Оновлюємо поточну позицію Y для наступного масиву
        # Для одного масиву використовуємо менший відступ, для кількох - більший
        if num_arrays == 1:
            current_y += (total_height * scale) + 150
        else:
            current_y += (total_height * scale) + 250  # Збільшуємо відступ між масивами для уникнення накладання тексту
    
    # Додаємо легенду внизу зображення з більшим відступом
    legend_y = height - 100  # Збільшуємо відступ для легенди
    
    # Малюємо фон для легенди для кращої видимості
    legend_width = 1200
    legend_height = 80
    legend_x = (width - legend_width) / 2
    
    # Малюємо прямокутник з заокругленими кутами для фону легенди
    draw.rounded_rectangle(
        [legend_x, legend_y - legend_height/2, 
         legend_x + legend_width, legend_y + legend_height/2],
        radius=10,
        fill=(240, 249, 255),
        outline=(96, 165, 250),
        width=2
    )
    
    # Додаємо заголовок для легенди
    draw.text(
        (width/2, legend_y - legend_height/2 - 10),
        "Умовні позначення:",
        fill=(0, 0, 0),
        font=font_large,
        anchor="ms"
    )
    
    # Додаємо елементи легенди
    add_legend(draw, width / 2, legend_y, font_medium)
    
    # Зберігаємо зображення, якщо вказано шлях
    if save_path:
        # Створюємо директорію, якщо вона не існує
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)
    
    # Конвертуємо зображення в base64 для відображення в браузері
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def calculate_profiles(panel_length, panel_width, panel_height, rows, panels_per_row, orientation, available_profiles):
    if not available_profiles or len(available_profiles) == 0:
        available_profiles = [6, 4, 3, 2]
    
    # Упорядковуємо профілі за спаданням довжини
    sorted_profiles = sorted(available_profiles, reverse=True)
    
    # Розрахунок потрібної довжини (ширина ряду панелей + відступи по 10см з кожного боку)
    required_length = (panels_per_row * panel_width) + 0.2
    
    # Результат
    profiles = []
    current_pos = 0
    remaining_length = required_length
    
    while remaining_length > 0.01:
        # Знаходимо найдовший профіль, який можна використати
        selected_length = None
        for length in sorted_profiles:
            if length <= remaining_length + 0.01:
                selected_length = length
                break
        
        # Якщо не знайшли підходящий профіль, беремо найкоротший
        if selected_length is None:
            selected_length = sorted_profiles[-1]
        
        # Додаємо профіль до масиву
        profiles.append({
            'start': current_pos,
            'length': selected_length,
            'end': current_pos + selected_length
        })
        
        current_pos += selected_length
        remaining_length -= selected_length
        
        # Запобігання нескінченному циклу
        if len(profiles) > 100:
            break
    
    return {
        'profiles': profiles,
        'total_length': current_pos,
        'cut_length': required_length
    }

def draw_panels(draw, offset_x, offset_y, panel_width, panel_height, rows, panels_per_row, panel_gap, scale, font):
    # Відступи для центрування
    start_x = offset_x
    start_y = offset_y
    
    # Малюємо кожен ряд панелей
    for row in range(rows):
        row_y = start_y + (row * (panel_height + panel_gap) * scale)
        
        # Малюємо кожну панель у ряду
        for col in range(panels_per_row):
            panel_x = start_x + (col * (panel_width + panel_gap) * scale)
            
            # Малюємо панель
            draw_panel(draw, panel_x, row_y, panel_width * scale, panel_height * scale)
            
            # Малюємо затискачі
            is_first = col == 0
            is_last = col == panels_per_row - 1
            draw_clamps(draw, panel_x, row_y, panel_width * scale, panel_height * scale, is_first, is_last)
            
            # Малюємо з'єднання профілів, якщо це не остання панель у ряді
            if col < panels_per_row - 1:
                conn_x = panel_x + (panel_width * scale)
                conn_y = row_y + (panel_height * scale / 2)
                draw_profile_connection(draw, conn_x, conn_y)

def draw_panel(draw, x, y, width, height):
    # Фон панелі - робимо прозорим, але не повністю (змінюємо значення alpha з 0 на 40)
    draw.rectangle([x, y, x + width, y + height], fill=(100, 100, 100, 40))
    
    # Рамка панелі - робимо темною для кращої видимості
    draw.rectangle([x, y, x + width, y + height], outline=(20, 20, 20), width=2)
    
    # Внутрішня структура панелі - підвищуємо контрастність ліній
    line_color = (40, 40, 40)
    
    # Горизонтальні лінії
    for i in range(1, 6):
        y_pos = y + (height / 6) * i
        draw.line([x, y_pos, x + width, y_pos], fill=line_color, width=1)
    
    # Вертикальні лінії
    for i in range(1, 3):
        x_pos = x + (width / 3) * i
        draw.line([x_pos, y, x_pos, y + height], fill=line_color, width=1)

def draw_clamps(draw, x, y, width, height, is_first, is_last):
    # Позиції по золотому перетину
    upper_y = y + height * 0.382
    lower_y = y + height * 0.618
    
    # Розмір зажиму
    clamp_size = 8
    
    # Крайні зажими (зелені)
    if is_first:
        # Лівий край
        draw.rectangle(
            [x - clamp_size/2, upper_y - clamp_size/2, 
             x + clamp_size/2, upper_y + clamp_size/2],
            fill=(0, 128, 0)
        )
        draw.rectangle(
            [x - clamp_size/2, lower_y - clamp_size/2, 
             x + clamp_size/2, lower_y + clamp_size/2],
            fill=(0, 128, 0)
        )
    
    if is_last:
        # Правий край
        draw.rectangle(
            [x + width - clamp_size/2, upper_y - clamp_size/2, 
             x + width + clamp_size/2, upper_y + clamp_size/2],
            fill=(0, 128, 0)
        )
        draw.rectangle(
            [x + width - clamp_size/2, lower_y - clamp_size/2, 
             x + width + clamp_size/2, lower_y + clamp_size/2],
            fill=(0, 128, 0)
        )
    
    # Міжпанельні зажими (червоні)
    if not is_last:
        draw.rectangle(
            [x + width - clamp_size/2, upper_y - clamp_size/2, 
             x + width + clamp_size/2, upper_y + clamp_size/2],
            fill=(204, 0, 0)
        )
        draw.rectangle(
            [x + width - clamp_size/2, lower_y - clamp_size/2, 
             x + width + clamp_size/2, lower_y + clamp_size/2],
            fill=(204, 0, 0)
        )

def draw_real_profiles(draw, offset_x, y, total_width, panel_height, profiles, scale, font):
    """Малює реальні профілі з урахуванням їх довжини"""
    # Розраховуємо загальну довжину всіх профілів
    total_profile_length = sum(profile['length'] for profile in profiles)
    
    # Розраховуємо виступ профілів з кожного боку
    protrusion = (total_profile_length - total_width) / 2
    
    # Початкова позиція X для першого профілю (з урахуванням виступу)
    current_x = offset_x - (protrusion * scale)
    
    # Малюємо кожен профіль
    for i, profile in enumerate(profiles):
        profile_length = profile['length'] * scale
        profile_height = 10  # Висота профілю в пікселях
        
        # Малюємо профіль
        draw.rectangle(
            [current_x, y - profile_height/2, current_x + profile_length, y + profile_height/2],
            fill=(96, 165, 250),
            outline=(30, 64, 175),
            width=1
        )
        
        # Додаємо текст з розміром профілю
        profile_text = f"{profile['length']:.2f}м"
        text_width = draw.textlength(profile_text, font=font)
        
        # Перевіряємо, чи достатньо місця для тексту
        if profile_length > text_width + 10:
            # Центруємо текст на профілі
            text_x = current_x + (profile_length - text_width) / 2
            draw.text((text_x, y - 20), profile_text, fill=(0, 0, 0), font=font)
        else:
            # Розміщуємо текст над профілем
            draw.text((current_x, y - 25), profile_text, fill=(0, 0, 0), font=font)
        
        # Додаємо номер профілю
        profile_num = f"#{i+1}"
        draw.text((current_x + 5, y + 15), profile_num, fill=(0, 0, 0), font=font)
        
        # Оновлюємо позицію X для наступного профілю
        current_x += profile_length
        
        # Малюємо з'єднання профілів, якщо це не останній профіль
        if i < len(profiles) - 1:
            draw_profile_connection(draw, current_x, y)

def draw_profile_connection(draw, x, y):
    # Малюємо хрестик для з'єднання профілів
    conn_size = 6
    line_color = (30, 64, 175)
    line_width = 3
    
    # Додаємо більш помітний хрестик зі світлішим кольором фону
    # Спочатку малюємо фоновий круг
    background_size = conn_size + 4
    draw.ellipse([x - background_size, y - background_size, x + background_size, y + background_size], 
                 fill=(173, 216, 230))
    
    # Потім малюємо хрестик поверх кола
    draw.line([x - conn_size, y - conn_size, x + conn_size, y + conn_size], fill=line_color, width=line_width)
    draw.line([x + conn_size, y - conn_size, x - conn_size, y + conn_size], fill=line_color, width=line_width)

def add_dimensions(draw, offset_x, offset_y, total_width, total_height, row_width, panel_height, panels_per_row, rows, font):
    """Додає розмірні лінії та підписи до схеми"""
    # Горизонтальна розмірна лінія (загальна ширина)
    dim_y = offset_y + total_height + 30
    
    # Малюємо лінію
    draw.line([(offset_x, dim_y), (offset_x + total_width, dim_y)], fill=(59, 130, 246), width=2)
    
    # Додаємо засічки
    draw.line([(offset_x, dim_y - 5), (offset_x, dim_y + 5)], fill=(59, 130, 246), width=2)
    draw.line([(offset_x + total_width, dim_y - 5), (offset_x + total_width, dim_y + 5)], fill=(59, 130, 246), width=2)
    
    # Додаємо текст розміру (збільшуємо відступ для кращої видимості)
    text = f"{row_width:.2f} м"
    text_width = draw.textlength(text, font=font)
    draw.text((offset_x + (total_width - text_width) / 2, dim_y + 15), text, fill=(0, 0, 0), font=font)
    
    # Вертикальна розмірна лінія (загальна висота)
    dim_x = offset_x - 30
    
    # Малюємо лінію
    draw.line([(dim_x, offset_y), (dim_x, offset_y + total_height)], fill=(59, 130, 246), width=2)
    
    # Додаємо засічки
    draw.line([(dim_x - 5, offset_y), (dim_x + 5, offset_y)], fill=(59, 130, 246), width=2)
    draw.line([(dim_x - 5, offset_y + total_height), (dim_x + 5, offset_y + total_height)], fill=(59, 130, 246), width=2)
    
    # Додаємо текст розміру (повертаємо для кращої видимості)
    text = f"{total_height / panel_height:.2f} м"
    
    # Створюємо новий образ для повернутого тексту
    text_width = draw.textlength(text, font=font)
    text_image = Image.new('RGBA', (int(text_width) + 10, 30), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((5, 5), text, fill=(0, 0, 0), font=font)
    
    # Повертаємо текст і вставляємо його
    rotated_text = text_image.rotate(90, expand=True)
    image_width, image_height = rotated_text.size
    
    # Розміщуємо текст з більшим відступом для уникнення накладання
    draw.text((dim_x - 20, offset_y + (total_height - text_width) / 2), text, fill=(0, 0, 0), font=font, angle=90)
    
    # Додаємо інформацію про кількість панелей
    info_text = f"Всього панелей: {rows * panels_per_row}"
    draw.text((offset_x + total_width + 20, offset_y + 10), info_text, fill=(0, 0, 0), font=font)
    
    # Додаємо інформацію про розміри панелей
    panel_info = f"Розмір панелі: {panel_height:.2f} м"
    draw.text((offset_x + total_width + 20, offset_y + 30), panel_info, fill=(0, 0, 0), font=font)
    
    return rotated_text

def add_protrusion_info(draw, offset_x, offset_y, panel_width, row_width, protrusion_length, cut_length, font):
    """Додає інформацію про виступ профілів"""
    # Розраховуємо позиції для тексту (збільшуємо відступи для уникнення накладання)
    y_pos = offset_y + 50  # Збільшуємо відступ
    
    # Додаємо інформацію про виступ профілів з обох боків
    left_protrusion_text = f"Виступ зліва: {protrusion_length:.2f} м"
    right_protrusion_text = f"Виступ справа: {protrusion_length:.2f} м"
    
    # Розміщуємо текст з лівого боку з більшим відступом
    draw.text((offset_x - 150, y_pos), left_protrusion_text, fill=(220, 38, 38), font=font)
    
    # Розміщуємо текст з правого боку з більшим відступом
    draw.text((offset_x + row_width + 20, y_pos), right_protrusion_text, fill=(220, 38, 38), font=font)
    
    # Додаємо інформацію про загальну довжину відрізу
    cut_info_text = f"Загальна довжина відрізу: {cut_length:.2f} м"
    draw.text((offset_x + row_width / 2 - 100, offset_y - 60), cut_info_text, fill=(220, 38, 38), font=font)

def add_legend(draw, center_x, y, font):
    """Додає легенду з поясненнями до схеми"""
    # Розраховуємо позиції для елементів легенди
    start_x = center_x - 300
    spacing = 200  # Збільшуємо відступ між елементами легенди
    
    # Профілі
    draw_profile_sample(draw, start_x, y, 40, 5)
    draw.text((start_x + 50, y), "Профілі", fill=(0, 0, 0), font=font, anchor="lm")
    
    # З'єднання профілів
    draw_profile_connection(draw, start_x + spacing, y)
    draw.text((start_x + spacing + 40, y), "З'єднання профілів", fill=(0, 0, 0), font=font, anchor="lm")
    
    # Міжпанельні затискачі
    draw_clamp_sample(draw, start_x + spacing * 2, y, "middle")
    draw.text((start_x + spacing * 2 + 40, y), "Міжпанельні затискачі", fill=(0, 0, 0), font=font, anchor="lm")
    
    # Крайні затискачі
    draw_clamp_sample(draw, start_x + spacing * 3, y, "edge")
    draw.text((start_x + spacing * 3 + 40, y), "Крайні затискачі", fill=(0, 0, 0), font=font, anchor="lm")
    
    # Панелі
    draw_panel_sample(draw, start_x + spacing * 4, y, 30, 20)
    draw.text((start_x + spacing * 4 + 40, y), "Панелі", fill=(0, 0, 0), font=font, anchor="lm")

def draw_profile_sample(draw, x, y, width, height):
    """Малює зразок профілю для легенди"""
    draw.rectangle([x, y - height/2, x + width, y + height/2], fill=(96, 165, 250), outline=(30, 64, 175), width=1)

def draw_clamp_sample(draw, x, y, clamp_type):
    """Малює зразок затискача для легенди"""
    clamp_size = 10
    if clamp_type == "edge":
        # Крайній затискач (зелений)
        draw.rectangle(
            [x - clamp_size/2, y - clamp_size/2, 
             x + clamp_size/2, y + clamp_size/2],
            fill=(34, 197, 94), outline=(21, 128, 61), width=1)
    else:
        # Міжпанельний затискач (червоний)
        draw.rectangle(
            [x - clamp_size/2, y - clamp_size/2, 
             x + clamp_size/2, y + clamp_size/2],
            fill=(239, 68, 68), outline=(185, 28, 28), width=1)

def draw_panel_sample(draw, x, y, width, height):
    """Малює зразок панелі для легенди"""
    # Малюємо панель (сірий прямокутник)
    draw.rectangle([x, y - height/2, x + width, y + height/2], 
                  fill=(100, 100, 100), outline=(50, 50, 50), width=1)

# Функція для збереження схеми у файл і повернення шляху для використання в PDF
def save_panel_scheme(panel_length, panel_width, panel_height, panel_arrays, orientation, available_profiles):
    # Отримуємо абсолютний шлях до директорії проекту
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формуємо шлях для збереження схеми
    file_name = f"panel_scheme_{len(panel_arrays)}_arrays.png"
    save_path = normalize_path(os.path.join(base_dir, "static", "images", file_name))
    
    # Створюємо директорію, якщо вона не існує
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Генеруємо і зберігаємо схему
    generate_panel_scheme(panel_length, panel_width, panel_height, panel_arrays, orientation, 
                          available_profiles, save_path=save_path)
    
    return save_path
