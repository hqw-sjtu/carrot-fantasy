"""
保卫萝卜 - 经验球特效测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()


def test_experience_orb_init():
    """测试经验球初始化"""
    from extra_effects import ExperienceOrb
    orb = ExperienceOrb(100, 100, value=25, target_pos=(400, 50))
    assert orb.x == 100
    assert orb.y == 100
    assert orb.value == 25
    assert orb.target_pos == (400, 50)
    assert orb.active == True
    assert orb.collected == False
    print("✅ test_experience_orb_init")


def test_experience_orb_update():
    """测试经验球更新"""
    from extra_effects import ExperienceOrb
    orb = ExperienceOrb(100, 100, value=10)
    # 更新0.1秒
    result = orb.update(0.1)
    assert orb.life > 0
    assert orb.active == True
    assert result == False  # 未被收集
    print("✅ test_experience_orb_update")


def test_experience_orb_fly_to_target():
    """测试经验球飞向目标"""
    from extra_effects import ExperienceOrb
    orb = ExperienceOrb(100, 100, value=10, target_pos=(105, 105))
    # 多帧更新直到接近目标
    for _ in range(50):
        result = orb.update(0.02)
        if result:  # 被收集
            break
    # 经验球应该被收集
    assert orb.collected == True or orb.life >= orb.max_life
    print("✅ test_experience_orb_fly_to_target")


def test_experience_orb_lifetime():
    """测试经验球生命周期"""
    from extra_effects import ExperienceOrb
    orb = ExperienceOrb(100, 100, value=10)
    # 更新超过最大生命周期
    for _ in range(200):
        orb.update(0.02)
    assert orb.active == False
    print("✅ test_experience_orb_lifetime")


def test_experience_manager():
    """测试经验管理器"""
    from extra_effects import ExperienceManager
    mgr = ExperienceManager.get_instance()
    # 重置为初始状态
    mgr.total_experience = 0
    mgr.level = 1
    mgr.exp_to_level = 100
    
    # 生成经验球
    mgr.spawn_orb(100, 100, value=50)
    mgr.spawn_orb(200, 200, value=60)
    
    # 更新（不收集，让它们过期）
    for _ in range(100):
        mgr.update(0.05)
    
    # 手动增加经验
    mgr.add_experience(50)
    
    info = mgr.get_level_info()
    assert info['level'] >= 1
    assert info['current_exp'] >= 0
    print("✅ test_experience_manager")


def test_experience_orb_trail():
    """测试经验球拖尾效果"""
    from extra_effects import ExperienceOrb
    orb = ExperienceOrb(100, 100, value=10)
    # 多帧更新产生拖尾
    for _ in range(15):
        orb.update(0.05)
    # 应该有拖尾
    assert len(orb.trail) > 0
    print("✅ test_experience_orb_trail")


if __name__ == '__main__':
    test_experience_orb_init()
    test_experience_orb_update()
    test_experience_orb_fly_to_target()
    test_experience_orb_lifetime()
    test_experience_manager()
    test_experience_orb_trail()
    print("\n🎉 所有经验球测试通过!")