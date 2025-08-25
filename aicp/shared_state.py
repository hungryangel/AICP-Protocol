from typing import Dict, Optional
try:
    from redis.asyncio import Redis  # optional
except Exception:  # redis 미설치 시
    Redis = None  # type: ignore

class SharedState:
    """
    SSoT (Single Source of Truth)
    - Redis가 있으면 Redis 백엔드 사용
    - 없으면 메모리 딕셔너리로 폴백
    """
    def __init__(self, redis: Optional["Redis"] = None):
        self.redis = redis
        self.mem: Dict[str, str] = {}
        self.key_prefix = "aicp:ssot:"

    async def set(self, key: str, value_text: str) -> None:
        if self.redis:
            await self.redis.set(self.key_prefix + key, value_text)
        else:
            self.mem[key] = value_text

    async def get(self, key: str) -> Optional[str]:
        if self.redis:
            val = await self.redis.get(self.key_prefix + key)
            if val is None: return None
            return val if isinstance(val, str) else val.decode()
        return self.mem.get(key)

    async def dump_all(self) -> Dict[str, str]:
        if self.redis:
            out: Dict[str,str] = {}
            keys = await self.redis.keys(self.key_prefix + "*")
            for k in keys:
                k_str = k if isinstance(k, str) else k.decode()
                v = await self.redis.get(k_str)
                out[k_str.replace(self.key_prefix,"")] = v if isinstance(v,str) else (v.decode() if v else "")
            return out
        return dict(self.mem)
