"""モデル"""

from tortoise import fields, models


class Author(models.Model):
    """著者"""

    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)


class Book(models.Model):
    """書籍"""

    id = fields.IntField(primary_key=True)
    author = fields.ForeignKeyField("models.Author", related_name="books")
    title = fields.CharField(max_length=255)
