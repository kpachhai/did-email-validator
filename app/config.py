from decouple import config

BRAND_NAME = "DID Email Validator REST API"

LOG_LEVEL = "DEBUG"

DEBUG = True

MONGO = {
    "DATABASE": config('MONGO_DATABASE'),
    "HOST": config('MONGO_HOST'),
    "PORT": config('MONGO_PORT'),
    "USERNAME": config('MONGO_USERNAME'),
    "PASSWORD": config('MONGO_PASSWORD')
}

VOUCH_APIKEY=config('VOUCH_APIKEY')

JWT_SECRETKEY=config('JWT_SECRETKEY')

REDIS = {
    "HOST": config('REDIS_HOST'),
    "PORT": config('REDIS_PORT')
}

WALLET = {
    "DID_REQUESTER": config('WALLET_DID_REQUESTER'), 
    "STORE_ROOT": config('WALLET_STORE_ROOT'),
    "STORE_PASSWORD": config('WALLET_STORE_PASSWORD'),
    "MNEMONIC": config('WALLET_MNEMONIC'),
    "MNEMONIC_PASSPHRASE": config('WALLET_MNEMONIC_PASSPHRASE'),
    "RESOLVE_URL": config('WALLET_RESOLVE_URL'),
    "CACHE_DIR": config('WALLET_CACHE_DIR')
}

EMAIL = {
    "ATTACHMENT_PATH": "/mnt/c/linux",
    "SENDER": config('EMAIL_SENDER'),
    "SMTP_SERVER": config('EMAIL_SMTP_SERVER'),
    "SMTP_PORT": config('EMAIL_SMTP_PORT'),
    "USERNAME": config('EMAIL_USERNAME'),
    "PASSWORD": config('EMAIL_PASSWORD'),
    "CALLBACK_URL": config('EMAIL_CALLBACK_URL')
}