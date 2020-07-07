import telebotapi
from telebotapi import types
import sqlite3
import requests
import keyring #---- в будущем запрятать токен в пароль
import logging
import datetime
import os

bot = telebotapi.TBot(token)

#class Logger(): #--------------------------------------------------пока не существует, но будет в скором времени
 #   date = datetime.now().date().isoformat()

  #  def __init__(self, filename):
   #     if 'logs' not in os.listdir():
    ##   self.log = open('.\\logs\\{}'.format(filename + '_' + self.date + '.log'), 'a')
 #-- вот тут будут лоджинги
# log = Logger('Telebot_Log')

class Database:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def start_db(self, user_id, first_name, last_name):
        self.cursor.execute("INSERT OR IGNORE INTO users (id, first_name, last_name, IsAdmin) VALUES (%d,'%s', '%s', 0)" % (
            user_id, first_name, last_name))
        self.connection.commit()

    def admin_check(self):
        admin_list = {}
        self.cursor.execute("SELECT Id FROM users WHERE IsAdmin = 1")
        for line in self.cursor:
            admin_list[line[0]] = {}
            admin_list[line[0]]['Id'] = line[0]
        return list(dict.keys(admin_list))

    def admin_login_password_check(self, user_id):
        admin_login_list = {}
        self.cursor.execute("SELECT user_id, login, password FROM admin_authtorization")
        for line in self.cursor:
            admin_login_list[line[0]] = {}
            admin_login_list[line[0]]['user_id'] = line[0]
            admin_login_list[line[0]]['login'] = line[1]
            admin_login_list[line[0]]['password'] = line[2]
        return admin_login_list[user_id]

    def admin_add(self, userID, login, password):
        self.cursor.execute("INSERT OR IGNORE INTO admin_authtorization (user_id, login, password) VALUES (%d,'%s','%s')" %(userID, login, password))
        self.cursor.execute("UPDATE users SET IsAdmin = 1 WHERE Id = %d" %userID)
        self.connection.commit()

    def theme_write_in_data(self, category, user_id):
        self.cursor.execute("INSERT INTO categories (user_id, category) VALUES (%d,'%s')" % (
            user_id, category))
        self.connection.commit()

    def theme_choises(self, user_id):
        spisok = []
        callback_spisok = []
        choises_list = {}
        self.cursor.execute(
            """SELECT CallbackData, CategoryName FROM admin_categories acat
            LEFT JOIN categories cat on acat.CallbackData = cat.category
            WHERE cat.user_id = %d
            """ % user_id)
        for line in self.cursor:
            choises_list[line[0]] = {}
            choises_list[line[0]]['CallbackData'] = line[0]
            choises_list[line[0]]['CategoryName'] = line[1]
        check_category = dict.values(choises_list)
        for elem in check_category:
            spisok.append(elem['CategoryName'])
            callback_spisok.append(elem['CallbackData'])
        return spisok, callback_spisok

    def necessary_subscription(self, user_id):
        spisok = []
        sub_list = {}
        self.cursor.execute(
            """SELECT DISTINCT(fan.fandom) as fandom FROM category_subscriptions_binding csb
            JOIN categories cat on csb.category_id = cat.category
            JOIN fandoms_subscriptions_binding fsb on csb.subscription_id = fsb.subscription_id
            JOIN fandoms fan on fsb.fandom_name = fan.fandom_name
            WHERE user_id = %d
            """ % user_id)
        for line in self.cursor:
            sub_list[line[0]] = {}
            sub_list[line[0]]['fandom'] = line[0]
        check = dict.values(sub_list)
        for elem in check:
            spisok.append(elem['fandom'])
        return spisok

    def get_chat_id_by_check_subscription(self, user_id):
        spisok = []
        sub_list = {}
        self.cursor.execute(
            """SELECT DISTINCT(fandom_id) FROM category_subscriptions_binding csb
            JOIN categories cat on csb.category_id = cat.category
            JOIN fandoms_subscriptions_binding fsb on csb.subscription_id = fsb.subscription_id
            JOIN fandoms fan on fsb.fandom_name = fan.fandom_name
            WHERE user_id=%d
            """ % user_id)

        for line in self.cursor:
            sub_list[line[0]] = {}
            sub_list[line[0]]['fandom_id'] = line[0]

        check = dict.values(sub_list)
        for elem in check:
            spisok.append(elem['fandom_id'])
        return spisok

    def give_web_and_name_for_subscriptions(self, user_id):
        spisok_theme = []
        spisok_web = []
        sub_list = {}
        self.cursor.execute(
            """SELECT theme_name, groups FROM subscriptions
            WHERE groups in (SELECT DISTINCT(groups) FROM subscriptions s
            JOIN category_subscriptions_binding csb on s.theme_id = csb.subscription_id
            JOIN categories cat on csb.category_id = cat.category
            WHERE user_id = %d)
            """ % user_id)
        for line in self.cursor:
            sub_list[line[0]] = {}
            sub_list[line[0]]['theme_name'] = line[0]
            sub_list[line[0]]['groups'] = line[1]
        check = dict.values(sub_list)
        for elem in check:
            spisok_theme.append(elem['theme_name'])
            spisok_web.append(elem['groups'])
        return spisok_theme, spisok_web

    def delete_categories(self, user_id):
        self.cursor.execute('DELETE from categories WHERE user_id = %d' % user_id)
        self.connection.commit()

