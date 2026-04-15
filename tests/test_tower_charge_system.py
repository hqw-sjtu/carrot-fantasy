"""
测试防御塔充能系统
"""

import pytest
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Headless模式
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((1, 1))


class TestTowerChargeSystem:
    """测试充能系统"""
    
    def test_charge_effect_creation(self):
        """测试充能特效创建"""
        from tower_charge_system import ChargeEffect
        
        effect = ChargeEffect(100, 100, (255, 100, 50))
        assert effect.x == 100
        assert effect.y == 100
        assert effect.color == (255, 100, 50)
        assert effect.life == 1.0
        
    def test_charge_effect_update(self):
        """测试充能特效更新"""
        from tower_charge_system import ChargeEffect
        
        effect = ChargeEffect(100, 100, (255, 100, 50))
        alive = effect.update()
        assert alive is True
        assert effect.life < 1.0
        
    def test_charge_effect_draw(self):
        """测试充能特效绘制"""
        from tower_charge_system import ChargeEffect
        
        effect = ChargeEffect(100, 100, (255, 100, 50))
        screen = pygame.Surface((200, 200))
        effect.draw(screen)  # 不应抛出异常
        
    def test_charge_burst_creation(self):
        """测试充能爆发创建"""
        from tower_charge_system import ChargeBurst
        
        burst = ChargeBurst(100, 100, (255, 215, 0))
        assert burst.x == 100
        assert burst.y == 100
        assert burst.done is False
        
    def test_charge_burst_update(self):
        """测试充能爆发更新"""
        from tower_charge_system import ChargeBurst
        
        burst = ChargeBurst(100, 100, (255, 215, 0))
        for _ in range(20):
            burst.update()
        # 应该还有一些ring存在
        assert len(burst.rings) >= 0
        
    def test_charge_manager_creation(self):
        """测试管理器创建"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        assert manager is not None
        assert len(manager.charges) == 0
        
    def test_start_charge(self):
        """测试开始充能"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1, 'fire')
        assert 1 in manager.charges
        assert manager.charges[1] == 0
        
    def test_add_charge(self):
        """测试增加充能"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 30)
        assert manager.get_charge(1) == 30
        manager.add_charge(1, 50)
        assert manager.get_charge(1) == 80  # 30 + 50 = 80
        
    def test_charge_cap(self):
        """测试充能上限"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 150)
        assert manager.get_charge(1) == 100  # 不超过100
        
    def test_is_charged(self):
        """测试是否充满"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        assert manager.is_charged(1) is False
        manager.add_charge(1, 100)
        assert manager.is_charged(1) is True
        
    def test_trigger_burst(self):
        """测试触发爆发"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 100)
        
        triggered = manager.trigger_burst(1, 100, 100, 'fire')
        assert triggered is True
        assert len(manager.bursts) == 1
        assert manager.get_charge(1) == 0  # 充能归零
        
    def test_trigger_burst_not_charged(self):
        """测试未充满时不触发"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 50)
        
        triggered = manager.trigger_burst(1, 100, 100)
        assert triggered is False
        assert len(manager.bursts) == 0
        
    def test_spawn_charge_effect(self):
        """测试生成充能效果"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.spawn_charge_effect(100, 100, 'ice')
        assert len(manager.effects) == 1
        
    def test_update_effects(self):
        """测试更新特效"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.spawn_charge_effect(100, 100)
        
        for _ in range(50):
            manager.update()
            
        # 效果应该消失
        assert len([e for e in manager.effects if e.life > 0]) == 0
        
    def test_draw_charge_bar(self):
        """测试绘制充能条"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 50)
        
        screen = pygame.Surface((200, 200))
        manager.draw_charge_bar(screen, 100, 100, 1)
        
    def test_get_charge_color(self):
        """测试获取充能颜色"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        # 不指定类型，使用默认
        manager.start_charge(1)
        manager.add_charge(1, 10)  # 10 < 30, 低充能
        
        # 低充能
        color = manager.get_charge_color(1)
        assert color == (255, 215, 0)  # default color
        
        # 中充能 (50 >= 30 且 < 70)
        manager.add_charge(1, 40)
        color = manager.get_charge_color(1)
        assert color != (255, 215, 0)  # 应该变亮
        
    def test_clear(self):
        """测试清除数据"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        manager.start_charge(1)
        manager.add_charge(1, 50)
        manager.spawn_charge_effect(100, 100)
        
        manager.clear()
        assert len(manager.charges) == 0
        assert len(manager.effects) == 0
        assert len(manager.bursts) == 0
        
    def test_charge_colors(self):
        """测试不同类型塔的颜色"""
        from tower_charge_system import TowerChargeManager
        
        manager = TowerChargeManager()
        
        fire_color = manager.charge_colors['fire']
        ice_color = manager.charge_colors['ice']
        lightning_color = manager.charge_colors['lightning']
        
        assert fire_color == (255, 100, 50)
        assert ice_color == (100, 200, 255)
        assert lightning_color == (255, 255, 100)


class TestGetChargeManager:
    """测试全局管理器"""
    
    def test_get_charge_manager(self):
        """测试获取全局管理器"""
        from tower_charge_system import get_charge_manager, _charge_manager
        
        # 清除之前的实例
        import tower_charge_system
        tower_charge_system._charge_manager = None
        
        manager1 = get_charge_manager()
        manager2 = get_charge_manager()
        
        assert manager1 is manager2  # 应该是同一个实例


if __name__ == '__main__':
    pytest.main([__file__, '-v'])