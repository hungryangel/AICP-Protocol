# aicp/security.py
import time, asyncio, os, jwt
from dataclasses import dataclass
from typing import List

class AuthError(Exception): ...

@dataclass
class Claims:
    sub: str
    tenant: str
    roles: List[str]
    scopes: List[str]

def verify_jwt(token: str, secret: str, audience: str | None = None) -> Claims:
    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"], audience=audience, options={"require": ["exp","sub"]})
        return Claims(
            sub=decoded["sub"],
            tenant=decoded.get("tenant","default"),
            roles=decoded.get("roles",[]),
            scopes=decoded.get("scopes",[]),
        )
    except Exception as e:
        raise AuthError(str(e))

def require_scopes(claims: Claims, needed: list[str]):
    if not set(needed).issubset(set(claims.scopes)):
        raise AuthError(f"insufficient_scope: need {needed} have {claims.scopes}")

class RateLimiter:
    """간단 토큰버킷 레이트리밋 (세션 단위)"""
    def __init__(self, rate_per_sec: float, burst: int = 20):
        self.rate = rate_per_sec
        self.capacity = burst
        self.tokens = burst
        self.updated = time.monotonic()

    async def take(self, n: int = 1):
        now = time.monotonic()
        delta = now - self.updated
        self.updated = now
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        if self.tokens >= n:
            self.tokens -= n
            return True
        # 부족하면 필요한 만큼만 대기
        wait = (n - self.tokens) / self.rate
        await asyncio.sleep(max(wait, 0))
        self.tokens = 0
        return True
