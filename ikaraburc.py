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

        global cp, c24, tepe24, k, cpa, cps

        cp, tepe24, c24 = float(r[0]["last"]), float(r[0]["high_24h"]), float(r[0]["change_percentage"])
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

        global taf, tsf, tam, tsm

        tam = [float(x[1]) for x in r["bids"]]
        tsm = [float(x[1]) for x in r["asks"]]

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

        global tmumlar, dmumlar, kmumlar, hacimler, hacimo

        tmumlar = [float(i[3]) for i in r]
        dmumlar = [float(i[4]) for i in r]
        kmumlar = [float(i[2]) for i in r]
        hacimler = [float(i[1]) for i in r]

        tmumlar.reverse()
        dmumlar.reverse()
        kmumlar.reverse()
        hacimler.reverse()
        hk = 12
        hacimg = round(sum(hacimler) / len(hacimler) * hk, 2)
        hacimo = round(sum(hacimler[:12]) / hacimg, 2)

        global emaks, emabs, emak, emab, kemas, kema, kema1, kemao
        emakp = 4
        emabp = 12
        emaks = []
        emabs = []
        for i in range(1000 - emabp):
            emaks.append(round(sum(kmumlar[i:i + emakp]) / emakp, digit))
            emabs.append(round(sum(kmumlar[i:i + emabp]) / emabp, digit))

        kyer = 0
        kemas = []
        for i in range(len(emabs)):
            if emaks[i] < emabs[i]:
                if kyer == 1:
                    kemas.append(emabs[i])
                kyer = -1
            else:
                if kyer == -1:
                    kemas.append(emabs[i])
                kyer = 1

        emak = emaks[0]
        emab = emabs[0]
        kema = kemas[0]
        kema1 = kemas[1]
        kemao = round((emak - kema) / min(emak, kema) * 100, 2)

        global sky, skd, bolge

        ykm = 1.03
        yema = kema
        for i in kemas:
            skd = i
            if yema / skd >= ykm or skd / yema >= ykm:
                break
        if yema / skd >= ykm:
            sky = "Tepe"
        else:
            sky = "Dip"

        if kemao > 0:
            bolge = "Yükseliş"
        elif kemao < 0:
            bolge = "Düşüş"
        elif kemao == 0:
            if emak < skd:
                bolge = "Yükseliş"
            else:
                bolge = "Düşüş"

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
        km, hf = 1.03, 0
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
            anapara = round(abs(usd + agider - sgelir), 2)
            kzt = round(ceder - agider + sgelir, 2)
            harcanan = min(agider, anapara)

            sonislem = r[0]["side"]
            mf = round((agider - sgelir) / ctm * 1.002, digit)
            mmf = round(anapara / (usd / cp + ctm) * 1.002, digit)
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
                        if samik >= mulk / 2:
                            break
            if sgelir > 0:
                for s in r:
                    if s["side"] == "sell":
                        ssmik = ssmik + float(s["amount"])
                        sstut = sstut + float(s["price"]) * float(s["amount"])
                        ssort = round(sstut / ssmik, digit)
                        if ssmik >= mulk / 2:
                            break

            saf = max(saf, saort)
            ssf = min(ssf, ssort)

            hf = round(max((anapara + harcanan * (km - 1) - usd) / ctm, saf * km), digit)

            if time.time() - tsiftah >= 6 * 24 * 60 * 60:
                harcanan = mulk
                anapara = mulk
                amalf = round(agider / amiktar, digit)
                hf = round(max((anapara + harcanan * (km - 1) - usd) / ctm, amalf * 1.20, saf * km), digit)

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
                and 750000 > float(coin_liste[i]["quote_volume"]) > 15000 \
                and float(coin_liste[i]["last"]) / float(coin_liste[i]["low_24h"]) > 1.10:
            toplu.append([coin_liste[i]["currency_pair"], float(coin_liste[i]["last"])])

    print("coin sayısı ", len(toplu))
    import pprint
    pprint.pp(toplu)


