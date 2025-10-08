"""服务层公共接口聚合，方便统一导入和管理。"""

from .resume_parser import parse_resume
from .resume_extractor import extract_resume_info, save_resume_json
from .embedding_utils import get_embedding, compute_similarity
from .resume_loader import load_resume_json
from .report_generator import generate_report
from .langchain_clients import DashscopeEmbeddings, get_vector_store




__all__ = [
    "parse_resume",
    "extract_resume_info",
    "save_resume_json",
    "get_embedding",
    "compute_similarity",
    "load_resume_json",
    "generate_report",
    "DashscopeEmbeddings",
    "get_vector_store",
]
