import telebot
from telebot import types
import time
import pymysql

db = pymysql.connect("localhost","root","1",db='test')
cursor = db.cursor()
TOKEN = <YOU_TOKEN>

def listener(messages):
    """
	Слушаем команды и пишем в логи
"""
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener
TIME_DEL_MESSAGE = 15


# handle the "/start" command
@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    #complete = bot.send_message(cid, "Сканирование завершено!")
    chatTitle = bot.get_chat(cid)
	# если таблицы нет, создаем и добавляем юзера
    try:
        sql = 'create table %s(id int(10) not null primary key, first_name char(20), last_name char(20), rating int(5))' % chatTitle.title
        cursor.execute(sql)
        print("Table [ %s ] created!" % chatTitle.title)
        sql = "insert into {} (id, first_name, last_name, rating) values (%s, %s, %s, %s)".format(chatTitle.title)
        cursor.execute(sql, (m.from_user.id, m.from_user.first_name, m.from_user.last_name, 0))
        print(sql % (m.from_user.id, m.from_user.first_name, m.from_user.last_name, 0))
        db.commit()
        print("%s %s успешно добавлен в журнал" % (m.from_user.first_name, m.from_user.last_name))
        mes = bot.send_message(cid, "%s %s успешно добавлен в журнал" % (m.from_user.first_name, m.from_user.last_name))
        time.sleep(TIME_DEL_MESSAGE)
        bot.delete_message(cid, mes.message_id)
        #bot.delete_message(cid, complete.message_id)
	# если таблица есть, просто добавляем юзера
    except:
		# если ид нет в таблице, добавляем в базу
        try:
            sql = "insert into {} (id, first_name, last_name, rating) values (%s, %s, %s, %s)".format(chatTitle.title)
            cursor.execute(sql, (m.from_user.id, m.from_user.first_name, m.from_user.last_name, 0))
            print(sql % (m.from_user.id, m.from_user.first_name, m.from_user.last_name, 0))
            db.commit()
            print("%s %s успешно добавлен в журнал" % (m.from_user.first_name, m.from_user.last_name))
            mes = bot.send_message(cid, "%s %s успешно добавлен в журнал" % (m.from_user.first_name, m.from_user.last_name))
            time.sleep(TIME_DEL_MESSAGE)
            bot.delete_message(cid, mes.message_id)
            #bot.delete_message(cid, complete.message_id)
		# если ид есть в базе, то говорим про это
        except:
            mes = bot.send_message(cid, "Ты уже есть в журнале этой группы!")
            time.sleep(TIME_DEL_MESSAGE)
            bot.delete_message(cid, mes.message_id)
            #bot.delete_message(cid, complete.message_id)
            print("[%s] %s %s уже есть в таблице %s" % (m.from_user.id, m.from_user.first_name, m.from_user.last_name, chatTitle.title))
	# непонятно что, но пусть побудет пока что
    try:
        sql = 'select * from wtfTable'
        cursor.execute(sql)
        print(sql)
    except:
        print("Зачем? Но пусть пока будет!")

# handle the "/get" command
@bot.message_handler(commands=['get'])
def command_get_list(m):
    i = 0
    n = []
    cid = m.chat.id
    chatTitle = bot.get_chat(cid)
    name = "Журнал группы {}\n\n".format(chatTitle.title)
    count = cursor.execute('select count(*) from {}'.format(chatTitle.title))
    all = 'select first_name, last_name from {}'.format(chatTitle.title)
    cursor.execute(all)
    for row in cursor:
        n.insert(i, str(i+1) + '. ' + row[0] + ' ' + row[1] + "\n")
        name += n[i]
        i += 1
    delet = bot.send_message(cid, name)
    time.sleep(TIME_DEL_MESSAGE)
    bot.delete_message(cid,delet.message_id)
    print("Количество строк в базе [%s] - %s\nRezult name array: {\n%s}" % (chatTitle.title, count, name))


# handle the "/set" ADMIN command
@bot.message_handler(commands=['set'])
def command_set_list(m):
    if (m.from_user.id == <ADMINID>) | (m.from_user.id == <ADMINID>):
        cid = m.chat.id
        chatTitle = bot.get_chat(cid)
        i = 0
        n = []
        sel = 'select first_name, last_name from {}'.format(chatTitle.title)
        cursor.execute(sel)
		# Берем выборку с базы и проставлям всем оценки (будут кнопки)
    else:
        bot.send_message(m.chat.id, "Не понимаю команды '/set'!")


# handle the press button callback
@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    print(query)
	
	
bot.polling()