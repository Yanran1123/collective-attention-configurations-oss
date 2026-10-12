import mongoengine


class ChangedFile(mongoengine.EmbeddedDocument):
    
    path = mongoengine.StringField(required=True)  # Corresponding to filename in GitHub REST API v3

    additions = mongoengine.IntField(required=True)
    deletions = mongoengine.IntField(required=True)
    
    # ******************
    # The following info are get from GitHub REST API v3 --> repo --> get a commit

    # sha of the file; GUESS: if the file is deleted it does not have oid
    oid = mongoengine.StringField()
    # E.g., modified, added
    # todo check what the VALUES of status are
    status = mongoengine.StringField()
    blobUrl = mongoengine.StringField()  # HTML url
    rawUrl = mongoengine.StringField()  # HTML url
    contentsUrl = mongoengine.StringField()  # url for GitHub REST API v3 call

    # ! GUESS: Some changed files have no oid or patch, the reason may be that the files are deleted
    patch = mongoengine.StringField()  # patch text


