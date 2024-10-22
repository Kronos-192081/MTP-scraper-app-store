from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app_store import AppStore
import random
from datetime import datetime
import json

app = FastAPI()

class Item(BaseModel):
    country: str
    app_name: str
    app_id: int
    how_many: int
    offset: int

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

@app.get("/heartbeat")
def read_root():
    return {"status": "OK"}

@app.post("/get_reviews")
def fetch_reviews(item: Item):
    try:
        app_store = AppStore(country=item.country, app_name=item.app_name, app_id=item.app_id, log_level="INFO")
        app_store.update_offset(item.offset)
        app_store.review(how_many=item.how_many, after=datetime(2021, 12, 31))
        ret = {}
        ret["data"] = app_store.reviews
        ret["offset"] = app_store._request_offset
        
        json_data = json.dumps(ret, cls=DateTimeEncoder)

        return JSONResponse(content=json.loads(json_data), status_code=200)

    except Exception as e:
        ret = {}
        ret["data"] = []
        ret["offset"] = 0
        ret["error"] = str(e)

        return JSONResponse(content=ret, status_code=404)
