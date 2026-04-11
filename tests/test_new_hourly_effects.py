# -*- coding: utf-8 -*-
"""新增特效测试 - 护盾、波纹"""

import sys
sys.path.insert(0, 'src')

import pytest
from extra_effects import ShieldEffect, RippleEffect


class TestShieldEffect:
    """护盾特效测试"""
    
    def test_shield_init(self):
        """测试护盾初始化"""
        effect = ShieldEffect(100, 100)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.active == True
        assert effect.life == 0
        
    def test_shield_update(self):
        """测试护盾更新"""
        effect = ShieldEffect(100, 100)
        effect.update(0.1)
        assert effect.life > 0
        assert effect.active == True
        
    def test_shield_expire(self):
        """测试护盾过期"""
        effect = ShieldEffect(100, 100)
        effect.max_life = 0.2  # 手动修改
        effect.update(0.3)
        assert effect.active == False
        
    def test_shield_rotation(self):
        """测试护盾旋转"""
        effect = ShieldEffect(100, 100)
        initial_rotation = effect.rotation
        effect.update(0.1)
        assert effect.rotation > initial_rotation
        
    def test_shield_draw(self, monkeypatch):
        """测试护盾绘制(不崩溃)"""
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((200, 200))
        effect = ShieldEffect(100, 100)
        effect.update(0.1)
        effect.draw(screen)  # 不应崩溃
        pygame.quit()


class TestRippleEffect:
    """波纹特效测试"""
    
    def test_ripple_init(self):
        """测试波纹初始化"""
        effect = RippleEffect(100, 100)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.active == True
        assert effect.life == 0
        
    def test_ripple_update(self):
        """测试波纹更新"""
        effect = RippleEffect(100, 100)
        effect.update(0.1)
        assert effect.life > 0
        
    def test_ripple_expire(self):
        """测试波纹过期"""
        effect = RippleEffect(100, 100)
        effect.max_life = 0.3  # 手动修改
        effect.update(0.5)
        assert effect.active == False
        
    def test_ripple_draw(self, monkeypatch):
        """测试波纹绘制(不崩溃)"""
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((200, 200))
        effect = RippleEffect(100, 100)
        effect.update(0.1)
        effect.draw(screen)
        pygame.quit()