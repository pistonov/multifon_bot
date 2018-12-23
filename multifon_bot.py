#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, re, xml.etree.ElementTree, datetime, time
import telepot
from telepot.loop import MessageLoop

# -- SETUP CONFIG -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

PHONE = "79261111111"  # Номер телефона
PASSWD = "SUpErPaSS"  # Пароль в системе Мультифон

TG_TOKEN = "1234567890:FHhfFHdjJFhfJFhdJFnvJFnvJFDHDSSADS"  # Ключ telegram бота
TG_ID = "1234567"  # ID пользователя telegram

# -- END SETUP CONFIG -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

TelegramBot = telepot.Bot(TG_TOKEN)

regexfloat = re.compile(r'^[-][0-9]+[.,][0-9]+|^[0-9]+[.,][0-9]+')
RM = ['GSM', 'SIP']


def balance():

    balance_url = "https://sm.megafon.ru/sm/client/balance?login=" + str(PHONE) + "@multifon.ru&password=" + str(PASSWD)

    try:
        r = requests.get(balance_url)
        response = xml.etree.ElementTree.fromstring(r.content)
        response_code = response[0][0].text
    except Exception as e:
        return False

    if response_code == "200":
        balance = response[1].text
        if balance and regexfloat.search(balance):
            return float(balance.split('\n', 1)[0])
        else:
            return False
    else:
        return False


def route_get():

    route_get_url = "https://sm.megafon.ru/sm/client/routing?login=" + str(PHONE) + "@multifon.ru&password=" + str(PASSWD)

    try:
        r = requests.get(route_get_url)
        response = xml.etree.ElementTree.fromstring(r.content)
        response_code = response[0][0].text
    except Exception as e:
        return False

    if response_code == "200":
        route = response[1].text
        return int(route.split('\n', 1)[0])
    else:
        return False


def route_set(route):

    route_set_url = "https://sm.megafon.ru/sm/client/routing/set?login=" + str(PHONE) + "@multifon.ru&password=" + str(PASSWD) + "&routing=" + str(route)
    try:
        r = requests.post(route_set_url)
        response = xml.etree.ElementTree.fromstring(r.content)
        response_code = response[0][0].text
    except Exception as e:
        return False

    if response_code == "200":
        return True
    else:
        return False


def handle(msg):
    try:
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            return

        chat_id = msg['chat']['id']

        if chat_id == TG_ID:
            commandfull = msg['text'].strip().lower()
            command = commandfull.split('@')[0]

            if command == '/status':
                balance = balance()
                if isinstance(balance, float):
                    balance = "Баланс- " + str(balance)
                else:
                    balance = "Не удалось получить баланс."

                route_get = route_get()
                if isinstance(route_get, int):
                    route_get = "Маршрут через " + RM[int(route_get)]
                else:
                    route_get = "Не удалось получить данные о маршруте."

                report_msg = str(balance) + '\n' + str(route_get)
                TelegramBot.sendMessage(chat_id, report_msg)

            if command == '/sip_on':
                if route_set(2) <> False:
                TelegramBot.sendMessage(chat_id, "Маршрут изменен на SIP")

            if command == '/sip_off':
                if route_set(0) <> False:
                TelegramBot.sendMessage(chat_id, "Маршрут изменен на GSM")

    except Exception as e:
        return False
# -----------------------------------------------------------

def main():
    MessageLoop(TelegramBot, handle).run_as_thread()
    while True:
        time.sleep(30)

if __name__ == '__main__':
    print "Multifon_bot started"
    main()
