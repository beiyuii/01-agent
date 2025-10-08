"""
resume_loader.py
负责读取解析好的简历 JSON 文件
"""

from pathlib import Path
import json
from fastapi import HTTPException
from app.core.config import settings


def load_resume_json(filename: str) -> dict:
    """从 uploads 目录读取简历 JSON 文件"""
    file_path = Path(settings.uploads_directory) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="简历文件不存在")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
