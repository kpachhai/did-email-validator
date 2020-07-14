import os
import shutil

from app import log, config
import sys
import ctypes

from datetime import datetime
import datedelta

from lib import ela_did

LOG = log.get_logger()


class CredentialGenerator:

    def __init__(self):
        self.did_api = ela_did.getElaDIDAPI()
        self.did_store = self.initialize_did_store()
        if self.did_store:
            print(self.did_store)
            self.did = self.import_did()
        else:
            self.did = None

    def adapter_create_id_transaction_callback(self, adapter, payload, memo):
        return 0  # Success

    def adapter_resolve_callback(self, adapter, did):
        return None  # Don't resolve any existing DID from sidechain from this tool

    def initialize_did_store(self):
        try:
            # Remove the didstore directory if it exists so we start from scratch
            if os.path.isdir(config.WALLET["STORE_ROOT"]):
                shutil.rmtree(config.WALLET["STORE_ROOT"])

            # Create an adapter for resolve() and createIdTransaction(). Needed but unused
            adapter = ela_did.DIDAdapter(
                ela_did.CREATE_ID_TRANSACTION_FUNC(self.adapter_create_id_transaction_callback),
                ela_did.RESOLVE_FUNC(self.adapter_resolve_callback))
            if adapter is None:
                raise RuntimeError("ERROR: Failed to open DID store")

            # Initialize the DID backend
            resolverurl = config.WALLET["RESOLVE_URL"]
            cachedir = config.WALLET["CACHE_DIR"]
            self.did_api.DIDBackend_InitializeDefault(resolverurl, cachedir)

            # Initialize a DID Store
            did_store = self.did_api.DIDStore_Open(config.WALLET["STORE_ROOT"], ctypes.pointer(adapter))
            if did_store is None:
                raise RuntimeError("ERROR: Failed to open DID store.")

            # Use given mnemonics
            mnemonic = config.WALLET["MNEMONIC"]
            language = "english".encode('utf-8')
            ret = self.did_api.DIDStore_InitPrivateIdentity(did_store, config.WALLET["STORE_PASSWORD"], mnemonic,
                                                            config.WALLET["MNEMONIC_PASSPHRASE"], language, True)
            if ret != 0:
                raise RuntimeError("ERROR: Failed to initialize private identity for DID.")
            return did_store
        except RuntimeError as err:
            errormessage = self.did_api.DIDError_GetMessage()
            LOG.error(f"DID - last error message: {errormessage}, Error: {err}")
            return None
        except Exception as err:
            message = "Error: " + str(err) + "\n"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message += "Unexpected error: " + str(exc_type) + "\n"
            message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
            LOG.error(f"Error: {message}")
            return None

    def import_did(self):
        try:
            did_doc = self.did_api.DIDStore_NewDID(self.did_store, config.WALLET["STORE_PASSWORD"], "".encode('utf-8'))
            did_url = self.did_api.DIDDocument_GetDefaultPublicKey(did_doc)
            didurl_buf = ctypes.create_string_buffer(self.did_api.MAX_DIDURL)
            did = self.did_api.DIDURL_ToString(did_url, didurl_buf, self.did_api.MAX_DIDURL, False)

            if did != config.WALLET["DID_REQUESTER"]:
                raise RuntimeError(
                    f"ERROR: Wrong DID imported. Expected {config.WALLET['DID_REQUESTER']} but got {did}")
            return did
        except RuntimeError as err:
            errormessage = self.did_api.DIDError_GetMessage()
            LOG.error(f"DID - last error message: {errormessage}, Error: {err}")
            return None
        except Exception as err:
            message = "Error: " + str(err) + "\n"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message += "Unexpected error: " + str(exc_type) + "\n"
            message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
            LOG.error(f"Error: {message}")
            return None

    def issue_credential(self, target_did, email):
        try:
            LOG.info("Issuing credential for did {} and email {}".format(target_did, email))

            issuer_did_url = self.did_api.DIDURL_FromString(self.did, None)
            if issuer_did_url is None:
                raise RuntimeError("Failed to get DID URL from string.")

            issuer_did = self.did_api.DIDURL_GetDid(issuer_did_url)
            if issuer_did is None:
                raise RuntimeError("Failed to get issuer_did DID from issuer_did DID URL.")

            # Create ourselves as an Issuer
            issuer = self.did_api.Issuer_Create(issuer_did, issuer_did_url, self.did_store)
            if issuer is None:
                raise RuntimeError("Failed to initialize an issuer from the given did and didurl")

            # Target DID (receiver of the credential)
            targetdidurl = self.did_api.DIDURL_FromString(target_did.encode('utf-8'), None)
            if targetdidurl is None:
                raise RuntimeError("Failed to get DID URL from string (target did).")

            targetdid = self.did_api.DIDURL_GetDid(targetdidurl)
            if targetdid is None:
                raise RuntimeError("Failed to get DID from DID URL (target did).")

            # Credential ID
            credfragment = "email".encode('utf-8')
            crediddidurl = self.did_api.DIDURL_NewByDid(targetdid, credfragment)
            if crediddidurl is None:
                raise RuntimeError("Failed to create the credential ID DID URL.")

            # service = {
            #     "type": "Email Validation Service",
            #     "email": email
            # }

            # # Create a new property entry (one of several possible)
            # emailprop = ela_did.Property2("service".encode('utf-8'), service )

            # Create a new property entry (one of several possible)
            emailprop = ela_did.Property("email".encode('utf-8'), email.encode('utf-8'))

            TypesArrayType = ctypes.c_char_p * 2
            PropertyArrayType = ela_did.Property * 1

            store_password = config.WALLET["STORE_PASSWORD"]

            expiration = datetime.now() + datedelta.YEAR
            timestampExp = int(datetime.timestamp(expiration))
            # Issue a credential, from Tuum, to the target DID.
            issuedcredential = self.did_api.Issuer_CreateCredential(
                issuer,
                targetdid,
                crediddidurl,
                TypesArrayType("VerifiableCredential".encode('utf-8'), "EmailCredential".encode('utf-8')),  #
                2,
                PropertyArrayType(emailprop),
                1,
                timestampExp,  # Timestamp
                store_password)
            if issuedcredential is None:
                raise RuntimeError("Failed to generate the credential.")

            jsonCredential = self.did_api.Credential_ToJson(issuedcredential, True)

            return jsonCredential
        except RuntimeError as err:
            errormessage = self.did_api.DIDError_GetMessage()
            LOG.error(f"DID - last error message: {errormessage}, Error: {err}")
            return None
        except Exception as err:
            message = "Error: " + str(err) + "\n"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message += "Unexpected error: " + str(exc_type) + "\n"
            message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
            LOG.error(f"Error: {message}")
            return None
