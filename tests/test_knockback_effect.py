# -*- coding: utf-8 -*-
"""击退效果系统测试"""
import pytest
import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from knockback_effect import KnockbackEffect, KnockbackManager, get_knockback_manager, apply_knockback


class MockTarget:
    """模拟目标对象"""
    def __init__(self, x=100, y=100):
        self.x = x
        self.y = y


class TestKnockbackEffect:
    """击退效果测试"""
    
    def test_effect_creation(self):
        """测试击退效果创建"""
        target = MockTarget()
        effect = KnockbackEffect(target, (1, 0), 30, 0.2)
        assert effect.target is target
        assert effect.direction == (1, 0)
        assert effect.distance == 30
        assert effect.duration == 0.2
        assert effect.elapsed == 0
        
    def test_direction_stored(self):
        """测试方向存储"""
        target = MockTarget()
        effect = KnockbackEffect(target, (3, 4), 25)
        # 方向在add_knockback中归一化，这里验证方向被正确保存
        assert effect.direction == (3, 4)
        
    def test_effect_update_progress(self):
        """测试击退进度更新"""
        target = MockTarget()
        effect = KnockbackEffect(target, (1, 0), 100, 0.2)
        effect.update(0.1)
        assert target.x > 100
        
    def test_effect_completion(self):
        """测试击退完成"""
        target = MockTarget()
        effect = KnockbackEffect(target, (1, 0), 30, 0.1)
        finished = effect.update(0.15)
        assert finished is True


class TestKnockbackManager:
    """击退管理器测试"""
    
    def test_manager_singleton(self):
        """测试单例模式"""
        m1 = get_knockback_manager()
        m2 = get_knockback_manager()
        assert m1 is m2
        
    def test_add_effect(self):
        """测试添加击退效果"""
        manager = get_knockback_manager()
        manager.clear()
        target = MockTarget()
        manager.add_knockback(target, (1, 0), 20)
        assert len(manager.effects) == 1
        
    def test_clear_all(self):
        """测试清除所有效果"""
        manager = get_knockback_manager()
        manager.clear()
        manager.add_knockback(MockTarget(), (1, 0), 20)
        manager.add_knockback(MockTarget(), (0, 1), 20)
        manager.clear()
        assert len(manager.effects) == 0


class TestApplyKnockback:
    """便捷函数测试"""
    
    def test_apply_from_attacker(self):
        """测试从攻击者位置推开"""
        manager = get_knockback_manager()
        manager.clear()
        target = MockTarget(100, 100)
        apply_knockback(target, (50, 100), 30)
        assert len(manager.effects) == 1