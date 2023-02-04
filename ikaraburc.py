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

def m1mumlar(bc):

    # coding: utf-8
    import requests
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = '/spot/candlesticks'
    query_param = 'currency_pair=' + bc + '&interval=1m' + '&limit=1000'
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

    global t1mumlar, d1mumlar
    t1mumlar = [float(i[3]) for i in r]
    d1mumlar = [float(i[4]) for i in r]
    t1mumlar.reverse()
    d1mumlar.reverse()

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
                and float(data[i]["high_24h"])/float(data[i]["low_24h"]) > 1.20 \
                and float(data[i]["high_24h"])/float(data[i]["last"]) > 1.10 \
                and float(data[i]["quote_volume"]) > 80000:
            toplu.append([data[i]["currency_pair"], float(data[i]["last"]), float(data[i]["low_24h"]), float(data[i]["high_24h"])])
    

def tc_degisim():
    global bc, bo, bf, ytablo, bti

    ytablo = PrettyTable()
    ytablo.clear()

    prices2 = []
    changes = []

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/tickers'
    data = requests.request('GET', host + prefix + url, headers=headers).json()

    for x in range(len(toplu)):
        for y in data:
            if toplu[x][0] == y['currency_pair']:
                prices2.append(float(y['last']))

    for i in range(len(toplu)):
        changes.append(round(((prices2[i] / toplu[i][1]) - 1) * 100, 2))

    bti = changes.index(max(changes))
    bc = toplu[bti][0]
    d24f = toplu[bti][2]
    t24f = toplu[bti][3]
    
    bf = prices2[bti]
    bo = changes[bti]
    
    m1mumlar(bc)
    tdo = round((t24f/d24f-1)*100,2)
    
    ytablo.field_names = [str(bc), str("%="+str(bo) + " 24%=" + str(tdo))]
    ytablo.add_row(["Coin Adedi", len(toplu)])
    ytablo.add_row(["Anlık Fiyat", bf])
    ytablo.add_row(["1saat dip =", min(d1mumlar[:60])])
    ytablo.add_row([d24f, t24f])
   
    
    ao = 5
    if t24f / bf < 1.10:
        for i in toplu:
            if i[0] == bc:
                toplu.remove(i)
                    
    if max((bf/min(d1mumlar[:20])-1)*100, changes[bti]) >= ao:
        if bf < min(min(d1mumlar[:60]) * 1.10, t24f/1.10):
            bulunanlar.append(bc)
            if len(bulunanlar) > 5:
                bulunanlar.pop(0)
            
            tbot_genel.send_message(telegram_chat_id, str(ytablo))
            tbot_genel.send_message(telegram_chat_id, str("https://www.gate.io/tr/trade-old/" + str(bc)))
        
        for i in toplu:
            if i[0] == bc:
                toplu.remove(i)


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
        agider, sgelir, limit = 0, 0, 0
        mf, mmf, kar_orani = 0, 0, 0
 
        for x in r:
            if x["currency_pair"] == str(self.coin).upper():
                limit = limit + 1
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
        harcanan = min(agider, anapara)
        if ceder >= 1:
            mf = round((agider - sgelir) / ctm * 1.002, digit)
            mmf = round(anapara / (usdt_to / cp + ctm) * 1.002, digit)
        if harcanan > 1:
            kar_orani = round(kar_tutari / harcanan * 100, 2)
       

        bilanco = PrettyTable()
        bilanco.field_names = [str(self.coin).upper(), cp]
        bilanco.add_row([str("Ceder= " + str(round(ceder, 2))), str("mf = " + str(max(mf, 0)))])
        bilanco.add_row([str(" Usdt= " + str(round(usdt_to, 2))), str("mmf= " + str(mmf))])
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

afiyat = cp * 0.98
sfiyat = cp * 1.05
msg_bilgi = "hayır"
msg_pump = "hayır"
msg_risk = "hayır"

tc_fiyatlar()
t1 = time.time()
import threading


