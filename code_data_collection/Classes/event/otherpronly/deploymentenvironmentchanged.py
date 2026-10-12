import datetime
import mongoengine

from Classes.event.otherpronly.deployment import Deployment


class DeploymentEnvironmentChanged(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    actor = mongoengine.StringField()
    actorType = mongoengine.StringField()
    createdAt = mongoengine.DateTimeField(required=True)

    # The deployment status that updated the deployment environment.
    updateState = mongoengine.StringField(required=True)

    deployment = mongoengine.EmbeddedDocumentField(Deployment)

    # Associated pull request
    subjectType = mongoengine.StringField(required=True)
    repository = mongoengine.StringField(required=True)
    number = mongoengine.IntField(required=True)
    subjectId = mongoengine.ObjectIdField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'events.deploymentEnvironmentChanged',
        'indexes': [
            {'fields': ['repository', 'number', 'createdAt'], 'name': "timeline_index"}
        ]
    }
