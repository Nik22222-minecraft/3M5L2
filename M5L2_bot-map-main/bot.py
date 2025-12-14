import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Привет! 🌍 Я бот, который показывает города на карте.\n"
        "Напиши /help для списка команд."
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "/show_city <city> — показать город на карте\n"
        "/remember_city <city> — сохранить город\n"
        "/show_my_cities — показать все сохранённые города"
    )

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Напиши название города после команды.")
        return

    city_name = parts[1]
    path = "city.png"

    manager.create_graph(path, [city_name])
    bot.send_photo(message.chat.id, open(path, "rb"))

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Напиши название города.")
        return

    city_name = parts[1]
    user_id = message.chat.id

    if manager.add_city(user_id, city_name):
        bot.send_message(
            message.chat.id,
            f"Город {city_name} успешно сохранён ✅"
        )
    else:
        bot.send_message(
            message.chat.id,
            "Я не знаю такой город 😢\n"
            "Проверь, что он написан на английском."
        )

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)

    if not cities:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых городов.")
        return

    path = "my_cities.png"
    manager.create_graph(path, cities)
    bot.send_photo(message.chat.id, open(path, "rb"))

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    bot.polling()