def ikinci_elek():
    global bc, bc_tablo

    bc_tablo = PrettyTable()
    uygunlar = []
    bc = "boş"
    for i in range(len(toplu)):
        degisim = []
        bc_tablo.clear()
        for s in range(len(toplu)):
            for n in coin_liste:
                if toplu[s][0] == n["currency_pair"]:
                    degisim.append([toplu[s][0], round(float(n["last"]) / toplu[s][1], 2)])

        bch = max(degisim, key=lambda x: x[1])
        print(bch)
        bc = bch[0]

        sil = "hayır"
        bc_tablo.clear()

        ct = coin_trader(bc)

        T1 = threading.Thread(target=ct.coin_digit)
        T2 = threading.Thread(target=ct.coin_fiyat)
        T4 = threading.Thread(target=ct.mumlar)
        T5 = threading.Thread(target=coins_fiyatlar)

        T1.start()
        T2.start()
        T4.start()
        T5.start()

        T1.join()
        T2.join()
        T4.join()
        T5.join()

        ema_ok = "ema uygun değil"
        ema_oko = "OK"
        hacim_ok = "OK"
        hacimo_ok = "OK"

        if sky == "Dip":
            if 0 <= kemao <= 2:
                ema_ok = "ema uygun"
        if sky == "Tepe":
            if 0 <= kemao <= 2 and cp / min(emaks[:24]) < 1.05:
                ema_ok = "ema uygun"

        if ema_ok == "ema uygun değil":
            ema_oko = "XXXXX"
            sil = "evet"

        if len(tmumlar) < 800:
            print("Yeni çıkan coin, silindi...", bc)
            sil = "evet"

        m1hacim = round(sum(hacimler[:12]), 2)
        if m1hacim < 1000:
            hacim_ok = "XXXXX"
            sil = "evet"

        if hacimo < 1.50:
            hacimo_ok = "XXXXX"
            sil = "evet"

        bc_tablo.field_names = [str(bc), "of " + str(len(toplu))]
        bc_tablo.add_row(["yer", [sky, cp]])
        bc_tablo.add_row(["kemao", [kemao, ema_oko]])
        bc_tablo.add_row(["m1hacim", [m1hacim, hacim_ok]])
        bc_tablo.add_row(["hacimo", [hacimo, hacimo_ok]])
        bc_tablo.add_row(["kema", kema])
        bc_tablo.add_row(["emak", emak])
        bc_tablo.add_row(["emab", emab])
        print(bc_tablo)

        toplu.remove(list(filter(lambda k: k[0] == bc, toplu))[0])

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

