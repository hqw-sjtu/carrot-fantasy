# -*- coding: utf-8 -*-
"""防御塔图鉴UI测试"""

import pytest
import pygame
import sys
import os

# 确保能找到模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 初始化pygame (headless模式)
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))


class TestTowerBestiaryUI:
    """测试防御塔图鉴UI"""
    
    def test_init(self):
        """测试UI初始化"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        assert ui.screen == screen
        assert ui.scroll_offset == 0
        assert ui.max_visible == 5
        assert len(ui.ALL_TOWERS) == 8
    
    def test_color_definitions(self):
        """测试颜色定义"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        assert ui.COLOR_BG == (20, 20, 40)
        assert ui.COLOR_PANEL == (30, 30, 60)
        assert ui.COLOR_BORDER == (60, 60, 100)
        assert ui.COLOR_TEXT == (220, 220, 240)
        assert ui.COLOR_ACCENT == (255, 180, 80)
        assert ui.COLOR_LOCKED == (80, 80, 100)
    
    def test_all_towers_defined(self):
        """测试所有塔类型定义"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        expected_towers = [
            "箭塔", "炮塔", "魔法塔", "电塔", 
            "冰塔", "火塔", "毒塔", "眩晕塔"
        ]
        
        tower_names = [t["name"] for t in ui.ALL_TOWERS]
        assert tower_names == expected_towers
        
        # 检查每个塔都有icon和desc
        for tower in ui.ALL_TOWERS:
            assert "icon" in tower
            assert "desc" in tower
    
    def test_scroll_logic(self):
        """测试滚动逻辑"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        # 初始状态
        assert ui.scroll_offset == 0
        
        # 向上滚动无效
        class MockEvent:
            def __init__(self, key):
                self.type = pygame.KEYDOWN
                self.key = key
        
        # 向下滚动
        ui.handle_event(MockEvent(pygame.K_DOWN))
        assert ui.scroll_offset == 1
        
        ui.handle_event(MockEvent(pygame.K_DOWN))
        assert ui.scroll_offset == 2
        
        # 向上滚动
        ui.handle_event(MockEvent(pygame.K_UP))
        assert ui.scroll_offset == 1
        
        # 边界检查 - 不能滚到负数
        ui.scroll_offset = 0
        ui.handle_event(MockEvent(pygame.K_UP))
        assert ui.scroll_offset == 0
    
    def test_escape_closes(self):
        """测试ESC关闭"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        class MockEvent:
            def __init__(self, key):
                self.type = pygame.KEYDOWN
                self.key = key
        
        result = ui.handle_event(MockEvent(pygame.K_ESCAPE))
        assert result == False
    
    def test_draw_no_crash(self):
        """测试绘制不崩溃"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        # 应该不抛出异常
        result = ui.draw()
        assert result == screen
    
    def test_bestiary_integration(self):
        """测试与图鉴系统集成"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        from src.tower_bestiary import get_bestiary
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        bestiary = get_bestiary()
        
        # 测试解锁功能
        bestiary.unlock_tower("箭塔")
        assert bestiary.is_unlocked("箭塔")
        assert bestiary.get_unlocked_count() >= 1
        
        # 记录击杀
        bestiary.record_kill("箭塔")
        bestiary.record_damage("箭塔", 100)
        
        stats = bestiary.get_tower_stats("箭塔")
        assert stats['kills'] >= 1
        assert stats['damage'] >= 100
    
    def test_visible_towers_calculation(self):
        """测试可见塔计算"""
        from src.tower_bestiary_ui import TowerBestiaryUI
        
        screen = pygame.Surface((800, 600))
        ui = TowerBestiaryUI(screen)
        
        # 初始显示
        visible = ui.ALL_TOWERS[ui.scroll_offset:ui.scroll_offset + ui.max_visible]
        assert len(visible) == ui.max_visible
        
        # 滚动后
        ui.scroll_offset = 3
        visible = ui.ALL_TOWERS[ui.scroll_offset:ui.scroll_offset + ui.max_visible]
        assert len(visible) == min(ui.max_visible, len(ui.ALL_TOWERS) - 3)


class TestTowerBestiaryIntegration:
    """图鉴系统集成测试"""
    
    def test_bestiary_singleton(self):
        """测试图鉴单例"""
        from src.tower_bestiary import get_bestiary
        
        b1 = get_bestiary()
        b2 = get_bestiary()
        
        assert b1 is b2
    
    def test_bestiary_save_load(self):
        """测试图鉴保存加载"""
        from src.tower_bestiary import TowerBestiary
        
        # 先清理
        bestiary = TowerBestiary()
        original_stats = bestiary.get_tower_stats("测试塔")
        original_damage = original_stats.get('damage', 0)
        
        # 累加记录
        bestiary.unlock_tower("测试塔")
        bestiary.record_kill("测试塔")
        bestiary.record_damage("测试塔", 500)
        
        # 重新创建应该加载累积数据
        bestiary2 = TowerBestiary()
        assert bestiary2.is_unlocked("测试塔")
        current_damage = bestiary2.get_tower_stats("测试塔")['damage']
        assert current_damage >= original_damage + 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])