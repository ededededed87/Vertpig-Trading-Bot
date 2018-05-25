import requests
import json
import hmac
import hashlib
import email
import smtplib
import base64

api_readonly_public_key_file = 'C:\Code\Python\Vertpig Bot\Public Key.txt'
api_readonly_private_key_file = 'C:\Code\Python\Vertpig Bot\Private Key.txt'







def get_public_key():
    file = open(api_readonly_public_key_file)
    public_key = file.readline()
    file.close()
    return public_key

def get_private_key():
    file = open(api_readonly_private_key_file)
    private_key = file.readline()
    file.close()
    private_key_as_bytes = bytes(private_key, 'utf-8')
    return private_key_as_bytes




def get_balances():

    url = "https://www.vertpig.com/api/v1.1/account/getbalances?apikey=" + get_public_key() + "&nonce=1"

    signature = hmac.new(get_private_key(), bytes(url, 'utf-8'), hashlib.sha512).hexdigest()
    header = {"apisign" : signature}
        
    res = requests.get(url, headers = header)
    return json.loads(res.content)


def get_btc_balance():

    return get_balances().get("result")[4].get("Available")
    
def get_vtc_balance():
    
    return get_balances().get("result")[2].get("Available")


market = "VTCBTC"
buy_price = 0.000236
sell_price = 0.000242
buy_quantity = get_btc_balance()
sell_quantity = get_vtc_balance()




def perform_action(method, buy_or_sell = "buy"):
    parameters = {"market" : market, "apikey" : get_public_key(), "nonce" : 1}

                
    rate = buy_price if (buy_or_sell == "buy") else sell_price
    quantity = buy_quantity if (buy_or_sell == "buy") else sell_quantity
    parameters = {"market" : market, "rate" : rate, "quantity" : quantity, "apikey" : get_public_key(), "nonce" : 1}



    public_methods = {"getticker", "getorderbook"}
    account_methods = {"getbalances"}
    market_methods = {"getopenorders", "buylimit", "selllimit", "cancel", "cancelall"}

    method_type = ""

    

    if method in public_methods:
        method_type = "public/"

    elif method in account_methods:
        method_type = "account/"

    elif method in market_methods:
        method_type = "market/"
        

    url = "https://www.vertpig.com/api/v1.1/" + method_type + method + "?"

    for i in parameters.keys():
        url += str(i) + "=" + str(parameters.get(i))
        if str(i) != "nonce":
            url += "&"
        
    signature = hmac.new(get_private_key(), bytes(url, 'utf-8'), hashlib.sha512).hexdigest()
    header = {"apisign" : signature}


    res = requests.get(url, headers = header)

    response_contents = json.loads(res.content)




    return(response_contents)
    print(len(response_contents.get("result")) == 0)




def has_open_orders():
    return len(perform_action("getopenorders").get("result")) != 0

def submit_buy_order():
    perform_action("buylimit","buy")

def submit_sell_order():
    perform_action("selllimit","sell")

def send_email(message):
    msg = email.message_from_string(message)
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = "Vertpig Update"

    s = smtplib.SMTP("smtp.live.com",587)
    s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls() #Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(email_address, password)

    s.sendmail(email_address, email_address, msg.as_string())

    s.quit()
    


if not has_open_orders():
    if get_btc_balance() != "0.00000000":
        submit_buy_order()
        send_email("Buy order has been placed.\n" +
                   "Price: " +  str(buy_price) + "\n" +
                   "VTC Quantity: " + str(buy_quantity))
        print("Buy submitted")
    elif get_vtc_balance != "0.00000000":
        submit_sell_order()
        send_email("Sell order has been placed.\n" +
                   "Price: " +  str(sell_price) + "\n"
                   "VTC  Quantity: " + str(sell_quantity))
        print("Sell submitted")
    else:
        print("no order submitted")
else:
        print("Order already on book")

