import requests
import json
import hmac
import hashlib

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

def perform_action(method,market):

    public_methods = {"getticker", "getorderbook"}
    account_methods = {"getbalances"}
    market_methods = {"getopenorders", "buylimit", "selllimit", "cancel", "cancelall"}

    method_type = ""

    parameters = {"market" : market, "apikey" : get_public_key(), "nonce" : 1}

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




    print(response_contents)


perform_action("getbalances","VTCEUR")



