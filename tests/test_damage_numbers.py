#!/usr/bin/env python3
"""测试伤害数字系统"""

import sys
sys.path.insert(0, 'src')

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from damage_numbers import DamageNumberManager

def test_damage_numbers():
    """测试伤害数字生成和更新"""
    manager = DamageNumberManager()
    
    # 测试普通伤害
    manager.add_damage(100, 200, 50, False)
    assert len(manager.damage_numbers) == 1
    print("✓ 普通伤害数字创建成功")
    
    # 测试暴击伤害
    manager.add_damage(150, 250, 100, True)
    assert len(manager.damage_numbers) == 2
    print("✓ 暴击伤害数字创建成功")
    
    # 测试治疗
    manager.add_damage(200, 300, 30, False, is_heal=True)
    assert len(manager.damage_numbers) == 3
    print("✓ 治疗数字创建成功")
    
    # 测试更新（模拟多帧）
    for _ in range(10):
        manager.update(0.016)  # 约60fps
    
    print(f"✓ 存活数字: {len(manager.damage_numbers)}/3")
    assert len(manager.damage_numbers) == 3
    
    # 渲染测试（不显示窗口）
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    manager.draw(screen)
    pygame.quit()
    
    print("✓ 渲染测试通过")
    print("\n✅ 全部测试通过!")

if __name__ == "__main__":
    test_damage_numbers()