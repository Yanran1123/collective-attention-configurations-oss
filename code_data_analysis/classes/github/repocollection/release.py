import mongoengine


class Release(mongoengine.EmbeddedDocument):
    tagName = mongoengine.StringField(required=True)
    # login information of the author
    author = mongoengine.StringField()

    # Git ObjectId of a commit
    tagCommit = mongoengine.StringField()

    name = mongoengine.StringField()
    description = mongoengine.StringField()
    url = mongoengine.StringField()

    # Time
    createdAt = mongoengine.DateTimeField()
    publishedAt = mongoengine.DateTimeField()
    updatedAt = mongoengine.DateTimeField()

    isDraft = mongoengine.BooleanField()
    isPrerelease = mongoengine.BooleanField()







