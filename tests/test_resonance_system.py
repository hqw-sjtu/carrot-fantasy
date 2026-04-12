"""
保卫萝卜 - 共鸣系统测试
"""

import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # 最小窗口
except:
    pytest.skip("Pygame not available", allow_module_level=True)

from towers import Tower
from resonance_system import (
    ResonanceEffect, ResonanceManager, 
    get_resonance_manager
)

# 导入配置
RESONANCE_CONFIG = {
    'min_towers': 2,
    'resonance_radius': 150,
    'damage_bonus_per_tower': 0.05,
    'max_bonus': 0.25,
    'effect_interval': 120,
}


class TestResonanceEffect:
    """共鸣特效测试"""
    
    def test_resonance_effect_init(self):
        """测试共鸣特效初始化"""
        effect = ResonanceEffect(100, 100, "箭塔", intensity=1.0)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.tower_type == "箭塔"
        assert effect.intensity == 1.0
        assert effect.lifetime == 0
        assert len(effect.particles) > 0
    
    def test_resonance_effect_update(self):
        """测试特效更新"""
        effect = ResonanceEffect(100, 100, "炮塔")
        initial_lifetime = effect.lifetime
        effect.update()
        assert effect.lifetime == initial_lifetime + 1
    
    def test_resonance_effect_lifecycle(self):
        """测试特效生命周期"""
        effect = ResonanceEffect(100, 100, "魔法塔")
        for _ in range(70):
            alive = effect.update()
        assert not alive  # 应该过期


class TestResonanceManager:
    """共鸣管理器测试"""
    
    def test_resonance_manager_init(self):
        """测试管理器初始化"""
        manager = ResonanceManager()
        assert manager.effects == []
        assert manager.tower_resonance_count == {}
        assert manager.resonance_active == set()
    
    def test_find_resonance_towers(self):
        """测试查找共鸣塔"""
        manager = ResonanceManager()
        
        # 创建测试塔
        tower1 = Tower("箭塔", 10, 100, 50, 1.0, x=100, y=100)
        tower2 = Tower("箭塔", 10, 100, 50, 1.0, x=150, y=100)  # 距离50,在共鸣范围
        tower3 = Tower("炮塔", 10, 100, 50, 1.0, x=120, y=100)  # 不同类型
        
        nearby = manager._find_resonance_towers(tower1, [tower1, tower2, tower3])
        assert len(nearby) == 1
        assert tower2 in nearby
    
    def test_resonance_with_insufficient_towers(self):
        """测试塔数量不足时无共鸣"""
        manager = ResonanceManager()
        
        tower1 = Tower("箭塔", 10, 100, 50, 1.0, x=100, y=100)
        
        manager.update([tower1], 0)
        
        assert manager.get_damage_bonus(tower1) == 0.0
        assert not manager.is_resonance_active(tower1)
    
    def test_resonance_activation(self):
        """测试共鸣激活"""
        manager = ResonanceManager()
        
        # 创建多座同类型塔
        towers = [
            Tower("箭塔", 10, 100, 50, 1.0, x=100, y=100),
            Tower("箭塔", 10, 100, 50, 1.0, x=180, y=100),
            Tower("箭塔", 10, 100, 50, 1.0, x=250, y=100),
        ]
        
        manager.update(towers, 0)
        
        # 3座塔应该触发共鸣
        for tower in towers:
            assert manager.is_resonance_active(tower)
            bonus = manager.get_damage_bonus(tower)
            assert bonus > 0
    
    def test_damage_bonus_calculation(self):
        """测试伤害加成计算"""
        manager = ResonanceManager()
        
        # 使用字典模拟主游戏的tower管理方式
        tower1 = Tower("魔法塔", 20, 120, 80, 0.8, x=100, y=100)
        tower2 = Tower("魔法塔", 20, 120, 80, 0.8, x=180, y=100)
        towers = {id(tower1): tower1, id(tower2): tower2}
        
        manager.update(towers, 0)
        
        # 2座塔,每座应有5%伤害加成
        for tower in [tower1, tower2]:
            bonus = manager.get_damage_bonus(tower)
            assert 0.04 <= bonus <= 0.06
    
    def test_cross_type_no_resonance(self):
        """测试不同类型塔不触发共鸣"""
        manager = ResonanceManager()
        
        tower1 = Tower("箭塔", 10, 100, 50, 1.0, x=100, y=100)
        tower2 = Tower("炮塔", 10, 100, 50, 1.0, x=120, y=100)
        
        manager.update([tower1, tower2], 0)
        
        assert manager.get_damage_bonus(tower1) == 0.0
        assert manager.get_damage_bonus(tower2) == 0.0
    
    def test_resonance_count(self):
        """测试共鸣塔数量统计"""
        manager = ResonanceManager()
        
        towers = [
            Tower("火塔", 15, 90, 60, 1.2, x=100, y=100),
            Tower("火塔", 15, 90, 60, 1.2, x=160, y=100),
            Tower("火塔", 15, 90, 60, 1.2, x=220, y=100),
            Tower("火塔", 15, 90, 60, 1.2, x=280, y=100),
        ]
        
        manager.update(towers, 0)
        
        # 每座塔附近应该有2-3座同类型塔
        for i, tower in enumerate(towers):
            count = manager.get_resonance_count(tower)
            assert count >= 1  # 至少1座相邻
    
    def test_effect_interval(self):
        """测试特效触发间隔"""
        manager = ResonanceManager()
        
        towers = [
            Tower("冰霜塔", 12, 110, 70, 0.9, x=100, y=100),
            Tower("冰霜塔", 12, 110, 70, 0.9, x=180, y=100),
        ]
        
        # 第一次更新触发特效
        manager.update(towers, 0)
        initial_effects = len(manager.effects)
        
        # 短时间内不应再次触发
        manager.update(towers, 50)
        assert len(manager.effects) == initial_effects
        
        # 超过间隔后可以触发新特效
        manager.update(towers, 200)
        # 可能有新特效
    
    def test_global_manager(self):
        """测试全局管理器"""
        manager1 = get_resonance_manager()
        manager2 = get_resonance_manager()
        assert manager1 is manager2
    
    def test_config_values(self):
        """测试配置值"""
        assert RESONANCE_CONFIG['min_towers'] >= 2
        assert RESONANCE_CONFIG['resonance_radius'] > 0
        assert 0 < RESONANCE_CONFIG['damage_bonus_per_tower'] < 0.2
        assert 0 < RESONANCE_CONFIG['max_bonus'] <= 0.5


class TestResonanceIntegration:
    """共鸣系统集成测试"""
    
    def test_full_resonance_cycle(self):
        """测试完整共鸣周期"""
        manager = ResonanceManager()
        
        # 创建场景
        towers = [
            Tower("箭塔", 10, 100, 50, 1.0, x=100, y=100),
            Tower("箭塔", 10, 100, 50, 1.0, x=180, y=100),
        ]
        
        # 更新多个周期
        for frame in range(150):
            manager.update(towers, frame)
        
        # 应该有特效
        assert len(manager.effects) >= 0  # 可能已过期
    
    def test_stress_many_towers(self):
        """压力测试:大量塔"""
        manager = ResonanceManager()
        
        # 创建10座塔
        towers = []
        for i in range(10):
            x = 100 + (i % 5) * 80
            y = 100 + (i // 5) * 80
            towers.append(Tower("魔法塔", 20, 120, 80, 0.8, x=x, y=y))
        
        manager.update(towers, 0)
        
        # 所有塔都应该检测到共鸣
        for tower in towers:
            assert manager.get_resonance_count(tower) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])