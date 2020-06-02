import falcon
from falcon_cors import CORS
from .emailCallbackService import EmailCallbackService
from services.brokerService import BrokerService
cors = CORS(
    allow_all_origins=True,
    allow_all_headers=True,
    allow_all_methods=True,
)

api = application = falcon.API(middleware=[cors.middleware])
# api = application = falcon.API()
brokerService = BrokerService()


api.add_route('/email_callback', EmailCallbackService(brokerService))