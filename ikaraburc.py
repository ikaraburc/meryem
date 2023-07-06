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
        global rcoin_digit
        while True:
            try:
                rcoin_digit = requests.request('GET', host + prefix + url, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                rcoin_digit = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                rcoin_digit = "Nothing"
            if rcoin_digit != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

    def coin_fiyat(self):

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/tickers'
        query_param = 'currency_pair=' + str.upper(self.coin)

        global rcoin_fiyat
        while True:
            try:
                rcoin_fiyat = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                rcoin_fiyat = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                r = "Nothing"
            if rcoin_fiyat != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

    def bakiye_getir(self):

        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/accounts'
        query_param = ''
        # for `gen_sign` implementation, refer to section `Authentication` above
        sign_headers = gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)

        global rbakiye_getir
        while True:
            try:
                rbakiye_getir = requests.request('GET', host + prefix + url, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                rbakiye_getir = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                rbakiye_getir = "Nothing"
            except KeyError:
                print("Key error hatası veriyor")
                rbakiye_getir = "Nothing"
            if rbakiye_getir != "Nothing" or rbakiye_getir["label"] not in rbakiye_getir:
                break
            else:
                print("Bağlantı bekleniyor...")

                continue

        # print(r)

    def tahta_getir(self):

        # alım satım orderbook derinliğini gör
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/order_book'
        query_param = "".join(['currency_pair=', str(self.coin).upper(), "&limit=50"])

        global rtahta_getir
        while True:
            try:
                rtahta_getir = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                rtahta_getir = "Nothing"
            except ValueError:
                print("Gelen Dosya Json değil...")
                rtahta_getir = "Nothing"
            except KeyError:
                print("Key error hatası veriyor")
                rtahta_getir = "Nothing"

            if rtahta_getir != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

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
        global mumd
        mumd = 1
        query_param = 'currency_pair=' + self.coin + '&interval=' + str(mumd) + 'm' + '&limit=1000'
        global rmumlar
        while True:
            try:
                rmumlar = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                rmumlar = "Nothing"

            except ValueError:
                print("Gelen Dosya Json değil...")
                rmumlar = "Nothing"

            if rmumlar != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

    def alsat_gecmisi(self):
        # emirleri listele
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url = '/spot/my_trades'
        query_param = 'currency_pair=' + str(self.coin) + "&limit=1000"

        sign_headers = gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)
        global ralsat_gecmisi
        while True:
            try:
                ralsat_gecmisi = requests.request('GET', host + prefix + url + "?" + query_param,
                                                  headers=headers).json()
            except ConnectionError as e:  # This is the correct syntax
                print(e)
                time.sleep(1)
                ralsat_gecmisi = "Nothing"
                continue
            except ValueError:
                print("Gelen Dosya Json değil...")
                ralsat_gecmisi = "Nothing"
                continue
            except KeyError:
                print("Key error hatası veriyor")
                ralsat_gecmisi = "Nothing"
                continue
            if ralsat_gecmisi != "Nothing":
                break
            else:
                print("Bağlantı bekleniyor...")
                continue

    def market_hacim(self):
        host = "https://api.gateio.ws"
        prefix = "/api/v4"
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        url = '/spot/trades'
        import time
        zaman = int(time.time() - 30 * 60)
        query_param = 'currency_pair=' + self.coin + "&from=" + str(zaman) + '&limit=1000'

        global rmarket_hacim
        rmarket_hacim = requests.request('GET', host + prefix + url + "?" + query_param, headers=headers).json()

    def toplu_islem(self):
        T0 = threading.Thread(target=self.coin_digit)
        T1 = threading.Thread(target=self.coin_fiyat)
        T2 = threading.Thread(target=self.bakiye_getir)
        T3 = threading.Thread(target=self.mumlar)
        T4 = threading.Thread(target=self.market_hacim)
        T5 = threading.Thread(target=self.tahta_getir)

        T0.start()
        T1.start()
        T2.start()
        T3.start()
        T4.start()
        T5.start()

        T0.join()
        T1.join()
        T2.join()
        T3.join()
        T4.join()
        T5.join()

        self.alsat_gecmisi()

        # ----------------- coin_digit
        global digit, mdigit, coin_adi, coin_birimi, mal
        coin_adi, coin_birimi = str(self.coin).split("_")
        mal = self.coin
        if "label" in rcoin_digit:
            print("Böyle bir coin yok....")
        else:
            digit, mdigit = int(rcoin_digit["precision"]), int(rcoin_digit["amount_precision"])

        # ----------------- coin_fiyat
        global cp, c24, tepe24, dip24, k, cpa, cps

        cp, tepe24, dip24, c24 = float(rcoin_fiyat[0]["last"]), float(rcoin_fiyat[0]["high_24h"]), float(
            rcoin_fiyat[0]["low_24h"]), float(
            rcoin_fiyat[0]["change_percentage"])
        cpa, cps = float(rcoin_fiyat[0]["highest_bid"]), float(rcoin_fiyat[0]["lowest_ask"])
        k = 1 / 10 ** digit
        if (cp + k) / cp >= 1.01:
            k = 0

        # ----------------- bakiye_getir
        global cam, ctm, usd, usdt_av, mulk, ceder

        eldeki_mal = list(filter(lambda coin: coin['currency'] == str.upper(coin_adi), rbakiye_getir))
        eldeki_usdt = list(filter(lambda coin: coin['currency'] == 'USDT', rbakiye_getir))

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

        # -----------tahta_getir

        global taf, tsf, tam, tsm

        tam = [float(x[0]) * float(x[1]) for x in rtahta_getir["bids"]]
        tsm = [float(x[0]) * float(x[1]) for x in rtahta_getir["asks"]]

        tam = [sum(tam[:i]) for i in range(1, len(tam))]
        tsm = [sum(tsm[:i]) for i in range(1, len(tsm))]

        taf = [float(x[0]) for x in rtahta_getir["bids"]]
        tsf = [float(x[0]) for x in rtahta_getir["asks"]]

        # -----------------------------------------------------------------------------------Mumlar

        global kmumlar, hacimler, tmumlar, dmumlar
        tmumlar = [float(i[3]) for i in rmumlar]
        dmumlar = [float(i[4]) for i in rmumlar]
        kmumlar = [float(i[2]) for i in rmumlar]
        hacimler = [float(i[1]) for i in rmumlar]
        tmumlar.reverse()
        dmumlar.reverse()
        kmumlar.reverse()
        hacimler.reverse()

        global mabs, mab, ott, yatay, aldo, usdo, kes, ottk, sdip, stop, maks, mak

        mabp = max(int(10 / mumd), mumd)
        makp = max(int(5 / mumd), mumd)
        ottp = 1.25
        ottk = 1 + ottp / 100
        
        mabs = [round((cp + sum(kmumlar[:mabp - 1])) / mabp, digit)]
        maks = [round((cp + sum(kmumlar[:makp - 1])) / makp, digit)]
        for i in range(len(kmumlar) - mabp):
            mabs.append(round(sum(kmumlar[i:i + mabp]) / mabp, digit))
            maks.append(round(sum(kmumlar[i:i + makp]) / makp, digit))

        mab = mabs[0]
        mak = maks[0]

        yatay = 0
        for i in range(len(mabs)):
            stop = max(mabs[:i + 1])
            sdip = min(mabs[:i + 1])
            sdipi = mabs.index(sdip)
            stopi = mabs.index(stop)
            yatay = min(sdipi, stopi)
            if stop / sdip >= ottk:
                if sdipi < stopi:
                    ott = round(sdip * ottk, digit)
                else:
                    ott = round(stop / ottk, digit)
                break
        kes = 0
        for i in range(yatay):
            if (kmumlar[i] <= ott <= kmumlar[i + 1]):
                kes = kes + 1
        global ote, donmak, kema
        ote = 2
        donmak = maks[int((ote + 1) / 2)]
        kyer = 0
        kemas = []
        for i in range(0, len(maks) - ote):
            if maks[i] < maks[int(i + ote)]:
                if kyer == 1:
                    kemas.append(round(maks[i], digit))
                kyer = -1
            else:
                if kyer == -1:
                    kemas.append(round(maks[i], digit))
                kyer = 1
        kema = kemas[0]

        # ------------Alsat_gecmisi
        global bilanco, sonislem, mf, kzo, kzt, anapara, harcanan, agider, sgelir, hf, km, saort, ssort, saf, ssf
        samik, satut, saort, saf = 0, 0, 0, ott
        ssmik, sstut, ssort, ssf = 0, 0, 0, ott

        miktar = ctm
        amiktar = 0
        anapara = mulk
        agider, sgelir, harcanan = 0, 0, 0
        hf, km = 0, 1.03
        mf, mmf, kzo, kzt = 0, 0, 0, 0
        sonislem = "boş"

        if ceder >= 1:
            for x in ralsat_gecmisi:
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

            sonislem = ralsat_gecmisi[0]["side"]
            mf = round((agider - sgelir) / ctm * 1.002, digit)
            mmf = round(anapara / (usd / cp + ctm) * 1.002, digit)
            amalf = round(agider / amiktar, digit)
            kzo = round(kzt / harcanan * 100, 2)

            if agider > 0:
                for a in ralsat_gecmisi:
                    if a["side"] == "buy":
                        saf = round(float(a["price"]), digit)
                        break
            if sgelir > 0:
                for s in ralsat_gecmisi:
                    if s["side"] == "sell":
                        ssf = round(float(s["price"]), digit)
                        break

            if agider > 0:
                for a in ralsat_gecmisi:
                    if a["side"] == "buy":
                        samik = samik + float(a["amount"])
                        satut = satut + float(a["price"]) * float(a["amount"])
                        saort = round(satut / samik, digit)
                        if satut >= mulk / 2:
                            break
            if sgelir > 0:
                for s in ralsat_gecmisi:
                    if s["side"] == "sell":
                        ssmik = ssmik + float(s["amount"])
                        sstut = sstut + float(s["price"]) * float(s["amount"])
                        ssort = round(sstut / ssmik, digit)
                        if sstut >= mulk / 2:
                            break

            hf = round(max((anapara + harcanan * (km - 1) - usd) / ctm, saort * km), digit)
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

        # --------------market_hacim
        global mbuys, msells
        mbuys = round(sum([float(i["amount"]) * float(i["price"]) for i in rmarket_hacim if i["side"] == "buy"]), 2)
        msells = round(sum([float(i["amount"]) * float(i["price"]) for i in rmarket_hacim if i["side"] == "sell"]), 2)


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
                and float(coin_liste[i]["quote_volume"]) > 25000 \
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
        ct.toplu_islem()

        yer = "BOŞ"
        for i in range(len(mabs)):
            if mabs[0] / mabs[i] >= 1.05:
                yer = "TEPE"
                break
            if mabs[i] / mabs[0] >= 1.05:
                yer = "DİP"
                break

        yero = "OK"
        gunluky = round((cp / dip24 - 1) * 100, 2)
        if yer == "TEPE":
            yero = "XXXXX"
            sil = "evet"

        if (mabs[0] * 1.02) >= taf[0] > mabs[3] and taf[0] > ott:
            ema_ok = "OK"
        else:
            ema_ok = "XXXXX"
            sil = "evet"

        mab_ok = "OK"
        if taf[0] <= mab:
            mab_ok = "XXXXX"
            sil = "evet"

        m1hacim = mbuys
        hacim_ok = "OK"
        if mbuys < max(msells, 1500) or len(tam) < 10 or len(tsm) < 10:
            hacim_ok = "XXXXX"
            sil = "evet"

        if len(kmumlar) < 800:
            print("Yeni çıkan coin, silindi...", bc)
            sil = "evet"

        bc_tablo.field_names = [str(bc) + " g%: " + str(gunluky), "of " + str(len(toplu))]
        bc_tablo.add_row(["cp:  ", str(cp)])
        bc_tablo.add_row(["ema?", [mabs[0], ema_ok]])
        bc_tablo.add_row(["yer", [yer, yero]])
        bc_tablo.add_row(["mab?", [mab, mab_ok]])
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
ct.toplu_islem()

