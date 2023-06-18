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

        global cp, c24, tepe24, dip24, k, cpa, cps

        cp, tepe24, dip24, c24 = float(r[0]["last"]), float(r[0]["high_24h"]), float(r[0]["low_24h"]), float(
            r[0]["change_percentage"])
        cpa, cps = float(r[0]["highest_bid"]), float(r[0]["lowest_ask"])
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
        query_param = "".join(['currency_pair=', str(self.coin).upper(), "&limit=50"])

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

        global taf, tsf, tam, tsm

        tam = [float(x[0]) * float(x[1]) for x in r["bids"]]
        tsm = [float(x[0]) * float(x[1]) for x in r["asks"]]

        tam = [sum(tam[:i]) for i in range(1, len(tam))]
        tsm = [sum(tsm[:i]) for i in range(1, len(tsm))]

        taf = [float(x[0]) for x in r["bids"]]
        tsf = [float(x[0]) for x in r["asks"]]

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
                        f"{afiyat:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false}, \
                        {"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"buy","iceberg":"',
                        str(round(abs(amiktar1 / 100), mdigit)),
                        '","amount":"', \
                        str(int(amiktar1) + float(str(amiktar1 % max(int(amiktar1), 1))[:mdigit + 2])), '","price":"',
                        f"{afiyat1:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false}]'])

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
                        f"{sfiyat:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false}, \
                        {"text":"t-123456","currency_pair":"', self.coin,
                        '","type":"limit","account":"spot","side":"sell","iceberg":"',
                        str(round(abs(0.01 / sfiyat1), mdigit)),
                        '","amount":"', \
                        str(int(smiktar1) + float(str(smiktar1 % max(int(smiktar1), 1))[:mdigit + 2])), '","price":"',
                        f"{sfiyat1:.{digit}f}", '","time_in_force":"gtc","auto_borrow":false}]'])

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
        query_param = 'currency_pair=' + self.coin + "&side=buy"
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
        query_param = 'currency_pair=' + self.coin + "&side=sell"
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

        global tmumlar, dmumlar, kmumlar, hacimler

        tmumlar = [float(i[3]) for i in r]
        dmumlar = [float(i[4]) for i in r]
        kmumlar = [float(i[2]) for i in r]
        hacimler = [float(i[1]) for i in r]

        tmumlar.reverse()
        dmumlar.reverse()
        kmumlar.reverse()
        hacimler.reverse()

        global maks, mabs, mak, mab, ma50, kemas

        mabp = 12
        ma50p = 50
        maks = []
        mabs = []
        ma50s = []
        for i in range(len(kmumlar) - ma50p):
            maks.append(round(kmumlar[i], digit))
            mabs.append(round(sum(kmumlar[i:i + mabp]) / mabp, digit))
            ma50s.append(round(sum(kmumlar[i:i + ma50p]) / ma50p, digit))

        kyer = 0
        kemas = []
        for i in range(len(mabs)):
            if maks[i] < mabs[i]:
                if kyer == 1:
                    kemas.append(mabs[i])
                kyer = -1
            else:
                if kyer == -1:
                    kemas.append(mabs[i])
                kyer = 1

        mak = maks[0]
        mab = mabs[0]
        ma50 = ma50s[0]

        global trend, trendy, yer, akoran, kema, kema1, ykk, kkoran
        ykk = 1.01

        for i in range(500):
            if kemas[0] / kemas[i] > ykk or kemas[i] / kemas[0] > ykk:
                kema = kemas[i - 1]
                kema1 = kemas[i]
                break

        akoran = round((mak - kema) / min(mak, kema) * 100, 2)
        kkoran = round((kemas[0] - kema) / min(kemas[0], kema) * 100, 2)

        km = 1.03
        skema = kema
        for i in kemas:
            if skema / i >= km or i / skema >= km:
                break

        if skema / i >= km:
            yer = "Tepe"
        else:
            yer = "Dip"

        trendy = round((mak - ma50) / min(mak, ma50) * 100, 2)
        trend = "Yükseliş"
        if cp < ma50:
            trend = "Düşüş"

    def alsat_gecmisi(self):
        # emirleri listele
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/my_trades'
        query_param = 'currency_pair=' + str(self.coin) + "&limit=1000"

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

        global bilanco, sonislem, saf, ssf, mf, kzo, kzt, anapara, harcanan, agider, sgelir, hf, km

        miktar = ctm
        amiktar = 0
        anapara = mulk
        agider, sgelir, harcanan = 0, 0, 0
        hf, km = 0, 1.03
        mf, mmf, kzo, kzt = 0, 0, 0, 0
        saf, ssf, sonislem = 0, 0, "boş"

        if ceder >= 1:
            for x in r:
                if x["side"] == "buy":
                    amiktar = amiktar + float(x["amount"])
                    miktar = miktar - float(x["amount"])
                    agider = agider + float(x["amount"]) * float(x["price"])
                    tsiftah = int(x["create_time"])
                    if x["fee_currency"] == coin_adi:
                        miktar = miktar + float(x["fee"])
                    if miktar * float(x["price"]) < 1:
                        break
                else:
                    miktar = miktar + float(x["amount"])
                    sgelir = sgelir + float(x["amount"]) * float(x["price"]) / 1.002

            agider = round(abs(agider), 2)
            sgelir = round(abs(sgelir), 2)
            anapara = round(abs(usd + agider - sgelir), 2)
            kzt = round(ceder - agider + sgelir, 2)
            harcanan = min(agider, anapara)

            sonislem = r[0]["side"]
            mf = round((agider - sgelir) / ctm * 1.002, digit)
            mmf = round(anapara / (usd / cp + ctm) * 1.002, digit)
            amalf = round(agider / amiktar, digit)
            kzo = round(kzt / harcanan * 100, 2)

            if agider > 0:
                for a in r:
                    if a["side"] == "buy":
                        saf = float(a["price"])
                        break
            if sgelir > 0:
                for s in r:
                    if s["side"] == "sell":
                        ssf = float(s["price"])
                        break
            global saort, ssort
            samik, satut, saort = 0, 0, 0
            ssmik, sstut, ssort = 0, 0, 0

            if agider > 0:
                for a in r:
                    if a["side"] == "buy":
                        samik = samik + float(a["amount"])
                        satut = satut + float(a["price"]) * float(a["amount"])
                        saort = round(satut / samik, digit)
                        if satut >= mulk / 2:
                            break
            if sgelir > 0:
                for s in r:
                    if s["side"] == "sell":
                        ssmik = ssmik + float(s["amount"])
                        sstut = sstut + float(s["price"]) * float(s["amount"])
                        ssort = round(sstut / ssmik, digit)
                        if sstut >= mulk / 2:
                            break

            saf = round(max(saf, saort), digit)
            ssf = round(min(ssf, ssort), digit)

            hf = round(max((anapara + harcanan * (km - 1) - usd) / ctm, saf * km), digit)
            if time.time() - tsiftah >= 6 * 24 * 60 * 60:
                hf = round(max(hf, amalf * 1.20), digit)

        bilanco = PrettyTable()
        bilanco.field_names = [str(self.coin).upper(), cp]
        bilanco.add_row(["Ceder= " + str(round(ceder, 2)), " mf= " + str(max(mf, 0))])
        bilanco.add_row([" Usdt= " + str(round(usd, 2)), "mmf= " + str(mmf)])
        bilanco.add_row([" Alım= " + str(round(harcanan, 2)), "Agider= " + str(round(agider, 2))])
        bilanco.add_row(["Apara= " + str(round(anapara, 2)), "Sgelir= " + str(round(sgelir, 2))])
        bilanco.add_row([" Mülk= " + str(round(mulk, 2)), "%" + str(kzo) + " " + str(kzt) + "$"])
        bilanco.align[str(self.coin).upper()] = "l"

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


