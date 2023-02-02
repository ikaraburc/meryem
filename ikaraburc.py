import requests
from prettytable import PrettyTable
from requests.exceptions import ConnectionError

from sifreler import *


def emirleri_sil():
    # coding: utf-8
    import requests

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/orders'
    query_param = 'side=buy'
    # for `gen_sign` implementation, refer to section `Authentication` above
    sign_headers = gen_sign('DELETE', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('DELETE', host + prefix + url + "?" + query_param, headers=headers)


def son_coin():
    # emirleri listele
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/my_trades'
    query_param = ""

    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)

    while True:
        try:
            r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
        except ConnectionError as e:  # This is the correct syntax
            print(e)
            time.sleep(1)
            r = "Nothing"
            continue
        except ValueError:
            print("Gelen Dosya Json değil...")
            r = "Nothing"
            continue
        except KeyError:
            print("Key error hatası veriyor")
            r = "Nothing"
            continue
        if r != "Nothing":
            break
        else:
            print("Bağlantı bekleniyor...")
            continue
    global scoin
    scoin = r[0]["currency_pair"]

def pazar_gecmisi(bulunan):
    import requests
    t = int(time.time() - 30 * 60)

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/trades'
    query_param = 'currency_pair=' + str(bulunan) + "&from=" + str(t)
    r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()

    global palim
    palim = sum([float(i["price"]) * float(i["amount"]) for i in r if i["side"] == "buy"])


def tc_fiyatlar():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/tickers'
    data = requests.request('GET', host + prefix + url, headers=headers).json()

    global coins, prices1, hacim, bulunanlar

    tekli = []
    bulunanlar = ["abc", "abcd"]

    for i in range(len(data)):
        if "_USDT" in data[i]["currency_pair"] \
                and "3S" not in data[i]["currency_pair"] \
                and "3L" not in data[i]["currency_pair"] \
                and "5S" not in data[i]["currency_pair"] \
                and "5L" not in data[i]["currency_pair"] \
                and float(data[i]["last"]) > 0 \
                and float(data[i]["low_24h"]) > 0 \
                and float(data[i]["quote_volume"]) > 80000:
            tekli.append([data[i]["currency_pair"], float(data[i]["last"])])
    toplu.append(tekli)


def tc_degisim():
    global bulunan, bul_oran, ytablo, bti

    ytablo = PrettyTable()
    ytablo.clear()

    prices2 = []
    changes = []

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/tickers'
    data = requests.request('GET', host + prefix + url, headers=headers).json()

    for x in range(len(toplu[0])):
        for y in data:
            if toplu[0][x][0] == y['currency_pair']:
                prices2.append(float(y['last']))

    for i in range(len(toplu[0])):
        changes.append(round(((prices2[i] / toplu[0][i][1]) - 1) * 100, 2))

    bti = changes.index(max(changes))
    bulunan = toplu[0][bti][0]
    bul_oran = changes[bti]
    print(len(toplu[0]), " coinden yukselen= ", bulunan, " % ", bul_oran, " fiyat = ", prices2[bti])

    ao = 10

    if abs(changes[bti]) >= ao:

        bulunanlar.append(bulunan)

        ytablo.field_names = [str(bulunan), str("% " + str(bul_oran))]
        ytablo.add_row(["Yeni Fiyat", prices2[bti]])
        ytablo.add_row(["Eski Fiyat", toplu[0][bti][1]])

        if len(bulunanlar) > 5:
            bulunanlar.pop(0)

        tbot_genel.send_message(telegram_chat_id, str(ytablo))
        tbot_genel.send_message(telegram_chat_id, str("https://www.gate.io/tr/trade-old/" + str(bulunan)))
        
        for i in toplu:
            for y in i:
                if y[0] == bulunan:
                    i.remove(y)


