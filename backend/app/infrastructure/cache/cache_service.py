import json
from typing import Any

from app.infrastructure.cache.redis_client import redis_client


class CacheService:

    @staticmethod
    def get(key:str)->Any|None:
        value = redis_client.get(key)

        if value is None:
            return None

        return json.loads(value)


    @staticmethod
    def set(
        key: str,
        value: Any,
        ttl_seconds: int,
    ) -> None:
        redis_client.set(
            key,
            json.dumps(value),
            ex=ttl_seconds,
        )


    @staticmethod
    def delete(key: str)->None:
        redis_client.delete(key)


    @staticmethod
    def exists(key:str)->bool:
        return bool(redis_client.exists(key))


    @staticmethod
    def invalidate_policy(
        policy_code: str,
        version: str,
    ) -> None:
        key = f"policy:{policy_code}:v{version}"

        redis_client.delete(key)

    

