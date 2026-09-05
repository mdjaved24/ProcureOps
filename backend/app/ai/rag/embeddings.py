from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings
import os

os.environ['HF_TOKEN']=settings.HF_TOKEN


@lru_cache(maxsize=1)
def get_embeddings()->HuggingFaceEmbeddings:
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )

    return embeddings