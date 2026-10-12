import mongoengine

from classes.github.commit.parent import Parent
from classes.github.issuecollection.changedfile import ChangedFile


class PrConnection(mongoengine.EmbeddedDocument):
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)


class InnovativeAction(mongoengine.Document):

    oid = mongoengine.StringField(required=True)
    actionId = mongoengine.ObjectIdField()  # id in the db1_small (MongoDB)
    actionType = mongoengine.StringField(required=True)

    authorLogin = mongoengine.StringField()  # author; For Alien, it is the email address
    authorType = mongoengine.StringField()  # authorType

    committerLogin = mongoengine.StringField()  # For Alien, it is the email address
    committerType = mongoengine.StringField()

    authoredByCommitter = mongoengine.BooleanField()

    authoredDate = mongoengine.DateTimeField(required=True)
    committedDate = mongoengine.DateTimeField(required=True)
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

    commitRepository = mongoengine.StringField()  # Can be different from associated prs
    isInDefaultBranch = mongoengine.BooleanField()  # Whether the commit is in the repository's default branch

    prConnections = mongoengine.EmbeddedDocumentListField(PrConnection)

    # Changes made by the commit; needs to be done by the call: Get a Commit
    # https://developer.github.com/v3/repos/commits/#get-a-commit
    additions = mongoengine.IntField()
    deletions = mongoengine.IntField()

    changedFiles = mongoengine.EmbeddedDocumentListField(ChangedFile)
    # Added because I use GraphQL to fetch a commit that has too many changed files,
    # but all the commits fetched by REST API v3 do not have this data field
    changedFilesCount = mongoengine.IntField()

    # -------------------------------
    # Peripheral information
    # # resourcePath removed the "https://github.com" part, compared with commitUrl
    # commitResourcePath = mongoengine.StringField()
    commitUrl = mongoengine.StringField(required=True)
    message = mongoengine.StringField(required=True)

    treeOid = mongoengine.StringField(required=True)

    commentCount = mongoengine.IntField(required=True)

    # Information about parent commits
    parents = mongoengine.EmbeddedDocumentListField(Parent)
    parentCount = mongoengine.IntField()

    # Associated PRs
    associatedPRs = mongoengine.ListField()  # a list of PullRequest object IDs

    meta = {
        'db_alias': 'analysis',
        'collection': 'innovative_actions',
        'indexes': [
            {'fields': ['commitRepository', 'isInDefaultBranch', 'committedDate'], 'name': "defaultBranchCommit_index"},
            {'fields': ['commitRepository', 'authoredDate'], 'name': "timeline_index"},
            {'fields': ['commitRepository', 'committedDate'], 'name': "timeline2_index"},
            {'fields': ['commitRepository', 'oid'], 'name': "GitObjectId_index", },
            {'fields': ['commitRepository', 'authorLogin', 'authorType', 'authoredDate'], 'name': "repo_author_index"},
            {'fields': ['prConnections.repository', 'prConnections.number', 'committedDate'], 'name': "prConnection_index"},
            {'fields': ['prConnections.repository', 'committedDate', 'authorType'], 'name': "prConnTime_index"},
            {'fields': ['prConnections.repository', 'authorLogin', 'authorType', 'committedDate'], 'name': "prAuthor_index"},
            {'fields': ['authorLogin', 'authorType', 'authoredDate'], 'name': "author_index"},
            {'fields': ['authorLogin', 'authorType', 'oid'], 'name': "author_oid_index"},
            {'fields': ['authorType'], 'name': "authorType_index"},
            {'fields': ['actionId'], 'name': "actionId_index"}
        ]
    }



