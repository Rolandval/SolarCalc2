import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Можливі шляхи до шрифтів
possible_font_dirs = [
    "C:\\Windows\\Fonts",
    "/usr/share/fonts/truetype",
    "/System/Library/Fonts",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
]

def find_file(filename, search_paths):
    """Шукає файл у вказаних шляхах"""
    for path in search_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if filename.lower() in [f.lower() for f in files]:
                    return os.path.join(root, filename)
    return None

def draw_panel(draw, x, y, width, height, fill_color=(220, 220, 220), outline_color=(100, 100, 100)):
    """
    Малює одну сонячну панель
    
    Args:
        draw: Об'єкт для малювання
        x, y: Координати верхнього лівого кута
        width, height: Ширина і висота панелі
        fill_color: Колір заливки
        outline_color: Колір контуру
    """
    # Малюємо прямокутник панелі
    draw.rectangle(
        [x, y, x + width, y + height],
        fill=fill_color,
        outline=outline_color,
        width=2
    )
    
    # Додаємо внутрішню структуру панелі (імітація комірок)
    cell_rows = 6
    cell_cols = 10
    cell_width = width / cell_cols
    cell_height = height / cell_rows
    
    # Малюємо сітку комірок
    for i in range(1, cell_rows):
        y_line = y + i * cell_height
        draw.line([(x, y_line), (x + width, y_line)], fill=outline_color, width=1)
    
    for i in range(1, cell_cols):
        x_line = x + i * cell_width
        draw.line([(x_line, y), (x_line, y + height)], fill=outline_color, width=1)

def draw_clamp(draw, x, y, width, height, clamp_type="middle"):
    """
    Малює затискач для панелі
    
    Args:
        draw: Об'єкт для малювання
        x, y: Координати центру затискача
        width, height: Ширина і висота панелі (для розрахунку розміру затискача)
        clamp_type: Тип затискача ("edge" - крайовий, "middle" - міжпанельний)
    """
    clamp_size = min(width, height) * 0.05  # Розмір затискача пропорційний до розміру панелі
    
    if clamp_type == "edge":
        # Крайовий затискач (L-подібний)
        color = (0, 128, 0)  # Зелений колір для крайових затискачів
        
        # Малюємо L-подібну форму
        draw.rectangle(
            [x - clamp_size, y - clamp_size/2, x, y + clamp_size/2],
            fill=color,
            outline=(0, 0, 0),
            width=1
        )
        draw.rectangle(
            [x - clamp_size, y - clamp_size/2, x + clamp_size/2, y],
            fill=color,
            outline=(0, 0, 0),
            width=1
        )
    else:
        # Міжпанельний затискач (прямокутний)
        color = (204, 0, 0)  # Червоний колір для міжпанельних затискачів
        
        draw.rectangle(
            [x - clamp_size/2, y - clamp_size/2, x + clamp_size/2, y + clamp_size/2],
            fill=color,
            outline=(0, 0, 0),
            width=1
        )

def draw_profile(draw, x1, y1, x2, y2, color=(96, 165, 250)):
    """
    Малює профіль (горизонтальну балку) для кріплення панелей
    
    Args:
        draw: Об'єкт для малювання
        x1, y1: Початкова точка профілю
        x2, y2: Кінцева точка профілю
        color: Колір профілю
    """
    profile_height = 8  # Висота профілю в пікселях
    
    # Малюємо профіль як прямокутник
    draw.rectangle(
        [x1, y1 - profile_height/2, x2, y1 + profile_height/2],
        fill=color,
        outline=(30, 64, 175),
        width=1
    )

