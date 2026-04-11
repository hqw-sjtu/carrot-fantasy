"""
新增特效测试 - 破碎/冰冻爆炸
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from extra_effects import ShatterEffect, FreezeBlastEffect


class TestShatterEffect:
    """破碎特效测试"""
    
    def test_shatter_init(self):
        effect = ShatterEffect(100, 100, color=(255, 100, 100), count=12)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.color == (255, 100, 100)
        assert effect.count == 12
        assert len(effect.fragments) == 12
        assert effect.active is True
    
    def test_shatter_update(self):
        effect = ShatterEffect(100, 100)
        initial_vy = effect.fragments[0]['vy']
        effect.update(0.016)  # 1帧
        assert effect.life > 0
        # 验证重力效果 - vy变化(增加300*dt)
        assert abs(effect.fragments[0]['vy'] - initial_vy - 300*0.016) < 1
    
    def test_shatter_finish(self):
        effect = ShatterEffect(100, 100)
        effect.update(1.0)  # 超过max_life
        assert effect.active is False
    
    def test_shatter_draw(self):
        import pygame
        pygame.init()
        screen = pygame.Surface((200, 200))
        effect = ShatterEffect(100, 100)
        effect.update(0.1)
        effect.draw(screen)  # 不应崩溃
        pygame.quit()


class TestFreezeBlastEffect:
    """冰冻爆炸特效测试"""
    
    def test_freeze_blast_init(self):
        effect = FreezeBlastEffect(100, 100, color=(100, 200, 255), count=20)
        assert effect.x == 100
        assert effect.y == 100
        assert effect.color == (100, 200, 255)
        assert effect.count == 20
        assert len(effect.crystals) == 20
        assert effect.active is True
    
    def test_freeze_blast_update(self):
        effect = FreezeBlastEffect(100, 100)
        initial_vx = effect.crystals[0]['vx']
        effect.update(0.016)
        # 验证减速效果
        assert abs(effect.crystals[0]['vx']) < abs(initial_vx)
    
    def test_freeze_blast_finish(self):
        effect = FreezeBlastEffect(100, 100)
        effect.update(1.5)  # 超过max_life
        assert effect.active is False
    
    def test_freeze_blast_draw(self):
        import pygame
        pygame.init()
        screen = pygame.Surface((200, 200))
        effect = FreezeBlastEffect(100, 100)
        effect.update(0.1)
        effect.draw(screen)  # 不应崩溃
        pygame.quit()