import mongoengine


class Language(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    size = mongoengine.IntField()

