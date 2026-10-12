import datetime

import mongoengine


class Team(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    organization = mongoengine.StringField(required=True)
    slug = mongoengine.StringField(required=True)  # Can use this to query a team in an organization
    combinedSlug = mongoengine.StringField(required=True)  # The slug corresponding to the organization and team

    createdAt = mongoengine.DateTimeField(required=True)
    updatedAt = mongoengine.DateTimeField(required=True)

    databaseId = mongoengine.IntField()
    avatarUrl = mongoengine.StringField()
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)

    name = mongoengine.StringField(required=True)
    # description = mongoengine.StringField()
    #
    # newTeamResourcePath = mongoengine.StringField(required=True)
    # newTeamUrl = mongoengine.StringField(required=True)
    #
    # parentTeamOrganization = mongoengine.StringField()
    # parentTeamSlug = mongoengine.StringField()
    # parentTeamCombinedSlug = mongoengine.StringField()
    #
    # privacy = mongoengine.StringField(required=True)
    # """
    # TeamPrivacy
    # The possible team privacy values.
    #
    # Values
    # SECRET
    # A secret team can only be seen by its members.
    #
    # VISIBLE
    # A visible team can be seen and @mentioned by every member of the organization.
    # """
    #
    # repositoriesResourcePath = mongoengine.StringField(required=True)
    # repositoriesUrl = mongoengine.StringField(required=True)
    # membersResourcePath = mongoengine.StringField(required=True)
    # membersUrl = mongoengine.StringField(required=True)
    # editTeamResourcePath = mongoengine.StringField(required=True)
    # editTeamUrl = mongoengine.StringField(required=True)
    # discussionsResourcePath = mongoengine.StringField(required=True)
    # discussionsUrl = mongoengine.StringField(required=True)
    # teamsResourcePath = mongoengine.StringField(required=True)
    # teamsUrl = mongoengine.StringField(required=True)
    #
    # # What algorithm is used for review assignment for this team
    # reviewRequestDelegationAlgorithm = mongoengine.StringField()
    # """
    # The possible team review assignment algorithms
    #
    # Values
    # LOAD_BALANCE
    # Balance review load across the entire team
    #
    # ROUND_ROBIN
    # Alternate reviews between each team member
    # """
    # # True if review assignment is enabled for this team
    # reviewRequestDelegationEnabled = mongoengine.BooleanField(required=True)
    # # How many team members are required for review assignment for this team
    # reviewRequestDelegationMemberCount = mongoengine.IntField()
    # # When assigning team members via delegation, whether the entire team should be notified as well.
    # reviewRequestDelegationNotifyTeam = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'teams',
        'indexes': [
            {'fields': ['organization', 'slug', 'name', 'createdAt'], 'name': "timeline_index"}
        ]
    }

