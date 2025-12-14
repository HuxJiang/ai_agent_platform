# search.py
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from dashscope import TextEmbedding
import dashscope
import os

_api_key = os.getenv("DASHSCOPE_API_KEY")

# 如果未找到，尝试手动加载.env文件
if not _api_key:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            # 简单解析.env文件，只查找DASHSCOPE_API_KEY
            for line in f:
                if line.strip().startswith("DASHSCOPE_API_KEY="):
                    _api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

if not _api_key:
    raise RuntimeError(
        "DASHSCOPE_API_KEY 未设置。请在环境变量或项目根目录的 .env 文件中设置该值。"
    )
dashscope.api_key = _api_key
COLLECTION_NAME = "rag_local"
VECTOR_SIZE = 1536  # text-embedding-v1 的维度

# === 初始化客户端 ===
client = QdrantClient(host="localhost", port=6333)  # 注意：新版推荐用 host/port 而非位置参数

# === 创建 collection（安全方式）===
# 兼容不同版本 qdrant-client 的返回值：有些版本返回 bool，有些返回具有 .exists 属性的对象
res = client.collection_exists(COLLECTION_NAME)
if hasattr(res, "exists"):
    exists_flag = res.exists
else:
    exists_flag = bool(res)

if exists_flag:
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
)

# === 获取 Embedding（调用阿里云）===
def get_embedding(text: str) -> list[float]:
    resp = TextEmbedding.call(model="text-embedding-v1", input=text)
    if resp.status_code == 200:
        return resp.output["embeddings"][0]["embedding"]
    else:
        raise RuntimeError(f"DashScope embedding error: {resp.code} - {resp.message}")

# === 插入数据 ===
doc_text = "通义千问（Qwen）是阿里云研发的超大规模语言模型。"
embedding = get_embedding(doc_text)

client.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        PointStruct(
            id=1,
            vector=embedding,
            payload={"content": doc_text}
        )
    ]
)

# === 向量检索 ===
query = "Qwen 是什么？"
query_vec = get_embedding(query)

# ⭐ 关键：使用 query_points 替代 search
search_result = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vec,          # 查询向量
    limit=3                   # 返回 top-k
).points  # ⚠️ 结果在 .points 属性中！

# === 输出结果 ===
for hit in search_result:
    print(f"相似度得分: {hit.score:.4f}")
    print(f"内容: {hit.payload['content']}\n")