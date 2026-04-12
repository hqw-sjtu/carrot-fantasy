"""测试Boss血条系统"""
import pytest
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None


class MockMonster:
    """模拟怪物用于测试"""
    def __init__(self, health=500, name="TestBoss"):
        self.health = health
        self.max_health = 500
        self.x = 400
        self.y = 300
        self.alive = True
        self.name = name


def test_boss_hp_bar_init():
    """测试Boss血条初始化"""
    from boss_hp_bar import BossHPBar
    monster = MockMonster()
    bar = BossHPBar(monster)
    assert bar.monster == monster
    assert bar.max_width == 200
    assert bar.height == 20


def test_boss_hp_bar_update():
    """测试Boss血条更新"""
    from boss_hp_bar import BossHPBar
    monster = MockMonster()
    bar = BossHPBar(monster)
    bar.update(0.1)
    assert bar.show_timer > 0


def test_boss_warning_init():
    """测试Boss警告初始化"""
    from boss_hp_bar import BossWarningEffect
    warning = BossWarningEffect(800, 600)
    assert warning.active == False
    assert warning.duration == 2.0


def test_boss_warning_activate():
    """测试Boss警告激活"""
    from boss_hp_bar import BossWarningEffect
    warning = BossWarningEffect(800, 600)
    warning.activate()
    assert warning.active == True
    assert warning.timer == 0


def test_boss_warning_expire():
    """测试Boss警告过期"""
    from boss_hp_bar import BossWarningEffect
    warning = BossWarningEffect(800, 600)
    warning.activate()
    warning.update(3.0)  # 超过duration
    assert warning.active == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
