from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import traceback
from django.http import HttpResponse
from panel_scheme_report import generate_panel_scheme, save_panel_scheme
from panel_scheme import generate_panel_schemes
from pdf_result import generate
from django import template
import math
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import os
from .models import Panels, Inverters, Batteries
import uuid
import requests
from datetime import datetime
import shutil
from telegram_bot import send_pdf_to_telegram, start_bot
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from django.core.mail import EmailMessage
from django.contrib import messages

register = template.Library()

# Функція для нормалізації шляхів (заміна зворотних слешів на прямі)
def normalize_path(path):
    if path is None:
        return None
    return path.replace('\\', '/')

# Функція для отримання курсу долара
def get_usd_rate():
    try:
        # Використовуємо API Національного банку України для отримання курсу
        response = requests.get('https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json')
        if response.status_code == 200:
            data = response.json()
            # Шукаємо долар США (код USD - 840)
            for currency in data:
                if currency['r030'] == 840:  # Код долара США
                    return currency['rate']
        
        # Якщо не вдалося отримати курс, повертаємо значення за замовчуванням
        return 42.5
    except Exception as e:
        print(f"Помилка при отриманні курсу долара: {e}")
        # Повертаємо значення за замовчуванням у разі помилки
        return 42.5


@ensure_csrf_cookie
def index(request):
    # Отримуємо всі доступні панелі, інвертори та батареї з бази даних
    panels = Panels.objects.all()
    inverters = Inverters.objects.all()
    batteries = Batteries.objects.all()
    
    # Згрупуємо панелі за брендами для зручності
    brands = {}
    for panel in panels:
        if panel.brand not in brands:
            brands[panel.brand] = []
        brands[panel.brand].append({
            'id': panel.id,
            'model': panel.model,
            'length': float(panel.panel_length),
            'width': float(panel.panel_width),
            'height': float(panel.panel_height),
            'panel_type': str(panel.panel_type),
        })
    
    # Згрупуємо інвертори за брендами
    inverter_brands = {}
    for inverter in inverters:
        if inverter.brand not in inverter_brands:
            inverter_brands[inverter.brand] = []
        inverter_brands[inverter.brand].append({
            'id': inverter.id,
            'model': inverter.model,
            'power': float(inverter.power),
            'phases_count': inverter.phases_count,
            'voltage_type': inverter.voltage_type,
            'strings_count': inverter.strings_count

        })
    
    # Згрупуємо батареї за брендами
    battery_brands = {}
    for battery in batteries:
        if battery.brand not in battery_brands:
            battery_brands[battery.brand] = []
        battery_brands[battery.brand].append({
            'id': battery.id,
            'model': battery.model,
            'capacity': float(battery.capacity),
            'is_head': battery.is_head,
            'is_stand': battery.is_stand,
            'voltage_type': battery.voltage_type
        })
    
    # Конвертуємо дані в JSON для використання в JavaScript
    brands_json = json.dumps(brands)
    inverter_brands_json = json.dumps(inverter_brands)
    battery_brands_json = json.dumps(battery_brands)
    
    context = {
        'results': None,
        'panels': panels,
        'brands': brands,
        'brands_json': brands_json,
        'inverters': inverters,
        'inverter_brands': inverter_brands,
        'inverter_brands_json': inverter_brands_json,
        'batteries': batteries,
        'battery_brands': battery_brands,
        'battery_brands_json': battery_brands_json
    }
    return render(request, 'index.html', context=context)


