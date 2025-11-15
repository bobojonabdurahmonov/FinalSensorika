from fastapi import FastAPI
from models import *

# === FastAPI app ===
app = FastAPI()


@app.get("/")
async def root():
    return {"msg": "success"}


# ============================
#      👉  POST /add
#  Ma’lumot qo‘shish
# ============================
@app.post("/add")
async def add_post(data: PostCreate):
    post = Post.create(
        region=data.region,
        district=data.district,
        area=data.area,
        index=data.index
    )
    return {"msg": "added", "id": post.id}


# ============================
#      👉  GET /find?index=100017
# ============================
@app.get("/find")
async def find_by_index(index: int):
    try:
        data = Post.get(Post.index == index)
        return {
            "region": data.region,
            "district": data.district,
            "area": data.area,
            "index": data.index
        }
    except Post.DoesNotExist:
        return {"error": "Not found"}


# ============================
#      👉  GET /search?region=...&district=...
# ============================
@app.get("/search")
async def search(region: str = None, district: str = None):
    query = Post.select()

    if region:
        query = query.where(Post.region == region)

    if district:
        query = query.where(Post.district == district)

    return [{"region": p.region, "district": p.district, "area": p.area, "index": p.index} for p in query]


# ============================
#      👉  GET /regions
# ============================
@app.get("/regions")
async def get_regions():
    regions = Post.select(Post.region).distinct()
    return [r.region for r in regions]


# ============================
#      👉  GET /districts?region=Toshkent
# ============================
@app.get("/districts")
async def get_districts(region: str):
    data = Post.select().where(Post.region == region)
    districts = set([d.district for d in data])
    return list(districts)
