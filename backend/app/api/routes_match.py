from fastapi import APIRouter, Query, HTTPException
import numpy as np
import json
from hashlib import md5
from typing import Any
from app.services import (
    load_resume_json,
    get_embedding,
    get_vector_store,
    compute_similarity,
)
from app.core.config import settings
from openai import OpenAI
from app.services.report_generator import generate_report
from app.utils.retry import run_with_retry
from app.utils.cache import TTLCache




router = APIRouter(prefix="/match", tags=["匹配"])

llm_client = OpenAI(
    api_key=settings.dashscope_api_key,
    base_url=settings.dashscope_base_url,
)

_summary_cache = TTLCache(ttl_seconds=settings.cache_ttl)


def _clean_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        candidate = value.strip()
    else:
        candidate = str(value).strip()
    return candidate or None


def _extract_resume_sections(resume_data: dict) -> tuple[str, list[str], list[str]]:
    """从简历数据中提取技能与经历文本，过滤掉空值。"""
    skills_source = resume_data.get("skills")
    if isinstance(skills_source, list):
        skills_iterable = skills_source
    elif isinstance(skills_source, str):
        skills_iterable = [skills_source]
    elif skills_source is None:
        skills_iterable = []
    else:
        skills_iterable = [skills_source]

    skills = []
    for item in skills_iterable:
        cleaned = _clean_value(item)
        if cleaned:
            skills.append(cleaned)

    experience_source = resume_data.get("experience")
    if isinstance(experience_source, list):
        experience_iterable = experience_source
    elif isinstance(experience_source, dict):
        experience_iterable = [experience_source]
    elif experience_source is None:
        experience_iterable = []
    else:
        experience_iterable = [experience_source]

    exp_desc = []
    for item in experience_iterable:
        if isinstance(item, dict):
            cleaned = _clean_value(item.get("description"))
        else:
            cleaned = _clean_value(item)
        if cleaned:
            exp_desc.append(cleaned)

    text_parts = skills + exp_desc
    if not text_parts:
        raise HTTPException(status_code=400, detail="简历缺少技能或经历信息，无法匹配岗位")

    return " ".join(text_parts), skills, exp_desc



@router.get("/auto")
def auto_match_jobs(
    resume_file: str = Query(..., description="简历 JSON 文件名，如 resume_张三.json"),
    top_k: int = 5
):
    """自动匹配推荐岗位"""
    resume_data = load_resume_json(resume_file)
    resume_text, _, _ = _extract_resume_sections(resume_data)

    resume_embedding = get_embedding(resume_text)
    vector_store = get_vector_store()
    collection = vector_store._collection  # type: ignore[attr-defined]

    try:
        query_results = collection.query(
            query_embeddings=[resume_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"向量检索失败: {exc}") from exc

    documents = query_results.get("documents", [[]])[0]
    metadatas = query_results.get("metadatas", [[]])[0]
    distances = query_results.get("distances", [[]])[0]

    results = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        similarity = 1 - float(distance)
        results.append({
            "score": round(similarity, 4),
            "job_id": meta.get("job_id"),
            "title": meta.get("title"),
            "company": meta.get("company"),
            "location": meta.get("location"),
            "deadline": meta.get("deadline"),
            "snippet": doc[:150],
        })

    summary_prompt = f"""
请总结以下岗位推荐结果，为候选人提供简短的匹配建议。

候选人简历技能：
{resume_text}

推荐岗位（前{top_k}条）：
{json.dumps(results, ensure_ascii=False, indent=2)}
"""

    cache_key = md5(summary_prompt.encode("utf-8")).hexdigest()
    summary = _summary_cache.get(cache_key)
    if summary is None:
        try:
            llm_response = run_with_retry(
                llm_client.chat.completions.create,
                model=settings.dashscope_model,
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.4,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"生成推荐摘要失败: {exc}") from exc
        summary = llm_response.choices[0].message.content.strip()
        _summary_cache.set(cache_key, summary)

    return {
        "resume_name": resume_data.get("basic_info", {}).get("name", "未知候选人"),
        "recommendations": results,
        "summary": summary
    }


@router.get("/single")
def match_single_job(
    resume_file: str = Query(..., description="简历 JSON 文件名"),
    job_id: str = Query(..., description="目标岗位 ID")
):
    """对单个岗位进行详细匹配分析"""

    resume_data = load_resume_json(resume_file)
    resume_text, cleaned_skills, _ = _extract_resume_sections(resume_data)

    vector_store = get_vector_store()
    collection = vector_store._collection  # type: ignore[attr-defined]
    try:
        job_docs = collection.get(
            where={"job_id": job_id},
            include=["documents", "metadatas", "embeddings"],
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"岗位信息加载失败: {exc}") from exc

    if not job_docs or len(job_docs.get("documents", [])) == 0:
        raise HTTPException(status_code=404, detail="岗位未找到")

    resume_embedding = get_embedding(resume_text)
    embeddings = job_docs.get("embeddings", [])
    if embeddings is None or len(embeddings) == 0:
        raise HTTPException(status_code=404, detail="岗位缺少向量信息")

    # 选取与简历最匹配的chunk作为分析依据
    scores = [
        compute_similarity(resume_embedding, chunk_emb)
        for chunk_emb in embeddings
    ]
    best_index = int(np.argmax(scores))
    score = scores[best_index]

    jd_text = job_docs["documents"][best_index]
    job_meta = job_docs["metadatas"][best_index]

    prompt_lines = [
        "请作为一名职业顾问，对以下简历与岗位进行详细匹配分析：",
        "---",
        "【候选人技能与经历】",
        resume_text,
        "",
        "【岗位描述】",
        jd_text,
        "",
        "请输出：",
        "1. 匹配度评分（0~100）",
        "2. 匹配技能和经验",
        "3. 缺失技能",
        "4. 提升建议",
    ]
    prompt = "\n".join(prompt_lines)
    analysis_cache_key = md5(prompt.encode("utf-8")).hexdigest()
    analysis = _summary_cache.get(analysis_cache_key)
    if analysis is None:
        try:
            llm_response = run_with_retry(
                llm_client.chat.completions.create,
                model="qwen2.5-7b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"生成匹配分析失败: {exc}") from exc
        analysis = llm_response.choices[0].message.content.strip()
        _summary_cache.set(analysis_cache_key, analysis)

    # Step 5: 生成报告文件
    report_data = {
        "resume_name": resume_data.get("basic_info", {}).get("name", "未知候选人"),
        "job_title": job_meta.get("title"),
        "company": job_meta.get("company"),
        "location": job_meta.get("location"),
        "similarity_score": round(score, 4),
        "analysis": analysis,
        "matched_skills": cleaned_skills,
        "missing_skills": [],  # TODO: 可后续通过关键词比对生成
        "recommendations": "根据分析结果，建议进一步强化岗位相关技能。"
    }

    report_path = generate_report(report_data)


    return {
        "resume_name": report_data["resume_name"],
        "job_title": report_data["job_title"],
        "company": report_data["company"],
        "location": report_data["location"],
        "similarity_score": report_data["similarity_score"],
        "analysis": report_data["analysis"],
        "report_path": report_path
    }


def get_match_cache_stats() -> dict[str, Any]:
    """返回岗位匹配相关缓存统计。"""
    return _summary_cache.stats()
