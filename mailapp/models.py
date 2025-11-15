from peewee import *
from pydantic import BaseModel

# === Database ===
db = SqliteDatabase("post_index.db")


class Post(Model):
    region = CharField()      # Viloyat
    district = CharField()    # Tuman
    area = CharField()        # Mahalla / hudud
    index = IntegerField()    # Pochta indeksi

    class Meta:
        database = db

db.connect()
db.create_tables([Post])



# ==== Schemas ====
class PostCreate(BaseModel):
    region: str
    district: str
    area: str
    index: int