alim_tamam = "evet"
if ceder < 1:
    yeni_tara = "evet"
    alim_tamam = "hayır"

afiyat = cp * 0.98
sfiyat = cp * 1.05

while True:
    ct.toplu_islem()

    print(bilanco)

    if agider >= mulk / 5:
        alim_tamam = "evet"
    if ceder < 1:
        if alim_tamam == "evet":
            ct.toplu_islem()
            tbot_ozel.send_message(telegram_chat_id, str("Eldeki son mal satıldı. Yeni mal taranıyor..."))
            tbot_ozel.send_message(telegram_chat_id, str(bilanco))
            yeni_tara = "evet"

        if yeni_tara == "evet":
            emirleri_sil()
            birinci_elek()
            son_coin()
            for i in toplu:
                if i[0] == scoin:
                    toplu.remove(i)
            while True:
                ikinci_elek()
                if bc != "boş":
                    tbot_ozel.send_message(telegram_chat_id, str(bc + str(" coine girildi...")))
                    ct = coin_trader(str(bc))
                    ct.toplu_islem()

                    emirleri_sil()
                    t2 = time.time()

                    yeni_tara = "hayır"
                    alim_tamam = "hayır"
                    tbot_ozel.send_message(telegram_chat_id, str(bilanco))
                    tbot_ozel.send_message(telegram_chat_id, str(bc_tablo))
                    tbot_ozel.send_message(telegram_chat_id, str("https://www.gate.io/tr/trade-old/" + str(bc)))
                    break
                else:
                    birinci_elek()
                    continue

    # ************- STRATEJİ -*******************************#
    af = taf[5]
    sf = max(hf, tsf[5])
    ksf = round(max(hf, saort * km), digit)
    ho = round((cp / mabs[20] - 1) * 100, 2)

    p1 = usd
    m1 = ctm

    if kes == 0:
        if tsf[0] <= ott:
            bolge = "DÜŞÜŞ TR"
            af = taf[0] / km
            sf = taf[0]
        elif taf[0] >= ott:
            bolge = "YÜKSELİŞ TR"
            af = tsf[0]
            sf = tsf[0] * km
        else:
            bolge = "SAÇMA TR"
            af = taf[0] / km
            sf = tsf[0] * km
    elif maks[0] < donmak:
        bolge = "YATAY DÜŞÜŞ"
        af = taf[0] / km
        sf = max(taf[0], kema / 1.01)
    elif maks[0] > donmak:
        bolge = "YATAY YÜKSELİŞ"
        af = min(tsf[0], kema * 1.01)
        sf = tsf[0] * km
    else:
        bolge = "YATAY SAÇMA"
        af = taf[0] / km
        sf = tsf[0] * km

    # ************- AL SAT EMİRLERİNİ GÖNDER BÖLÜMÜ -*************************************#
    af = round(af, digit)
    sf = round(sf, digit)

    if usd >= 2:
        if af > afiyat or af < afiyat / 1.005 or usdt_av > 1:
            T1 = threading.Thread(target=ct.alimlar_sil)
            T2 = threading.Thread(target=ct.toplu_islem)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            afiyat = af
            afiyat1 = round(min(afiyat * 0.93, taf[9] + k), digit)

            amiktar = (p1 - 0.5) / afiyat
            amiktar1 = (usd - p1 - 0.5) / afiyat1

            ct.coklu_al()

    if ceder >= 2:
        yedek = 2 / cp
        if sf > sfiyat * 1.005 or sf < sfiyat or cam > yedek:
            T1 = threading.Thread(target=ct.satimlar_sil)
            T2 = threading.Thread(target=ct.toplu_islem)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            sfiyat = sf
            sfiyat1 = max(sfiyat * 1.05, ksf, tsf[9] - k)

            smiktar = m1
            smiktar1 = ctm - m1

            if sf < ksf:
                smiktar = m1 - yedek

            ct.coklu_sat()

    # ************- EKRANA PRİNT BÖLÜMÜ -*******************************#
    fiyatlar = PrettyTable()
    fiyatlar.field_names = [str(bolge) + " ho%" + str(ho), "ott  " + str(ott), "cp " + str(cp)]
    fiyatlar.add_row(["kes:" + str(kes) + " yat:" + str(yatay), "af    " + str(af), "taf0  " + str(taf[0])])
    fiyatlar.add_row(["stop: " + str(round(ott * ottk, digit)), "sf    " + str(sf), "tsf0  " + str(tsf[0])])
    fiyatlar.add_row(["sdip: " + str(round(ott / ottk, digit)), "saf   " + str(saf), "ssf   " + str(ssf)])
    fiyatlar.add_row(["ksf: " + str(ksf) + " " + str(sonislem), "saort " + str(saort), "ssort " + str(ssort)])
    print(fiyatlar)

    continue
