# -*- coding: utf-8 -*-
"""波次预览系统测试"""
import pytest
import pygame
import sys
import os

# 初始化pygame用于测试
pygame.init()
pygame.display.set_mode((800, 600))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from wave_preview import WavePreview, WavePreviewManager


class TestWavePreview:
    """波次预览测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.preview = WavePreview()
        self.test_waves = [
            {"monsters": [("小怪物", 5)], "interval": 1.0},
            {"monsters": [("小怪物", 8), ("中怪物", 2)], "interval": 0.8},
            {"monsters": [("中怪物", 5), ("大怪物", 1)], "interval": 0.6},
            {"monsters": [("大怪物", 3), ("Boss", 1)], "interval": 0.5},
            {"monsters": [("超级Boss", 1)], "interval": 1.0},
        ]
    
    def test_preview_creation(self):
        """测试预览创建"""
        assert self.preview is not None
        assert not self.preview.visible
        assert self.preview.current_wave == 0
        assert self.preview.max_preview_time == 5.0
    
    def test_show_preview_basic(self):
        """测试显示波次预览-基础"""
        result = self.preview.show_preview(0, self.test_waves)
        assert result is True
        assert self.preview.visible
        assert self.preview.current_wave == 0
    
    def test_show_preview_with_difficulty(self):
        """测试显示波次预览-难度"""
        result = self.preview.show_preview(1, self.test_waves, difficulty=1.5)
        assert result is True
        assert self.preview.difficulty == 1.5
        # 怪物数量应该乘以难度
        assert self.preview.monster_counts.get("小怪物") == 12  # 8 * 1.5
    
    def test_show_preview_out_of_range(self):
        """测试超出范围"""
        result = self.preview.show_preview(10, self.test_waves)
        assert result is False
        assert not self.preview.visible
    
    def test_preview_update(self):
        """测试预览更新"""
        self.preview.show_preview(0, self.test_waves)
        initial_offset = self.preview.animation_offset
        
        self.preview.update(0.1)
        assert self.preview.preview_time == 0.1
        assert self.preview.animation_offset > initial_offset
    
    def test_preview_timeout(self):
        """测试预览超时自动隐藏"""
        self.preview.show_preview(0, self.test_waves)
        self.preview.max_preview_time = 1.0  # 缩短用于测试
        
        self.preview.update(0.5)
        assert self.preview.visible
        
        self.preview.update(0.6)
        assert not self.preview.visible
    
    def test_boss_preview(self):
        """测试Boss波次预览"""
        result = self.preview.show_preview(4, self.test_waves)
        assert result is True
        assert "超级Boss" in self.preview.monster_counts
        assert self.preview.total_enemies == 1
    
    def test_manager_creation(self):
        """测试管理器创建"""
        manager = WavePreviewManager()
        assert manager is not None
        assert manager.preview is not None
        assert not manager.countdown_active
        assert not manager.wave_started


class TestWavePreviewDraw:
    """波次预览绘制测试"""
    
    def setup_method(self):
        self.preview = WavePreview()
        self.test_waves = [
            {"monsters": [("小怪物", 5), ("中怪物", 3)], "interval": 1.0},
        ]
    
    def test_draw_when_not_visible(self):
        """测试不可见时不绘制"""
        screen = pygame.Surface((800, 600))
        self.preview.draw(screen)
        # 不应报错
    
    def test_draw_when_visible(self):
        """测试可见时绘制"""
        self.preview.show_preview(0, self.test_waves)
        screen = pygame.Surface((800, 600))
        self.preview.update(0.1)
        self.preview.draw(screen)
        # 不应报错


class TestWavePreviewIntegration:
    """波次预览集成测试"""
    
    def setup_method(self):
        self.manager = WavePreviewManager()
        self.test_waves = [
            {"monsters": [("小怪物", 5)], "interval": 1.0},
            {"monsters": [("小怪物", 8), ("Boss", 1)], "interval": 0.8},
        ]
    
    def test_countdown_trigger(self):
        """测试倒计时触发"""
        self.manager.trigger_countdown(1, self.test_waves, difficulty=1.2)
        assert self.manager.countdown_active
        assert self.manager.preview.visible
        assert self.manager.preview.monster_counts.get("Boss") == 1
    
    def test_wave_start_signal(self):
        """测试波次开始信号"""
        self.manager.trigger_countdown(0, self.test_waves)
        
        # 触发后countdown_active应为True
        assert self.manager.countdown_active is True
        assert self.manager.wave_started is False
        
        # 预览显示期间不会触发波次开始
        result = self.manager.update(0.1)
        assert result is False  # 预览期间不返回True
        
        # 验证preview正在显示
        assert self.manager.preview.visible is True