class coin_trader:
    def __init__(self, coin):
        self.coin = coin

    def coin_digit(self):
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/currency_pairs/' + self.coin
        query_param = ''

        while True:
            try:
                r = requests.request('GET', host + prefix + url, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

        global digit, mdigit, coin_adi, coin_birimi
        coin_adi, coin_birimi = str(self.coin).split("_")
        
        if "label" in r:
            print("Böyle bir coin yok....")
        else:
            digit, mdigit = int(r["precision"]), int(r["amount_precision"])

    def coin_fiyat(self):

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/tickers'
        query_param = 'currency_pair=' + str.upper(self.coin)

        while True:
            try:
                r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

        global cp, c24, tepe24, k

        cp, tepe24, c24 = float(r[0]["last"]), float(r[0]["high_24h"]), float(r[0]["change_percentage"])

        k = 1 / 10 ** digit
        if (cp + k) / cp >= 1.01:
            k = 0

    def bakiye_getir(self):

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/accounts'
        query_param = ''
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('GET', host + prefix + url, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            except KeyError:
                print("Key error hatası veriyor")
                r = "Nothing"
            if r != "Nothing" or r["label"] not in r:
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

        # print(r)
        global cam, ctm, usdt_to, usdt_av, mulk, ceder

        eldeki_mal = list(filter(lambda coin: coin['currency'] == str.upper(coin_adi), r))
        eldeki_usdt = list(filter(lambda coin: coin['currency'] == 'USDT', r))

        if len(eldeki_mal) > 0:
            cam, clm = float(eldeki_mal[0]["available"]), float(eldeki_mal[0]["locked"])
        else:
            cam, clm = 0, 0

        usdt_av, usdt_lo = float(eldeki_usdt[0]["available"]), float(eldeki_usdt[0]["locked"])

        usdt_to = usdt_av + usdt_lo
        ctm = cam + clm
        ceder = ctm * cp
        mulk = usdt_to + ceder

    def tahta_getir(self):

        # alım satım orderbook derinliğini gör
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/order_book'
        query_param = "".join(['currency_pair=', str(self.coin).upper(), "&limit=25"])

        while True:
            try:
                r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            except KeyError:
                print("Key error hatası veriyor")
                r = "Nothing"

            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

        global fbids, fasks, mbids, masks

        mbids = [float(x[1]) for x in r["bids"]]
        masks = [float(x[1]) for x in r["asks"]]

        mbids = [sum(mbids[:i]) for i in range(1, len(mbids))]
        masks = [sum(masks[:i]) for i in range(1, len(masks))]

        fbids = [float(x[0]) for x in r["bids"]]
        fasks = [float(x[0]) for x in r["asks"]]

    def mumlar_10s(self):
        # coding: utf-8
        import requests

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/candlesticks'
        query_param = 'currency_pair=' + self.coin + '&interval=10s' + '&limit=1000'

        while True:
            try:
                r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

        global tmumlar, dmumlar
        tmumlar = [float(i[3]) for i in r]
        dmumlar = [float(i[4]) for i in r]
        tmumlar.reverse()
        dmumlar.reverse()

    def coklu_al(self):
        # Alış emri girilmesi.........

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/batch_orders'
        query_param = ''

        body = "".join(['[{"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"buy","iceberg":"',
                        str(round(abs(amiktar / 100), mdigit)),
                        '","amount":"', \
                        str(int(amiktar) + float(str(amiktar % max(int(amiktar), 1))[:mdigit + 2])), '","price":"',
                        f"{afiyat:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false},\
         {"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"buy","iceberg":"',
                        str(round(abs(amiktar1 / 100), mdigit)),
                        '","amount":"', \
                        str(int(amiktar1) + float(str(amiktar1 % max(int(amiktar1), 1))[:mdigit + 2])), '","price":"',
                        f"{afiyat1:.{digit}f}",
                        '","time_in_force":"gtc","auto_borrow":false}]'])

        sign_headers = gen_sign('POST', prefix + url, query_param, body)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('POST', host + prefix + url, headers=headers, data=body).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue
        # print(r)

    def coklu_sat(self):

        # Satış emri girilmesi.........

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/batch_orders'
        query_param = ''
        body = "".join(['[{"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"sell","iceberg":"',
                        str(round(abs(0.01 / sfiyat), mdigit)),
                        '","amount":"', \
                        str(int(smiktar) + float(str(smiktar % max(int(smiktar), 1))[:mdigit + 2])), '","price":"',
                        f"{sfiyat:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false},\
         {"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"sell","iceberg":"',
                        str(round(abs(smiktar1 / 100), mdigit)),
                        '","amount":"', \
                        str(int(smiktar1) + float(str(smiktar1 % max(int(smiktar1), 1))[:mdigit + 2])), '","price":"',
                        f"{sfiyat1:.{digit}f}",
                        '","time_in_force":"gtc","auto_borrow":false}]'])

        sign_headers = gen_sign('POST', prefix + url, query_param, body)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('POST', host + prefix + url, headers=headers, data=body).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue
        # print(r)

    def alimlar_sil(self):

        # emirlerin tümünü sil
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = "/spot/orders/"
        query_param = 'currency_pair=' + self.coin + "&" + 'side=buy'
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = gen_sign('DELETE', prefix + url, query_param)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('DELETE', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

        # print("Alım emirleri silindi......")

    def satimlar_sil(self):
        # emirlerin tümünü sil
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = "/spot/orders/"
        query_param = 'currency_pair=' + self.coin + "&" + 'side=sell'
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = gen_sign('DELETE', prefix + url, query_param)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('DELETE', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

        # print("Satım emirleri silindi......")

    def alsat_gecmisi(self):

        # emirleri listele
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/my_trades'
        query_param = "limit=1000"

        sign_headers = gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)

        while True:
            try:
                r = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                r = "Nothing"
                continue
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
                continue
            except KeyError:
                print("Key error hatası veriyor")
                r = "Nothing"
                continue
            if r != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

        global bilanco, kar_orani, sonislems, sonislem, sonafiyat, sonsfiyat, mf, kar_orani, kar_tutari, anapara, mmf, harcanan, agider, sgelir

        miktar = ctm
        anapara = mulk
        harcanan = 0
        agider, sgelir, amiktar, limit = 0, 0, 0, 0
        mf, amf, mmf, kar_tutari, kar_orani = 0, 0, 0, 0, 0
 
        for x in r:
            limit = limit + 1
            if x["currency_pair"] == str(self.coin).upper():
                if x["side"] == "buy":
                    miktar = miktar - float(x["amount"])
                    agider = agider + float(x["amount"]) * float(x["price"])
                    if x["fee_currency"] == coin_adi:
                        miktar = miktar + float(x["fee"])
                else:
                    miktar = miktar + float(x["amount"])
                    sgelir = sgelir + float(x["amount"]) * float(x["price"]) / 1.002
            else:
                break
        
        anapara = round(usdt_to + agider - sgelir, 2)
        kar_tutari = round(ceder - agider + sgelir, 2)
        mmf = round(anapara / (usdt_to / cp + ctm) * 1.002, digit)
        
        harcanan = min(agider, anapara)
        if ceder >= 1:
            mf = round((agider - sgelir) / ctm * 1.002, digit)
        if harcanan > 1:
            kar_orani = round(kar_tutari / harcanan * 100, 2)
       

        bilanco = PrettyTable()
        bilanco.field_names = [str(self.coin).upper(), cp]
        bilanco.add_row([str("Ceder= " + str(round(ceder, 2))), str("mf = " + str(max(mf, 0)))])
        bilanco.add_row([str(" Usdt= " + str(round(usdt_to, 2))), str("mmf= " + str(mmf))])
        bilanco.add_row([str("Apara= " + str(round(anapara, 2))), str(str("harcanan= ") + str(round(harcanan, 2)))])
        bilanco.add_row(
            [str(" Mülk= " + str(round(mulk, 2))), str(str("Max ctm= ") + str(round(usdt_to / cp + ctm, mdigit)))])
        bilanco.add_row([str(str(kar_tutari) + " $"), str("% " + str(kar_orani))])
        bilanco.align[str(self.coin).upper()] = "l"

        sonislem, sonafiyat, sonsfiyat = "bos", 0, 0
        sonislems = r[:limit]
        if ceder >= 1:
            for x in sonislems:
                if x["side"] == "buy":
                    sonafiyat = float(x["price"])
                    break
            for x in r:
                if x["side"] == "sell":
                    sonsfiyat = float(x["price"])
                    break
            sonislem = r[0]["side"]

    def toplu_islem(self):
        T1 = threading.Thread(target=self.coin_fiyat)
        T2 = threading.Thread(target=self.bakiye_getir)
        T3 = threading.Thread(target=self.alsat_gecmisi)
        T4 = threading.Thread(target=self.tahta_getir)
        T5 = threading.Thread(target=self.mumlar_10s)
        T6 = threading.Thread(target=tc_degisim)

        T1.start()
        T2.start()
        T3.start()
        T4.start()
        T5.start()
        T6.start()

        T1.join()
        T2.join()
        T3.join()
        T4.join()
        T5.join()
        T6.join()


# ***********************************************************************************************************************************************************

emirleri_sil()
son_coin()

ct = coin_trader(str(scoin))
ct.coin_digit()
ct.coin_fiyat()
ct.bakiye_getir()
ct.alsat_gecmisi()

alim_ok = "hayır"
yeni_tara = "hayır"
if ceder < 1:
    yeni_tara = "evet"

tbot_ozel.send_message(telegram_chat_id, str("İşlem yeniden başlatıldı."))

afiyat = cp * 0.98
sfiyat = cp * 1.05
msg_bilgi = "hayır"
msg_pump = "hayır"
msg_risk = "hayır"

toplu = []
tc_fiyatlar()
t1 = time.time()
import threading


while True:
    ct.toplu_islem()
    print(bilanco)

    veri_sn = 1 * 60
    if time.time() - t1 >= veri_sn:
        tc_fiyatlar()
        t1 = time.time()

        if len(toplu) > 10 * 60 / veri_sn :
            toplu.pop(0)

    if harcanan >= mulk / 5:
        alim_ok = "evet"

    if ceder < 1:

        if alim_ok == "evet":
            ct.alsat_gecmisi()
            tbot_ozel.send_message(telegram_chat_id, str("Eldeki son mal satıldı. Yeni mal taranıyor..."))
            tbot_ozel.send_message(telegram_chat_id, str(bilanco))
            yeni_tara = "evet"
            bulunanlar = ["abc", "abcd"]

        if yeni_tara == "evet":
            emirleri_sil()
            son_coin()
            for i in toplu:
                for y in i:
                    if y[0] == scoin:
                        i.remove(y)
                
            while True:
                tc_degisim()
                ct = coin_trader(str(bulunan))
                ct.mumlar_10s()
                if tmumlar[0] >= min(dmumlar[:120]) * 1.10:
                    tbot_ozel.send_message(telegram_chat_id, str(bulunan + str(" coine girildi...")))
                    
                    ct.coin_digit()
                    T1 = threading.Thread(target=ct.coin_fiyat)
                    T2 = threading.Thread(target=ct.bakiye_getir)
                    T3 = threading.Thread(target=ct.alsat_gecmisi)
                    T4 = threading.Thread(target=ct.tahta_getir)
                    T5 = threading.Thread(target=ct.mumlar_10s)

                    T1.start()
                    T2.start()
                    T3.start()
                    T4.start()
                    T5.start()

                    T1.join()
                    T2.join()
                    T3.join()
                    T4.join()
                    T5.join()
                    emirleri_sil()
                    t2 = time.time()

                    yeni_tara = "hayır"
                    alim_ok = "hayır"
                    tbot_ozel.send_message(telegram_chat_id, str(bilanco))
                    break
                continue
    # ************- STABİL - PUMP - DUMP BÖLGESİ -*******************************#

    at = 6 * 45
    zip_max = max(tmumlar[:at])
    zip_min = min(dmumlar[:at])
    tdk = round(zip_max / zip_min, 2)
    adk = round(cp / zip_min, 2)

    alk, slk = 4, 4
    km = round(max(min(zip_max/cp * 0.9, 1.07), 1.03), 2)
    zk = round(max(1.05, (1 + (tdk - 1) * 0.35)), 2)

    if adk >= 1.15:
        bolge = "USYükseliş..."
        asi, afi, ma = 5, 10, 7

    elif 1.15 > adk >= 1.10:
        bolge = "SYükseliş..."
        asi, afi, ma = 4, 7, 5

    elif 1.10 > adk >= 1.05:
        bolge = "Yükseliş..."
        asi, afi, ma = 1, 6, 4

    elif 1.05 > adk and tdk >= 1.03:
        bolge = "Stabil"
        asi, afi, ma = 1, 5, 2
        alk, slk = 3, 3
    
    if tdk < 1.03:
        bolge = "Ölü"
        km = 1.02
        alk, slk = 2, 2
        asi, afi, ma = 0, 5, 2

    # ************- ZAF + ZSF BUL -*******************************#

    for x in range(1, 1000):
        if round(max(tmumlar[:x]) / min(dmumlar[:x]), 2) >= zk:
            zaf = min(dmumlar[:x])
            zsf = max(tmumlar[:x])
            break
        else:
            x = min(x, 1000)
            zaf = (max(tmumlar[:x]) + min(dmumlar[:x])) / 2 / km
            zsf = (max(tmumlar[:x]) + min(dmumlar[:x])) / 2 * km

    zaf = zaf * 1.005
    zsf = zsf / 1.005

    hf = 0
    hp = anapara + harcanan * (max(1.03, km) - 1)
    if ceder >= 1:
        hf = round(max((hp - usdt_to) / ctm, fbids[1]), digit)
        if mulk > anapara and mf <= 0:
            hf = fbids[1]

    # ************- AL SAT GEÇMİŞ BÖLÜMÜ -*******************************#

    sonort0, sonort1 = 0, 0
    songaort, songsort = 0, 0
    gamik, gsmik = 0, 0
    gatut, gstut = 0, 0
    mik0, mik1 = 0, 0
    tut0, tut1 = 0, 0

    if ceder >= 1:
        for i in range(0, len(sonislems)):
            if sonislems[i]["side"] == "buy":
                gamik = gamik + float(sonislems[i]["amount"])
                gatut = gatut + float(sonislems[i]["price"]) * float(sonislems[i]["amount"])
                songaort = gatut / gamik
                if gamik >= mulk / alk / cp * 0.9:
                    break

        for i in range(0, len(sonislems)):
            if sonislems[i]["side"] == "sell":
                gsmik = gsmik + float(sonislems[i]["amount"])
                gstut = gstut + float(sonislems[i]["price"]) * float(sonislems[i]["amount"])
                songsort = gstut / gsmik
                if gsmik >= mulk / alk / cp * 0.9:
                    break

        for i in range(len(sonislems)):
            if sonislems[i]["side"] == sonislem:
                mik0 = mik0 + float(sonislems[i]["amount"])
                tut0 = tut0 + float(sonislems[i]["amount"]) * float(sonislems[i]["price"])
                sonort0 = tut0 / mik0
            else:
                break

        for x in range(len(sonislems)):
            if sonislems[x]["side"] == sonislem:
                continue
            else:
                for i in range(x, len(sonislems)):
                    if sonislems[i]["side"] == sonislem:
                        break
                    mik1 = mik1 + float(sonislems[i]["amount"])
                    tut1 = tut1 + float(sonislems[i]["amount"]) * float(sonislems[i]["price"])
                    sonort1 = tut1 / mik1
            break
    # ************- ALIŞ SATIŞ MİKTAR -*******************************#

    if sonislem == "buy":
        sonaort = sonort0
        sonsort = sonort1
    elif sonislem == "sell":
        sonsort = sonort0
        sonaort = sonort1
    else:
        sonaort = 0
        sonsort = 0
    p1 = mulk / alk
    p2 = usdt_to - p1

    m1 = mulk / slk / cp
    m2 = ctm - m1

    if usdt_to <= mulk / alk * 1.1:
        p1 = usdt_to
        p2 = 0
    if ceder <= mulk / slk * 1.1:
        m1 = ctm
        m2 = 0

    if p2 > 0:
        ap1 = min(p1, p2)
        ap2 = max(p1, p2)
        p1 = ap1
        p2 = ap2
    if m2 > 0:
        sm1 = min(m1, m2)
        sm2 = max(m1, m2)
        m1 = sm1
        m2 = sm2

    # ************- HAF + HSF -*******************************#
    haf, hsf = zaf, zsf
    if sonislem == "buy":
        haf = sonaort
        if tut0 > mulk / alk * 0.7:
            haf = songaort / km
        hsf = max(songaort, sonafiyat) * km

    elif sonislem == "sell":
        haf = min(songaort, sonaort)
        hsf = sonsort
        if tut0 > mulk/slk * 0.7:
            haf = min(songsort, sonsfiyat) / km
            hsf = max(songaort * km, songsort * km)

    af = haf
    if adk >= 1.07:
        af = min(af, zaf)
        
    sf = hsf

    if usdt_to <= mulk /4:
        if hsf / zsf < km:
            zsf = hsf
        sf = min(hsf, zsf)
        
        m1 = max(mulk / 4 - usdt_to, 10) / cp
        m2 = ctm - m1
    
    hf = max(hf, songaort * km, sonaort * km, fbids[1])
    if sf >= hf:
        sf = min(sf, hf)
    
        
    # ************- TAF -*******************************#

    for fa in range(asi, afi + 1):
        if 50 <= masks[fa] * fasks[fa]:
            break
    for eai in range(asi, afi + 1):
        if masks[max(ma, fa)] < mbids[eai]:
            break

    if fbids[eai] == afiyat:
        taf = fbids[eai + 1] + k
    else:
        taf = fbids[eai] + k

    if af >= taf * 1.003:
        for yai in range(eai, asi - 1, -1):
            if abs(taf - fbids[yai]) / fbids[yai] >= 3 / 1000:
                yai = yai + 1
                break
        if fbids[yai] == afiyat:
            taf = fbids[yai + 1] + k
        else:
            taf = fbids[yai] + k
        af = taf
   
    if harcanan < mulk /4:
        if ceder > 1:
            p1 = max(mulk/alk - ceder, 10)
        haf = taf
        af = taf
    
    af = min(af, taf)
    # ************- TSF -*******************************#
    
    ssi, sfi, ms = 0, 4, 2
    if sf < mf:
        ssi, sfi, ms = 1, 5, 4
        
    for fs in range(asi, afi + 1):
        if 50 <= mbids[fs] * fbids[fs]:
            break
    for esi in range(ssi, sfi + 1):
        if mbids[max(ms, fs)] < masks[esi]:
            break

    if fasks[esi] == sfiyat:
        tsf = fasks[esi + 1] - k
    else:
        tsf = fasks[esi] - k

    if sf <= tsf * 1.003:
        for ysi in range(esi, ssi - 1, -1):
            if abs(tsf - fasks[ysi]) / fasks[ysi] >= 3 / 1000:
                ysi = ysi + 1
                break
        if fasks[ysi] == sfiyat:
            tsf = fasks[ysi + 1] - k
        else:
            tsf = fasks[ysi] - k
        sf = tsf
    
    sf = max(sf, tsf)
    # ************- HEDEFE ULAŞTIYSAK -*******************************#
    
    if fbids[0] >= hf:
        if tsf / fbids[0] < 1.005:
            sf = fbids[0]
        elif tsf / (fasks[0]-k) < 1.005:
            sf = fasks[0] - k
        else:
            sf = tsf
            
    # ************- AL SAT EMİRLERİNİ GÖNDER BÖLÜMÜ -*******************************#
    af = round(af, digit)
    sf = round(sf, digit)
    
    if usdt_to >= 1:
        if af > afiyat or af < afiyat / 1.002 or usdt_av >= 2:
            T1 = threading.Thread(target=ct.alimlar_sil)
            T2 = threading.Thread(target=ct.bakiye_getir)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            afiyat = af
            afiyat1 = round(min(afiyat * 0.93, fbids[10] + k), digit)

            amiktar = (p1 - 0.5) / afiyat
            amiktar1 = (usdt_to - p1) / afiyat1

            ct.coklu_al()

    if ceder >= 1:
        if  sf > sfiyat * 1.002 or sf < sfiyat or cam * cp >= 5:
            T1 = threading.Thread(target=ct.satimlar_sil)
            T2 = threading.Thread(target=ct.bakiye_getir)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            sfiyat = sf
            f2 = 0
            if m2 > 0:
                f2 = (hp - sf * m1 - usdt_to) / m2
            
            if sf < hf or sf * ctm < hp:
                m1 = m1 - 4/sf
                
            sfiyat1 = round(max(sf * 1.1, fasks[10] - k, f2), digit)
            smiktar = m1
            smiktar1 = m2

            ct.coklu_sat()

    # ************- EKRANA PRİNT BÖLÜMÜ -*******************************#
    fiyatlar = PrettyTable()
    fiyatlar.field_names = [str(str(bolge) + " adk=" + str(adk) + " km=" + str(km)), str("cp= " + str(cp)),
                            str("hf " + str(round(hf,digit)))]
    fiyatlar.add_row([str("af,sf,hp= " + str(round(hp, 2))), round(af, digit), round(sf, digit)])
    fiyatlar.add_row(
        [str(str(sonislem) + " haf,hsf " + str(round(hsf / haf, 2))), round(haf, digit), round(hsf, digit)])
    fiyatlar.add_row(["son aort, sort ", round(sonaort, digit), round(sonsort, digit)])
    fiyatlar.add_row(["son gaort, gsort ", round(songaort, digit), round(songsort, digit)])
    fiyatlar.add_row([str("taf, tsf " + str(round(tsf / taf, 2))), round(taf, digit), round(tsf, digit)])
    fiyatlar.add_row([str("zaf, zsf zk=" + str(round(zk, 2))), round(zaf, digit), round(zsf, digit)])
    fiyatlar.add_row(
        [str("zip_min, zip_max tdk=" + str(tdk)), round(zip_min, digit), round(zip_max, digit)])
    fiyatlar.add_row([str("dolar, adet " + str(round(mulk, 2))), round(mulk / alk, 2), round(mulk / slk / cp, mdigit)])

    print(fiyatlar)

    continue