while True:
    ct.toplu_islem()
    print(bilanco)

    if agider >= mulk / 5:
        alim_tamam = "evet"
    if ceder < 1:
        if kzo > (km - 1) * 100:
            alim_tamam = "evet"

        if alim_tamam == "evet" or kemao > 5:
            ct.alsat_gecmisi()
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
                    ct.coin_digit()
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
    af = min(hf, taf[5])
    sf = max(hf, tsf[5])

    if bolge == "Yükseliş":
        if sky == "Dip":
            bolge = "Dipten Yükseliş"
            p1 = usd
            afi = 2
            af = min(kema * 1.01, taf[afi])

        elif sky == "Tepe":
            bolge = "Tepeden Yükseliş"
            afi = 3
            if harcanan < mulk / 2:
                p1 = max(mulk / 2 - ceder, 2)
                af = min(kema * 1.01, taf[afi])
            else:
                p1 = min(usd, mulk / 5)
                af = taf[afi] / km
        if ssf > 0:
            af = min(af, ssf / 1.01, taf[afi])
        sfi = 2
        if ceder > 1:
            m1 = min(ctm, mulk / 5 / cp)
            sf = max(saf * km, hf, tsf[0] * 1.01, tsf[sfi])
            if tsf[0] / saf >= 1.05:
                sf = max(saf * km, hf, taf[0] * 1.01, tsf[sfi])

            if tsf[0] >= hf:
                if tsf[0] < max(tmumlar[:2]) / 1.02 or (taf[0] <= emab):
                    sfi = 2
                    bolge = "Tepeden Dönüş"
                    sf = tsf[sfi]

    elif bolge == "Düşüş":
        p1 = min(usd, mulk / 5)

        if sky == "Tepe":
            afi = 5
            bolge = "Tepeden Düşüş"
            af = taf[afi] / km
        else:
            afi = 3
            bolge = "Dipten Düşüş"
            af = min(taf[afi], tsf[0] / 1.01)

        if ceder > 1:
            if tsf[0] >= saf * km:
                sfi = 1
                bolge = "Kârlı düşüş"
                sf = max(saf * km, tsf[sfi])
                m1 = ctm
            else:
                sfi = 2
                bolge = "Kârsız düşüş"
                if usd < mulk / 4:
                    sf = tsf[sfi]
                    m1 = max(mulk / 4 - usd, 2) / cp
                else:
                    sf = max(saf * km, tsf[sfi])
                    m1 = min(mulk / 5 / cp, ctm)

        if emab <= tsf[0] < skd:
            afi, sfi = 3, 3
            bolge = "Dipten Dönüş"
            p1 = min(usd, mulk / 5)
            af = min(ssf / 1.01, taf[afi])
            sf = max(saf * km, tsf[sfi])

    # ************- TAF - TSF ************************************************************#
    m = 3
    for i in range(4):
        if max(tsm[m], 50 / taf[m]) < tam[i]:
            afi = min(i, afi)
            break
    for i in range(4):
        if max(tam[m], 50 / tsf[m]) < tsm[i]:
            sfi = min(i, sfi)
            break

    alist = [tsf[0]] + taf[:afi + 1]
    ters = taf[:4]
    ters.reverse()
    slist = ters + tsf[:sfi + 1]

    if alist[- 1] <= af:
        for a in range(len(alist) - 1, -1, -1):
            af = alist[a] + k
            if alist[a] / alist[- 1] >= 1.005:
                af = alist[a + 1] + k
                break
        if af - k == afiyat:
            af = afiyat
    if slist[- 1] >= sf:
        for s in range(len(slist) - 1, -1, -1):
            sf = slist[s] - k
            if slist[- 1] / slist[s] >= 1.005:
                sf = slist[s + 1] - k
                break
        if sf + k == sfiyat:
            sf = sfiyat

    # ************- AL SAT EMİRLERİNİ GÖNDER BÖLÜMÜ -*************************************#
    af = round(af, digit)
    sf = round(sf, digit)

    if usd >= 1:
        if af > afiyat or af < afiyat / 1.005 or usdt_av > 1:
            T1 = threading.Thread(target=ct.alimlar_sil)
            T2 = threading.Thread(target=ct.bakiye_getir)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            afiyat = af
            afiyat1 = round(min(afiyat * 0.93, taf[10] + k), digit)

            amiktar = (p1 - 0.5) / afiyat
            amiktar1 = (usd - p1) / afiyat1

            ct.coklu_al()

    if ceder >= 1:
        yedek = 2 / cp
        if sf > sfiyat * 1.005 or sf < sfiyat or cam > yedek:
            T1 = threading.Thread(target=ct.satimlar_sil)
            T2 = threading.Thread(target=ct.bakiye_getir)
            T1.start()
            T2.start()
            T1.join()
            T2.join()

            sfiyat = sf
            sfiyat1 = sfiyat * 1.05

            smiktar = m1
            smiktar1 = ctm - m1

            if sf < hf:
                smiktar = m1 - yedek

            ct.coklu_sat()

    # ************- EKRANA PRİNT BÖLÜMÜ -*******************************#
    fiyatlar = PrettyTable()
    fiyatlar.field_names = [str(bolge) + str(" kemao% " + str(kemao)), mal, str("cp " + str(cp))]
    fiyatlar.add_row(["kema " + str(kema), str(" emak " + str(emak)), str("emab " + str(emab))])
    fiyatlar.add_row(["af, sf % " + str(round((sf - af) / af * 100, 2)), round(af, digit), round(sf, digit)])
    fiyatlar.add_row(["taf0,tsf0", str(taf[0]), str(tsf[0])])
    fiyatlar.add_row([str(sonislem) + " saf,ssf", round(saf, digit), round(ssf, digit)])
    fiyatlar.add_row(["mülk " + str(round(mulk, 2)), "ctm " + str(round(ctm, mdigit)), "hf " + str(hf)])

    print(fiyatlar)

    continue