def generate_panel_schemes(panel_length, panel_width, panel_height, panel_arrays, orientation, available_profiles=None):
    """
    Генерує схеми розміщення панелей для кожного масиву.
    
    Args:
        panel_length (float): Довжина панелі в метрах
        panel_width (float): Ширина панелі в метрах
        panel_height (float): Висота профілю панелі в міліметрах (не використовується в новій версії)
        panel_arrays (list): Список масивів панелей (кожен масив - словник з rows, panels_per_row, name)
        orientation (str): Орієнтація панелей ('альбомна' або 'книжкова')
        available_profiles (list): Доступні довжини профілів у метрах (не використовується в новій версії)
    
    Returns:
        list: Список схем для кожного масиву у форматі base64
    """
    schemes = []
    
    # Пошук шрифту
    font_path = find_file("arial.ttf", possible_font_dirs)
    if not font_path:
        font_path = find_file("DejaVuSans.ttf", possible_font_dirs)
    
    # Завантаження шрифту
    font = None
    title_font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, 16)
            title_font = ImageFont.truetype(font_path, 24)
        except Exception as e:
            print(f"Помилка завантаження шрифту: {e}")
    
    # Масштаб для перетворення метрів у пікселі
    scale = 100  # 1 метр = 100 пікселів
    
    # Відступ між панелями в пікселях
    panel_gap = 10
    
    # Визначаємо розміри панелі в залежності від орієнтації
    if orientation == 'альбомна':
        # Альбомна орієнтація - панель розташована горизонтально
        panel_w = panel_length
        panel_h = panel_width
    else:
        # Книжкова орієнтація - панель розташована вертикально
        panel_w = panel_width
        panel_h = panel_length
    
    # Обробляємо кожен масив
    for i, array in enumerate(panel_arrays):
        rows = array['rows']
        panels_per_row = array['panels_per_row']
        array_name = array.get('name', f'Масив #{i+1}')
        
        # Розраховуємо ширину ряду та висоту масиву в метрах
        row_width_m = panel_w * panels_per_row + (panel_gap / scale) * (panels_per_row - 1)
        array_height_m = panel_h * rows + (panel_gap / scale) * (rows - 1)
        
        # Розраховуємо ширину ряду та висоту масиву в пікселях
        row_width_px = panel_w * scale * panels_per_row + panel_gap * (panels_per_row - 1)
        array_height_px = panel_h * scale * rows + panel_gap * (rows - 1)
        
        # Відступи для зображення
        margin = 200
        
        # Розраховуємо розміри зображення
        img_width = int(row_width_px + margin * 2)
        img_height = int(array_height_px + margin * 2.5)  # Додатковий відступ знизу для легенди
        
        # Створюємо зображення з білим фоном
        image = Image.new('RGB', (img_width, img_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # Розраховуємо відступи для центрування схеми
        offset_x = margin
        offset_y = margin
        
        # Малюємо всі панелі
        for row in range(rows):
            # Позиції профілів для поточного ряду
            profile_y1 = offset_y + row * (panel_h * scale + panel_gap) + panel_h * scale * 0.25
            profile_y2 = offset_y + row * (panel_h * scale + panel_gap) + panel_h * scale * 0.75
            
            # Малюємо два профілі для кожного ряду
            # Профіль 1 (верхній)
            draw_profile(
                draw,
                offset_x - 20,  # Виступ профілю зліва
                profile_y1,
                offset_x + row_width_px + 20,  # Виступ профілю справа
                profile_y1
            )
            
            # Профіль 2 (нижній)
            draw_profile(
                draw,
                offset_x - 20,  # Виступ профілю зліва
                profile_y2,
                offset_x + row_width_px + 20,  # Виступ профілю справа
                profile_y2
            )
            
            for col in range(panels_per_row):
                # Розраховуємо позицію панелі
                x = offset_x + col * (panel_w * scale + panel_gap)
                y = offset_y + row * (panel_h * scale + panel_gap)
                
                # Малюємо панель
                draw_panel(draw, x, y, panel_w * scale, panel_h * scale)
                
                # Додаємо номер панелі
                panel_number = row * panels_per_row + col + 1
                text_x = x + (panel_w * scale) / 2
                text_y = y + (panel_h * scale) / 2
                
                if font:
                    draw.text((text_x, text_y), str(panel_number), fill=(0, 0, 0), font=font, anchor="mm")
                else:
                    draw.text((text_x, text_y), str(panel_number), fill=(0, 0, 0), anchor="mm")
                
                # Додаємо міжпанельні затискачі на профілях (якщо не остання панель в ряду)
                if col < panels_per_row - 1:
                    # Позиція для міжпанельного затискача
                    clamp_x = x + panel_w * scale + panel_gap / 2
                    
                    # Додаємо затискачі на обох профілях
                    draw_clamp(draw, clamp_x, profile_y1, panel_w * scale, panel_h * scale, "middle")
                    draw_clamp(draw, clamp_x, profile_y2, panel_w * scale, panel_h * scale, "middle")
                
                # Додаємо крайові затискачі на профілях на початку і в кінці ряду
                if col == 0:  # Лівий край
                    # Додаємо затискачі на обох профілях
                    draw_clamp(draw, x, profile_y1, panel_w * scale, panel_h * scale, "edge")
                    draw_clamp(draw, x, profile_y2, panel_w * scale, panel_h * scale, "edge")
                
                if col == panels_per_row - 1:  # Правий край
                    # Позиція для крайового затискача
                    clamp_x = x + panel_w * scale
                    
                    # Додаємо затискачі на обох профілях
                    draw_clamp(draw, clamp_x, profile_y1, panel_w * scale, panel_h * scale, "edge")
                    draw_clamp(draw, clamp_x, profile_y2, panel_w * scale, panel_h * scale, "edge")
        
        # Додаємо розмірні лінії
        # Горизонтальна розмірна лінія (ширина ряду)
        dim_y = offset_y + array_height_px + 50
        line_color = (59, 130, 246)  # Синій колір для розмірних ліній
        
        # Малюємо горизонтальну лінію
        draw.line([(offset_x, dim_y), (offset_x + row_width_px, dim_y)], fill=line_color, width=2)
        
        # Додаємо засічки
        draw.line([(offset_x, dim_y - 10), (offset_x, dim_y + 10)], fill=line_color, width=2)
        draw.line([(offset_x + row_width_px, dim_y - 10), (offset_x + row_width_px, dim_y + 10)], fill=line_color, width=2)
        
        # Додаємо текст розміру
        width_text = f"{row_width_m:.2f} м"
        if font:
            text_width = draw.textlength(width_text, font=font)
            draw.text(
                (offset_x + (row_width_px - text_width) / 2, dim_y + 15),
                width_text,
                fill=(0, 0, 0),
                font=font
            )
        
        # Вертикальна розмірна лінія (висота масиву)
        dim_x = offset_x - 50
        
        # Малюємо вертикальну лінію
        draw.line([(dim_x, offset_y), (dim_x, offset_y + array_height_px)], fill=line_color, width=2)
        
        # Додаємо засічки
        draw.line([(dim_x - 10, offset_y), (dim_x + 10, offset_y)], fill=line_color, width=2)
        draw.line([(dim_x - 10, offset_y + array_height_px), (dim_x + 10, offset_y + array_height_px)], fill=line_color, width=2)
        
        # Додаємо текст розміру для висоти
        height_text = f"{array_height_m:.2f} м"
        if font:
            # Створюємо тимчасове зображення для тексту
            text_width = draw.textlength(height_text, font=font)
            text_height = font.getbbox(height_text)[3] - font.getbbox(height_text)[1]
            
            # Створюємо тимчасове зображення для тексту
            text_img = Image.new('RGBA', (int(text_width), int(text_height + 10)), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((0, 0), height_text, fill=(0, 0, 0), font=font)
            
            # Повертаємо текст на 90 градусів
            rotated_text = text_img.rotate(90, expand=True)
            
            # Розміщуємо повернутий текст
            image.paste(
                rotated_text,
                (int(dim_x - text_height - 15), int(offset_y + (array_height_px - text_width) / 2)),
                rotated_text
            )
        
        # Додаємо легенду
        legend_y = img_height - margin / 2
        
        # Малюємо елементи легенди
        legend_items = [
            {"color": (220, 220, 220), "text": "Сонячна панель"},
            {"color": (96, 165, 250), "text": "Профіль кріплення"},
            {"color": (0, 128, 0), "text": "Крайовий затискач"},
            {"color": (204, 0, 0), "text": "Міжпанельний затискач"}
        ]
        
        # Розраховуємо позиції для елементів легенди
        legend_spacing = 200
        legend_start_x = img_width / 2 - (len(legend_items) * legend_spacing) / 2
        
        for idx, item in enumerate(legend_items):
            # Позиція елемента
            item_x = legend_start_x + idx * legend_spacing
            
            # Малюємо квадрат з кольором
            draw.rectangle(
                [item_x, legend_y - 10, item_x + 20, legend_y + 10],
                fill=item["color"],
                outline=(0, 0, 0),
                width=1
            )
            
            # Додаємо текст
            if font:
                draw.text(
                    (item_x + 30, legend_y),
                    item["text"],
                    fill=(0, 0, 0),
                    font=font,
                    anchor="lm"
                )
        
        # Додаємо заголовок схеми з назвою масиву та орієнтацією
        title = f"{array_name} ({rows}x{panels_per_row}, {orientation} орієнтація)"
        
        if title_font:
            title_width = draw.textlength(title, font=title_font)
            draw.text(
                ((img_width - title_width) / 2, 30),
                title,
                fill=(0, 0, 0),
                font=title_font
            )
        
        # Додаємо інформацію про кількість панелей
        total_panels_text = f"Всього панелей: {rows * panels_per_row}"
        if font:
            draw.text(
                (offset_x, offset_y - 30),
                total_panels_text,
                fill=(0, 0, 0),
                font=font
            )
        
        # Конвертуємо зображення в base64
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Додаємо схему до результатів
        schemes.append({
            'array_id': i,
            'name': array_name,
            'rows': rows,
            'panels_per_row': panels_per_row,
            'total_panels': rows * panels_per_row,
            'orientation': orientation,
            'image_base64': img_str
        })
    
    return schemes

def calculate_profiles(panel_length, panel_width, rows, panels_per_row, orientation):
    """
    Розраховує необхідні профілі для монтажу панелей
    
    Args:
        panel_length (float): Довжина панелі в метрах
        panel_width (float): Ширина панелі в метрах
        rows (int): Кількість рядів
        panels_per_row (int): Кількість панелей в ряду
        orientation (str): Орієнтація панелей ('альбомна' або 'книжкова')
    
    Returns:
        dict: Інформація про профілі
    """
    # Визначаємо розміри панелі в залежності від орієнтації
    if orientation == 'альбомна':
        # Альбомна орієнтація - панель розташована горизонтально
        panel_w = panel_length
        panel_h = panel_width
    else:
        # Книжкова орієнтація - панель розташована вертикально
        panel_w = panel_width
        panel_h = panel_length
    
    # Розраховуємо ширину ряду в метрах
    row_width = panel_w * panels_per_row
    
    # Додаємо виступ профілю з кожного боку (20 см)
    profile_length = row_width + 0.4  # Додаємо по 20 см з кожного боку
    
    # Кожен ряд має 2 профілі
    profiles_per_row = 2
    
    # Загальна кількість профілів
    total_profiles = rows * profiles_per_row
    
    # Загальна довжина профілів
    total_profile_length = total_profiles * profile_length
    
    return {
        'profile_length': profile_length,
        'profiles_per_row': profiles_per_row,
        'total_profiles': total_profiles,
        'total_length': total_profile_length
    }