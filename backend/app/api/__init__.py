"""API 模块 - 聚合所有 FastAPI 路由。"""

from .routes import router as router
from .routes_kb import router as router_kb
from .routes_resume import router as routes_resume
from .routes_match import router as routes_match


__all__ = ["router", "router_kb", "routes_resume", "routes_match"]
