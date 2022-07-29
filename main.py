import os
import telebot
import logging
import openpyxl
from config import *
from flask import Flask, request
from telebot import types

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)

path = 'C:\Users\Asus\PycharmProjects\myplate\users.xlsx'
wb_obj = openpyxl.load_workbook(path)
sheet_obj = wb_obj.active


@bot.message_handler(commands=['start'])
def start(message):
    global user_id
    user_id = message.from_user.id
    global username
    username = message.from_user.username
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    yes = types.KeyboardButton("Хорошо")
    markup.add(yes)
    bot.reply_to(message, f'Добро пожаловать, {username}. Перед работой с ботом, Вы должны ответить на несколько вопросов.', reply_markup=markup)


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
    global f
    if sex == "Женский":
        f = -161
    else:
        f = 5
    bot.send_message(message.chat.id, "Ваш рост в сантиметрах?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, reg_height)


def reg_height(message):
    global height
    height = int(message.text)
    bot.send_message(message.chat.id, "Сколько Вы весите в киллограммах?")
    bot.register_next_step_handler(message, reg_weight)


def reg_weight(message):
    global weight
    weight = int(message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton("Минимальная активность")
    button2 = types.KeyboardButton("Слабая активность: раз в неделю")
    button3 = types.KeyboardButton("Средняя активность: 3 раза в неделю")
    button4 = types.KeyboardButton("Высокая активность: почти каждый день")
    button5 = types.KeyboardButton("Экстра-активность: тяжелая физическая работа; спорт")
    markup.add(button1, button2, button3, button4, button5)
    bot.send_message(message.chat.id, "Ваша степень физической активности:", reply_markup=markup)
    bot.register_next_step_handler(message, reg_all)


def reg_all(message):
    markup_inline = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton(text='➖Молоко', callback_data='молоко')
    item2 = types.InlineKeyboardButton(text='➖Яйцо', callback_data='яйцо')
    item3 = types.InlineKeyboardButton(text='➖Пшеница', callback_data='пшеница')
    item4 = types.InlineKeyboardButton(text='➖Рыба', callback_data='рыба')
    item5 = types.InlineKeyboardButton(text='➖Орехи', callback_data='орехи')
    item6 = types.InlineKeyboardButton(text='➖Грибы', callback_data='грибы')
    item7 = types.InlineKeyboardButton(text="➖Курица", callback_data='курица')
    item8 = types.InlineKeyboardButton(text='➖Шоколад', callback_data='шоколад')
    item9 = types.InlineKeyboardButton(text='➖Кофе', callback_data='кофе')
    item10 = types.InlineKeyboardButton(text='➖Картофель', callback_data='картофель')
    item11 = types.InlineKeyboardButton(text='➖Лимон', callback_data='лимон')
    item12 = types.InlineKeyboardButton(text='➖Рис', callback_data='рис')
    item13 = types.InlineKeyboardButton(text='➖Перец', callback_data='перец')
    markup_inline.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13)
    bot.send_message(message.chat.id, "На какие продукты у Вас аллергия?", reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.send_message(call.message.chat.id, 'Хорошо!')
    allergy = ""
    global allergy
    products = ["молоко", "яйцо", "пшеница", "рыба", "орехи", "грибы", "курица", "шоколад", "кофе", "картофель", "лимон", "рис", "перец"]
    for i in range(0, 14):
        if call.data == products[i]:
            allergy = allergy + call.data
    bot.register_next_step_handler(callback, reg_all)


def reg_phy(message):
    global phy
    phy = message.text
    bot.reply_to(message, 'Cпасибо за информацию!', reply_markup=types.ReplyKeyboardRemove())
    if phy == "Минимальная активность":
        A = 1.2
    elif phy == "Слабая активность: раз в неделю":
        A = 1.375
    elif phy == "Средняя активность: 3 раза в неделю":
        A = 1.55
    elif phy == "Высокая активность: почти каждый день":
        A = 1.725
    elif phy == "Экстра-активность: тяжелая физическая работа; спорт":
        A = 1.9
    else:
        bot.send_message(message.chat.id, "invalid data")
    global call
    call = (10 * weight + 6.25 * height - 5 * age + f) * A
    bot.send_message(message.chat.id,  "Бот расчитывает количество калорий по формуле Миффлина-Сан Жеора- одной из самых последних формул расчета калорий для оптимального похудения или сохранения нормального веса.")
    bot.send_message(message.chat.id, "Необходимое количество килокалорий (ккал) в сутки для Вас = " + str(call)+" "+"ккал")
    bot.send_message(message.chat.id, "Нажмите /save для сохранения данных ")


@bot.message_handler(commands=['save'])
def save(message):
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=1).value = user_id
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=2).value = username
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=3).value = name
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=4).value = age
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=5).value = height
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=6).value = weight
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=7).value = phy
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=8).value = call
     sheet_obj.cell(row=sheet_obj.max_row + 1, column=9).value = allergy



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


@bot.message_handler(content_types=['text'])
def get_user_book(message):
  book = message.text.lower()
  path = open("/content/drive/MyDrive/NIS учебники/" + book + ".pdf", "rb")
  bot.send_message(message.chat.id, "Ищем книгу...")
  bot.send_document(message.chat.id, path)
  path.close()


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
