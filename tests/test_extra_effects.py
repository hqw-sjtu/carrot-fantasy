"""
额外特效系统测试
"""
import sys
sys.path.insert(0, 'src')

import pygame
pygame.init()

from extra_effects import TowerAttackTrailEffect, GoldRainEffect, UpgradeBeamEffect, TowerSelectionPulse


class TestTowerAttackTrailEffect:
    """攻击拖尾特效测试"""
    
    def test_trail_init(self):
        trail = TowerAttackTrailEffect((100, 100), (200, 200))
        assert trail.start_pos == (100, 100)
        assert trail.end_pos == (200, 200)
        assert trail.active == True
        assert trail.max_life == 0.3
        
    def test_trail_update(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.1)
        assert trail.life == 0.1
        assert trail.active == True
        
    def test_trail_fade(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.2)
        # 进度应为 ~0.67
        progress = trail.life / trail.max_life
        assert 0.6 < progress < 0.8
        
    def test_trail_finish(self):
        trail = TowerAttackTrailEffect((0, 0), (100, 100))
        trail.update(0.5)
        assert trail.active == False


class TestGoldRainEffect:
    """金币雨特效测试"""
    
    def test_gold_rain_init(self):
        rain = GoldRainEffect(800, 600, count=20)
        assert len(rain.coins) == 20
        assert rain.max_life == 3.0
        assert rain.active == True
        
    def test_gold_rain_update(self):
        rain = GoldRainEffect(800, 600, count=10)
        rain.update(0.5)
        assert rain.life == 0.5
        
    def test_gold_rain_fall(self):
        rain = GoldRainEffect(800, 600, count=5)
        initial_y = [c['y'] for c in rain.coins]
        rain.update(1.0)
        final_y = [c['y'] for c in rain.coins]
        # 所有金币都应该往下掉
        assert all(final_y[i] > initial_y[i] for i in range(5))
        
    def test_gold_rain_finish(self):
        rain = GoldRainEffect(800, 600, count=5)
        rain.update(5.0)
        assert rain.active == False

class TestUpgradeBeamEffect:
    """升级光柱特效测试"""
    
    def test_upgrade_beam_init(self):
        beam = UpgradeBeamEffect(400, 300, level=2)
        assert beam.x == 400
        assert beam.y == 300
        assert beam.level == 2
        assert beam.active == True
        assert len(beam.particles) == 20
        
    def test_upgrade_beam_update(self):
        beam = UpgradeBeamEffect(400, 300, level=2)
        beam.update(0.3)
        assert beam.life == 0.3
        
    def test_upgrade_beam_color_by_level(self):
        beam_lv2 = UpgradeBeamEffect(400, 300, level=2)
        beam_lv3 = UpgradeBeamEffect(400, 300, level=3)
        beam_lv4 = UpgradeBeamEffect(400, 300, level=4)
        # 不同等级应有不同颜色 (lv2金色, lv3紫色, lv4橙红)
        assert beam_lv2.color != beam_lv3.color
        assert beam_lv3.color != beam_lv4.color
        assert beam_lv2.color == (255, 215, 0)  # 金色
        assert beam_lv3.color == (138, 43, 226)  # 紫色
        
    def test_upgrade_beam_finish(self):
        beam = UpgradeBeamEffect(400, 300, level=2)
        beam.update(1.0)
        assert beam.active == False


class TestTowerSelectionPulse:
    """塔选中脉冲特效测试"""
    
    def test_pulse_init(self):
        pulse = TowerSelectionPulse(400, 300, radius=50)
        assert pulse.x == 400
        assert pulse.y == 300
        assert pulse.base_radius == 50
        assert pulse.active == True
        
    def test_pulse_loop(self):
        pulse = TowerSelectionPulse(400, 300)
        pulse.update(1.0)
        assert pulse.life == 1.0
        pulse.update(1.0)  # 超过max_life
        assert pulse.life < 1.5  # 应该循环重置
        
    def test_pulse_draw_no_crash(self):
        # 测试绘制不会崩溃（创建模拟screen）
        import pygame
        pygame.init()
        screen = pygame.Surface((800, 600))
        pulse = TowerSelectionPulse(400, 300)
        pulse.update(0.1)
        try:
            pulse.draw(screen)
        except Exception as e:
            assert False, f"Draw crashed: {e}"
