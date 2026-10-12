import mongoengine


class AssociatedPR(mongoengine.EmbeddedDocument):
    number = mongoengine.IntField(required=True)
    repository = mongoengine.StringField(required=True)
