"""
report_generator.py
生成岗位匹配分析报告 (HTML)
模板: templates/report_template.html
"""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
import os
from app.core.config import settings


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
REPORT_DIR = Path(settings.reports_directory)


def generate_report(data: dict) -> str:
    """
    渲染匹配分析报告
    参数:
        data (dict): {
            "resume_name": "张三",
            "job_title": "后端工程师",
            "company": "ACME科技",
            "location": "上海",
            "similarity_score": 0.86,
            "analysis": "张三的技能与岗位高度匹配...",
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Docker"],
            "recommendations": "建议加强容器化相关经验。"
        }
    返回:
        报告HTML文件路径
    """

    # 确保目录存在
    os.makedirs(REPORT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("report_template.html")

    render_data = {
        **data,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "score_percent": int(data.get("similarity_score", 0) * 100)
    }

    html_content = template.render(render_data)

    # 报告文件路径
    filename = f"{data['resume_name']}_{data['job_title']}_匹配报告.html"
    report_path = REPORT_DIR / filename

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return str(report_path)
