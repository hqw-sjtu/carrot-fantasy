"""
测试闪电链特效系统
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    import os
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    SCREEN = pygame.display.set_mode((800, 600))
except:
    SCREEN = None


class TestLightningSegment:
    """测试闪电线段"""
    
    def test_segment_creation(self):
        """测试线段创建"""
        from lightning_chain_effect import LightningSegment
        seg = LightningSegment((0, 0), (100, 100))
        
        assert seg.start == (0, 0)
        assert seg.end == (100, 100)
        assert seg.color == (200, 220, 255)
        assert seg.width == 2
        
    def test_segment_update(self):
        """测试线段更新"""
        from lightning_chain_effect import LightningSegment
        seg = LightningSegment((0, 0), (100, 100))
        
        alive = seg.update(0.05)
        assert alive is True
        
        alive = seg.update(0.2)
        assert alive is False


class TestLightningBolt:
    """测试闪电"""
    
    def test_bolt_creation(self):
        """测试闪电创建"""
        from lightning_chain_effect import LightningBolt
        bolt = LightningBolt((0, 0), (200, 200))
        
        assert bolt.start == (0, 0)
        assert bolt.end == (200, 200)
        assert len(bolt.segments) > 0
        
    def test_bolt_update(self):
        """测试闪电更新"""
        from lightning_chain_effect import LightningBolt
        bolt = LightningBolt((0, 0), (200, 200))
        
        alive = bolt.update(0.1)
        assert alive is True
        
    def test_bolt_high_intensity(self):
        """测试高强度闪电(带分叉)"""
        from lightning_chain_effect import LightningBolt
        bolt = LightningBolt((0, 0), (200, 200), intensity=1.0)
        
        # 高强度闪电应有更多分叉
        assert bolt.intensity == 1.0


class TestLightningChainEffect:
    """测试闪电链管理器"""
    
    def test_init(self):
        """测试初始化"""
        from lightning_chain_effect import LightningChainEffect
        effect = LightningChainEffect()
        
        assert len(effect.bolts) == 0
        assert len(effect.particles) == 0
        
    def test_create_chain(self):
        """测试创建闪电链"""
        from lightning_chain_effect import LightningChainEffect
        effect = LightningChainEffect()
        
        targets = [(100, 100), (200, 150), (300, 200)]
        effect.create_chain((50, 50), targets)
        
        assert len(effect.bolts) > 0
        
    def test_create_chain_empty_targets(self):
        """测试空目标"""
        from lightning_chain_effect import LightningChainEffect
        effect = LightningChainEffect()
        
        effect.create_chain((50, 50), [])
        
        assert len(effect.bolts) == 0
        
    def test_update(self):
        """测试更新"""
        from lightning_chain_effect import LightningChainEffect
        effect = LightningChainEffect()
        
        targets = [(100, 100), (200, 150)]
        effect.create_chain((50, 50), targets)
        
        alive = effect.update(0.05)
        assert alive is True
        
    def test_singleton(self):
        """测试单例"""
        from lightning_chain_effect import get_instance, reset
        reset()
        
        instance1 = get_instance()
        instance2 = get_instance()
        
        assert instance1 is instance2


@pytest.mark.skipif(SCREEN is None, reason="Pygame not available")
class TestLightningDraw:
    """测试绘制(需要pygame)"""
    
    def test_draw_no_crash(self):
        """测试绘制不崩溃"""
        from lightning_chain_effect import LightningChainEffect
        
        # 创建离屏surface测试绘制
        surface = pygame.Surface((200, 200))
        effect = LightningChainEffect()
        
        targets = [(100, 100), (200, 150), (300, 200)]
        effect.create_chain((50, 50), targets)
        
        # 不应抛出异常
        effect.update(0.05)
        effect.draw(surface)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])