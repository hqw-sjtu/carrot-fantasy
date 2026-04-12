"""
保卫萝卜 - 庆祝特效系统测试
Carrot Fantasy - Celebration Effects Tests
"""
import pytest
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None


class TestConfettiParticle:
    """彩色纸屑粒子测试"""
    
    def test_confetti_creation(self):
        from celebration_effects import ConfettiParticle
        particle = ConfettiParticle(400, 300)
        assert particle.x == 400
        assert particle.y == 300
        assert particle.lifetime == 3.0
        assert particle.max_lifetime == 3.0
    
    def test_confetti_colors(self):
        from celebration_effects import ConfettiParticle
        assert len(ConfettiParticle.CONFETTI_COLORS) == 8
    
    def test_confetti_update(self):
        from celebration_effects import ConfettiParticle
        particle = ConfettiParticle(400, 300)
        result = particle.update(0.016)  # 1帧
        assert result is True
        assert particle.lifetime < 3.0
    
    def test_confetti_physics(self):
        from celebration_effects import ConfettiParticle
        particle = ConfettiParticle(400, 300)
        # 初始向上运动，然后受重力影响
        initial_vy = particle.vy
        assert initial_vy < 0  # 初始向上速度


class TestFireworkParticle:
    """烟花粒子测试"""
    
    def test_firework_creation(self):
        from celebration_effects import FireworkParticle
        particle = FireworkParticle(400, 200, (255, 70, 70))
        assert particle.x == 400
        assert particle.y == 200
        assert particle.color == (255, 70, 70)
    
    def test_firework_update(self):
        from celebration_effects import FireworkParticle
        particle = FireworkParticle(400, 200, (255, 70, 70))
        result = particle.update(0.016)
        assert result is True
        assert particle.lifetime < 1.5
    
    def test_firework_trail(self):
        from celebration_effects import FireworkParticle
        particle = FireworkParticle(400, 200, (255, 70, 70))
        for _ in range(15):
            particle.update(0.016)
        # 轨迹应该被限制在10个点
        assert len(particle.trail) <= 10


class TestCelebrationEffect:
    """庆祝特效管理器测试"""
    
    def test_celebration_creation(self):
        from celebration_effects import CelebrationEffect
        effect = CelebrationEffect(800, 600)
        assert effect.width == 800
        assert effect.height == 600
        assert effect.active is False
    
    def test_celebration_start(self):
        from celebration_effects import CelebrationEffect
        effect = CelebrationEffect(800, 600)
        effect.start()
        assert effect.active is True
        assert len(effect.confetti) == 100
        assert len(effect.fireworks) == 5
    
    def test_celebration_update(self):
        from celebration_effects import CelebrationEffect
        effect = CelebrationEffect(800, 600)
        effect.start()
        initial_confetti = len(effect.confetti)
        initial_fireworks = len(effect.fireworks)
        
        effect.update(0.016)
        
        assert len(effect.confetti) <= initial_confetti
        assert len(effect.fireworks) <= initial_fireworks
    
    def test_celebration_lifetime(self):
        from celebration_effects import CelebrationEffect
        effect = CelebrationEffect(800, 600)
        effect.start()
        
        # 模拟4秒后还有一些残留粒子，手动清空
        effect.lifetime = 5.0
        effect.confetti.clear()
        effect.fireworks.clear()
        effect.update(0.016)
        assert effect.active is False


class TestStageCompleteEffect:
    """关卡完成公告效果测试"""
    
    def test_stage_complete_creation(self):
        from celebration_effects import StageCompleteEffect
        effect = StageCompleteEffect(800, 600, score=1000, stars=2)
        assert effect.score == 1000
        assert effect.stars == 2
        assert effect.active is True
    
    def test_stage_complete_update(self):
        from celebration_effects import StageCompleteEffect
        effect = StageCompleteEffect(800, 600)
        result = effect.update(0.016)
        assert result is True
        assert effect.lifetime > 0
    
    def test_stage_complete_scale_animation(self):
        from celebration_effects import StageCompleteEffect
        effect = StageCompleteEffect(800, 600)
        
        # 0.25秒时应该放大到一半
        for _ in range(16):
            effect.update(0.016)
        assert effect.scale > 0.4
        
        # 0.6秒时应该完全放大
        for _ in range(22):
            effect.update(0.016)
        assert effect.scale > 0.95
    
    def test_stage_complete_finish(self):
        from celebration_effects import StageCompleteEffect
        effect = StageCompleteEffect(800, 600)
        
        # 模拟3秒
        for _ in range(200):
            effect.update(0.016)
        
        assert effect.active is False
    
    def test_stars_display(self):
        from celebration_effects import StageCompleteEffect
        # 测试3星
        effect = StageCompleteEffect(800, 600, stars=3)
        assert effect.stars == 3
        
        # 测试0星
        effect2 = StageCompleteEffect(800, 600, stars=0)
        assert effect2.stars == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])