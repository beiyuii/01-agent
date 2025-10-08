"""
简历抽取模块：使用阿里云百炼模型从原始文本中提取结构化信息。
输出格式符合统一的 Resume JSON Schema。
"""

import json
from openai import OpenAI
from app.core.config import settings
from app.utils.retry import run_with_retry


# 初始化百炼客户端
client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url
)


def extract_resume_info(text: str) -> dict:
    """
    使用 LLM 从简历文本中提取结构化信息
    返回标准化 JSON Schema 格式
    """
    prompt = f"""
        你是一名智能简历信息抽取助手。你的任务是从下列简历文本中提取关键的信息，
        并返回符合 JSON Schema 的结构化数据。

        请严格输出 JSON，不要包含额外文字。

        Schema 示例：
        {{
        "basic_info": {{
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        }},
        "education": [
            {{
            "school": "",
            "degree": "",
            "major": "",
            "start_date": "",
            "end_date": ""
            }}
        ],
        "experience": [
            {{
            "company": "",
            "role": "",
            "description": "",
            "start_date": "",
            "end_date": ""
            }}
        ],
        "skills": [],
        "projects": [
            {{
            "name": "",
            "description": "",
            "skills_used": [],
            "link": ""
            }}
        ],
        "certificates": [],
        "others": ""
        }}

        请根据简历文本提取尽可能多的结构化信息。

        简历文本如下：
        {text}
    """

    response = run_with_retry(
        client.chat.completions.create,
        model=settings.dashscope_model,
        messages=[
            {"role": "system", "content": "你是一名结构化信息抽取专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    raw_output = response.choices[0].message.content.strip()

    # 清理潜在的多余文本，确保是JSON
    json_start = raw_output.find("{")
    json_end = raw_output.rfind("}") + 1
    json_str = raw_output[json_start:json_end]

    try:
        data = json.loads(json_str)
    except Exception as e:
        raise RuntimeError(f"简历结构化解析失败：{e}\n输出内容：{raw_output}")

    return data


def save_resume_json(data: dict, save_path: str):
    """保存结构化简历到 JSON 文件"""
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
