import mongoengine


class Topic(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    # The number of users who have starred this topic
    stargazerCount = mongoengine.IntField(required=True)

    # The HTTP path for this repository-topic
    resourcePath = mongoengine.StringField(required=True)
    # The HTTP URL for this repository-topic
    url = mongoengine.StringField(required=True)
