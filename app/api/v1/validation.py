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
        try:

            LOG.info("Receiving Callback")

            data = req.media

            print(data)
            
            jwt_token = jwt.decode(data["jwt"], verify=False)
            didurl = jwt_token['presentation']['proof']['verificationMethod']
            did = didurl.split("#", 1)[0]
            email = ""        
            credentials = jwt_token['presentation']['verifiableCredential']
            for cred in credentials:
                if did + "#email" == cred['id']:
                    email = cred['credentialSubject']['email']
            
            req = jwt_token["req"].replace("elastos://credaccess/", "")
            requestId = jwt.decode(req, verify=False)["appid"]
            rows = EmailValidationTx.objects(transactionId=requestId)

            if not rows:
                raise RuntimeError("ERROR: Request not found")

            item = rows[0]
            
            if not item.status == EmailValidationStatus.WAITING_RESPONSE:
                raise RuntimeError("ERROR: Request is already processed")
          
            if item.did != did:
               item.reason = "Did is not the same"
               item.status = EmailValidationStatus.FAILED
            elif item.email != email:
               item.reason = "Email is not the same"
               item.status = EmailValidationStatus.FAILED
            else:
               cred = credentialGenerator.issue_credential(didurl, email)
               item.verifiableCredential = json.loads(cred)
               item.status = EmailValidationStatus.SUCCEDED

            item.save()
            doc = item.as_dict()

            response = {
                "transactionId": doc["transactionId"],
                "validatorKey": config.VOUCH_APIKEY,
                "verifiableCredential": doc["verifiableCredential"],
                "response": doc["status"],
                "reason": doc["reason"]
            }

            print(response)

            redisBroker.send_email_response(response)
            
            LOG.info("End Callback")
            self.on_success(res, "OK")

        except RuntimeError as err:
            LOG.error(err)
            self.on_success(res, "OK")
        except Exception as err:
            message = "Error: " + str(err) + "\n"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message += "Unexpected error: " + str(exc_type) + "\n"
            message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
            LOG.error(message)
            self.on_success(res, "OK")
        
   