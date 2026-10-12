import mongoengine


class RepoDescription(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField()

    db1Id = mongoengine.ObjectIdField(required=True)
    nameWithOwner = mongoengine.StringField(required=True)

    # Default branch
    defaultBranch = mongoengine.StringField()
    defaultBranchCommitOid = mongoengine.StringField()  # The most recent commit in our database

    owner = mongoengine.StringField(required=True)
    # Return the type of the owner: user or organization
    ownerType = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    createdAt = mongoengine.DateTimeField(required=True)
    description = mongoengine.StringField()

    # The number of kilobytes this repository occupies on disk
    diskUsage = mongoengine.IntField(required=True)
    primaryLanguage = mongoengine.StringField()
    # The total size in Bytes of files written in coding languages; languageSize = node["languages"]["totalSize"]
    languageSize = mongoengine.IntField(required=True)

    forkCount = mongoengine.IntField(required=True)
    stargazerCount = mongoengine.IntField(required=True)
    watcherCount = mongoengine.IntField(required=True)

    releaseCount = mongoengine.IntField(required=True)
    topicCount = mongoengine.IntField(required=True)
    languageCount = mongoengine.IntField(required=True)
    licenseKey = mongoengine.StringField()
    licenseName = mongoengine.StringField()
    licensePseudo = mongoengine.BooleanField()

    # Based on the actors that have done some action for the repository
    userCount = mongoengine.IntField()
    botCount = mongoengine.IntField()
    alienCount = mongoengine.IntField()
    organizationCount = mongoengine.IntField()
    enterpriseCount = mongoengine.IntField()
    mannequinCount = mongoengine.IntField()

    innovativeOnly_userCount = mongoengine.IntField()
    innovativeOnly_botCount = mongoengine.IntField()
    innovativeOnly_alienCount = mongoengine.IntField()
    innovativeOnly_organizationCount = mongoengine.IntField()
    innovativeOnly_enterpriseCount = mongoengine.IntField()
    innovativeOnly_mannequinCount = mongoengine.IntField()

    supportiveOnly_userCount = mongoengine.IntField()
    supportiveOnly_botCount = mongoengine.IntField()
    supportiveOnly_alienCount = mongoengine.IntField()
    supportiveOnly_organizationCount = mongoengine.IntField()
    supportiveOnly_enterpriseCount = mongoengine.IntField()
    supportiveOnly_mannequinCount = mongoengine.IntField()

    bothInnoSupp_userCount = mongoengine.IntField()
    bothInnoSupp_botCount = mongoengine.IntField()
    bothInnoSupp_alienCount = mongoengine.IntField()
    bothInnoSupp_organizationCount = mongoengine.IntField()
    bothInnoSupp_enterpriseCount = mongoengine.IntField()
    bothInnoSupp_mannequinCount = mongoengine.IntField()

    issueCount = mongoengine.IntField()
    prCount = mongoengine.IntField()

    # Note that all the innovtiveAction count are calculated by prConnections__repository
    innovativeActionCount = mongoengine.IntField()
    supportiveActionCount = mongoengine.IntField()

    user_innovativeActionCount = mongoengine.IntField()
    user_supportiveActionCount = mongoengine.IntField()

    bot_innovativeActionCount = mongoengine.IntField()
    bot_supportiveActionCount = mongoengine.IntField()

    alien_innovativeActionCount = mongoengine.IntField()
    alien_supportiveActionCount = mongoengine.IntField()

    organization_innovativeActionCount = mongoengine.IntField()
    organization_supportiveActionCount = mongoengine.IntField()

    enterprise_innovativeActionCount = mongoengine.IntField()
    enterprise_supportiveActionCount = mongoengine.IntField()

    mannequin_innovativeActionCount = mongoengine.IntField()
    mannequin_supportiveActionCount = mongoengine.IntField()

    meta = {
        'db_alias': 'analysis',
        'collection': 'repos_info_2539',
        'indexes': [
            {'fields': ['owner', 'name'], 'name': "basic_index"},
            {'fields': ['nameWithOwner'], 'name': "repository_index"}
        ]
    }
