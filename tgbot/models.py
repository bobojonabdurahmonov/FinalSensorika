from peewee import *

# Initialize the database
db = SqliteDatabase("subscriptions.db")

class Subscriptions(Model):
    user_id = IntegerField()
    nick = CharField(max_length=200)
    amount = IntegerField()
    term = DateTimeField()

    class Meta:
        database = db

db.connect()
db.create_tables([Subscriptions])
