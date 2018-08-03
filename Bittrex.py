import requests
import json
import hmac
import hashlib
import email
import smtplib
import base64

original_vtc_balance = 5
original_btc_balance = 0.0008183



bittrex_public_api_file = r'C:\Code\Python\Vertpig Bot\BittrexPublicKey.txt'
bittrex_private_api_file = r'C:\Code\Python\Vertpig Bot\BittrexPrivateKey.txt'

vertpig_public_api_file = r'C:\Code\Python\Vertpig Bot\VertpigPublicKey.txt'
vertpig_private_api_file = r'C:\Code\Python\Vertpig Bot\VertpigPrivateKey.txt'

bittrex = "bittrex"
vertpig = "vertpig"
buy = "buy"
sell = "sell"


def get_public_key(exchange):
    api_file = bittrex_public_api_file if (exchange == "bittrex") else vertpig_public_api_file
    file = open(api_file)
    public_key = file.readline()
    file.close()
    return public_key


def get_private_key(exchange):
    api_file = bittrex_private_api_file if (exchange == "bittrex") else vertpig_private_api_file
    file = open(api_file)
    private_key = file.readline()
    file.close()
    private_key_as_bytes = bytes(private_key, 'utf-8')
    return private_key_as_bytes


def get_balances(exchange):
    url = "https://www." + exchange + ".com/api/v1.1/account/getbalances?apikey=" + get_public_key(
        exchange) + "&nonce=1"

    signature = hmac.new(get_private_key(exchange), bytes(url, 'utf-8'), hashlib.sha512).hexdigest()
    header = {"apisign": signature}

    res = requests.get(url, headers=header)
    return json.loads(res.content).get("result")


def get_vtc_balance(exchange):
    for i in get_balances(exchange):
        if i.get("Currency") == "VTC":
            return i.get("Available")


def get_btc_balance(exchange):
    for i in get_balances(exchange):
        if i.get("Currency") == "BTC":
            return i.get("Available")


def get_vertpig_price():
    price_type = "Bid" if get_high_exchange() == "vertpig" else "Ask"
    url = "https://vertpig.com/api/v1.1/public/getticker?market=BTC-VTC"
    response = json.loads(requests.get(url).content)
    return float(response.get("result").get(price_type))


def get_bittrex_price():
    price_type = "Bid" if get_high_exchange() == "bittrex" else "Ask"
    url = "https://bittrex.com/api/v1.1/public/getticker?market=BTC-VTC"
    response = json.loads(requests.get(url).content)
    return float(response.get("result").get(price_type))


def get_last_price(exchange):
    url = "https://" + exchange + ".com/api/v1.1/public/getticker?market=BTC-VTC"
    response = json.loads(requests.get(url).content)
    return float(response.get("result").get("Last"))


def get_low_exchange():
    if min(get_last_price(vertpig), get_last_price(bittrex)) == get_last_price(vertpig):
        return "vertpig"
    else:
        return "bittrex"


def get_high_exchange():
    if max(get_last_price(vertpig), get_last_price(bittrex)) == get_last_price(vertpig):
        return "vertpig"
    else:
        return "bittrex"


def get_percentage_difference(vertpig_price, bittrex_price):
    low = min(vertpig_price, bittrex_price)
    high = max(vertpig_price, bittrex_price)
    percentage_difference = ((high - low) / low) * 100
    return round(percentage_difference, 2)


def trade(exchange, buy_or_sell):
    if exchange == vertpig:
        method = "buymarket" if buy_or_sell == "buy" else "sellmarket"
    else:
        method = "buylimit" if buy_or_sell == buy else "selllimit"
        quantity = get_btc_balance(bittrex) if buy_or_sell == buy else get_vtc_balance(bittrex)
        rate = get_bittrex_price() if buy_or_sell == buy else get_bittrex_price()

    market = "BTC-VTC"
    amount = get_vtc_balance(exchange) if method == "sellmarket" else get_btc_balance(exchange)
    url = "https://www." + exchange + ".com/api/v1.1/market/" + method + "?apikey=" + get_public_key(exchange) + \
          "&nonce=1&market=" + market

    if exchange == vertpig:
        url += "&amount=" + str(amount)
    else:
        url += "&quantity=" + str(quantity) + "&rate=" + str(rate)

    signature = hmac.new(get_private_key(exchange), bytes(url, 'utf-8'), hashlib.sha512).hexdigest()
    header = {"apisign": signature}
    print(url)
    requests.get(url, headers=header)


def get_total_value():
    return (float(get_vtc_balance(vertpig)) + float(get_btc_balance(vertpig)) / float(get_vertpig_price())) + get_vtc_balance(bittrex) \
           + (get_btc_balance(bittrex) / get_bittrex_price())


def send_email(message):
    msg = email.message_from_string(message)
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = message

    s = smtplib.SMTP("smtp.live.com",587)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(email_address, password)

    s.sendmail(email_address, email_address, "")

    s.quit()

print("Vertpig: " + get_vtc_balance(vertpig) + "VTC, " + get_btc_balance(vertpig) + "BTC")
print("Bittrex: " + str(get_vtc_balance(bittrex)) + "VTC, " + str(get_btc_balance(bittrex)) + "BTC")
print("Estimated total is " + str(round(get_total_value(), 2)) + "VTC")

print()
print("The price on Vertpig is " + str(get_vertpig_price()))
print("The price on Bittrex is " + str(get_bittrex_price()))
print("Percentage: " + str(get_percentage_difference(get_vertpig_price(), get_bittrex_price())) + "%")
print()

if get_percentage_difference(get_vertpig_price(), get_bittrex_price()) > 1.25:
    if get_bittrex_price() > get_vertpig_price() and get_vtc_balance("bittrex") > 0.00000002 and float(get_btc_balance(vertpig)) > 0.00000002:
        trade(bittrex, sell)
        trade(vertpig, buy)
        send_email("Bittrex Sell, Vertpig Buy. Total: " + str(round(get_total_value(), 2)) + "VTC")
        print("I will sell on bittrex and buy on Vertpig")
    elif get_bittrex_price() < get_vertpig_price() and float(get_vtc_balance("vertpig")) > 0.00000002 \
            and get_btc_balance("bittrex") > 1e-07:
        trade(bittrex, buy)
        trade(vertpig, sell)
        send_email("Vertpig Sell, Bittrex Buy. Total: " + str(round(get_total_value(), 2)) + "VTC")
        print("I will sell on Vertpig and buy on Bittrex")
    else:
        print("I will not make a trade")
else:
    print("I will not make a trade")
