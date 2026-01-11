import telebot
import requests
from datetime import datetime

TOKEN = "8534727094:AAE0Y_zNQTN2iUhsBn9tFtUF3M6qhdm3dPM"
bot = telebot.TeleBot(TOKEN)
DEEPSEEK_API_KEY = "sk-06d469e0b76e41929d9fb8081b188907"


# Экономия токенов

MAX_TOKENS = 200 #больше токенов больше ответ
API_URL = "https://api.deepseek.com/v1/chat/completions"

#потом заменить на базу
user_usage = {}

#Проверка лимитов. Увеличивает кол-во исп. вопросов + 1
def check_daily_limit(user_id):
    """Проверка лимита запросов в день"""
    today = datetime.now().date().isoformat()

    #Впервые зашел в бота
    if user_id not in user_usage:
        user_usage[user_id] = {'date': today, 'count': 1}
        return True
    #Если наступил след. день. сбросить лимит запросов
    if user_usage[user_id]['date'] != today:
        user_usage[user_id] = {'date': today, 'count': 1}
        return True

    #Если лимит исчерпан !!!!!!!
    if user_usage[user_id]['count'] >= 15:  # Максимум 15 вопросов в день
        return False

    user_usage[user_id]['count'] += 1
    return True


#Запрос к DeepSeek API с оптимизацией токенов
def askDeepseek(question):


    # Обрезаем вопрос если слишком длинный
    if len(question) > 300:
        question = question[:300] + "..."

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Ты полезный помощник. Отвечай максимально кратко и по делу. Ограничь ответ 3-4 предложениями. Используй не более 600-700 букв в ответе"
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": MAX_TOKENS,  # Экономим токены
        "temperature": 0.5,  # Уменьшил температуру для более предсказуемых ответов
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Ошибка API: {response.status_code}, {response.text}")
            return f"Ошибка: {response.status_code}. Попробуйте позже."

    except requests.exceptions.Timeout:
        return "Время ожидания истекло. Попробуйте снова."
    except Exception as e:
        print(f"Ошибка в askDeepseek: {e}")
        return "Произошла ошибка при обработке запроса."



@bot.message_handler(commands=['start'])
def start(message):

    welcome_text = ("Это бот-дипсик. Задай вопрос и получи краткий ответ."
                    "Использу /ai и сразу после команды пиши вопрос")
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=['ai'])
def deepseekSearch(message):
    """Обработчик команды /ai"""
    user_id = message.from_user.id

    # Проверяем лимит
    if not check_daily_limit(user_id):
        bot.send_message(
            message.chat.id,
            "❌ Вы превысили дневной лимит в 10 вопросов. Попробуйте завтра!"
        )
        return

    # Получаем вопрос
    user_question = message.text.replace("/ai", "").strip()

    if not user_question:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, напишите вопрос после команды /ai\nПример: /ai Что такое ИИ?"
        )
        return

    # Отправляем статус "печатает"
    bot.send_chat_action(message.chat.id, 'typing')

    # Получаем ответ от DeepSeek
    deepseekAnswer = askDeepseek(user_question)

    # Отправляем ответ
    bot.send_message(message.chat.id, deepseekAnswer)



# @bot.message_handler(commands=['stats'])


bot.infinity_polling()



# JSON объекты
# 1 токен = 3 символа
# 100 токенов = 300 символов(короткий ответ)
# 1000 токенов = 3000 символов(большой ответ)
# 1 млн токенов = 40 руб
# 10000 ответов
# 5-10 вопросов от 1 человека на 1 день

# 1 месяц. обслуживал 100 человек в день. каждый день спрашивая по 10 вопросов
# 3млн токенов и 120 руб

# ПОТОМ ВЕРНУТЬ
# @bot.message_handler(commands=['start'])
# def start(message):
#
#     user = message.from_user
#
#     supabase.table("users").insert({
#         'telegram_id': user.id,
#         'username': user.username,
#         'first_name': user.first_name
#     }).execute()
#
#     bot.send_message(message.chat.id, "Финансовый трекер")


from supabase import create_client
#
# supabase = create_client(
#     "https://asqxifhosgyvlijrxmli.supabase.co",
#     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzcXhpZmhvc2d5dmxpanJ4bWxpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTczNDcxMjQsImV4cCI6MjA3MjkyMzEyNH0.OmDAmQ1KM_QQCsooSLwOpFI98tvIIWPubjp8VtTKcEo"
# )

# ПОТОМ ВЕРНУТЬ

# message = {
#     'message_id': 123,
#     'chat': {
#         'id': 123456789,  # ID чата
#         'type': 'private'
#     },
#     'from': {  # <-- Вот откуда from_user!
#         'id': 987654321,      # telegram_id пользователя
#         'is_bot': False,
#         'first_name': 'Иван',
#         'last_name': 'Иванов',
#         'username': 'ivan_ivanov',
#         'language_code': 'ru'
#     },
#     'date': 1705312800,
#     'text': '/start'
# }


