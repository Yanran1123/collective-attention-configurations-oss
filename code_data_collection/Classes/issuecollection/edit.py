import mongoengine


class Edit(mongoengine.EmbeddedDocument):
    editor = mongoengine.StringField()
    editorType = mongoengine.StringField()

    createdAt = mongoengine.DateTimeField(required=True)  # When the object was created
    editedAt = mongoengine.DateTimeField(required=True)  # When this content was edited
    updatedAt = mongoengine.DateTimeField(required=True)  # when the object was last updated
    deletedAt = mongoengine.DateTimeField()  # When the object was deleted
    deletedBy = mongoengine.StringField()
    deletedByType = mongoengine.StringField()  # Which type of actor deleted the content

    diff = mongoengine.StringField()  # A summary of the changes for this edit
