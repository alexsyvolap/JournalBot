from flask import Flask, request
import telebot
import const
import pymysql
import re

token = const.token

bot = telebot.TeleBot(token, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=const.URL_WEBHOOK)

app = Flask(__name__)

@app.route('/', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# function connect to database and create cursor
def create_cursor(db):
    db = pymysql.connect(const.BD_HOST, const.BD_USER, const.BD_PASSWORD, db=const.BD_DATABASE, charset='utf8')
    return db


keyboard = telebot.types.InlineKeyboardMarkup()
one = telebot.types.InlineKeyboardButton(text="1", callback_data="one")
two = telebot.types.InlineKeyboardButton(text="2", callback_data="two")
three = telebot.types.InlineKeyboardButton(text="3", callback_data="three")
four = telebot.types.InlineKeyboardButton(text="4", callback_data="four")
five = telebot.types.InlineKeyboardButton(text="5", callback_data="five")
close = telebot.types.InlineKeyboardButton(text="❌" , callback_data="close")

lb = ""
fname = ""
lname = ""
cid = 0
uid = 0
ct = ""
def add_glob(message):
    global fname, lname, cid, uid, ct
    fname = message.from_user.first_name
    if message.from_user.last_name:
        lname = message.from_user.last_name
    else:
        lname = "NULL"
    cid = message.chat.id
    uid = message.from_user.id
    a = bot.get_chat(cid)
    ct = str(a.title).lower()

def show_tables(db, cursor):
    sql = "show tables"
    k = cursor.execute(sql)
    r = cursor.fetchall()
    i = 0
    n = [k]
    for row in r:
        n.insert(i, row[0])
        i += 1
    return n

def show_fields(db, cursor):
    sql = "show fields from {}".format(ct)
    k = cursor.execute(sql)
    r = cursor.fetchall()
    n = []
    i = 0
    for row in r:
        n.insert(i, row[0])
        i += 1
    return n

def set_lab(indx, lab, mes, db, cursor, uid):
    if uid in const.admins:
        global ct
        r = re.split(r" ", mes.text)
        sql = "select id, rating from %s where fname='%s' and lname='%s'" % (ct, str(r[0]), str(r[1]))
        h = cursor.execute(sql)
        g = cursor.fetchall()
        id = 0
        rating = 0
        for row in g:
            id = row[0]
            rating = row[1]
        p = "select %s from %s where id=%s" % (lab, ct, id)
        k = cursor.execute(p)
        bal = cursor.fetchall()
        print(bal[0][0], rating)
        if k == 1:
            q = (rating - bal[0][0]) + indx
        upd = "update %s set %s=%s, rating=%s" % (ct, lab, indx, q)
        u = "where id=%s" % (str(id))
        sql = upd + " " + u
        return sql
    else: return "User not admin"

def final(index, db, cursor):
    sf = show_fields(db, cursor)
    o = ""
    u = 0
    print(index)
    if (index == "_set") | (index == "_del"):
        u = 4
    else:
        u = 3
    t = 3
    if len(sf) > u:
        o = sf[u]
        keyboard.keyboard.clear()
        while u < len(sf):
            btn = telebot.types.InlineKeyboardButton(text="%s" % sf[u], callback_data="%s" % sf[u] + index)
            keyboard.add(btn)
            u += 1
    else:
        bot.send_message(cid, "Лабараторных еще нету")
        return "Error"

def what(indx, sf):
    i = 0
    o = []
    while i < len(sf):
        o.insert(i, sf[i]+indx)
        i += 1
    return o

def ocenki(index, sf, db, cursor):
    global ct
    if str(index) in sf:
        print("Такой столбик есть, изменяем!")
        sql = "select fname, lname from {}".format(ct)
        k = cursor.execute(sql)
        keyboard.keyboard.clear()
        keyboard.add(one, two, three, four, five)
        keyboard.add(close)
        for row in cursor:
            bot.send_message(cid, str(row[0]) + " " + str(row[1]), reply_markup=keyboard)
    else:
        print("Столбика нету!")
        bot.send_message(cid, "Сори, %s столбика нету\n\nЧтобы добавить используйте /add %s" % (index, index))


# handle '/help' command
@bot.message_handler(commands=['help'])
def command_help(message):
    cid = message.chat.id
    uid = message.from_user.id
    print("[" + str(uid) + "]: /help")
    if uid in const.admins:
        bot.send_message(cid, """
Используйте следующие команды! \n
/start - записаться в журнал 📄
/get - посмотреть журнал 📑
/set - изменить оценки лабараторной 📝
/add <> - добавить в журнал лабараторную <> 🖋
/del - удалить из журнала лабараторную 📉
""")
    else:
        bot.send_message(cid, """
Используйте следующие команды!\n
/start - записаться в журнал 📄
/get - посмотреть журнал 📑
""")


"""
# handle '/re' command
@bot.message_handler(commands=['re'])
def command_re(message):
    bot.remove_webhook()

# handle '/se' command
@bot.message_handler(commands=['se'])
def command_se(message):
    bot.set_webhook(url=const.URL_WEBHOOK)
"""


# handle '/start' command
@bot.message_handler(commands=['start'])
def command_start(message):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    add_glob(message)
    global fname, lname, cid, uid, ct
    print("[" + str(uid) + "]: /start")
    if ct == "none":
        print("Error!!!!")
        bot.send_message(cid, "Меня можно использовать только в группах! ⛔️")
        return "ОШИБОЧКА!"
    n = show_tables(db, cursor)
    if ct in n:
        print("Таблица уже создана!")
        sql = "select id from {} where id=%s".format(ct)
        k = cursor.execute(sql % uid)
        if k == 1:
            print("Юзер уже есть в таблице!")
            bot.send_message(cid, "Ты уже есть в журнале! ⛔️")
        else:
            print("Юзера еще нет в таблице!")
            sql = "insert into {}(id, fname, lname, rating) values(%s, %s, %s, 0)".format(ct)
            cursor.execute(sql, (uid, fname, lname))
            bot.send_message(cid, "%s %s успешно добавлен в журнал! ✅" % (fname, lname))
            db.commit()
            print("Юзер добавлен успешно")
    else:
        print("Таблица еще не создана!")
        # т.к. таблицы нету еще, то и юзр будет записан в нее первым
        # создаем таблицу и записываем юзера туда
        sql = "create table {}(id int(10) not null primary key, fname char(20), lname char(20), rating int(10))".format(ct)
        cursor.execute(sql)
        print("Таблица создана, добавляем юзера")
        sql = "insert into {}(id, fname, lname, rating) values(%s, %s, %s, 0)".format(ct)
        cursor.execute(sql, (uid, fname, lname))
        bot.send_message(cid, "%s %s успешно добавлен в журнал! ✅" % (fname, lname))
        db.commit()
        print("Юзер добавлен успешно")
    # закрываем соединение с базой
    cursor.close()
    db.close()

# handle '/add' ADMIN command
@bot.message_handler(commands=['add'])
def command_add(message):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    add_glob(message)
    global fname, lname, cid, uid, ct
    print("[" + str(uid) + "]: /add")
    if ct == "none":
        print("Error!!!!")
        bot.send_message(cid, "Меня можно использовать только в группах! ⛔️")
        return "ОШИБОЧКА!"
    if uid in const.admins:
        st = show_tables(db, cursor)
        if ct in st:
            sp = re.split(r" ", message.text)
            o = ""
            if len(sp) == 2:
                o = sp[1]
            else:
                bot.send_message(cid, "Используйте /add <>")
                return "Error Synt!!!!"
            n = show_fields(db, cursor)
            if str(o) in n:
                print("Такой столбик уже есть!")
                bot.send_message(cid, "Такой столбик есть! ⛔️")
            else:
                print("Столбика нету, добавим!")
                sql = "alter table {0} add {1} int(5) default 0".format(ct, o)
                cursor.execute(sql)
                bot.send_message(cid, "Столбик %s был успешно добавлен! ✅" % o)
                db.commit()
        else:
            bot.send_message(cid, "Никто еще не писал /start, журнал не создан! ⛔️")
    else:
        bot.send_message(cid, "Не знаю команды '/add'!")
    # закрываем соединение с базой
    cursor.close()
    db.close()

# handle '/del' ADMIN command
@bot.message_handler(commands=['del'])
def command_del(message):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    add_glob(message)
    global fname, lname, cid, uid, ct
    print("[" + str(uid) + "]: /del")
    if ct == "none":
        print("Error!!!!")
        bot.send_message(cid, "Меня можно использовать только в группах! ⛔️")
        return "ОШИБОЧКА!"
    if uid in const.admins:
        st = show_tables(db, cursor)
        if ct in st:
            final("_del", db, cursor)
            if (request != "Error"):
                bot.send_message(cid, "Выберите лабараторную для удаления ❌ ", reply_markup=keyboard)
            else: return request
        else:
            bot.send_message(cid, "Никто еще не писал /start, журнал не создан! ⛔️")
    else:
        bot.send_message(cid, "Не знаю команды '/del'!")
    # закрываем соединение с базой
    cursor.close()
    db.close()

# handle '/set' command
@bot.message_handler(commands=['set'])
def command_set(message):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    add_glob(message)
    global fname, lname, cid, uid, ct, keyboard
    print("[" + str(uid) + "]: /set")
    if ct == "none":
        print("Error!!!!")
        bot.send_message(cid, "Меня можно использовать только в группах! ⛔️")
        return "ОШИБОЧКА!"
    if uid in const.admins:
        st = show_tables(db, cursor)
        if ct in st:
            request = final("_set", db, cursor)
            if(request != "Error"):
                bot.send_message(cid, "Выберите лабараторную для изменения! 🔀", reply_markup=keyboard)
            else: return request
        else:
            bot.send_message(cid, "Никто еще не писал /start, журнал не создан! ⛔️")
    else:
        bot.send_message(cid, "Не знаю команды '/set'!")
    # закрываем соединение с базой
    cursor.close()
    db.close()


# handle '/get' command
@bot.message_handler(commands=['get'])
def command_get(message):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    add_glob(message)
    global fname, lname, cid, uid, ct
    print("[" + str(uid) + "]: /get")
    if ct == "none":
        print("Error!!!!")
        bot.send_message(cid, "Меня можно использовать только в группах! ⛔️")
        return "ОШИБОЧКА!"
    sf = show_fields(db, cursor)
    o = ""
    t = 3
    if len(sf) > 3:
        o = sf[3]
        keyboard.keyboard.clear()
        while t < len(sf):
            btn = telebot.types.InlineKeyboardButton(text="%s" % sf[t], callback_data="%s" % sf[t])
            keyboard.add(btn)
            t += 1
    else:
        bot.send_message(cid, "Лабараторных еще нету ⛔️")
        cursor.close()
        db.close()
        return "ОШИБОЧКА!"
    bot.send_message(cid, "Выберите лабараторную ✅", reply_markup=keyboard)
    # закрываем соединение с базой
    cursor.close()
    db.close()


# callback handle (button check)
@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    db = 0
    db = create_cursor(db)
    cursor = db.cursor()
    data = query.data
    mes = query.message
    global fname, lname, cid, ct, lb
    uid = query.from_user.id
    sf = []
    sf = show_fields(db, cursor)
    if uid in const.admins:
        sql = ""
        delete = what("_del" ,sf)
        sets = what("_set", sf)
        if data == 'one':
            sql = set_lab(1, lb, mes, db, cursor, uid)
        elif data == 'two':
            sql = set_lab(2, lb, mes, db, cursor, uid)
        elif data == 'three':
            sql = set_lab(3, lb, mes, db, cursor, uid)
        elif data == 'four':
            sql = set_lab(4, lb, mes, db, cursor, uid)
        elif data == 'five':
            sql = set_lab(5, lb, mes, db, cursor, uid)
        elif data == 'close':
            bot.delete_message(cid, mes.message_id)
            return "del message"
        elif data in delete:
            t = re.split(r"_", data)
            lb = t[0]
            sql = "alter table {0} drop column {1}".format(ct, t[0])
            complete = bot.send_message(cid, "Столбик %s был успешно удален! ❌ " % t[0])
        elif data in sets:
            t = re.split(r"_", data)
            lb = t[0]
            ocenki(t[0], sf, db, cursor)
            bot.delete_message(cid, mes.message_id)
            return "OK!"
        elif data in sf:
            lb = data
            s = "select fname, lname, %s from %s" % (data, ct)
            cursor.execute(s)
            bot.delete_message(cid, mes.message_id)
            i = 0
            n = []
            name = ""
            for row in cursor:
                n.insert(i, str(i+1) + ". " + str(row[0]) + " " + str(row[1]) + " - " + str(row[2]))
                name += n[i] + "\n"
                i += 1
            bot.send_message(cid, name)
        if sql != "":
            cursor.execute(sql)
            db.commit()
            bot.delete_message(cid, mes.message_id)
        cursor.close()
        db.close()
    else:
        if data in sf:
            lb = data
            s = "select fname, lname, %s from %s" % (data, ct)
            cursor.execute(s)
            bot.delete_message(cid, mes.message_id)
            i = 0
            n = []
            name = ""
            for row in cursor:
                n.insert(i, str(i+1) + ". " + str(row[0]) + " " + str(row[1]) + " - " + str(row[2]))
                name += n[i] + "\n"
                i += 1
            bot.send_message(cid, name)
        cursor.close()
        db.close()
        return "SYNT ERROR!"
