#from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from conf import TOKEN, DB_NAME
from sqlite_db import DBHelper

from googletrans import Translator
import requests
import datetime
#import time
translator = Translator(service_urls=['translate.googleapis.com'])

BTN_TODAY, BTN_WEEKS, BTN_10days,  BTN_REGION = ('Bugun', 'Haftalik', '10 kunlik', '🇺🇿 Mintaqa')



STATE_REGION = 1
STATE_CALENDAR = 2
db = DBHelper(DB_NAME)
user_region = dict()


main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY], [BTN_WEEKS , BTN_10days ],[BTN_REGION]
], resize_keyboard=True)




def region_buttons():
    # regions = {1: 'Andijon viloyati', 2: 'Buxoro viloyati', 3: 'Fargʻona viloyati', 4: 'Jizzax viloyati',
    #            5: 'Xorazm viloyati', 6: 'Namangan viloyati', 7: 'Navoiy viloyati', 8: 'Qashqadaryo viloyati',
    #            9: 'Qoraqalpogʻiston Respublikasi', 10: 'Samarqand viloyati', 11: 'Sirdaryo viloyati',
    #            12: 'Surxondaryo viloyati',
    #            13: 'Toshkent viloyati', 14: 'Toshkent shahar'}
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons
        #print(key, region)


def start(update, context):
    user = update.message.from_user
    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_html ("Assalomu alaykum <b>{}!</b>\n \n<b>Ob-havo ma'lumotlari bilan tanishing</b> "
                               "\n \n Sizga qaysi mintaqa bo'yicha ma'lumot kerak".format(user.first_name),
                               reply_markup= InlineKeyboardMarkup(buttons))
    return STATE_REGION
def inline_callback(update, context):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        user_region[user_id] = int(query.data)
        query.message.delete()
        query.message.reply_html(text='<b>Ob-havo ma`lumotlari </b>2️⃣0️⃣2️⃣1️⃣ \n\n Quyidagilardan birini '
                                      'tanlang 👇',
                                reply_markup=main_buttons)
        # query.edit_message_text(text='<b>Ob-havo ma`lumotlari </b>2️⃣0️⃣2️⃣1️⃣ \n\n Quyidagilardan birini tanlang 👇',
        #                         parse_mode="HTML", reply_markup=main_buttons)

        return STATE_CALENDAR
    except Exception as e:
        print('error', str(e))

def calendar_today(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region_eng(region_id)
        print(region['name_eng'])
        #today = str(datetime.now().date())
        today = str(datetime.date.today())
        print(today)
        city = region['name_eng']
        api = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=c9627bc3eed2016b8724d57604f4dbe9"

        json_data = requests.get(api).json()
        condition = json_data['weather'][0]['main']
        print(condition)
        temp = int(json_data['main']['temp'] - 273.15)
        min_temp = int(json_data['main']['temp_min'] - 273.15)
        max_temp = int(json_data['main']['temp_max'] - 273.15)
        pressure = json_data['main']['pressure']
        humidity = json_data['main']['humidity']
        wind = json_data['wind']['speed']
        # sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
        # sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))
        #translated_text = translator.translate(condition, dest="uz")
        #print(translated_text.text)
        final_info = str(condition) + "\n" + str(temp) + "°C"
        print(final_info)
        final_data = "\n" + "past temperatura: " + str(min_temp) + "°C" + "\n" + "baland temperatura: " + str(
            max_temp) + "°C" + "\n" + "Bosim: " + str(pressure) + "\n" + "Namlik: " + str(
            humidity) + "\n" + "Shamol tezligi: " + str(wind) #+ "\n" + "Quyosh chiqishi: " + sunrise + "\n" + "Quyosh botishi: " + sunset
        if json_data['weather'][0]['main'] =='Rain':
            update.message.reply_html('<b>Bugungi {}ning</b>\nob-havosi bilan tanishing:\n{}\n{} 🌧🌧🌧 {}'.format(
                 region['name'], today, final_info, final_data))
        elif json_data['weather'][0]['main'] == 'Clouds':
            update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}\n{} ☁☁☁ \n{}'.format(
                 region['name'],today, final_info, final_data))
        elif json_data['weather'][0]['main'] == 'Snow':
            update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}\n{} 🌨🌨🌨 \n{}'.format(
                 region['name'], today, final_info, final_data))
        elif json_data['weather'][0]['main'] == 'Clear':
            update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}  🌤🌤🌤 {}\n{}'.format(
                 region['name'], today, final_info, final_data))
        else:
            update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}\n{}\n{}'.format(
                 region['name'], today, final_info, final_data))
        print(region['name'])


    except Exception as e:
        print('Error ', str(e))

def calendar_tomorrow(update, context):

    update.message.reply_text('Ertaga belgilandi')

