import mongoengine


class License(mongoengine.EmbeddedDocument):
    key = mongoengine.StringField(required=True)
    name = mongoengine.StringField()
    nickname = mongoengine.StringField()
    pseudoLicense = mongoengine.BooleanField()
    spdxID = mongoengine.StringField()
    url = mongoengine.StringField()
