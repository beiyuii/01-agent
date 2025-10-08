"""岗位数据 ETL 脚本，负责数据清洗、向量化及持久化入库。"""

from pathlib import Path
import shutil
import sys

import pandas as pd
from langchain.text_splitter import CharacterTextSplitter

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import settings
from app.services import get_vector_store


# 脚本功能：
# 1. 读取数据
# 2. 数据清洗
# 3. 数据转换
# 4. 数据存储

# 读取数据并进行清洗
def load_clean_data(path: str) -> pd.DataFrame:
    """加载原始数据并进行缺失值清洗。

    Args:
        path (str): 原始 CSV/Excel 文件路径。

    Returns:
        pd.DataFrame: 清洗后的标准化数据表。
    """

    expected_columns = [
        "序号",
        "公司名称",
        "批次",
        "企业性质",
        "行业大类",
        "招聘对象",
        "招聘岗位",
        "网申状态",
        "工作地点",
        "更新时间",
        "截止时间",
        "官方公告",
        "投递方式",
        "内推码|备注",
    ]

    if str(path).endswith(".csv"):
        df = pd.read_csv(
            path,
            encoding="utf-8-sig",
            usecols=range(len(expected_columns)),
            names=expected_columns,
            header=0,
        )
    else:
        df = pd.read_excel(path, usecols=expected_columns)

    # 转化表头为标准格式（去除空格并按预期顺序排列）
    df.columns = df.columns.map(lambda col: str(col).strip())

    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "数据表缺少预期字段，请检查数据源: " + ", ".join(missing_columns)
        )

    df = df[expected_columns]

    # 数据清洗
    # 1. 对重要数据缺失的进行删除
    df = df.dropna(subset=["公司名称", "招聘岗位"])

    # 2. 重要的数据中对空值、异常值进行填充处理
    df["批次"] = df["批次"].fillna("未知")
    df["企业性质"] = df["企业性质"].fillna("未知")
    df["行业大类"] = df["行业大类"].fillna("未知")
    df["招聘对象"] = df["招聘对象"].fillna("未知")
    df["招聘岗位"] = df["招聘岗位"].fillna("未知")
    df["网申状态"] = df["网申状态"].fillna("未知")
    df["工作地点"] = df["工作地点"].fillna("未知")
    df["更新时间"] = df["更新时间"].fillna("未知")
    df["截止时间"] = df["截止时间"].fillna("未知")

    # 3. 对不重要的数据进行空值填充
    df["官方公告"] = df["官方公告"].fillna("")
    df["投递方式"] = df["投递方式"].fillna("")
    df["内推码|备注"] = df["内推码|备注"].fillna("")

    # 4. 重排序号（保证唯一 & 连续）
    df["序号"] = range(1, len(df) + 1)
    return df


# 构建文档和元数据
def build_documents(df: pd.DataFrame):
    """将岗位数据转换为文本与元数据集合。

    Args:
        df (pd.DataFrame): 结构化岗位数据。

    Returns:
        tuple[list[str], list[dict], list[str]]: 文档内容、元数据与原始 ID。
    """

    # 将岗位数据转为 documents + metadata + ids
    documents, metadatas, ids = [], [], []

    for _, row in df.iterrows():
        # 拼接成用于向量化的文本内容
        content = f"""
        公司名称: {row["公司名称"]}
        企业性质: {row["企业性质"]}
        行业大类: {row["行业大类"]}
        招聘对象: {row["招聘对象"]}
        招聘岗位: {row["招聘岗位"]}
        网申状态: {row["网申状态"]}
        投递方式: {row["投递方式"]}
        """

        metadata = {
            "job_id": f"job_{row['序号']}",
            "company": row["公司名称"],
            "title": row["招聘岗位"],
            "batch": row["批次"],
            "industry": row["行业大类"],
            "location": row["工作地点"],
            "deadline": row["截止时间"],
            "note": row["内推码|备注"],
        }

        ids.append(f"job_{row['序号']}")
        documents.append(content)
        metadatas.append(metadata)

    return documents, metadatas, ids

# 分块
def chunk_documents(documents: list, metadatas: list, ids: list):
    """对文档进行分块处理，确保向量化稳定。

    Args:
        documents (list): 原始岗位文本列表。
        metadatas (list): 与文本对应的元数据。
        ids (list): 原始岗位 ID 集合。

    Returns:
        tuple[list[str], list[dict], list[str]]: 分块后的文本、元数据与分块 ID。
    """

    # 对文档进行分块以免出现文档过长导致向量化失败
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    all_ids, all_documents, all_metadatas = [], [], []

    for i, document in enumerate(documents):
        chunks = splitter.split_text(document)
        for j, chunk in enumerate(chunks):
            base_id = metadatas[i]["job_id"]
            all_ids.append(f"{base_id}-{j}")
            all_documents.append(chunk)
            all_metadatas.append(metadatas[i])

    return all_documents, all_metadatas, all_ids

def persist_to_chroma(ids, documents, metadatas):
    """写入向量库并持久化数据。

    Args:
        ids (list): 文档分块 ID 列表。
        documents (list): 分块文本内容。
        metadatas (list): 对应元数据集合。
    """

    persist_dir = Path(settings.chroma_persist_directory)
    tmp_dir = persist_dir.with_name(persist_dir.name + "_tmp")
    backup_dir = persist_dir.with_name(persist_dir.name + "_backup")

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    store = get_vector_store(persist_directory=str(tmp_dir))
    store.add_texts(texts=documents, metadatas=metadatas, ids=ids)
    store.persist()

    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    if persist_dir.exists():
        shutil.move(str(persist_dir), str(backup_dir))

    shutil.move(str(tmp_dir), str(persist_dir))
    print(
        f"✅ 已写入 {len(ids)} 条数据到 ChromaDB ({settings.chroma_collection_name})，原始数据已备份到 {backup_dir}"
    )

# 整合运行
def run():
    """执行 ETL 主流程，包括清洗、分块与持久化。"""

    df = load_clean_data(settings.data_path)
    documents, metadatas, ids = build_documents(df)
    documents, metadatas, ids = chunk_documents(documents, metadatas, ids)

    document_count = len(documents)
    if document_count == 0:
        print("⚠️ 未找到可用文档，ETL 流程提前结束。")
        return

    print("💾 开始写入 ChromaDB ...")
    persist_to_chroma(ids, documents, metadatas)

if __name__ == "__main__":
    run()
