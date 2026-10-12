import datetime

import mongoengine


class RepoAssociation(mongoengine.EmbeddedDocument):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    repo_owner_name = mongoengine.StringField(required=True)
    association = mongoengine.StringField(required=True)

