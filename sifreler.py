import hashlib , hmac
from datetime import datetime
import requests
import telebot
import json
import time

telegram_chat_id = 5536977745

TELEGRAM_API_KEY1 = '6197528258:AAEb8-6_iuW1z7_tTsUBejj-H7e-_Lkn_Es'
tbot_genel = telebot.TeleBot(TELEGRAM_API_KEY1)

TELEGRAM_API_KEY2 = '6030385999:AAF6VgYmhQlc948iMHgSjNWp52XBaBteM6A'
tbot_ozel = telebot.TeleBot(TELEGRAM_API_KEY2)

# key ve secret key girilmesi
def gen_sign(method, url, query_string=None, payload_string=None):
    key = '26b35f7512bf529458763bb357ad9078'
    secret = '20055569d1097c71dbc636b9295f9a2dbc69128d8e048aa1cf93494d7b4ab0b1'

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

