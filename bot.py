import telebot
from telebot import types
from timetable import *

token = ''
bot = telebot.TeleBot(token)
dataBaseChats = {}

def bot_start(chat_id):
    global dataBaseChats

    chat_data = {
        'listClass': [],
        'listSymbol': [],
        'listGroup': [],
        'listDays': [],
        'parClass': -1,
        'parSymbol': '',
        'parGroup': -1,
        'parDay': '',
        }

    dataBaseChats[chat_id] = chat_data

def setParClass(chat_id, value):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    dataBaseChats[chat_id]['parClass'] = value
    dataBaseChats[chat_id]['parSymbol'] = ''
    dataBaseChats[chat_id]['parGroup'] = -1
    dataBaseChats[chat_id]['parDay'] = ''

def getParClass(chat_id):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    return dataBaseChats[chat_id]['parClass']

def setParSymbol(chat_id, value):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    dataBaseChats[chat_id]['parSymbol'] = value
    dataBaseChats[chat_id]['parGroup'] = -1
    dataBaseChats[chat_id]['parDay'] = ''
    
def getParSymbol(chat_id):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    par = dataBaseChats[chat_id]['parSymbol']
    return par.upper()

def setParGroup(chat_id, value):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    dataBaseChats[chat_id]['parGroup'] = value
    dataBaseChats[chat_id]['parDay'] = ''
    
def getParGroup(chat_id):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    return dataBaseChats[chat_id]['parGroup']

def setParDay(chat_id, value):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    dataBaseChats[chat_id]['parDay'] = value
    
def getParDay(chat_id):
    if not chat_id in dataBaseChats: bot_start(chat_id)
    return dataBaseChats[chat_id]['parDay']

# Получить список классов
def getListClass(chat_id):
    listClass = []

    parClass = str(getParClass(chat_id))
    parSymbol = getParSymbol(chat_id)
    parGroup = str(getParGroup(chat_id))
    
    if parClass == -1 or parSymbol == '' or parGroup == -1:
        bot_start(chat_id)

    for key in timeTable:
        valueClass, valueSymbol, valueGroup = key.split()
        if not int(valueClass) in listClass: listClass.append(int(valueClass))

    listClass.sort()

    dataBaseChats[chat_id]['listClass'] = listClass
    
    return dataBaseChats[chat_id]['listClass']

# Получить список букв для классов
def getListSymbol(chat_id):
    listSymbol = []

    for key in timeTable:
        valueClass, valueSymbol, valueGroup = key.split()
        if int(valueClass) == getParClass(chat_id) and not valueSymbol.lower() in listSymbol: listSymbol.append(valueSymbol.lower())

    listSymbol.sort()

    dataBaseChats[chat_id]['listSymbol'] = listSymbol
    
    return dataBaseChats[chat_id]['listSymbol']

# Получить список подгрупп
def getListGroup(chat_id):
    listGroup = []

    for key in timeTable:
        valueClass, valueSymbol, valueGroup = key.split()
        if int(valueClass) == getParClass(chat_id) and valueSymbol.upper() == getParSymbol(chat_id) and (not int(valueGroup) in listGroup):
            listGroup.append(int(valueGroup))
        
    listGroup.sort()

    dataBaseChats[chat_id]['listGroup'] = listGroup
    
    return dataBaseChats[chat_id]['listGroup']

def getListDays(chat_id):
    listDays = []
    
    parClass = str(getParClass(chat_id))
    parSymbol = getParSymbol(chat_id)
    parGroup = str(getParGroup(chat_id))
    
    if parClass == -1 or parSymbol == '' or parGroup == -1:
        return listDays

    key = parClass + ' ' + parSymbol + ' ' + parGroup
    for key in timeTable[key]:
        if (not key in listDays):
            listDays.append(key)
        
    dataBaseChats[chat_id]['listDays'] = listDays
    
    return dataBaseChats[chat_id]['listDays']