class Keyboards:

    def __init__(self, keyboard):
        self.keyboard = keyboard

    def user_first_menu(self): #------------------------ решить сука пробелму с клавишами
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text="🎥Фильмы", callback_data="key1"),
            types.InlineKeyboardButton(text="🎬Сериалы", callback_data="key2"),
            types.InlineKeyboardButton(text="📚Книги", callback_data="key3")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text="❤K-Pop", callback_data="key4"),
            types.InlineKeyboardButton(text="🦸‍♂️Комиксы", callback_data="key5")
            #пустое
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text="🎮Игры", callback_data="key6"),
            types.InlineKeyboardButton(text="🇯🇵Аниме", callback_data="key7")
            #types.InlineKeyboardButton(text="Косплей", callback_data="key8")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text='Я выбрал все интересные мне тематики', callback_data='first_step_continue')
        )
        return self.keyboard

    def user_second_menu(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text="Я подписался на выбранные каналы✅", callback_data="second_step_continue")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text='Редактировать тематики❌', callback_data='second_step_back')
        )
        return self.keyboard

    def user_second_back_choice(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text='Добавить тематики', callback_data='second_step_back_add'),
            types.InlineKeyboardButton(text='Удалить все выбранные тематики', callback_data='second_step_back_delete')
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text='Назад❌', callback_data='first_step_continue')
        )
        return self.keyboard

    def hypersilki(self, names, web):
        keyboard = types.InlineKeyboardMarkup()
        count = 0
        for name, webs in zip(names, web):
            count += 1
            keyboard.add(
                types.InlineKeyboardButton(text=name, url=str(webs))
            )
            if count == 5:
                break
        keyboard.add(
            types.InlineKeyboardButton(text='Развернуть➡️', callback_data='hyper_step_full'),
            types.InlineKeyboardButton(text='Назад❌', callback_data='first_step_continue')
        )
        return keyboard

    def hypersilki_full(self, names, web):
        keyboard = types.InlineKeyboardMarkup()
        for name, webs in zip(names, web):
            keyboard.add(
                types.InlineKeyboardButton(text=name, url=str(webs))
            )
        keyboard.add(
            types.InlineKeyboardButton(text='Свернуть❌', callback_data='second_step_continue'),
            types.InlineKeyboardButton(text='Назад❌', callback_data='first_step_continue')
        )
        return keyboard
    #----------------------------------------------------------------------- клава админа - пидора
    def admin_action(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text="Редактировать тематики", callback_data="admin_edit"),
            types.InlineKeyboardButton(text="Управлять админкой", callback_data="admin_admins")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text="Выход", callback_data="admin_exit")
        )
        return self.keyboard

    def admin_action_edit(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text="Добавить тематику", callback_data="admin_edit_add"),
            types.InlineKeyboardButton(text="Удалить тематику", callback_data="admon_edit_delete")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="admin_edit_back")
        )
        return self.keyboard

    def admin_admins(self):
        self.keyboard = types.InlineKeyboardMarkup()
        self.keyboard.add(
            types.InlineKeyboardButton(text="Добавить админа", callback_data="admin_admins_add_admin"),
            types.InlineKeyboardButton(text="Функция - 2 ", callback_data="admin_admins_func_2"),
            types.InlineKeyboardButton(text="Функция - 3 ", callback_data="admin_admins_delete_func_3")
        )
        self.keyboard.add(
            types.InlineKeyboardButton(text="Назад", callback_data="admin_edit_back")
        )
        return self.keyboard

# ----- вот эта хуйня - это тип для клавиутары выше в классе
inline_board = Keyboards(keyboard=types.InlineKeyboardMarkup())
replay_board = Keyboards(keyboard=types.ReplyKeyboardMarkup())

#при старте
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    DB = Database("./info/sql.db")
    DB.start_db(user_id=user_id, first_name=first_name, last_name=last_name)
    bot.send_message(message.from_user.id, "Приветствую, {}. "
                                           "Выбери интересующие тебя тематики из списка представленных, но не более семи:".format(
        first_name), reply_markup=inline_board.user_first_menu())


