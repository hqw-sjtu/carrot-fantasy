"""
保卫萝卜 - 对象池系统测试
Carrot Fantasy - Object Pool Tests
"""

import pytest
import threading
import time
from src.object_pool import (
    ObjectPool, PooledObject, Pools, 
    DamageNumberPool, ParticlePool, CoinPool,
    PoolMonitor, init_pools
)


class MockPooledObject(PooledObject):
    """测试用池化对象"""
    
    def __init__(self):
        self.value = 0
        self.reset_called = False
        
    def reset(self):
        self.value = 0
        self.reset_called = True


class TestObjectPool:
    """对象池测试"""
    
    def test_pool_init(self):
        """测试池初始化"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        assert pool._max_size == 10
        assert pool._created_count == 0
        assert pool._reused_count == 0
        
    def test_acquire_creates_new(self):
        """测试获取新对象"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        obj = pool.acquire()
        assert obj is not None
        assert isinstance(obj, MockPooledObject)
        assert pool._created_count == 1
        
    def test_acquire_reuses(self):
        """测试复用对象"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        obj1 = pool.acquire()
        obj1.value = 42
        pool.release(obj1)
        
        obj2 = pool.acquire()
        assert obj2 is obj1
        assert pool._reused_count == 1
        assert pool._created_count == 1
        
    def test_release_resets_object(self):
        """测试释放时重置对象"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        obj = pool.acquire()
        obj.value = 999
        pool.release(obj)
        
        assert obj.value == 0
        assert obj.reset_called
        
    def test_max_size_limit(self):
        """测试池大小限制"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=2)
        
        obj1 = pool.acquire()
        obj2 = pool.acquire()
        obj3 = pool.acquire()  # 超过最大值
        
        pool.release(obj1)
        pool.release(obj2)
        pool.release(obj3)  # 超过最大值，不应被回收
        
        stats = pool.get_stats()
        assert stats['pool_size'] <= 2
        
    def test_clear(self):
        """测试清空池"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        for _ in range(5):
            obj = pool.acquire()
            pool.release(obj)
            
        pool.clear()
        stats = pool.get_stats()
        assert stats['pool_size'] == 0
        
    def test_stats(self):
        """测试统计信息"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=10)
        
        # 基本acquire/release操作
        obj = pool.acquire()
        pool.release(obj)
        
        stats = pool.get_stats()
        assert 'created' in stats
        assert 'reused' in stats
        assert 'pool_size' in stats
        assert stats['max_size'] == 10
        assert 'reuse_rate' in stats


class TestPools:
    """预定义池测试"""
    
    def test_create_pool(self):
        """测试创建命名池"""
        pool = Pools.create_pool('test', lambda: MockPooledObject(), 5)
        assert pool is not None
        assert Pools.get_pool('test') is pool
        
    def test_get_nonexistent(self):
        """测试获取不存在的池"""
        assert Pools.get_pool('nonexistent') is None
        
    def test_acquire_release(self):
        """测试获取释放命名对象"""
        Pools.create_pool('test_acquire', lambda: MockPooledObject(), 5)
        
        obj = Pools.acquire('test_acquire')
        assert obj is not None
        
        Pools.release('test_acquire', obj)
        
    def test_release_nonexistent(self):
        """测试释放到不存在的池"""
        Pools.release('nonexistent', None)  # 不应崩溃
        
    def test_get_all_stats(self):
        """测试获取所有池统计"""
        Pools.create_pool('stats_test', lambda: MockPooledObject(), 5)
        Pools.acquire('stats_test')
        
        stats = Pools.get_all_stats()
        assert 'stats_test' in stats


class TestPooledObject:
    """池化对象基类测试"""
    
    def test_base_reset(self):
        """测试基类reset方法"""
        obj = PooledObject()
        obj.reset()  # 不应崩溃
        
    def test_custom_reset(self):
        """测试自定义reset"""
        obj = MockPooledObject()
        obj.value = 100
        obj.reset()
        assert obj.value == 0


class TestPoolMonitor:
    """池监控测试"""
    
    def test_enable_disable(self):
        """测试启用禁用"""
        PoolMonitor.enable()
        assert PoolMonitor.is_enabled()
        
        PoolMonitor.disable()
        assert not PoolMonitor.is_enabled()
        
    def test_get_report_empty(self):
        """测试空池报告"""
        init_pools()  # 初始化
        report = PoolMonitor.get_report()
        assert report is not None


class TestConcurrentAccess:
    """并发访问测试"""
    
    def test_thread_safety(self):
        """测试线程安全"""
        pool = ObjectPool(lambda: MockPooledObject(), max_size=50)
        errors = []
        
        def worker():
            try:
                for _ in range(20):
                    obj = pool.acquire()
                    time.sleep(0.001)
                    pool.release(obj)
            except Exception as e:
                errors.append(e)
                
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        assert len(errors) == 0