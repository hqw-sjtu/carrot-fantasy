"""
毒气塔功能测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_poison_tower_creation():
    """测试毒气塔创建"""
    import pygame
    pygame.init()
    
    from towers import Tower
    tower = Tower(
        name="毒气塔",
        damage=8,
        range=2.2,
        cost=130,
        attack_speed=0.6,
        x=100,
        y=100,
        poison_damage=3,
        poison_duration=3.0
    )
    
    assert tower.name == "毒气塔"
    assert tower.poison_damage == 3
    assert tower.poison_duration == 3.0
    pygame.quit()

def test_poison_projectile():
    """测试毒气子弹"""
    import pygame
    pygame.init()
    
    from projectiles import Projectile
    from monsters import Monster
    
    # 创建怪物
    monster = Monster(200, 100, 1.0, "green")
    monster.alive = True
    
    # 创建毒气子弹
    proj = Projectile(
        x=100, y=100,
        target=monster,
        damage=8,
        poison_damage=3,
        poison_duration=3.0
    )
    
    assert proj.poison_damage == 3
    assert proj.poison_duration == 3.0
    
    # 模拟命中
    proj.hit_target()
    
    # 验证中毒效果
    assert monster.poison_damage == 3
    assert monster.poison_timer > 0
    
    pygame.quit()

def test_poison_damage_update():
    """测试毒气持续伤害更新"""
    import pygame
    pygame.init()
    
    from monsters import Monster
    
    monster = Monster(200, 100, 1.0, "green")
    monster.alive = True
    monster.health = 100
    
    # 施加中毒效果
    monster.apply_poison(5, 2.0)  # 5伤害/秒，持续2秒
    
    assert monster.poison_damage == 5
    assert monster.poison_timer == 2.0
    
    # 更新1秒
    monster.update(1.0)
    
    # 扣除中毒伤害
    assert monster.health < 100
    assert monster.poison_timer > 0
    
    pygame.quit()

def test_config_poison_tower():
    """测试配置文件中的毒气塔"""
    import json
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    towers = config.get('towers', {})
    assert '毒气塔' in towers
    
    poison_tower = towers['毒气塔']
    assert poison_tower['cost'] == 130
    assert poison_tower['poison_damage'] == 3
    assert poison_tower['poison_duration'] == 3.0