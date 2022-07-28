import os
import telebot
import logging
import psycopg2
from config import *
from flask import Flask, request
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)


db_connection = psycopg2.connect(DB_URI, sslmode='require')
db_object = db_connection.cursor()


def update_messages_count(user_id):
    db_object.execute(f"UPDATE users SET messages = messages + 1 WHERE id = {user_id}")
    db_connection.commit()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    yes = types.KeyboardButton("Хорошо")
    markup.add(yes)
    bot.reply_to(message, f'Добро пожаловать, {username}. Перед работой с ботом, Вы должны ответить на несколько вопросов.', reply_markup=markup)

    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(id, username, messages) VALUES (%s, %s, %s)", (user_id, username, 0))
        db_connection.commit()

    update_messages_count(user_id)


@bot.message_handler(content_types=['text'])
def reg(message):
    markup_close = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Предлагаю познакомиться! Как вас зовут?", reply_markup=markup_close)
    bot.register_next_step_handler(message, reg_name)


def reg_name(message):
    global name
    name = message.text
    bot.reply_to(message, "Прекрасное имя!")
    bot.send_message(message.chat.id, "Сколько Вам лет?")
    bot.register_next_step_handler(message, reg_age)


def reg_age(message):
    global age
    age = int(message.text)
    bot.reply_to(message, "Окей")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton("Женский")
    button2 = types.KeyboardButton("Мужской")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "Ваш пол:", reply_markup=markup)
    bot.register_next_step_handler(message, reg_sex)


def reg_sex(message):
    global sex
    sex = message.text
    bot.send_message(message.chat.id, "Ваш рост?")
    bot.register_next_step_handler(message, reg_height)


def reg_height(message):
    global height
    height = int(message.text)
    bot.send_message(message.chat.id, "Сколько Вы весите?")
    bot.register_next_step_handler(message,reg_weight)


def reg_weight(message):
    global weight
    weight = int (message.text)
    bot.send_message(message.chat.id, "Ваша степень физической активности:")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton("Минимальная активность")
    button2 = types.KeyboardButton("Слабая активность: раз в неделю")
    button3 = types.KeyboardButton("Средняя активность: 3 раза в неделю")
    button4 = types.KeyboardButton("Высокая активность: почти каждый день")
    button5 = types.KeyboardButton("Экстра-активность: тяжелая физическая работа; спорт")
    markup.add(buttons)
    bot.register_next_step_handler(message, reg_weight)



@bot.message_handler(commands=['begin'])
def buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    receipt = types.KeyboardButton("Рецепты")
    data = types.KeyboardButton("Моя персональная информация")
    info = types.KeyboardButton("О боте")
    exit = types.KeyboardButton("Выход")
    markup.add(receipt, data)
    markup.add(info, exit)
    bot.send_message(message.chat.id, 'Выберите действие на меню', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def user_text(message):
  if message.text.lower() == 'моя персональная информация':
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
      button1 = types.KeyboardButton(text='Имя')
      button2 = types.KeyboardButton(text='Возраст')
      button3 = types.KeyboardButton(text='Пол')
      button4 = types.KeyboardButton(text='Рост')
      button5 = types.KeyboardButton(text='Вес')
      button6 = types.KeyboardButton(text='Физическая активность')
      button7 = types.KeyboardButton(text='Ккал в сутки')
      button8 = types.KeyboardButton(text='Назад')
      markup.add(button1, button2, button3, button4)
      markup.add(button5, button6, button7, button8)
      bot.send_message(message.chat.id, '', reply_markup=markup)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))