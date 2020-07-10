import datetime
from mongoengine import StringField, DictField, DateTimeField, Document, BooleanField

class EmailValidationStatus(object):
      PENDING = "Pending"
      WAITING_RESPONSE = "Waiting for response"
      APPROVED = "Approved"
      REJECTED = "Rejected"

class EmailValidationTx(Document):
    transactionId = StringField(max_length=40)
    email = StringField(max_length=128)
    did = StringField(max_length=128)
    status = StringField(max_length=32)
    reason = StringField(max_length=128)
    isEmailSent=BooleanField()
    verifiableCredential = DictField()
    created = DateTimeField()
    modified = DateTimeField(default=datetime.datetime.utcnow)

    def __repr__(self):
        return str(self.as_dict())

    def as_dict(self):
        return {
            "transactionId": str(self.transactionId),
            "did": self.did,
            "email": self.email,
            "status": self.status,
            "reason": self.reason,
            "isEmailSent": self.isEmailSent,
            "verifiableCredential": self.verifiableCredential,
            "created": str(self.created),
            "modified": str(self.modified)
        }

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = datetime.datetime.utcnow()
        self.modified = datetime.datetime.utcnow()
        return super(EmailValidationTx, self).save(*args, **kwargs)