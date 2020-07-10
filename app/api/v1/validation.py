import base64
import jwt
import os
import sys
import textwrap
import ctypes
import json
from app import log,config, redisBroker, credentialGenerator
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
            didurl = jwt_token['presentation']['proof']['verificationMethod']
            did = didurl.split("#", 1)[0]
            req = jwt_token["req"].replace("elastos://credaccess/", "")
            requestId = jwt.decode(req, verify=False)["appid"]
        except Exception as err:
            raise AppError(description="Could not parse the response correctly: " + str(err))
        
        rows = EmailValidationTx.objects(transactionId=requestId)

        if not rows:
            raise AppError(description="Request not found")

        item = rows[0]
            
        if not item.status == EmailValidationStatus.WAITING_RESPONSE:
            raise AppError(description="Request is already processed")
          
        if item.did != did:
            item.reason = "DID is not the same"
            item.status = EmailValidationStatus.REJECTED
        else:
            cred = credentialGenerator.issue_credential(didurl, item.email)
            if not cred:
                raise AppError(description="Could not issue credentials")
            item.verifiableCredential = json.loads(cred)
            item.status = EmailValidationStatus.APPROVED

        item.save()
        doc = item.as_dict()

        response = {
            "transactionId": doc["transactionId"],
            "validatorKey": config.VOUCH_APIKEY,
            "verifiableCredential": doc["verifiableCredential"],
            "response": doc["status"],
            "reason": doc["reason"]
        }

        try:
            redisBroker.send_email_response(response)
        except Exception as err:
            raise AppError(description="Could not send message to redis broker: " + str(err))
            
        LOG.info("End Callback")
        self.on_success(res, "OK")
        
   