def calendar_weeks(update, context):
    try:
        user_id = update.message.from_user.id
        if not user_region[user_id]:
            return STATE_REGION
        region_id = user_region[user_id]
        region = db.get_region_eng(region_id)
        print(region['name_eng'])
        #today = datetime.now().date()
        #today = datetime.date.today() + datetime.timedelta(days=1)

        city = region['name_eng']
        api = "http://api.openweathermap.org/data/2.5/forecast/daily?q="+city+"&cnt=7&appid=c9627bc3eed2016b8724d57604f4dbe9"

        #api = "http://api.openweathermap.org/data/2.5/forecast?q=" + city + "&appid=c9627bc3eed2016b8724d57604f4dbe9"
        json_data = requests.get(api).json()
        print(json_data)
        vec = []

        for i in json_data['list']:
            # print(i['weather'])
            for jj in i['weather']:
                print(jj['main'])
                vec.append(jj['main'])
        # condition = json_data['weather'][0]['main']
        # print(condition)
        aa = []
        iqlim = 0
        for i in json_data['list']:
            today = datetime.date.today() + datetime.timedelta(days=iqlim)
            #print(i['temp']['day'])
            aa.append(i['temp'])
            update.message.reply_html('<b>Bir haftalik {}ning ob-havosi bilan tanishing:</b>\n{}\n{}\nErtalab: {}°C\nKunduzi: {}°C\nKechasi: {}°C'.format(
            region['name'],today, vec[iqlim], int(i['temp']['morn']-273.15), int(i['temp']['day'] - 273.15),int(i['temp']['night']-273.15) ))

            iqlim+=1
        #print([day['day'] for day in aa])
        # bb = type(json_data['list'])
        # jj = 0
        # for i in json_data['list']:
        #     if jj == 5:
        #         break
        #     else:
        #         print(i['weather'][0]['main'])
        #     jj+=1
        # print(jj)
        # condition = json_data['weather'][0]['main']
        # print(condition)
        # temp = int(json_data['main']['temp'] - 273.15)
        # print(temp)
        # min_temp = int(json_data['main']['temp_min'] - 273.15)
        # max_temp = int(json_data['main']['temp_max'] - 273.15)
        # pressure = json_data['main']['pressure']
        # humidity = json_data['main']['humidity']
        # wind = json_data['wind']['speed']
        # sunrise = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunrise'] - 21600))
        # sunset = time.strftime('%I:%M:%S', time.gmtime(json_data['sys']['sunset'] - 21600))
    #     translated_text = translator.translate(condition, dest="uz")
    #     print(translated_text.text)
    #     final_info = str(translated_text.text) + "\n" + str(temp) + "°C"
    #     print(final_info)
    #     final_data = "\n" + "past temperatura: " + str(min_temp) + "°C" + "\n" + "baland temperatura: " + str(
    #         max_temp) + "°C" + "\n" + "Bosim: " + str(pressure) + "\n" + "Namlik: " + str(
    #         humidity) + "\n" + "Shamol tezligi: " + str(wind) #+ "\n" + "Quyosh chiqishi: " + sunrise + "\n" + "Quyosh botishi: " + sunset
    #     if json_data['weather'][0]['main'] =='Rain':
    #         update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{} 🌧🌧🌧 {}'.format(
    #             region['name'], final_info, final_data))
    #     elif json_data['weather'][0]['main'] == 'Clouds':
    #         update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{} ☁☁☁  {}'.format(
    #             region['name'], final_info, final_data))
    #     elif json_data['weather'][0]['main'] == 'Snow':
    #         update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}  🌨🌨🌨 {}'.format(
    #             region['name'], final_info, final_data))
    #     elif json_data['weather'][0]['main'] == 'Clear':
    #         update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}  🌤🌤🌤 {}'.format(
    #             region['name'], final_info, final_data))
    #     else:
    #         update.message.reply_html('<b>Bugungi {}ning</b>\n ob-havosi bilan tanishing:\n{}{}'.format(
    #             region['name'], final_info, final_data))
    #     print(region['name'])
    #
    #
    except Exception as e:
        print('Error ', str(e))
    #update.message.reply_text('Haftalik iqlim belgilandi')

def select_region(update, context):
    buttons = region_buttons()
    update.message.reply_text('Sizga qaysi mintaqa bo`yicha ma`lumot kerak?',
                              reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION 


def main():
    updater = Updater(TOKEN, use_context=True)

    #Dispatcher eventlarni aniqlash uchun
    dispatcher = updater.dispatcher
    #start komandasini ushlab qolish
    #dispatcher.add_handler(CommandHandler('start', start))

    #inline button query
    #dispatcher.add_handler(CallbackQueryHandler(inline_callback ))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [CallbackQueryHandler(inline_callback )],
            STATE_CALENDAR:[
                MessageHandler(Filters.regex('^('+BTN_TODAY+')$'), calendar_today),
                MessageHandler(Filters.regex('^('+BTN_10days+')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^('+BTN_WEEKS+')$'), calendar_weeks),
                MessageHandler(Filters.regex('^('+BTN_REGION+')$'), select_region)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

main()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
