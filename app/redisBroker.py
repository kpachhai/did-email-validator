import redis
import json
import time
import jwt
import qrcode
import sys
import smtplib
import io
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from app import log, config
from app.model.emailValidationTx import EmailValidationTx, EmailValidationStatus

LOG = log.get_logger()

client = redis.Redis(host=config.REDIS['HOST'], port=config.REDIS['PORT'], password=config.REDIS['PASSWORD'])

def send_validation_response(doc):
    channel = "validator-response"
    client.publish(channel, json.dumps(doc))


def monitor_redis():
    LOG.info("Starting validator monitor")
   
    channel =  "validator-{0}".format(config.VOUCH_APIKEY)
    
    p = client.pubsub()
    p.subscribe(channel)

    LOG.info("Validator monitor started")

    while True:
        time.sleep(1)
        message = p.get_message()

        if message and not message['data'] == 1:
            try:
                message = message['data'].decode('utf-8')
                doc = json.loads(message)
                LOG.info(f'Validator Received message: {message}')

                if doc["type"] == "email":
                    if doc["action"] == "cancel":
                        cancel_email_validation(doc)
                    else:
                        new_email_validation(doc)
                    LOG.info(f'Email sent')

            except Exception as err:
                message = "Error: " + str(err) + "\n"
                exc_type, exc_obj, exc_tb = sys.exc_info()
                message += "Unexpected error: " + str(exc_type) + "\n"
                message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
                LOG.error(f"Error: {message}")


def new_email_validation(doc):
    row = EmailValidationTx(
        transactionId=doc["transactionId"],
        email=doc["email"],
        did=doc["did"].split("#")[0],
        status=EmailValidationStatus.PENDING,
        isEmailSent=False,
        verifiableCredential={},
        reason=""
    )

    row.save()

    send_email(doc)

    row.isEmailSent = True
    row.status = EmailValidationStatus.WAITING_RESPONSE
    row.save()

    send_validation_response({
            "isSuccess": True,
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "action": "create",
            "response": "Success",
            "reason": "Transaction received with success"
        })


def cancel_email_validation(doc):
    LOG.info(f'Email-Validator Cancel transaction')
    rows = EmailValidationTx.objects(transactionId=doc["transactionId"])
    if not rows:
        LOG.info(f'Transaction {doc["transactionId"]} not found')
        send_validation_response({
            "isSuccess": False,
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "action": "cancel",
            "response": "Error",
            "reason": "Transaction not found"
        })
        return

    transaction = rows[0]

    if transaction.status == EmailValidationStatus.CANCELED:
        LOG.info('Transaction already canceled')
        send_validation_response({
            "isSuccess": True,
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "action": "cancel",
            "response": "Canceled",
            "reason": "Transaction already canceled"
        })
        return

    if transaction.status != EmailValidationStatus.WAITING_RESPONSE and transaction.status != EmailValidationStatus.PENDING:
        LOG.info('Transaction already processed')
        send_validation_response({
            "isSuccess": False,
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "action": "cancel",
            "response": "Error",
            "reason": "Transaction already processed"
        })
        return     

    transaction.status = EmailValidationStatus.CANCELED
    transaction.save()

    send_validation_response({
            "isSuccess": True,
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "action": "cancel",
            "response": "Success",
            "reason": "Transaction canceled with success"
        })
    



def send_email(doc):
    message = MIMEMultipart("mixed")
    message["Subject"] = "Validate your email"
    message["From"] = config.EMAIL["SENDER"]
    message["To"] = doc["email"]

    qrCodeName = f'{doc["transactionId"]}.png'

    # write the HTML part
    html = """\
    <html>
    <body>
    <h2>Scan this QR Code using elastOS to validate your email</h2>
    <img src="cid:qrcodeelastos" alt="Use the attached file" />
    </body>
    </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    qrCodeUrl = get_elastos_sign_in_url(doc["transactionId"])
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=4,
    )
    qr.add_data(qrCodeUrl)
    qr.make(fit=True)
    img = qr.make_image()

    buf = io.BytesIO()
    img.save(buf, format='PNG')

    image = MIMEImage(buf.getvalue())
    image.add_header('Content-ID', f'<qrcodeelastos>')
    message.attach(image)

    attach = MIMEImage(buf.getvalue())
    attach.add_header('Content-Disposition', 'attachment', filename=qrCodeName)
    message.attach(attach)

    with smtplib.SMTP(config.EMAIL["SMTP_SERVER"], config.EMAIL["SMTP_PORT"]) as server:
        if config.EMAIL["SMTP_TLS"]:
            LOG.info("SMTP server initiating a secure connection with TLS")
            server.starttls()
        LOG.info("SMTP server {0}:{1} started".format(config.EMAIL["SMTP_SERVER"], config.EMAIL["SMTP_PORT"]))
        server.login(config.EMAIL["SMTP_USERNAME"], config.EMAIL["SMTP_PASSWORD"])
        LOG.info("SMTP server logged in with user {0}".format(config.EMAIL["SMTP_USERNAME"]))
        server.sendmail(config.EMAIL["SENDER"], [doc["email"]], message.as_bytes())
        LOG.info("SMTP server sent email message")


def get_elastos_sign_in_url(requestId):
    jwt_claims = {
        'appid': requestId,
        'iss': config.WALLET["DID_REQUESTER"].decode('utf-8'),
        'iat': int(round(time.time())),
        'exp': int(round(time.time() + 300)),
        'callbackurl': config.EMAIL["CALLBACK_URL"]
    }
    jwt_token = jwt.encode(jwt_claims, config.JWT_SECRETKEY, algorithm='HS256')

    url = 'elastos://credaccess/' + jwt_token.decode()

    return url
