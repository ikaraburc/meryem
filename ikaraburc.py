import threading

import requests
from prettytable import PrettyTable
from requests.exceptions import ConnectionError

from sifreler import *


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

        global digit, mdigit, coin_adi, coin_birimi, mal
        coin_adi, coin_birimi = str(self.coin).split("_")
        mal = self.coin
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
        global cam, ctm, usd, usdt_av, mulk, ceder

        eldeki_mal = list(filter(lambda coin: coin['currency'] == str.upper(coin_adi), r))
        eldeki_usdt = list(filter(lambda coin: coin['currency'] == 'USDT', r))

        if len(eldeki_mal) > 0:
            cam, clm = float(eldeki_mal[0]["available"]), float(eldeki_mal[0]["locked"])
        else:
            cam, clm = 0, 0
        if len(eldeki_usdt) > 0:
            usdt_av, usdt_lo = float(eldeki_usdt[0]["available"]), float(eldeki_usdt[0]["locked"])
        else:
            usdt_av, usdt_lo = 0, 0

        usd = usdt_av + usdt_lo
        ctm = cam + clm
        ceder = ctm * cp
        mulk = usd + ceder

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

    def mumlar(self):
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/candlesticks'
        query_param = 'currency_pair=' + self.coin + '&interval=5m' + '&limit=1000'
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

        global tmumlar, dmumlar, m1hacim, ema, kema, emas, kemas

        tmumlar = [float(i[3]) for i in r]
        dmumlar = [float(i[4]) for i in r]
        kmumlar = [float(i[2]) for i in r]
        m1hacim = [float(i[1]) for i in r]

        tmumlar.reverse()
        dmumlar.reverse()
        kmumlar.reverse()
        m1hacim.reverse()
        m1hacim = round(sum(m1hacim[:7]), 2)

        emas = []
        ema_periyot = 12
        for i in range(len(kmumlar[:100])):
            emas.append([round(sum(kmumlar[i:i + ema_periyot]) / ema_periyot, digit), kmumlar[i]])

        kemas = []
        if emas[0][0] < emas[0][1]:
            yer = -1
        else:
            yer = 1
        for i in range(len(emas)):
            if emas[i][0] < emas[i][1]:
                if yer == 1:
                    kemas.append(emas[i][0])
                yer = -1
            else:
                if yer == -1:
                    kemas.append(emas[i][0])
                yer = 1
        ema = emas[0][0]
        kema = kemas[0]

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
        query_param = 'currency_pair=' + self.coin + "&limit=1000"

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

        global bilanco, sonislems, sonislem, sonafiyat, sonsfiyat, mf, kar_orani, kar_tutari, anapara, harcanan, agider, sgelir

        miktar = ctm
        anapara = mulk
        agider, sgelir, limit = 0, 0, 0
        mf, mmf, kar_orani, tsiftah = 0, 0, 0, time.time()

        for x in r:
            if miktar * float(x["price"]) >= 1:
                limit = limit + 1
                if x["side"] == "buy":
                    miktar = miktar - float(x["amount"])
                    agider = agider + float(x["amount"]) * float(x["price"])
                    tsiftah = float(x["create_time"])
                    if x["fee_currency"] == coin_adi:
                        miktar = miktar + float(x["fee"])
                else:
                    miktar = miktar + float(x["amount"])
                    sgelir = sgelir + float(x["amount"]) * float(x["price"]) / 1.002
            else:
                break

        agider = round(abs(agider), 2)
        anapara = round(abs(usd + agider - sgelir), 2)
        kar_tutari = round(ceder - agider + sgelir, 2)
        harcanan = min(agider, anapara)
        if harcanan > 0:
            mf = round((agider - sgelir) / ctm * 1.002, digit)
            mmf = round(anapara / (usd / cp + ctm) * 1.002, digit)
            kar_orani = round(kar_tutari / harcanan * 100, 2)

        if time.time() - tsiftah >= 6 * 24 * 60 * 60 or kar_orani > 20:
            mf = -100
            kar_orani = -100
        bilanco = PrettyTable()
        bilanco.field_names = [str(self.coin).upper(), cp]
        bilanco.add_row([str("Ceder= " + str(round(ceder, 2))), str("mf = " + str(max(mf, 0)))])
        bilanco.add_row([str(" Usdt= " + str(round(usd, 2))), str("mmf= " + str(mmf))])
        bilanco.add_row([str("Apara= " + str(round(anapara, 2))), str(str("harcanan= ") + str(round(harcanan, 2)))])
        bilanco.add_row(
            [str(" Mülk= " + str(round(mulk, 2))), str(str("Agider= ") + str(round(agider, 2)))])
        bilanco.add_row([str(str(kar_tutari) + " $"), str("% " + str(kar_orani))])
        bilanco.align[str(self.coin).upper()] = "l"

        sonislem, sonafiyat, sonsfiyat = "bos", 0, 0
        sonislems = r[:limit]
        if ceder >= 1:
            for x in r:
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
        T3 = threading.Thread(target=self.tahta_getir)
        T4 = threading.Thread(target=self.mumlar)

        T1.start()
        T2.start()
        T3.start()
        T4.start()

        T1.join()
        T2.join()
        T3.join()
        T4.join()

        self.alsat_gecmisi()


