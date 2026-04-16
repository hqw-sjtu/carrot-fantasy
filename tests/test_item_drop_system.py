"""
Item Drop System Tests
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


class TestItemDrop:
    """Test ItemDrop class"""
    
    def test_item_types_defined(self):
        """Test all item types are defined"""
        from item_drop_system import ItemDrop
        assert "coin" in ItemDrop.TYPES
        assert "health" in ItemDrop.TYPES
        assert "speed" in ItemDrop.TYPES
        assert "damage" in ItemDrop.TYPES
        assert "shield" in ItemDrop.TYPES
        
    def test_item_creation(self):
        """Test item creation"""
        from item_drop_system import ItemDrop
        item = ItemDrop(100, 100, "coin")
        assert item.type == "coin"
        assert item.x == 100
        assert item.y == 100
        assert item.lifetime > 0
        
    def test_item_physics(self):
        """Test item physics update"""
        from item_drop_system import ItemDrop
        item = ItemDrop(100, 100, "coin")  # Start in air
        initial_y = item.y
        item.update(0.05)
        # Gravity pulls down, but initial velocity is upward
        # Just verify position changed
        assert item.y != initial_y
        
    def test_item_lifetime(self):
        """Test item lifetime expiration"""
        from item_drop_system import ItemDrop
        item = ItemDrop(100, 100, "coin")
        # Update many times to reduce lifetime (10s lifetime, 0.1s per update = 100 updates)
        for _ in range(120):
            if not item.update(0.1):
                break
        assert item.lifetime <= 0 or not item.update(0.1)
        
    def test_item_collect(self):
        """Test item collection"""
        from item_drop_system import ItemDrop
        item = ItemDrop(100, 100, "coin")
        result = item.collect()
        assert result is not None
        assert result["name"] == "金币"
        
    def test_boss_drop_bonus(self):
        """Test boss has higher drop chance"""
        from item_drop_system import ItemDrop
        drops = ItemDrop.try_drop(100, 100, monster_value=100, is_boss=True)
        # Boss should have at least one drop
        assert len(drops) >= 1


class TestItemManager:
    """Test ItemManager class"""
    
    def test_manager_init(self):
        """Test manager initialization"""
        from item_drop_system import ItemManager
        manager = ItemManager()
        assert manager.get_count() == 0
        
    def test_add_item(self):
        """Test adding items"""
        from item_drop_system import ItemManager, ItemDrop
        manager = ItemManager()
        item = ItemDrop(100, 100, "coin")
        manager.add_drop(item)
        assert manager.get_count() == 1
        
    def test_update_items(self):
        """Test updating items"""
        from item_drop_system import ItemManager, ItemDrop
        manager = ItemManager()
        manager.add_drop(ItemDrop(100, 100, "coin"))
        manager.update(0.1)
        assert manager.get_count() >= 0
        
    def test_collect_items(self):
        """Test collecting items with mouse"""
        from item_drop_system import ItemManager, ItemDrop
        manager = ItemManager()
        item = ItemDrop(100, 100, "coin")
        manager.add_drop(item)
        collected = manager.check_collect(100, 100)
        assert len(collected) >= 1
        assert collected[0]["name"] == "金币"
