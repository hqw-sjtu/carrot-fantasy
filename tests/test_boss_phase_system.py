"""
保卫萝卜 - Boss战斗阶段系统测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from boss_phase_system import BossPhaseSystem, get_boss_phase_system


class MockBoss:
    """模拟Boss怪物"""
    def __init__(self):
        self.name = "测试Boss"
        self.x = 400
        self.y = 300
        self.alive = True


class TestBossPhaseSystem:
    """Boss阶段系统测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        system = BossPhaseSystem()
        assert system.phase == "normal"
        assert system.active == False
        assert system.boss is None
        
    def test_warning_phase(self):
        """测试警告阶段"""
        system = BossPhaseSystem()
        system.start_warning()
        
        assert system.phase == "warning"
        assert system.warning_timer == 0
        
    def test_boss_battle_activation(self):
        """测试Boss战斗激活"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        
        system.activate_boss_battle(mock_boss)
        
        assert system.phase == "boss_battle"
        assert system.boss == mock_boss
        assert system.flash_intensity == 1.0
        assert system.vignette_alpha == 150
        assert system.screen_shake == 5
        
    def test_victory(self):
        """测试胜利阶段"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        
        system.victory()
        
        assert system.phase == "victory"
        assert system.boss is None
        assert len(system.particles) > 0
        
    def test_reset(self):
        """测试重置"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        system.particles.append({"x": 100, "y": 100, "life": 1.0})
        
        system.reset()
        
        assert system.phase == "normal"
        assert system.boss is None
        assert system.particles == []
        
    def test_screen_offset(self):
        """测试屏幕震动偏移"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        
        offset = system.get_screen_offset()
        
        assert isinstance(offset, tuple)
        assert len(offset) == 2
        assert system.screen_shake > 0
        
    def test_particle_spawn(self):
        """测试粒子生成"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        
        assert len(system.particles) > 0
        for p in system.particles:
            assert "x" in p
            assert "y" in p
            assert "vx" in p
            assert "vy" in p
            assert "life" in p
            assert "color" in p
            assert "size" in p
            
    def test_particle_update(self):
        """测试粒子更新"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        
        initial_count = len(system.particles)
        system.update(0.1)
        
        # 粒子应该减少
        assert len(system.particles) <= initial_count
        
    def test_global_singleton(self):
        """测试全局单例"""
        system1 = get_boss_phase_system()
        system2 = get_boss_phase_system()
        
        assert system1 is system2
        
    def test_warning_to_boss_transition(self):
        """测试警告到Boss战斗的过渡"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        
        # 开始警告
        system.start_warning()
        system.update(3.5)  # 超过3秒警告时间
        
        # 手动激活Boss战斗
        system.activate_boss_battle(mock_boss)
        
        assert system.phase == "boss_battle"
        
    def test_victory_to_normal_transition(self):
        """测试胜利到正常的过渡"""
        system = BossPhaseSystem()
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        system.victory()
        system.update(3.5)
        
        assert system.phase == "normal"


class TestBossPhaseDraw:
    """Boss阶段绘制测试"""
    
    def test_draw_no_crash(self):
        """测试绘制不崩溃"""
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        system = BossPhaseSystem()
        
        # 测试各种阶段的绘制
        system.start_warning()
        system.draw(screen)
        
        mock_boss = MockBoss()
        system.activate_boss_battle(mock_boss)
        system.draw(screen)
        
        system.victory()
        system.draw(screen)
        
        pygame.quit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])