def emirleri_sil():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/orders'
    query_param = ''
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
    if len(r) >= 1:
        scoin = r[0]["currency_pair"]
    else:
        scoin = "BTC_USDT"


def tc_fiyatlar():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/tickers'
    data = requests.request('GET', host + prefix + url, headers=headers).json()

    global bulunanlar, toplu

    toplu = []
    bulunanlar = ["abc", "abcd"]

    for i in range(len(data)):
        if "_USDT" in data[i]["currency_pair"] \
                and "3S" not in data[i]["currency_pair"] \
                and "3L" not in data[i]["currency_pair"] \
                and "5S" not in data[i]["currency_pair"] \
                and "5L" not in data[i]["currency_pair"] \
                and float(data[i]["last"]) > 0 \
                and float(data[i]["low_24h"]) > 0 \
                and 1.50 > float(data[i]["last"]) / float(data[i]["low_24h"]) > 1.10 \
                and float(data[i]["quote_volume"]) > 80000:
            toplu.append([data[i]["currency_pair"], float(data[i]["last"]), float(data[i]["low_24h"]),
                          float(data[i]["high_24h"])])

    print("coin sayısı ", len(toplu))
    import pprint
    pprint.pp(toplu)


def tc_degisim():
    global bc, ytablo, ytoplu

    ytablo = PrettyTable()
    ytablo.clear()
    uygunlar = []
    bc = "boş"
    for i in range(len(toplu)):
        sil = "hayır"
        ytablo.clear()

        bc = toplu[i][0]
        ct = coin_trader(bc)
        ct.coin_digit()
        ct.toplu_islem()

        t = int(60 / 5 * 2)
        tao = round((max(tmumlar[:t]) / cp - 1) * 100, 2)
        ado = round((cp / min(dmumlar[:t]) - 1) * 100, 2)

        if emas[24][0] >= ema * 1.10 and min(ema / 1.02, fbids[0]) <= ema <= max(ema * 1.02, fasks[0]):
            ema_ok = "ema uygun"
        else:
            sil = "evet"
            ema_ok = "ema uygun değil"

        ytablo.field_names = [str(bc), str(" of " + str(len(toplu) - i))]
        ytablo.add_row(["tao", tao])
        ytablo.add_row(["ado", ado])
        ytablo.add_row(["cp", cp])
        ytablo.add_row(["kema", round(kema, digit)])
        ytablo.add_row(["ema", round(ema, digit)])
        ytablo.add_row(["ema", ema_ok])
        ytablo.add_row(["m1hacim", m1hacim])

        print(ytablo)

        if len(tmumlar) < 800:
            print("Yeni çıkan coin", bc)
            sil = "evet"

        if ado > 5:
            sil = "evet"

        if m1hacim < 750:
            sil = "evet"

        if sil != "evet":
            uygunlar.append([bc, tao])

    import pprint

    if len(uygunlar) > 0:
        uygunlar.sort(key=lambda x: x[1])
        uygunlar.reverse()
        print("tarama bitti....")
        pprint.pp(uygunlar)
        bc = uygunlar[0][0]
    else:
        print("COİN BULUNAMADI....")
        bc = "boş"


# ***********************************************************************************************************************************************************

emirleri_sil()
son_coin()

ct = coin_trader(str(scoin))
ct.coin_digit()
ct.coin_fiyat()
ct.bakiye_getir()

alim_tamam = "evet"
if ceder < 1:
    yeni_tara = "evet"
    alim_tamam = "hayır"

afiyat = cp * 0.98
sfiyat = cp * 1.05

