"""
保卫萝卜 - 提示系统单元测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
try:
    import pygame
    pygame.init()
except:
    pygame = None


@pytest.mark.skipif(pygame is None, reason="pygame not available")
class TestTooltipSystem:
    """提示系统测试"""
    
    def test_tooltip_init(self):
        """测试提示系统初始化"""
        from tooltip_system import TooltipSystem
        tooltip = TooltipSystem()
        assert tooltip is not None
        assert tooltip._initialized is True
    
    def test_get_tower_tooltip(self):
        """测试获取塔提示信息"""
        from tooltip_system import TooltipSystem
        
        class MockTower:
            name = "箭塔"
            damage = 10
            range = 100
            cost = 50
            attack_speed = 1.0
            level = 2
            quality = "rare"
            slow_factor = 1.0
            skill_name = "专射击"
            specialization = "damage"
            specialized = True
            
            def get_sell_price(self):
                return 25
        
        class MockState:
            wave = 1
            money = 100
            lives = 20
        
        tooltip = TooltipSystem()
        tower = MockTower()
        state = MockState()
        
        result = tooltip._get_tower_tooltip(tower, state)
        
        assert result is not None
        title, desc, stats = result
        assert "箭塔" in title or "Arrow" in title
        # 伤害信息在stats列表中
        damage_in_stats = any("伤害" in s or "10" in s for s in stats)
        assert damage_in_stats
    
    def test_get_monster_tooltip(self):
        """测试获取怪物提示信息"""
        from tooltip_system import TooltipSystem
        
        class MockMonster:
            type = "basic"
            x = 100
            y = 100
            hp = 50
            max_hp = 100
            reward = 10
            boss = False
            frozen = 0
            slowed = False
        
        tooltip = TooltipSystem()
        monster = MockMonster()
        
        result = tooltip._get_monster_tooltip(monster)
        
        assert result is not None
        title, desc, stats = result
        assert "赏金" in desc or "10" in desc
    
    def test_boss_tooltip(self):
        """测试Boss提示信息"""
        from tooltip_system import TooltipSystem
        
        class MockMonster:
            type = "boss"
            x = 100
            y = 100
            hp = 1000
            max_hp = 5000
            reward = 500
            boss = True
            frozen = 30
            slowed = True
        
        tooltip = TooltipSystem()
        monster = MockMonster()
        
        result = tooltip._get_monster_tooltip(monster)
        
        assert result is not None
        title, desc, stats = result
        assert "Boss" in title
        assert "冰冻" in str(stats) or "frozen" in str(stats).lower()
    
    def test_get_tooltip_no_target(self):
        """测试无目标时返回None"""
        from tooltip_system import TooltipSystem
        
        class MockState:
            wave = 1
            money = 100
            lives = 20
        
        tooltip = TooltipSystem()
        
        # 空列表应该返回None
        result = tooltip.get_tooltip((100, 100), [], [], MockState())
        assert result is None
    
    def test_tooltip_global_instance(self):
        """测试全局单例"""
        from tooltip_system import get_tooltip_system
        
        instance1 = get_tooltip_system()
        instance2 = get_tooltip_system()
        
        assert instance1 is instance2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])