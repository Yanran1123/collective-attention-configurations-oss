import datetime

import mongoengine

from classes.github.commit.parent import Parent
from classes.github.issuecollection.changedfile import ChangedFile


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
    committedDate = mongoengine.StringField(required=True)  # Should be datetime?
    """
    https://docs.microsoft.com/en-us/azure/devops/repos/git/git-dates?view=azure-devops
    Git tracks two dates in commits: author date and commit date. In addition, Azure DevOps Services and TFS track when 
        a commit was first pushed to the server.

    Author date: when a commit was originally authored. Typically, when someone first ran git commit.
    Commit date: when a commit was applied to the branch. In many cases it is the same as the author date. 
        Sometimes it differs: if a commit was amended, rebased, or applied by someone other than the author as part of 
        a patch. In those cases, the date will be when the rebase happened or the patch was applied.
    Push date: when a commit was pushed to the remote repository in question. This date is specific to the 
        remote version control system you are using, and won't be available in your local repository.
    """

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





