import requests
import json
import hmac
import hashlib
import email
import smtplib
import base64


bittrex_public_api_file = r'C:\Code\Python\Vertpig Bot\BittrexPublicKey.txt'
bittrex_private_api_file = r'C:\Code\Python\Vertpig Bot\BittrexPrivateKey.txt'

vertpig_public_api_file ='C:\Code\Python\Vertpig Bot\VertpigPublicKey.txt'
vertpig_private_api_file = 'C:\Code\Python\Vertpig Bot\VertpigPrivateKey.txt'

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

    url = "https://www." + exchange + ".com/api/v1.1/account/getbalances?apikey=" + get_public_key(exchange) + "&nonce=1"

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

print (get_vtc_balance("vertpig"))

def get_vertpig_price():
    url = "https://vertpig.com/api/v1.1/public/getticker?market=BTC-VTC"
    response = json.loads(requests.get(url).content)
    return float(response.get("result").get("Last"))


def get_bittrex_price():
    url = "https://bittrex.com/api/v1.1/public/getticker?market=BTC-VTC"
    response = json.loads(requests.get(url).content)
    return float(response.get("result").get("Last"))

def get_low_exchange():
    if  min(get_vertpig_price(), get_bittrex_price()) == get_vertpig_price():
        return "vertpig"
    else:
        return "bittrex"

def get_high_exchange():
    if  max(get_vertpig_price(), get_bittrex_price()) == get_vertpig_price():
        return "vertpig"
    else:
        return "bittrex"

def get_percentage_difference(vertpig_price, bittrex_price):
    low = min(vertpig_price, bittrex_price)
    high = max(vertpig_price, bittrex_price)
    percentage_difference = ((high - low) / low) * 100
    return round(percentage_difference,2)


print("The price on Vertpig is " + str(get_vertpig_price()))
print("The price on Bittrex is " + str(get_bittrex_price()))
print("The price on " + get_high_exchange() + " is " + str(get_percentage_difference(get_vertpig_price(), get_bittrex_price())) + "% higher than the price on " + get_low_exchange())

if get_percentage_difference(get_vertpig_price(),get_bittrex_price()) > 0.5:
    if get_high_exchange() == "bittrex" and get_vtc_balance("bittrex") != 0 and get_btc_balance("vertpig") != "0.00000000":
        print("I will sell on bittrex and buy on Vertpig")
    elif get_high_exchange() == "vertpig" and get_vtc_balance("vertpig") != "0.00000000" and get_btc_balance("bittrex") != 0:
        print("I will sell on Vertpig and buy on Bittrex")
    else: print("I will not make a trade")
else:
    print("I will not make a trade")