import redis
import json
import time
import requests

callbackUrl = "http://localhost:8080/callback"
channel = 'email-validator'
channelResponse = 'email-validator-response'

client = redis.Redis(host = '127.0.0.1', port = 6379)

p = client.pubsub()
p.subscribe(channel)

while True:
    message = p.get_message()

    if message and not message['data'] == 1:
        message = message['data'].decode('utf-8')
        doc = json.loads(message)
        print(f'Email-Validator Received message: {message}')
        time.sleep(10)
        print(f'Send email response: Success')
        response = {
            "transactionId": doc["transactionId"],
            "verifiedCredential":{
                "header": {
                    "specification": "SPECIFICATION-EXAMPLE",
                    "operation": "OPERATTION-EXAMPLE"
                },
                "payload": "eyJpZCI6ImRpZDplbGFzdG9zOmlpNFpDejhMWVJIYXgzWUI3OVNXSmNNTTJoamFIVDM1S04iLCJwdWJsaWNLZXkiOlt7ImlkIjoiI3ByaW1hcnkiLCJwdWJsaWNLZXlCYXNlNTgiOiJ0MUNpRHFWMlBFRFNGOEN2ZXRFaXBqUEpaUFBuVGJSN2Iyd2cxZTVBYW83bSJ9XSwiYXV0aGVudGljYXRpb24iOlsiI3ByaW1hcnkiXSwidmVyaWZpYWJsZUNyZWRlbnRpYWwiOlt7ImlkIjoiI3RlY2gudHV1bS5hY2FkZW15IiwidHlwZSI6WyJBcHBsaWNhdGlvblByb2ZpbGVDcmVkZW50aWFsIiwiR2FtZUFwcGxpY2F0aW9uUHJvZmlsZUNyZWRlbnRpYWwiLCJTZWxmUHJvY2xhaW1lZENyZWRlbnRpYWwiXSwiaXNzdWFuY2VEYXRlIjoiMjAyMC0wNC0yOVQwNDowNDo0MFoiLCJleHBpcmF0aW9uRGF0ZSI6IjIwMjUtMDQtMjhUMDQ6MDQ6NDBaIiwiY3JlZGVudGlhbFN1YmplY3QiOnsiYWN0aW9uIjoiTGVhcm4gRWxhc3RvcyBieSBwbGF5aW5nIGdhbWVzIGFnYWluc3QgZnJpZW5kcyIsImFwcHBhY2thZ2UiOiJ0ZWNoLnR1dW0uYWNhZGVteSIsImFwcHR5cGUiOiJlbGFzdG9zYnJvd3NlciIsImlkZW50aWZpZXIiOiJ0ZWNoLnR1dW0uYWNhZGVteSJ9LCJwcm9vZiI6eyJ2ZXJpZmljYXRpb25NZXRob2QiOiIjcHJpbWFyeSIsInNpZ25hdHVyZSI6Ikd0aHpvdE50cVNZUzRpdEpjZkM4VFRUUVJEajRCUFNKejliS3ZuM1BPRDBQcEMtX0wyTnJaRXhTVWpjaWlhcWJMazNaOFQtWGJvcmVJcF9vNU9TbXlnIn19XSwiZXhwaXJlcyI6IjIwMjUtMDMtMTlUMTU6MzY6NTNaIiwicHJvb2YiOnsiY3JlYXRlZCI6IjIwMjAtMDQtMjlUMDQ6MDQ6NDBaIiwic2lnbmF0dXJlVmFsdWUiOiJ1OXR5QmVySVhzLUZqQ0xOdDl1MGdRMTNoSElPUGh5VC10dTVjSHBNZjBJNE1rUEpXQ1IwSXJVQk5ORjQ5WDktOE5tYXpaOXEtSWo3NkZvSVFWcDZuQSJ9fQ",
                "proof": {
                    "type": "ECDSAsecp256r1",
                    "verificationMethod": "VERIFICATION-KEY",
                    "signature": "VALIDATION-HASH"
                }
            },
            "response": "Success"
        }
        requests.post(callbackUrl, data=json.dumps(response))
        print(f'End email validation for {doc["transactionId"]}')

