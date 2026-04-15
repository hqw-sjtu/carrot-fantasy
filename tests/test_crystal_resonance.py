"""
保卫萝卜 - 水晶共鸣系统测试
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from crystal_resonance import CrystalResonance, get_resonance_system, reset_resonance_system


class MockTower:
    """模拟防御塔"""
    def __init__(self, tid, name, x, y, damage=10, attack_speed=1.0, range_=100):
        self.id = tid
        self.name = name
        self.x = x
        self.y = y
        self.damage = damage
        self.attack_speed = attack_speed
        self.range = range_


class TestCrystalResonance:
    """水晶共鸣系统测试"""
    
    def setup_method(self):
        """每个测试前重置系统"""
        reset_resonance_system()
        self.resonance = get_resonance_system()
        
    def test_resonance_init(self):
        """测试初始化"""
        assert self.resonance is not None
        assert len(self.resonance.active_resonances) == 0
        assert len(self.resonance.resonance_bonuses) == 0
        
    def test_resonance_threshold(self):
        """测试共鸣阈值"""
        assert self.resonance.RESONANCE_THRESHOLD == 1  # 改为1：1个邻居即触发
        
    def test_bonus_coefficients(self):
        """测试加成系数"""
        assert self.resonance.BONUS_DAMAGE == 0.15
        assert self.resonance.BONUS_ATTACK_SPEED == 0.10
        assert self.resonance.BONUS_RANGE == 0.08
        
    def test_single_tower_no_resonance(self):
        """单塔不触发共鸣"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100)
        }
        
        bonuses = self.resonance.calculate_resonance(towers, 1)
        assert bonuses["damage"] == 0
        assert bonuses["attack_speed"] == 0
        
    def test_different_type_no_resonance(self):
        """不同类型塔不触发共鸣"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100),
            2: MockTower(2, "炮塔", 150, 150)
        }
        
        bonuses = self.resonance.calculate_resonance(towers, 1)
        assert bonuses["damage"] == 0
        
    def test_same_type_adjacent_resonance(self):
        """同类型相邻塔触发共鸣"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100),
            2: MockTower(2, "箭塔", 120, 100),  # 距离20，在阈值内
        }
        
        bonuses = self.resonance.calculate_resonance(towers, 1)
        assert bonuses["damage"] > 0
        assert bonuses["attack_speed"] > 0
        
    def test_multiple_tower_resonance(self):
        """多塔共鸣加成累积"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100),
            2: MockTower(2, "箭塔", 120, 100),
            3: MockTower(3, "箭塔", 140, 100),
        }
        
        bonuses = self.resonance.calculate_resonance(towers, 1)
        # 2个相邻塔 = 2级共鸣
        assert bonuses["damage"] == 2 * 0.15  # 0.30
        assert bonuses["attack_speed"] == 2 * 0.10  # 0.20
        assert bonuses["range"] == 2 * 0.08  # 0.16
        
    def test_update_all_resonances(self):
        """测试批量更新共鸣"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100),
            2: MockTower(2, "箭塔", 120, 100),
            3: MockTower(3, "炮塔", 200, 200),
        }
        
        self.resonance.update_all_resonances(towers)
        
        assert len(self.resonance.active_resonances) > 0
        
    def test_apply_bonus(self):
        """测试应用共鸣加成"""
        tower = MockTower(1, "箭塔", 100, 100)
        
        self.resonance.resonance_bonuses[1] = {
            "damage": 0.15,
            "attack_speed": 0.10,
            "range": 0.08
        }
        
        damage = self.resonance.apply_bonus(tower, "damage", 100)
        assert abs(damage - 115) < 0.01  # 浮点数近似比较
        
    def test_resonance_colors(self):
        """测试共鸣颜色配置"""
        assert "箭塔" in self.resonance.resonance_colors
        assert "炮塔" in self.resonance.resonance_colors
        assert "魔法塔" in self.resonance.resonance_colors
        assert "冰霜塔" in self.resonance.resonance_colors
        
    def test_singleton_pattern(self):
        """测试单例模式"""
        r1 = get_resonance_system()
        r2 = get_resonance_system()
        assert r1 is r2
        
    def test_reset_system(self):
        """测试系统重置"""
        r1 = get_resonance_system()
        r1.active_resonances.add(1)
        
        reset_resonance_system()
        r2 = get_resonance_system()
        
        assert len(r2.active_resonances) == 0
        assert r1 is not r2
        
    def test_far_towers_no_resonance(self):
        """距离过远不触发共鸣"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100, range_=100),
            2: MockTower(2, "箭塔", 500, 500),  # 距离约565像素，超过阈值
        }
        
        bonuses = self.resonance.calculate_resonance(towers, 1)
        assert bonuses["damage"] == 0
        
    def test_get_bonus(self):
        """测试获取特定加成"""
        self.resonance.resonance_bonuses[1] = {"damage": 0.15}
        
        bonus = self.resonance.get_bonus(1, "damage")
        assert bonus == 0.15
        
        # 不存在的塔
        bonus = self.resonance.get_bonus(999, "damage")
        assert bonus == 0.0


class TestResonanceParticleSystem:
    """共鸣粒子系统测试"""
    
    def setup_method(self):
        reset_resonance_system()
        self.resonance = get_resonance_system()
        
    def test_particle_init(self):
        """测试粒子系统初始化"""
        assert len(self.resonance.resonance_particles) == 0
        
    def test_particle_update(self):
        """测试粒子更新"""
        towers = {
            1: MockTower(1, "箭塔", 100, 100),
            2: MockTower(2, "箭塔", 120, 100),
        }
        
        self.resonance.update_all_resonances(towers)
        self.resonance.update_particles(towers, 0.016)  # ~60fps
        
        # 粒子应该被创建
        assert len(self.resonance.resonance_particles) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])