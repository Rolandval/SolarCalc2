import telebot
import os
import logging
from django.conf import settings
import threading

logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.getenv('BOT_TOKEN'))

# Ініціалізуємо бота
bot = telebot.TeleBot(BOT_TOKEN)

# Словник для зберігання chat_id користувачів
user_chat_ids = {}

# Додаємо chat_id за замовчуванням, якщо він вказаний в налаштуваннях
default_chat_id = getattr(settings, 'TELEGRAM_DEFAULT_CHAT_ID', os.getenv('TELEGRAM_DEFAULT_CHAT_ID'))
if default_chat_id:
    user_chat_ids['default'] = default_chat_id
    logger.info(f"Додано chat_id за замовчуванням: {default_chat_id}")

# Змінна для відстеження стану бота
bot_running = False
bot_thread = None

@bot.message_handler(commands=['start'])
def start(message):
    """Обробник команди /start"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_chat_ids[user_id] = chat_id
    
    logger.info(f"Користувач {user_id} почав роботу з ботом, chat_id: {chat_id}")
    bot.send_message(chat_id, f"Вітаю! Я бот для відправки PDF звітів про сонячні електростанції.\n"
                             f"Ваш chat_id: {chat_id}\n"
                             f"Будь ласка, додайте цей chat_id в налаштування Django (settings.py) "
                             f"як значення TELEGRAM_DEFAULT_CHAT_ID.")
    
    # Показуємо список доступних звітів, якщо вони є
    show_available_reports(chat_id)

def show_available_reports(chat_id):
    """Показує список доступних звітів"""
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'results')
    
    if not os.path.exists(reports_dir):
        bot.send_message(chat_id, "Немає доступних звітів.")
        return
    
    reports = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
    
    if not reports:
        bot.send_message(chat_id, "Немає доступних звітів.")
        return
    
    message = "Доступні звіти:\n\n"
    for i, report in enumerate(reports, 1):
        message += f"{i}. {report}\n"
    
    bot.send_message(chat_id, message)

def send_pdf_to_telegram(pdf_path, chat_id=None):
    """
    Відправляє PDF звіт в Telegram
    
    Args:
        pdf_path (str): Шлях до PDF файлу
        chat_id (str, optional): ID чату, куди відправляти файл. 
                                Якщо не вказано, відправляється всім користувачам.
    
    Returns:
        bool: True, якщо відправка успішна, False в іншому випадку
    """
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF файл не знайдено: {pdf_path}")
            return False
        
        # Якщо chat_id не вказано, відправляємо всім користувачам
        if chat_id is None:
            if not user_chat_ids:
                logger.warning("Немає зареєстрованих користувачів для відправки PDF")
                return False
            
            success = False
            for user_id, user_chat_id in user_chat_ids.items():
                try:
                    with open(pdf_path, 'rb') as pdf_file:
                        bot.send_document(user_chat_id, pdf_file, caption="Звіт про сонячну електростанцію")
                    logger.info(f"PDF звіт успішно відправлено користувачу {user_id}")
                    success = True
                except Exception as e:
                    logger.error(f"Помилка при відправці PDF користувачу {user_id}: {e}")
            
            return success
        else:
            # Відправляємо конкретному користувачу
            with open(pdf_path, 'rb') as pdf_file:
                bot.send_document(chat_id, pdf_file, caption="Звіт про сонячну електростанцію")
            logger.info(f"PDF звіт успішно відправлено в чат {chat_id}")
            return True
    
    except Exception as e:
        logger.error(f"Помилка при відправці PDF в Telegram: {e}")
        return False

# Функція для запуску бота в окремому потоці
def start_bot():
    """Запускає бота в окремому потоці, якщо він ще не запущений"""
    global bot_running, bot_thread
    
    # Перевіряємо, чи бот вже запущений
    if bot_running:
        logger.info("Telegram бот вже запущено")
        return
    
    def run_bot():
        global bot_running
        try:
            logger.info("Запуск Telegram бота")
            bot_running = True
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            logger.error(f"Помилка при запуску бота: {e}")
        finally:
            bot_running = False
    
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Потік буде завершено разом з основним потоком
    bot_thread.start()
    logger.info("Telegram бот запущено в окремому потоці")

# Запускаємо бота при імпорті модуля
start_bot()