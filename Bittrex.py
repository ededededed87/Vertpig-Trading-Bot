import requests
import json
import hmac
import hashlib
import email
import smtplib
import base64

url = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

print(requests.get(url).content)