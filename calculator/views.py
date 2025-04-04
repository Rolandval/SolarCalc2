from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import traceback
from django.http import HttpResponse
from pdf_result import generate
from django import template
import math
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
from panel_scheme import generate_panel_scheme, save_panel_scheme
import os
from .models import Panels, Inverters, Batteries
import uuid
import requests
from datetime import datetime
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
            'height': float(panel.panel_height)
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
            'phases_count': inverter.phases_count
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
            'is_stand': battery.is_stand
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
                except Panels.DoesNotExist:
                    # Якщо панель не знайдена, використовуємо значення з форми
                    panel_length = float(data.get('panel_length', 0))
                    panel_width = float(data.get('panel_width', 0))
                    panel_height = float(data.get('panel_height', 0))
                    panel_model_name = data.get('custom_panel_model', '')  # Використовуємо введену назву
            else:
                # Якщо id моделі не вказано, використовуємо значення з форми
                panel_length = float(data.get('panel_length', 0))
                panel_width = float(data.get('panel_width', 0))
                panel_height = float(data.get('panel_height', 0))
                panel_model_name = data.get('custom_panel_model', '')  # Використовуємо введену назву

            panels_per_row = int(data.get('panels_per_row', 0))
            rows = int(data.get('rows', 0))
            total_panels = int(data.get('total_panels', 0))
            if total_panels != rows * panels_per_row:
                return JsonResponse({'success': False, 'error': 'Кількість рядів та кількість панелей в ряді не співпадають'})
            
            panel_arrangement = data.get('panel_arrangement', '')
            if panel_arrangement == '':
                return JsonResponse({'success': False, 'error': 'Необхідно вибрати розташування профілів'})
            panel_type = data.get('panel_type', '')
            if panel_type == '':
                return JsonResponse({'success': False, 'error': 'Необхідно вибрати тип панелі'})
            available_lengths = [float(x.strip()) for x in data['profile_lengths'].split(',')]
            strings = int(data.get('strings', 0))

            profil_len = 0
            if panel_arrangement == 'альбомна':
                profil_len = ((panel_length * panels_per_row) + (0.002*(panels_per_row - 1)) + 0.01) * rows
            elif panel_arrangement == 'портретна':
                profil_len = ((panel_width * panels_per_row) + (0.002*(panels_per_row - 1)) + 0.01) * rows
            sorted_arr = sorted(available_lengths, reverse=True)
            profiles = []
            remaining_length = profil_len
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

            g_clamps = 4 * rows
            v_clamps = (total_panels * 2) - 2
            m_sh = math.ceil(profil_len / 0.9)
            front_connectors = (panels_per_row - 1) * rows

            connectors = 0

            if panel_type == 'альбомна':
                connectors = (strings * 2) + 1
            elif panel_type == 'портретна':
                connectors = ((strings * 2) + 1) + rows

            # Генеруємо схему
            scheme_image = generate_panel_scheme(
                panel_length, panel_width, panel_height,
                rows, panels_per_row,
                panel_arrangement, available_lengths
            )
            
            # Зберігаємо зображення схеми для використання в PDF
            scheme_file_path = save_panel_scheme(
                panel_length, panel_width, panel_height,
                rows, panels_per_row,
                panel_arrangement, available_lengths
            )
            
            # Конвертуємо зображення в base64 для вбудовування в HTML
            buffer = BytesIO()
            scheme_image.save(buffer, format='PNG')
            scheme_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Отримуємо курс долара
            usd_rate = round(get_usd_rate(), 2)
            
            results = {
                'success': True,
                'data': {
                    'panel_count': total_panels,
                    'profiles': grouped_profiles,
                    'g_clamps': g_clamps,
                    'v_clamps': v_clamps,
                    'm_sh': m_sh,
                    'front_connectors': front_connectors,
                    'connectors': connectors,
                    'scheme_image': f'data:image/png;base64,{scheme_base64}',
                    'scheme_file_path': scheme_file_path,  # Додаємо шлях до файлу схеми
                    'usd_rate': usd_rate,  # Додаємо курс долара
                    'current_date': datetime.now().strftime('%d.%m.%Y'),  # Додаємо поточну дату
                    # Додаємо параметри з форми
                    'form_data': {
                        'panel_brand': data.get('panel_brand', ''),
                        'panel_model': data.get('panel_model', ''),
                        'panel_width': panel_width,
                        'panel_length': panel_length,
                        'panel_height': panel_height,
                        'panel_arrangement': panel_arrangement,
                        'panel_type': panel_type,
                        'rows': rows,
                        'panels_per_row': panels_per_row,
                        'total_panels': total_panels,
                        'profile_lengths': data.get('profile_lengths', ''),
                        'string_count': data.get('string_count', ''),
                        'screw_material': data.get('screw_material', 'оцинковані'),  # Додаємо матеріал гвинт-шурупа
                        'profile_material': data.get('profile_material', 'алюміній'),  # Додаємо матеріал профілю
                        # Додаткові параметри (необов'язкові)
                        'inverterModel': data.get('custom_inverter_model', '') or data.get('inverter_model', ''),
                        'inverterPower': data.get('inverter_power', ''),
                        'inverterPhases': data.get('inverter_phases', ''),
                        'inverterBrand': data.get('inverter_brand', ''),
                        'inverterModelId': data.get('inverter_model', ''),
                        'batteryModel': data.get('custom_battery_model', '') or data.get('battery_model', ''),
                        'batteryPower': data.get('battery_capacity', ''),
                        'batteryBrand': data.get('battery_brand', ''),
                        'batteryModelId': data.get('battery_model', ''),
                        'batteryIsHead': 'Так' if data.get('battery_is_head') else 'Ні',
                        'batteryIsStand': 'Так' if data.get('battery_is_stand') else 'Ні',
                        'batteryIsStand8': 'Так' if data.get('battery_is_stand_8') else 'Ні',
                        'batteryIsStand12': 'Так' if data.get('battery_is_stand_12') else 'Ні',
                        'panelModelId': data.get('panel_model', ''),
                        'panelModelName': panel_model_name,  # Додаємо назву моделі
                        'inverterModelName': inverter_model_name,  # Додаємо назву моделі інвертора
                        'batteryModelName': battery_model_name  # Додаємо назву моделі батареї
                    }
                }
            }
            print(results)
            print("Profiles dictionary:", profile_counts)

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
            param_o = request.POST.get('param-o')
            param_k = request.POST.get('param-k')
            param_e = request.POST.get('param-e')
            param_r = request.POST.get('param-r')

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
            
            # Збираємо динамічно додані рядки для кожної категорії
            dynamic_equipment = []
            dynamic_mounting = []
            dynamic_electrical = []
            dynamic_work = []
            
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

            # Викликаємо функцію generate з отриманими даними
            pdf_path = generate(
                O=param_o, K=param_k, E=param_e, R=param_r,
                O11=int(data.get('O11', 0) or 0), O12=float(data.get('O12', 0) or 0.0),
                O21=int(data.get('O21', 0) or 0), O22=float(data.get('O22', 0) or 0.0),
                O31=int(data.get('O31', 0) or 0), O32=float(data.get('O32', 0) or 0.0),
                K1112= k_values,
                K21=int(data.get('K21', 0) or 0), K22=float(data.get('K22', 0) or 0.0),
                K31=int(data.get('K31', 0) or 0), K32=float(data.get('K32', 0) or 0.0),
                K41=int(data.get('K41', 0) or 0), K42=float(data.get('K42', 0) or 0.0),
                K51=int(data.get('K51', 0) or 0), K52=float(data.get('K52', 0) or 0.0),
                K61=int(data.get('K61', 0) or 0), K62=float(data.get('K62', 0) or 0.0),
                K71=int(data.get('K71', 0) or 0), K72=float(data.get('K72', 0) or 0.0),
                K81=int(data.get('K81', 0) or 0), K82=float(data.get('K82', 0) or 0.0),
                K91=int(data.get('K91', 0) or 0), K92=float(data.get('K92', 0) or 0.0),
                E11=int(data.get('E11', 0) or 0), E12=float(data.get('E12', 0) or 0.0),
                E21=int(data.get('E21', 0) or 0), E22=float(data.get('E22', 0) or 0.0),
                R11=int(data.get('R11', 0) or 0), R12=float(data.get('R12', 0) or 0.0),
                R21=int(data.get('R21', 0) or 0), R22=float(data.get('R22', 0) or 0.0),
                R31=int(data.get('R31', 0) or 0), R32=float(data.get('R32', 0) or 0.0),
                scheme_image=normalize_path(str(data.get('scheme_image', ''))),
                panel_height=int(data.get('panel_height', 30) or 30),  # Додаємо параметр висоти панелі
                dynamic_equipment=dynamic_equipment,
                dynamic_mounting=dynamic_mounting,
                dynamic_electrical=dynamic_electrical,
                dynamic_work=dynamic_work,
                usd_rate=float(data.get('usd_rate', '0').replace(',', '.') or 0.0),  # Замінюємо кому на крапку
                total_usd=float(data.get('total_usd', '0').replace(',', '.') or 0.0),  # Замінюємо кому на крапку
                screw_material=data.get('screw_material', 'оцинковані'),  # Додаємо матеріал гвинт-шурупа
                profile_material=data.get('profile_material', 'алюміній')  # Додаємо матеріал профілю
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

    return JsonResponse({'success': False, 'error': 'Метод не підтримується'})


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
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_panel.html', context)
            
            # Обробка завантаженого файлу
            datasheet_file = request.FILES['datasheet']
            
            # Створення унікального імені файлу
            file_extension = os.path.splitext(datasheet_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Шлях для збереження файлу
            datasheet_path = 'media/datasheets/' + unique_filename
            
            # Збереження файлу
            with open(datasheet_path, 'wb+') as destination:
                for chunk in datasheet_file.chunks():
                    destination.write(chunk)
            
            # Збереження відносного шляху в БД
            relative_path = 'datasheets/' + unique_filename
            
            # Створення нової панелі
            panel = Panels(
                brand=brand,
                model=model,
                panel_length=panel_length,
                panel_width=panel_width,
                panel_height=panel_height,
                datasheet=relative_path
            )
            panel.save()
            
            # Передаємо дані про успішне створення в контекст
            context['success'] = True
            context['panel'] = panel
            
            return render(request, 'create_panel.html', context)
            
        except Exception as e:
            print(traceback.format_exc())
            context['error'] = str(e)
            return render(request, 'create_panel.html', context)
    
    return render(request, 'create_panel.html', context)


def download_datasheet(request, panel_id):
    """
    Завантажує datasheet для вибраної моделі панелі.
    """
    try:
        # Отримуємо панель за id
        panel = Panels.objects.get(id=panel_id)
        
        # Нормалізуємо шлях до файлу
        panel_datasheet = normalize_path(panel.datasheet)
        
        # Формуємо повний шлях до файлу
        datasheet_path = os.path.dirname(os.path.dirname(__file__)) + '/media/' + panel_datasheet
        
        if os.path.exists(datasheet_path):
            # Відкриваємо файл для читання в бінарному режимі
            with open(datasheet_path, 'rb') as datasheet:
                # Визначаємо тип файлу (припускаємо, що це PDF)
                response = HttpResponse(datasheet.read(), content_type='application/pdf')
                # Встановлюємо заголовок для завантаження файлу
                response['Content-Disposition'] = f'attachment; filename="{panel.brand}_{panel.model}_datasheet.pdf"'
                return response
        else:
            # Якщо файл не знайдено, повертаємо помилку 404
            return HttpResponse(f"Datasheet не знайдено за шляхом: {datasheet_path}", status=404)
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
        
        # Нормалізуємо шлях до файлу
        inverter_datasheet = normalize_path(inverter.datasheet)
        
        # Формуємо повний шлях до файлу
        datasheet_path = os.path.dirname(os.path.dirname(__file__)) + '/media/' + inverter_datasheet
        
        if os.path.exists(datasheet_path):
            # Відкриваємо файл для читання в бінарному режимі
            with open(datasheet_path, 'rb') as datasheet:
                # Визначаємо тип файлу (припускаємо, що це PDF)
                response = HttpResponse(datasheet.read(), content_type='application/pdf')
                # Встановлюємо заголовок для завантаження файлу
                response['Content-Disposition'] = f'attachment; filename="{inverter.brand}_{inverter.model}_datasheet.pdf"'
                return response
        else:
            # Якщо файл не знайдено, повертаємо помилку 404
            return HttpResponse(f"Datasheet не знайдено за шляхом: {datasheet_path}", status=404)
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
        
        # Нормалізуємо шлях до файлу
        battery_datasheet = normalize_path(battery.datasheet)
        
        # Формуємо повний шлях до файлу
        datasheet_path = os.path.dirname(os.path.dirname(__file__)) + '/media/' + battery_datasheet
        
        if os.path.exists(datasheet_path):
            # Відкриваємо файл для читання в бінарному режимі
            with open(datasheet_path, 'rb') as datasheet:
                # Визначаємо тип файлу (припускаємо, що це PDF)
                response = HttpResponse(datasheet.read(), content_type='application/pdf')
                # Встановлюємо заголовок для завантаження файлу
                response['Content-Disposition'] = f'attachment; filename="{battery.brand}_{battery.model}_datasheet.pdf"'
                return response
        else:
            # Якщо файл не знайдено, повертаємо помилку 404
            return HttpResponse(f"Datasheet не знайдено за шляхом: {datasheet_path}", status=404)
    except Batteries.DoesNotExist:
        # Якщо батарея не знайдена, повертаємо помилку 404
        return HttpResponse("Батарею не знайдено", status=404)
    except Exception as e:
        # Якщо сталася інша помилка, повертаємо помилку 500
        return HttpResponse(f"Помилка: {str(e)}", status=500)


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
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_inverter.html', context)
            
            # Обробка завантаженого файлу
            datasheet_file = request.FILES['datasheet']
            
            # Створення унікального імені файлу
            file_extension = os.path.splitext(datasheet_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Шлях для збереження файлу
            datasheet_path = 'media/datasheets/' + unique_filename
            
            # Збереження файлу
            with open(datasheet_path, 'wb+') as destination:
                for chunk in datasheet_file.chunks():
                    destination.write(chunk)
            
            # Збереження відносного шляху в БД
            relative_path = 'datasheets/' + unique_filename
            
            # Створення нового інвертора
            inverter = Inverters(
                brand=brand,
                model=model,
                power=power,
                phases_count=phases_count,
                datasheet=relative_path
            )
            inverter.save()
            
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
            is_stand = 'is_stand' in request.POST
            
            # Перевірка наявності файлу
            if 'datasheet' not in request.FILES:
                context['error'] = 'Файл datasheet необхідний'
                return render(request, 'create_battery.html', context)
            
            # Обробка завантаженого файлу
            datasheet_file = request.FILES['datasheet']
            
            # Створення унікального імені файлу
            file_extension = os.path.splitext(datasheet_file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Шлях для збереження файлу
            datasheet_path = 'media/datasheets/' + unique_filename
            
            # Збереження файлу
            with open(datasheet_path, 'wb+') as destination:
                for chunk in datasheet_file.chunks():
                    destination.write(chunk)
            
            # Збереження відносного шляху в БД
            relative_path = 'datasheets/' + unique_filename
            
            # Створення нової батареї
            battery = Batteries(
                brand=brand,
                model=model,
                capacity=capacity,
                is_head=is_head,
                is_stand=is_stand,
                datasheet=relative_path
            )
            battery.save()
            
            # Передаємо дані про успішне створення в контекст
            context['success'] = True
            context['battery'] = battery
            
            return render(request, 'create_battery.html', context)
            
        except Exception as e:
            print(traceback.format_exc())
            context['error'] = str(e)
            return render(request, 'create_battery.html', context)
    
    return render(request, 'create_battery.html', context)
