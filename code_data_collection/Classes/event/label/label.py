import datetime

import mongoengine


class Label(mongoengine.Document):
    dataCollectionTime = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    createdAt = mongoengine.DateTimeField()
    color = mongoengine.StringField(required=True)
    isDefault = mongoengine.BooleanField(required=True)
    description = mongoengine.StringField()
    repository = mongoengine.StringField(required=True)
    resourcePath = mongoengine.StringField(required=True)
    url = mongoengine.StringField(required=True)
    updatedAt = mongoengine.DateTimeField()

    meta = {
        'db_alias': 'core',
        'collection': 'labels',
        'indexes': [
            {'fields': ['repository', 'name', 'color'], 'name': "basic_index"},
            {'fields': ['repository', 'resourcePath'], 'name': "path_index"}
        ]
    }
