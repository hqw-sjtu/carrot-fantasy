"""
保卫萝卜 - 防御塔皮肤系统测试
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import pygame
    pygame.init()
except:
    pass


class TestTowerSkin:
    """防御塔皮肤测试"""
    
    def test_skin_creation(self):
        from tower_skins import TowerSkin
        skin = TowerSkin(TowerSkin.CLASSIC)
        assert skin.skin_type == TowerSkin.CLASSIC
    
    def test_skin_colors(self):
        from tower_skins import TowerSkin
        skin = TowerSkin(TowerSkin.GOLD)
        colors = skin.get_colors((100, 100, 100))
        assert "outline" in colors
        assert "highlight" in colors
        assert "glow" in colors
    
    def test_rainbow_skin(self):
        from tower_skins import TowerSkin
        skin = TowerSkin(TowerSkin.RAINBOW)
        skin.rainbow_phase = 0
        colors = skin.get_colors((100, 100, 100))
        assert colors["outline"] != colors["highlight"]  # 动态变化
    
    def test_skin_update(self):
        from tower_skins import TowerSkin
        skin = TowerSkin(TowerSkin.RAINBOW)
        initial_phase = skin.rainbow_phase
        skin.update(0.016)
        assert skin.rainbow_phase > initial_phase


class TestTowerSkinSystem:
    """皮肤管理系统测试"""
    
    def test_system_creation(self):
        from tower_skins import TowerSkinSystem, TowerSkin
        system = TowerSkinSystem()
        owned = system.get_owned_skins()
        assert TowerSkin.CLASSIC in owned
        assert len(owned) >= 1
    
    def test_buy_skin(self):
        from tower_skins import TowerSkinSystem, TowerSkin
        system = TowerSkinSystem()
        # 金币不足
        success, msg = system.buy_skin(TowerSkin.GOLD, 100)
        assert success is False
        assert "金币不足" in msg
        
        # 金币足够
        success, msg = system.buy_skin(TowerSkin.GOLD, 600)
        assert success is True
        assert "成功" in msg
        
        # 再次购买已拥有
        success, msg = system.buy_skin(TowerSkin.GOLD, 600)
        assert success is False
    
    def test_equip_skin(self):
        from tower_skins import TowerSkinSystem, TowerSkin
        system = TowerSkinSystem()
        system.buy_skin(TowerSkin.GOLD, 600)
        
        # 未拥有无法装备
        success, msg = system.equip_skin("tower1", TowerSkin.NEON)
        assert success is False
        
        # 成功装备
        success, msg = system.equip_skin("tower1", TowerSkin.GOLD)
        assert success is True
        assert "已装备" in msg
    
    def test_get_skin(self):
        from tower_skins import TowerSkinSystem, TowerSkin
        system = TowerSkinSystem()
        skin = system.get_skin("unknown_tower")
        assert skin.skin_type == TowerSkin.CLASSIC  # 默认经典
        
        # 先购买再装备
        system.buy_skin(TowerSkin.GOLD, 600)
        system.equip_skin("tower1", TowerSkin.GOLD)
        skin = system.get_skin("tower1")
        assert skin.skin_type == TowerSkin.GOLD
    
    def test_shop_data(self):
        from tower_skins import TowerSkinSystem
        system = TowerSkinSystem()
        data = system.get_skin_shop_data()
        assert len(data) >= 5
        assert all("type" in item for item in data)
        assert all("name" in item for item in data)
        assert all("price" in item for item in data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])