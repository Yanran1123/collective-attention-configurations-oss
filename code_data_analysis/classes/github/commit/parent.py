import mongoengine


class Parent(mongoengine.EmbeddedDocument):
    # GitObjectId of the parent commit
    oid = mongoengine.StringField(required=True)
    # url used to get the commit information through GitHub REST API v3
    restUrl = mongoengine.StringField()
    # The HTTP url of the parent commit
    url = mongoengine.StringField()
