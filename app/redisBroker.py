import redis
import sys
import json
import time
import requests
import jwt
import qrcode
import smtplib
import base64
import io
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from app import log, config
from app.model.emailValidationTx import EmailValidationTx, EmailValidationStatus

LOG = log.get_logger()




def send_email_response(doc):
    broker =  redis.Redis(host = config.REDIS['HOST'], port = config.REDIS['PORT'])
    channel = "email-validator-response"
    broker.publish(channel, json.dumps(doc))

   
def monitor_redis():
    LOG.info("Starting email validator monitor")
    
    channel =  "email-validator-{0}".format(config.VOUCH_APIKEY)

    client = redis.Redis(host = config.REDIS["HOST"], port = config.REDIS["PORT"])
    p = client.pubsub()
    p.subscribe(channel)

    LOG.info("Email validator monitor started")

    while True:
    
        message = p.get_message()

        if message and not message['data'] == 1:
            try:
                message = message['data'].decode('utf-8')
                doc = json.loads(message)
                LOG.info(f'Email-Validator Received message: {message}')

                row = EmailValidationTx(
                    transactionId=doc["transactionId"],
                    email=doc["email"],
                    did= doc["did"].split("#")[0],
                    status=EmailValidationStatus.PENDING,
                    verifiableCredential={},
                    reason=""
                )

                row.save()

                send_email(doc)

                row.status = EmailValidationStatus.WAITING_RESPONSE
                row.save()
                
                LOG.info(f'Email sent')
            except Exception as e:
                LOG.error(f'Email Error: {e}')
            

def send_email(doc):
    message = MIMEMultipart("alternative")
    message["Subject"] = "Validate your email"
    message["From"] = config.EMAIL["SENDER"]
    message["To"] = doc["email"]

    # write the HTML part
    html = """\
    <html>
    <body>
    <p>Scan this QR Code using elastOS to validate your email</p>
    <img src="cid:qrcodeelastos" />
    </body>
    </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    qrCodeUrl =  get_elastos_sign_in_url(doc["transactionId"])
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size = 5,
        border = 4,
    )
    qr.add_data(qrCodeUrl)
    qr.make(fit=True)
    img = qr.make_image()

    buf = io.BytesIO()
    img.save(buf, format='PNG')
     
    
    image = MIMEImage(buf.getvalue())

    

    # Specify the  ID according to the img src in the HTML part
    image.add_header('Content-ID', '<qrcodeelastos>')
    message.attach(image)

    with smtplib.SMTP(config.EMAIL["SMTP_SERVER"], config.EMAIL["SMTP_PORT"]) as server:
        if config.EMAIL["SMTP_TLS"]:
            LOG.info("SMTP server initiating a secure connection with TLS")
            server.starttls()
        LOG.info("SMTP server {0}:{1} started".format(config.EMAIL["SMTP_SERVER"], config.EMAIL["SMTP_PORT"]))
        server.login(config.EMAIL["SMTP_USERNAME"],config.EMAIL["SMTP_PASSWORD"])
        LOG.info("SMTP server logged in with user {0}".format(config.EMAIL["SMTP_USERNAME"]))
        server.sendmail(config.EMAIL["SENDER"], [doc["email"]], message.as_bytes())
        LOG.info("SMTP server sent email message")



def get_elastos_sign_in_url(requestId):
    jwt_claims = {
        'appid': requestId,
        'iss': config.WALLET["DID_REQUESTER"].decode("utf-8"),
        'iat': int(round(time.time())),
        'exp': int(round(time.time() + 300)),
        'callbackurl': config.EMAIL["CALLBACK_URL"]
    }
    jwt_token = jwt.encode(jwt_claims, config.JWT_SECRETKEY, algorithm='HS256')

    url = 'elastos://credaccess/' + jwt_token.decode()

    return url
    

    