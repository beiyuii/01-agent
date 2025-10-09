import logging

from fastapi import FastAPI
from app.api import router
from app.api import router_kb
from app.api import routes_resume
from app.api import routes_match
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

app = FastAPI(title="职位Agent系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 根据前端实际地址调整
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_kb)
app.include_router(routes_resume)
app.include_router(routes_match)



# 测试
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

