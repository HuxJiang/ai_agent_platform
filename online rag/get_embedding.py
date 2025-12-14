from http import HTTPStatus
import dashscope
import os

# 从环境或 .env 中读取密钥
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

def get_embedding(text):
    response = dashscope.TextEmbedding.call(
        model='text-embedding-v1',
        input=text
    )
    if response.status_code == HTTPStatus.OK:
        return response.output['embeddings'][0]['embedding']
    else:
        raise Exception(f"Embedding failed: {response.code} - {response.message}")