def getTimetable(key, day):
    result = ''
    data = timeTable[key][day]
    
    for i in range(len(data)):
        stNumber = str(i + 1)
        stTime = lessonTimes[i + 1]
        stLesson = data[i][0]
        if data[i][1] != '':
            stRoom = ' (' + data[i][1] + ')'
        else:
            stRoom = ''
        
        if stLesson == '':
            stLesson = 'нет'
            stRoom = ''
            
        result += stNumber + '. ' + stTime + ' - ' + stLesson.lower() + stRoom + '\n'
    
    return result


@bot.message_handler(commands=['start'])
def start_message(message):
    bot_start(message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for parClass in getListClass(message.chat.id):
        item = types.KeyboardButton(parClass)
        markup.add(item)

    text = 'Вас приветствует бот расписания 1511!\n\nЯ могу выполнять прямые запросы, например "9 В 2"\n\nВыберите класс:'
    
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(content_types='text')
def message_reply(message):
    chat_id = message.chat.id
    
    line = message.text

    if line == 'Другой день': setParDay(chat_id, '')
    if line == 'Другая группа': setParGroup(chat_id, -1)
    if line == 'Другая буква': setParSymbol(chat_id, '')
    if line == 'Другой класс': bot_start(chat_id)

    lineEdit = ''
    # Удаление лишних символов
    for s in line:
        if s.isalpha() or s.isdigit(): lineEdit += s
        else: lineEdit += ' '

    lineEdit = lineEdit.strip() # Удаляет начальные и конечные пробелы
    lineEdit = lineEdit.lower() # Перевод строки в нижний регистр
    words = lineEdit.split() # Преобразование строки в список слов
    
    for word in words:
        if word.isnumeric() and int(word) in getListClass(chat_id):
            setParClass(chat_id, int(word))
        elif word.isalpha() and word in getListSymbol(chat_id):
            setParSymbol(chat_id, word)
        elif word.isnumeric() and int(word) in getListGroup(chat_id):
            setParGroup(chat_id, int(word))
        elif word.isalpha():
            for key in daysWeek:
                if word == daysWeek[key] and key in getListDays(chat_id):
                    setParDay(chat_id, key)

    parClass = getParClass(chat_id)
    parSymbol = getParSymbol(chat_id)
    parGroup = getParGroup(chat_id)
    parDay = getParDay(chat_id)

    if parClass == -1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        for n in getListClass(chat_id):
            item = types.KeyboardButton(str(n))
            markup.add(item)
        
        bot.send_message(chat_id, 'Выберите класс:', reply_markup=markup)
        
    elif parSymbol == '':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for st in getListSymbol(chat_id):
            item = types.KeyboardButton(st.upper())
            markup.add(item)

        markup.add(types.KeyboardButton('Другой класс'))
        bot.send_message(chat_id, 'Выберите букву:', reply_markup=markup)
        
    elif parGroup == -1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for n in getListGroup(chat_id):
            item = types.KeyboardButton(str(n))
            markup.add(item)

        markup.add(types.KeyboardButton('Другая буква'))
        markup.add(types.KeyboardButton('Другой класс'))
        bot.send_message(chat_id, 'Выберите группу:', reply_markup=markup)
        
    elif parDay == '':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for day in getListDays(chat_id):
            item = types.KeyboardButton(daysWeek[day].capitalize())
            markup.add(item)

        markup.add(types.KeyboardButton('Другая группа'))
        markup.add(types.KeyboardButton('Другая буква'))
        markup.add(types.KeyboardButton('Другой класс'))
        bot.send_message(chat_id, 'Выберите день недели:', reply_markup=markup)
        
    else:
        key = str(parClass) + ' ' + parSymbol + ' ' + str(parGroup)
        text = 'Расписание для ' + key + ' (' + daysWeek[parDay] + '):\n\n' + getTimetable(key, parDay)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton('Другой день'))
        markup.add(types.KeyboardButton('Другая группа'))
        markup.add(types.KeyboardButton('Другая буква'))
        markup.add(types.KeyboardButton('Другой класс'))
        bot.send_message(chat_id, text, reply_markup=markup)
        

bot.infinity_polling()
