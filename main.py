from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.dcinside import Dcinside
from routers.private_mail import Mail

tags_metadata = [
    {
        "name": "FastAPI",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {
        "name": "IZ*ONE Private Mail",
        "description": "아이즈원 프라이빗 메일 API"
    },
    {
        "name": "DCINSIDE GALLERY RECOMMEND",
        "description": "디시인사이드 개념글 API"
    },
]

app = FastAPI(title="슨스's API", version="1.0.0", description="This is a very fancy project, with auto docs for the API and everything", openapi_tags=tags_metadata)

origins = ["https://iz-one.kr", "https://pm.iz-one.kr"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", description="Hello World!") # deprecated=True (사용하지 않게 될 API 표시)
async def index():
    return {"message": "Hello World"}

app.include_router(Mail, prefix="/v1/mails", tags=["IZ*ONE Private Mail"])
app.include_router(Dcinside, prefix="/v1/dcinside", tags=["DCINSIDE GALLERY RECOMMEND"])