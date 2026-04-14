"""
眩晕塔系统测试
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from stun_tower import StunEffect, StunIndicator, StunTower, update_stun_effects, draw_stun_indicators


class MockEnemy:
    """模拟敌人"""
    def __init__(self, x, y, hp=100):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.stunned = False
        self.stun_effect = None
        self.stun_resistance = 0


class TestStunEffect:
    """眩晕效果测试"""
    
    def test_stun_effect_creation(self):
        effect = StunEffect(2.0, 1.0)
        assert effect.duration == 2.0
        assert effect.intensity == 1.0
        assert effect.remaining == 2.0
        assert effect.stunned == True
    
    def test_stun_effect_update(self):
        effect = StunEffect(1.0, 1.0)
        assert effect.update(0.5) == True
        assert effect.remaining == 0.5
        assert effect.update(0.6) == False
    
    def test_stun_effect_progress(self):
        effect = StunEffect(2.0, 1.0)
        effect.update(1.0)
        assert effect.get_progress() == 0.5


class TestStunIndicator:
    """眩晕指示器测试"""
    
    def test_indicator_creation(self):
        indicator = StunIndicator.create(100, 100, 2.0, 1.0)
        assert indicator.x == 100
        assert indicator.y == 100
        assert indicator.duration == 2.0
        assert indicator.remaining == 2.0
    
    def test_indicator_update(self):
        indicator = StunIndicator(100, 100, 1.0, 1.0)
        assert indicator.update(0.5) == True
        assert indicator.remaining == 0.5
        assert indicator.update(0.6) == False
    
    def test_indicator_clear(self):
        StunIndicator.clear_all()
        assert len(StunIndicator._instances) == 0


class TestStunTower:
    """眩晕塔测试"""
    
    def test_stun_tower_creation(self):
        tower = StunTower(100, 100, level=1)
        assert tower.x == 100
        assert tower.y == 100
        assert tower.level == 1
        assert tower.damage == 5
        assert tower.range == 100
    
    def test_stun_tower_level2(self):
        tower = StunTower(100, 100, level=2)
        assert tower.damage == 8
        assert tower.range == 120
    
    def test_stun_tower_level3(self):
        tower = StunTower(100, 100, level=3)
        assert tower.damage == 12
        assert tower.range == 150
        assert tower.aoe_radius == 50
    
    def test_find_targets(self):
        tower = StunTower(100, 100, level=1)
        enemies = [
            MockEnemy(50, 100),   # 距离50，在范围内
            MockEnemy(150, 100),  # 距离50，在范围内
            MockEnemy(300, 300),  # 距离282，超出范围
        ]
        
        targets = tower._find_targets(enemies)
        assert len(targets) == 2
    
    def test_attack(self):
        tower = StunTower(100, 100, level=1)
        enemy = MockEnemy(50, 100, hp=100)
        enemies = [enemy]
        projectiles = []
        
        tower._attack(enemies, projectiles)
        
        assert enemy.hp < 100  # 受到伤害
        assert enemy.stunned == True  # 被眩晕
        assert enemy.stun_effect is not None


class TestIntegration:
    """集成测试"""
    
    def test_update_stun_effects(self):
        enemy = MockEnemy(100, 100, hp=100)
        enemy.stun_effect = StunEffect(1.0, 1.0)
        
        update_stun_effects([enemy], 0.5)
        
        assert enemy.stunned == True
        assert enemy.stun_effect.remaining == 0.5
    
    def test_stun_resistance(self):
        """测试眩晕抗性"""
        tower = StunTower(100, 100, level=3)
        enemy = MockEnemy(50, 100, hp=100)
        enemy.stun_resistance = 0.5  # 50%抗性
        
        tower._attack([enemy], [])
        
        # 2秒眩晕 * (1-0.5) = 1秒实际眩晕
        assert enemy.stun_effect.remaining <= 1.1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])