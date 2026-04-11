"""
额外特效系统测试
"""
import sys
sys.path.insert(0, 'src')

import pygame
pygame.init()

from extra_effects import TowerAttackTrailEffect, GoldRainEffect


class TestTowerAttackTrailEffect:
    """攻击拖尾特效测试"""
    
    def test_trail_init(self):
        trail = TowerAttackTrailEffect((100, 100), (200, 200))
        assert trail.start_pos == (100, 100)
        assert trail.end_pos == (200, 200)
        assert trail.active == True
        assert trail.max_life == 0.3
        
    def test_trail_update(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.1)
        assert trail.life == 0.1
        assert trail.active == True
        
    def test_trail_fade(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.2)
        # 进度应为 ~0.67
        progress = trail.life / trail.max_life
        assert 0.6 < progress < 0.8
        
    def test_trail_finish(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.5)
        assert trail.active == False


class TestGoldRainEffect:
    """金币雨特效测试"""
    
    def test_gold_rain_init(self):
        rain = GoldRainEffect(800, 600, count=20)
        assert len(rain.coins) == 20
        assert rain.max_life == 3.0
        assert rain.active == True
        
    def test_gold_rain_update(self):
        rain = GoldRainEffect(800, 600, count=10)
        rain.update(0.5)
        assert rain.life == 0.5
        
    def test_gold_rain_fall(self):
        rain = GoldRainEffect(800, 600, count=5)
        initial_y = [c['y'] for c in rain.coins]
        rain.update(1.0)
        final_y = [c['y'] for c in rain.coins]
        # 所有金币都应该往下掉
        assert all(final_y[i] > initial_y[i] for i in range(5))
        
    def test_gold_rain_finish(self):
        rain = GoldRainEffect(800, 600, count=5)
        rain.update(5.0)
        assert rain.active == False