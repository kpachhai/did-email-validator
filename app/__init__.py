import falcon
import redis
import json
import time
import threading

from falcon_cors import CORS
from app import log, config, redisBroker, credentialGenerator
from app.api.common import base
from app.api.v1 import validation
from app.model import emailValidationTx
from app.errors import AppError
from mongoengine import connect


LOG = log.get_logger()

class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info("API Server is starting")

        # Simple endpoint for base
        self.add_route("/", base.BaseResource())
        
        # Receive callback from elastOS
        self.add_route("/v1/validator/callback", validation.EmailConfirmation())
        
        self.add_error_handler(AppError, AppError.handle)


connect(
    config.MONGO['DATABASE'],
    host="mongodb://" + config.MONGO['USERNAME'] + ":" + config.MONGO['PASSWORD'] + "@" +
         config.MONGO['HOST'] + ":" + str(config.MONGO['PORT']) + "/?authSource=admin"
)

#credentialGenerator.import_did()

cors = CORS(
    allow_all_origins=True,
    allow_all_headers=True,
    allow_all_methods=True)
application = App(middleware=[cors.middleware])

th = threading.Thread(target=redisBroker.monitor_redis)
th.setDaemon(True)
th.start()

