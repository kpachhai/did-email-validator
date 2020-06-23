import os
import sys
#from ctypes import c_char, Structure 
import ctypes

MAX_ID_SPECIFIC_STRING = 48
MAX_FRAGMENT = 48

CREATE_ID_TRANSACTION_FUNC = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p)
RESOLVE_FUNC = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p)

class DID(ctypes.Structure):
    _fields_ = [('idstring', ctypes.c_char * MAX_ID_SPECIFIC_STRING)]

class DIDURL(ctypes.Structure):
    _fields_ = [('did', DID), ('fragment', ctypes.c_char * MAX_FRAGMENT)]

class DIDAdapter(ctypes.Structure):
    _fields_ = [('createIdTransaction', CREATE_ID_TRANSACTION_FUNC),('resolve', RESOLVE_FUNC)]

class Property(ctypes.Structure):
    _fields_ = [('key', ctypes.c_char_p), ('value', ctypes.c_char_p)]

def loadElaDIDLibrary():
    script_path = os.path.dirname(os.path.abspath(__file__))
    try:
        if sys.platform.startswith("darwin"):
            dll_name = "darwin/libeladid.1.0.0.dylib"
        else:
            dll_name = "linux/libeladid.so.1.0.0"
        dll_path = os.path.abspath(os.path.join(script_path, '../lib', dll_name))
        dll_handle = ctypes.CDLL(dll_path, ctypes.RTLD_GLOBAL)
        assert dll_handle
    except Exception as e:
        print(e)
        print('Failed to load "' + dll_name + '" library at ' + os.path.dirname(dll_path))
        exit(1)
    return dll_handle