def coins_fiyatlar():
    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    url = '/spot/tickers'
    global coin_liste
    coin_liste = requests.request('GET', host + prefix + url, headers=headers).json()


def birinci_elek():
    global toplu
    toplu = []
    coins_fiyatlar()
    for i in range(len(coin_liste)):
        if "_USDT" in coin_liste[i]["currency_pair"] \
                and "3S" not in coin_liste[i]["currency_pair"] \
                and "3L" not in coin_liste[i]["currency_pair"] \
                and "5S" not in coin_liste[i]["currency_pair"] \
                and "5L" not in coin_liste[i]["currency_pair"] \
                and float(coin_liste[i]["last"]) > 0 \
                and float(coin_liste[i]["low_24h"]) > 0 \
                and float(coin_liste[i]["quote_volume"]) > 15000 \
                and float(coin_liste[i]["change_percentage"]) > 0 \
                and float(coin_liste[i]["last"]) / float(coin_liste[i]["low_24h"]) > 1.05:
            toplu.append([coin_liste[i]["currency_pair"], float(coin_liste[i]["last"]),
                          round(float(coin_liste[i]["last"]) / float(coin_liste[i]["low_24h"]), 2)])

    print("coin sayısı ", len(toplu))
    toplu.sort(key=lambda x: x[2])
    toplu.reverse()
    import pprint
    pprint.pp(toplu)


