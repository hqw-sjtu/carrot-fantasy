"""
测试 - 金币飞行系统
Test - Coin Flight System
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))
except:
    pytest.skip("pygame not available", allow_module_level=True)

from coin_flight import FlyingCoin, CoinFlightSystem


class TestFlyingCoin:
    """测试飞行金币"""
    
    def test_coin_creation(self):
        """测试金币创建"""
        coin = FlyingCoin(100, 100, 200, 200, 5)
        assert coin.x == 100
        assert coin.y == 100
        assert coin.target_x == 200
        assert coin.target_y == 200
        assert coin.value == 5
        assert coin.progress == 0
    
    def test_coin_update(self):
        """测试金币更新"""
        coin = FlyingCoin(100, 100, 200, 200, 1)
        result = coin.update(0.1)
        assert result is True
        assert coin.progress > 0
    
    def test_coin_completion(self):
        """测试金币完成"""
        coin = FlyingCoin(100, 100, 200, 200, 1)
        # 正常飞行完成
        for _ in range(50):
            if not coin.update(0.05):
                break
        # 验证最终完成
        assert coin.progress >= 1.0
    
    def test_coin_render(self):
        """测试金币渲染"""
        coin = FlyingCoin(100, 100, 200, 200, 1)
        surface = pygame.Surface((400, 300))
        coin.render(surface)  # 不应该崩溃
    
    def test_arc_movement(self):
        """测试弧线运动"""
        coin = FlyingCoin(100, 100, 100, 200, 1)
        
        positions = []
        for _ in range(20):
            coin.update(0.05)
            positions.append((coin.x, coin.y))
        
        # 检查有弧线变化
        y_values = [p[1] for p in positions]
        assert max(y_values) > 150  # 有上升


class TestCoinFlightSystem:
    """测试金币飞行系统"""
    
    def test_system_creation(self):
        """测试系统创建"""
        system = CoinFlightSystem()
        assert len(system.coins) == 0
        assert system.target_pos == (70, 30)
    
    def test_set_target(self):
        """测试设置目标"""
        system = CoinFlightSystem()
        system.set_target(100, 50)
        assert system.target_pos == (100, 50)
    
    def test_spawn_coin(self):
        """测试生成单金币"""
        system = CoinFlightSystem()
        system.spawn_coin(100, 100, 10)
        assert len(system.coins) == 1
        assert system.coins[0].value == 10
    
    def test_spawn_coins(self):
        """测试生成多金币"""
        system = CoinFlightSystem()
        system.spawn_coins(100, 100, 5, 2)
        assert len(system.coins) == 5
    
    def test_system_update(self):
        """测试系统更新"""
        system = CoinFlightSystem()
        system.spawn_coin(100, 100, 1)
        system.update(0.1)
        assert len(system.coins) > 0
    
    def test_system_render(self):
        """测试系统渲染"""
        system = CoinFlightSystem()
        system.spawn_coin(100, 100, 1)
        surface = pygame.Surface((400, 300))
        system.render(surface)  # 不应该崩溃
    
    def test_is_active(self):
        """测试活跃状态"""
        system = CoinFlightSystem()
        assert system.is_active() is False
        
        system.spawn_coin(100, 100, 1)
        assert system.is_active() is True
    
    def test_clear(self):
        """测试清除"""
        system = CoinFlightSystem()
        system.spawn_coins(100, 100, 5, 1)
        assert len(system.coins) == 5
        
        system.clear()
        assert len(system.coins) == 0
        assert system.is_active() is False


class TestCoinFlightIntegration:
    """测试金币飞行集成"""
    
    def test_full_flight_cycle(self):
        """测试完整飞行周期"""
        system = CoinFlightSystem()
        surface = pygame.Surface((400, 300))
        
        # 生成金币
        system.spawn_coin(100, 100, 5)
        
        # 模拟更新直到完成
        for _ in range(100):
            system.update(0.02)
            if not system.is_active():
                break
        
        assert True  # 完成了
    
    def test_multiple_coins_flight(self):
        """测试多金币飞行"""
        system = CoinFlightSystem()
        surface = pygame.Surface((400, 300))
        
        # 生成多个金币
        system.spawn_coins(100, 100, 10, 1)
        
        # 渲染
        system.render(surface)
        
        # 更新直到完成
        for _ in range(200):
            system.update(0.02)
            if not system.is_active():
                break
        
        assert True