@bot.callback_query_handler(func=lambda call: 'key' in call.data)
def get_choice(callback):
    user_id = callback.from_user.id
    category = callback.data
    DB = Database("./info/sql.db")
    user_category_check_list = DB.theme_choises(user_id=user_id)[1]
    try:
        if len(user_category_check_list) >= 7:
            bot.answer_callback_query(callback.id, text='Вы выбрали максимально возможное количество тематик🤷‍♂') #далее функция некст степ хендлера
        elif len(user_category_check_list) < 7:
            if callback.data in user_category_check_list:
                bot.answer_callback_query(callback.id, text='Вы уже выбирали эту тематику❌\nДалее вы сможете ее изменить👌')
            elif callback.data not in user_category_check_list:
                DB.theme_write_in_data(category=category, user_id=user_id)
                bot.answer_callback_query(callback.id, text='Ваш выбор сохранен✅')
    except IndexError:
        DB.theme_write_in_data(category=category, user_id=user_id)
        bot.answer_callback_query(callback.id, text='Ваш выбор сохранен✅')

@bot.callback_query_handler(func=lambda call: 'step' in call.data)
def user_steps(callback):
    user_id = callback.from_user.id
    DB = Database("./info/sql.db")
    count = len(DB.theme_choises(user_id=user_id)[0])
    theme_choises = DB.theme_choises(user_id=user_id)[0]
    nes_subscription = DB.necessary_subscription(user_id=user_id)
    names = DB.give_web_and_name_for_subscriptions(user_id=user_id)[0]
    web = DB.give_web_and_name_for_subscriptions(user_id=user_id)[1]
    if callback.data == 'first_step_continue':
        if count < 1:
            bot.answer_callback_query(callback.id, '❌Выберите хотя бы одну тематику!')
        elif count >= 1:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, 'Вы выбрали {} тематик(и):\n{}\n'
                                                   '\nПодпишитесь на выбранные каналы, чтобы получить доступ к беседкам\t'
                                                   'по выбранным тематикам: \n\n{}'.format(count, ', '.join(theme_choises), '\n'.join(nes_subscription)),
                                                    disable_web_page_preview=True, reply_markup=inline_board.user_second_menu())

    if callback.data == 'second_step_continue':
        chat_ids = DB.get_chat_id_by_check_subscription(user_id=user_id)
        user_list = []
        for chat_id in chat_ids:
            try:
                podpiska = requests.get('https://api.telegram.org/bot%s/getChatMember?chat_id=%d&user_id=%d' %(token, chat_id ,user_id)).json()
                r = dict(podpiska)['result']['status']
                user_list.append(r)
            except:
                print("error")
        if 'left' not in user_list and 'member' in user_list:
            bot.send_message(callback.message.chat.id, 'Вы успешно выполнили все условия!✅\nВот ваши ссылки:',
                            reply_markup=inline_board.hypersilki(names=names, web=web))
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        elif 'left' in user_list:
            bot.answer_callback_query(callback.id, "❌Вы должны подписаться на выбранные каналы!")

    if callback.data == 'second_step_back':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Вы можете изменить или добавить интересующие вас темы:\nВ данный момент вы выбрали: \n{}'.format(', '.join(theme_choises)), reply_markup=inline_board.user_second_back_choice())
    if callback.data == 'second_step_back_add':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Выбери интересующие тебя тематики из списка представленных:", reply_markup=inline_board.user_first_menu())
    if callback.data == 'second_step_back_delete':
        DB.delete_categories(user_id=user_id)
        theme_choises = DB.theme_choises(user_id=user_id)[0]
        bot.answer_callback_query(callback.id, 'Вы удалили все тематики. Нажмите на добавить тематики, чтобы перевыбрать!')
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Вы можете изменить или добавить интересующие вас темы:\nВ данный момент вы выбрали: \n{}'.format(', '.join(theme_choises)), reply_markup=inline_board.user_second_back_choice())
    if callback.data == 'hyper_step_full':
        bot.edit_message_reply_markup(callback.message.chat.id, callback.message.message_id, reply_markup=inline_board.hypersilki_full(names=names, web=web))

#остановился тут, на добавлении - удалении тематик. Короче, почти закончено.

#----------------------------------------Для Админов--------------------------------------------------------------#

#самое сложно - редактор админов, но с текущей БД это делается)

