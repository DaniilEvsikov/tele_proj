from aiogram import Bot, Dispatcher, executor, types
import json
import urllib.request
import sqlite3

settingsFile = open("settings.json", encoding="utf-8")
settings = json.load(settingsFile)

bot = Bot(token=settings["token"])
dispatcher = Dispatcher(bot)

isBeginAdding = False
isAdmin = False

adminid = settings["adid"]




def get_weather_user(user: int):
    conn = sqlite3.connect('db/sqlbase_tele.db', check_same_thread=False)
    cursor = conn.cursor()
    print("wr",user)
    for location, in cursor.execute('SELECT location FROM maintabl WHERE user_id = ?', (user,)):
        place=location
    cursor.close()
    return(get_weather(place))

def get_weather(place: str):
    weather = json.loads(urllib.request.urlopen(f'http://api.openweathermap.org/data/2.5/weather?q={place}&units=metric&appid=a15417c7ebe0bcce38f2aabdd96f2549&lang=ru').read())
    return(settings["texts"]["weather"].format(str(weather["name"]), str(weather["main"]["temp"]),
                                                             str(weather["wind"]["speed"]),
                                                             str(weather["weather"][0]["description"])))


def db_table_val(user_id: int, location: str):
    print("start addingg")
    conn = sqlite3.connect('db/sqlbase_tele.db', check_same_thread=False)
    cursor = conn.cursor()
    addin=(user_id, location)
    cursor.execute("INSERT OR REPLACE INTO maintabl (user_id, location) VALUES (?, ?)", addin)
    conn.commit()
    print("ready")
    cursor.close()


#def db_table_val_replace(user_id, location: str):
#    print("start deleting", user_id)
#    dlus=(user_id,)
#    print(dlus)
#    conn = sqlite3.connect('db/sqlbase_tele.db', check_same_thread=False)
#    cursor = conn.cursor()
#    cursor.execute("DELETE FROM maintabl WHERE user_id=?", dlus)
#    conn.commit()
#    print("replacing")
#    cursor.close()
#    db_table_val(user_id, location)

@dispatcher.message_handler(commands=['check'])
async def check(message: types.Message):
    global isAdmin

    print(1)
    usr_id = message.from_user.id
    if (str(usr_id) == str(adminid)):
        isAdmin = True
        print("ready for sending")
        await message.answer("Вы админ. Функции: \n /regular_send рутинная рассылка")
    else:
        isAdmin = False
        print("not ready for sending")
        await message.answer("Вы не админ")


@dispatcher.message_handler(commands=['help'])
async def hellp(message: types.Message):
    await message.answer("Список комманд пользователя: \n /start Начало работы с ботом \n /show_weather Показ текущей погоды в выбраной локации \n /register установление города")


@dispatcher.message_handler(commands=['show_weather'])
async def show(message: types.Message):
    us_id = message.from_user.id
    print("begin",us_id)
    await message.answer(get_weather_user(us_id))
    #await message.answer("Эх dude, во-первых, ты выбрал не зарегестрировался, если хочешь быть крутым на старте, пройди регистрацию по /register")


@dispatcher.message_handler(commands=['regular_send'])
async def check_2(message: types.Message):
    global isAdmin
    if isAdmin:

        conn = sqlite3.connect('db/sqlbase_tele.db', check_same_thread=False)
        cursor = conn.cursor()
        print(1)
        userlist=[]
#        for row in cursor.execute('SELECT location from maintabl'):
#            print(1)
#            print(get_weather(*row))
        for user in cursor.execute('SELECT user_id from maintabl'):
            print(1)
            print(*user)
            userlist.append(user)
        for user_id in userlist:
            await bot.send_message(*user_id, get_weather_user(*user_id))
        cursor.close()


@dispatcher.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Давайте начнём с регистрации /register")


@dispatcher.message_handler(commands=['register'])
async def start(message: types.Message):
    global isBeginAdding

    await message.answer("Введите город в котором вы проживаете (на английском. Примеры: Moscow, Berlin)")
    isBeginAdding = True


@dispatcher.message_handler()
async def adding_city(message: types.Message):
    global isBeginAdding

    if isBeginAdding:
        isBeginAdding = False
        input_txt = message.text
        try:
            us_id = message.from_user.id
            location = input_txt
            print(us_id, location)
            try:
                await message.answer(get_weather(location))
            except:
                await message.answer('Введённого города не существует, или вы его неправильно вписали. Бывает.')
                return()
            db_table_val(user_id=us_id, location=location)

        except:
            pass



if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)

