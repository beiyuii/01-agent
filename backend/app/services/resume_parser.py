"""简历解析服务模块 - 支持 PDF、DOCX、TXT 格式"""

from pdfminer.high_level import extract_text
from docx import Document


def parse_resume(file_path: str) -> str:
    """解析简历文件，根据扩展名自动选择解析方法"""
    ext = file_path.split(".")[-1].lower()
    if ext == "pdf":
        return parse_pdf(file_path)
    elif ext == "docx":
        return parse_docx(file_path)
    elif ext == "txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def parse_pdf(file_path: str) -> str:
    """解析PDF文件，提取文本内容"""
    try:
        text = extract_text(file_path)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"PDF 解析失败: {e}")


def parse_docx(file_path: str) -> str:
    """解析DOCX文件，提取段落文本"""
    try:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        raise RuntimeError(f"DOCX 解析失败: {e}")


def parse_txt(file_path: str) -> str:
    """解析TXT文件，读取文本内容"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()
