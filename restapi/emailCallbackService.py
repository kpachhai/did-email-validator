import json
import falcon
from services.brokerService import BrokerService


class EmailCallbackService:
    def __init__(self, brokerService: BrokerService):
       self.brokerService = brokerService
    def on_post(self, req, resp):
       print("Receiving email callback")
       try:
            body = req.stream.read()
            doc = json.loads(body)
            params = doc["params"]

            

            response = {
                "transactionId": doc["transactionId"],
                "verifiedCredential":{
                    "id": "",
                    "type": ["BasicProfileCredential"],
                    "issuanceDate" : "",
                    "issuer": "",
                    "credentialSubject": {
                        "id": "",
                        "email": ""
                    },
                    "proof": {
                        "type": "ECDSAsecp256r1",
                        "verificationMethod": "VERIFICATION-KEY",
                        "signature": "VALIDATION-HASH"
                    }
                },
                "response": "Success"
            }

            self.brokerService.send_email_response(response)
            
            # transaction = db.create_transaction(doc["validationType"], doc["providerId"], params)
            resp.media = {}
            print(f'End email validation for {doc["transactionId"]}')
       except AttributeError:
            #print(sys.exc_info()[1])
            raise falcon.HTTPBadRequest(
                'Invalid post',
                'Payload must be submitted in the request body.')


       resp.status = falcon.HTTP_201
       resp.location = '/%s/start'