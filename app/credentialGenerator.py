from app import log, config

import os
import sys
import textwrap
import ctypes
import json

from datetime import datetime
import datedelta

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../lib'))
import ela_did

def adapter_createIdTransactionCallback(adapter, payload, memo):
    return 0 # Success

def adapter_resolveCallback(adapter, did):
    return None # Don't resolve any existing DID from sidechain from this tool

LOG = log.get_logger()


try:
    unicode
except NameError:
    # Define `unicode` for Python3
    def unicode(s, *_):
        return s



def import_did():
    try:
        LOG.info("Initializing DID Store")
        # Get the bindings helper object
        did_api = ela_did.getElaDIDAPI()

        language = "english".encode('utf-8')

        # Create an adapter for resolve() and createIdTransaction(). Needed but unused
        adapter = ela_did.DIDAdapter(ela_did.CREATE_ID_TRANSACTION_FUNC(adapter_createIdTransactionCallback), ela_did.RESOLVE_FUNC(adapter_resolveCallback))

        # Initialize the DID backend
        resolverurl = config.WALLET["RESOLVE_URL"].encode('utf-8')
        cachedir = config.WALLET["CACHE_DIR"].encode('utf-8')
        did_api.DIDBackend_InitializeDefault(resolverurl, cachedir)

        # Initialize a DID Store
        didStore = did_api.DIDStore_Open(config.WALLET["STORE_ROOT"].encode('utf-8'), ctypes.pointer(adapter))
        if didStore == None:
            raise RuntimeError("ERROR: Failed to open DID store.")
        
        LOG.info("Import DID")

        # Get the mnemonic ready
        mnemonic = config.WALLET["MNEMONIC"].encode('utf-8')
        mnemonic_passphrase = config.WALLET["MNEMONIC_PASSPHRASE"].encode('utf-8')
        store_password = config.WALLET["STORE_PASSWORD"].encode('utf-8')

        # Initialize the DID store with the mnemonic
        ret = did_api.DIDStore_InitPrivateIdentity(didStore, store_password, mnemonic, mnemonic_passphrase, language, True)
        if ret != 0:
            raise RuntimeError("ERROR: Failed to initialize private identity for DID.")

        # Create a new DID, slot 0
        did_doc = did_api.DIDStore_NewDID(didStore, store_password, "".encode('utf-8'))
        if did_doc == None:
            raise RuntimeError("ERROR: Failed to create the DID.")

        # Retrieve the DID url string
        didurl = did_api.DIDDocument_GetDefaultPublicKey(did_doc)
        didurl_buf = ctypes.create_string_buffer(did_api.MAX_DIDURL)
        config.WALLET["DID_REQUESTER"] = did_api.DIDURL_ToString(didurl, didurl_buf, did_api.MAX_DIDURL, False)
        LOG.info("DID Requester loaded: {0}".format(config.WALLET["DID_REQUESTER"]))
    except RuntimeError as err:
        errormessage = did_api.DIDError_GetMessage()
        LOG.error("DID - last error message: ".encode('utf-8') + errormessage)
        LOG.error(err)
        exit(2)

    except Exception as err:
        message = "Error: " + str(err) + "\n"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        message += "Unexpected error: " + str(exc_type) + "\n"
        message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
        LOG.error(message)
        exit(3)   


def issue_credential(target_did, email):
    try:
        # Get the bindings helper object
        did_api = ela_did.getElaDIDAPI()

        # Create an adapter for resolve() and createIdTransaction(). Needed but unused
        adapter = ela_did.DIDAdapter(ela_did.CREATE_ID_TRANSACTION_FUNC(adapter_createIdTransactionCallback), ela_did.RESOLVE_FUNC(adapter_resolveCallback))

        # Initialize the DID backend
        resolverurl = config.WALLET["RESOLVE_URL"].encode('utf-8')
        cachedir = config.WALLET["CACHE_DIR"].encode('utf-8')
        did_api.DIDBackend_InitializeDefault(resolverurl, cachedir)

        # Initialize a DID Store
        didStore = did_api.DIDStore_Open(config.WALLET["STORE_ROOT"].encode('utf-8'), ctypes.pointer(adapter))
        if didStore == None:
            raise RuntimeError("ERROR: Failed to open DID store.")

        LOG.info("Issuing credental {} - {}".format(target_did, email))

        requester = config.WALLET["DID_REQUESTER"].encode('utf-8')

        LOG.info(requester)

        didurl = did_api.DIDURL_FromString(requester, None)
        if didurl == None:
            raise RuntimeError("Failed to get DID URL from string.")

        did = did_api.DIDURL_GetDid(didurl)
        if did == None:
            raise RuntimeError("Failed to get DID from DID URL.")

        # Create ourselve as a Issuer
        issuer = did_api.Issuer_Create(did, didurl, didStore)
        if issuer == None:
            raise RuntimeError("Failed to initialize a issuer from the given did and didurl")

        # Target DID (receiver of the credential)
        targetdidurl = did_api.DIDURL_FromString(target_did.encode('utf-8'), None)
        if targetdidurl == None:
            raise RuntimeError("Failed to get DID URL from string (target did).")

        targetdid = did_api.DIDURL_GetDid(targetdidurl)
        if targetdid == None:
            raise RuntimeError("Failed to get DID from DID URL (target did).")

        # Credential ID
        credfragment = "email".encode('utf-8')
        crediddidurl = did_api.DIDURL_NewByDid(targetdid, credfragment)
        if crediddidurl == None:
            raise RuntimeError("Failed to create the credential ID DID URL.")

        # service = {
        #     "type": "Email Validation Service",
        #     "email": email
        # }

        # # Create a new property entry (one of several possible)
        # emailprop = ela_did.Property2("service".encode('utf-8'), service )

        # Create a new property entry (one of several possible)
        emailprop = ela_did.Property("email".encode('utf-8'), email.encode('utf-8'))



        TypesArrayType = ctypes.c_char_p * 1
        PropertyArrayType = ela_did.Property * 1

        store_password = config.WALLET["STORE_PASSWORD"].encode('utf-8')

        print(store_password)
        expiration = datetime.now() + datedelta.YEAR
        timestampExp = int(datetime.timestamp(expiration))
        print(timestampExp)
        # Issue a credential, from Tuum, to the target DID.
        issuedcredential = did_api.Issuer_CreateCredential(
            issuer,
            targetdid,
            crediddidurl,
            TypesArrayType("VerifiableCredential".encode('utf-8')), #
            1,
            PropertyArrayType(emailprop),
            1,
            timestampExp, # Timestamp
            store_password)

        if issuedcredential == None:
            raise RuntimeError("Failed to generate the credential.")
        
        jsonCredential = did_api.Credential_ToJson(issuedcredential, True)

        print(jsonCredential)

        return jsonCredential
    except RuntimeError as err:
        errormessage = did_api.DIDError_GetMessage()
        print("DID - last error message: ".encode('utf-8') + errormessage)
        print(err)
        exit(2)

    except Exception as err:
        message = "Error: " + str(err) + "\n"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        message += "Unexpected error: " + str(exc_type) + "\n"
        message += ' File "' + exc_tb.tb_frame.f_code.co_filename + '", line ' + str(exc_tb.tb_lineno) + "\n"
        print(message)
        exit(3)

    