def ikinci_elek():
    global bc, bc_tablo

    bc_tablo = PrettyTable()
    uygunlar = []
    bc = "boş"
    for i in range(len(toplu)):
        sil = "hayır"
        bc_tablo.clear()
        bc = toplu[0][0]

        ct = coin_trader(bc)

        T1 = threading.Thread(target=ct.coin_digit)
        T2 = threading.Thread(target=ct.coin_fiyat)
        T3 = threading.Thread(target=ct.mumlar)

        T1.start()
        T2.start()
        T3.start()

        T1.join()
        T2.join()
        T3.join()

        yero = "OK"
        gunluky = round((cp / dip24 - 1) * 100, 2)
        if yer == "Tepe":
            yero = "XXXXX"
            sil = "evet"

        if -1 <= akoran < 1 and cp >= mabs[5]:
            ema_ok = "OK"
        else:
            ema_ok = "XXXXX"
            sil = "evet"

        m1hacim = round(sum(hacimler[:12]), 2)
        hacim_ok = "OK"
        if m1hacim < 2000:
            hacim_ok = "XXXXX"
            sil = "evet"

        if len(tmumlar) < 800:
            print("Yeni çıkan coin, silindi...", bc)
            sil = "evet"

        bc_tablo.field_names = [str(bc) + " g%: " + str(gunluky), "of" + str(len(toplu))]
        bc_tablo.add_row(["cp:  ", str(cp)])
        bc_tablo.add_row(["kema:", str(kema)])
        bc_tablo.add_row(["yer", [yer, yero]])
        bc_tablo.add_row(["akoran", [akoran, ema_ok]])
        bc_tablo.add_row(["m1hacim", [m1hacim, hacim_ok]])

        print(bc_tablo)

        toplu.pop(0)

        if sil != "evet":
            uygunlar.append(bc)
            print(uygunlar)
            break

    import pprint

    if len(uygunlar) > 0:
        print("tarama bitti....")
        pprint.pp(uygunlar)
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
ct.mumlar()

alim_tamam = "evet"
if ceder < 1:
    yeni_tara = "evet"
    alim_tamam = "hayır"

afiyat = cp * 0.98
sfiyat = cp * 1.05
ct.toplu_islem()
ct.satimlar_sil()
ct.bakiye_getir()

sfiyat = taf[3]
smiktar = ctm



sfiyat1 = max(sfiyat * 1.05, ksf, tsf[9] - k)
smiktar1 = 0
ct.coklu_sat()
ct.toplu_islem()
