"""
商店系统测试
"""
import pytest
import pygame
from unittest.mock import Mock, MagicMock
import sys
sys.path.insert(0, 'src')

# 初始化pygame
pygame.init()
pygame.display.set_mode((800, 600))


class TestShopItem:
    """商店物品测试"""
    
    def test_shop_item_init(self):
        """测试商店物品初始化"""
        from shop_system import ShopItem
        
        item = ShopItem(
            item_id="test_item",
            name="Test Item",
            name_cn="测试物品",
            price=100,
            description="Test description",
            icon="⚔️",
            effect_type="damage",
            effect_value=1.5
        )
        
        assert item.id == "test_item"
        assert item.name == "Test Item"
        assert item.name_cn == "测试物品"
        assert item.price == 100
        assert item.description == "Test description"
        assert item.icon == "⚔️"
        assert item.effect_type == "damage"
        assert item.effect_value == 1.5
        assert item.count == 0


class TestShopSystem:
    """商店系统测试"""
    
    @pytest.fixture
    def mock_game(self):
        """模拟游戏对象"""
        game = Mock()
        game.gold = 1000
        game.screen = pygame.display.set_mode((800, 600))
        game.effects = Mock()
        game.effects.spawn_particle = Mock()
        return game
    
    def test_shop_init(self, mock_game):
        """测试商店初始化"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        
        assert shop.is_open == False
        assert shop.selected_item is None
        assert len(shop.items) == 10
    
    def test_shop_items_initialized(self, mock_game):
        """测试商店物品已初始化"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        
        # 检查关键物品
        assert "damage_boost" in shop.items
        assert "gold_boost" in shop.items
        assert "nuke" in shop.items
        assert "freeze" in shop.items
        
        # 验证物品属性
        assert shop.items["damage_boost"].price == 200
        assert shop.items["gold_boost"].price == 300
        assert shop.items["nuke"].price == 1000
    
    def test_shop_open_close(self, mock_game):
        """测试商店开关"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        
        # 初始状态
        assert not shop.is_open
        
        # 打开商店
        shop.open()
        assert shop.is_open
        
        # 关闭商店
        shop.close()
        assert not shop.is_open
        
        # 切换
        shop.toggle()
        assert shop.is_open
        shop.toggle()
        assert not shop.is_open
    
    def test_buy_item_success(self, mock_game):
        """测试购买物品成功"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        initial_gold = mock_game.gold
        
        # 模拟激活boost
        mock_game.activate_boost = Mock()
        
        # 购买物品
        result = shop.buy_item("damage_boost")
        
        assert result == True
        assert mock_game.gold == initial_gold - 200
        assert shop.items["damage_boost"].count == 1
    
    def test_buy_item_insufficient_gold(self, mock_game):
        """测试金币不足购买"""
        from shop_system import ShopSystem
        
        mock_game.gold = 50
        shop = ShopSystem(mock_game)
        
        result = shop.buy_item("damage_boost")
        
        assert result == False
        assert mock_game.gold == 50  # 金币未变
    
    def test_buy_item_invalid(self, mock_game):
        """测试购买无效物品"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        
        result = shop.buy_item("invalid_item")
        
        assert result == False
    
    def test_apply_damage_effect(self, mock_game):
        """测试应用伤害效果"""
        from shop_system import ShopSystem
        
        mock_game.activate_boost = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["damage_boost"]
        shop._apply_item_effect(item)
        
        mock_game.activate_boost.assert_called_once_with("damage", 1.5, 10)
    
    def test_apply_gold_effect(self, mock_game):
        """测试应用金币效果"""
        from shop_system import ShopSystem
        
        mock_game.activate_boost = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["gold_boost"]
        shop._apply_item_effect(item)
        
        mock_game.activate_boost.assert_called_once_with("gold", 2.0, 30)
    
    def test_apply_freeze_effect(self, mock_game):
        """测试应用冰冻效果"""
        from shop_system import ShopSystem
        
        mock_game.freeze_monsters = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["freeze"]
        shop._apply_item_effect(item)
        
        mock_game.freeze_monsters.assert_called_once_with(5.0)
    
    def test_apply_nuke_effect(self, mock_game):
        """测试应用核弹效果"""
        from shop_system import ShopSystem
        
        mock_game.nuke_all_monsters = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["nuke"]
        shop._apply_item_effect(item)
        
        mock_game.nuke_all_monsters.assert_called_once()
    
    def test_apply_lives_effect(self, mock_game):
        """测试应用生命效果"""
        from shop_system import ShopSystem
        
        mock_game.lives = 10
        mock_game.activate_boost = Mock()
        mock_game.freeze_monsters = Mock()
        mock_game.nuke_all_monsters = Mock()
        mock_game.skip_wave = Mock()
        mock_game.activate_global_slow = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["save_lives"]
        shop._apply_item_effect(item)
        
        assert mock_game.lives == 11
    
    def test_apply_skip_wave_effect(self, mock_game):
        """测试应用跳过波次效果"""
        from shop_system import ShopSystem
        
        mock_game.skip_wave = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["skip_wave"]
        shop._apply_item_effect(item)
        
        mock_game.skip_wave.assert_called_once()
    
    def test_apply_global_slow_effect(self, mock_game):
        """测试应用全局减速效果"""
        from shop_system import ShopSystem
        
        mock_game.activate_global_slow = Mock()
        shop = ShopSystem(mock_game)
        
        item = shop.items["slow_all"]
        shop._apply_item_effect(item)
        
        mock_game.activate_global_slow.assert_called_once_with(0.5, 15)
    
    def test_render(self, mock_game):
        """测试商店渲染"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        shop.open()
        
        # 不应报错
        shop.render(mock_game.screen)
    
    def test_render_closed(self, mock_game):
        """测试关闭时渲染"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game)
        
        # 不应报错
        shop.render(mock_game.screen)


class TestShopSystemIntegration:
    """商店系统集成测试"""
    
    @pytest.fixture
    def mock_game_full(self):
        """完整模拟游戏对象"""
        game = Mock()
        game.gold = 500
        game.screen = pygame.display.set_mode((800, 600))
        game.lives = 5
        game.effects = Mock()
        game.effects.spawn_particle = Mock()
        game.activate_boost = Mock()
        game.freeze_monsters = Mock()
        game.nuke_all_monsters = Mock()
        game.skip_wave = Mock()
        game.activate_global_slow = Mock()
        return game
    
    def test_full_purchase_flow(self, mock_game_full):
        """完整购买流程"""
        from shop_system import ShopSystem
        
        shop = ShopSystem(mock_game_full)
        
        # 购买多个物品
        shop.buy_item("damage_boost")
        assert mock_game_full.gold == 300
        
        shop.buy_item("gold_boost")
        assert mock_game_full.gold == 0
        
        # 金币不足
        result = shop.buy_item("damage_boost")
        assert result == False
    
    def test_item_count_tracking(self, mock_game_full):
        """物品计数追踪"""
        from shop_system import ShopSystem
        
        # 重新创建mock确保activate_global_slow存在
        mock_game_full.activate_global_slow = Mock()
        mock_game_full.gold = 3000  # 足够购买
        shop = ShopSystem(mock_game_full)
        
        # 多次购买同一物品
        for _ in range(3):
            shop.buy_item("save_lives")
        
        assert shop.items["save_lives"].count == 3
        assert mock_game_full.lives == 8  # 初始5 + 3