def getElaDIDAPI():
    eladid = loadElaDIDLibrary()

    eladid.MAX_DID          = 128
    eladid.MAX_DIDURL       = 256
    eladid.SIGNATURE_LENGTH = 130

    eladid.DIDBackend_InitializeDefault.restype = ctypes.c_int
    eladid.DIDBackend_InitializeDefault.argtypes = [
        ctypes.c_char_p,    # resolver url
        ctypes.c_char_p     # cache dir path
    ]

    eladid.DIDStore_Open.restype = ctypes.c_void_p # DIDStore*
    eladid.DIDStore_Open.argtypes = [
        ctypes.c_char_p,    # root
        ctypes.c_void_p     # adapter
    ]

    eladid.DIDStore_InitPrivateIdentity.restype = ctypes.c_int
    eladid.DIDStore_InitPrivateIdentity.argtypes = [
        ctypes.c_void_p,    # DIDStore*
        ctypes.c_char_p,    # storepass
        ctypes.c_char_p,    # mnemonic
        ctypes.c_char_p,    # passphrase
        ctypes.c_char_p,    # language
        ctypes.c_bool       # force
    ]

    eladid.DIDStore_NewDID.restype = ctypes.c_void_p # DIDDocument*
    eladid.DIDStore_NewDID.argtypes = [
        ctypes.c_void_p,    # DIDStore*
        ctypes.c_char_p,    # storepass
        ctypes.c_char_p     # hint
    ]
    
    eladid.DID_Resolve.restype = ctypes.c_void_p # DIDDocument*
    eladid.DID_Resolve.argtypes = [
        ctypes.c_void_p,    # DID*
        ctypes.c_bool       # force
    ]

    eladid.DIDStore_LoadDID.restype = ctypes.c_void_p # DIDDocument*
    eladid.DIDStore_LoadDID.argtypes = [
        ctypes.c_void_p,    # DIDStore*
        ctypes.c_void_p     # DID*
    ]
    
    eladid.DIDDocument_Sign.restype = ctypes.c_int
    eladid.DIDDocument_Sign.argtypes = [
        ctypes.c_void_p,    # DIDDocument*
        ctypes.c_void_p,    # DIDURL *key
        ctypes.c_char_p,    # storepass
        ctypes.c_char_p,    # sig
        ctypes.c_int,       # count
        ctypes.c_void_p,    # data
        ctypes.c_size_t     # len
    ]

    eladid.DIDStore_PublishDID.restype = ctypes.c_int
    eladid.DIDStore_PublishDID.argtypes = [
        ctypes.c_void_p,    # DIDStore*
        ctypes.c_void_p,    # DIDDocument*
        ctypes.c_void_p,    # ??? DIDURL*
        ctypes.c_char_p,    # storepass
    ]

    eladid.DIDDocument_GetSubject.restype = ctypes.c_void_p # DID*
    eladid.DIDDocument_GetSubject.argtypes = [
        ctypes.c_void_p,    # DIDDocument*
    ]

    eladid.DIDDocument_GetDefaultPublicKey.restype = ctypes.c_void_p # DIDURL*
    eladid.DIDDocument_GetDefaultPublicKey.argtypes = [
        ctypes.c_void_p,    # DIDDocument*
    ]

    eladid.DIDDocument_GetPublicKey.restype = ctypes.c_void_p # PublicKey*
    eladid.DIDDocument_GetPublicKey.argtypes = [
        ctypes.c_void_p,    # DIDDocument*
        ctypes.c_void_p,    # DIDURL*
    ]

    eladid.DIDDocument_Verify.restype = ctypes.c_int
    eladid.DIDDocument_Verify.argtypes = [
        ctypes.c_void_p,    # DIDDocument *document
        ctypes.c_void_p,    # DIDURL *keyid
        ctypes.c_char_p,    # sig
        ctypes.c_int,       # count
        ctypes.c_void_p,    # data
        ctypes.c_size_t     # len
    ]

    eladid.PublicKey_GetPublicKeyBase58.restype = ctypes.c_char_p # Base58 string
    eladid.PublicKey_GetPublicKeyBase58.argtypes = [
        ctypes.c_void_p,    # PublicKey**
    ]

    eladid.DIDURL_ToString.restype = ctypes.c_char_p
    eladid.DIDURL_ToString.argtypes = [
        ctypes.c_void_p,    # DIDURL*
        ctypes.c_char_p,    # idstring
        ctypes.c_size_t,    # len
        ctypes.c_bool,      # compact
    ]

    eladid.DIDURL_FromString.restype = ctypes.c_void_p # DIDURL*
    eladid.DIDURL_FromString.argtypes = [
        ctypes.c_char_p,    # idstring
        ctypes.c_void_p,    # DID* ref
    ]

    eladid.DIDURL_GetDid.restype = ctypes.c_void_p # DID*
    eladid.DIDURL_GetDid.argtypes = [
        ctypes.c_void_p,    # DIDURL*
    ]

    eladid.DID_FromString.restype = ctypes.c_void_p # DID*
    eladid.DID_FromString.argtypes = [
        ctypes.c_char_p,    # idstring
    ]

    eladid.DID_ToString.restype = ctypes.c_char_p
    eladid.DID_ToString.argtypes = [
        ctypes.c_void_p,    # DID*
        ctypes.c_char_p,    # idstring
        ctypes.c_size_t,    # len
    ]

    eladid.Mnemonic_Generate.restype = ctypes.c_char_p
    eladid.Mnemonic_Generate.argtypes = [
        ctypes.c_int,       # language
    ]

    eladid.Issuer_Create.restype = ctypes.c_void_p # Issuer*
    eladid.Issuer_Create.argtypes = [
        ctypes.c_void_p,    # did
        ctypes.c_void_p,    # didurl
        ctypes.c_void_p     # DIDStore*
    ]
 
    eladid.Issuer_CreateCredential.restype = ctypes.c_void_p # Credential*
    eladid.Issuer_CreateCredential.argtypes = [
        ctypes.c_void_p,    # issuer
        ctypes.c_void_p,    # did of the target user
        ctypes.c_void_p,    # credential id didurl
        ctypes.POINTER(ctypes.c_char_p),   # array of credential types strings
        ctypes.c_int,       # size of the credential types array
        ctypes.POINTER(Property),   # array of Property(s)
        ctypes.c_int,       # Properties array size
        ctypes.c_int64,     # expiration timestamp
        ctypes.c_char_p     # store password
    ]

    eladid.Credential_ToJson.restype = ctypes.c_char_p # JSON string
    eladid.Credential_ToJson.argtypes = [
        ctypes.c_void_p,    # Credential*
        ctypes.c_bool,      # normalized
    ]

    eladid.DIDURL_NewByDid.restype = ctypes.c_void_p # DIDURL*
    eladid.DIDURL_NewByDid.argtypes = [
        ctypes.c_void_p,    # DID*
        ctypes.c_char_p,     # fragment
    ]

    eladid.DIDError_GetMessage.restype = ctypes.c_char_p # Last error message
    eladid.DIDError_GetMessage.argtypes = [
    ]

    return eladid

