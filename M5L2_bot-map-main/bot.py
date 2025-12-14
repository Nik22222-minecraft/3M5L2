import telebot
from config import TOKEN, DATABASE
from logic import DB_Map

bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)
manager.create_tables()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! 🌍 Я бот с картами городов.\n"
        "Команды: /help"
    )


@bot.message_handler(commands=["help"])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        "/show_city <city>\n"
        "/show_country <country>\n"
        "/show_population <число>\n"
        "/set_color <color>"
    )


@bot.message_handler(commands=["set_color"])
def set_color(message):
    color = message.text.split()[-1]
    manager.set_color(message.chat.id, color)
    bot.send_message(message.chat.id, f"Цвет маркеров: {color}")


@bot.message_handler(commands=["show_city"])
def show_city(message):
    city = message.text.split()[-1]
    path = "city.png"
    color = manager.get_color(message.chat.id)

    manager.create_graph(path, [city], color)
    bot.send_photo(message.chat.id, open(path, "rb"))


@bot.message_handler(commands=["show_country"])
def show_country(message):
    country = message.text.split()[-1]
    cities = manager.get_cities_by_country(country)

    path = "country.png"
    manager.create_graph(path, cities, manager.get_color(message.chat.id))
    bot.send_photo(message.chat.id, open(path, "rb"))


@bot.message_handler(commands=["show_population"])
def show_population(message):
    pop = int(message.text.split()[-1])
    cities = manager.get_cities_by_population(pop)

    path = "population.png"
    manager.create_graph(path, cities, manager.get_color(message.chat.id))
    bot.send_photo(message.chat.id, open(path, "rb"))


if __name__ == "__main__":
    bot.polling()
