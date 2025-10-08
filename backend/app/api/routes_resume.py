from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from app.core.config import settings
from app.services import parse_resume
from app.services.resume_extractor import extract_resume_info, save_resume_json

router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_DIR = Path(settings.uploads_directory)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 上传文件并返回解析后的结果
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型，仅支持 {', '.join(settings.allowed_file_types)}"
        )
    
    # 保存文件
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 解析文件内容
        content = parse_resume(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析文件失败: {e}")
    finally:
        # 清理临时文件
        file_path.unlink(missing_ok=True)

    # 调用LLM进行信息抽取
    extracted_data = extract_resume_info(content)

    # 保存 JSON
    json_path = file_path.with_suffix(".json")
    save_resume_json(extracted_data, str(json_path))

    return {
        "filename": file.filename,
        "json_file": str(json_path),
        "resume_data": extracted_data
    }
        
