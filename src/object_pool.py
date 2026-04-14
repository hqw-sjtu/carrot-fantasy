"""
保卫萝卜 - 对象池系统
Carrot Fantasy - Object Pool System
用于高性能对象复用，减少GC压力
"""

from collections import deque
from typing import TypeVar, Generic, Optional, Callable
import threading


T = TypeVar('T')


class ObjectPool(Generic[T]):
    """通用对象池"""
    
    def __init__(self, factory: Callable[[], T], max_size: int = 100):
        """
        初始化对象池
        
        Args:
            factory: 对象工厂函数
            max_size: 最大池大小
        """
        self._factory = factory
        self._max_size = max_size
        self._pool = deque()
        self._lock = threading.Lock()
        self._created_count = 0
        self._reused_count = 0
        
    def acquire(self) -> T:
        """获取对象"""
        with self._lock:
            if self._pool:
                self._reused_count += 1
                return self._pool.popleft()
            else:
                self._created_count += 1
                return self._factory()
                
    def release(self, obj: T) -> None:
        """归还对象"""
        if obj is None:
            return
        with self._lock:
            if len(self._pool) < self._max_size:
                # 重置对象状态（如果支持）
                if hasattr(obj, 'reset'):
                    try:
                        obj.reset()
                    except:
                        pass
                self._pool.append(obj)
                
    def clear(self) -> None:
        """清空对象池"""
        with self._lock:
            self._pool.clear()
            
    def get_stats(self) -> dict:
        """获取池统计信息"""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'max_size': self._max_size,
                'created': self._created_count,
                'reused': self._reused_count,
                'reuse_rate': self._reused_count / max(1, self._created_count + self._reused_count)
            }


class PooledObject:
    """池化对象基类"""
    
    def reset(self) -> None:
        """重置对象状态 - 子类实现"""
        pass


# 预定义常用对象池
class Pools:
    """预定义对象池"""
    
    _pools = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_pool(cls, name: str) -> Optional[ObjectPool]:
        """获取命名池"""
        with cls._lock:
            return cls._pools.get(name)
    
    @classmethod
    def create_pool(cls, name: str, factory: Callable, max_size: int = 100) -> ObjectPool:
        """创建命名池"""
        with cls._lock:
            if name in cls._pools:
                return cls._pools[name]
            pool = ObjectPool(factory, max_size)
            cls._pools[name] = pool
            return pool
    
    @classmethod
    def acquire(cls, name: str):
        """从池获取对象"""
        pool = cls.get_pool(name)
        if pool:
            return pool.acquire()
        return None
    
    @classmethod
    def release(cls, name: str, obj):
        """归还对象到池"""
        pool = cls.get_pool(name)
        if pool:
            pool.release(obj)
            
    @classmethod
    def get_all_stats(cls) -> dict:
        """获取所有池统计"""
        with cls._lock:
            return {name: pool.get_stats() for name, pool in cls._pools.items()}


# 伤害数字池
class DamageNumberPool(ObjectPool):
    """伤害数字对象池"""
    
    def __init__(self, max_size: int = 200):
        from src.damage_numbers import DamageNumber
        super().__init__(lambda: DamageNumber(0, 0, 0), max_size)


# 粒子池
class ParticlePool(ObjectPool):
    """粒子对象池"""
    
    def __init__(self, max_size: int = 500):
        from src.particle_system import Particle
        super().__init__(self._create_particle, max_size)
        
    @staticmethod
    def _create_particle():
        from src.particle_system import Particle
        return Particle(0, 0, (255, 255, 255))


# 金币池
class CoinPool(ObjectPool):
    """金币对象池"""
    
    def __init__(self, max_size: int = 100):
        from src.coin_flight import Coin
        super().__init__(lambda: Coin(0, 0), max_size)


# 初始化预定义池
def init_pools():
    """初始化预定义对象池"""
    Pools.create_pool('damage_number', lambda: None, 200)
    Pools.create_pool('particle', lambda: None, 500)
    Pools.create_pool('coin', lambda: None, 100)


# 性能监控
class PoolMonitor:
    """对象池性能监控"""
    
    _enabled = False
    
    @classmethod
    def enable(cls):
        cls._enabled = True
        
    @classmethod
    def disable(cls):
        cls._enabled = False
        
    @classmethod
    def is_enabled(cls) -> bool:
        return cls._enabled
    
    @classmethod
    def get_report(cls) -> str:
        """生成性能报告"""
        stats = Pools.get_all_stats()
        if not stats:
            return "对象池未初始化"
            
        lines = ["=== 对象池性能报告 ==="]
        total_created = 0
        total_reused = 0
        
        for name, data in stats.items():
            lines.append(f"\n【{name}】")
            lines.append(f"  池大小: {data['pool_size']}/{data['max_size']}")
            lines.append(f"  创建: {data['created']}, 复用: {data['reused']}")
            lines.append(f"  复用率: {data['reuse_rate']*100:.1f}%")
            total_created += data['created']
            total_reused += data['reused']
            
        if total_created + total_reused > 0:
            overall_rate = total_reused / (total_created + total_reused) * 100
            lines.append(f"\n总体复用率: {overall_rate:.1f}%")
            
        return "\n".join(lines)