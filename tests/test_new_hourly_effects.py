"""
保卫萝卜 - Boss技能系统测试
"""
import pytest
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
pygame.init()


class MockBoss:
    """模拟Boss对象"""
    def __init__(self):
        self.x = 400
        self.y = 300
        self.hp = 100
        self.max_hp = 100
        self.shield = 0


class MockGame:
    """模拟游戏对象"""
    def __init__(self):
        self.monsters = []
        self.towers = []
        self.dt = 0.016
        self.particle_system = MockParticleSystem()


class MockParticleSystem:
    """模拟粒子系统"""
    def add_teleport_effect(self, x, y):
        pass


class TestBossSkills:
    """Boss技能测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.boss = MockBoss()
        self.game = MockGame()
        
    def test_boss_skill_manager_creation(self):
        """测试技能管理器创建"""
        from boss_skills import BossSkillManager, get_boss_skill_manager
        
        manager = BossSkillManager(self.boss)
        assert len(manager.skills) == 5
        assert manager.current_skill is None
        
    def test_get_boss_skill_manager(self):
        """测试获取技能管理器单例"""
        from boss_skills import get_boss_skill_manager
        
        manager1 = get_boss_skill_manager(self.boss)
        manager2 = get_boss_skill_manager(self.boss)
        assert manager1 is manager2
        
    def test_summon_minions_skill(self):
        """测试召唤小怪技能"""
        from boss_skills import SummonMinionsSkill
        
        skill = SummonMinionsSkill(self.boss)
        assert skill.name == "召唤小怪"
        assert skill.cooldown == 15.0
        assert skill.current_cooldown == 0
        
        # 检查技能属性存在
        assert hasattr(skill, 'spawn_count')
        assert skill.spawn_count == 5
        
    def test_healing_skill(self):
        """测试回血技能"""
        from boss_skills import HealingSkill
        
        skill = HealingSkill(self.boss)
        self.boss.hp = 50
        
        skill.activate(self.game)
        
        assert self.boss.hp == 100  # 回满
        
    def test_shield_skill(self):
        """测试护盾技能"""
        from boss_skills import ShieldSkill
        
        skill = ShieldSkill(self.boss)
        skill.activate(self.game)
        
        assert self.boss.shield > 0
        assert skill.active is True
        
    def test_teleport_skill(self):
        """测试传送技能"""
        from boss_skills import TeleportSkill
        
        skill = TeleportSkill(self.boss)
        original_x, original_y = self.boss.x, self.boss.y
        
        skill.activate(self.game)
        
        # 位置应该改变
        assert (self.boss.x, self.boss.y) != (original_x, original_y)
        
    def test_skill_cooldown(self):
        """测试技能冷却"""
        from boss_skills import BossSkill
        
        # 创建自定义技能测试冷却逻辑
        class TestSkill(BossSkill):
            def __init__(self, boss):
                super().__init__(boss, cooldown=10.0)
                
        skill = TestSkill(self.boss)
        
        # 冷却中无法激活
        skill.current_cooldown = 5.0
        result = skill.activate(self.game)
        assert result is False
        
        # 冷却完成可激活
        skill.current_cooldown = 0
        result = skill.activate(self.game)
        assert result is True
        assert skill.active is True
        assert skill.current_cooldown == 10.0
        
    def test_skill_manager_update(self):
        """测试技能管理器更新"""
        from boss_skills import BossSkillManager
        
        manager = BossSkillManager(self.boss)
        
        # Boss血量低于50%时应该尝试使用技能
        self.boss.hp = 30
        self.boss.max_hp = 100
        
        # 更新几次
        for _ in range(10):
            manager.update(0.016, self.game)
            
    def test_get_skill_info(self):
        """测试获取技能信息"""
        from boss_skills import BossSkillManager
        
        manager = BossSkillManager(self.boss)
        info = manager.get_skill_info()
        
        assert len(info) == 5
        assert all("召唤小怪" in s or "地震攻击" in s or "自我修复" in s or 
                   "能量护盾" in s or "瞬间移动" in s for s in info)


class TestScreenShake:
    """屏幕震动系统测试"""
    
    def setup_method(self):
        """测试前设置"""
        pass
        
    def test_screen_shake_manager_creation(self):
        """测试屏幕震动管理器创建"""
        from camera_system import ScreenShakeManager, get_screen_shake_manager
        
        manager = ScreenShakeManager()
        assert manager.intensity == 0
        assert manager.duration == 0
        
    def test_add_shake(self):
        """测试添加震动"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_shake(10, 1.0)
        
        assert manager.intensity == 10
        assert manager.duration == 1.0
        
    def test_critical_shake(self):
        """测试暴击震动"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_critical_shake()
        
        assert manager.intensity == 3
        assert manager.duration == 0.15
        
    def test_boss_shake(self):
        """测试Boss震动"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_boss_shake()
        
        assert manager.intensity == 10
        
    def test_explosion_shake(self):
        """测试爆炸震动"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_explosion_shake(400, 300, (400, 300))
        
        assert manager.intensity > 0
        
    def test_screen_shake_update(self):
        """测试震动更新"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_shake(10, 1.0)
        
        # 更新几次
        for _ in range(10):
            manager.update(0.1)
            
        assert manager.duration < 1.0
        
    def test_screen_shake_intensity_factor(self):
        """测试强度因子"""
        from camera_system import ScreenShakeManager
        
        manager = ScreenShakeManager()
        manager.add_shake(20, 1.0)
        
        factor = manager.get_intensity_factor()
        assert factor == 1.0
        
    def test_get_screen_shake_singleton(self):
        """测试单例"""
        from camera_system import get_screen_shake_manager
        
        manager1 = get_screen_shake_manager()
        manager2 = get_screen_shake_manager()
        
        assert manager1 is manager2


class TestCamera:
    """相机系统测试"""
    
    def test_camera_creation(self):
        """测试相机创建"""
        from camera_system import Camera, get_camera
        
        camera = Camera(800, 600)
        assert camera.width == 800
        assert camera.height == 600
        assert camera.zoom == 1.0
        
    def test_camera_zoom(self):
        """测试相机缩放"""
        from camera_system import Camera
        
        camera = Camera()
        camera.set_zoom(1.5)
        
        assert camera.target_zoom == 1.5
        
    def test_camera_zoom_limits(self):
        """测试缩放限制"""
        from camera_system import Camera
        
        camera = Camera()
        camera.set_zoom(0.1)  # 小于最小值
        assert camera.target_zoom == 0.5
        
        camera.set_zoom(3.0)  # 大于最大值
        assert camera.target_zoom == 2.0
        
    def test_world_to_screen(self):
        """测试世界坐标转屏幕坐标"""
        from camera_system import Camera
        
        camera = Camera(800, 600)
        camera.set_position(400, 300)  # 设置相机中心
        sx, sy = camera.world_to_screen(400, 300)
        
        # 中心点应该映射到屏幕中心
        assert 350 < sx < 450
        assert 250 < sy < 350
        
    def test_screen_to_world(self):
        """测试屏幕坐标转世界坐标"""
        from camera_system import Camera
        
        camera = Camera(800, 600)
        camera.set_position(400, 300)  # 设置相机中心
        wx, wy = camera.screen_to_world(400, 300)
        
        # 屏幕中心应该映射到相机位置
        assert 350 < wx < 450
        assert 250 < wy < 350
        
    def test_get_camera_singleton(self):
        """测试相机单例"""
        from camera_system import get_camera
        
        camera1 = get_camera()
        camera2 = get_camera()
        
        assert camera1 is camera2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])