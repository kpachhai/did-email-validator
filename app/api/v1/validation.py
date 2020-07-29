import jwt
import json
from app import log, config, redisBroker
from app.constants import CRED_GEN
from app.api.common import BaseResource
from app.model.emailValidationTx import EmailValidationTx, EmailValidationStatus
from app.errors import (
    AppError,
)

LOG = log.get_logger()


class EmailConfirmation(BaseResource):
    """
    Handle for endpoint: /v1/validation/callback
    """

    def on_post(self, req, res):
        LOG.info("Receiving Callback")

        data = req.media

        try:
            jwt_token = jwt.decode(data["jwt"], verify=False)
            target_did = jwt_token['presentation']['proof']['verificationMethod']
            did = target_did.split("#", 1)[0]
            req = jwt_token["req"].replace("elastos://credaccess/", "")
            requestId = jwt.decode(req, verify=False)["appid"]
        except Exception as err:
            raise AppError(description="Could not parse the response correctly: " + str(err))
        
        rows = EmailValidationTx.objects(transactionId=requestId)

        if not rows:
            raise AppError(description="Request not found")

        item = rows[0]

        if item.status == EmailValidationStatus.CANCELED:
            LOG.info("This transaction is canceled")
            self.on_success(res, "OK")
            return

        if not item.status == EmailValidationStatus.WAITING_RESPONSE:
            raise AppError(description="Request is already processed")

        
          
        if item.did != did:
            item.reason = "DID is not the same"
            item.status = EmailValidationStatus.REJECTED
        else:
            cred = CRED_GEN.issue_credential(target_did, item.email)
            if not cred:
                raise AppError(description="Could not issue credentials")
            item.verifiableCredential = json.loads(cred)
            item.status = EmailValidationStatus.APPROVED

        item.save()
        doc = item.as_dict()

        response = {
            "isSuccess": True,
            "action": "update",
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "verifiableCredential": doc["verifiableCredential"],
            "response": doc["status"],
            "reason": doc["reason"]
        }

        try:
            redisBroker.send_validation_response(response)
        except Exception as err:
            raise AppError(description="Could not send message to redis broker: " + str(err))
            
        LOG.info(f"Successfully issued credential: {json.dumps(doc)}")
        self.on_success(res, "OK")
