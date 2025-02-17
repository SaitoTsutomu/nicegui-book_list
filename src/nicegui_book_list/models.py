"""モデル"""

from tortoise import fields, models


class Author(models.Model):
    """著者モデル

    :ivar id: 主キー
    :ivar name: 著者名
    """

    id: fields.IntField = fields.IntField(primary_key=True)
    name: fields.CharField = fields.CharField(max_length=255)


class Book(models.Model):
    """書籍モデル

    :ivar id: 主キー
    :ivar author: 著者
    :ivar title: 書籍名
    """

    id: fields.IntField = fields.IntField(primary_key=True)
    author: fields.ForeignKeyField = fields.ForeignKeyField("models.Author", related_name="books")
    title: fields.CharField = fields.CharField(max_length=255)
