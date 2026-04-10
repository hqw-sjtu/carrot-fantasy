"""
保卫萝卜 - 伤害数字系统测试
"""
import pytest
import sys
import os

# 添加 src 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pytest.skip("Pygame not available", allow_module_level=True)

from damage_numbers import DamageNumber, DamageNumberManager


def test_damage_number_init():
    """测试伤害数字初始化"""
    dmg = DamageNumber(100, 100, 50)
    assert dmg.damage == 50
    assert dmg.x == 100
    assert dmg.y == 100
    assert dmg.is_crit == False
    assert dmg.combo_count == 0


def test_damage_number_crit():
    """测试暴击伤害数字"""
    dmg = DamageNumber(100, 100, 100, is_crit=True)
    assert dmg.is_crit == True
    assert dmg.scale >= 1.5


def test_damage_number_heal():
    """测试治疗数字"""
    dmg = DamageNumber(100, 100, 50, is_heal=True)
    assert dmg.is_heal == True
    assert dmg.damage == 50


def test_damage_number_combo():
    """测试连击伤害数字"""
    dmg = DamageNumber(100, 100, 30, combo_count=5)
    assert dmg.combo_count == 5
    assert dmg.scale >= 1.5


def test_damage_number_update():
    """测试伤害数字更新"""
    dmg = DamageNumber(100, 100, 50)
    initial_y = dmg.y
    result = dmg.update(0.016)  # 1帧
    assert result == True
    assert dmg.y < initial_y  # 应该向上移动
    assert dmg.lifetime < dmg.max_lifetime


def test_damage_number_lifetime():
    """测试生命周期"""
    dmg = DamageNumber(100, 100, 50)
    # 模拟多帧更新
    for _ in range(100):
        if not dmg.update(0.016):
            break
    assert dmg.lifetime <= 0


def test_damage_number_manager():
    """测试伤害数字管理器"""
    manager = DamageNumberManager()
    assert len(manager.damage_numbers) == 0
    
    # 添加伤害数字
    manager.add_damage(100, 100, 50)
    assert len(manager.damage_numbers) == 1
    
    # 添加暴击
    manager.add_damage(200, 200, 100, is_crit=True)
    assert len(manager.damage_numbers) == 2
    
    # 更新
    manager.update(0.016)
    
    # 清理
    manager.clear()
    assert len(manager.damage_numbers) == 0


def test_damage_number_manager_combo():
    """测试连击系统"""
    manager = DamageNumberManager()
    
    # 模拟快速连击 - 通过快速调用来触发连击系统
    for i in range(5):
        manager.add_damage(100, 100, 20)
    
    assert len(manager.damage_numbers) == 5
    
    # 连击计数在manager中，不在单个伤害数字中
    assert manager.combo_count >= 1


def test_damage_number_draw():
    """测试绘制（不崩溃）"""
    manager = DamageNumberManager()
    screen = pygame.display.get_surface()
    
    # 添加各种类型伤害
    manager.add_damage(100, 100, 50)           # 普通
    manager.add_damage(200, 200, 100, is_crit=True)  # 暴击
    manager.add_damage(300, 300, 30, is_heal=True)   # 治疗
    
    # 绘制（不检查具体像素，只确保不崩溃）
    manager.draw(screen)
    pygame.display.flip()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])