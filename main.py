import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import random

# Ваши данные для авторизации
token = "token"
group_id = "id"

# Инициализация библиотеки vk_api
vk_session = vk_api.VkApi(token=token)
longpoll = VkBotLongPoll(vk_session, group_id=group_id)
vk = vk_session.get_api()

# Счетчик кликов для каждого пользователя (в данном случае используем простой словарь)
click_counters = {}

# Баланс баллов для каждого пользователя
balances = {}

# Список слов с соответствующими ссылками на изображения
word_list = [
    {"word": "перое", "image": "img/1.png"},
    {"word": "второе", "image": "img/2.png"},
    {"word": "третье", "image": "img/3.png"},
    {"word": "четвертое", "image": "img/4.png"},
    {"word": "пятое", "image": "img/5.png"}
]

# Получение информации о пользователе
def get_user_info(user_id):
    user_data = vk.users.get(user_ids=user_id, fields="first_name,last_name")[0]
    first_name = user_data["first_name"]
    last_name = user_data["last_name"]
    return {"first_name": first_name, "last_name": last_name}

# Отправка клавиатуры с кнопкой "Профиль" пользователю
def send_profile_keyboard(user_id):
    keyboard = {
        "one_time": False,
        "buttons": [
            [{"action": {"type": "text", "label": "+клик"}, "color": "positive"}],
            [{"action": {"type": "text", "label": "Показать профиль"}, "color": "primary"}]
        ]
    }
    vk.messages.send(peer_id=user_id, message="Нажми кнопку +клик для увеличения счетчика кликов:", keyboard=json.dumps(keyboard), random_id=0)

# Основной цикл обработки событий
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.object.message['from_id']
        text = event.object.message['text']
        
        if user_id not in click_counters:
            click_counters[user_id] = 0
            balances[user_id] = 0
        
        if text.lower() == "+клик":
            click_counters[user_id] += 1
            balances[user_id] += 0.1  # 1 клик = 0.1 балла
            
            if click_counters[user_id] % 5 == 0:
                word_data = random.choice(word_list)
                chosen_word = word_data["word"]
                image_link = word_data["image"]
                
                # Отправка сообщения с изображением
                vk.messages.send(
                    peer_id=user_id,
                    message=f"Ты кликнул {click_counters[user_id]} раз. Твой баланс: {balances[user_id]:.1f} баллов. Твое слово: {chosen_word}",
                    random_id=0,
                    attachment=word_data["image"] #возможноый баг
                )
        elif text.lower() == "показать профиль":
            user_data = get_user_info(user_id)
            vk.messages.send(peer_id=user_id, message=f"Фамилия: {user_data['last_name']}\nИмя: {user_data['first_name']}\nБаланс: {balances[user_id]:.1f} баллов", random_id=0)
        else:
            # Отправляем клавиатуру при первом сообщении
            send_profile_keyboard(user_id)
