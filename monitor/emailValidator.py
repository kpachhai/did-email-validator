import redis
import json
import time
import requests
import jwt
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

print("Starting email validation")
callbackUrl = "http://localhost:8081"
channel = 'email-validator-eyvc79BEYdycHYQFhqCKXKsdzqt'
didRequester = "did:elastos:test1293791273912"
secretKey = "asdasdasdasdasd"
senderEmail = "test@test.com"
client = redis.Redis(host = '127.0.0.1', port = 6379)

p = client.pubsub()
p.subscribe(channel)

print("Service started")

while True:
    
    message = p.get_message()


    if message and not message['data'] == 1:
        message = message['data'].decode('utf-8')
        doc = json.loads(message)
        print(f'Email-Validator Received message: {message}')
        send_email(doc)
        print(f'Email sended:')
        



def send_email(doc):
    qrCodePath = "{}.png".format(doc["transactionId"])
    qrCodeUrl =  get_elastos_sign_in_url(doc["transactionId"])
    qrCodeImg = qrcode.make(qrCodeUrl)
    qrCodeImg.save(qrCodePath)

    message = MIMEMultipart("alternative")
    message["Subject"] = "Validate your email"
    message["From"] = senderEmail
    message["To"] = doc["email"]

    # write the HTML part
    html = """\
    <html>
    <body>
    <p>Scan this QR Code using elastOS to validate your email</p>
    <img src="cid:qrcodeelastos">
    </body>
    </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    fp = open(qrCodePath, 'rb')
    image = MIMEImage(fp.read())
    fp.close()

    # Specify the  ID according to the img src in the HTML part
    image.add_header('Content-ID', '<qrcodeelastos>')
    message.attach(image)

    with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
        server.login("abe005c92b454d", "ea9212b219712d")
        server.sendmail(senderEmail, doc["email"], message)



def get_elastos_sign_in_url(requestId):
    jwt_claims = {
        'appid': requestId,
        'iss': didRequester,
        'iat': int(round(time.time())),
        'exp': int(round(time.time() + 300)),
        'callbackurl': callbackUrl + '/v1/validation/callback',
        'claims': {
            'email': True
        }
    }
    jwt_token = jwt.encode(jwt_claims, secretKey, algorithm='HS256')

    url = 'elastos://credaccess/' + jwt_token.decode()

    return url