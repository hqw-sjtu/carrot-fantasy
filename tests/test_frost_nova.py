"""
测试冰霜新星特效
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


class MockMonster:
    """模拟怪物用于测试"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.frozen = 0
        self.slow_factor = 1.0
        self.slow_timer = 0


class MockGame:
    """模拟游戏对象"""
    def __init__(self):
        self.monsters = []


class TestFrostNovaEffect:
    """测试冰霜新星特效"""
    
    def test_init(self):
        """测试初始化"""
        from frost_nova_effect import FrostNovaEffect
        effect = FrostNovaEffect(400, 300, radius=200, intensity=1.0)
        
        assert effect.x == 400
        assert effect.y == 300
        assert effect.max_radius == 200
        assert effect.intensity == 1.0
        assert effect.active is True
        assert effect.current_radius == 0
        
    def test_update_radius(self):
        """测试半径扩散"""
        from frost_nova_effect import FrostNovaEffect
        effect = FrostNovaEffect(400, 300, radius=200)
        
        # 模拟更新
        effect.update(0.1, MockGame())
        
        assert effect.current_radius > 0
        assert effect.life > 0
        
    def test_freeze_enemies(self):
        """测试冰冻敌人"""
        from frost_nova_effect import FrostNovaEffect
        
        game = MockGame()
        monster1 = MockMonster(400, 300)  # 在范围内
        monster2 = MockMonster(100, 100)  # 范围外
        game.monsters = [monster1, monster2]
        
        effect = FrostNovaEffect(400, 300, radius=200)
        effect.update(0.1, game)
        
        # 范围内怪物应该被冰冻
        assert len(effect.frozen_enemies) > 0
        
    def test_lifetime(self):
        """测试生命周期"""
        from frost_nova_effect import FrostNovaEffect
        effect = FrostNovaEffect(400, 300)
        
        # 超过最大生命周期
        effect.update(1.0, MockGame())
        
        assert effect.active is False
        
    @pytest.mark.skipif(SCREEN is None, reason="Pygame not available")
    def test_draw(self):
        """测试绘制"""
        from frost_nova_effect import FrostNovaEffect
        effect = FrostNovaEffect(400, 300)
        effect.update(0.2, MockGame())  # 激活特效
        effect.current_radius = 50  # 确保有半径
        
        # 不应抛出异常
        try:
            effect.draw(SCREEN)
        except pygame.error:
            pytest.skip("Pygame display not available")
        
    def test_presets(self):
        """测试预设配置"""
        from frost_nova_effect import FrostNovaPresets
        
        small = FrostNovaPresets.small()
        assert small['radius'] == 120
        
        medium = FrostNovaPresets.medium()
        assert medium['radius'] == 180
        
        large = FrostNovaPresets.large()
        assert large['radius'] == 250
        
        ultimate = FrostNovaPresets.ultimate()
        assert ultimate['radius'] == 350
        
    def test_manager(self):
        """测试管理器"""
        from frost_nova_effect import FrostNovaManager
        
        # 触发特效
        effect = FrostNovaManager.trigger(400, 300, 200)
        assert effect is not None
        assert len(FrostNovaManager._effects) == 1
        
        # 更新
        FrostNovaManager.update(0.1, MockGame())
        
        # 绘制
        if SCREEN:
            try:
                FrostNovaManager.draw(SCREEN)
            except pygame.error:
                pytest.skip("Pygame display not available")
        
        # 清除
        FrostNovaManager.clear()
        assert len(FrostNovaManager._effects) == 0


class TestFrostNovaIntegration:
    """测试冰霜新星集成"""
    
    def test_slow_effect(self):
        """测试减速效果"""
        from frost_nova_effect import FrostNovaEffect
        
        monster = MockMonster(400, 300)
        assert monster.slow_factor == 1.0
        
        game = MockGame()
        game.monsters = [monster]
        
        effect = FrostNovaEffect(400, 300, radius=200, intensity=1.0)
        effect.update(0.1, game)
        
        # 怪物应该被减速
        assert monster.frozen > 0
        assert monster.slow_factor < 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])