"""
保卫萝卜 - 技能冷却显示系统测试
"""
import pytest
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from skill_cooldown_display import SkillCooldownDisplay, SkillBar
from ultimate_skills import UltimateSkill, MeteorStrike


class TestSkillCooldownDisplay:
    """技能冷却显示组件测试"""
    
    @pytest.fixture
    def mock_pygame(self):
        """模拟pygame"""
        if not PYGAME_AVAILABLE:
            pytest.skip("pygame not available")
        pygame.init()
        yield pygame
        pygame.quit()
        
    def test_skill_cooldown_display_init(self):
        """测试冷却显示初始化"""
        display = SkillCooldownDisplay(100, 100, size=60)
        assert display.x == 100
        assert display.y == 100
        assert display.size == 60
        assert display.skill is None
        
    def test_set_skill(self):
        """测试技能绑定"""
        display = SkillCooldownDisplay(100, 100)
        skill = UltimateSkill("测试技能", 10, 50, 2.0)
        display.set_skill(skill)
        assert display.skill == skill
        
    def test_update_ready_pulse(self):
        """测试就绪脉冲更新"""
        display = SkillCooldownDisplay(100, 100)
        skill = UltimateSkill("测试", 10, 50, 2.0)
        display.set_skill(skill)
        
        # 技能就绪时应该有脉冲
        skill.current_cooldown = 0
        display.update(0.1)
        assert display.ready_pulse > 0
        
    def test_update_cooldown(self):
        """测试冷却中状态"""
        display = SkillCooldownDisplay(100, 100)
        skill = UltimateSkill("测试", 10, 50, 2.0)
        display.set_skill(skill)
        skill.current_cooldown = 5
        
        display.update(0.1)
        # 冷却中不应该有脉冲
        assert display.ready_pulse == 0


class TestSkillBar:
    """技能栏测试"""
    
    def test_skill_bar_init(self):
        """测试技能栏初始化"""
        bar = SkillBar(50, 50, skill_size=50, spacing=10)
        assert bar.x == 50
        assert bar.y == 50
        assert bar.skill_size == 50
        assert bar.spacing == 10
        assert len(bar.slots) == 0
        
    def test_add_skill(self):
        """测试添加技能"""
        bar = SkillBar(50, 50, skill_size=50)
        skill = MeteorStrike()
        bar.add_skill(skill)
        assert len(bar.slots) == 1
        assert bar.slots[0].skill == skill
        
    def test_add_multiple_skills(self):
        """测试添加多个技能"""
        bar = SkillBar(50, 50, skill_size=50, spacing=10)
        skill1 = MeteorStrike()
        skill2 = UltimateSkill("测试2", 20, 80, 3.0)
        
        bar.add_skill(skill1)
        bar.add_skill(skill2)
        
        assert len(bar.slots) == 2
        # 检查位置
        assert bar.slots[1].x > bar.slots[0].x
        
    def test_get_skill_by_index(self):
        """测试通过索引获取技能"""
        bar = SkillBar(50, 50)
        skill1 = MeteorStrike()
        skill2 = UltimateSkill("测试2", 20, 80, 3.0)
        
        bar.add_skill(skill1)
        bar.add_skill(skill2)
        
        assert bar.get_skill_by_index(0) == skill1
        assert bar.get_skill_by_index(1) == skill2
        assert bar.get_skill_by_index(5) is None
        assert bar.get_skill_by_index(-1) is None
        
    def test_update(self):
        """测试更新"""
        bar = SkillBar(50, 50)
        skill = MeteorStrike()
        bar.add_skill(skill)
        
        # 应该不报错
        bar.update(0.1)


class TestUltimateSkill:
    """终极技能基本功能测试"""
    
    def test_skill_init(self):
        """测试技能初始化"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        assert skill.name == "测试"
        assert skill.cooldown == 10
        assert skill.damage == 50
        assert skill.duration == 2.0
        assert skill.current_cooldown == 0
        assert not skill.active
        
    def test_skill_is_ready(self):
        """测试技能就绪状态"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        assert skill.is_ready()
        
        skill.current_cooldown = 5
        assert not skill.is_ready()
        
    def test_activate_ready_skill(self):
        """测试激活就绪技能"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        result = skill.activate()
        assert result is True
        assert skill.active
        assert skill.current_cooldown == 10
        
    def test_activate_cooldown_skill(self):
        """测试激活冷却中技能"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        skill.current_cooldown = 5
        result = skill.activate()
        assert result is False
        assert not skill.active
        
    def test_update_cooldown(self):
        """测试冷却更新"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        skill.current_cooldown = 5
        skill.update(1.0)
        assert skill.current_cooldown == 4.0
        
    def test_update_active_duration(self):
        """测试激活持续时间"""
        skill = UltimateSkill("测试", 10, 50, 2.0)
        skill.activate()
        assert skill.active
        
        skill.update(1.5)
        assert skill.life == 1.5
        
        skill.update(1.0)
        # 超过持续时间，应该结束
        assert not skill.active


if __name__ == "__main__":
    pytest.main([__file__, "-v"])