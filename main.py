import telebot
import time
import sqlite3 as sq
from telebot import types

bot = telebot.TeleBot('')


user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    conn = sq.connect('mood.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS mood(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day INTEGER,
        month INTEGER,  
        year INTEGER,
        mood TEXT)''')
    conn.commit()
    cur.close()
    conn.close()
    
    keyboard = types.InlineKeyboardMarkup()
    key_all=types.InlineKeyboardButton(text='Все записи',callback_data='all')
    key_cont = types.InlineKeyboardButton(text='Продолжить',callback_data='continue')
    keyboard.add(key_cont,key_all)
    bot.send_message(message.chat.id, 'Привет, это трекер настроения. Нажмите кнопку, чтобы продолжить,или глянь все записи', reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data == 'all')
def callback_all(call):
    bot.answer_callback_query(call.id)
    conn = sq.connect('mood.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM mood")
    records = cur.fetchall()
    conn.close()
    if not records:
        bot.send_message(call.message.chat.id,"Похоже записей нет")
        return
    message_text='Ваши записи: '
    for records in records:
        message_text+= f'{records[1]}.{records[2]}.{records[3]}:{records[4]}\n'
    bot.send_message(call.message.chat.id,message_text)
    
        
  

@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def callback_worker(call):
    msg = bot.send_message(call.message.chat.id, 'Введите число дня (от 1 до 31):')
    bot.register_next_step_handler(msg, process_day)
    bot.answer_callback_query(call.id)

def process_day(message):
    try:
        day = int(message.text)
        if 1 <= day <= 31:
            
            user_data[message.chat.id] = {'day': day}
            
            
            keyboard = types.InlineKeyboardMarkup()
            key_month = types.InlineKeyboardButton(text='Месяц', callback_data='month')
            keyboard.add(key_month)
            
            bot.send_message(
                message.chat.id, 
                f'День {day} сохранен. Нажмите кнопку "Месяц"', 
                reply_markup=keyboard
            )
        else:
            bot.send_message(message.chat.id, 'Число должно быть от 1 до 31!')
            bot.register_next_step_handler(message, process_day)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число!')
        bot.register_next_step_handler(message, process_day)

@bot.callback_query_handler(func=lambda call: call.data == 'month')
def month_callback(call):
    msg = bot.send_message(call.message.chat.id, 'Введите месяц (1-12):')
    bot.register_next_step_handler(msg, process_month)
    bot.answer_callback_query(call.id)

def process_month(message):
    try:
        month = int(message.text)
        if 1 <= month <= 12:
            
            user_data[message.chat.id]['month'] = month
            
           
            msg = bot.send_message(message.chat.id, 'Введите год:')
            bot.register_next_step_handler(msg, process_year)
        else:
            bot.send_message(message.chat.id, 'Месяц должен быть от 1 до 12!')
            bot.register_next_step_handler(message, process_month)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите число!')
        bot.register_next_step_handler(message, process_month)

def process_year(message):
    try:
        year = int(message.text)
        
        user_data[message.chat.id]['year'] = year
        
       
        msg = bot.send_message(message.chat.id, 'Опишите ваше настроение:')
        bot.register_next_step_handler(msg, save_mood)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введите год цифрами!')
        bot.register_next_step_handler(message, process_year)

def save_mood(message):
   
    data = user_data.get(message.chat.id, {})
    mood = message.text
    
    
    conn = sq.connect('mood.db')
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO mood(day, month, year, mood) VALUES (?, ?, ?, ?)',
        (data.get('day'), data.get('month'), data.get('year'), mood)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    bot.send_message(
        message.chat.id,
        f'Сохранено!\nДата: {data.get("day")}.{data.get("month")}.{data.get("year")}\nНастроение: {mood}'
    )
    
    
    user_data.pop(message.chat.id, None)
    


    
        




while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f'Ошибка: {e}')
        time.sleep(15)






    







            
        

        
