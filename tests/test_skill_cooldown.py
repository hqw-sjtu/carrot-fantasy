# -*- coding: utf-8 -*-
"""技能冷却显示测试"""
import pytest
import sys
sys.path.insert(0, 'src')

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # headless
except:
    pytest.skip("pygame not available", allow_module_level=True)

from skill_cooldown_display import SkillCooldownDisplay


class MockSkill:
    """模拟技能"""
    def __init__(self, cooldown=30.0, current=0):
        self.cooldown = cooldown
        self.current_cooldown = current
    
    def is_ready(self):
        return self.current_cooldown <= 0


class TestSkillCooldownDisplay:
    """技能冷却显示测试"""
    
    def test_init(self):
        """测试初始化"""
        display = SkillCooldownDisplay(100, 100, size=60)
        assert display.x == 100
        assert display.y == 100
        assert display.size == 60
        assert display.skill is None
        assert display.glow_rings == []
    
    def test_set_skill(self):
        """测试绑定技能"""
        display = SkillCooldownDisplay(100, 100)
        skill = MockSkill(cooldown=30.0)
        display.set_skill(skill)
        assert display.skill is skill
    
    def test_update_ready(self):
        """测试就绪状态更新"""
        display = SkillCooldownDisplay(100, 100)
        skill = MockSkill(cooldown=30.0, current=0)
        display.set_skill(skill)
        
        display.update(0.1)
        assert display.ready_pulse > 0
    
    def test_update_cooldown(self):
        """测试冷却中状态更新"""
        display = SkillCooldownDisplay(100, 100)
        skill = MockSkill(cooldown=30.0, current=15.0)
        display.set_skill(skill)
        
        display.update(0.1)
        assert display.ready_pulse == 0
    
    def test_add_glow_ring(self):
        """测试添加光晕环"""
        display = SkillCooldownDisplay(100, 100)
        display.add_glow_ring(color=(100, 200, 255), radius_offset=5)
        assert len(display.glow_rings) == 1
        assert display.glow_rings[0]['color'] == (100, 200, 255)
    
    def test_glow_ring_animation(self):
        """测试光晕环动画"""
        display = SkillCooldownDisplay(100, 100)
        display.add_glow_ring()
        
        initial_alpha = display.glow_rings[0]['alpha']
        initial_radius = display.glow_rings[0]['radius_offset']
        
        display.update(0.1)
        
        assert display.glow_rings[0]['alpha'] < initial_alpha
        assert display.glow_rings[0]['radius_offset'] > initial_radius
    
    def test_glow_ring_cleanup(self):
        """测试光晕环自动清理"""
        display = SkillCooldownDisplay(100, 100)
        display.add_glow_ring()
        
        # 持续更新直到光晕消失
        for _ in range(100):
            display.update(0.1)
            if not display.glow_rings:
                break
        
        assert len(display.glow_rings) == 0