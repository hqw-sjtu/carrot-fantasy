"""
保卫萝卜 - 激光瞄准与终极技能测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pygame = None

pytestmark = pytest.mark.skipif(pygame is None, reason="pygame not available")


class TestLaserTargetSystem:
    """激光瞄准系统测试"""
    
    def test_laser_system_init(self):
        from laser_target_system import LaserTargetSystem
        system = LaserTargetSystem()
        assert system.lasers == []
        assert system.max_life == 0.15
        
    def test_add_laser(self):
        from laser_target_system import LaserTargetSystem
        system = LaserTargetSystem()
        system.add_laser((100, 100), (200, 200), "箭塔", 10)
        assert len(system.lasers) == 1
        assert system.lasers[0]['damage'] == 10
        
    def test_laser_update(self):
        from laser_target_system import LaserTargetSystem
        system = LaserTargetSystem()
        system.add_laser((100, 100), (200, 200))
        system.update(0.2)  # 超过max_life
        assert len(system.lasers) == 0
        
    def test_tower_colors(self):
        from laser_target_system import LaserTargetSystem
        system = LaserTargetSystem()
        system.add_laser((100, 100), (200, 200), "炮塔")
        assert system.lasers[0]['color'] == (255, 100, 50)


class TestTargetLockEffect:
    """目标锁定特效测试"""
    
    def test_target_lock_init(self):
        from laser_target_system import TargetLockEffect
        class FakeTarget:
            x = 100
            y = 200
            alive = True
        target = FakeTarget()
        effect = TargetLockEffect(target)
        assert effect.active == True
        assert effect.max_life == 0.3
        
    def test_target_lock_update(self):
        from laser_target_system import TargetLockEffect
        class FakeTarget:
            x = 100
            y = 200
            alive = True
        target = FakeTarget()
        effect = TargetLockEffect(target)
        effect.update(0.5)
        assert effect.active == False


class TestUltimateSkills:
    """终极技能测试"""
    
    def test_meteor_strike_init(self):
        from ultimate_skills import MeteorStrike
        skill = MeteorStrike()
        assert skill.name == "陨石打击"
        assert skill.cooldown == 30
        assert skill.is_ready()
        
    def test_meteor_activate(self):
        from ultimate_skills import MeteorStrike
        skill = MeteorStrike()
        result = skill.activate()
        assert result == True
        assert skill.active == True
        assert len(skill.meteors) == 20
        
    def test_lightning_storm_init(self):
        from ultimate_skills import LightningStorm
        skill = LightningStorm()
        assert skill.name == "闪电风暴"
        assert skill.cooldown == 25
        
    def test_ice_age_init(self):
        from ultimate_skills import IceAge
        skill = IceAge()
        assert skill.name == "冰河时代"
        assert skill.cooldown == 40
        # activate后才生成粒子
        skill.activate()
        assert len(skill.freeze_particles) == 100
        
    def test_divine_shield_init(self):
        from ultimate_skills import DivineShield
        skill = DivineShield()
        assert skill.name == "神圣护盾"
        
    def test_tower_summon_init(self):
        from ultimate_skills import TowerSummon
        skill = TowerSummon()
        assert skill.name == "塔召唤"
        
    def test_skill_manager(self):
        from ultimate_skills import UltimateSkillManager
        manager = UltimateSkillManager()
        assert 'meteor' in manager.skills
        assert 'lightning' in manager.skills
        assert 'ice_age' in manager.skills
        assert 'shield' in manager.skills
        assert 'summon' in manager.skills
        
    def test_skill_cooldown(self):
        from ultimate_skills import UltimateSkillManager
        manager = UltimateSkillManager()
        # 激活技能
        result = manager.activate_skill('meteor')
        assert result == True
        # 冷却中
        result = manager.activate_skill('meteor')
        assert result == False
        assert manager.get_cooldown('meteor') > 0
        
    def test_skill_update(self):
        from ultimate_skills import UltimateSkillManager
        manager = UltimateSkillManager()
        manager.activate_skill('meteor')
        manager.update(0.1)
        assert manager.skills['meteor'].active == True
        
    def test_skill_duration_expire(self):
        from ultimate_skills import MeteorStrike
        skill = MeteorStrike()
        skill.activate()
        skill.update(10)  # 超过duration
        assert skill.active == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])