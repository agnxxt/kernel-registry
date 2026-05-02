"""Rate Limiter - Token bucket rate limiting for agents"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting"""
    tokens: int
    last_refill: datetime = field(default_factory=datetime.now)
    capacity: int = 100


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, default_capacity: int = 100, refill_rate: int = 10):
        self.default_capacity = default_capacity
        self.refill_rate = refill_rate  # tokens per minute
        self.buckets: Dict[str, RateLimitBucket] = {}
    
    def _key(self, tenant_id: str, agent_id: str, action: str) -> str:
        return f"{tenant_id}:{agent_id}:{action}"
    
    def _refill(self, bucket: RateLimitBucket):
        """Refill tokens based on time elapsed"""
        now = datetime.now()
        elapsed = (now - bucket.last_refill).total_seconds()
        minutes = elapsed / 60
        new_tokens = int(minutes * self.refill_rate)
        bucket.tokens = min(bucket.capacity, bucket.tokens + new_tokens)
        bucket.last_refill = now
    
    def check(self, tenant_id: str, agent_id: str, action: str, limit: int = None) -> bool:
        """Check if action is allowed"""
        key = self._key(tenant_id, agent_id, action)
        
        if key not in self.buckets:
            capacity = limit or self.default_capacity
            self.buckets[key] = RateLimitBucket(capacity, capacity=capacity)
        
        bucket = self.buckets[key]
        self._refill(bucket)
        
        if bucket.tokens >= 1:
            bucket.tokens -= 1
            return True
        return False
    
    def get_remaining(self, tenant_id: str, agent_id: str, action: str) -> int:
        """Get remaining tokens"""
        key = self._key(tenant_id, agent_id, action)
        if key not in self.buckets:
            return self.default_capacity
        bucket = self.buckets[key]
        self._refill(bucket)
        return bucket.tokens
    
    def reset(self, tenant_id: str, agent_id: str = None, action: str = None):
        """Reset rate limits"""
        if agent_id and action:
            key = self._key(tenant_id, agent_id, action)
            if key in self.buckets:
                del self.buckets[key]
        elif agent_id:
            # Reset all actions for agent
            prefix = f"{tenant_id}:{agent_id}:"
            for k in list(self.buckets.keys()):
                if k.startswith(prefix):
                    del self.buckets[k]
        else:
            # Reset all
            self.buckets.clear()


__all__ = ['RateLimiter', 'RateLimitBucket']