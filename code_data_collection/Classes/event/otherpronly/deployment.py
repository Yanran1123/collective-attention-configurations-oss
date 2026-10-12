import mongoengine


class Deployment(mongoengine.EmbeddedDocument):

    creator = mongoengine.StringField(required=True)
    creatorType = mongoengine.StringField(required=True)
    createdAt = mongoengine.DateTimeField(required=True)
    updatedAt = mongoengine.DateTimeField(requied=True)

    # Identifies the oid of the deployment commit, even if the commit has been deleted.
    commitOid = mongoengine.StringField(required=True)

    task = mongoengine.StringField()  # The deployment task
    databaseId = mongoengine.IntField()
    description = mongoengine.StringField()
    payload = mongoengine.StringField()  # Extra information that a deployment system might need
    environment = mongoengine.StringField()  # The last environment to which this deployment was made
    originalEnvironment = mongoengine.StringField()  # The original environment to which this deployment was made.
    state = mongoengine.StringField()  # The current state of the deployment
    """
    DeploymentState
    The possible states for a deployment status.
    Values
    
    ERROR
    The deployment experienced an error.
    
    FAILURE
    The deployment has failed.
    
    INACTIVE
    The deployment is inactive.
    
    IN_PROGRESS
    The deployment is in progress.
    
    PENDING
    The deployment is pending.
    
    QUEUED
    The deployment is queued
    
    SUCCESS
    The deployment was successful.
    """



