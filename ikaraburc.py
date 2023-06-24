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
        query_param = 'currency_pair=' + self.coin + '&interval=5m' + '&limit=1000'
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
        global cp, c24, tepe24, dip24, k, cpa, cps, ott_k

        cp, tepe24, dip24, c24 = float(rcoin_fiyat[0]["last"]), float(rcoin_fiyat[0]["high_24h"]), float(
            rcoin_fiyat[0]["low_24h"]), float(
            rcoin_fiyat[0]["change_percentage"])
        cpa, cps = float(rcoin_fiyat[0]["highest_bid"]), float(rcoin_fiyat[0]["lowest_ask"])
        k = 1 / 10 ** digit
        if (cp + k) / cp >= 1.01:
            k = 0
        ott_k = max(1, round((cps / cpa - 1) * 100, 2))

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

        # ---------------Mumlar

        global kmumlar, hacimler, tmumlar, dmumlar
        tmumlar = [float(i[3]) for i in rmumlar]
        dmumlar = [float(i[4]) for i in rmumlar]
        kmumlar = [float(i[2]) for i in rmumlar]
        hacimler = [float(i[1]) for i in rmumlar]
        kmumlar.reverse()
        hacimler.reverse()

        global maks, mak, ott, otty, otta, son_dip, son_top, ott_yer, mabs, mab, yott_say, kesti
        makp = 2
        ottk = (1 + ott_k / 100)
        bant_percent = (1 + 0.0015)
        mabp = 12
        maks = []
        mabs = []
        for i in range(len(kmumlar) - mabp):
            maks.append(round(sum(kmumlar[i:i + makp]) / makp, digit))
            mabs.append(round(sum(kmumlar[i:i + mabp]) / mabp, digit))

        mak = maks[0]
        mab = mabs[0]

        for i in range(len(maks)):
            if max(maks[:i + 1]) / min(maks[:i + 1]) >= ottk:
                son_dip = min(maks[:i])
                son_top = max(maks[:i])
                break
        for i in range(len(maks)):
            if maks[i] == son_dip:
                son_dip_i = i
                break
        for i in range(len(maks)):
            if maks[i] == son_top:
                son_top_i = i
                break
        if son_dip_i < son_top_i:
            ott = round(son_dip * ottk, digit)
            ott_yer = "düşüyor"
            if maks[0] > son_dip:
                ott_yer = "Düşüşten dönüyor"
        else:
            ott = round(son_top / ottk, digit)
            ott_yer = "yükseliyor"
            if maks[0] < son_top:
                ott_yer = "yükselişten dönüyor"

        otty = round(ott * bant_percent, digit)
        otta = round(ott / bant_percent, digit)
        yott_say = min(son_dip_i, son_top_i)

        kesti = 0
        for i in range(yott_say):
            if (tmumlar[i] >= ott and dmumlar[i] <= ott):
                kesti += 1

        # ------------Alsat_gecmisi
        global bilanco, sonislem, saf, ssf, mf, kzo, kzt, anapara, harcanan, agider, sgelir, hf, km

        miktar = ctm
        amiktar = 0
        anapara = mulk
        agider, sgelir, harcanan = 0, 0, 0
        hf, km = 0, 1.03
        mf, mmf, kzo, kzt = 0, 0, 0, 0
        saf, ssf, sonislem = 0, 0, "boş"

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
            global saort, ssort
            samik, satut, saort = 0, 0, 0
            ssmik, sstut, ssort = 0, 0, 0

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
        for i in range(len(maks)):
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

        if (mabs[0] * 1.02) >= taf[0] > mabs[3]:
            ema_ok = "OK"
        else:
            ema_ok = "XXXXX"
            sil = "evet"

        m1hacim = mbuys
        hacim_ok = "OK"
        if mbuys < max(msells, 1500) or len(tam) < 10 or len(tsm) < 10:
            hacim_ok = "XXXXX"
            sil = "evet"

        if len(kmumlar) < 800:
            print("Yeni çıkan coin, silindi...", bc)
            sil = "evet"

        bc_tablo.field_names = [str(bc) + " g%: " + str(gunluky), "of" + str(len(toplu))]
        bc_tablo.add_row(["cp:  ", str(cp)])
        bc_tablo.add_row(["ott:", str(ott)])
        bc_tablo.add_row(["yer", [yer, yero]])
        bc_tablo.add_row(["kema?", [ema_ok]])
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
        if kzo > (km - 1) * 100:
            alim_tamam = "evet"

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

    # ************- EMA STRATEJİSİ -*******************************#
    af = taf[5]
    sf = max(hf, tsf[5])
    ksf = hf

    for i in range(5):
        afi = i
        ataf = taf[i] + k
        if tsm[2] <= tam[i]:
            break
    for i in range(5):
        sfi = i
        stsf = tsf[i] - k
        if tam[2] <= tsm[i]:
            break

    p1 = min(usd, mulk / 4)
    m1 = min(ctm, mulk / 4 / cp)
    bando = (1 + ott_k / 100)
    orta = round((taf[0] + tsf[0]) / 2, digit)

    if (taf[0] <= ott <= tsf[0]) or (ott < taf[0] < dmumlar[1]) or (tmumlar[1] < tsf[0] < ott):
        bolge = "YATAY"
        af = taf[0] / km
        sf = tsf[0] * km
    elif tsf[0] < ott:
        bolge = "DÜŞÜŞ"
        af = taf[0] / km
        sf = max(stsf, stsf)
        m1 = ctm
    elif taf[0] >= ott:
        bolge = "YÜKSELİŞ"
        af = ataf
        sf = tsf[0] * km
        p1 = usd
        if cp > mabs[5] * 1.05:
            af = min(af, taf[2])
            p1 = min(usd, mulk / 4)
    else:
        bolge = "SAÇMA YATAY"
        af = taf[0] / km
        sf = tsf[0] * km

    # ************- TAF *************************************************************#
    alist = [tsf[1], tsf[0]] + taf[:afi + 1]
    if alist[- 1] <= af:
        for a in range(len(alist) - 1, -1, -1):
            af = alist[a] + k
            if alist[a] / alist[-1] >= 1.005:
                af = alist[a + 1] + k
                break
        if af - k == afiyat and afiyat > alist[-1]:
            af = alist[alist.index(af - k) + 1] + k

    # ************- TSF ************************************************************#
    slist = [taf[1], taf[0]] + tsf[:sfi + 1]

    if slist[- 1] >= sf:
        for s in range(len(slist) - 1, -1, -1):
            sf = slist[s] - k
            if slist[- 1] / slist[s] >= 1.005:
                sf = slist[s + 1] - k
                break
        if sf + k == sfiyat and sfiyat < slist[-1]:
            sf = slist[slist.index(sf + k) + 1] - k

    # ************- AL SAT EMİRLERİNİ GÖNDER BÖLÜMÜ -*************************************#
    af = round(af, digit)
    sf = round(sf, digit)

    if usd >= 1:
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
            amiktar1 = (usd - p1) / afiyat1

            ct.coklu_al()

    if ceder >= 1:
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
    ott_oran = round((cp - ott) / min(cp, ott) * 100, 2)
    fiyatlar = PrettyTable()
    fiyatlar.field_names = [str(bolge) + " ott% " + str(ott_oran), "ott " + str(ott), str("cp " + str(cp))]

    fiyatlar.add_row(["yott: " + str(yott_say) + " sloss%:" + str(ott_k), "af    " + str(round(af, digit)),
                      "sf    " + str(round(sf, digit))])
    fiyatlar.add_row(["kesti: " + str(kesti), "taf0  " + str(taf[0]), "tsf0  " + str(tsf[0])])
    fiyatlar.add_row([str("ctm? " + str(round((ctm + usd / tsf[0]) / 1000, mdigit)) + "k"), "saf   " + str(saf),
                      "ssf   " + str(ssf)])
    fiyatlar.add_row(["mülk  " + str(round(mulk, 2)), "ksf " + str(round(ksf, digit)),
                      "ksf% " + str(round((ksf / cp - 1) * 100, 2)) + " " + str(sonislem)])

    print(fiyatlar)

    continue
