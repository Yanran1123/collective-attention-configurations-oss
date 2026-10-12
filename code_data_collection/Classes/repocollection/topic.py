import mongoengine


class Topic(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
