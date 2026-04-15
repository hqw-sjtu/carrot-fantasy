"""
Attack Rhythm System Tests - 塔攻击节奏系统测试
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
from src.attack_rhythm import AttackRhythm, RhythmManager, get_rhythm_manager


@pytest.fixture(scope="module")
def pygame_init():
    if not pygame.get_init():
        pygame.init()
    yield


class MockTower:
    """模拟防御塔"""
    def __init__(self):
        self.x = 400
        self.y = 300
        self.range = 150


class TestAttackRhythm:
    """攻击节奏测试套件"""
    
    def test_rhythm_creation(self, pygame_init):
        rhythm = AttackRhythm()
        assert rhythm is not None
        assert not rhythm.active
        assert rhythm.rhythm_interval == 0.5
        assert len(rhythm.rings) == 0
        
    def test_rhythm_activation(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower, 0.3)
        
        assert rhythm.active
        assert rhythm.tower == tower
        assert rhythm.rhythm_interval == 0.3
        assert rhythm.elapsed == 0.0
        
    def test_rhythm_deactivation(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower)
        rhythm.deactivate()
        
        assert not rhythm.active
        assert rhythm.tower is None
        assert len(rhythm.rings) == 0
        
    def test_rhythm_update(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower, 0.2)
        
        # 触发脉冲
        rhythm.update(0.25)
        assert len(rhythm.rings) == 1
        
    def test_rhythm_pulse_generation(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower, 0.1)
        
        # 多次更新触发脉冲
        for _ in range(5):
            rhythm.update(0.15)
            
        assert len(rhythm.rings) >= 1
        
    def test_rhythm_brightness_cycle(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower, 0.5)
        
        rhythm.update(0.0)
        b1 = rhythm.brightness
        
        rhythm.update(0.25)
        b2 = rhythm.brightness
        
        assert b1 != b2  # 亮度应该变化
        
    def test_rings_fade_out(self, pygame_init):
        tower = MockTower()
        rhythm = AttackRhythm()
        rhythm.activate(tower, 0.1)
        
        rhythm.update(0.15)  # 触发脉冲
        ring = rhythm.rings[0]
        
        rhythm.update(0.5)  # 让环老化
        assert ring['alpha'] < 255


class TestRhythmManager:
    """节奏管理器测试套件"""
    
    def test_manager_singleton(self, pygame_init):
        m1 = get_rhythm_manager()
        m2 = get_rhythm_manager()
        assert m1 is m2
        
    def test_manager_register_tower(self, pygame_init):
        manager = RhythmManager()
        manager.clear()
        
        tower = MockTower()
        manager.register_tower(tower, 0.2)
        
        rhythm = manager.get_rhythm(tower)
        assert rhythm is not None
        assert rhythm.active
        assert rhythm.rhythm_interval == 0.2
        
    def test_manager_unregister_tower(self, pygame_init):
        manager = RhythmManager()
        manager.clear()
        
        tower = MockTower()
        manager.register_tower(tower)
        manager.unregister_tower(tower)
        
        rhythm = manager.get_rhythm(tower)
        assert rhythm is None
        
    def test_manager_update(self, pygame_init):
        manager = RhythmManager()
        manager.clear()
        
        tower = MockTower()
        manager.register_tower(tower, 0.1)
        manager.update(0.15)
        
        rhythm = manager.get_rhythm(tower)
        assert len(rhythm.rings) >= 1
        
    def test_manager_clear(self, pygame_init):
        manager = RhythmManager()
        
        tower = MockTower()
        manager.register_tower(tower)
        manager.clear()
        
        assert len(manager.rhythms) == 0
        
    def test_manager_enable_disable(self, pygame_init):
        manager = RhythmManager()
        manager.enabled = False
        
        tower = MockTower()
        manager.register_tower(tower, 0.1)
        manager.update(0.15)
        
        rhythm = manager.get_rhythm(tower)
        assert len(rhythm.rings) == 0  # 未启用时不产生脉冲
        
        manager.enabled = True
        manager.update(0.15)
        
        assert len(rhythm.rings) >= 1