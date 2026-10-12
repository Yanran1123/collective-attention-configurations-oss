import datetime
import mongoengine

# todo Need to fetch all the associated commitComments?


class CommitCommentThread(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    commitOid = mongoengine.StringField(required=True)
    path = mongoengine.StringField()
    position = mongoengine.IntField()

    # The pull request this commit comment thread belongs to
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    # Use first 50; Check whether the count is bigger than 50; raise Exception if yes
    # record hasNextPage and endCursor
    commitCommentCount = mongoengine.IntField(required=True)

    # # todo Delete this filed when the commitCommentIds are collected?
    # commitComments = mongoengine.EmbeddedDocumentListField(CommitCommentSimple)

    # All the commitComments belongs to this thread
    commitCommentIds = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'events.commitCommentThread',
        'indexes': [
            {'fields': ['repository', 'number'], 'name': "pr_index"}
        ]
    }