@csrf_exempt
def calculate(request):
    """
    Обробляє дані форми та повертає результати розрахунку.
    """
    if request.method == 'POST':
        try:
            # Отримання даних
            data = request.POST.dict()
            
            # Отримання даних інвертора та акумулятора, якщо вони вибрані
            inverter_model_name = ''
            battery_model_name = ''
            
            # Отримання даних інвертора
            if 'inverter_model' in data and data['inverter_model']:
                try:
                    inverter = Inverters.objects.get(id=data['inverter_model'])
                    inverter_model_name = f"{inverter.brand} {inverter.model}"
                except Inverters.DoesNotExist:
                    inverter_model_name = data.get('custom_inverter_model', '')
            else:
                inverter_model_name = data.get('custom_inverter_model', '')
            
            # Отримання даних акумулятора
            if 'battery_model' in data and data['battery_model']:
                try:
                    battery = Batteries.objects.get(id=data['battery_model'])
                    battery_model_name = f"{battery.brand} {battery.model}"
                except Batteries.DoesNotExist:
                    battery_model_name = data.get('custom_battery_model', '')
            else:
                battery_model_name = data.get('custom_battery_model', '')
            
            # Визначення розмірів панелі з id моделі або з прямого введення
            if 'panel_model' in data and data['panel_model']:
                # Отримуємо дані панелі з бази за id
                try:
                    panel = Panels.objects.get(id=data['panel_model'])
                    panel_length = float(panel.panel_length)
                    panel_width = float(panel.panel_width)
                    panel_height = float(panel.panel_height)
                    panel_model_name = f"{panel.brand} {panel.model}"  # Зберігаємо назву моделі
                    panel_brand = panel.brand  # Додаємо бренд панелі
                except Panels.DoesNotExist:
                    # Якщо панель не знайдена, використовуємо значення з форми
                    panel_length = float(data.get('panel_length', 0))
                    panel_width = float(data.get('panel_width', 0))
                    panel_height = float(data.get('panel_height', 0))
                    panel_model_name = data.get('custom_panel_model', '')  # Використовуємо введену назву
                    panel_brand = data.get('panel_brand', '')  # Додаємо бренд панелі
            else:
                # Якщо id моделі не вказано, використовуємо значення з форми
                panel_length = float(data.get('panel_length', 0))
                panel_width = float(data.get('panel_width', 0))
                panel_height = float(data.get('panel_height', 0))
                panel_model_name = data.get('custom_panel_model', '')  # Використовуємо введену назву
                panel_brand = data.get('panel_brand', '')  # Додаємо бренд панелі
            
            # Ініціалізуємо змінні для наземного розміщення з значеннями за замовчуванням
            carcase_material = None
            column_distance = 0
            carcase_high = 0
            available_carcase_lengths = []
            a = 0
            
            if 'ground_mounting' in data and data['ground_mounting'] == 'on':
                # Отримуємо параметри наземного розміщення
                if 'frame_material_1' in data:
                    carcase_material = data.get('frame_material_1', '')
                if 'column_distance_1' in data:
                    column_distance = float(data.get('column_distance_1', 0))
                if 'mounting_height_1' in data:
                    carcase_high = float(data.get('mounting_height_1', 0))
                if 'mounting_angle_1' in data:
                    a = float(data.get('mounting_angle_1', 0))
                if 'profile_carcase_lengths' in data:
                    available_carcase_lengths = [float(x.strip()) for x in data['profile_carcase_lengths'].split(',')]
                elif not available_carcase_lengths:  # Якщо не вказано, використовуємо значення за замовчуванням
                    available_carcase_lengths = [3.0, 4.0, 6.0]

            # Обробка масивів панелей
            panel_arrays = []
            array_index = 1
            total_panels = 0
            
            while f'rows_{array_index}' in data:
                rows = int(data.get(f'rows_{array_index}', 0))
                panels_per_row = int(data.get(f'panels_per_row_{array_index}', 0))
                array_name = data.get(f'array_name_{array_index}', f'Масив #{array_index}')
                array_orientation = data.get(f'array_orientation_{array_index}', 'альбомна')
                
                if rows > 0 and panels_per_row > 0:
                    panel_arrays.append({
                        'id': array_index,
                        'rows': rows,
                        'panels_per_row': panels_per_row,
                        'total': rows * panels_per_row,
                        'name': array_name,
                        'orientation': array_orientation
                    })
                    total_panels += rows * panels_per_row
                
                array_index += 1
            
            # Перевірка наявності масивів панелей
            if not panel_arrays:
                return JsonResponse({'success': False, 'error': 'Необхідно вказати хоча б один масив панелей'})
            
            # Перевірка відповідності загальної кількості панелей
            if total_panels != int(data.get('total_panels', 0)):
                return JsonResponse({'success': False, 'error': 'Загальна кількість панелей не співпадає з сумою панелей у масивах'})
            
            panel_arrangement = data.get('panel_arrangement', '')
            if panel_arrangement == '':
                return JsonResponse({'success': False, 'error': 'Необхідно вибрати розташування профілів'})
            panel_type = data.get('panel_type', '')
            if panel_type == '':
                return JsonResponse({'success': False, 'error': 'Необхідно вибрати тип панелі'})
            available_lengths = [float(x.strip()) for x in data['profile_lengths'].split(',')]
            strings = int(data.get('string_count', 0))

            # Розрахунок загальної довжини профілів для всіх масивів
            total_profil_len = 0
            total_carcase_len = 0
            total_carcase_count = 0
            for array in panel_arrays:
                rows = array['rows']
                panels_per_row = array['panels_per_row']
                
                array_profil_len = 0
                if array['orientation'] == 'альбомна':
                    array_profil_len = (((panel_length * panels_per_row) + (0.002*(panels_per_row - 1)) + 0.01) * rows) * 2
                    if carcase_material == 'оцинкований' or carcase_material == 'алюміній' or carcase_material == 'залізо':
                        vertical_profile_len = (panel_width * rows) - 0.12
                        c = vertical_profile_len - 0.12
                        N = int(((panel_width * panels_per_row) / column_distance) + 1)
                        K = math.sin(math.radians(a)) * c
                        carcase_profile = (carcase_high * N * 2) + (K * N)
                        array_profil_len += vertical_profile_len * N
                        total_carcase_len += carcase_profile
                        total_carcase_count += N * 2

                elif array['orientation'] == 'портретна':
                    array_profil_len = (((panel_width * panels_per_row) + (0.002*(panels_per_row - 1)) + 0.01) * rows) * 2
                    if carcase_material == 'оцинкований' or carcase_material == 'алюміній' or carcase_material == 'залізо':
                        vertical_profile_len = (panel_length * rows) - 0.12
                        c = vertical_profile_len - 0.12
                        N = int(((panel_length * panels_per_row) / column_distance) + 1)
                        K = math.sin(math.radians(a)) * c
                        carcase_profile = (carcase_high * N * 2) + (K * N)
                        array_profil_len += vertical_profile_len * N
                        total_carcase_len += carcase_profile
                        total_carcase_count += N * 2
                
                array['profil_len'] = array_profil_len
                total_profil_len += array_profil_len
            
            sorted_arr = sorted(available_lengths, reverse=True)
            profiles = []
            remaining_length = total_profil_len
            while remaining_length > 0:
                possible_lengths = [l for l in sorted_arr if l <= remaining_length]
                if not possible_lengths:
                    profiles.append(sorted_arr[-1])
                    break
                best_length = max(possible_lengths)
                profiles.append(best_length)
                remaining_length -= best_length

            # Підрахунок кількості кожного типу профілю
            profile_counts = {length: profiles.count(length) for length in set(profiles)}
            grouped_profiles = [{'length': length, 'count': count} for length, count in profile_counts.items()]
            profiles_count = sum(profile_counts.values())



            sorted_carcase_arr = sorted(available_carcase_lengths, reverse=True)
            carcase_profiles = []
            remaining_carcase_length = total_carcase_len
            while remaining_carcase_length > 0:
                possible_carcase_lengths = [l for l in sorted_carcase_arr if l <= remaining_carcase_length]
                if not possible_carcase_lengths:
                    carcase_profiles.append(sorted_carcase_arr[-1])
                    break
                best_length = max(possible_carcase_lengths)
                carcase_profiles.append(best_length)
                remaining_carcase_length -= best_length

            # Підрахунок кількості кожного типу профілю
            carcase_profile_counts = {length: carcase_profiles.count(length) for length in set(carcase_profiles)}
            grouped_carcase_profiles = [{'length': length, 'count': count} for length, count in carcase_profile_counts.items()]

            # Розрахунок загальної кількості затискачів для всіх масивів
            total_g_clamps = 0
            for array in panel_arrays:
                array_g_clamps = 4 * array['rows']
                array['g_clamps'] = array_g_clamps
                total_g_clamps += array_g_clamps
            
            # Розрахунок загальної кількості вертикальних затискачів для всіх масивів
            total_v_clamps = 0
            for array in panel_arrays:
                array_v_clamps = (array['total'] * 2) - 2
                array['v_clamps'] = array_v_clamps
                total_v_clamps += array_v_clamps
            
            # Розрахунок загальної кількості монтажних шин для всіх масивів
            total_m_sh = 0
            for array in panel_arrays:
                array_m_sh = math.ceil(array['profil_len'] / 0.9)
                array['m_sh'] = array_m_sh
                total_m_sh += array_m_sh
            
            # Розрахунок загальної кількості фронтальних конекторів для всіх масивів
            total_front_connectors = profiles_count - 1
            
            # Розрахунок загальної кількості конекторів для всіх масивів
            total_connectors = 0
            for array in panel_arrays:
                array_connectors = 0
                if array['orientation'] == 'альбомна':
                    array_connectors += (strings * 2) + 1
                elif array['orientation'] == 'портретна':
                    array_connectors += ((strings * 2) + 1) + array['rows']
                array['connectors'] = array_connectors
                total_connectors += array_connectors

            # Генеруємо схему
            scheme_image = generate_panel_scheme(
                panel_length, panel_width, panel_height,
                panel_arrays,
                panel_arrangement, available_lengths
            )
            
            # Генеруємо окремі схеми для кожного масиву
            panel_schemes = generate_panel_schemes(
                panel_length, panel_width, panel_height,
                panel_arrays,
                panel_arrangement, available_lengths
            )
            
            # Серіалізуємо схеми панелей в JSON для передачі в PDF-звіт
            panel_schemes_json = json.dumps(panel_schemes)
            
            scheme_file_path = save_panel_scheme(
                panel_length, panel_width, panel_height,
                panel_arrays,
                panel_arrangement, available_lengths
            )
            
            # Конвертуємо зображення в base64
            scheme_base64 = scheme_image
            
            # Отримуємо курс долара
            usd_rate = round(get_usd_rate(), 2)
            
            # Повертаємо результат
            results = {
                'success': True,
                'data': {
                    'panel_count': total_panels,
                    'profiles': grouped_profiles,
                    'g_clamps': total_g_clamps,
                    'v_clamps': total_v_clamps,
                    'm_sh': total_m_sh,
                    'front_connectors': total_front_connectors,
                    'connectors': total_connectors,
                    'scheme_image': f'data:image/png;base64,{scheme_base64}',
                    'scheme_file_path': scheme_file_path,  # Додаємо шлях до файлу схеми
                    'panel_schemes': panel_schemes,  # Додаємо окремі схеми для кожного масиву
                    'panel_schemes_json': panel_schemes_json,  # Додаємо серіалізовані схеми для PDF-звіту
                    'usd_rate': usd_rate,  # Додаємо курс долара
                    'panel_data': {
                        'panel_model': panel_model_name,
                        'panel_brand': panel_brand,  # Додаємо бренд панелі
                        'panel_length': panel_length,
                        'panel_width': panel_width,
                        'panel_height': panel_height,
                        'panel_arrangement': panel_arrangement,
                        'panel_type': panel_type,
                        'panel_arrays': panel_arrays,
                        'total_panels': total_panels,
                        'profile_lengths': data.get('profile_lengths', ''),
                        'string_count': data.get('string_count', ''),
                        'screw_material': data.get('screw_material', 'оцинковані'),  # Додаємо матеріал гвинт-шурупа
                        'profile_material': data.get('profile_material', 'алюміній'),  # Додаємо матеріал профілю
                        'foundation_type_1': data.get('foundation_type_1', 'забивна палка'),
                        'grouped_carcase_profiles': grouped_carcase_profiles,
                        # Додаткові параметри (необов'язкові)
                        'inverterModel': data.get('custom_inverter_model', '') or data.get('inverter_model', ''),
                        'inverterPower': data.get('inverter_power', ''),
                        'inverterPhases': data.get('inverter_phases', ''),
                        'inverterBrand': data.get('inverter_brand', ''),
                        'inverterVoltage': data.get('inverter_voltage', ''),
                        'inverterModelId': data.get('inverter_model', ''),
                        'batteryModel': data.get('custom_battery_model', '') or data.get('battery_model', ''),
                        'batteryPower': data.get('battery_capacity', ''),
                        'batteryBrand': data.get('battery_brand', ''),
                        'batteryVoltage': data.get('battery_voltage', ''),
                        'batteryModelId': data.get('battery_model', ''),
                        'batteryIsHead': 'Так' if data.get('battery_is_head') else 'Ні',
                        'batteryIsStand': 'Так' if data.get('battery_is_stand') else 'Ні',
                        'batteryIsStand8': 'Так' if data.get('battery_is_stand_8') else 'Ні',
                        'batteryIsStand12': 'Так' if data.get('battery_is_stand_12') else 'Ні',
                        'panelModelId': data.get('panel_model', ''),
                        'panelModelName': panel_model_name,  # Додаємо назву моделі
                        'inverterModelName': inverter_model_name,  # Додаємо назву моделі інвертора
                        'batteryModelName': battery_model_name,  # Додаємо назву моделі батареї
                        'current_date': datetime.now().strftime('%Y-%m-%d'),  # Додаємо поточну дату
                    }
                }
            }
            print(results)
            print("Profiles dictionary:", profile_counts)

            # Додаємо дані про каркас до контексту, якщо наземне розміщення активовано
            if carcase_material:
                results['data'].update({
                    'carcase_material': carcase_material,
                    'column_distance': column_distance,
                    'carcase_high': carcase_high,
                    'mounting_angle': a,
                    'total_carcase_len': total_carcase_len,
                    'total_carcase_count': total_carcase_count,
                    'grouped_carcase_profiles': grouped_carcase_profiles
                })
                
                # Додаємо тип основи
                if 'foundation_type_1' in data:
                    results['data']['foundation_type_1'] = data.get('foundation_type_1', 'забивна палка')
                else:
                    results['data']['foundation_type_1'] = 'забивна палка'
            
            # Додаємо поточну дату та інформацію про обладнання в контекст
            results['data']['current_date'] = datetime.now().strftime('%d.%m.%Y')
            
            # Переносимо дані з panel_data у верхній рівень data для доступу в шаблоні
            if 'panel_data' in results['data']:
                for key, value in results['data']['panel_data'].items():
                    results['data'][key] = value
            
            return render(request, 'table.html', context=results)

        except Exception as e:
             return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def generate_pdf(request):
    if request.method == 'POST':
        try:
            # Отримуємо дані з параметрів запиту
            data = request.POST.dict()
            print("Отримані дані:", data)
            
            # Правильно обробляємо чекбокси
            # Якщо чекбокс відмічений, він буде присутній у request.POST зі значенням 'on'
            param_o = 'param-o' in request.POST
            param_k = 'param-k' in request.POST
            param_e = 'param-e' in request.POST
            param_r = 'param-r' in request.POST
            param_usd = 'param-usd' in request.POST
            
            print(f"Параметри для PDF: O={param_o}, K={param_k}, E={param_e}, R={param_r}, USD={param_usd}")
            
            # Отримуємо параметри для включення datasheet
            include_panel_ds = request.POST.get('include_panel_ds') == 'on'
            include_inverter_ds = request.POST.get('include_inverter_ds') == 'on'
            include_battery_ds = request.POST.get('include_battery_ds') == 'on'
            
            # Отримуємо дані з форми
            panel_model_name = data.get('panel_model_name', '')
            panel_length = float(data.get('panel_length', 0))
            panel_width = float(data.get('panel_width', 0))
            panel_height = float(data.get('panel_height', 0))
            panel_arrangement = data.get('panel_arrangement', '')
            panel_type = data.get('panel_type', '')
            
            # Отримуємо ідентифікатори моделей для datasheet
            panel_model_id = data.get('panelModelId', '')
            inverter_model_id = data.get('inverterModelId', '')
            battery_model_id = data.get('batteryModelId', '')
            
            # Отримуємо дані про масиви панелей
            panel_arrays = json.loads(data.get('panel_arrays', '[]'))
            total_panels = int(data.get('total_panels', 0))
            
            # Розрахунок загальної кількості рядів для відображення в PDF
            total_rows = sum(array['rows'] for array in panel_arrays)
            
            # Розрахунок середньої кількості панелей в ряді для відображення в PDF
            avg_panels_per_row = total_panels / total_rows if total_rows > 0 else 0
            
            # Отримуємо схеми для кожного масиву, якщо вони є
            panel_schemes = []
            if 'panel_schemes' in data:
                try:
                    panel_schemes = json.loads(data.get('panel_schemes', '[]'))
                except json.JSONDecodeError:
                    print("Помилка декодування panel_schemes з JSON")
            
            # Створюємо списки для K11 і K12
            K11_values = []
            K12_values = {}
            
            # Збираємо всі наявні параметри K11_{length} та K12_{length}
            for key, value in data.items():
                if key.startswith('K11_') and value:
                    length = key.replace('K11_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        count = int(value)
                        K11_values.append({"length": length_float, "count": count})
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
                        
                elif key.startswith('K12_') and value:
                    length = key.replace('K12_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        price = float(value)
                        K12_values[length_float] = price
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Збираємо динамічні рядки для кріплень (K10n, K11n, K12n, K13n для n=0,1,2,...)
            dynamic_mounting = []
            
            # Перебираємо всі ключі, які починаються з K10, K11, K12, K13 і мають довжину 4 символи (для нового формату)
            for key, value in data.items():
                if (key.startswith('K10') or key.startswith('K11') or key.startswith('K12') or key.startswith('K13')) and len(key) == 4 and value:
                    # Отримуємо індекс рядка (останній символ)
                    row_index = key[3]
                    
                    # Перевіряємо, чи це назва елемента (K10n)
                    if key.startswith('K10'):
                        name = value
                        # Шукаємо відповідні кількість, ціну та суму
                        quantity_key = f'K11{row_index}'
                        price_key = f'K12{row_index}'
                        
                        quantity = int(data.get(quantity_key, 0) or 0)
                        price = float(data.get(price_key, 0) or 0.0)
                        
                        # Додаємо до списку динамічних рядків
                        if name and quantity > 0:
                            dynamic_mounting.append({
                                'name': name,
                                'quantity': quantity,
                                'unit': 'шт',
                                'price': price
                            })
                            print(f"Додано динамічний рядок: назва={name}, кількість={quantity}, ціна={price}")
            
            # Виведемо діагностичну інформацію
            print("K11_values keys:", [key for key in data.keys() if key.startswith('K11_')])
            
            # Створюємо масив словників для профілів
            k_values = []
            for item in K11_values:
                length = item["length"]
                count = item["count"]
                # Шукаємо відповідну ціну для цієї довжини
                price = K12_values.get(length, 0)
                
                k_values.append({
                    "length": length, 
                    "count": count,
                    "price": price
                })
                
            print("K11_values:", K11_values)
            print("K12_values:", K12_values)
            print("k_values:", k_values)
            
            # Збираємо параметри для профілів каркасу (K71_*)
            carcase_profiles = []
            for key, value in data.items():
                if key.startswith('K71_') and value:
                    length = key.replace('K71_', '')
                    try:
                        # Шукаємо відповідну ціну для цієї довжини
                        # Спочатку шукаємо з комою, як в оригінальному ключі
                        price_key = f'K72_{key.replace("K71_", "")}'
                        price = float(data.get(price_key, 0) or 0)
                        print(f"Профіль120 {length}м: кількість={value}, ціна_ключ={price_key}, ціна={price}")
                        carcase_profiles.append({
                            "length": float(length.replace(',', '.')), 
                            "count": int(value),
                            "price": price
                        })
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Виведемо діагностичну інформацію для профілів каркасу
            print("K71_* keys:", [key for key in data.keys() if key.startswith('K71_')])
            print("carcase_profiles:", carcase_profiles)
            print("carcase_material:", data.get('carcase_material', ''))
            print("foundation_type_1:", data.get('foundation_type_1', ''))
            
            # Збираємо динамічно додані рядки для кожної категорії
            dynamic_equipment = []
            dynamic_mounting = []
            dynamic_electrical = []
            dynamic_work = []
            dynamic_other = []  # Додаємо порожній список для dynamic_other
            
            # Обробляємо динамічні рядки для обладнання (O)
            for key in sorted([k for k in data.keys() if k.startswith('O') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка (наприклад, з O41 отримуємо 4)
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'O{row_num}1', 0) or 0)
                    unit = data.get(f'O{row_num}unit', 'шт')
                    price = float(data.get(f'O{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_equipment.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для кріплення (K)
            for key in sorted([k for k in data.keys() if k.startswith('K') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 7]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'K{row_num}1', 0) or 0)
                    unit = data.get(f'K{row_num}unit', 'шт')
                    price = float(data.get(f'K{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_mounting.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для електрики (E)
            for key in sorted([k for k in data.keys() if k.startswith('E') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 2]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'E{row_num}1', 0) or 0)
                    unit = data.get(f'E{row_num}unit', 'шт')
                    price = float(data.get(f'E{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_electrical.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для роботи (R)
            for key in sorted([k for k in data.keys() if k.startswith('R') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'R{row_num}1', 0) or 0)
                    unit = data.get(f'R{row_num}unit', 'шт')
                    price = float(data.get(f'R{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_work.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })

            # --- Normalize brand/model extraction for panel ---
            panel_brand = data.get('panel_brand', '')
            panel_model = data.get('panel_model', '')
            if panel_brand == 'other':
                panel_brand = data.get('custom_panel_brand', '')
            if panel_model == 'other':
                panel_model = data.get('custom_panel_model', '')

            # --- Normalize brand/model extraction for inverter ---
            inverter_brand = data.get('inverter_brand', '')
            inverter_model = data.get('inverter_model', '')
            if inverter_brand == 'other':
                inverter_brand = data.get('custom_inverter_brand', '')
            if inverter_model == 'other':
                inverter_model = data.get('custom_inverter_model', '')

            # --- Normalize brand/model extraction for battery ---
            battery_brand = data.get('battery_brand', '')
            battery_model = data.get('battery_model', '')
            if battery_brand == 'other':
                battery_brand = data.get('custom_battery_brand', '')
            if battery_model == 'other':
                battery_model = data.get('custom_battery_model', '')

            print(f"PDF: panel_brand={panel_brand}, panel_model={panel_model}, inverter_brand={inverter_brand}, inverter_model={inverter_model}, battery_brand={battery_brand}, battery_model={battery_model}")

            # Викликаємо функцію generate з отриманими даними
            pdf_path = generate(
                O=param_o, K=param_k, E=param_e, R=param_r,
                O11=int(data.get('O11', 0) or 0), O12=float(data.get('O12', 0) or 0.0),
                O21=int(data.get('O21', 0) or 0), O22=float(data.get('O22', 0) or 0.0),
                O31=int(data.get('O31', 0) or 0), O32=float(data.get('O32', 0) or 0.0),
                K1112=k_values,
                K21=int(data.get('K21', 0) or 0), K22=float(data.get('K22', 0) or 0.0),
                K31=int(data.get('K31', 0) or 0), K32=float(data.get('K32', 0) or 0.0),
                K41=int(data.get('K41', 0) or 0), K42=float(data.get('K42', 0) or 0.0),
                K51=int(data.get('K51', 0) or 0), K52=float(data.get('K52', 0) or 0.0),
                K71=carcase_profiles,
                K81=int(data.get('K81', 0) or 0), K82=float(data.get('K82', 0) or 0.0),
                K91=int(data.get('K91', 0) or 0), K92=float(data.get('K92', 0) or 0.0),
                K111=int(data.get('K111', 0) or 0), K121=float(data.get('K121', 0) or 0.0),
                K112=int(data.get('K112', 0) or 0), K122=float(data.get('K122', 0) or 0.0),
                K211=int(data.get('K211', 0) or 0), K221=float(data.get('K221', 0) or 0.0),
                K212=int(data.get('K212', 0) or 0), K222=float(data.get('K222', 0) or 0.0),
                K912=int(data.get('K912', 0) or 0), K922=float(data.get('K922', 0) or 0.0),
                K913=int(data.get('K913', 0) or 0), K923=float(data.get('K923', 0) or 0.0),
                E11=int(data.get('E11', 0) or 0), E12=float(data.get('E12', 0) or 0.0),
                E21=int(data.get('E21', 0) or 0), E22=float(data.get('E22', 0) or 0.0),
                R11=int(data.get('R11', 0) or 0), R12=float(data.get('R12', 0) or 0.0),
                R21=int(data.get('R21', 0) or 0), R22=float(data.get('R22', 0) or 0.0),
                R31=int(data.get('R31', 0) or 0), R32=float(data.get('R32', 0) or 0.0),
                scheme_image=normalize_path(str(data.get('scheme_image', ''))),
                dynamic_equipment=dynamic_equipment,
                dynamic_mounting=dynamic_mounting,
                dynamic_electrical=dynamic_electrical,
                dynamic_work=dynamic_work,
                dynamic_other=dynamic_other,
                usd_rate=float(data.get('usd_rate', '0').replace(',', '.') or 0.0),
                total_usd=float(data.get('total_usd', '0').replace(',', '.') or 0.0),
                screw_material=data.get('screw_material', 'оцинковані'),
                profile_material=data.get('profile_material', 'алюміній'),
                current_date=datetime.now().strftime('%d.%m.%Y'),
                show_usd=param_usd,
                panel_model_name=panel_model_name,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                panel_arrangement=panel_arrangement,
                panel_type=panel_type,
                panel_arrays=panel_arrays,
                total_panels=total_panels,
                total_rows=total_rows,
                avg_panels_per_row=avg_panels_per_row,
                panel_schemes=panel_schemes,
                carcase_material=data.get('carcase_material', ''),
                foundation_type_1=data.get('foundation_type_1', ''),
                carcase_profiles=carcase_profiles,
                include_panel_ds=include_panel_ds,
                include_inverter_ds=include_inverter_ds,
                include_battery_ds=include_battery_ds,
                panel_model_id=panel_model_id,
                inverter_model_id=inverter_model_id,
                battery_model_id=battery_model_id,
                panel_brand=panel_brand,
                panel_model=panel_model,
                inverter_brand=inverter_brand,
                inverter_model=inverter_model,
                battery_brand=battery_brand,
                battery_model=battery_model,
            )

            # Нормалізуємо шлях до PDF
            pdf_path = normalize_path(pdf_path)

            # Повертаємо згенерований PDF
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf:
                    response = HttpResponse(pdf.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename=report.pdf'
                    return response
            else:
                return JsonResponse({'success': False, 'error': f'PDF файл не знайдено за шляхом: {pdf_path}'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def send_pdf_telegram(request):
    """
    Ендпоінт для генерації та відправки PDF звіту через Telegram
    """
    if request.method == 'POST':
        try:
            # Отримуємо дані з параметрів запиту
            data = request.POST.dict()
            print("Отримані дані для Telegram:", data)
            
            # Правильно обробляємо чекбокси
            # Якщо чекбокс відмічений, він буде присутній у request.POST зі значенням 'on'
            param_o = 'param-o' in request.POST
            param_k = 'param-k' in request.POST
            param_e = 'param-e' in request.POST
            param_r = 'param-r' in request.POST
            param_usd = 'param-usd' in request.POST
            
            print(f"Параметри для Telegram PDF: O={param_o}, K={param_k}, E={param_e}, R={param_r}, USD={param_usd}")
            
            # Отримуємо параметри для включення datasheet
            include_panel_ds = request.POST.get('include_panel_ds') == 'on'
            include_inverter_ds = request.POST.get('include_inverter_ds') == 'on'
            include_battery_ds = request.POST.get('include_battery_ds') == 'on'
            
            # Отримуємо дані з форми
            panel_model_name = data.get('panel_model_name', '')
            panel_length = float(data.get('panel_length', 0))
            panel_width = float(data.get('panel_width', 0))
            panel_height = float(data.get('panel_height', 0))
            panel_arrangement = data.get('panel_arrangement', '')
            panel_type = data.get('panel_type', '')
            
            # Отримуємо ідентифікатори моделей для datasheet
            panel_model_id = data.get('panelModelId', '')
            inverter_model_id = data.get('inverterModelId', '')
            battery_model_id = data.get('batteryModelId', '')
            
            # Отримуємо дані про масиви панелей
            panel_arrays = json.loads(data.get('panel_arrays', '[]'))
            total_panels = int(data.get('total_panels', 0))
            
            # Розрахунок загальної кількості рядів для відображення в PDF
            total_rows = sum(array['rows'] for array in panel_arrays)
            
            # Розрахунок середньої кількості панелей в ряді для відображення в PDF
            avg_panels_per_row = total_panels / total_rows if total_rows > 0 else 0
            
            # Отримуємо схеми для кожного масиву, якщо вони є
            panel_schemes = []
            if 'panel_schemes' in data:
                try:
                    panel_schemes = json.loads(data.get('panel_schemes', '[]'))
                except json.JSONDecodeError:
                    print("Помилка декодування panel_schemes з JSON")
            
            # Створюємо списки для K11 і K12
            K11_values = []
            K12_values = {}
            
            # Збираємо всі наявні параметри K11_{length} та K12_{length}
            for key, value in data.items():
                if key.startswith('K11_') and value:
                    length = key.replace('K11_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        count = int(value)
                        K11_values.append({"length": length_float, "count": count})
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
                        
                elif key.startswith('K12_') and value:
                    length = key.replace('K12_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        price = float(value)
                        K12_values[length_float] = price
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Збираємо динамічні рядки для кріплень (K10n, K11n, K12n, K13n для n=0,1,2,...)
            dynamic_mounting = []
            
            # Перебираємо всі ключі, які починаються з K10, K11, K12, K13 і мають довжину 4 символи (для нового формату)
            for key, value in data.items():
                if (key.startswith('K10') or key.startswith('K11') or key.startswith('K12') or key.startswith('K13')) and len(key) == 4 and value:
                    # Отримуємо індекс рядка (останній символ)
                    row_index = key[3]
                    
                    # Перевіряємо, чи це назва елемента (K10n)
                    if key.startswith('K10'):
                        name = value
                        # Шукаємо відповідні кількість, ціну та суму
                        quantity_key = f'K11{row_index}'
                        price_key = f'K12{row_index}'
                        
                        quantity = int(data.get(quantity_key, 0) or 0)
                        price = float(data.get(price_key, 0) or 0.0)
                        
                        # Додаємо до списку динамічних рядків
                        if name and quantity > 0:
                            dynamic_mounting.append({
                                'name': name,
                                'quantity': quantity,
                                'unit': 'шт',
                                'price': price
                            })
                            print(f"Додано динамічний рядок: назва={name}, кількість={quantity}, ціна={price}")
            
            # Виведемо діагностичну інформацію
            print("K11_values keys:", [key for key in data.keys() if key.startswith('K11_')])
            
            # Створюємо масив словників для профілів
            k_values = []
            for item in K11_values:
                length = item["length"]
                count = item["count"]
                # Шукаємо відповідну ціну для цієї довжини
                price = K12_values.get(length, 0)
                
                k_values.append({
                    "length": length, 
                    "count": count,
                    "price": price
                })
                
            print("K11_values:", K11_values)
            print("K12_values:", K12_values)
            print("k_values:", k_values)
            
            # Збираємо параметри для профілів каркасу (K71_*)
            carcase_profiles = []
            for key, value in data.items():
                if key.startswith('K71_') and value:
                    length = key.replace('K71_', '')
                    try:
                        # Шукаємо відповідну ціну для цієї довжини
                        # Спочатку шукаємо з комою, як в оригінальному ключі
                        price_key = f'K72_{key.replace("K71_", "")}'
                        price = float(data.get(price_key, 0) or 0)
                        print(f"Профіль120 {length}м: кількість={value}, ціна_ключ={price_key}, ціна={price}")
                        carcase_profiles.append({
                            "length": float(length.replace(',', '.')), 
                            "count": int(value),
                            "price": price
                        })
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Виведемо діагностичну інформацію для профілів каркасу
            print("K71_* keys:", [key for key in data.keys() if key.startswith('K71_')])
            print("carcase_profiles:", carcase_profiles)
            print("carcase_material:", data.get('carcase_material', ''))
            print("foundation_type_1:", data.get('foundation_type_1', ''))
            
            # Збираємо динамічно додані рядки для кожної категорії
            dynamic_equipment = []
            dynamic_mounting = []
            dynamic_electrical = []
            dynamic_work = []
            dynamic_other = []  # Додаємо порожній список для dynamic_other
            
            # Обробляємо динамічні рядки для обладнання (O)
            for key in sorted([k for k in data.keys() if k.startswith('O') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка (наприклад, з O41 отримуємо 4)
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'O{row_num}1', 0) or 0)
                    unit = data.get(f'O{row_num}unit', 'шт')
                    price = float(data.get(f'O{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_equipment.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для кріплення (K)
            for key in sorted([k for k in data.keys() if k.startswith('K') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 7]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'K{row_num}1', 0) or 0)
                    unit = data.get(f'K{row_num}unit', 'шт')
                    price = float(data.get(f'K{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_mounting.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для електрики (E)
            for key in sorted([k for k in data.keys() if k.startswith('E') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 2]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'E{row_num}1', 0) or 0)
                    unit = data.get(f'E{row_num}unit', 'шт')
                    price = float(data.get(f'E{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_electrical.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для роботи (R)
            for key in sorted([k for k in data.keys() if k.startswith('R') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'R{row_num}1', 0) or 0)
                    unit = data.get(f'R{row_num}unit', 'шт')
                    price = float(data.get(f'R{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_work.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })

            # --- Normalize brand/model extraction for panel ---
            panel_brand = data.get('panel_brand', '')
            panel_model = data.get('panel_model', '')
            if panel_brand == 'other':
                panel_brand = data.get('custom_panel_brand', '')
            if panel_model == 'other':
                panel_model = data.get('custom_panel_model', '')

            # --- Normalize brand/model extraction for inverter ---
            inverter_brand = data.get('inverter_brand', '')
            inverter_model = data.get('inverter_model', '')
            if inverter_brand == 'other':
                inverter_brand = data.get('custom_inverter_brand', '')
            if inverter_model == 'other':
                inverter_model = data.get('custom_inverter_model', '')

            # --- Normalize brand/model extraction for battery ---
            battery_brand = data.get('battery_brand', '')
            battery_model = data.get('battery_model', '')
            if battery_brand == 'other':
                battery_brand = data.get('custom_battery_brand', '')
            if battery_model == 'other':
                battery_model = data.get('custom_battery_model', '')

            print(f"PDF: panel_brand={panel_brand}, panel_model={panel_model}, inverter_brand={inverter_brand}, inverter_model={inverter_model}, battery_brand={battery_brand}, battery_model={battery_model}")

            # Викликаємо функцію generate з отриманими даними
            pdf_path = generate(
                O=param_o, K=param_k, E=param_e, R=param_r,
                O11=int(data.get('O11', 0) or 0), O12=float(data.get('O12', 0) or 0.0),
                O21=int(data.get('O21', 0) or 0), O22=float(data.get('O22', 0) or 0.0),
                O31=int(data.get('O31', 0) or 0), O32=float(data.get('O32', 0) or 0.0),
                K1112=k_values,
                K21=int(data.get('K21', 0) or 0), K22=float(data.get('K22', 0) or 0.0),
                K31=int(data.get('K31', 0) or 0), K32=float(data.get('K32', 0) or 0.0),
                K41=int(data.get('K41', 0) or 0), K42=float(data.get('K42', 0) or 0.0),
                K51=int(data.get('K51', 0) or 0), K52=float(data.get('K52', 0) or 0.0),
                K71=carcase_profiles,
                K81=int(data.get('K81', 0) or 0), K82=float(data.get('K82', 0) or 0.0),
                K91=int(data.get('K91', 0) or 0), K92=float(data.get('K92', 0) or 0.0),
                K111=int(data.get('K111', 0) or 0), K121=float(data.get('K121', 0) or 0.0),
                K112=int(data.get('K112', 0) or 0), K122=float(data.get('K122', 0) or 0.0),
                K211=int(data.get('K211', 0) or 0), K221=float(data.get('K221', 0) or 0.0),
                K212=int(data.get('K212', 0) or 0), K222=float(data.get('K222', 0) or 0.0),
                K912=int(data.get('K912', 0) or 0), K922=float(data.get('K922', 0) or 0.0),
                K913=int(data.get('K913', 0) or 0), K923=float(data.get('K923', 0) or 0.0),
                E11=int(data.get('E11', 0) or 0), E12=float(data.get('E12', 0) or 0.0),
                E21=int(data.get('E21', 0) or 0), E22=float(data.get('E22', 0) or 0.0),
                R11=int(data.get('R11', 0) or 0), R12=float(data.get('R12', 0) or 0.0),
                R21=int(data.get('R21', 0) or 0), R22=float(data.get('R22', 0) or 0.0),
                R31=int(data.get('R31', 0) or 0), R32=float(data.get('R32', 0) or 0.0),
                scheme_image=normalize_path(str(data.get('scheme_image', ''))),
                dynamic_equipment=dynamic_equipment,
                dynamic_mounting=dynamic_mounting,
                dynamic_electrical=dynamic_electrical,
                dynamic_work=dynamic_work,
                dynamic_other=dynamic_other,
                usd_rate=float(data.get('usd_rate', '0').replace(',', '.') or 0.0),
                total_usd=float(data.get('total_usd', '0').replace(',', '.') or 0.0),
                screw_material=data.get('screw_material', 'оцинковані'),
                profile_material=data.get('profile_material', 'алюміній'),
                current_date=datetime.now().strftime('%d.%m.%Y'),
                show_usd=param_usd,
                panel_model_name=panel_model_name,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                panel_arrangement=panel_arrangement,
                panel_type=panel_type,
                panel_arrays=panel_arrays,
                total_panels=total_panels,
                total_rows=total_rows,
                avg_panels_per_row=avg_panels_per_row,
                panel_schemes=panel_schemes,
                carcase_material=data.get('carcase_material', ''),
                foundation_type_1=data.get('foundation_type_1', ''),
                carcase_profiles=carcase_profiles,
                include_panel_ds=include_panel_ds,
                include_inverter_ds=include_inverter_ds,
                include_battery_ds=include_battery_ds,
                panel_model_id=panel_model_id,
                inverter_model_id=inverter_model_id,
                battery_model_id=battery_model_id,
                panel_brand=panel_brand,
                panel_model=panel_model,
                inverter_brand=inverter_brand,
                inverter_model=inverter_model,
                battery_brand=battery_brand,
                battery_model=battery_model,
            )

            # Нормалізуємо шлях до PDF
            pdf_path = normalize_path(pdf_path)

            # Перевіряємо, чи існує файл
            if not os.path.exists(pdf_path):
                return JsonResponse({'success': False, 'error': f'PDF файл не знайдено за шляхом: {pdf_path}'})
            
            # Створюємо директорію для результатів, якщо вона не існує
            results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Копіюємо файл в директорію results
            filename = os.path.basename(pdf_path)
            target_path = os.path.join(results_dir, filename)
            shutil.copy2(pdf_path, target_path)
            
            # Запускаємо бота, якщо він ще не запущений
            start_bot()
            
            # Відправляємо файл через Telegram
            success = send_pdf_to_telegram(target_path)
            
            if success:
                return JsonResponse({'success': True, 'message': 'PDF звіт успішно відправлено через Telegram'})
            else:
                return JsonResponse({'success': False, 'error': 'Помилка при відправці PDF через Telegram'})
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не підтримується'})

@csrf_exempt
def send_pdf_email(request):
    """
    Ендпоінт для генерації та відправки PDF звіту на email
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не підтримується'})
    
    # Перевіряємо, чи це AJAX-запит
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if not is_ajax:
        return JsonResponse({'success': False, 'error': 'Тільки AJAX-запити підтримуються'})
    
    try:
        # Отримуємо email з запиту
        email = request.POST.get('email')
        if not email:
            return JsonResponse({'success': False, 'error': 'Email не вказано'})
        
        # Отримуємо дані з параметрів запиту
        data = request.POST.dict()
        print("Отримані дані для Email:", data)
        
        # Правильно обробляємо чекбокси
        # Якщо чекбокс відмічений, він буде присутній у request.POST зі значенням 'on'
        param_o = 'param-o' in request.POST
        param_k = 'param-k' in request.POST
        param_e = 'param-e' in request.POST
        param_r = 'param-r' in request.POST
        param_usd = 'param-usd' in request.POST
        
        print(f"Параметри для Email PDF: O={param_o}, K={param_k}, E={param_e}, R={param_r}, USD={param_usd}")
        
        # Отримуємо параметри для включення datasheet
        include_panel_ds = request.POST.get('include_panel_ds') == 'on'
        include_inverter_ds = request.POST.get('include_inverter_ds') == 'on'
        include_battery_ds = request.POST.get('include_battery_ds') == 'on'
        
        # Отримуємо дані з форми
        panel_model_name = data.get('panel_model_name', '')
        panel_length = float(data.get('panel_length', 0))
        panel_width = float(data.get('panel_width', 0))
        panel_height = float(data.get('panel_height', 0))
        panel_arrangement = data.get('panel_arrangement', '')
        panel_type = data.get('panel_type', '')
        
        # Отримуємо ідентифікатори моделей для datasheet
        panel_model_id = data.get('panelModelId', '')
        inverter_model_id = data.get('inverterModelId', '')
        battery_model_id = data.get('batteryModelId', '')
        
        # Отримуємо дані про масиви панелей
        panel_arrays = json.loads(data.get('panel_arrays', '[]'))
        total_panels = int(data.get('total_panels', 0))
        
        # Розрахунок загальної кількості рядів для відображення в PDF
        total_rows = sum(array['rows'] for array in panel_arrays)
        
        # Розрахунок середньої кількості панелей в ряді для відображення в PDF
        avg_panels_per_row = total_panels / total_rows if total_rows > 0 else 0
        
        # Отримуємо схеми для кожного масиву, якщо вони є
        panel_schemes = []
        if 'panel_schemes' in data:
            try:
                panel_schemes = json.loads(data.get('panel_schemes', '[]'))
            except json.JSONDecodeError:
                print("Помилка декодування panel_schemes з JSON")
        
        # Створюємо списки для K11 і K12
        K11_values = []
        K12_values = {}
        
        # Збираємо всі наявні параметри K11_{length} та K12_{length}
        for key, value in data.items():
            if key.startswith('K11_') and value:
                length = key.replace('K11_', '')
                try:
                    # Замінюємо кому на крапку перед перетворенням
                    length = length.replace(',', '.')
                    length_float = float(length)
                    count = int(value)
                    K11_values.append({"length": length_float, "count": count})
                except (ValueError, TypeError):
                    print(f"Помилка при обробці {key}: {value}")
                    
            elif key.startswith('K12_') and value:
                length = key.replace('K12_', '')
                try:
                    # Замінюємо кому на крапку перед перетворенням
                    length = length.replace(',', '.')
                    length_float = float(length)
                    price = float(value)
                    K12_values[length_float] = price
                except (ValueError, TypeError):
                    print(f"Помилка при обробці {key}: {value}")
        
        # Збираємо динамічні рядки для кріплень (K10n, K11n, K12n, K13n для n=0,1,2,...)
        dynamic_mounting = []
        
        # Перебираємо всі ключі, які починаються з K10, K11, K12, K13 і мають довжину 4 символи (для нового формату)
        for key, value in data.items():
            if (key.startswith('K10') or key.startswith('K11') or key.startswith('K12') or key.startswith('K13')) and len(key) == 4 and value:
                # Отримуємо індекс рядка (останній символ)
                row_index = key[3]
                
                # Перевіряємо, чи це назва елемента (K10n)
                if key.startswith('K10'):
                    name = value
                    # Шукаємо відповідні кількість, ціну та суму
                    quantity_key = f'K11{row_index}'
                    price_key = f'K12{row_index}'
                    
                    quantity = int(data.get(quantity_key, 0) or 0)
                    price = float(data.get(price_key, 0) or 0.0)
                    
                    # Додаємо до списку динамічних рядків
                    if name and quantity > 0:
                        dynamic_mounting.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': 'шт',
                            'price': price
                        })
                        print(f"Додано динамічний рядок: назва={name}, кількість={quantity}, ціна={price}")
        
        # Виведемо діагностичну інформацію
        print("K11_values keys:", [key for key in data.keys() if key.startswith('K11_')])
        
        # Створюємо масив словників для профілів
        k_values = []
        for item in K11_values:
            length = item["length"]
            count = item["count"]
            # Шукаємо відповідну ціну для цієї довжини
            price = K12_values.get(length, 0)
            
            k_values.append({
                "length": length, 
                "count": count,
                "price": price
            })
            
        print("K11_values:", K11_values)
        print("K12_values:", K12_values)
        print("k_values:", k_values)
        
        # Збираємо параметри для профілів каркасу (K71_*)
        carcase_profiles = []
        for key, value in data.items():
            if key.startswith('K71_') and value:
                length = key.replace('K71_', '')
                try:
                    # Шукаємо відповідну ціну для цієї довжини
                    # Спочатку шукаємо з комою, як в оригінальному ключі
                    price_key = f'K72_{key.replace("K71_", "")}'
                    price = float(data.get(price_key, 0) or 0)
                    print(f"Профіль120 {length}м: кількість={value}, ціна_ключ={price_key}, ціна={price}")
                    carcase_profiles.append({
                        "length": float(length.replace(',', '.')), 
                        "count": int(value),
                        "price": price
                    })
                except (ValueError, TypeError):
                    print(f"Помилка при обробці {key}: {value}")
        
        # Виведемо діагностичну інформацію для профілів каркасу
        print("K71_* keys:", [key for key in data.keys() if key.startswith('K71_')])
        print("carcase_profiles:", carcase_profiles)
        print("carcase_material:", data.get('carcase_material', ''))
        print("foundation_type_1:", data.get('foundation_type_1', ''))
        
        # Збираємо динамічно додані рядки для кожної категорії
        dynamic_equipment = []
        dynamic_mounting = []
        dynamic_electrical = []
        dynamic_work = []
        dynamic_other = []  # Додаємо порожній список для dynamic_other
        
        # Обробляємо динамічні рядки для обладнання (O)
        for key in sorted([k for k in data.keys() if k.startswith('O') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
            row_num = key[1:-1]  # Отримуємо номер рядка (наприклад, з O41 отримуємо 4)
            if key.endswith('0'):  # Поле назви
                name = data.get(key, '')
                quantity = int(data.get(f'O{row_num}1', 0) or 0)
                unit = data.get(f'O{row_num}unit', 'шт')
                price = float(data.get(f'O{row_num}2', 0) or 0.0)
                
                if name and quantity > 0:
                    dynamic_equipment.append({
                        'name': name,
                        'quantity': quantity,
                        'unit': unit,
                        'price': price
                    })
        
        # Обробляємо динамічні рядки для кріплення (K)
        for key in sorted([k for k in data.keys() if k.startswith('K') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 7]):
            row_num = key[1:-1]  # Отримуємо номер рядка
            if key.endswith('0'):  # Поле назви
                name = data.get(key, '')
                quantity = int(data.get(f'K{row_num}1', 0) or 0)
                unit = data.get(f'K{row_num}unit', 'шт')
                price = float(data.get(f'K{row_num}2', 0) or 0.0)
                
                if name and quantity > 0:
                    dynamic_mounting.append({
                        'name': name,
                        'quantity': quantity,
                        'unit': unit,
                        'price': price
                    })
        
        # Обробляємо динамічні рядки для електрики (E)
        for key in sorted([k for k in data.keys() if k.startswith('E') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 2]):
            row_num = key[1:-1]  # Отримуємо номер рядка
            if key.endswith('0'):  # Поле назви
                name = data.get(key, '')
                quantity = int(data.get(f'E{row_num}1', 0) or 0)
                unit = data.get(f'E{row_num}unit', 'шт')
                price = float(data.get(f'E{row_num}2', 0) or 0.0)
                
                if name and quantity > 0:
                    dynamic_electrical.append({
                        'name': name,
                        'quantity': quantity,
                        'unit': unit,
                        'price': price
                    })
        
        # Обробляємо динамічні рядки для роботи (R)
        for key in sorted([k for k in data.keys() if k.startswith('R') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
            row_num = key[1:-1]  # Отримуємо номер рядка
            if key.endswith('0'):  # Поле назви
                name = data.get(key, '')
                quantity = int(data.get(f'R{row_num}1', 0) or 0)
                unit = data.get(f'R{row_num}unit', 'шт')
                price = float(data.get(f'R{row_num}2', 0) or 0.0)
                
                if name and quantity > 0:
                    dynamic_work.append({
                        'name': name,
                        'quantity': quantity,
                        'unit': unit,
                        'price': price
                    })

            # --- Normalize brand/model extraction for panel ---
            panel_brand = data.get('panel_brand', '')
            panel_model = data.get('panel_model', '')
            if panel_brand == 'other':
                panel_brand = data.get('custom_panel_brand', '')
            if panel_model == 'other':
                panel_model = data.get('custom_panel_model', '')

            # --- Normalize brand/model extraction for inverter ---
            inverter_brand = data.get('inverter_brand', '')
            inverter_model = data.get('inverter_model', '')
            if inverter_brand == 'other':
                inverter_brand = data.get('custom_inverter_brand', '')
            if inverter_model == 'other':
                inverter_model = data.get('custom_inverter_model', '')

            # --- Normalize brand/model extraction for battery ---
            battery_brand = data.get('battery_brand', '')
            battery_model = data.get('battery_model', '')
            if battery_brand == 'other':
                battery_brand = data.get('custom_battery_brand', '')
            if battery_model == 'other':
                battery_model = data.get('custom_battery_model', '')

            print(f"PDF: panel_brand={panel_brand}, panel_model={panel_model}, inverter_brand={inverter_brand}, inverter_model={inverter_model}, battery_brand={battery_brand}, battery_model={battery_model}")

            # Викликаємо функцію generate з отриманими даними
            pdf_path = generate(
                O=param_o, K=param_k, E=param_e, R=param_r,
                O11=int(data.get('O11', 0) or 0), O12=float(data.get('O12', 0) or 0.0),
                O21=int(data.get('O21', 0) or 0), O22=float(data.get('O22', 0) or 0.0),
                O31=int(data.get('O31', 0) or 0), O32=float(data.get('O32', 0) or 0.0),
                K1112=k_values,
                K21=int(data.get('K21', 0) or 0), K22=float(data.get('K22', 0) or 0.0),
                K31=int(data.get('K31', 0) or 0), K32=float(data.get('K32', 0) or 0.0),
                K41=int(data.get('K41', 0) or 0), K42=float(data.get('K42', 0) or 0.0),
                K51=int(data.get('K51', 0) or 0), K52=float(data.get('K52', 0) or 0.0),
                K71=carcase_profiles,
                K81=int(data.get('K81', 0) or 0), K82=float(data.get('K82', 0) or 0.0),
                K91=int(data.get('K91', 0) or 0), K92=float(data.get('K92', 0) or 0.0),
                K111=int(data.get('K111', 0) or 0), K121=float(data.get('K121', 0) or 0.0),
                K112=int(data.get('K112', 0) or 0), K122=float(data.get('K122', 0) or 0.0),
                K211=int(data.get('K211', 0) or 0), K221=float(data.get('K221', 0) or 0.0),
                K212=int(data.get('K212', 0) or 0), K222=float(data.get('K222', 0) or 0.0),
                K912=int(data.get('K912', 0) or 0), K922=float(data.get('K922', 0) or 0.0),
                K913=int(data.get('K913', 0) or 0), K923=float(data.get('K923', 0) or 0.0),
                E11=int(data.get('E11', 0) or 0), E12=float(data.get('E12', 0) or 0.0),
                E21=int(data.get('E21', 0) or 0), E22=float(data.get('E22', 0) or 0.0),
                R11=int(data.get('R11', 0) or 0), R12=float(data.get('R12', 0) or 0.0),
                R21=int(data.get('R21', 0) or 0), R22=float(data.get('R22', 0) or 0.0),
                R31=int(data.get('R31', 0) or 0), R32=float(data.get('R32', 0) or 0.0),
                scheme_image=normalize_path(str(data.get('scheme_image', ''))),
                dynamic_equipment=dynamic_equipment,
                dynamic_mounting=dynamic_mounting,
                dynamic_electrical=dynamic_electrical,
                dynamic_work=dynamic_work,
                dynamic_other=dynamic_other,
                usd_rate=float(data.get('usd_rate', '0').replace(',', '.') or 0.0),
                total_usd=float(data.get('total_usd', '0').replace(',', '.') or 0.0),
                screw_material=data.get('screw_material', 'оцинковані'),
                profile_material=data.get('profile_material', 'алюміній'),
                current_date=datetime.now().strftime('%d.%m.%Y'),
                show_usd=param_usd,
                panel_model_name=panel_model_name,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                panel_arrangement=panel_arrangement,
                panel_type=panel_type,
                panel_arrays=panel_arrays,
                total_panels=total_panels,
                total_rows=total_rows,
                avg_panels_per_row=avg_panels_per_row,
                panel_schemes=panel_schemes,
                carcase_material=data.get('carcase_material', ''),
                foundation_type_1=data.get('foundation_type_1', ''),
                carcase_profiles=carcase_profiles,
                include_panel_ds=include_panel_ds,
                include_inverter_ds=include_inverter_ds,
                include_battery_ds=include_battery_ds,
                panel_model_id=panel_model_id,
                inverter_model_id=inverter_model_id,
                battery_model_id=battery_model_id,
                panel_brand=panel_brand,
                panel_model=panel_model,
                inverter_brand=inverter_brand,
                inverter_model=inverter_model,
                battery_brand=battery_brand,
                battery_model=battery_model,
            )

            # Нормалізуємо шлях до PDF
            pdf_path = normalize_path(pdf_path)

            # Відправляємо PDF на email
            if send_pdf_to_email(pdf_path, email):
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Помилка при відправці PDF на email'})
    
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

def send_pdf_to_email(pdf_path, recipient_email):
    """
    Відправляє PDF звіт на вказаний email
    
    Args:
        pdf_path (str): Шлях до PDF файлу
        recipient_email (str): Email отримувача
    
    Returns:
        bool: True, якщо відправка успішна, False в іншому випадку
    """
    try:
        # Перевірка налаштувань
        sender_email = settings.EMAIL_USER
        print(f"Відправка email з {sender_email} на {recipient_email}")
        
        # Перевіряємо, чи існує файл
        if not os.path.exists(pdf_path):
            print(f"PDF файл не знайдено: {pdf_path}")
            return False
            
        # Використовуємо Django EmailMessage для відправки
        from django.core.mail import EmailMessage
        from email.mime.application import MIMEApplication
        
        # Створюємо об'єкт повідомлення
        subject = "Звіт про сонячну електростанцію"
        body = """
        Доброго дня!
        
        Ось ваш звіт про сонячну електростанцію.
        
        З повагою,
        SolarCalc
        """
        
        # Створюємо і відправляємо email
        print("Створення об'єкту EmailMessage...")
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender_email,
            to=[recipient_email],
        )
        
        # Додаємо PDF як вкладення
        print(f"Додавання вкладення: {pdf_path}")
        
        # Створюємо копію PDF файлу з новим ім'ям
        new_pdf_path = pdf_path.replace('.pdf', '_email.pdf')
        shutil.copy2(pdf_path, new_pdf_path)
        print(f"Створено копію PDF для email: {new_pdf_path}")
        
        # Додаємо PDF як вкладення з явними заголовками
        with open(new_pdf_path, 'rb') as f:
            pdf_content = f.read()
            # Використовуємо MIMEApplication для кращої сумісності з поштовими клієнтами
            pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=os.path.basename(new_pdf_path))
            email.attach(pdf_attachment)
        
        # Відправляємо email
        print("Відправка email...")
        email.send(fail_silently=False)
        print(f"Email успішно відправлено на {recipient_email}")
        
        # Видаляємо тимчасовий файл
        if os.path.exists(new_pdf_path):
            os.remove(new_pdf_path)
            print(f"Видалено тимчасовий файл: {new_pdf_path}")
            
        return True
    
    except Exception as e:
        print(f"Помилка при відправці PDF на email: {e}")
        print(f"Детальна інформація про помилку: {traceback.format_exc()}")
        return False

@ensure_csrf_cookie
def create_panel(request):
    """
    Ендпоінт для створення нової панелі з можливістю завантаження datasheet.
    """
    context = {}
    
    if request.method == 'POST':
        try:
            # Отримання даних
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            panel_length = float(request.POST.get('panel_length'))
            panel_width = float(request.POST.get('panel_width'))
            panel_height = float(request.POST.get('panel_height'))
            panel_type = request.POST.get('panel_type')
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_panel.html', context)
            
            # Створення нової панелі
            panel = Panels(
                brand=brand,
                model=model,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                panel_type=panel_type
            )
            panel.save()
            
            # Завантаження файлу через метод upload_datasheet
            datasheet_file = request.FILES['datasheet']
            panel.upload_datasheet(datasheet_file)
            
            # Передаємо дані про успішне створення в контекст
            context['success'] = True
            context['panel'] = panel
            
            return render(request, 'create_panel.html', context)
            
        except Exception as e:
            print(traceback.format_exc())
            context['error'] = str(e)
            return render(request, 'create_panel.html', context)
    
    return render(request, 'create_panel.html', context)

@ensure_csrf_cookie
def create_inverter(request):
    """
    Ендпоінт для створення нового інвертора з можливістю завантаження datasheet.
    """
    context = {}
    
    if request.method == 'POST':
        try:
            # Отримання даних
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            power = float(request.POST.get('power'))
            phases_count = int(request.POST.get('phases_count'))
            voltage_type = request.POST.get('voltage', '')
            strings_count = request.POST.get('strings_count')
            
            # Створення нового інвертора
            inverter = Inverters(
                brand=brand,
                model=model,
                power=power,
                phases_count=phases_count,
                voltage_type=voltage_type,
                strings_count=strings_count if strings_count else None,
            )
            inverter.save()
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_inverter.html', context)
            
            # Завантаження файлу через метод upload_datasheet
            datasheet_file = request.FILES['datasheet']
            inverter.upload_datasheet(datasheet_file)
            
            # Передаємо дані про успішне створення в контекст
            context['success'] = True
            context['inverter'] = inverter
            
            return render(request, 'create_inverter.html', context)
            
        except Exception as e:
            print(traceback.format_exc())
            context['error'] = str(e)
            return render(request, 'create_inverter.html', context)
    
    return render(request, 'create_inverter.html', context)

@ensure_csrf_cookie
def create_battery(request):
    """
    Ендпоінт для створення нової батареї з можливістю завантаження datasheet.
    """
    context = {}
    
    if request.method == 'POST':
        try:
            # Отримання даних
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            capacity = float(request.POST.get('capacity'))
            is_head = 'is_head' in request.POST
            is_stand = False
            voltage_type = request.POST.get('voltage')
            
            # Створення нової батареї
            battery = Batteries(
                brand=brand,
                model=model,
                capacity=capacity,
                is_head=is_head,
                is_stand=is_stand,
                voltage_type=voltage_type
            )
            battery.save()
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_battery.html', context)
            
            # Завантаження файлу через метод upload_datasheet
            datasheet_file = request.FILES['datasheet']
            battery.upload_datasheet(datasheet_file)
            
            # Передаємо дані про успішне створення в контекст
            context['success'] = True
            context['battery'] = battery
            
            return render(request, 'create_battery.html', context)
            
        except Exception as e:
            print(traceback.format_exc())
            context['error'] = str(e)
            return render(request, 'create_battery.html', context)
    
    return render(request, 'create_battery.html', context)

@csrf_exempt
def send_pdf_telegram(request):
    """
    Ендпоінт для генерації та відправки PDF звіту через Telegram
    """
    if request.method == 'POST':
        try:
            # Отримуємо дані з параметрів запиту
            data = request.POST.dict()
            print("Отримані дані для Telegram:", data)
            
            # Правильно обробляємо чекбокси
            # Якщо чекбокс відмічений, він буде присутній у request.POST зі значенням 'on'
            param_o = 'param-o' in request.POST
            param_k = 'param-k' in request.POST
            param_e = 'param-e' in request.POST
            param_r = 'param-r' in request.POST
            param_usd = 'param-usd' in request.POST
            
            print(f"Параметри для Telegram PDF: O={param_o}, K={param_k}, E={param_e}, R={param_r}, USD={param_usd}")
            
            # Отримуємо параметри для включення datasheet
            include_panel_ds = request.POST.get('include_panel_ds') == 'on'
            include_inverter_ds = request.POST.get('include_inverter_ds') == 'on'
            include_battery_ds = request.POST.get('include_battery_ds') == 'on'
            
            # Отримуємо дані з форми
            panel_model_name = data.get('panel_model_name', '')
            panel_length = float(data.get('panel_length', 0))
            panel_width = float(data.get('panel_width', 0))
            panel_height = float(data.get('panel_height', 0))
            panel_arrangement = data.get('panel_arrangement', '')
            panel_type = data.get('panel_type', '')
            
            # Отримуємо ідентифікатори моделей для datasheet
            panel_model_id = data.get('panelModelId', '')
            inverter_model_id = data.get('inverterModelId', '')
            battery_model_id = data.get('batteryModelId', '')
            
            # Отримуємо дані про масиви панелей
            panel_arrays = json.loads(data.get('panel_arrays', '[]'))
            total_panels = int(data.get('total_panels', 0))
            
            # Розрахунок загальної кількості рядів для відображення в PDF
            total_rows = sum(array['rows'] for array in panel_arrays)
            
            # Розрахунок середньої кількості панелей в ряді для відображення в PDF
            avg_panels_per_row = total_panels / total_rows if total_rows > 0 else 0
            
            # Отримуємо схеми для кожного масиву, якщо вони є
            panel_schemes = []
            if 'panel_schemes' in data:
                try:
                    panel_schemes = json.loads(data.get('panel_schemes', '[]'))
                except json.JSONDecodeError:
                    print("Помилка декодування panel_schemes з JSON")
            
            # Створюємо списки для K11 і K12
            K11_values = []
            K12_values = {}
            
            # Збираємо всі наявні параметри K11_{length} та K12_{length}
            for key, value in data.items():
                if key.startswith('K11_') and value:
                    length = key.replace('K11_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        count = int(value)
                        K11_values.append({"length": length_float, "count": count})
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
                        
                elif key.startswith('K12_') and value:
                    length = key.replace('K12_', '')
                    try:
                        # Замінюємо кому на крапку перед перетворенням
                        length = length.replace(',', '.')
                        length_float = float(length)
                        price = float(value)
                        K12_values[length_float] = price
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Збираємо динамічні рядки для кріплень (K10n, K11n, K12n, K13n для n=0,1,2,...)
            dynamic_mounting = []
            
            # Перебираємо всі ключі, які починаються з K10, K11, K12, K13 і мають довжину 4 символи (для нового формату)
            for key, value in data.items():
                if (key.startswith('K10') or key.startswith('K11') or key.startswith('K12') or key.startswith('K13')) and len(key) == 4 and value:
                    # Отримуємо індекс рядка (останній символ)
                    row_index = key[3]
                    
                    # Перевіряємо, чи це назва елемента (K10n)
                    if key.startswith('K10'):
                        name = value
                        # Шукаємо відповідні кількість, ціну та суму
                        quantity_key = f'K11{row_index}'
                        price_key = f'K12{row_index}'
                        
                        quantity = int(data.get(quantity_key, 0) or 0)
                        price = float(data.get(price_key, 0) or 0.0)
                        
                        # Додаємо до списку динамічних рядків
                        if name and quantity > 0:
                            dynamic_mounting.append({
                                'name': name,
                                'quantity': quantity,
                                'unit': 'шт',
                                'price': price
                            })
                            print(f"Додано динамічний рядок: назва={name}, кількість={quantity}, ціна={price}")
            
            # Виведемо діагностичну інформацію
            print("K11_values keys:", [key for key in data.keys() if key.startswith('K11_')])
            
            # Створюємо масив словників для профілів
            k_values = []
            for item in K11_values:
                length = item["length"]
                count = item["count"]
                # Шукаємо відповідну ціну для цієї довжини
                price = K12_values.get(length, 0)
                
                k_values.append({
                    "length": length, 
                    "count": count,
                    "price": price
                })
                
            print("K11_values:", K11_values)
            print("K12_values:", K12_values)
            print("k_values:", k_values)
            
            # Збираємо параметри для профілів каркасу (K71_*)
            carcase_profiles = []
            for key, value in data.items():
                if key.startswith('K71_') and value:
                    length = key.replace('K71_', '')
                    try:
                        # Шукаємо відповідну ціну для цієї довжини
                        # Спочатку шукаємо з комою, як в оригінальному ключі
                        price_key = f'K72_{key.replace("K71_", "")}'
                        price = float(data.get(price_key, 0) or 0)
                        print(f"Профіль120 {length}м: кількість={value}, ціна_ключ={price_key}, ціна={price}")
                        carcase_profiles.append({
                            "length": float(length.replace(',', '.')), 
                            "count": int(value),
                            "price": price
                        })
                    except (ValueError, TypeError):
                        print(f"Помилка при обробці {key}: {value}")
            
            # Виведемо діагностичну інформацію для профілів каркасу
            print("K71_* keys:", [key for key in data.keys() if key.startswith('K71_')])
            print("carcase_profiles:", carcase_profiles)
            print("carcase_material:", data.get('carcase_material', ''))
            print("foundation_type_1:", data.get('foundation_type_1', ''))
            
            # Збираємо динамічно додані рядки для кожної категорії
            dynamic_equipment = []
            dynamic_mounting = []
            dynamic_electrical = []
            dynamic_work = []
            dynamic_other = []  # Додаємо порожній список для dynamic_other
            
            # Обробляємо динамічні рядки для обладнання (O)
            for key in sorted([k for k in data.keys() if k.startswith('O') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка (наприклад, з O41 отримуємо 4)
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'O{row_num}1', 0) or 0)
                    unit = data.get(f'O{row_num}unit', 'шт')
                    price = float(data.get(f'O{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_equipment.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для кріплення (K)
            for key in sorted([k for k in data.keys() if k.startswith('K') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 7]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'K{row_num}1', 0) or 0)
                    unit = data.get(f'K{row_num}unit', 'шт')
                    price = float(data.get(f'K{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_mounting.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для електрики (E)
            for key in sorted([k for k in data.keys() if k.startswith('E') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 2]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'E{row_num}1', 0) or 0)
                    unit = data.get(f'E{row_num}unit', 'шт')
                    price = float(data.get(f'E{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_electrical.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })
            
            # Обробляємо динамічні рядки для роботи (R)
            for key in sorted([k for k in data.keys() if k.startswith('R') and len(k) >= 3 and k[1:].isdigit() and int(k[1:]) > 3]):
                row_num = key[1:-1]  # Отримуємо номер рядка
                if key.endswith('0'):  # Поле назви
                    name = data.get(key, '')
                    quantity = int(data.get(f'R{row_num}1', 0) or 0)
                    unit = data.get(f'R{row_num}unit', 'шт')
                    price = float(data.get(f'R{row_num}2', 0) or 0.0)
                    
                    if name and quantity > 0:
                        dynamic_work.append({
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'price': price
                        })

            # --- Normalize brand/model extraction for panel ---
            panel_brand = data.get('panel_brand', '')
            panel_model = data.get('panel_model', '')
            if panel_brand == 'other':
                panel_brand = data.get('custom_panel_brand', '')
            if panel_model == 'other':
                panel_model = data.get('custom_panel_model', '')

            # --- Normalize brand/model extraction for inverter ---
            inverter_brand = data.get('inverter_brand', '')
            inverter_model = data.get('inverter_model', '')
            if inverter_brand == 'other':
                inverter_brand = data.get('custom_inverter_brand', '')
            if inverter_model == 'other':
                inverter_model = data.get('custom_inverter_model', '')

            # --- Normalize brand/model extraction for battery ---
            battery_brand = data.get('battery_brand', '')
            battery_model = data.get('battery_model', '')
            if battery_brand == 'other':
                battery_brand = data.get('custom_battery_brand', '')
            if battery_model == 'other':
                battery_model = data.get('custom_battery_model', '')

            print(f"PDF: panel_brand={panel_brand}, panel_model={panel_model}, inverter_brand={inverter_brand}, inverter_model={inverter_model}, battery_brand={battery_brand}, battery_model={battery_model}")

            # Викликаємо функцію generate з отриманими даними
            pdf_path = generate(
                O=param_o, K=param_k, E=param_e, R=param_r,
                O11=int(data.get('O11', 0) or 0), O12=float(data.get('O12', 0) or 0.0),
                O21=int(data.get('O21', 0) or 0), O22=float(data.get('O22', 0) or 0.0),
                O31=int(data.get('O31', 0) or 0), O32=float(data.get('O32', 0) or 0.0),
                K1112=k_values,
                K21=int(data.get('K21', 0) or 0), K22=float(data.get('K22', 0) or 0.0),
                K31=int(data.get('K31', 0) or 0), K32=float(data.get('K32', 0) or 0.0),
                K41=int(data.get('K41', 0) or 0), K42=float(data.get('K42', 0) or 0.0),
                K51=int(data.get('K51', 0) or 0), K52=float(data.get('K52', 0) or 0.0),
                K71=carcase_profiles,
                K81=int(data.get('K81', 0) or 0), K82=float(data.get('K82', 0) or 0.0),
                K91=int(data.get('K91', 0) or 0), K92=float(data.get('K92', 0) or 0.0),
                K111=int(data.get('K111', 0) or 0), K121=float(data.get('K121', 0) or 0.0),
                K112=int(data.get('K112', 0) or 0), K122=float(data.get('K122', 0) or 0.0),
                K211=int(data.get('K211', 0) or 0), K221=float(data.get('K221', 0) or 0.0),
                K212=int(data.get('K212', 0) or 0), K222=float(data.get('K222', 0) or 0.0),
                K912=int(data.get('K912', 0) or 0), K922=float(data.get('K922', 0) or 0.0),
                K913=int(data.get('K913', 0) or 0), K923=float(data.get('K923', 0) or 0.0),
                E11=int(data.get('E11', 0) or 0), E12=float(data.get('E12', 0) or 0.0),
                E21=int(data.get('E21', 0) or 0), E22=float(data.get('E22', 0) or 0.0),
                R11=int(data.get('R11', 0) or 0), R12=float(data.get('R12', 0) or 0.0),
                R21=int(data.get('R21', 0) or 0), R22=float(data.get('R22', 0) or 0.0),
                R31=int(data.get('R31', 0) or 0), R32=float(data.get('R32', 0) or 0.0),
                scheme_image=normalize_path(str(data.get('scheme_image', ''))),
                dynamic_equipment=dynamic_equipment,
                dynamic_mounting=dynamic_mounting,
                dynamic_electrical=dynamic_electrical,
                dynamic_work=dynamic_work,
                dynamic_other=dynamic_other,
                usd_rate=float(data.get('usd_rate', '0').replace(',', '.') or 0.0),
                total_usd=float(data.get('total_usd', '0').replace(',', '.') or 0.0),
                screw_material=data.get('screw_material', 'оцинковані'),
                profile_material=data.get('profile_material', 'алюміній'),
                current_date=datetime.now().strftime('%d.%m.%Y'),
                show_usd=param_usd,
                panel_model_name=panel_model_name,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                panel_arrangement=panel_arrangement,
                panel_type=panel_type,
                panel_arrays=panel_arrays,
                total_panels=total_panels,
                total_rows=total_rows,
                avg_panels_per_row=avg_panels_per_row,
                panel_schemes=panel_schemes,
                carcase_material=data.get('carcase_material', ''),
                foundation_type_1=data.get('foundation_type_1', ''),
                carcase_profiles=carcase_profiles,
                include_panel_ds=include_panel_ds,
                include_inverter_ds=include_inverter_ds,
                include_battery_ds=include_battery_ds,
                panel_model_id=panel_model_id,
                inverter_model_id=inverter_model_id,
                battery_model_id=battery_model_id,
                panel_brand=panel_brand,
                panel_model=panel_model,
                inverter_brand=inverter_brand,
                inverter_model=inverter_model,
                battery_brand=battery_brand,
                battery_model=battery_model,
            )

            # Нормалізуємо шлях до PDF
            pdf_path = normalize_path(pdf_path)

            # Перевіряємо, чи існує файл
            if not os.path.exists(pdf_path):
                return JsonResponse({'success': False, 'error': f'PDF файл не знайдено за шляхом: {pdf_path}'})
            
            # Створюємо директорію для результатів, якщо вона не існує
            results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            # Копіюємо файл в директорію results
            filename = os.path.basename(pdf_path)
            target_path = os.path.join(results_dir, filename)
            shutil.copy2(pdf_path, target_path)
            
            # Запускаємо бота, якщо він ще не запущений
            start_bot()
            
            # Відправляємо файл через Telegram
            success = send_pdf_to_telegram(target_path)
            
            if success:
                return JsonResponse({'success': True, 'message': 'PDF звіт успішно відправлено через Telegram'})
            else:
                return JsonResponse({'success': False, 'error': 'Помилка при відправці PDF через Telegram'})
            
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Метод не підтримується'})

def download_datasheet(request, panel_id):
    """
    Завантажує datasheet для вибраної моделі панелі.
    """
    try:
        # Отримуємо панель за id
        panel = Panels.objects.get(id=panel_id)
        
        # Перевіряємо, чи є URL файлу
        if not panel.datasheet_url:
            return HttpResponse("Файл не знайдено", status=404)
            
        # Отримуємо URL файлу
        file_url = panel.datasheet_url
        
        # Відкриваємо URL через requests
        response = requests.get(file_url)
        if response.status_code == 200:
            # Створюємо відповідь з файлом
            content_type = 'application/pdf'  # За замовчуванням PDF
            if file_url.lower().endswith('.jpg') or file_url.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_url.lower().endswith('.png'):
                content_type = 'image/png'
            
            django_response = HttpResponse(response.content, content_type=content_type)
            django_response['Content-Disposition'] = f'attachment; filename="{panel.datasheet_name}"'
            return django_response
        else:
            return HttpResponse("Не вдалося завантажити файл", status=404)
    
    except Panels.DoesNotExist:
        # Якщо панель не знайдена, повертаємо помилку 404
        return HttpResponse("Панель не знайдена", status=404)
    except Exception as e:
        # Якщо сталася інша помилка, повертаємо помилку 500
        return HttpResponse(f"Помилка: {str(e)}", status=500)

def download_inverter_datasheet(request, inverter_id):
    """
    Завантажує datasheet для вибраного інвертора.
    """
    try:
        # Отримуємо інвертор за id
        inverter = Inverters.objects.get(id=inverter_id)
        
        # Перевіряємо, чи є URL файлу
        if not inverter.datasheet_url:
            return HttpResponse("Файл не знайдено", status=404)
            
        # Отримуємо URL файлу
        file_url = inverter.datasheet_url
        
        # Відкриваємо URL через requests
        response = requests.get(file_url)
        if response.status_code == 200:
            # Створюємо відповідь з файлом
            content_type = 'application/pdf'  # За замовчуванням PDF
            if file_url.lower().endswith('.jpg') or file_url.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_url.lower().endswith('.png'):
                content_type = 'image/png'
            
            django_response = HttpResponse(response.content, content_type=content_type)
            django_response['Content-Disposition'] = f'attachment; filename="{inverter.datasheet_name}"'
            return django_response
        else:
            return HttpResponse("Не вдалося завантажити файл", status=404)
    
    except Inverters.DoesNotExist:
        # Якщо інвертор не знайдений, повертаємо помилку 404
        return HttpResponse("Інвертор не знайдено", status=404)
    except Exception as e:
        # Якщо сталася інша помилка, повертаємо помилку 500
        return HttpResponse(f"Помилка: {str(e)}", status=500)

def download_battery_datasheet(request, battery_id):
    """
    Завантажує datasheet для вибраної батареї.
    """
    try:
        # Отримуємо батарею за id
        battery = Batteries.objects.get(id=battery_id)
        
        # Перевіряємо, чи є URL файлу
        if not battery.datasheet_url:
            return HttpResponse("Файл не знайдено", status=404)
            
        # Отримуємо URL файлу
        file_url = battery.datasheet_url
        
        # Відкриваємо URL через requests
        response = requests.get(file_url)
        if response.status_code == 200:
            # Створюємо відповідь з файлом
            content_type = 'application/pdf'  # За замовчуванням PDF
            if file_url.lower().endswith('.jpg') or file_url.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_url.lower().endswith('.png'):
                content_type = 'image/png'
            
            django_response = HttpResponse(response.content, content_type=content_type)
            django_response['Content-Disposition'] = f'attachment; filename="{battery.datasheet_name}"'
            return django_response
        else:
            return HttpResponse("Не вдалося завантажити файл", status=404)
    
    except Batteries.DoesNotExist:
        # Якщо батарея не знайдена, повертаємо помилку 404
        return HttpResponse("Батарею не знайдено", status=404)
    except Exception as e:
        # Якщо сталася інша помилка, повертаємо помилку 500
        return HttpResponse(f"Помилка: {str(e)}", status=500)
