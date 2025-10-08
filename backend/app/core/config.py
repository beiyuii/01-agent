from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 环境配置
    environment: str = Field(default="development", description="运行环境")
    debug: bool = Field(default=True, description="调试模式")
    log_level: str = Field(default="INFO", description="日志级别")
    
    # API 配置
    dashscope_api_key: str = Field(..., description="百炼API密钥")
    dashscope_model: str = Field(default="qwen3-max", description="默认使用的模型")
    dashscope_embedding_model: str = Field(
        default="text-embedding-v4",
        description="嵌入模型名称",
    )
    dashscope_base_url: Optional[str] = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="API基础URL"
    )
    
    # 数据库配置
    chroma_persist_directory: Path = Field(default=Path("./data/chroma"))
    chroma_collection_name: str = Field(default="job_postings")
    data_path: Path = Field(
        default=Path("./data/raw/data_2026信息表.csv"),
        description="原始数据文件路径"
    )
    db_path: Path = Field(
        default=Path("./data/chroma"),
        description="清洗或嵌入后的数据存储目录"
    )

    # 文件存储配置
    reports_directory: Path = Field(default=Path("./data/reports"),description="html报告")
    uploads_directory: Path = Field(default=Path("./data/uploads"),description="用户上传")
    
    # 服务配置
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)
    
    # 业务配置
    max_file_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    allowed_file_types: List[str] = Field(default_factory=lambda: ["pdf", "docx", "txt"])
    max_recommendations: int = Field(default=10)
    similarity_threshold: float = Field(default=0.6)
    
    # 缓存配置
    enable_cache: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    @field_validator("allowed_file_types", mode="before")
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    @field_validator("dashscope_api_key")
    def check_api_key(cls, v):
        if not v or v.strip() == "":
            raise ValueError("请在 .env 中配置 DASHSCOPE_API_KEY，否则无法调用百炼API")
        return v

    @field_validator("dashscope_model", "dashscope_embedding_model")
    def check_model_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("模型名称不能为空")
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        for directory in [
            self.chroma_persist_directory,
            self.db_path,
            self.reports_directory,
            self.uploads_directory,
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


# 全局配置实例
settings = Settings()

def get_settings() -> Settings:
    return settings
