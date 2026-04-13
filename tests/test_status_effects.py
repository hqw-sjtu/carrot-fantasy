"""
状态效果系统测试 | Status Effects System Tests
"""

import pytest
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from status_effects import (
    StatusEffect, StatusEffectManager, StatusEffectType,
    TowerStatusApplier, get_status_manager
)


class MockMonster:
    """模拟怪物用于测试"""
    id_counter = 0
    
    def __init__(self):
        MockMonster.id_counter += 1
        self.id = MockMonster.id_counter
        self.x = 100
        self.y = 100
        self.speed = 50
        self.original_speed = 50
        self.frozen = 0
        self.slow_timer = 0
        self.slow_factor = 1.0
        self.burn_timer = 0
        self.poison_timer = 0
        self.health = 100
        self.max_health = 100
    
    def apply_slow(self, slow_factor, duration):
        if slow_factor < self.slow_factor:
            self.slow_factor = slow_factor
            self.speed = self.original_speed * slow_factor
        self.slow_timer = max(self.slow_timer, duration)
    
    def take_damage(self, damage):
        self.health -= damage


class TestStatusEffectType:
    """状态效果类型常量测试"""
    
    def test_effect_types_defined(self):
        assert StatusEffectType.FROZEN == "frozen"
        assert StatusEffectType.SLOW == "slow"
        assert StatusEffectType.POISON == "poison"
        assert StatusEffectType.BURN == "burn"
        assert StatusEffectType.STUN == "stun"
        assert StatusEffectType.WEAKEN == "weaken"


class TestStatusEffect:
    """单一状态效果测试"""
    
    def test_creation(self):
        effect = StatusEffect(StatusEffectType.FROZEN, 2.0, 0.8)
        assert effect.effect_type == "frozen"
        assert effect.duration == 2.0
        assert effect.intensity == 0.8
        assert not effect.applied
    
    def test_update(self):
        effect = StatusEffect(StatusEffectType.SLOW, 1.0, 1.0)
        assert effect.update(0.5) is True
        assert effect.duration < 1.0
        assert effect.update(1.0) is False
    
    def test_progress(self):
        effect = StatusEffect(StatusEffectType.POISON, 2.0, 1.0)
        effect.max_duration = 2.0
        assert effect.get_progress() == 1.0
        effect.duration = 1.0
        assert effect.get_progress() == 0.5
    
    def test_default_colors(self):
        effect = StatusEffect(StatusEffectType.BURN, 1.0)
        assert effect.color == (255, 100, 0)


class TestStatusEffectManager:
    """状态效果管理器测试"""
    
    def setup_method(self):
        self.manager = StatusEffectManager()
    
    def test_apply_new_effect(self):
        monster = MockMonster()
        result = self.manager.apply_effect(
            monster, StatusEffectType.FROZEN, 2.0, 0.8
        )
        assert result is True
        assert self.manager.has_effect(monster.id, StatusEffectType.FROZEN)
    
    def test_apply_existing_effect_extends_duration(self):
        monster = MockMonster()
        self.manager.apply_effect(monster, StatusEffectType.SLOW, 2.0, 0.5)
        
        # 再次应用同一效果
        effects = self.manager.get_active_effects(monster.id)
        original_duration = effects[0].duration
        
        self.manager.apply_effect(monster, StatusEffectType.SLOW, 3.0, 0.6)
        
        effects = self.manager.get_active_effects(monster.id)
        assert effects[0].duration == 3.0
    
    def test_update_effects(self):
        monster = MockMonster()
        self.manager.apply_effect(monster, StatusEffectType.BURN, 1.0, 0.7, damage_per_second=10)
        
        damage_stats = self.manager.update(monster, 0.5)
        # 0.5秒应该有约5点伤害
        assert 'burn' in damage_stats or damage_stats.get('burn', 0) > 0
    
    def test_clear_effects(self):
        monster = MockMonster()
        self.manager.apply_effect(monster, StatusEffectType.FROZEN, 2.0)
        self.manager.apply_effect(monster, StatusEffectType.POISON, 3.0)
        
        self.manager.clear_effects(monster.id)
        
        assert not self.manager.has_effect(monster.id, StatusEffectType.FROZEN)
        assert not self.manager.has_effect(monster.id, StatusEffectType.POISON)
    
    def test_get_active_effects(self):
        monster = MockMonster()
        self.manager.apply_effect(monster, StatusEffectType.FROZEN, 2.0)
        self.manager.apply_effect(monster, StatusEffectType.SLOW, 3.0)
        
        effects = self.manager.get_active_effects(monster.id)
        assert len(effects) == 2
    
    def test_has_effect(self):
        monster = MockMonster()
        self.manager.apply_effect(monster, StatusEffectType.FROZEN, 2.0)
        
        assert self.manager.has_effect(monster.id, StatusEffectType.FROZEN)
        assert not self.manager.has_effect(monster.id, StatusEffectType.POISON)


class TestTowerStatusApplier:
    """防御塔状态效果应用器测试"""
    
    def setup_method(self):
        self.manager = StatusEffectManager()
        self.applier = TowerStatusApplier(self.manager)
    
    def test_apply_ice_tower_effect(self):
        monster = MockMonster()
        tower = type('Tower', (), {'tower_type': 'ice_tower'})()
        
        self.applier.apply_tower_effect(tower, monster)
        
        assert self.manager.has_effect(monster.id, StatusEffectType.FROZEN)
    
    def test_apply_poison_tower_effect(self):
        monster = MockMonster()
        tower = type('Tower', (), {'tower_type': 'poison_tower'})()
        
        self.applier.apply_tower_effect(tower, monster)
        
        assert self.manager.has_effect(monster.id, StatusEffectType.POISON)
    
    def test_unknown_tower_type(self):
        monster = MockMonster()
        tower = type('Tower', (), {'tower_type': 'unknown_tower'})()
        
        result = self.applier.apply_tower_effect(tower, monster)
        # 应该没有效果
        assert len(self.manager.get_active_effects(monster.id)) == 0


class TestGlobalStatusManager:
    """全局状态效果管理器测试"""
    
    def test_get_status_manager(self):
        manager1 = get_status_manager()
        manager2 = get_status_manager()
        
        # 应该是同一个实例(单例)
        assert manager1 is manager2