while True:
    ct.toplu_islem()
    print(bilanco)

    veri_sn = 10 * 60
    if time.time() - t1 >= veri_sn:
        tc_fiyatlar()
        t1 = time.time()

    if harcanan >= mulk / 5:
        alim_ok = "evet"

    if ceder < 1:

        if alim_ok == "evet":
            ct.alsat_gecmisi()
            tbot_ozel.send_message(telegram_chat_id, str("Eldeki son mal satıldı. Yeni mal taranıyor..."))
            tbot_ozel.send_message(telegram_chat_id, str(bilanco))
            yeni_tara = "evet"

        if yeni_tara == "evet":
            emirleri_sil()
            son_coin()
            for i in toplu:
                if i[0] == scoin:
                    toplu.remove(i)
            bulunanlar= ["abc"]
            while True:
                tc_degisim()
                print(ytablo)
                if bulunanlar[-1] == bc:
                    tbot_ozel.send_message(telegram_chat_id, str(bc + str(" coine girildi...")))
                    ct = coin_trader(str(bc))
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

    at = 6 * 30
    zip_max = max(tmumlar[:at])
    zip_min = min(dmumlar[:at])
    tdk = round(zip_max / zip_min, 2)
    adk = round(fbids[0] / zip_min, 2)
        
    km = 1.02
    zk = round(max(1.05, 1 + 0.4 * (tdk-1)),2)

    if adk >= 1.15:
        bolge = "USYükseliş..."
        asi, afi, ma = 5, 10, 5
        alk, slk = 4, 2

    elif 1.15 > adk >= 1.10:
        bolge = "SYükseliş..."
        asi, afi, ma = 4, 7, 4
        alk, slk = 4, 2

    elif 1.10 > adk >= 1.05:
        bolge = "Yükseliş..."
        asi, afi, ma = 1, 6, 2
        alk, slk = 3, 3

    elif 1.05 > adk and tdk >= 1.03:
        bolge = "Stabil"
        asi, afi, ma = 1, 5, 2
        alk, slk = 2, 3
    
    if tdk < 1.03:
        bolge = "Ölü"
        alk, slk = 2, 3
        asi, afi, ma = 1, 5, 2

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
    hp = anapara + harcanan * (km - 1)
    if ceder >= 1:
        hf = round(max((hp - usdt_to) / ctm, fbids[1]), digit)
      
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
                if gatut >= mulk / alk * 0.9:
                    break

        for i in range(0, len(sonislems)):
            if sonislems[i]["side"] == "sell":
                gsmik = gsmik + float(sonislems[i]["amount"])
                gstut = gstut + float(sonislems[i]["price"]) * float(sonislems[i]["amount"])
                songsort = gstut / gsmik
                if gstut >= mulk / slk * 0.9:
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
    p1 = usdt_to % (mulk / alk)
    p2 = usdt_to - p1

    m1 = ctm % (mulk / slk / cp)
    m2 = ctm - m1
    
    if usdt_to <= mulk / alk * 1.1:
        p1 = usdt_to
        p2 = 0
    elif min(p1, p2) <= mulk/10:
        p1 = mulk/alk
        p2 = usdt_to - p1
    
    if ceder <= mulk / slk * 1.1:
        m1 = ctm
        m2 = 0
    elif min(m1, m2) * cp <= mulk/10:
        m1 = mulk / slk / cp
        m2 = ctm - m1

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
        if max(tut0, p1)>= mulk / alk * 0.9:
            haf = songaort / km
        hsf = max(songaort, sonafiyat) * km

    elif sonislem == "sell":
        haf = min(max(songaort,sonaort), sonsort/km)
        hsf = max(songaort, sonafiyat) * km
        if max(m1 * cp, tut0) >= mulk/slk * 0.9:
            haf = min(songsort, sonsfiyat) / km
            hsf = max(songaort * km, songsort * km)

    af = haf
    if adk > 1.07:
        af = min(af, zaf)
        
    sf = hsf

    if usdt_to <= mulk/alk:
        if hsf / zsf < km:
            zsf = hsf
        sf = min(hsf, zsf)
        
        m1 = max(mulk/alk - usdt_to, 10) / cp
        m2 = ctm - m1
            
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

    if af >= taf * 1.003:
        for yai in range(eai, - 1, -1):
            if abs(taf - fbids[yai]) / fbids[yai] >= 3 / 1000:
                yai = yai + 1
                break
        if fbids[yai] == afiyat:
            taf = fbids[yai + 1] + k
        else:
            taf = fbids[yai] + k
        af = taf
   
    if harcanan < mulk/alk:
        haf = taf
        af = haf
        if adk >= 1.15:
            af = min(zaf, haf)
        if ceder > 1:
            p1 = max(mulk/alk - ceder, 10)
            
    af = min(af, taf)
    # ************- TSF -*******************************#
    
    ssi, sfi, ms = 0, 4, 2
        
    for fs in range(0, 5):
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
        for ysi in range(esi, - 1, -1):
            if abs(tsf - fasks[ysi]) / fasks[ysi] >= 0.5/100:
                ysi = ysi + 1
                break
        if fasks[ysi] == sfiyat:
            tsf = fasks[ysi + 1] - k
        else:
            tsf = fasks[ysi] - k
      
    sf = max(sf, tsf)
    # ************- HEDEFE ULAŞTIYSAK -*******************************#
    
    if fbids[0] >= hsf >= max(hf, mf):
        if tsf / fbids[0] < 1.01:
            sf = fbids[0]
            
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
            
            if sf < hf or sf * ctm + usdt_to < hp:
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
    fiyatlar.add_row([str("zip_min, zip_max tdk=" + str(tdk)), round(zip_min, digit), round(zip_max, digit)])
    fiyatlar.add_row([str(str(round(mulk, 2)) +"$ "+str(round(ctm, mdigit))+"#"), round(mulk / alk, 2), round(mulk / slk / cp, mdigit)])
    fiyatlar.add_row([str("alk, slk=" + str(alk) +"-"+str(slk)), round(p1, 2), round(m1, mdigit)])

    print(fiyatlar)

    continue