while True:
    ct.toplu_islem()
    print(bilanco)

    if harcanan >= mulk / 5:
        alim_tamam = "evet"
    if ceder < 1:
        if alim_tamam == "evet":
            ct.alsat_gecmisi()
            tbot_ozel.send_message(telegram_chat_id, str("Eldeki son mal satıldı. Yeni mal taranıyor..."))
            tbot_ozel.send_message(telegram_chat_id, str(bilanco))
            yeni_tara = "evet"

        if yeni_tara == "evet":
            emirleri_sil()
            tc_fiyatlar()
            son_coin()
            for i in toplu:
                if i[0] == scoin:
                    toplu.remove(i)
            while True:
                tc_degisim()
                if bc != "boş":
                    tbot_ozel.send_message(telegram_chat_id, str(bc + str(" coine girildi...")))
                    ct = coin_trader(str(bc))
                    ct.coin_digit()
                    ct.toplu_islem()

                    emirleri_sil()
                    t2 = time.time()

                    yeni_tara = "hayır"
                    alim_tamam = "hayır"
                    tbot_ozel.send_message(telegram_chat_id, str(bilanco))
                    tbot_ozel.send_message(telegram_chat_id, str("https://www.gate.io/tr/trade-old/" + str(bc)))
                    break
                else:
                    tc_fiyatlar()
                    continue
    # ************- STABİL - PUMP - DUMP BÖLGESİ -*******************************#

    at = 12
    zmax = max(tmumlar[:at])
    zmin = min(dmumlar[:at])
    tdo = round((zmax / zmin - 1) * 100, 2)
    ado = round((fbids[0] / zmin - 1) * 100, 2)

    km = 1.03
    zk = 1.07
    alk, slk = 4, 4

    if ado >= 20:
        bolge = "Pumpa girdi..."
        asi, afi, ma = 6, 13, 6

    elif 20 > ado >= 15:
        bolge = "USYükseliş..."
        asi, afi, ma = 5, 13, 5

    elif 15 > ado >= 10:
        bolge = "SYükseliş..."
        asi, afi, ma = 4, 10, 4

    elif 10 > ado >= 5:
        bolge = "Yükseliş..."
        asi, afi, ma = 4, 6, 3

    else:
        bolge = "Dibe yakın..."
        asi, afi, ma = 2, 6, 2

        if min(ema / 1.02, fbids[0]) <= ema <= max(ema * 1.02, fasks[0]):
            bolge = "Alım yeri..."
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

    # ************- AL SAT GEÇMİŞ BÖLÜMÜ -*******************************#

    sonort0, sonort1 = 0, 0
    songaort, songsort = 0, 0
    gamik, gsmik = 0, 0
    gatut, gstut = 0, 0
    mik0, mik1 = 0, 0
    tut0, tut1 = 0, 0

    if harcanan > 0:
        for i in range(0, len(sonislems)):
            if sonislems[i]["side"] == "buy":
                gamik = gamik + float(sonislems[i]["amount"])
                gatut = gatut + float(sonislems[i]["price"]) * float(sonislems[i]["amount"])
                songaort = gatut / gamik
                if gatut >= mulk / alk * 0.8:
                    break

        for i in range(0, len(sonislems)):
            if sonislems[i]["side"] == "sell":
                gsmik = gsmik + float(sonislems[i]["amount"])
                gstut = gstut + float(sonislems[i]["price"]) * float(sonislems[i]["amount"])
                songsort = gstut / gsmik
                if gstut >= mulk / slk * 0.8:
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
        sonatut = tut0
        sonstut = tut1

    elif sonislem == "sell":
        sonsort = sonort0
        sonaort = sonort1
        sonatut = tut0
        sonstut = tut1
    else:
        sonaort = 0
        sonsort = 0
        sonatut = 0
        sonstut = 0

    p1 = usd % (mulk / alk)
    if p1 < 5:
        p1 = mulk / alk

    m1 = ctm % (mulk / slk / cp)
    if m1 * cp < 5:
        m1 = mulk / slk / cp

    if usd <= mulk / alk * 1.10:
        p1 = usd

    if ctm <= mulk / slk / cp * 1.10:
        m1 = ctm

    p1 = min(p1, usd - p1)
    m1 = min(m1, ctm - m1)

    # ************- HAF + HSF -*******************************#

    haf, hsf = zaf, zsf
    if harcanan > 0:
        if sonislem == "buy":
            haf = sonaort
            if max(tut0, p1) >= mulk / alk * 0.8:
                haf = songaort / km
            hsf = max(songaort, sonafiyat) * km

        elif sonislem == "sell":
            haf = min(songsort, sonsort) / km
            hsf = max(max(songaort, sonafiyat) * km, sonsort)
            if tut0 >= mulk / slk * 0.8:
                haf = min(songsort, sonsfiyat) / km
                hsf = max(songaort, songsort) * km

    af = haf
    if ceder <= mulk / alk:
        af = max(af, zaf)
    if ado >= 10:
        af = min(af, zaf)

    sf = hsf
    if usd <= (mulk / slk - 5) and fasks[0] < sonafiyat / km:
        sf = min(hsf, zsf)
        if hsf / zsf <= 1.02:
            sf = hsf
        m1 = (mulk / slk - usd) / cp

    # ************- TAF -*******************************#

    for fa in range(0, 5):
        if 50 <= masks[fa] * fasks[fa]:
            break
    for eai in range(asi, afi + 1):
        if masks[max(ma, fa)] < mbids[eai]:
            break

    if fbids[eai] == afiyat:
        taf = fbids[eai + 1] + k
    else:
        taf = fbids[eai] + k

    if af >= taf / 1.005 and eai > asi:
        for yai in range(eai, asi, -1):
            if abs(taf - fbids[yai]) / fbids[yai] >= 5 / 1000:
                yai = yai + 1
                break
        if fbids[yai] == afiyat:
            taf = fbids[yai + 1] + k
        else:
            taf = fbids[yai] + k
        af = taf

    af = min(af, taf)

    # ************- TSF -*******************************#

    ssi, sfi, ms = 2, 4, 2
    if kar_orani >= (km - 1) * 100:
        ssi, sfi, ms = 0, 2, 2

    for fs in range(0, 5):
        if 50 <= mbids[fs] * fbids[fs]:
            break
    for esi in range(ssi, sfi + 1):
        if mbids[max(ms, fs)] < masks[esi]:
            break
        else:
            esi = sfi

    if fasks[esi] == sfiyat:
        tsf = fasks[esi + 1] - k
    else:
        tsf = fasks[esi] - k

    if sf <= tsf * 1.005 and esi > ssi:
        for ysi in range(esi, ssi, -1):
            if abs(tsf - fasks[ysi]) / fasks[ysi] >= 5 / 1000:
                ysi = ysi + 1
                break
            else:
                ysi = ssi

        if fasks[ysi] == sfiyat:
            tsf = fasks[ysi + 1] - k
        else:
            tsf = fasks[ysi] - k

    # ************- EMA STRATEJİSİ -*******************************#

    if fbids[0] > ema:
        yema = "yükseliş"
        if kar_orani > -100:
            if tsf / ema <= 1.03:
                if tsf >= mf * km:
                    m1 = ctm
                    m2 = 0
                    sf = tsf
                else:
                    sf = max(sf, tsf)
            else:
                sf = max(sf, fasks[4] - k)
        elif kar_orani == -100:
            m1 = min(ctm, mulk / slk / cp)
            sf = max(sf * 1.03, fasks[4] - k)

    elif fasks[0] < ema:
        yema = "düşüş"
        af = af / 1.02
        if kar_orani >= (km - 1) * 100:
            m1 = ctm
            sf = fasks[0] - k
        else:
            sf = max(sf, fasks[0] - k)
            m1 = min(ctm, mulk / 2 / cp)
    else:
        for i in range(100):
            if abs(emas[i][0] - ema) / ema >= 5 / 100:
                break
        if (emas[i][0] - ema) / ema >= 5 / 100:
            yema = "dip yatay"
            sf = max(sf * 1.03, tsf)
        else:
            yema = "tepe yatay"
            sf = max(sf, tsf)

    # ************- AL SAT EMİRLERİNİ GÖNDER BÖLÜMÜ -*******************************#
    af = round(af, digit)
    sf = round(sf, digit)

    if usd >= 1:
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
            amiktar1 = (usd - p1) / afiyat1

            ct.coklu_al()

    if ceder > 1:
        if sf > sfiyat * 1.002 or sf < sfiyat or cam * cp >= 5:
            T1 = threading.Thread(target=ct.satimlar_sil)
            T2 = threading.Thread(target=ct.bakiye_getir)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            sfiyat = sf
            yedek = 0
            if -100 < kar_orani < km:
                yedek = 2 / cp
            sfiyat1 = round(max(sf * 1.1, fasks[10] - k), digit)
            smiktar = m1
            smiktar1 = ctm - m1 - yedek

            ct.coklu_sat()

    # ************- EKRANA PRİNT BÖLÜMÜ -*******************************#
    fiyatlar = PrettyTable()
    fiyatlar.field_names = [str(bolge) + str("ado% " + str(ado)), mal, str("cp " + str(cp))]
    fiyatlar.add_row([str(yema) + str(" tdo% " + str(tdo)), str("kema " + str(kema)), str("ema " + str(ema))])
    fiyatlar.add_row([str(sonislem) + str(" af,sf ") + str(round(sf / af, 2)), round(af, digit), round(sf, digit)])
    fiyatlar.add_row([str(" haf,hsf " + str(round(hsf / haf, 2))), round(haf, digit), round(hsf, digit)])
    fiyatlar.add_row(["son aort, sort ", round(sonaort, digit), round(sonsort, digit)])
    fiyatlar.add_row(["son gaort, gsort ", round(songaort, digit), round(songsort, digit)])
    fiyatlar.add_row([str("taf, tsf " + str(round(tsf / taf, 2))), round(taf, digit), round(tsf, digit)])
    fiyatlar.add_row([str("zaf, zsf zk=" + str(round(zk, 2))), round(zaf, digit), round(zsf, digit)])

    print(fiyatlar)

    continue
