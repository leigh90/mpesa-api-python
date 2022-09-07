# class SafaricomSTKPush:
import base64
import requests
from flask import Flask,request
app = Flask(__name__)
import datetime
from decouple import config

now = datetime.datetime.now()
timestamp = now.strftime("%Y%m%d%H%M%S")

# CREDENTIALS
username = config("CONSUMER_KEY")
password = config("CONSUMER_SECRET")
passkey = config('PASSKEY')
phonenumber = config('PHONENUMBER')
authorization_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
payment_request_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def generate_password():
    """
    Generate password to make STK request
    """
    shortcode = str(174379)
    mbecaphrase = shortcode + passkey + timestamp
    mbecaphrase_bytes = mbecaphrase.encode('ascii')
    base64_bytes = base64.b64encode(mbecaphrase_bytes)
    mbeca_password = base64_bytes.decode('ascii')
    return mbeca_password

@app.route("/authentication")
def get_access_token():
    """
    Request access token from Daraja - https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials
    """
    passphrase = username + ":" + password
    passphrase_bytes = passphrase.encode('ascii')
    base64_bytes = base64.b64encode(passphrase_bytes)
    base64_string = base64_bytes.decode('ascii')
    params = {"grant_type":"client_credentials"}
    response = requests.get(url=authorization_url,params=params, headers = {'Authorization': 'Basic {}'.format(base64_string)})
    return response.json()["access_token"]

@app.route("/payment_request")
def send_payment_request():
    """
    Make STK Push request
    """
    payload = {
        "BusinessShortCode": 174379,
        "Password": "{}".format(generate_password()),
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phonenumber,
        "PartyB": 174379,
        "PhoneNumber": phonenumber,
        "CallBackURL": "https://9441-41-215-58-26.in.ngrok.io/webhook",
        "AccountReference": "CompanyXLTD",
        "TransactionDesc": "Payment of X" 
}
    headers = {'Authorization': 'Bearer {}'.format(get_access_token())}
    response = requests.post(url=payment_request_url,json=payload,headers=headers)
    return response.json()

@app.route("/webhook", methods= ["POST"])
def stk_webhook():
    """
    Callback URL 
    """
    print(request.json)
    return "I'm back"


if __name__ == '__main__':
    app.run(debug=True)
