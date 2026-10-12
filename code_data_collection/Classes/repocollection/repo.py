import mongoengine
import datetime

from Classes.repocollection.language import Language
from Classes.repocollection.license import License
from Classes.repocollection.release import Release
from Classes.repocollection.topic import Topic


class Repo(mongoengine.Document):

    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    owner = mongoengine.StringField(required=True)
    # Return the type of the owner: user or organization
    ownerType = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    nameWithOwner = mongoengine.StringField(required=True)
    createdAt = mongoengine.DateTimeField(required=True)
    description = mongoengine.StringField()
    # some repo that are deleted do not have homepage url, so cannot be required
    # if I set the Field type as URLField, there would be issues, so I set it as StringField
    homepageUrl = mongoengine.StringField()

    # -----------------------------------------------------
    # THIS BLOCK: Less likely to change over time

    # name field of defaultBranchRef
    defaultBranch = mongoengine.StringField(required=True)
    primaryLanguage = mongoengine.StringField()

    # The number of kilobytes this repository occupies on disk
    diskUsage = mongoengine.IntField(required=True)
    # Identify the primary key from the database
    databaseId = mongoengine.IntField()

    # ----------------------------------------------------
    # FROM HERE: Information that changes over time

    forkCount = mongoengine.IntField(required=True)
    stargazerCount = mongoengine.IntField(required=True)
    watcherCount = mongoengine.IntField(required=True)

    isArchived = mongoengine.BooleanField(required=True)
    isLocked = mongoengine.BooleanField(required=True)
    isMirror = mongoengine.BooleanField(required=True)
    isTemplate = mongoengine.BooleanField(required=True)
    mergeCommitAllowed = mongoengine.BooleanField(required=True)

    # Embedded document lists
    releaseCount = mongoengine.IntField(required=True)
    releases = mongoengine.EmbeddedDocumentListField(Release)
    topicCount = mongoengine.IntField(required=True)
    topics = mongoengine.EmbeddedDocumentListField(Topic)
    languageCount = mongoengine.IntField(required=True)
    # The total size in Bytes of files written in that language
    languageSize = mongoengine.IntField(required=True)
    # A list of all languages used in the repo
    languages = mongoengine.EmbeddedDocumentListField(Language)

    # Embedded document
    license = mongoengine.EmbeddedDocumentField(License)

    meta = {
        'db_alias': 'core',
        'collection': 'repos',
        'indexes': [
            {'fields': ['owner', 'name'], 'name': "basic_index"}
        ]
    }

