"""
保卫萝卜 - 新增特效测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from particle_system import DiamondSparkle, GoldRainEffect


class TestDiamondSparkle:
    """钻石闪烁特效测试"""
    
    def test_diamond_sparkle_init(self):
        """测试钻石特效初始化"""
        d = DiamondSparkle(100, 100)
        assert d.max_life == 30
        assert len(d.diamonds) == 6
        assert d.life == d.max_life
    
    def test_diamond_sparkle_update(self):
        """测试钻石特效更新"""
        d = DiamondSparkle(100, 100)
        result = d.update(16)
        assert result is True
        assert d.life < d.max_life
    
    def test_diamond_sparkle_lifecycle(self):
        """测试钻石特效生命周期"""
        d = DiamondSparkle(100, 100)
        for _ in range(50):
            if not d.update(16):
                break
        assert d.life <= 0


class TestGoldRainEffect:
    """金币雨特效测试"""
    
    def test_gold_rain_init(self):
        """测试金币雨初始化"""
        g = GoldRainEffect(200, 200, count=10)
        assert g.max_life == 60
        assert len(g.coins) == 10
    
    def test_gold_rain_update(self):
        """测试金币雨更新"""
        g = GoldRainEffect(200, 200, count=10)
        result = g.update(16)
        assert result is True
    
    def test_gold_rain_delays(self):
        """测试金币延迟下落"""
        g = GoldRainEffect(200, 200, count=5)
        # 初始时部分金币应该有延迟
        delayed = sum(1 for c in g.coins if c['delay'] > 0)
        assert delayed > 0