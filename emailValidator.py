import redis
import json
import time
import requests

callbackUrl = "http://localhost:14514/callback"
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
            "response": "Success"
        }
        requests.post(callbackUrl, data=json.dumps(response))
        print(f'End email validation for {doc["transactionId"]}')

