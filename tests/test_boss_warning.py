"""
Boss警告特效测试
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((1000, 700))
except:
    SCREEN = None

from base_effects import BossWarningEffect


class TestBossWarningEffect:
    """Boss警告特效测试"""
    
    def test_boss_warning_init(self):
        """测试Boss警告特效初始化"""
        effect = BossWarningEffect(500, 350, 1000, 700)
        assert effect.x == 500
        assert effect.y == 350
        assert effect.screen_width == 1000
        assert effect.screen_height == 700
        assert effect.max_life == 90
        assert effect.active == True
        assert effect.pulse_count == 3
        
    def test_boss_warning_update(self):
        """测试Boss警告特效更新"""
        effect = BossWarningEffect(500, 350)
        initial_life = effect.life
        
        effect.update(10)
        assert effect.life == initial_life + 10
        assert effect.active == True
        
        # 测试生命周期结束
        effect.life = 95
        effect.update(10)
        assert effect.active == False
        
    def test_boss_warning_shake(self):
        """测试Boss警告特效屏幕震动"""
        effect = BossWarningEffect(500, 350)
        
        # 早期应该有震动
        effect.life = 30
        effect.update(1)
        assert hasattr(effect, 'shake_x')
        
    def test_boss_warning_draw(self):
        """测试Boss警告特效绘制"""
        if SCREEN is None:
            pytest.skip("Pygame not available")
            
        effect = BossWarningEffect(500, 350, 1000, 700)
        effect.update(10)
        
        # 绘制不应抛出异常
        effect.draw(SCREEN)
        
    def test_boss_warning_multiple_pulses(self):
        """测试多次脉冲效果"""
        effect = BossWarningEffect(500, 350)
        
        # 模拟多个脉冲周期
        for i in range(5):
            effect.update(15)
            
        assert effect.life > 0
        assert effect.active == True