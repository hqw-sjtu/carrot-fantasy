"""
传送门特效测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pygame
import pytest
from base_effects import PortalEffect


class TestPortalEffect:
    """传送门特效测试"""
    
    def setup_method(self):
        """初始化Pygame"""
        if not pygame.get_init():
            pygame.init()
        pygame.display.set_mode((1000, 700))
    
    def test_portal_init(self):
        """测试传送门初始化"""
        effect = PortalEffect(500, 350)
        assert effect.x == 500
        assert effect.y == 350
        assert effect.color == (100, 200, 255)
        assert effect.radius == 40
        assert effect.max_life == 60
        assert len(effect.rings) == 3
        assert len(effect.particles) >= 15
    
    def test_portal_init_custom(self):
        """测试自定义参数初始化"""
        effect = PortalEffect(100, 200, (255, 100, 100), 60)
        assert effect.color == (255, 100, 100)
        assert effect.radius == 60
    
    def test_portal_update(self):
        """测试传送门更新"""
        effect = PortalEffect(500, 350)
        assert effect.active == True
        
        # 更新到过期
        for _ in range(70):
            effect.update(1)
        
        assert effect.life > 0
        assert effect.active == False
    
    def test_portal_particles_update(self):
        """测试粒子更新"""
        effect = PortalEffect(500, 350)
        initial_particles = len(effect.particles)
        
        effect.update(1)
        effect.update(1)
        
        # 粒子应该逐渐消失
        assert len(effect.particles) <= initial_particles
    
    def test_portal_rings_update(self):
        """测试光环更新"""
        effect = PortalEffect(500, 350)
        initial_distances = [r['distance'] for r in effect.rings]
        
        effect.update(1)
        
        # 光环应该扩散
        for i, ring in enumerate(effect.rings):
            assert ring['distance'] > initial_distances[i]
    
    def test_portal_draw(self):
        """测试传送门绘制（无报错）"""
        effect = PortalEffect(500, 350)
        screen = pygame.display.get_surface()
        
        # 绘制不应该报错
        effect.draw(screen)
    
    def test_portal_in_manager(self):
        """测试在管理器中的使用"""
        from base_effects import BaseEffectManager
        
        manager = BaseEffectManager()
        manager.add_portal(500, 350)
        
        assert len(manager.effects) == 1
        assert isinstance(manager.effects[0], PortalEffect)
    
    def test_portal_different_colors(self):
        """测试不同颜色传送门"""
        colors = [
            (100, 200, 255),  # 蓝色
            (255, 100, 100),  # 红色(Boss)
            (255, 200, 50),   # 金色(精英)
            (100, 255, 100),  # 绿色
        ]
        
        for color in colors:
            effect = PortalEffect(500, 350, color)
            assert effect.color == color


if __name__ == '__main__':
    pytest.main([__file__, '-v'])