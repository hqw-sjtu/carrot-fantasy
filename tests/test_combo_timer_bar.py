"""
测试连击计时器条形组件
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None


class TestComboTimerBar:
    """测试连击计时器条"""
    
    def test_init(self):
        """测试初始化"""
        from combo_timer_bar import ComboTimerBar
        bar = ComboTimerBar(100, 100)
        assert bar.x == 100
        assert bar.y == 100
        assert bar.width == 200
        assert bar.height == 20
        assert not bar.active
        
    def test_trigger(self):
        """测试触发连击计时"""
        from combo_timer_bar import ComboTimerBar
        bar = ComboTimerBar(100, 100)
        bar.trigger(5, 3.0)
        
        assert bar.active
        assert bar.combo_count == 5
        assert bar.current_time == 3.0
        assert bar.max_time == 3.0
        
    def test_update_decrease(self):
        """测试时间递减"""
        from combo_timer_bar import ComboTimerBar
        bar = ComboTimerBar(100, 100)
        bar.trigger(3, 2.0)
        
        bar.update(0.5)
        assert bar.current_time == 1.5
        
    def test_update_expire(self):
        """测试计时器过期"""
        from combo_timer_bar import ComboTimerBar
        bar = ComboTimerBar(100, 100)
        bar.trigger(2, 1.0)
        
        bar.update(1.5)
        assert not bar.active
        assert bar.current_time == 0
        assert bar.combo_count == 0
        
    def test_get_fill_color(self):
        """测试填充颜色"""
        from combo_timer_bar import ComboTimerBar
        bar = ComboTimerBar(100, 100)
        
        # 高时间 - 绿色
        bar.trigger(5, 2.0)
        bar.current_time = 1.5  # 75%
        assert bar.get_fill_color() == bar.colors['fill_high']
        
        # 中时间 - 黄色
        bar.current_time = 0.8  # 40%
        assert bar.get_fill_color() == bar.colors['fill_mid']
        
        # 低时间 - 红色
        bar.current_time = 0.3  # 15%
        assert bar.get_fill_color() == bar.colors['fill_low']
        
    def test_manager_singleton(self):
        """测试管理器单例"""
        from combo_timer_bar import ComboTimerBarManager
        mgr1 = ComboTimerBarManager.get_instance()
        mgr2 = ComboTimerBarManager.get_instance()
        assert mgr1 is mgr2
        
    def test_manager_trigger(self):
        """测试管理器触发"""
        from combo_timer_bar import ComboTimerBarManager
        mgr = ComboTimerBarManager.get_instance()
        mgr.trigger(10, 5.0)
        
        bar = ComboTimerBarManager.get_instance()
        assert bar.active
        assert bar.combo_count == 10
        
    @pytest.mark.skipif(SCREEN is None, reason="Pygame not available")
    def test_draw(self):
        """测试绘制"""
        from combo_timer_bar import ComboTimerBar
        
        # 使用离屏surface测试绘制
        surface = pygame.Surface((300, 100))
        bar = ComboTimerBar(50, 50)
        bar.trigger(3, 2.0)
        bar.update(1.0)  # 剩余1秒
        
        # 不应抛出异常
        bar.draw(surface)
        
    def test_set_position(self):
        """测试设置位置"""
        from combo_timer_bar import ComboTimerBarManager
        ComboTimerBarManager.set_position(300, 200)
        
        bar = ComboTimerBarManager.get_instance()
        assert bar.x == 300
        assert bar.y == 200
        
    def test_set_size(self):
        """测试设置尺寸"""
        from combo_timer_bar import ComboTimerBarManager
        ComboTimerBarManager.set_size(300, 30)
        
        bar = ComboTimerBarManager.get_instance()
        assert bar.width == 300
        assert bar.height == 30


if __name__ == '__main__':
    pytest.main([__file__, '-v'])