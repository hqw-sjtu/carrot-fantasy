# -*- coding: utf-8 -*-
"""防御塔图鉴系统测试"""

import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tower_bestiary import TowerBestiary


class TestTowerBestiary:
    """防御塔图鉴测试"""
    
    def setup_method(self):
        """每个测试前重置单例"""
        TowerBestiary.reset_instance()
    
    def test_init(self):
        """测试初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            assert bestiary is not None
            assert bestiary.get_unlocked_count() == 0
    
    def test_unlock_tower(self):
        """测试解锁塔"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            
            # 解锁塔
            result = bestiary.unlock_tower("箭塔")
            assert result is True
            assert bestiary.is_unlocked("箭塔")
            assert bestiary.get_unlocked_count() == 1
    
    def test_duplicate_unlock(self):
        """测试重复解锁"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            
            bestiary.unlock_tower("箭塔")
            result = bestiary.unlock_tower("箭塔")
            assert result is False
            assert bestiary.get_unlocked_count() == 1
    
    def test_record_kill(self):
        """测试记录击杀"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            
            bestiary.unlock_tower("箭塔")
            bestiary.record_kill("箭塔")
            bestiary.record_kill("箭塔")
            
            stats = bestiary.get_tower_stats("箭塔")
            assert stats['kills'] == 2
    
    def test_record_damage(self):
        """测试记录伤害"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            
            bestiary.unlock_tower("炮塔")
            bestiary.record_damage("炮塔", 100)
            bestiary.record_damage("炮塔", 200)
            
            stats = bestiary.get_tower_stats("炮塔")
            assert stats['damage'] == 300
    
    def test_reset(self):
        """测试重置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary = TowerBestiary(path)
            
            bestiary.unlock_tower("箭塔")
            bestiary.unlock_tower("炮塔")
            assert bestiary.get_unlocked_count() == 2
            
            bestiary.reset()
            assert bestiary.get_unlocked_count() == 0
    
    def test_singleton(self):
        """测试单例模式"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test_bestiary.json')
            bestiary1 = TowerBestiary(path)
            bestiary2 = TowerBestiary(path)
            
            # 同一路径应返回同一实例
            assert bestiary1 is bestiary2


class TestTowerBestiaryUI:
    """防御塔图鉴UI测试"""
    
    def test_init(self):
        """测试UI初始化"""
        import pygame
        pygame.init()
        screen = pygame.Surface((800, 600))
        
        from tower_bestiary_ui import TowerBestiaryUI
        
        ui = TowerBestiaryUI(screen)
        assert ui is not None
        assert ui.screen is screen
        assert len(ui.ALL_TOWERS) > 0
        
        pygame.quit()