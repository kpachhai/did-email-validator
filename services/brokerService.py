import redis
import json

class BrokerService:
    def __init__(self):
        self.__redis = redis.Redis(host = '127.0.0.1', port = 6379)
    
    def __send_message(self, doc, channel):
        print("Send message to broker")
        self.__redis.publish(channel, json.dumps(doc))

    def send_email_response(self, doc, apiKey):
        self.__send_message(doc, "email-validator-response")

  