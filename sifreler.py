import hashlib , hmac
from datetime import datetime
import requests
import telebot
import json
import time

telegram_chat_id = 675290340

TELEGRAM_API_KEY1 = '5262142568:AAEgoWC3f7PAsHhMr5QENw4k7wKPMRJo794'
tbot_genel = telebot.TeleBot(TELEGRAM_API_KEY1)

TELEGRAM_API_KEY2 = '5036185619:AAHOB2hLEaz1NDHfK6OBxqQZfiPUPqfj2fw'
tbot_ozel = telebot.TeleBot(TELEGRAM_API_KEY2)

# key ve secret key girilmesi
def gen_sign(method, url, query_string=None, payload_string=None):
    key = '271a6cf852703f7dd115beb53ce5a56b'
    secret = '805d188cc47713286794cc827dd2594d9f665d48bf7c6e30386e636bb90d2157'

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}

