import random
import string

from decouple import config

BRAND_NAME = "DID Email Validator REST API"

PRODUCTION = config('PRODUCTION', default=False, cast=bool)

LOG_LEVEL = "DEBUG"

DEBUG = True

MONGO = {
    "DATABASE": config('MONGO_DATABASE', default="validatordb", cast=str),
    "HOST": config('MONGO_HOST', default="localhost", cast=str),
    "PORT": config('MONGO_PORT', default=27019, cast=int),
    "USERNAME": config('MONGO_USERNAME', default="mongoadmin", cast=str),
    "PASSWORD": config('MONGO_PASSWORD', default="validatormongo", cast=str)
}

VOUCH_APIKEY=config('VOUCH_APIKEY', default="eyvc79BEYdycHYQFhqCKXKsdzqt", cast=str)

JWT_SECRETKEY=config('JWT_SECRETKEY', default="SECRET_KEY", cast=str)

REDIS = {
    "HOST": config('REDIS_HOST', default="localhost", cast=str),
    "PORT": config('REDIS_PORT', default=6379, cast=int),
    "PASSWORD": config('REDIS_PASSWORD', default="", cast=str)
}

WALLET = {
    "DID_REQUESTER": "", 
    "STORE_ROOT": config('WALLET_STORE_ROOT', default="didstore", cast=str),
    "STORE_PASSWORD": config('WALLET_STORE_PASSWORD', default="password", cast=str),
    "MNEMONIC": config('WALLET_MNEMONIC', default="bean brave rain crush pottery bone lamp purse vintage valley access lawsuit", cast=str),
    "MNEMONIC_PASSPHRASE": ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(100)),
    "RESOLVE_URL": config('WALLET_RESOLVE_URL', default="http://api.elastos.io:20606", cast=str),
    "CACHE_DIR": config('WALLET_CACHE_DIR', default="./.cache.did.elastos", cast=str)
}

EMAIL = {
    "ATTACHMENT_PATH": "/mnt/c/linux",
    "SENDER": config('EMAIL_SENDER', default="test@test.com", cast=str),
    "SMTP_SERVER": config('EMAIL_SMTP_SERVER', default="smtp.example.com", cast=str),
    "SMTP_PORT": config('EMAIL_SMTP_PORT', default="", cast=str),
    "SMTP_USERNAME": config('EMAIL_SMTP_USERNAME', default="support@example.com", cast=str),
    "SMTP_PASSWORD": config('EMAIL_SMTP_PASSWORD', default="password", cast=str),
    "SMTP_TLS": config('EMAIL_SMTP_TLS', default=False, cast=bool),
    "CALLBACK_URL": config('EMAIL_CALLBACK_URL', default="http://localhost:8081/v1/validation/callback", cast=str)
}