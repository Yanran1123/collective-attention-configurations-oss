import datetime

import mongoengine

from Classes.commit.parent import Parent
from Classes.issuecollection.changedfile import ChangedFile


class Commit(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    oid = mongoengine.StringField(required=True)
    # abbreviatedOid = mongoengine.StringField()

    # todo need to figure out how to get information about coauthors
    author = mongoengine.StringField()
    authorType = mongoengine.StringField()
    # The object ID of Actor class
    authorId = mongoengine.ObjectIdField()

    committer = mongoengine.StringField()
    committerType = mongoengine.StringField()
    # The object ID of Actor class
    committerId = mongoengine.ObjectIdField()

    authoredByCommitter = mongoengine.BooleanField()

    authoredDate = mongoengine.DateTimeField(required=True)
    committedDate = mongoengine.StringField(required=True)

    repository = mongoengine.StringField()

    # Peripheral information

    # # resourcePath removed the "https://github.com" part, compared with commitUrl
    # commitResourcePath = mongoengine.StringField()
    commitUrl = mongoengine.StringField(required=True)
    message = mongoengine.StringField(required=True)

    treeOid = mongoengine.StringField(required=True)

    commentCount = mongoengine.IntField(required=True)

    # Changes made by the commit; needs to be done by the call: Get a Commit
    # https://developer.github.com/v3/repos/commits/#get-a-commit
    additions = mongoengine.IntField()
    deletions = mongoengine.IntField()

    changedFiles = mongoengine.EmbeddedDocumentListField(ChangedFile)
    # Added because I use GraphQL to fetch a commit that has too many changed files, 
    # but all the commits fetched by REST API v3 do not have this data field
    changedFilesCount = mongoengine.IntField()

    # Information about parent commits
    parents = mongoengine.EmbeddedDocumentListField(Parent)

    # Associated PRs
    associatedPRs = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'commits',
        'indexes': [
            {'fields': ['repository', 'authoredDate'], 'name': "timeline_index"},
            {'fields': ['repository', 'oid'], 'name': "GitObjectId_index"}
        ]
    }





