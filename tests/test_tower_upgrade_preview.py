# -*- coding: utf-8 -*-
"""
防御塔升级预览系统测试套件
"""

import pytest
import pygame
import sys
import os

# 初始化 pygame
pygame.init()
pygame.display.set_mode((800, 600))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from tower_upgrade_preview import TowerUpgradePreview, get_upgrade_preview, UpgradePath


class TestTowerUpgradePreview:
    """升级预览系统测试"""
    
    def test_initialization(self):
        """测试初始化"""
        preview = TowerUpgradePreview()
        assert preview is not None
        assert preview.visible == False
        assert preview.tower_type is None
        assert preview.current_level == 1
        
    def test_upgrade_paths_exist(self):
        """测试升级路径配置存在"""
        preview = TowerUpgradePreview()
        expected_towers = ["arrow", "cannon", "magic", "ice", "lightning", "poison"]
        
        for tower_type in expected_towers:
            assert tower_type in preview.UPGRADE_PATHS
            paths = preview.UPGRADE_PATHS[tower_type]
            assert len(paths) == 5  # 5个等级
            
            # 验证每个等级都有属性
            for path in paths:
                assert isinstance(path, UpgradePath)
                assert path.damage_bonus >= 0
                assert path.range_bonus >= 0
                assert path.speed_bonus >= 0
                
    def test_show_hide(self):
        """测试显示/隐藏功能"""
        preview = TowerUpgradePreview()
        
        # 测试显示
        preview.show("arrow", 400, 300, 2)
        assert preview.visible == True
        assert preview.tower_type == "arrow"
        assert preview.current_level == 2
        
        # 测试隐藏
        preview.hide()
        assert preview.visible == False
        
    def test_toggle(self):
        """测试切换功能"""
        preview = TowerUpgradePreview()
        
        # 第一次显示
        preview.toggle("cannon", 300, 200, 1)
        assert preview.visible == True
        assert preview.tower_type == "cannon"
        
        # 第二次隐藏（同一类型）
        preview.toggle("cannon", 300, 200, 1)
        assert preview.visible == False
        
    def test_invalid_tower_type(self):
        """测试无效的防御塔类型"""
        preview = TowerUpgradePreview()
        preview.show("invalid_tower", 400, 300)
        assert preview.visible == False  # 应该不显示
        
    def test_get_upgrade_cost(self):
        """测试升级成本计算"""
        preview = TowerUpgradePreview()
        preview.tower_type = "arrow"
        preview.current_level = 2
        
        # 测试升级到3级
        cost_3 = preview.get_upgrade_cost(3)
        assert cost_3 == 100  # 箭塔3级成本100
        
        # 测试升级到5级 (3+4+5级总和)
        cost_5 = preview.get_upgrade_cost(5)
        assert cost_5 == 700  # 100+200+400
        
        # 测试降级或同级
        cost_same = preview.get_upgrade_cost(2)
        assert cost_same == 0
        
    def test_is_point_inside(self):
        """测试点是否在面板内"""
        preview = TowerUpgradePreview()
        preview.show("magic", 400, 300, 1)
        
        # 点在面板内
        assert preview.is_point_inside(preview.panel_x + 10, preview.panel_y + 10) == True
        
        # 点在面板外
        assert preview.is_point_inside(0, 0) == False
        assert preview.is_point_inside(1000, 1000) == False
        
    def test_global_instance(self):
        """测试全局实例获取"""
        instance1 = get_upgrade_preview()
        instance2 = get_upgrade_preview()
        
        assert instance1 is instance2  # 应该是单例
        
    def test_draw_returns_bool(self):
        """测试绘制返回值"""
        preview = TowerUpgradePreview()
        
        # 未显示时返回 False
        screen = pygame.display.set_mode((800, 600))
        result = preview.draw(screen)
        assert result == False
        
        # 显示时返回 True
        preview.show("ice", 400, 300, 1)
        result = preview.draw(screen)
        assert result == True
        
    def test_font_initialization(self):
        """测试字体初始化"""
        preview = TowerUpgradePreview()
        
        # 初始时字体为 None
        assert preview.font is None
        assert preview.title_font is None
        
        # 初始化后应该有字体
        preview.initialize()
        assert preview.font is not None
        assert preview.title_font is not None


class TestUpgradePath:
    """升级路径数据类测试"""
    
    def test_dataclass_creation(self):
        """测试数据类创建"""
        path = UpgradePath(
            level=3,
            name="精通",
            damage_bonus=40,
            range_bonus=20,
            speed_bonus=30,
            cost=100,
            special_effect="穿透+1"
        )
        
        assert path.level == 3
        assert path.name == "精通"
        assert path.damage_bonus == 40
        assert path.cost == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])