class AdminAddCategory:
    def __init__(self, database="./info/sql.db"):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def categoryId(self):
        admin_list = {}
        self.cursor.execute('SELECT Id FROM admin_categories')
        for line in self.cursor:
            admin_list[line[0]] = {}
            admin_list[line[0]]['Id'] = line[0]
        return list(dict.keys(admin_list))[-1]

    def admin_add_new_category(self, category_name):
        calldata = 'key' + (self.categoryId() + 1)
        self.cursor.execute('INSERT OR IGNORE INTO admin_categories (CategoryName, CallbackData) VALUES (%s, %s)' %(category_name, calldata))

    def admin_add_new_subscription(self, theme_name, groups):
        self.cursor.execute('INSERT OR IGNORE INTO subscriptions (theme_name, groups) VALUES (%s, %s)' % (theme_name, groups))

    def admin_add_new_fandom(self, fandom_id, fandom_name, fandom_web):
        self.cursor.execute('INSERT OR IGNORE INTO fandoms (fandom_id, fandom_name, fandom) VALUES (%d, %s, %s)' % (fandom_id, fandom_name, fandom_web))

    def save(self):
        self.connection.commit()

# авторизация в боте
@bot.message_handler(commands=['admin'])
def admin_pass(message):
    DB = Database("./info/sql.db")
    admin_list_id = DB.admin_check()
    if message.from_user.id not in admin_list_id:
        bot.send_message(message.chat.id, 'Ошибся командой, ты не админ %s' %message.from_user.first_name)
    else:
        msg = bot.send_message(message.chat.id, "Привет, теперь авторизируйся :)")
        bot.register_next_step_handler(msg, admin_login_password)

#--закончил на проверке логин/пароль админа - функция тут. Скрипт БД там
def admin_login_password(message):
    user_id = message.from_user.id
    data = message.text.split()  #список ['логин', 'пароль']
    DB = Database("./info/sql.db")
    check = DB.admin_login_password_check(user_id=user_id)
    try:
        if data[0] == check['login'] and data[1] == check['password']:
            bot.send_message(message.from_user.id, 'Что будем делать?', reply_markup=inline_board.admin_action())
        else:  # если такой комбинации не существует, ждём команды /start Опять
            msg = bot.send_message(message.from_user.id, 'Неправильно введен логин\пароль')
            bot.register_next_step_handler(msg, admin_login_password)
    except IndexError:
        msg = bot.send_message(message.from_user.id,'Введи логин/пароль в строчку через пробел.')
        bot.register_next_step_handler(msg, admin_login_password)

@bot.callback_query_handler(func=lambda call: 'admin' in call.data)
def admin_button(callback):
    if callback.data == "admin_edit":
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text="Что вы хотите сделать?", reply_markup=inline_board.admin_action_edit())
    if callback.data == "admin_edit_add":
        bot.send_message(callback.message.chat.id, 'В процессе')
        # if callback.data == "admin_edit_delete":
    if callback.data == "admin_edit_back":
       bot.edit_message_text('Что вы хотите сделать?', chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id, reply_markup=inline_board.admin_action())
    if callback.data == "admin_exit":
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="Пока!")
    if callback.data == "admin_admins":
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text="Что вы хотите сделать?", reply_markup=inline_board.admin_admins())
    if callback.data == "admin_admins_add_admin":
        msg = bot.send_message(callback.message.chat.id,
                               """
Введите TelegramID, Логин и Пароль пользователя в формате TelegramID/Login/Password.
Данные должны быть предоставлены вам будущим админом заранее.
               
Чтобы узнать айди, будущий админ может воспользоваться ботом @userinfobot
""")
        bot.register_next_step_handler(msg, admin_register) #возможно переделать в нижнюю клавиатуру, которая выдает команды
         #функция хендлер по добавлению админа
    #if callback.data == "admin_admins_func_2":
    #if callback.data == "admin_admins_func_3"
    #if callback.data == "admin_admins_back":

def admin_register(message):
    DB = Database("./info/sql.db")
    txt = message.text.split('/')
    try:
        userID, login, password = (int(txt[0]), txt[1], txt[2])
        DB.admin_add(userID=userID, login=login, password=password)
        bot.send_message(message.chat.id, 'Администратор успешно добавлен!')
    except IndexError:
        bot.send_message(message.chat.id, 'Нажмите еще раз на "Добавить администратора", и введите данные одним сообщением через \"/\"')


    #if confirm_password == password:
        #DB.admin_add(userID=userID, login=login, password=password)
        #bot.edit_message_text(message.chat.id, 'Администратор добавлен✅')
    #else:
        #msg = bot.send_message(message.from_user.id, 'Пароли не свопадают, попробуйте еще раз❌')
        #bot.register_next_step_handler(msg, admin_register(message))
#--------------------ПУСК!
bot.polling(none_stop=True, interval=0)
