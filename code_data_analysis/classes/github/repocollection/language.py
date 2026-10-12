import mongoengine


class Language(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    color = mongoengine.StringField()
    # The number of bytes of code written in the language
    size = mongoengine.IntField(required=True)

