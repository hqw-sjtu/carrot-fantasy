"""
保卫萝卜 - 新增特效测试
测试 StarburstEffect 和 TrailFadeEffect
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestStarburstEffect:
    """星爆发散特效测试"""
    
    def test_starburst_init(self):
        """测试星爆发散初始化"""
        from extra_effects import StarburstEffect
        effect = StarburstEffect(100, 200, color=(255, 215, 0), rays=12)
        assert effect.x == 100
        assert effect.y == 200
        assert effect.color == (255, 215, 0)
        assert effect.rays == 12
        assert effect.max_life == 1.0
        assert effect.active is True
        assert len(effect.particles) == 12
    
    def test_starburst_update(self):
        """测试星爆发散更新"""
        from extra_effects import StarburstEffect
        effect = StarburstEffect(100, 200, rays=8)
        initial_x = effect.particles[0]['x']
        effect.update(0.016)  # 1帧
        assert effect.life > 0
        # 粒子应该移动
        assert effect.particles[0]['x'] != initial_x
    
    def test_starburst_finish(self):
        """测试星爆发散结束"""
        from extra_effects import StarburstEffect
        effect = StarburstEffect(100, 200)
        effect.update(1.5)  # 超过最大生命周期
        assert effect.active is False
    
    def test_starburst_particles_decay(self):
        """测试粒子透明度衰减"""
        from extra_effects import StarburstEffect
        effect = StarburstEffect(100, 200, rays=6)
        effect.update(0.5)  # 半生命周期
        # alpha应该减少
        assert effect.particles[0]['alpha'] < 255


class TestTrailFadeEffect:
    """渐变拖尾特效测试"""
    
    def test_trail_fade_init(self):
        """测试渐变拖尾初始化"""
        from extra_effects import TrailFadeEffect
        points = [(100, 100), (110, 110), (120, 120)]
        effect = TrailFadeEffect(points, color=(100, 200, 255), width=8)
        assert effect.points == points
        assert effect.color == (100, 200, 255)
        assert effect.width == 8
        assert effect.max_life == 0.5
        assert effect.active is True
    
    def test_trail_fade_empty_points(self):
        """测试空点列表"""
        from extra_effects import TrailFadeEffect
        effect = TrailFadeEffect([])
        assert effect.active is False
    
    def test_trail_fade_update(self):
        """测试渐变拖尾更新"""
        from extra_effects import TrailFadeEffect
        points = [(100, 100), (110, 110), (120, 120)]
        effect = TrailFadeEffect(points)
        initial_len = len(effect.points)
        effect.update(0.1)
        # 点应该被移除
        assert len(effect.points) <= initial_len
    
    def test_trail_fade_finish(self):
        """测试渐变拖尾结束"""
        from extra_effects import TrailFadeEffect
        points = [(100, 100), (110, 110)]
        effect = TrailFadeEffect(points)
        effect.update(0.6)  # 超过最大生命周期
        assert effect.active is False


class TestEffectManager:
    """特效管理器测试"""
    
    def test_spawn_starburst(self):
        """测试生成星爆发散"""
        from extra_effects import EffectManager
        manager = EffectManager.get_instance()
        initial_count = len(manager.starbursts)
        manager.spawn_starburst(100, 200)
        assert len(manager.starbursts) == initial_count + 1
    
    def test_spawn_trail_fade(self):
        """测试生成渐变拖尾"""
        from extra_effects import EffectManager
        manager = EffectManager.get_instance()
        initial_count = len(manager.trail_fades)
        manager.spawn_trail_fade([(100, 100), (200, 200)])
        assert len(manager.trail_fades) == initial_count + 1